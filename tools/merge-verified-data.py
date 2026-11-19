#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Merge verified full data into tools/build-v2.py (one-way, idempotent).
Reads: data/leagues.json (full tables, verified 2026-11-18),
       data/fixtures.json (results with stats),
       tools/match-info-2026-11-18.json (venue/channel/referee).
Writes: tools/build-v2.py — replaces the LEAGUES / UPCOMING / RESULTS blocks
        and extends fx() with venue/channel/referee.
Then run: python3 tools/build-v2.py  (regenerates data/*.json, JS, HTML).
"""
import json
import pprint
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
BUILD = ROOT / "tools" / "build-v2.py"

leagues = json.load(open(ROOT / "data" / "leagues.json", encoding="utf-8"))["leagues"]
fixtures = json.load(open(ROOT / "data" / "fixtures.json", encoding="utf-8"))
info = json.load(open(ROOT / "tools" / "match-info-2026-11-18.json", encoding="utf-8"))
channels = info["channels"]
matches_info = info["matches"]

# --- build LEAGUES python literal (same schema as before, full tables) ---
clean_leagues = []
for l in leagues:
    clean_leagues.append({
        "id": l["id"], "name": l["name"], "short": l["short"],
        "country": l["country"], "season": l["season"], "round": l["round"],
        "next_round": l["next_round"], "source": l["source"],
        "table": l["table"], "scorers": l["scorers"], "meta": l["meta"],
    })


def enrich(m):
    """Add venue/channel/referee (only where documented) to a fixture dict."""
    d = dict(m)
    mi = matches_info.get(m["id"], {})
    if mi.get("venue"):
        d["venue"] = mi["venue"]
    if mi.get("venue_note"):
        d["venue_note"] = mi["venue_note"]
    ch = channels.get(m["league"])
    if ch:
        d["channel"] = ch
    if mi.get("referee"):
        d["referee"] = mi["referee"]
    return d


upcoming = [enrich(m) for m in fixtures["upcoming"]]
results = [enrich(m) for m in fixtures["results"]]

src = BUILD.read_text(encoding="utf-8")

# --- 1. replace LEAGUES block ---
leagues_code = "LEAGUES = " + pprint.pformat(clean_leagues, width=110, sort_dicts=False) + "\n"
new_src, n = re.subn(r"LEAGUES = \[.*?^\]\n(?=\n# Fixtures)",
                     lambda _: leagues_code.rstrip("\n"), src,
                     flags=re.M | re.S)
assert n == 1, f"LEAGUES block not found (n={n})"
src = new_src

# --- 2. extend fx() helper to carry venue/channel/referee ---
old_fx = '''def fx(fid, home, away, league, league_name, date, time, source, date_label=None):
    d = {"id": fid, "home": home, "away": away, "league": league,
         "league_name": league_name, "date": date, "time": time,
         "status": "scheduled", "source": source}
    if date_label:
        d["date_label"] = date_label
    return d'''
new_fx = '''def fx(fid, home, away, league, league_name, date, time, source, date_label=None,
       venue=None, venue_note=None, channel=None, referee=None):
    d = {"id": fid, "home": home, "away": away, "league": league,
         "league_name": league_name, "date": date, "time": time,
         "status": "scheduled", "source": source}
    if date_label:
        d["date_label"] = date_label
    if venue:
        d["venue"] = venue
    if venue_note:
        d["venue_note"] = venue_note
    if channel:
        d["channel"] = channel
    if referee:
        d["referee"] = referee
    return d'''
assert old_fx in src, "fx() helper not found"
src = src.replace(old_fx, new_fx, 1)

# --- 3. replace UPCOMING list (fx() calls, now with venue/channel/referee) ---
def fx_call(m):
    def q(v):
        return "None" if v is None else repr(v)
def fx_call(m):
    def q(v):
        return "None" if v is None else repr(v)
    args = [repr(m["id"]), repr(m["home"]), repr(m["away"]), repr(m["league"]),
            repr(m["league_name"]), repr(m["date"]), q(m.get("time")), repr(m["source"])]
    if m.get("date_label"):
        args.append(f'date_label={m["date_label"]!r}')
    if m.get("venue"):
        args.append(f'venue={m["venue"]!r}')
    if m.get("venue_note"):
        args.append(f'venue_note={m["venue_note"]!r}')
    if m.get("channel"):
        args.append(f'channel={m["channel"]!r}')
    if m.get("referee"):
        args.append(f'referee={m["referee"]!r}')
    return "fx(" + ", ".join(args) + "),"


upcoming_code = "UPCOMING = [\n " + "\n ".join(fx_call(m) for m in upcoming) + "\n]"
new_src, n = re.subn(r"UPCOMING = \[.*?^\]\n(?=\n# Last verified results)",
                     lambda _: upcoming_code, src, flags=re.M | re.S)
assert n == 1, f"UPCOMING block not found (n={n})"
src = new_src

# --- 4. replace RESULTS list (dicts, with stats/venue/channel/referee) ---
results_code = "RESULTS = " + pprint.pformat(results, width=110, sort_dicts=False)
new_src, n = re.subn(r"RESULTS = \[.*?^\]\n(?=\nALLOWED = )",
                     lambda _: results_code, src, flags=re.M | re.S)
assert n == 1, f"RESULTS block not found (n={n})"
src = new_src

# --- 5. update the leagues.json note (full tables now) ---
src = src.replace(
    '"note": "أول 5 مراكز موثقة فقط لكل دوري (آخر تحقق 2026-11-18). الجدول الكامل قيد التحقق."',
    '"note": "الجداول الكاملة موثقة لكل دوري (آخر تحقق 2026-11-18). انظر tools/verified-stats-2026-11-18.json للمصادر."')

BUILD.write_text(src, encoding="utf-8")
print(f"merged: {sum(len(l['table']) for l in clean_leagues)} table rows, "
      f"{sum(len(l['scorers']) for l in clean_leagues)} scorers, "
      f"{len(upcoming)} upcoming, {len(results)} results "
      f"({sum(1 for r in results if 'stats' in r)} with stats) into tools/build-v2.py")
