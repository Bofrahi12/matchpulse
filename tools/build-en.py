# -*- coding: utf-8 -*-
"""Almalaeb V2 builder — rebuilds ~/workspace/matchpulse from V1 data + VERIFIED data only.
Run: python3 tools/build-en.py  (from inside matchpulse/)
Every number in data/ below was verified 2026-11-18 from the sources listed
in REPORT.md. Anything unverified is an explicit placeholder, never invented.
"""
import json, os, re, shutil
from datetime import date as _date

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
V1 = os.path.expanduser("~/workspace/matchpulse")
CHECKED = "2026-11-18"

# ------------------------------------------------- Dynamic dates (for the daily update) ---
_EN_MONTHS = ["January", "February", "March", "April", "May", "June",
              "July", "August", "September", "October", "November", "December"]
_EN_WEEKDAYS = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]


def en_date(iso):
    d = _date.fromisoformat(iso) if isinstance(iso, str) else iso
    return f"{_EN_WEEKDAYS[d.weekday()]} {d.day} {_EN_MONTHS[d.month - 1]} {d.year}"


def en_date_short(iso):
    d = _date.fromisoformat(iso) if isinstance(iso, str) else iso
    return f"{d.day} {_EN_MONTHS[d.month - 1]}"


def en_range(d1, d2):
    a, b = _date.fromisoformat(d1), _date.fromisoformat(d2)
    if a.month == b.month and a.year == b.year:
        return f"{a.day}–{b.day} {_EN_MONTHS[a.month - 1]} {a.year}"
    return f"{a.day} {_EN_MONTHS[a.month - 1]} – {b.day} {_EN_MONTHS[b.month - 1]} {b.year}"


# Build date shown in footers (updated from data/*.json in _load_live_data)
BUILD_DATE_EN = en_date(CHECKED)
# Today/tomorrow/live fixtures data (from data/fixtures.json — written by the daily update)
FX_TODAY, FX_TOMORROW, FX_LIVE = [], [], []
FX_NOTE = ""
FX_TODAY_DATE = FX_TOMORROW_DATE = None


def _load_live_data():
    """Prefers data/*.json (written by tools/daily-update.py) over the embedded data.
    If the files are missing or incomplete, the embedded data stays as a fallback."""
    global LEAGUES, UPCOMING, RESULTS, CHECKED, BUILD_DATE_EN
    global FX_TODAY, FX_TOMORROW, FX_LIVE, FX_NOTE, FX_TODAY_DATE, FX_TOMORROW_DATE
    try:
        with open(os.path.join(ROOT, "data/leagues-en.json"), encoding="utf-8") as f:
            dl = json.load(f)
        if len(dl.get("leagues", [])) == 6:
            LEAGUES = dl["leagues"]
            CHECKED = dl.get("updated", CHECKED)
    except Exception:
        pass
    try:
        with open(os.path.join(ROOT, "data/fixtures-en.json"), encoding="utf-8") as f:
            df = json.load(f)
        if isinstance(df.get("upcoming"), list) and isinstance(df.get("results"), list):
            UPCOMING = df["upcoming"]
            RESULTS = df["results"]
            FX_TODAY = df.get("today", [])
            FX_TOMORROW = df.get("tomorrow", [])
            FX_LIVE = df.get("live", [])
            FX_NOTE = df.get("note", "")
            FX_TODAY_DATE = df.get("today_date")
            FX_TOMORROW_DATE = df.get("tomorrow_date")
            CHECKED = df.get("updated", CHECKED)
    except Exception:
        pass
    BUILD_DATE_EN = en_date(CHECKED)

# ---------------------------------------------------------------- data ---
# Tables: TOP 5 ONLY — verified 2026-11-18 (KickoffLens, updated 02:22 UTC,
# cross-checked TheStatsAPI / NBC Sports / laligatable.co).
# gf/ga only where verified; gd always verified. None = not verified.
def row(pos, team, p, w, d, l, gd, pts, gf=None, ga=None):
    return {"pos": pos, "team": team, "p": p, "w": w, "d": d, "l": l,
            "gf": gf, "ga": ga, "gd": gd, "pts": pts}

LEAGUES = [{'id': 'premier-league',
  'name': 'Premier League',
  'short': 'Premier League',
  'country': 'England',
  'season': '2026-27',
  'round': 'Matchweek 10',
  'next_round': 'Matchweek 11 — 21–23 November 2026',
  'source': 'thestatsapi.com (18 November 2026, 22:41 UTC) + cross-checked with nbcsports.com andrenderfoot.com — '
            'Top scorers: renderfoot.com (18 November 2026) + cross-checked with nbcsports.com andradiotimes.com',
  'table': [{'pos': 1,
             'team': 'Arsenal',
             'p': 10,
             'w': 9,
             'd': 0,
             'l': 1,
             'gf': 15,
             'ga': 5,
             'gd': 10,
             'pts': 27},
            {'pos': 2,
             'team': 'Brighton & Hove Albion',
             'p': 10,
             'w': 7,
             'd': 1,
             'l': 2,
             'gf': 26,
             'ga': 7,
             'gd': 19,
             'pts': 22},
            {'pos': 3,
             'team': 'Manchester City',
             'p': 10,
             'w': 7,
             'd': 0,
             'l': 3,
             'gf': 21,
             'ga': 13,
             'gd': 8,
             'pts': 21},
            {'pos': 4,
             'team': 'Liverpool',
             'p': 10,
             'w': 5,
             'd': 3,
             'l': 2,
             'gf': 14,
             'ga': 10,
             'gd': 4,
             'pts': 18},
            {'pos': 5,
             'team': 'Chelsea',
             'p': 10,
             'w': 5,
             'd': 1,
             'l': 4,
             'gf': 19,
             'ga': 16,
             'gd': 3,
             'pts': 16},
            {'pos': 6,
             'team': 'Everton',
             'p': 10,
             'w': 4,
             'd': 4,
             'l': 2,
             'gf': 12,
             'ga': 10,
             'gd': 2,
             'pts': 16},
            {'pos': 7,
             'team': 'Bournemouth',
             'p': 10,
             'w': 4,
             'd': 3,
             'l': 3,
             'gf': 16,
             'ga': 14,
             'gd': 2,
             'pts': 15},
            {'pos': 8,
             'team': 'Brentford',
             'p': 10,
             'w': 3,
             'd': 5,
             'l': 2,
             'gf': 16,
             'ga': 11,
             'gd': 5,
             'pts': 14},
            {'pos': 9,
             'team': 'Leeds United',
             'p': 10,
             'w': 3,
             'd': 5,
             'l': 2,
             'gf': 10,
             'ga': 8,
             'gd': 2,
             'pts': 14},
            {'pos': 10,
             'team': 'Aston Villa',
             'p': 10,
             'w': 3,
             'd': 4,
             'l': 3,
             'gf': 14,
             'ga': 17,
             'gd': -3,
             'pts': 13},
            {'pos': 11,
             'team': 'Tottenham Hotspur',
             'p': 10,
             'w': 3,
             'd': 3,
             'l': 4,
             'gf': 10,
             'ga': 11,
             'gd': -1,
             'pts': 12},
            {'pos': 12,
             'team': 'Newcastle United',
             'p': 10,
             'w': 3,
             'd': 3,
             'l': 4,
             'gf': 13,
             'ga': 16,
             'gd': -3,
             'pts': 12},
            {'pos': 13,
             'team': 'Hull City',
             'p': 10,
             'w': 2,
             'd': 5,
             'l': 3,
             'gf': 11,
             'ga': 11,
             'gd': 0,
             'pts': 11},
            {'pos': 14,
             'team': 'Ipswich Town',
             'p': 10,
             'w': 3,
             'd': 2,
             'l': 5,
             'gf': 15,
             'ga': 20,
             'gd': -5,
             'pts': 11},
            {'pos': 15,
             'team': 'Fulham',
             'p': 10,
             'w': 2,
             'd': 4,
             'l': 4,
             'gf': 10,
             'ga': 12,
             'gd': -2,
             'pts': 10},
            {'pos': 16,
             'team': 'Nottingham Forest',
             'p': 10,
             'w': 2,
             'd': 3,
             'l': 5,
             'gf': 9,
             'ga': 13,
             'gd': -4,
             'pts': 9},
            {'pos': 17,
             'team': 'Coventry City',
             'p': 10,
             'w': 3,
             'd': 0,
             'l': 7,
             'gf': 10,
             'ga': 19,
             'gd': -9,
             'pts': 9},
            {'pos': 18,
             'team': 'Manchester United',
             'p': 10,
             'w': 1,
             'd': 5,
             'l': 4,
             'gf': 14,
             'ga': 19,
             'gd': -5,
             'pts': 8},
            {'pos': 19,
             'team': 'Sunderland',
             'p': 10,
             'w': 2,
             'd': 2,
             'l': 6,
             'gf': 8,
             'ga': 17,
             'gd': -9,
             'pts': 8},
            {'pos': 20,
             'team': 'Crystal Palace',
             'p': 10,
             'w': 2,
             'd': 1,
             'l': 7,
             'gf': 10,
             'ga': 24,
             'gd': -14,
             'pts': 7}],
  'scorers': [{'player': 'Erling Haaland', 'team': 'Manchester City', 'goals': 9},
              {'player': 'Alexander Isak', 'team': 'Liverpool', 'goals': 7},
              {'player': 'Thierno Barry', 'team': 'Everton', 'goals': 6},
              {'player': 'Nicolas Jackson', 'team': 'Aston Villa', 'goals': 6},
              {'player': 'Evanilson', 'team': 'Bournemouth', 'goals': 5},
              {'player': 'João Pedro', 'team': 'Chelsea', 'goals': 5},
              {'player': 'Rayan Cherki', 'team': 'Manchester City', 'goals': 5},
              {'player': 'Morgan Rogers', 'team': 'Chelsea', 'goals': 5},
              {'player': 'Marcus Tavernier', 'team': 'Bournemouth', 'goals': 5},
              {'player': 'Bryan Mbeumo', 'team': 'Manchester United', 'goals': 4}],
  'meta': 'Premier League 2026-27 table: Arsenal lead with 27 points, Brighton & Hove Albion 22, Manchester '
          'City 21 — Top scorers, Matchweek 11 fixtures (21–23 November) and results.'},
 {'id': 'la-liga',
  'name': 'La Liga',
  'short': 'La Liga',
  'country': 'Spain',
  'season': '2026-27',
  'round': 'Matchweek 12',
  'next_round': 'Matchweek 13 — 20–23 November 2026',
  'source': 'thestatsapi.com (18 November 2026, 22:47 UTC) + cross-checked with laligatable.co andsportsbetting3.com — '
            'Top scorers: renderfoot.com (18 November 2026) + cross-checked with fotmob.com andmoroccoworldnews.com',
  'table': [{'pos': 1,
             'team': 'FC Barcelona',
             'p': 12,
             'w': 11,
             'd': 0,
             'l': 1,
             'gf': 48,
             'ga': 13,
             'gd': 35,
             'pts': 33},
            {'pos': 2,
             'team': 'Real Madrid',
             'p': 12,
             'w': 10,
             'd': 0,
             'l': 2,
             'gf': 31,
             'ga': 10,
             'gd': 21,
             'pts': 30},
            {'pos': 3,
             'team': 'Atlético Madrid',
             'p': 12,
             'w': 9,
             'd': 1,
             'l': 2,
             'gf': 23,
             'ga': 10,
             'gd': 13,
             'pts': 28},
            {'pos': 4,
             'team': 'Real Betis',
             'p': 12,
             'w': 8,
             'd': 2,
             'l': 2,
             'gf': 20,
             'ga': 15,
             'gd': 5,
             'pts': 26},
            {'pos': 5,
             'team': 'Real Sociedad',
             'p': 12,
             'w': 7,
             'd': 1,
             'l': 4,
             'gf': 21,
             'ga': 20,
             'gd': 1,
             'pts': 22},
            {'pos': 6,
             'team': 'Sevilla FC',
             'p': 12,
             'w': 5,
             'd': 3,
             'l': 4,
             'gf': 17,
             'ga': 19,
             'gd': -2,
             'pts': 18},
            {'pos': 7,
             'team': 'Athletic Bilbao',
             'p': 11,
             'w': 4,
             'd': 4,
             'l': 3,
             'gf': 15,
             'ga': 11,
             'gd': 4,
             'pts': 16},
            {'pos': 8,
             'team': 'Villarreal CF',
             'p': 12,
             'w': 4,
             'd': 3,
             'l': 5,
             'gf': 17,
             'ga': 15,
             'gd': 2,
             'pts': 15},
            {'pos': 9,
             'team': 'Deportivo La Coruña',
             'p': 12,
             'w': 3,
             'd': 6,
             'l': 3,
             'gf': 15,
             'ga': 14,
             'gd': 1,
             'pts': 15},
            {'pos': 10,
             'team': 'Racing Santander',
             'p': 12,
             'w': 4,
             'd': 2,
             'l': 6,
             'gf': 17,
             'ga': 30,
             'gd': -13,
             'pts': 14},
            {'pos': 11,
             'team': 'Celta Vigo',
             'p': 12,
             'w': 2,
             'd': 7,
             'l': 3,
             'gf': 10,
             'ga': 10,
             'gd': 0,
             'pts': 13},
            {'pos': 12,
             'team': 'Deportivo Alavés',
             'p': 12,
             'w': 3,
             'd': 4,
             'l': 5,
             'gf': 15,
             'ga': 17,
             'gd': -2,
             'pts': 13},
            {'pos': 13,
             'team': 'RCD Espanyol',
             'p': 12,
             'w': 3,
             'd': 3,
             'l': 6,
             'gf': 13,
             'ga': 14,
             'gd': -1,
             'pts': 12},
            {'pos': 14,
             'team': 'Rayo Vallecano',
             'p': 11,
             'w': 3,
             'd': 3,
             'l': 5,
             'gf': 15,
             'ga': 21,
             'gd': -6,
             'pts': 12},
            {'pos': 15,
             'team': 'Getafe CF',
             'p': 12,
             'w': 3,
             'd': 3,
             'l': 6,
             'gf': 8,
             'ga': 18,
             'gd': -10,
             'pts': 12},
            {'pos': 16,
             'team': 'CA Osasuna',
             'p': 12,
             'w': 3,
             'd': 3,
             'l': 6,
             'gf': 12,
             'ga': 23,
             'gd': -11,
             'pts': 12},
            {'pos': 17,
             'team': 'Levante UD',
             'p': 12,
             'w': 2,
             'd': 5,
             'l': 5,
             'gf': 16,
             'ga': 21,
             'gd': -5,
             'pts': 11},
            {'pos': 18,
             'team': 'Elche CF',
             'p': 12,
             'w': 2,
             'd': 4,
             'l': 6,
             'gf': 14,
             'ga': 20,
             'gd': -6,
             'pts': 10},
            {'pos': 19,
             'team': 'Valencia CF',
             'p': 12,
             'w': 2,
             'd': 3,
             'l': 7,
             'gf': 8,
             'ga': 20,
             'gd': -12,
             'pts': 9},
            {'pos': 20,
             'team': 'Málaga CF',
             'p': 12,
             'w': 0,
             'd': 5,
             'l': 7,
             'gf': 9,
             'ga': 23,
             'gd': -14,
             'pts': 5}],
  'scorers': [{'player': 'Raphinha', 'team': 'FC Barcelona', 'goals': 15},
              {'player': 'Kylian Mbappé', 'team': 'Real Madrid', 'goals': 13},
              {'player': 'Lamine Yamal', 'team': 'FC Barcelona', 'goals': 10},
              {'player': 'Yassir Zabiri', 'team': 'Racing Santander', 'goals': 9},
              {'player': 'Ante Budimir', 'team': 'CA Osasuna', 'goals': 8},
              {'player': 'Fermín López', 'team': 'FC Barcelona', 'goals': 7},
              {'player': 'Sergio Camello', 'team': 'Rayo Vallecano', 'goals': 7},
              {'player': 'Roberto Fernández', 'team': 'RCD Espanyol', 'goals': 6},
              {'player': 'Fer Niño', 'team': 'Elche CF', 'goals': 6},
              {'player': 'Álex Baena', 'team': 'Atlético Madrid', 'goals': 5}],
  'meta': 'La Liga 2026-27 table: FC Barcelona lead with 33 points, Real Madrid 30, Atlético 28 — Raphinha '
          'top scorer La Liga with 15 goals, Matchweek 13 fixtures and results.'},
 {'id': 'serie-a',
  'name': 'Serie A',
  'short': 'Serie A',
  'country': 'Italy',
  'season': '2026-27',
  'round': 'Matchweek 11',
  'next_round': 'Matchweek 12 — 21–23 November 2026',
  'source': 'thestatsapi.com (18 November 2026, 22:53 UTC) + cross-checked with scanodds.com andpitchlabstats.com — '
            'Top scorers: renderfoot.com (18 November 2026) + cross-checked with pitchlabstats.com andmyfootballfacts.com',
  'table': [{'pos': 1,
             'team': 'SS Lazio',
             'p': 11,
             'w': 9,
             'd': 2,
             'l': 0,
             'gf': 25,
             'ga': 9,
             'gd': 16,
             'pts': 29},
            {'pos': 2,
             'team': 'Inter Milan',
             'p': 11,
             'w': 9,
             'd': 1,
             'l': 1,
             'gf': 28,
             'ga': 13,
             'gd': 15,
             'pts': 28},
            {'pos': 3,
             'team': 'AS Roma',
             'p': 11,
             'w': 8,
             'd': 3,
             'l': 0,
             'gf': 31,
             'ga': 10,
             'gd': 21,
             'pts': 27},
            {'pos': 4,
             'team': 'AC Milan',
             'p': 11,
             'w': 7,
             'd': 3,
             'l': 1,
             'gf': 23,
             'ga': 13,
             'gd': 10,
             'pts': 24},
            {'pos': 5,
             'team': 'Como 1907',
             'p': 11,
             'w': 7,
             'd': 2,
             'l': 2,
             'gf': 18,
             'ga': 10,
             'gd': 8,
             'pts': 23},
            {'pos': 6,
             'team': 'Frosinone Calcio',
             'p': 11,
             'w': 6,
             'd': 2,
             'l': 3,
             'gf': 24,
             'ga': 15,
             'gd': 9,
             'pts': 20},
            {'pos': 7,
             'team': 'Juventus FC',
             'p': 11,
             'w': 5,
             'd': 3,
             'l': 3,
             'gf': 15,
             'ga': 12,
             'gd': 3,
             'pts': 18},
            {'pos': 8,
             'team': 'Bologna FC',
             'p': 11,
             'w': 5,
             'd': 2,
             'l': 4,
             'gf': 16,
             'ga': 14,
             'gd': 2,
             'pts': 17},
            {'pos': 9,
             'team': 'Cagliari Calcio',
             'p': 11,
             'w': 5,
             'd': 1,
             'l': 5,
             'gf': 10,
             'ga': 15,
             'gd': -5,
             'pts': 16},
            {'pos': 10,
             'team': 'SSC Napoli',
             'p': 11,
             'w': 4,
             'd': 3,
             'l': 4,
             'gf': 18,
             'ga': 14,
             'gd': 4,
             'pts': 15},
            {'pos': 11,
             'team': 'Torino FC',
             'p': 11,
             'w': 4,
             'd': 2,
             'l': 5,
             'gf': 15,
             'ga': 17,
             'gd': -2,
             'pts': 14},
            {'pos': 12,
             'team': 'Atalanta BC',
             'p': 11,
             'w': 4,
             'd': 2,
             'l': 5,
             'gf': 17,
             'ga': 20,
             'gd': -3,
             'pts': 14},
            {'pos': 13,
             'team': 'Genoa CFC',
             'p': 11,
             'w': 4,
             'd': 1,
             'l': 6,
             'gf': 11,
             'ga': 16,
             'gd': -5,
             'pts': 13},
            {'pos': 14,
             'team': 'US Lecce',
             'p': 11,
             'w': 3,
             'd': 1,
             'l': 7,
             'gf': 12,
             'ga': 22,
             'gd': -10,
             'pts': 10},
            {'pos': 15,
             'team': 'ACF Fiorentina',
             'p': 11,
             'w': 2,
             'd': 3,
             'l': 6,
             'gf': 17,
             'ga': 25,
             'gd': -8,
             'pts': 9},
            {'pos': 16,
             'team': 'Parma Calcio',
             'p': 11,
             'w': 2,
             'd': 2,
             'l': 7,
             'gf': 9,
             'ga': 17,
             'gd': -8,
             'pts': 8},
            {'pos': 17,
             'team': 'US Sassuolo Calcio',
             'p': 11,
             'w': 2,
             'd': 2,
             'l': 7,
             'gf': 16,
             'ga': 29,
             'gd': -13,
             'pts': 8},
            {'pos': 18,
             'team': 'AC Monza',
             'p': 11,
             'w': 2,
             'd': 1,
             'l': 8,
             'gf': 17,
             'ga': 25,
             'gd': -8,
             'pts': 7},
            {'pos': 19,
             'team': 'Venezia FC',
             'p': 11,
             'w': 2,
             'd': 0,
             'l': 9,
             'gf': 8,
             'ga': 21,
             'gd': -13,
             'pts': 6},
            {'pos': 20,
             'team': 'Udinese Calcio',
             'p': 11,
             'w': 1,
             'd': 2,
             'l': 8,
             'gf': 12,
             'ga': 25,
             'gd': -13,
             'pts': 5}],
  'scorers': [{'player': 'Gustavo Varela', 'team': 'AC Monza', 'goals': 9},
              {'player': 'Donyell Malen', 'team': 'AS Roma', 'goals': 8},
              {'player': 'Antonio Raimondo', 'team': 'Frosinone Calcio', 'goals': 8},
              {'player': 'Nikola Krstovic', 'team': 'Atalanta BC', 'goals': 7},
              {'player': 'Marcus Thuram', 'team': 'Inter Milan', 'goals': 6},
              {'player': 'Adrien Rabiot', 'team': 'AC Milan', 'goals': 5},
              {'player': 'Tasos Douvikas', 'team': 'Como 1907', 'goals': 5},
              {'player': 'Alphadjo Cissè', 'team': 'AC Milan', 'goals': 5},
              {'player': 'Giacomo Calo', 'team': 'Frosinone Calcio', 'goals': 5},
              {'player': 'Daniel Maldini', 'team': 'Cagliari Calcio', 'goals': 5}],
  'meta': 'Serie A 2026-27 table: SS Lazio lead with 29 points, Inter 28, AS Roma 27 — Top scorers, '
          'Matchweek 12 fixtures (21–23 November) and results.'},
 {'id': 'bundesliga',
  'name': 'Bundesliga',
  'short': 'Bundesliga',
  'country': 'Germany',
  'season': '2026-27',
  'round': 'Matchweek 9',
  'next_round': 'Matchweek 10 — 20–22 November 2026',
  'source': 'thestatsapi.com (18 November 2026, 22:51 UTC) + cross-checked with bettingtips.africa andturingstats.com — '
            'Top scorers: bundesliga.com + renderfoot.com (18 November 2026)',
  'table': [{'pos': 1,
             'team': 'FC Bayern Munich',
             'p': 9,
             'w': 6,
             'd': 3,
             'l': 0,
             'gf': 29,
             'ga': 9,
             'gd': 20,
             'pts': 21},
            {'pos': 2,
             'team': 'Borussia Dortmund',
             'p': 9,
             'w': 6,
             'd': 3,
             'l': 0,
             'gf': 16,
             'ga': 7,
             'gd': 9,
             'pts': 21},
            {'pos': 3,
             'team': 'SC Freiburg',
             'p': 9,
             'w': 6,
             'd': 1,
             'l': 2,
             'gf': 20,
             'ga': 10,
             'gd': 10,
             'pts': 19},
            {'pos': 4,
             'team': 'RB Leipzig',
             'p': 9,
             'w': 6,
             'd': 0,
             'l': 3,
             'gf': 27,
             'ga': 13,
             'gd': 14,
             'pts': 18},
            {'pos': 5,
             'team': 'Bayer 04 Leverkusen',
             'p': 9,
             'w': 5,
             'd': 1,
             'l': 3,
             'gf': 20,
             'ga': 17,
             'gd': 3,
             'pts': 16},
            {'pos': 6,
             'team': 'SV Werder Bremen',
             'p': 9,
             'w': 4,
             'd': 3,
             'l': 2,
             'gf': 17,
             'ga': 15,
             'gd': 2,
             'pts': 15},
            {'pos': 7,
             'team': 'SV Elversberg',
             'p': 9,
             'w': 4,
             'd': 1,
             'l': 4,
             'gf': 17,
             'ga': 18,
             'gd': -1,
             'pts': 13},
            {'pos': 8,
             'team': 'VfB Stuttgart',
             'p': 9,
             'w': 4,
             'd': 0,
             'l': 5,
             'gf': 15,
             'ga': 15,
             'gd': 0,
             'pts': 12},
            {'pos': 9,
             'team': 'TSG Hoffenheim',
             'p': 9,
             'w': 4,
             'd': 0,
             'l': 5,
             'gf': 16,
             'ga': 17,
             'gd': -1,
             'pts': 12},
            {'pos': 10,
             'team': 'Eintracht Frankfurt',
             'p': 9,
             'w': 3,
             'd': 3,
             'l': 3,
             'gf': 15,
             'ga': 20,
             'gd': -5,
             'pts': 12},
            {'pos': 11,
             'team': 'Hamburger SV',
             'p': 9,
             'w': 4,
             'd': 0,
             'l': 5,
             'gf': 10,
             'ga': 20,
             'gd': -10,
             'pts': 12},
            {'pos': 12,
             'team': '1. FSV Mainz 05',
             'p': 9,
             'w': 3,
             'd': 1,
             'l': 5,
             'gf': 18,
             'ga': 19,
             'gd': -1,
             'pts': 10},
            {'pos': 13,
             'team': 'SC Paderborn 07',
             'p': 9,
             'w': 2,
             'd': 4,
             'l': 3,
             'gf': 8,
             'ga': 11,
             'gd': -3,
             'pts': 10},
            {'pos': 14,
             'team': 'FC Augsburg',
             'p': 9,
             'w': 2,
             'd': 3,
             'l': 4,
             'gf': 20,
             'ga': 20,
             'gd': 0,
             'pts': 9},
            {'pos': 15,
             'team': '1. FC Köln',
             'p': 9,
             'w': 2,
             'd': 3,
             'l': 4,
             'gf': 10,
             'ga': 14,
             'gd': -4,
             'pts': 9},
            {'pos': 16,
             'team': '1. FC Union Berlin',
             'p': 9,
             'w': 1,
             'd': 4,
             'l': 4,
             'gf': 7,
             'ga': 21,
             'gd': -14,
             'pts': 7},
            {'pos': 17,
             'team': 'FC Schalke 04',
             'p': 9,
             'w': 1,
             'd': 3,
             'l': 5,
             'gf': 5,
             'ga': 11,
             'gd': -6,
             'pts': 6},
            {'pos': 18,
             'team': 'Borussia Mönchengladbach',
             'p': 9,
             'w': 1,
             'd': 1,
             'l': 7,
             'gf': 12,
             'ga': 25,
             'gd': -13,
             'pts': 4}],
  'scorers': [{'player': 'Niclas Füllkrug', 'team': 'SV Werder Bremen', 'goals': 9},
              {'player': 'Patrik Schick', 'team': 'Bayer 04 Leverkusen', 'goals': 8},
              {'player': 'Michael Olise', 'team': 'FC Bayern Munich', 'goals': 6},
              {'player': 'Younes Ebnoutalib', 'team': 'Eintracht Frankfurt', 'goals': 6},
              {'player': 'Phillip Tietz', 'team': '1. FSV Mainz 05', 'goals': 6},
              {'player': 'Christopher Nkunku', 'team': 'RB Leipzig', 'goals': 5},
              {'player': 'Jonathan Burkardt', 'team': 'Eintracht Frankfurt', 'goals': 5},
              {'player': 'Ermedin Demirovic', 'team': 'VfB Stuttgart', 'goals': 5},
              {'player': 'Yuito Suzuki', 'team': 'SC Freiburg', 'goals': 5},
              {'player': 'Rômulo', 'team': 'RB Leipzig', 'goals': 5}],
  'meta': 'Bundesliga 2026-27 table: FC Bayern Munich and Dortmund level on 21 points, SC Freiburg 19 — '
          'Top scorers, Matchweek 10 fixtures (20–22 November) and results.'},
 {'id': 'ligue-1',
  'name': 'Ligue 1',
  'short': 'Ligue 1',
  'country': 'France',
  'season': '2026-27',
  'round': 'Matchweek 10',
  'next_round': 'Matchweek 11 — 20–22 November 2026',
  'source': 'thestatsapi.com (18 November 2026, 22:31 UTC) + cross-checked with xgstats.com andligue1schedule.com — '
            'Top scorers: renderfoot.com (18 November 2026) + cross-checked with myfootballfacts.com andsocerstreams.org',
  'table': [{'pos': 1,
             'team': 'Paris Saint-Germain',
             'p': 10,
             'w': 7,
             'd': 2,
             'l': 1,
             'gf': 22,
             'ga': 10,
             'gd': 12,
             'pts': 23},
            {'pos': 2, 'team': 'Lille OSC', 'p': 10, 'w': 6, 'd': 3, 'l': 1, 'gf': 14, 'ga': 7, 'gd': 7, 'pts': 21},
            {'pos': 3,
             'team': 'Paris FC',
             'p': 10,
             'w': 6,
             'd': 2,
             'l': 2,
             'gf': 17,
             'ga': 10,
             'gd': 7,
             'pts': 20},
            {'pos': 4,
             'team': 'Olympique de Marseille',
             'p': 10,
             'w': 6,
             'd': 0,
             'l': 4,
             'gf': 22,
             'ga': 14,
             'gd': 8,
             'pts': 18},
            {'pos': 5,
             'team': 'Olympique Lyonnais',
             'p': 10,
             'w': 5,
             'd': 2,
             'l': 3,
             'gf': 15,
             'ga': 9,
             'gd': 6,
             'pts': 17},
            {'pos': 6,
             'team': 'OGC Nice',
             'p': 10,
             'w': 5,
             'd': 2,
             'l': 3,
             'gf': 15,
             'ga': 12,
             'gd': 3,
             'pts': 17},
            {'pos': 7,
             'team': 'AS Monaco',
             'p': 10,
             'w': 4,
             'd': 4,
             'l': 2,
             'gf': 13,
             'ga': 11,
             'gd': 2,
             'pts': 16},
            {'pos': 8,
             'team': 'Stade Rennais',
             'p': 10,
             'w': 5,
             'd': 1,
             'l': 4,
             'gf': 21,
             'ga': 21,
             'gd': 0,
             'pts': 16},
            {'pos': 9,
             'team': 'Stade Brestois 29',
             'p': 10,
             'w': 4,
             'd': 3,
             'l': 3,
             'gf': 18,
             'ga': 12,
             'gd': 6,
             'pts': 15},
            {'pos': 10,
             'team': 'FC Lorient',
             'p': 10,
             'w': 4,
             'd': 3,
             'l': 3,
             'gf': 9,
             'ga': 8,
             'gd': 1,
             'pts': 15},
            {'pos': 11,
             'team': 'RC Lens',
             'p': 10,
             'w': 4,
             'd': 1,
             'l': 5,
             'gf': 17,
             'ga': 15,
             'gd': 2,
             'pts': 13},
            {'pos': 12,
             'team': 'Toulouse FC',
             'p': 10,
             'w': 3,
             'd': 4,
             'l': 3,
             'gf': 15,
             'ga': 14,
             'gd': 1,
             'pts': 13},
            {'pos': 13,
             'team': 'RC Strasbourg Alsace',
             'p': 10,
             'w': 3,
             'd': 1,
             'l': 6,
             'gf': 18,
             'ga': 22,
             'gd': -4,
             'pts': 10},
            {'pos': 14,
             'team': 'AJ Auxerre',
             'p': 10,
             'w': 3,
             'd': 1,
             'l': 6,
             'gf': 13,
             'ga': 24,
             'gd': -11,
             'pts': 10},
            {'pos': 15,
             'team': 'Le Mans FC',
             'p': 10,
             'w': 1,
             'd': 5,
             'l': 4,
             'gf': 12,
             'ga': 19,
             'gd': -7,
             'pts': 8},
            {'pos': 16,
             'team': 'Angers SCO',
             'p': 10,
             'w': 2,
             'd': 2,
             'l': 6,
             'gf': 9,
             'ga': 19,
             'gd': -10,
             'pts': 8},
            {'pos': 17,
             'team': 'ESTAC Troyes',
             'p': 10,
             'w': 2,
             'd': 2,
             'l': 6,
             'gf': 7,
             'ga': 17,
             'gd': -10,
             'pts': 8},
            {'pos': 18,
             'team': 'Le Havre AC',
             'p': 10,
             'w': 0,
             'd': 2,
             'l': 8,
             'gf': 9,
             'ga': 22,
             'gd': -13,
             'pts': 2}],
  'scorers': [{'player': 'Lassine Sinayoko', 'team': 'Paris FC', 'goals': 9},
              {'player': 'Amine Gouiri', 'team': 'Olympique de Marseille', 'goals': 7},
              {'player': 'Esteban Lepaul', 'team': 'Stade Rennais', 'goals': 7},
              {'player': 'Cameron Archer', 'team': 'AJ Auxerre', 'goals': 6},
              {'player': 'Elye Wahi', 'team': 'OGC Nice', 'goals': 6},
              {'player': 'Ludovic Ajorque', 'team': 'Stade Brestois 29', 'goals': 5},
              {'player': 'Boulaye Dia', 'team': 'Stade Rennais', 'goals': 5},
              {'player': 'Casper Tengstedt', 'team': 'Toulouse FC', 'goals': 5},
              {'player': 'Florian Thauvin', 'team': 'RC Lens', 'goals': 5},
              {'player': 'Gessime Yassine', 'team': 'RC Strasbourg Alsace', 'goals': 4}],
  'meta': 'Ligue 1 2026-27 table: Paris Saint-Germain lead with 23 points, Lille OSC 21, Paris FC 20 — '
          'Top scorers, Matchweek 11 fixtures (20–22 November) and results.'},
 {'id': 'botola',
  'name': 'Botola Pro',
  'short': 'Botola Pro',
  'country': 'Morocco',
  'season': '2026-27',
  'round': 'Matchweek 7',
  'next_round': 'Matchweek 8 — date to be confirmed',
  'source': 'Wikipedia 2026–27 Botola Pro — Source: FRMF.ma (fixtures up to 09 November 2026) + cross-checked with '
            'pitchlabstats.com andglobalsportsarchive.com — Top scorers: pitchlabstats.com + Wikipedia (FRMF) — '
            'Note: match Wydad–WS Témara was awarded 3–0 to Wydad by LNFP decision on 07 November 2026 (ineligible player), '
            'with one point deducted from WS Témara',
  'table': [{'pos': 1,
             'team': 'Kawkab Marrakech',
             'p': 7,
             'w': 5,
             'd': 1,
             'l': 1,
             'gf': 10,
             'ga': 6,
             'gd': 4,
             'pts': 16},
            {'pos': 2,
             'team': 'CODM Meknès',
             'p': 7,
             'w': 4,
             'd': 2,
             'l': 1,
             'gf': 10,
             'ga': 4,
             'gd': 6,
             'pts': 14},
            {'pos': 3,
             'team': 'Wydad AC',
             'p': 7,
             'w': 4,
             'd': 2,
             'l': 1,
             'gf': 9,
             'ga': 3,
             'gd': 6,
             'pts': 14},
            {'pos': 4,
             'team': 'Raja CA',
             'p': 7,
             'w': 3,
             'd': 3,
             'l': 1,
             'gf': 7,
             'ga': 5,
             'gd': 2,
             'pts': 12},
            {'pos': 5,
             'team': 'AS FAR',
             'p': 6,
             'w': 3,
             'd': 2,
             'l': 1,
             'gf': 9,
             'ga': 5,
             'gd': 4,
             'pts': 11},
            {'pos': 6,
             'team': 'Maghreb AS',
             'p': 7,
             'w': 3,
             'd': 2,
             'l': 2,
             'gf': 6,
             'ga': 5,
             'gd': 1,
             'pts': 11},
            {'pos': 7,
             'team': 'IR Tanger',
             'p': 7,
             'w': 3,
             'd': 1,
             'l': 3,
             'gf': 8,
             'ga': 9,
             'gd': -1,
             'pts': 10},
            {'pos': 8,
             'team': 'Hassania Agadir',
             'p': 7,
             'w': 2,
             'd': 3,
             'l': 2,
             'gf': 14,
             'ga': 12,
             'gd': 2,
             'pts': 9},
            {'pos': 9,
             'team': 'Union Touarga',
             'p': 7,
             'w': 2,
             'd': 2,
             'l': 3,
             'gf': 4,
             'ga': 6,
             'gd': -2,
             'pts': 8},
            {'pos': 10,
             'team': 'DH Jadida',
             'p': 7,
             'w': 2,
             'd': 2,
             'l': 3,
             'gf': 14,
             'ga': 16,
             'gd': -2,
             'pts': 8},
            {'pos': 11,
             'team': 'FUS Rabat',
             'p': 7,
             'w': 2,
             'd': 2,
             'l': 3,
             'gf': 4,
             'ga': 5,
             'gd': -1,
             'pts': 8},
            {'pos': 12,
             'team': 'RS Berkane',
             'p': 6,
             'w': 1,
             'd': 5,
             'l': 0,
             'gf': 6,
             'ga': 4,
             'gd': 2,
             'pts': 8},
            {'pos': 13,
             'team': 'US Amal Tiznit',
             'p': 7,
             'w': 2,
             'd': 1,
             'l': 4,
             'gf': 8,
             'ga': 12,
             'gd': -4,
             'pts': 7},
            {'pos': 14,
             'team': 'WS Témara',
             'p': 7,
             'w': 2,
             'd': 1,
             'l': 4,
             'gf': 5,
             'ga': 7,
             'gd': -2,
             'pts': 6},
            {'pos': 15,
             'team': 'MA Tétouan',
             'p': 7,
             'w': 0,
             'd': 3,
             'l': 4,
             'gf': 2,
             'ga': 10,
             'gd': -8,
             'pts': 3},
            {'pos': 16,
             'team': 'RCA Zemamra',
             'p': 7,
             'w': 0,
             'd': 2,
             'l': 5,
             'gf': 6,
             'ga': 13,
             'gd': -7,
             'pts': 2}],
  'scorers': [{'player': 'Imad Riahi', 'team': 'Hassania Agadir', 'goals': 6},
              {'player': 'Abderrazak Ennakouss', 'team': 'DH Jadida', 'goals': 6},
              {'player': 'Youssef El Fahli', 'team': 'AS FAR', 'goals': 5},
              {'player': 'Zakaria Essalhi', 'team': 'US Amal Tiznit', 'goals': 5},
              {'player': 'Silvère Ganvoula', 'team': 'Wydad AC', 'goals': 4},
              {'player': 'Saleh Essallami', 'team': 'Kawkab Marrakech', 'goals': 4},
              {'player': 'Hamza El Wasti', 'team': 'CODM Meknès', 'goals': 3},
              {'player': 'Mouad Mouchtanim', 'team': 'DH Jadida', 'goals': 2},
              {'player': 'Tshegofatso Mabasa', 'team': 'Maghreb AS', 'goals': 2},
              {'player': 'Ayoub Maamouri', 'team': 'Kawkab Marrakech', 'goals': 2}],
  'meta': 'Botola Pro 2026-27 table: Kawkab Marrakech lead with 16 points, CODM Meknès '
          'and Wydad 14, Raja 12 — Matchweek 8 fixtures and results.'}]
# Fixtures — times are Morocco time (UTC+1). time=None = time not verified.
def fx(fid, home, away, league, league_name, date, time, source, date_label=None,
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
    return d

UPCOMING = [
 fx('bayern-koln-2026-11-20', 'FC Bayern Munich', '1. FC Köln', 'bundesliga', 'Bundesliga', '2026-11-20', '20:30', 'kickofflens.com + football.mib.news (19:30 UTC)', venue='Allianz Arena, Munich', channel='beIN Sports'),
 fx('athletic-espanyol-2026-11-20', 'Athletic Bilbao', 'RCD Espanyol', 'la-liga', 'La Liga', '2026-11-20', '21:00', 'kickofflens.com + football.mib.news (20:00 UTC)', venue='San Mamés, Bilbao', channel='beIN Sports'),
 fx('troyes-lehavre-2026-11-20', 'ESTAC Troyes', 'Le Havre AC', 'ligue-1', 'Ligue 1', '2026-11-20', '20:45', 'vavel.com (14:45 ET = 19:45 UTC) + football.mib.news', venue='Stade de l’Aube, ESTAC Troyes', channel='beIN Sports'),
 fx('man-city-fulham-2026-11-21', 'Manchester City', 'Fulham', 'premier-league', 'Premier League', '2026-11-21', '13:30', 'premierleague.com + nbcsports.com (12:30 UK)', venue='Etihad Stadium, Manchester', channel='beIN Sports'),
 fx('aston-villa-sunderland-2026-11-21', 'Aston Villa', 'Sunderland', 'premier-league', 'Premier League', '2026-11-21', '16:00', 'premierleague.com (15:00 UK)', venue='Villa Park, Birmingham', channel='beIN Sports'),
 fx('bournemouth-nottingham-2026-11-21', 'Bournemouth', 'Nottingham Forest', 'premier-league', 'Premier League', '2026-11-21', '16:00', 'premierleague.com (15:00 UK)', venue='Vitality Stadium, Bournemouth', channel='beIN Sports'),
 fx('coventry-crystal-palace-2026-11-21', 'Coventry City', 'Crystal Palace', 'premier-league', 'Premier League', '2026-11-21', '16:00', 'livescore.in + premierleague.com (15:00 UK)', venue='Coventry Building Society Arena, Coventry', channel='beIN Sports'),
 fx('tottenham-ipswich-2026-11-21', 'Tottenham Hotspur', 'Ipswich Town', 'premier-league', 'Premier League', '2026-11-21', '16:00', 'livescore.in + premierleague.com (15:00 UK)', venue='Tottenham Hotspur Stadium, London', channel='beIN Sports'),
 fx('newcastle-arsenal-2026-11-21', 'Newcastle United', 'Arsenal', 'premier-league', 'Premier League', '2026-11-21', '18:30', 'premierleague.com + nbcsports.com (17:30 UK)', venue='St. James’ Park, Newcastle', channel='beIN Sports', referee='Chris Kavanagh'),
 fx('real-madrid-celta-2026-11-21', 'Real Madrid', 'Celta Vigo', 'la-liga', 'La Liga', '2026-11-21', None, 'laligatable.co (Real Madrid’s next match — kick-off time TBC)', venue='Santiago Bernabéu, Madrid', channel='beIN Sports'),
 fx('union-leipzig-2026-11-21', '1. FC Union Berlin', 'RB Leipzig', 'bundesliga', 'Bundesliga', '2026-11-21', '15:30', 'fcstats.com (09:30 ET = 15:30 CET)', venue='Stadion An der Alten Försterei, Berlin', channel='beIN Sports'),
 fx('leverkusen-paderborn-2026-11-21', 'Bayer 04 Leverkusen', 'SC Paderborn 07', 'bundesliga', 'Bundesliga', '2026-11-21', '15:30', 'fcstats.com (09:30 ET = 15:30 CET)', venue='BayArena, Leverkusen', channel='beIN Sports'),
 fx('gladbach-dortmund-2026-11-21', 'Borussia Mönchengladbach', 'Borussia Dortmund', 'bundesliga', 'Bundesliga', '2026-11-21', '15:30', 'fcstats.com (09:30 ET = 15:30 CET)', venue='Borussia-Park, Mönchengladbach', channel='beIN Sports'),
 fx('augsburg-mainz-2026-11-21', 'FC Augsburg', '1. FSV Mainz 05', 'bundesliga', 'Bundesliga', '2026-11-21', '15:30', 'fcstats.com (09:30 ET = 15:30 CET)', venue='WWK Arena, FC Augsburg', channel='beIN Sports'),
 fx('nice-psg-2026-11-21', 'OGC Nice', 'Paris Saint-Germain', 'ligue-1', 'Ligue 1', '2026-11-21', '17:15', 'vavel.com (11:15 ET = 16:15 UTC)', venue='Allianz Riviera, OGC Nice', channel='beIN Sports'),
 fx('lille-lyon-2026-11-21', 'Lille OSC', 'Olympique Lyonnais', 'ligue-1', 'Ligue 1', '2026-11-21', '20:45', 'vavel.com (14:45 ET = 19:45 UTC)', venue='Decathlon Arena - Stade Pierre-Mauroy, Lille OSC', channel='beIN Sports'),
 fx('hull-brighton-2026-11-22', 'Hull City', 'Brighton & Hove Albion', 'premier-league', 'Premier League', '2026-11-22', '15:00', 'livescore.in (06:00 PT = 14:00 UTC)', venue='The MKM Stadium, Hull', channel='beIN Sports'),
 fx('liverpool-manutd-2026-11-22', 'Liverpool', 'Manchester United', 'premier-league', 'Premier League', '2026-11-22', '18:30', 'premierleague.com + nbcsports.com (16:30 UK)', venue='Anfield, Liverpool', channel='beIN Sports'),
 fx('barcelona-villarreal-2026-11-22', 'FC Barcelona', 'Villarreal CF', 'la-liga', 'La Liga', '2026-11-22', None, 'laligatable.co (Barcelona’s next match — kick-off time TBC)', venue_note='To be confirmed — Camp Nou or Estadi Olímpic Lluís Companys (Montjuïc)', channel='beIN Sports'),
 fx('atalanta-inter-2026-11-22', 'Atalanta BC', 'Inter Milan', 'serie-a', 'Serie A', '2026-11-22', None, 'showupandplay.com (weekend of 21–23 November — exact day TBC)', date_label='21–23 November 2026', venue='Gewiss Stadium, Bergamo', channel='beIN Sports'),
 fx('juventus-venezia-2026-11-22', 'Juventus FC', 'Venezia FC', 'serie-a', 'Serie A', '2026-11-22', None, 'Facebook post FAFG (weekend of 21–23 November — exact day TBC)', date_label='21–23 November 2026', venue='Allianz Stadium, Torino FC', channel='beIN Sports'),
 fx('brentford-everton-2026-11-23', 'Brentford', 'Everton', 'premier-league', 'Premier League', '2026-11-23', '21:00', 'livescore.in (12:00 PT = 20:00 UTC)', venue='Gtech Community Stadium, London', channel='beIN Sports'),
]
# Last verified results: final weekend before the international break (7–8 Nov 2026).
# Day-per-match NOT individually verified — grouped as one weekend, source noted.
RESULTS = [{'id': 'mainz-bayern-2026-11-08',
  'home': '1. FSV Mainz 05',
  'away': 'FC Bayern Munich',
  'home_goals': 1,
  'away_goals': 2,
  'league': 'bundesliga',
  'league_name': 'Bundesliga',
  'date': '2026-11-08',
  'status': 'finished',
  'source': 'showupandplay.com (report 08 November 2026)',
  'stats': {'possession_home': 31,
            'possession_away': 69,
            'shots_home': 11,
            'shots_away': 26,
            'shots_on_target_home': 1,
            'shots_on_target_away': 9,
            'corners_home': 7,
            'corners_away': 8,
            'source': 'previaxi.com + soccerpunter.com + sportmeridian.com (18 November 2026) — played 07 November '
                      '2026 14:30 UTC'},
  'venue': 'MEWA Arena, 1. FSV Mainz 05',
  'channel': 'beIN Sports'},
 {'id': 'dortmund-elversberg-2026-11-08',
  'home': 'Borussia Dortmund',
  'away': 'SV Elversberg',
  'home_goals': 2,
  'away_goals': 1,
  'league': 'bundesliga',
  'league_name': 'Bundesliga',
  'date': '2026-11-08',
  'status': 'finished',
  'source': 'showupandplay.com (report 08 November 2026)',
  'stats': {'possession_home': 51,
            'possession_away': 49,
            'shots_home': 19,
            'shots_away': 16,
            'shots_on_target_home': 6,
            'shots_on_target_away': 7,
            'corners_home': 6,
            'corners_away': 6,
            'source': 'soccerpunter.com + matchreplays.com + sportmeridian.com (18 November 2026) — played 07 '
                      'November 2026 14:30 UTC'},
  'venue': 'Signal Iduna Park, Dortmund',
  'channel': 'beIN Sports'},
 {'id': 'napoli-lazio-2026-11-08',
  'home': 'SSC Napoli',
  'away': 'SS Lazio',
  'home_goals': 1,
  'away_goals': 1,
  'league': 'serie-a',
  'league_name': 'Serie A',
  'date': '2026-11-08',
  'status': 'finished',
  'source': 'showupandplay.com (report 08 November 2026)',
  'stats': {'possession_home': 49,
            'possession_away': 51,
            'shots_home': 15,
            'shots_away': 15,
            'shots_on_target_home': 6,
            'shots_on_target_away': 6,
            'corners_home': 6,
            'corners_away': 6,
            'source': 'skysports.com + moneyball-odds.com + yardbarker.com (18 November 2026)'},
  'venue': 'Stadio Diego Armando Maradona, SSC Napoli',
  'channel': 'beIN Sports'},
 {'id': 'inter-como-2026-11-08',
  'home': 'Inter Milan',
  'away': 'Como 1907',
  'home_goals': 2,
  'away_goals': 0,
  'league': 'serie-a',
  'league_name': 'Serie A',
  'date': '2026-11-08',
  'status': 'finished',
  'source': 'showupandplay.com (report 08 November 2026)',
  'stats': {'possession_home': 43,
            'possession_away': 57,
            'shots_home': 14,
            'shots_away': 5,
            'shots_on_target_home': 4,
            'shots_on_target_away': 1,
            'corners_home': 4,
            'corners_away': 2,
            'source': 'skysports.com + pitchlabstats.com + moneyball-odds.com (18 November 2026)'},
  'venue': 'Stadio Giuseppe Meazza, Milan',
  'channel': 'beIN Sports'},
 {'id': 'roma-sassuolo-2026-11-08',
  'home': 'AS Roma',
  'away': 'US Sassuolo Calcio',
  'home_goals': 3,
  'away_goals': 0,
  'league': 'serie-a',
  'league_name': 'Serie A',
  'date': '2026-11-08',
  'status': 'finished',
  'source': 'showupandplay.com (report 08 November 2026)',
  'stats': {'possession_home': 65,
            'possession_away': 35,
            'shots_home': 28,
            'shots_away': 6,
            'shots_on_target_home': 9,
            'shots_on_target_away': 1,
            'corners_home': 12,
            'corners_away': 1,
            'source': 'espn.ph + mykhel.com + soccerpunter.com (18 November 2026) — played 07 November 2026 19:45 '
                      'UTC'},
  'venue': 'Stadio Olimpico, AS Roma',
  'channel': 'beIN Sports'},
 {'id': 'genoa-milan-2026-11-08',
  'home': 'Genoa CFC',
  'away': 'AC Milan',
  'home_goals': 1,
  'away_goals': 2,
  'league': 'serie-a',
  'league_name': 'Serie A',
  'date': '2026-11-08',
  'status': 'finished',
  'source': 'showupandplay.com (report 08 November 2026)',
  'stats': {'possession_home': 38,
            'possession_away': 62,
            'shots_home': 17,
            'shots_away': 6,
            'shots_on_target_home': 5,
            'shots_on_target_away': 2,
            'corners_home': 3,
            'corners_away': 0,
            'source': 'skysports.com + moneyball-odds.com + livescore.com (18 November 2026)'},
  'venue': 'Stadio Luigi Ferraris, Genoa CFC',
  'channel': 'beIN Sports'},
 {'id': 'fiorentina-juventus-2026-11-08',
  'home': 'ACF Fiorentina',
  'away': 'Juventus FC',
  'home_goals': 2,
  'away_goals': 2,
  'league': 'serie-a',
  'league_name': 'Serie A',
  'date': '2026-11-08',
  'status': 'finished',
  'source': 'showupandplay.com (report 08 November 2026)',
  'stats': {'possession_home': 41,
            'possession_away': 59,
            'shots_home': 22,
            'shots_away': 18,
            'shots_on_target_home': 6,
            'shots_on_target_away': 6,
            'corners_home': 5,
            'corners_away': 12,
            'source': 'skysports.com + soccerway.com + flashscore.com (18 November 2026)'},
  'venue': 'Stadio Artemio Franchi, Florence',
  'channel': 'beIN Sports'}]
ALLOWED = ["premier-league", "la-liga", "serie-a", "bundesliga", "ligue-1", "botola"]
LEAGUE_BY_ID = {l["id"]: l for l in LEAGUES}

# ------------------------------------------------------------- logos ---
# Logos: read from data/logos.json (local files in assets/img/logos/ only).
# any a team without a verified logo displayed its name as text only — no broken image ever.
def _load_logos():
    try:
        with open(os.path.join(ROOT, "data/logos.json"), encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {"leagues": {}, "clubs": []}
LOGOS_DATA = _load_logos()
LOGO_BY_EN = {c["en"]: c["file"] for c in LOGOS_DATA.get("clubs", [])}
def logo_img(team, cls="team-logo"):
    f = LOGO_BY_EN.get(team)
    if not f:
        return ""
    return (f'<img class="{cls}" src="{f}" alt="Logo of {team}" '
            f'loading="lazy" onerror="this.remove()">')
def league_logo_img(lid):
    f = LOGOS_DATA.get("leagues", {}).get(lid)
    if not f:
        return ""
    return (f'<img class="league-logo" src="{f}" alt="League logo" '
            f'loading="lazy" onerror="this.remove()">')

def w(path, text):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(text)

def dump(path, obj):
    w(path, json.dumps(obj, ensure_ascii=False, indent=2) + "\n")

# ------------------------------------------------------------- CSS add ---
CSS_ADD_EN = '''
/* ---------- MatchPulse: additions ---------- */
/* Hide empty ad slots (teardown fixes 18 Nov 2026) — the live CPA offers
   section (.offers-*) is NOT hidden. */
.ad-slot, .anchored-ad, .ad-leaderboard, .ad-infeed, .ad-rect { display: none !important; }
/* MatchPulse font (LTR) */
:root { --font: "Inter","Segoe UI",system-ui,-apple-system,sans-serif; }
body { font-family: var(--font); }
.data-note { border-left: 3px solid var(--accent); border-right: none; }
/* League logo next to the league name in section titles */
.league-chip img, .league-chip svg { width: 18px; height: 18px; object-fit: contain; vertical-align: -3px; margin-inline-end: 6px; }
/* Status badges */
.status-badge { display: inline-block; padding: 2px 8px; border-radius: 999px; font-size: 11px; font-weight: 700; }
.status-live { background: #e11d48; color: #fff; }
.status-ft { background: #16a34a; color: #fff; }
.status-tbc { background: #f59e0b; color: #111; }
/* Match page tabs */
.match-tabs { display: flex; gap: 8px; margin: 16px 0; flex-wrap: wrap; }
.match-tab { padding: 8px 14px; border: 1px solid var(--line); border-radius: 999px; background: var(--card); cursor: pointer; font-weight: 700; }
.match-tab.active { background: var(--accent); color: #fff; border-color: var(--accent); }
/* Stat bars */
.stat-row { display: grid; grid-template-columns: 44px 1fr 44px; align-items: center; gap: 10px; margin: 10px 0; }
.stat-bar { height: 8px; background: var(--line); border-radius: 999px; overflow: hidden; position: relative; }
.stat-bar i { position: absolute; top: 0; bottom: 0; }
.stat-bar i.home { left: 0; background: var(--accent); }
.stat-bar i.away { right: 0; background: #64748b; }
/* Table team cell wraps instead of horizontal scrolling on phones (390px) */
.standings-table td.team-cell { white-space: normal; }
.standings-table td.team-cell img { width: 20px; height: 20px; object-fit: contain; vertical-align: -4px; margin-inline-end: 6px; }
/* Sponsored ads (live CPA offers) — display-ad look, NOT content cards */
.offers-section { margin: 28px 0; }
.offers-section h2 { font-size: 1.25rem; }
.ad-label { font-size: 11px; color: #64748b; border: 1px solid var(--line); border-radius: 6px; padding: 1px 6px; vertical-align: middle; }
.offers-note { color: #64748b; font-size: 13px; }
.ad-kicker { text-align: center; font-size: 11px; letter-spacing: 3px; color: #64748b; text-transform: uppercase; margin: 0 0 8px; }
.ad-tag { display: inline-block; align-self: flex-start; font-size: 11px; font-weight: 800; letter-spacing: 1px; text-transform: uppercase; color: var(--ad, #22e07a); border: 1px solid var(--ad, #22e07a); border-radius: 999px; padding: 2px 8px; margin-bottom: 6px; }
/* --- the ad unit: horizontal display ad --- */
.ad-unit, .ad-leaderboard-unit { position: relative; display: flex; gap: 16px; align-items: center; padding: 18px; border-radius: 14px; background: linear-gradient(135deg, #1b2342, #141b30); border: 1px solid #2b3656; border-top: 3px solid var(--ad, #22e07a); box-shadow: 0 8px 22px rgba(0,0,0,.35); text-decoration: none; color: inherit; overflow: hidden; }
.ad-unit:hover, .ad-leaderboard-unit:hover, .ad-mini:hover { border-color: var(--ad, #22e07a); }
.ad-sponsored { position: absolute; top: 0; right: 0; background: #f59e0b; color: #111; font-size: 10px; font-weight: 800; letter-spacing: 1px; text-transform: uppercase; padding: 3px 9px; border-radius: 0 0 0 8px; }
.ad-visual { flex: 0 0 56px; width: 56px; height: 56px; border-radius: 12px; display: flex; align-items: center; justify-content: center; font-size: 28px; background: var(--ad, #22e07a); }
.ad-body { flex: 1; min-width: 0; display: flex; flex-direction: column; }
.ad-headline { font-weight: 800; font-size: 1.05rem; line-height: 1.25; }
.ad-benefit { font-size: .9rem; color: #c6d0e8; margin-top: 3px; }
.ad-meta { font-size: 12px; color: #8b98b8; margin-top: 5px; }
.ad-cta { flex: 0 0 auto; background: var(--ad, #22e07a); color: #fff; font-weight: 800; text-transform: uppercase; letter-spacing: .4px; font-size: .85rem; padding: 12px 18px; border-radius: 999px; white-space: nowrap; text-align: center; }
.ad-stack { display: grid; gap: 12px; }
@media (min-width: 700px) { .ad-stack { grid-template-columns: 1fr 1fr; } }
@media (max-width: 640px) { .ad-unit { flex-wrap: wrap; } .ad-unit .ad-cta { width: 100%; } }
/* --- leaderboard banner (homepage): wide horizontal ad --- */
.ad-leaderboard-wrap { margin: 28px 0; }
.ad-leaderboard-unit { padding: 22px; border-radius: 16px; }
.ad-leaderboard-unit .ad-visual { flex-basis: 72px; width: 72px; height: 72px; font-size: 36px; border-radius: 16px; }
.ad-leaderboard-unit .ad-headline { font-size: 1.35rem; }
.ad-leaderboard-unit .ad-cta { padding: 14px 26px; font-size: 1rem; }
.ad-grid { display: grid; gap: 12px; margin-top: 12px; }
@media (min-width: 700px) { .ad-grid { grid-template-columns: repeat(3, 1fr); } }
/* --- vertical mini ad card (300x250 style) --- */
.ad-mini { position: relative; display: flex; flex-direction: column; gap: 6px; padding: 18px 16px 16px; border-radius: 14px; background: linear-gradient(160deg, #1b2342, #141b30); border: 1px solid #2b3656; border-top: 3px solid var(--ad, #22e07a); box-shadow: 0 8px 22px rgba(0,0,0,.35); text-decoration: none; color: inherit; overflow: hidden; }
.ad-mini .ad-visual { width: 52px; height: 52px; font-size: 26px; margin-top: 4px; }
.ad-mini .ad-cta { margin-top: 8px; }
/* --- showcase rows (offers.html): large ad units --- */
.ad-showcase { position: relative; display: flex; gap: 18px; padding: 22px 20px; border-radius: 16px; background: linear-gradient(135deg, #1b2342, #141b30); border: 1px solid #2b3656; border-top: 3px solid var(--ad, #22e07a); box-shadow: 0 8px 22px rgba(0,0,0,.35); margin: 16px 0; overflow: hidden; }
.ad-showcase .ad-visual { flex: 0 0 88px; width: 88px; height: 88px; font-size: 44px; border-radius: 16px; }
.ad-showcase .ad-headline { font-size: 1.3rem; margin: 2px 0 0; }
.ad-showcase .ad-benefit { font-size: .95rem; }
.ad-facts { font-size: .85rem; color: #c6d0e8; margin: 8px 0 0; }
.ad-cta-btn { display: inline-block; margin-top: 14px; background: var(--ad, #22e07a); color: #fff; font-weight: 800; text-transform: uppercase; letter-spacing: .4px; font-size: .95rem; padding: 13px 24px; border-radius: 999px; text-decoration: none; }
.ad-cta-btn:hover { filter: brightness(1.12); }
@media (max-width: 640px) { .ad-showcase, .ad-leaderboard-unit { flex-wrap: wrap; } .ad-leaderboard-unit .ad-cta, .ad-cta-btn { width: 100%; text-align: center; } }
.offers-teaser { border: 1px solid var(--line); border-radius: 12px; padding: 12px 14px; margin: 14px 0; background: var(--card); font-weight: 700; }
.offers-teaser a { text-decoration: none; color: inherit; }
'''
CSS_ADD = CSS_ADD_EN

# -------------------------------------------------------------- JS ------
MAIN_JS = r"""/* MatchPulse — main.js: strict filter: 6 leagues only, no simulation, no other competitions */
(function () {
  "use strict";
  var ALLOWED_IDS = ["premier-league", "la-liga", "serie-a", "bundesliga", "ligue-1", "botola"];
  var ALLOWED_NAMES = ["Premier League", "La Liga", "Serie A",
    "Bundesliga", "Ligue 1", "Botola Pro", "Botola Pro"];
  window.MATCHPULSE_ALLOWED = ALLOWED_IDS;
  window.isAllowedLeague = function (m) {
    if (!m) return false;
    if (m.league && ALLOWED_IDS.indexOf(m.league) !== -1) return true;
    if (m.league_name && ALLOWED_NAMES.indexOf(m.league_name) !== -1) return true;
    return false;
  };
  function onlyAllowed(list) { return (list || []).filter(window.isAllowedLeague); }

  async function loadJSON(path) {
    try { const r = await fetch(path); if (!r.ok) throw new Error("http " + r.status); return await r.json(); }
    catch (e) { return null; }
  }
  window.MatchPulseData = {
    async leagues() {
      const d = await loadJSON("data/leagues-en.json");
      if (d && d.leagues) return d;
      return { leagues: FALLBACK.leagues, updated: (typeof FALLBACK !== "undefined" && FALLBACK.updated) || "" };
    },
    async fixtures() {
      const d = await loadJSON("data/fixtures-en.json");
      if (d) return d;
      return FALLBACK.fixtures;
    },
    async news() {
      const d = await loadJSON("data/news-en.json");
      if (d && d.articles) return d.articles;
      return [];
    }
  };

  /* Logos: local files from data/logos.json — a team without a logo shows text only */
  window.MatchPulseLogos = { leagues: {}, byEn: {}, ready: false, promise: null };
  window.loadLogos = function () {
    if (window.MatchPulseLogos.promise) return window.MatchPulseLogos.promise;
    window.MatchPulseLogos.promise = (async function () {
      try {
        const d = await loadJSON("data/logos.json");
        if (d) {
          window.MatchPulseLogos.leagues = d.leagues || {};
          (d.clubs || []).forEach(c => { window.MatchPulseLogos.byEn[c.en] = c.file; });
        }
      } catch (e) {}
      window.MatchPulseLogos.ready = true;
      return window.MatchPulseLogos;
    })();
    return window.MatchPulseLogos.promise;
  };
  window.logoFor = function (teamName) {
    if (!teamName || teamName === "—") return "";
    const f = window.MatchPulseLogos.byEn[teamName];
    if (!f) return "";
    const esc = String(teamName).replace(/"/g, "&quot;");
    return `<img class="team-logo" src="${f}" alt="Logo of ${esc}" loading="lazy" onerror="this.remove()">`;
  };
  window.leagueLogoFor = function (leagueId) {
    const f = window.MatchPulseLogos.leagues[leagueId];
    if (!f) return "";
    return `<img class="league-logo" src="${f}" alt="League logo" loading="lazy" onerror="this.remove()">`;
  };

  document.addEventListener("DOMContentLoaded", function () {
    const btn = document.querySelector(".menu-btn");
    const nav = document.querySelector(".main-nav");
    if (btn && nav) btn.addEventListener("click", () => nav.classList.toggle("open"));
    document.querySelectorAll(".js-year").forEach(el => { el.textContent = new Date().getFullYear(); });
    document.querySelectorAll(".newsletter form").forEach(form => {
      form.addEventListener("submit", function (e) {
        e.preventDefault();
        const input = form.querySelector('input[type="email"]');
        const note = form.parentElement.querySelector(".form-note");
        const val = (input.value || "").trim();
        if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(val)) {
          if (note) { note.textContent = "Please enter a valid email address."; note.style.color = "#ff4d5e"; }
          return;
        }
        if (note) { note.textContent = "Thanks! Your subscription is confirmed. ⚽"; note.style.color = "#22e07a"; }
        input.value = "";
      });
    });
    const closeAd = document.querySelector(".close-ad");
    if (closeAd) closeAd.addEventListener("click", () => {
      document.querySelector(".anchored-ad").style.display = "none";
    });
  });

  /* Ticker: the six leagues only — no obscure leagues */
  window.renderTicker = async function (elId) {
    const el = document.getElementById(elId);
    if (!el) return;
    const fx = await window.MatchPulseData.fixtures();
    const items = [];
    onlyAllowed(fx.live || []).forEach(m => {
      items.push(`<span class="ticker-item"><span class="live-dot">● LIVE ${m.minute}'</span> <b>${m.home} ${m.home_goals} - ${m.away_goals} ${m.away}</b></span>`);
    });
    onlyAllowed(fx.upcoming || []).slice(0, 8).forEach(m => {
      items.push(`<span class="ticker-item">${m.home} × ${m.away} <b>${m.date_label || m.date} ${m.time || ""}</b></span>`);
    });
    const liveCount = onlyAllowed(fx.live || []).length;
    const head = liveCount ? "" : "<span class='ticker-item'>No live matches right now — coming up:</span>";
    el.innerHTML = head + (items.join("") || "<span class='ticker-item'>No fixtures scheduled in the six leagues right now</span>");
  };

  window.posClass = function (pos, leagueId) {
    if (pos <= 4) return "pos-ucl";
    if (leagueId === "botola") return pos >= 15 ? "pos-rel" : "";
    if (pos >= 18) return "pos-rel";
    return "";
  };

  function cell(v) { return (v === undefined || v === null || v === "") ? "—" : v; }
  function gdTxt(r) {
    if (r.gd !== undefined && r.gd !== null) return (r.gd > 0 ? "+" : "") + r.gd;
    if (r.gf !== null && r.gf !== undefined && r.ga !== null && r.ga !== undefined) {
      const gd = r.gf - r.ga; return (gd > 0 ? "+" : "") + gd;
    }
    return "—";
  }
  window.standingsTableHTML = function (league, limit) {
    const rows = (limit ? league.table.slice(0, limit) : league.table).map(r => {
      if (r.placeholder) return `<tr><td>${r.pos}</td><td class="team" style="color:var(--muted)">${r.team}</td><td>—</td><td>—</td><td>—</td><td>—</td><td>—</td><td><b>—</b></td></tr>`;
      return `<tr class="${window.posClass(r.pos, league.id)}">
        <td>${r.pos}</td><td class="team">${window.logoFor(r.team)}${r.team}</td><td>${cell(r.p)}</td>
        <td>${cell(r.w)}</td><td>${cell(r.d)}</td><td>${cell(r.l)}</td>
        <td>${gdTxt(r)}</td><td><b>${cell(r.pts)}</b></td></tr>`;
    }).join("");
    return `<div class="table-wrap"><table class="standings">
      <thead><tr><th>#</th><th>Team</th><th>P</th><th>W</th><th>D</th><th>L</th><th>GD</th><th>Pts</th></tr></thead>
      <tbody>${rows}</tbody></table></div>`;
  };

  window.matchRowHTML = function (m) {
    const isLive = m.status === "live";
    const isFin = m.status === "finished";
    const score = isLive || isFin
      ? `<span class="score${isLive ? " live" : ""}">${m.home_goals} - ${m.away_goals}</span>`
      : `<span class="score">${m.time || "—"}</span>`;
    const badge = isLive
      ? `<span class="status-badge live">● LIVE ${m.minute || ""}'</span>`
      : isFin
        ? `<span class="status-badge finished">Full time</span>`
        : `<span class="status-badge upcoming">Not started yet</span>`;
    const time = isLive
      ? `<span class="time">${m.minute || ""}'</span>`
      : `<span class="time">${m.date_label || m.date || ""} ${m.time || ""}</span>`;
    const inner = `<div class="match-row">
      <span class="lg">${m.league_name || ""}${badge}</span>
      <span class="team">${window.logoFor(m.home)}${m.home}</span>${score}<span class="team away">${window.logoFor(m.away)}${m.away}</span>${time}
    </div>`;
    return m.id ? `<a class="match-link" href="match.html?id=${m.id}">${inner}</a>` : inner;
  };
})();
"""

MATCHES_JS = r"""/* MatchPulse — matches.js: real tabs from data/fixtures-en.json only. No simulation. */
(function () {
  "use strict";
  let FX = null, currentTab = "today";
  function $(id) { return document.getElementById(id); }
  function emptyMsg(txt) {
    return `<p style="color:var(--muted);text-align:center;padding:26px 0">${txt}</p>`;
  }
  function listHTML(list) {
    const ok = (list || []).filter(window.isAllowedLeague);
    return ok.length ? ok.map(window.matchRowHTML).join("") : null;
  }
  /* Dynamic dates from data/fixtures.json (today_date/tomorrow_date) — no hardcoded dates */
  function dayLabel(iso) {
    if (!iso) return "";
    return new Date(iso + "T12:00:00").toLocaleDateString("en-GB", {weekday: "long", day: "numeric", month: "long", year: "numeric"});
  }
  function shortDay(iso) {
    if (!iso) return "";
    return new Date(iso + "T12:00:00").toLocaleDateString("en-GB", {day: "numeric", month: "long"});
  }
  function nextDay() {
    const up = (FX.upcoming || []);
    const t = FX.tomorrow_date || "";
    for (const m of up) { if (m.date > t) return m.date; }
    return null;
  }
  function relabelTabs() {
    document.querySelectorAll(".tabs button").forEach(btn => {
      const t = btn.dataset.tab;
      if (t === "today") btn.textContent = "📅 Today " + shortDay(FX.today_date);
      else if (t === "tomorrow") btn.textContent = "📅 Tomorrow " + shortDay(FX.tomorrow_date);
      else if (t === "friday") { const nd = nextDay(); btn.textContent = nd ? "⏭️ " + dayLabel(nd) : "⏭️ Upcoming"; }
    });
  }
  function render() {
    const box = $("matches-box");
    if (!box || !FX) return;
    let html = "";
    const nd = nextDay();
    const back = nd ? ` Back ${dayLabel(nd)}.` : "";
    if (currentTab === "today") {
      html = listHTML(FX.today) || emptyMsg(`No matches today (${dayLabel(FX.today_date)}) in the six leagues.${back}`);
    } else if (currentTab === "tomorrow") {
      html = listHTML(FX.tomorrow) || emptyMsg(`No matches tomorrow (${dayLabel(FX.tomorrow_date)}) in the six leagues.${back}`);
    } else if (currentTab === "friday") {
      const fri = (FX.upcoming || []).filter(m => nd && m.date === nd);
      html = listHTML(fri) || emptyMsg(nd ? `No fixtures scheduled on ${dayLabel(nd)}.` : "No upcoming fixtures scheduled.");
    } else if (currentTab === "upcoming") {
      html = listHTML(FX.upcoming) || emptyMsg("No upcoming fixtures scheduled.");
    } else {
      const r = FX.results || [];
      html = r.length ? listHTML(r) : emptyMsg("No results recorded.");
      if (r.length) {
        const dates = r.map(m => m.date).sort();
        const range = dates[0] === dates[dates.length - 1] ? shortDay(dates[0]) : shortDay(dates[0]) + " – " + shortDay(dates[dates.length - 1]);
        html = `<p class="data-note">Latest results (${range}) — Source: ESPN. All times UTC.</p>` + html;
      }
    }
    box.innerHTML = html;
  }
  document.addEventListener("DOMContentLoaded", async function () {
    await window.loadLogos();
    FX = await window.MatchPulseData.fixtures();
    render();
    relabelTabs();
    document.querySelectorAll(".tabs button").forEach(btn => {
      btn.addEventListener("click", () => {
        document.querySelectorAll(".tabs button").forEach(b => b.classList.remove("active"));
        btn.classList.add("active");
        currentTab = btn.dataset.tab;
        render();
      });
    });
  });
})();
"""

STANDINGS_JS = r"""/* MatchPulse — standings.js: 6 leagues only */
(function () {
  "use strict";
  const ORDER = ["premier-league", "la-liga", "serie-a", "bundesliga", "ligue-1", "botola"];
  let DATA = null, current = "premier-league";
  function leagueById(id) { return DATA.leagues.find(l => l.id === id) || DATA.leagues[0]; }
  function renderSelector() {
    const box = document.getElementById("league-select");
    if (!box) return;
    box.innerHTML = ORDER.map(id => leagueById(id)).filter(Boolean).map(l =>
      `<button data-l="${l.id}" class="${l.id === current ? "active" : ""}">${window.leagueLogoFor(l.id)}${l.name}</button>`).join("");
    box.querySelectorAll("button").forEach(b => b.addEventListener("click", () => {
      current = b.dataset.l;
      box.querySelectorAll("button").forEach(x => x.classList.remove("active"));
      b.classList.add("active");
      renderLeague();
    }));
  }
  function renderLeague() {
    const l = leagueById(current);
    const title = document.getElementById("league-title");
    if (title) title.innerHTML = `${window.leagueLogoFor(l.id)}${l.name} <small style="color:var(--muted);font-size:.85rem">Season ${l.season || "2026-27"} — ${l.round || ""}</small>`;
    const tw = document.getElementById("table-wrap");
    if (tw) tw.innerHTML = window.standingsTableHTML(l)
      + `<p class="data-note"><b>Source:</b> ${l.source || "—"} — <b>Last checked:</b> ${DATA.updated || ""}. The full table is verified for every league.</p>`;
    const sc = document.getElementById("scorers");
    if (sc) {
      const list = (l.scorers || []).slice(0, 8);
      sc.innerHTML = list.length ? list.map((s, i) => `
        <div class="scorer"><span class="rank">${i + 1}</span>
        <span class="info"><b>${s.player}</b><span>${window.logoFor(s.team)}${s.team}</span></span>
        <span class="goals">${s.goals}</span></div>`).join("")
        : `<div class="placeholder-box">No verified top-scorer list for this league yet — it will be added once verified from an official source.</div>`;
    }
    const upd = document.getElementById("data-updated");
    if (upd && DATA.updated) upd.textContent = "Last updated: " + DATA.updated;
  }
  document.addEventListener("DOMContentLoaded", async function () {
    await window.loadLogos();
    DATA = await window.MatchPulseData.leagues();
    renderSelector();
    renderLeague();
  });
})();
"""

HOME_JS = r"""/* MatchPulse — home.js: the homepage keeps the international-break message (static hero in HTML) */
(function () {
  "use strict";
  function newsCard(a) {
    return `<a href="news/${a.slug}.html" class="news-card">
      <div class="news-thumb">${a.emoji}</div>
      <div class="news-body">
        <div class="news-meta"><span class="cat">${a.category}</span><span>${a.date}</span></div>
        <h3>${a.title}</h3><p>${a.excerpt}</p>
      </div></a>`;
  }
  document.addEventListener("DOMContentLoaded", async function () {
    window.renderTicker("ticker-track");
    await window.loadLogos();
    try {
      const articles = await window.MatchPulseData.news();
      if (articles.length) {
        document.querySelector("#home-news").innerHTML = articles.slice(0, 6).map(newsCard).join("");
      }
    } catch (e) {}
    try {
      const fx = await window.MatchPulseData.fixtures();
      const up = (fx.upcoming || []).filter(window.isAllowedLeague).slice(0, 6);
      document.querySelector("#home-matches").innerHTML = up.length
        ? up.map(window.matchRowHTML).join("")
        : `<p style="color:var(--muted)">No fixtures scheduled right now.</p>`;
    } catch (e) {}
    try {
      const data = await window.MatchPulseData.leagues();
      const pick = ["premier-league", "la-liga", "botola"]
        .map(id => data.leagues.find(l => l.id === id)).filter(Boolean);
      document.querySelector("#home-tables").innerHTML = pick.map(l => `
        <div>
          <div class="section-head" style="margin-bottom:10px">
            <h2 style="font-size:1.05rem">${l.name}</h2>
            <a class="more" href="league-${l.id}.html">Full table →</a>
          </div>
          ${window.standingsTableHTML(l, 5)}
          <p style="color:var(--muted);font-size:.78rem;margin-top:6px">Top 5 — full table on the league page — last checked: ${data.updated || ""}</p>
        </div>`).join("");
    } catch (e) {}
  });
})();
"""

MATCH_JS = r"""/* MatchPulse — match.js: match detail page (?id=) — verified data only, the rest is an explicit placeholder */
(function () {
  "use strict";
  function q(name) { return new URLSearchParams(location.search).get(name); }
  function esc(s) { return String(s == null ? "" : s); }
  document.addEventListener("DOMContentLoaded", async function () {
    window.renderTicker("ticker-track");
    await window.loadLogos();
    const id = q("id");
    const box = document.getElementById("match-detail");
    if (!box) return;
    const fx = await window.MatchPulseData.fixtures();
    const all = [].concat(fx.live || [], fx.today || [], fx.tomorrow || [], fx.upcoming || [], fx.results || []);
    const m = all.find(x => x.id === id);
    if (!m) {
      box.innerHTML = `<div class="placeholder-box"><h2 style="margin-bottom:8px">Match not found</h2><p>The link is wrong or the match is not in the six leagues. <a href="matches.html" style="color:var(--accent)">← Back to fixtures</a></p></div>`;
      return;
    }
    const isFin = m.status === "finished";
    const score = isFin ? `${m.home_goals} - ${m.away_goals}` : (m.time || "—");
    const status = isFin ? "Full time" : `Upcoming match — ${m.date_label || m.date} ${m.time ? "• " + m.time + " UTC" : "• Kick-off time TBC"}`;
    document.title = `${m.home} × ${m.away} | MatchPulse`;
    const h1 = document.getElementById("match-h1");
    if (h1) h1.textContent = `${m.home} × ${m.away}`;
    const infoVenue = m.venue || m.venue_note || "To be confirmed";
    const infoRef = m.referee || "To be confirmed";
    const infoChan = m.channel || "To be confirmed";
    const infoTime = isFin ? "Full time" : ((m.date_label || m.date || "") + (m.time ? " • " + m.time + " UTC" : " • Kick-off time TBC"));
    function statBar(label, h, a) {
      const t = (h || 0) + (a || 0);
      const hp = t ? Math.round(100 * h / t) : 50;
      return `<div class="stat-row"><span><b>${h}</b></span><div><div style="text-align:center;font-size:.8rem;color:var(--muted)">${label}</div><div class="stat-bar"><i class="h" style="width:${hp}%"></i><i class="a" style="width:${100 - hp}%"></i></div></div><span style="text-align:left"><b>${a}</b></span></div>`;
    }
    const st = m.stats || null;
    const statsHTML = st ? (
      statBar("Possession %", st.possession_home, st.possession_away)
      + statBar("Shots", st.shots_home, st.shots_away)
      + statBar("Shots on target", st.shots_on_target_home, st.shots_on_target_away)
      + statBar("Corners", st.corners_home, st.corners_away)
      + `<p style="color:var(--muted);font-size:.78rem;margin-top:10px">Source: ${esc(st.source || "—")}</p>`
    ) : `<div class="placeholder-box">Statistics are not available for this match yet.<br>They will appear here (possession, shots, corners) once verified from an official source.</div>`;
    const eventsHTML = (m.events && m.events.length) ? m.events.map(e =>
      `<div class="event-row"><span class="ev-min">${esc(e.minute || "")}'</span><span class="ev-type">${esc(e.type || "")}</span><b>${esc(e.player || "")}</b><span style="color:var(--muted)">${esc(e.team || "")}</span></div>`).join("")
      : `<div class="placeholder-box">No verified events for this match yet (goals, cards, substitutions).<br>Events will be added once verified from an official source.</div>`;
    box.innerHTML = `
    <div class="scoreboard">
      <div class="teams"><span class="team-name">${window.logoFor(m.home)}${esc(m.home)}</span>
      <span class="big-score">${score}</span>
      <span class="team-name">${window.logoFor(m.away)}${esc(m.away)}</span></div>
      <div class="status">${m.league_name} • ${status}</div>
      <div class="status" style="font-size:.8rem">Source: ${esc(m.source || "—")} — Last checked: ${esc(fx.updated || "")}</div>
    </div>
    <div class="match-info">
      <span><span class="lbl">🏟️ Stadium:</span><b>${esc(infoVenue)}</b></span>
      <span><span class="lbl">Referee:</span><b>${esc(infoRef)}</b></span>
      <span><span class="lbl">📺 TV channel:</span><b>${esc(infoChan)}</b></span>
      <span><span class="lbl">🕐 Kick-off:</span><b>${esc(infoTime)}</b></span>
    </div>
    <div class="match-tabs">
      <button data-mtab="events" class="active">Events</button>
      <button data-mtab="stats">Statistics</button>
      <button data-mtab="lineups">Lineups</button>
      <button data-mtab="h2h">Head-to-head</button>
    </div>
    <div class="mtab-panel" data-panel="events">
      ${eventsHTML}
    </div>
    <div class="mtab-panel" data-panel="stats" style="display:none">${statsHTML}</div>
    <div class="mtab-panel" data-panel="lineups" style="display:none">
      <div class="placeholder-box">The official lineups are not verified yet — they are published one hour before kick-off from an official source.</div>
    </div>
    <div class="mtab-panel" data-panel="h2h" style="display:none">
      <div class="placeholder-box">The head-to-head record between the two teams is not verified yet — it will be added from an official source.</div>
    </div>
    <p><a href="matches.html" style="color:var(--accent);font-weight:700">← Back to all fixtures</a></p>`;
    box.querySelectorAll(".match-tabs button").forEach(btn => {
      btn.addEventListener("click", () => {
        box.querySelectorAll(".match-tabs button").forEach(b => b.classList.remove("active"));
        btn.classList.add("active");
        const tab = btn.dataset.mtab;
        box.querySelectorAll(".mtab-panel").forEach(p => { p.style.display = p.dataset.panel === tab ? "" : "none"; });
      });
    });
  });
})();
"""

# ---------------------------------------------------------- templates ---
BASE = "https://matchpulse.onrender.com"
ICON = """<link rel="icon" href="data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'><text y='.9em' font-size='90'>⚽</text></svg>">"""
FONTS = """<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;700;800&display=swap" rel="stylesheet">
<link rel="stylesheet" href="assets/css/style.css">"""


# --- MatchPulse CPA offers (live, from data/offers.json — CPAlead) ---------
# AD-STYLE presentation (redesign 19 Nov 2026, user order: offers must LOOK
# like ads, not a list): sponsored ad units with a SPONSORED badge, a brand-
# colour visual tile (plain symbol, no invented logos, no product photos), a
# bold promo headline, a benefit line and a big CTA button. Links / payouts /
# geo come straight from data/offers.json and are NEVER edited here.
OFFERS = json.load(open(os.path.join(ROOT, "data", "offers.json"), encoding="utf-8"))["offers"]

# Per-offer ad identity: (visual icon, brand colour).
AD_STYLE = {
    "hidden-gems": ("💎", "#14b8a6"),
    "free-vpn": ("🔒", "#3b82f6"),
    "capcut-pro": ("🎬", "#8b5cf6"),
    "complete-surveys": ("📝", "#d97706"),
}

def _ad_style(o):
    return AD_STYLE.get(o["id"], ("🎁", "#22e07a"))

def ad_card(o):
    """One sponsored ad unit (horizontal) — display-ad look."""
    icon, color = _ad_style(o)
    return f"""
    <a class="ad-unit" href="{o["url"]}" target="_blank" rel="nofollow sponsored noopener" style="--ad:{color}">
      <span class="ad-sponsored">Sponsored</span>
      <span class="ad-visual" aria-hidden="true">{icon}</span>
      <span class="ad-body">
        <span class="ad-headline">{o["name"]}</span>
        <span class="ad-benefit">{o.get("blurb", "")}</span>
        <span class="ad-meta">{o["geo"]} &middot; {o["device"]}</span>
      </span>
      <span class="ad-cta">{o.get("cta", "Claim this offer")} &rarr;</span>
    </a>"""

def ad_mini(o):
    """One sponsored ad unit (vertical mini card, 300x250 style)."""
    icon, color = _ad_style(o)
    return f"""
    <a class="ad-mini" href="{o["url"]}" target="_blank" rel="nofollow sponsored noopener" style="--ad:{color}">
      <span class="ad-sponsored">Sponsored</span>
      <span class="ad-visual" aria-hidden="true">{icon}</span>
      <span class="ad-headline">{o["name"]}</span>
      <span class="ad-benefit">{o.get("blurb", "")}</span>
      <span class="ad-meta">{o["geo"]} &middot; {o["device"]}</span>
      <span class="ad-cta">{o.get("cta", "Claim this offer")} &rarr;</span>
    </a>"""

def ad_leaderboard(o):
    """Wide horizontal leaderboard banner (970x250 style) for the featured offer."""
    icon, color = _ad_style(o)
    return f"""
    <a class="ad-leaderboard-unit" href="{o["url"]}" target="_blank" rel="nofollow sponsored noopener" style="--ad:{color}">
      <span class="ad-sponsored">Sponsored</span>
      <span class="ad-visual" aria-hidden="true">{icon}</span>
      <span class="ad-body">
        <span class="ad-tag">{o.get("tag", "Featured")}</span>
        <span class="ad-headline">{o["name"]}</span>
        <span class="ad-benefit">{o.get("blurb", "")}</span>
        <span class="ad-meta">{o["geo"]} &middot; {o["device"]}</span>
      </span>
      <span class="ad-cta">{o.get("cta", "Claim this offer")} &rarr;</span>
    </a>"""

def offers_html(variant="box"):
    """Sponsored offers as display ads (#ad). variant="leaderboard" (homepage:
    featured offer as a wide banner + the rest as mini ad cards);
    variant="box" (default: tables, news, league, fixtures — compact ad stack).
    Links are the exact CPAlead tracking URLs."""
    if variant == "leaderboard":
        feat = next((o for o in OFFERS if o.get("tag") == "Featured"), OFFERS[0])
        rest = [o for o in OFFERS if o is not feat]
        return f"""
<section class="offers-section ad-leaderboard-wrap" id="offers">
  <p class="ad-kicker">Advertisement <span class="ad-label">#ad</span></p>
  {ad_leaderboard(feat)}
  <div class="ad-grid">{''.join(ad_mini(o) for o in rest)}
  </div>
  <p class="offers-note">Sponsored offers — we may earn a commission if you sign up. Available in the listed countries only. No betting, no dating, no popups.</p>
</section>"""
    return f"""
<section class="offers-section" id="offers">
  <h2>Sponsored offers <span class="ad-label">#ad</span></h2>
  <p class="offers-note">Sponsored offers — we may earn a commission if you sign up. Available in the listed countries only. No betting, no dating, no popups.</p>
  <div class="ad-stack">{''.join(ad_card(o) for o in OFFERS)}
  </div>
</section>"""

def offers_page_html():
    rows = []
    for o in OFFERS:
        icon, color = _ad_style(o)
        cap = (" &middot; <strong>Daily cap:</strong> " + str(o["cap"])) if o.get("cap") and o["cap"] != "No daily cap" else ""
        rows.append(f"""
    <div class="ad-showcase" style="--ad:{color}">
      <span class="ad-sponsored">Sponsored</span>
      <span class="ad-visual" aria-hidden="true">{icon}</span>
      <div class="ad-body">
        <span class="ad-tag">{o.get("tag", "")}</span>
        <h3 class="ad-headline">{o["name"]}</h3>
        <p class="ad-benefit">{o.get("blurb", "")}</p>
        <p class="ad-facts"><strong>Payout:</strong> {o["payout"]} &middot; <strong>Countries:</strong> {o["geo"]} &middot; <strong>Devices:</strong> {o["device"]}{cap}</p>
        <a class="ad-cta-btn" href="{o["url"]}" target="_blank" rel="nofollow sponsored noopener">{o.get("cta", "Claim this offer")} &rarr;</a>
      </div>
    </div>""")
    tpl = """<!DOCTYPE html>
<html lang="en" dir="ltr">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Sponsored offers &amp; rewards | MatchPulse</title>
<meta name="description" content="Free sponsored offers for MatchPulse readers: free VPN for Windows, CapCut Pro trial, surveys and more. #ad">
<link rel="canonical" href="{BASE}/offers.html">
<link rel="icon" href="assets/logo.svg" type="image/svg+xml">
<link rel="stylesheet" href="assets/css/style.css">
</head>
<body>
{header}
<main class="wrap page">
  <h1>Sponsored offers <span class="ad-label">#ad</span></h1>
  <p class="offers-note">Sponsored offers — we may earn a commission if you sign up. Available in the listed countries only.</p>
  {rows}
</main>
{footer}
<script src="assets/js/data-fallback.js"></script>
<script src="assets/js/main.js"></script>
</body>
</html>"""
    return tpl.replace("{rows}", "".join(rows))


def header(active=""):
    def a(page, label):
        return f'<li><a href="{page}" class="active">{label}</a></li>' if page == active else f'<li><a href="{page}">{label}</a></li>'
    return f"""<header class="site-header">
  <div class="container header-inner">
    <a href="index.html" class="logo"><span class="ball">⚽</span><span>MatchPulse<small>LIVE FOOTBALL</small></span></a>
    <button class="menu-btn" aria-label="Menu">☰</button>
    <nav class="main-nav"><ul>
      {a("index.html", "Home")}{a("matches.html", "Fixtures")}{a("standings.html", "Tables")}{a("news.html", "News")}{a("offers.html", "Offers")}
    </ul></nav>
  </div>
</header>"""

CHIPS = f"""<div class="container"><div class="league-chips">
<a href="league-premier-league.html">{league_logo_img("premier-league")}Premier League</a>
<a href="league-la-liga.html">{league_logo_img("la-liga")}La Liga</a>
<a href="league-serie-a.html">{league_logo_img("serie-a")}Serie A</a>
<a href="league-bundesliga.html">{league_logo_img("bundesliga")}Bundesliga</a>
<a href="league-ligue-1.html">{league_logo_img("ligue-1")}Ligue 1</a>
<a href="league-botola.html">{league_logo_img("botola")}Botola Pro</a>
</div></div>"""

TICKER = """<div class="ticker-wrap"><div class="container ticker">
  <span class="ticker-label">LIVE</span>
  <div class="ticker-track" id="ticker-track"><span class="ticker-item">No live matches right now — Loading upcoming fixtures…</span></div>
</div></div>"""

CPA_SLOT = offers_html()

AD_LEADER = """<div class="container"><div class="ad-slot"><div class="ad-leaderboard">Ad space — Leaderboard 970×250</div></div></div>"""

def footer():
    return f"""<footer class="site-footer">
  <div class="container">
    <div class="footer-grid">
      <div>
        <h4>⚽ MatchPulse</h4>
        <p style="color:var(--muted);font-size:.9rem">Your home for football: live results, league tables and the latest news from Europe’s five major leagues and Botola Pro.</p>
      </div>
      <div>
        <h4>Sections</h4>
        <ul>
          <li><a href="matches.html">Today’s matches</a></li>
          <li><a href="standings.html">League tables</a></li>
          <li><a href="news.html">Latest news</a></li>
          <li><a href="offers.html">Free offers</a></li>
          <li><a href="league-botola.html">Botola Pro</a></li>
        </ul>
      </div>
      <div>
        <h4>Info</h4>
        <ul>
          <li><a href="about.html">About us</a></li>
          <li><a href="contact.html">Contact</a></li>
          <li><a href="privacy.html">Privacy policy</a></li>
        </ul>
      </div>
    </div>
    <div class="footer-bottom">
      <span>© <span class="js-year">2026</span> MatchPulse — All rights reserved.</span>
      <span>Data for information only — Last updated: {BUILD_DATE_EN}</span>
    </div>
  </div>
</footer>
<div class="anchored-ad"><span>Ad space for mobile</span><button class="close-ad">✕</button></div>"""

def table_html(league, limit=None):
    rows = league["table"][:limit] if limit else league["table"]
    out = []
    for r in rows:
        def c(v):
            return "—" if v is None else str(v)
        if r.get("placeholder"):
            out.append(f'<tr><td>{r["pos"]}</td><td class="team" style="color:var(--muted)">{r["team"]}</td><td>—</td><td>—</td><td>—</td><td>—</td><td>—</td><td><b>—</b></td></tr>')
            continue
        gd = r["gd"]
        gd_txt = ("+" if gd and gd > 0 else "") + str(gd) if gd is not None else "—"
        cls = "pos-ucl" if r["pos"] <= 4 else ("pos-rel" if (league["id"] == "botola" and r["pos"] >= 15) or (league["id"] != "botola" and r["pos"] >= 18) else "")
        out.append(f'<tr class="{cls}"><td>{r["pos"]}</td><td class="team">{logo_img(r["team"])}{r["team"]}</td><td>{c(r["p"])}</td><td>{c(r["w"])}</td><td>{c(r["d"])}</td><td>{c(r["l"])}</td><td>{gd_txt}</td><td><b>{c(r["pts"])}</b></td></tr>')
    return ('<div class="table-wrap"><table class="standings">'
            '<thead><tr><th>#</th><th>Team</th><th>P</th><th>W</th><th>D</th><th>L</th><th>GD</th><th>Pts</th></tr></thead>'
            f'<tbody>{"".join(out)}</tbody></table></div>')

def scorers_html(league):
    sc = league["scorers"]
    if not sc:
        return '<div class="placeholder-box">No verified top-scorer list for this league yet — it will be added once verified from an official source.</div>'
    cards = "".join(
        f'<div class="scorer"><span class="rank">{i+1}</span><span class="info"><b>{s["player"]}</b><span>{logo_img(s["team"])}{s["team"]}</span></span><span class="goals">{s["goals"]}</span></div>'
        for i, s in enumerate(sc))
    return f'<div class="scorers">{cards}</div>'

def fixtures_list_html(matches):
    if not matches:
        return ""
    items = []
    for m in matches:
        score = f'{m["home_goals"]} - {m["away_goals"]}' if m["status"] == "finished" else (m.get("time") or "—")
        when = f'{m.get("date_label") or m["date"]} {m.get("time") or ""}'.strip()
        if m.get("time") is None:
            when += " — Kick-off time TBC"
        inner = (f'<div class="match-row"><span class="lg">{m["league_name"]}</span>'
                 f'<span class="team">{logo_img(m["home"])}{m["home"]}</span><span class="score">{score}</span>'
                 f'<span class="team away">{logo_img(m["away"])}{m["away"]}</span><span class="time">{when}</span></div>')
        items.append(f'<a class="match-link" href="match.html?id={m["id"]}">{inner}</a>' if m.get("id") else inner)
    return f'<div class="match-list">{"".join(items)}</div>'

def patch(path, pairs):
    with open(path, encoding="utf-8") as f:
        s = f.read()
    for old, new in pairs:
        # idempotent: skip if the replacement is already in place
        if old in s and new not in s:
            s = s.replace(old, new)
    w(path, s)

# ------------------------------------------------------------- build -----
def _count_txt(n):
    if n == 0:
        return "No matches"
    if n == 1:
        return "1 match"
    if n == 2:
        return "2 matches"
    return f"{n} matches"


def hero_blocks():
    """Hero block + day strip on the homepage — from today/tomorrow/upcoming data."""
    today_n, tom_n = len(FX_TODAY), len(FX_TOMORROW)
    nxt = None
    for m in UPCOMING:
        if m["date"] > (FX_TOMORROW_DATE or ""):
            nxt = m["date"]
            break
    nxt_n = len([m for m in UPCOMING if m["date"] == nxt]) if nxt else 0
    if today_n:
        tag, title = "⚽ Today’s matches", f"Today’s matches: {_count_txt(today_n)} in the six leagues"
        first = ", ".join(f"{m['home']} × {m['away']}" for m in FX_TODAY[:3])
        sub = (f"{en_date(FX_TODAY_DATE)} — {first}." if FX_TODAY_DATE else first)
        btn = "See today’s matches →"
    else:
        tag, title = "⏸️ No matches today", "Today’s matches: no matches in the six leagues"
        if nxt:
            first = ", ".join(f"{m['home']} × {m['away']}" for m in [x for x in UPCOMING if x["date"] == nxt][:3])
            sub = f"{en_date(FX_TODAY_DATE) if FX_TODAY_DATE else ''} — Back {en_date(nxt)}: {first}."
        else:
            sub = "No upcoming fixtures scheduled right now."
        btn = "See upcoming fixtures →"
    hero = (f'<section class="hero" id="hero"><div class="hero-card"><div class="hero-content">\n'
            f'    <span class="tag">{tag}</span>\n    <h1>{title}</h1>\n    <p>{sub}</p>\n'
            f'    <a class="btn" href="matches.html">{btn}</a>\n  </div></div></section>')
    cells = []
    if FX_TODAY_DATE:
        cells.append(f'<div class="day"><b>Today — {en_date_short(FX_TODAY_DATE)}</b><span>{_count_txt(today_n)}</span></div>')
    if FX_TOMORROW_DATE:
        cells.append(f'<div class="day"><b>Tomorrow — {en_date_short(FX_TOMORROW_DATE)}</b><span>{_count_txt(tom_n)}</span></div>')
    if nxt:
        cells.append(f'<div class="day next"><b>{en_date_short(nxt)}</b><span>{_count_txt(nxt_n)}</span></div>')
    strip = '<div class="date-strip">\n    ' + "\n    ".join(cells) + '\n  </div>'
    return hero, strip


def refresh_dates():
    """Updates frozen dates ('Last updated: …' / 'Last checked …') in the generated pages
    from V1 files (Tables, leagues, News…) — without touching articles news/ (their dates are historical)."""
    pages = ["index.html", "matches.html", "match.html", "standings.html", "news.html",
             "about.html", "contact.html", "privacy.html", "offers.html"] + \
            [f"league-{l['id']}.html" for l in LEAGUES]
    for name in pages:
        p = os.path.join(ROOT, name)
        if not os.path.exists(p):
            continue
        with open(p, encoding="utf-8") as f:
            s = f.read()
        s2 = re.sub(r"Last updated: (?:\S+ )?\d{1,2} \S+ \d{4}", f"Last updated: {BUILD_DATE_EN}", s)
        s2 = re.sub(r"Last checked: (?:\S+ )?\d{1,2} \S+ \d{4}", f"Last checked: {BUILD_DATE_EN}", s2)
        s2 = re.sub(r"Last checked (?:\S+ )?\d{1,2} \S+ \d{4}", f"Last checked {BUILD_DATE_EN}", s2)
        if s2 != s:
            w(p, s2)


def main():
    _load_live_data()  # Prefers data/*.json (written by the daily update) over the embedded data
    # ---- data files (verified only) ----
    dump(os.path.join(ROOT, "data/leagues-en.json"),
         {"updated": CHECKED, "leagues": LEAGUES,
          "note": f"Full tables verified for every league (last checked {en_date(CHECKED)}). Source: ESPN + FRMF.ma for Botola Pro."})
    dump(os.path.join(ROOT, "data/fixtures-en.json"),
         {"updated": CHECKED,
          "today_date": FX_TODAY_DATE, "tomorrow_date": FX_TOMORROW_DATE,
          "note": FX_NOTE or "All times UTC.",
          "live": FX_LIVE, "today": FX_TODAY, "tomorrow": FX_TOMORROW,
          "upcoming": UPCOMING, "results": RESULTS})
    with open(os.path.join(ROOT, "data/news-en.json"), encoding="utf-8") as f:
        news = json.load(f)
    news["articles"] = [a for a in news["articles"] if a.get("category") != "Champions League"]
    dump(os.path.join(ROOT, "data/news-en.json"), news)

    # ---- CSS ----
    css = os.path.join(ROOT, "assets/css/style.css")
    with open(css, encoding="utf-8") as f:
        s = f.read()
    _ar_marker = "/* ---------- الملعب V2"
    if _ar_marker in s:
        s = s[:s.index(_ar_marker)].rstrip() + "\n"
    if "MatchPulse" not in s:
        w(css, s + CSS_ADD)

    # ---- JS ----
    w(os.path.join(ROOT, "assets/js/main.js"), MAIN_JS)
    w(os.path.join(ROOT, "assets/js/matches.js"), MATCHES_JS)
    w(os.path.join(ROOT, "assets/js/standings.js"), STANDINGS_JS)
    w(os.path.join(ROOT, "assets/js/home.js"), HOME_JS)
    w(os.path.join(ROOT, "assets/js/match.js"), MATCH_JS)
    fb = {"updated": CHECKED, "leagues": LEAGUES,
          "fixtures": {"live": FX_LIVE, "today": FX_TODAY, "tomorrow": FX_TOMORROW, "upcoming": UPCOMING, "results": RESULTS}}
    w(os.path.join(ROOT, "assets/js/data-fallback.js"),
        f"/* MatchPulse — verified fallback data ({BUILD_DATE_EN}), used only if data/*.json cannot be loaded */\n"
        "const FALLBACK = " + json.dumps(fb, ensure_ascii=False, indent=2) + ";\n")

    # ---- index.html (fresh) ----
    HERO, STRIP = hero_blocks()
    index = f"""<!DOCTYPE html>
<html lang="en" dir="ltr">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>MatchPulse | Today’s fixtures, live scores, league tables & latest news</title>
<meta name="description" content="MatchPulse — today’s fixtures and live results, tables for the Premier League, La Liga, Serie A, Bundesliga, Ligue 1 and Botola Pro, and the latest news in English. Last updated: {BUILD_DATE_EN}.">
<meta property="og:title" content="MatchPulse | Live scores & football news">
<meta property="og:description" content="Today’s fixtures, tables for Europe’s five major leagues and Botola Pro, and the latest news.">
<meta property="og:type" content="website">
<meta property="og:locale" content="en_US">
<script type="application/ld+json">{{"@context":"https://schema.org","@type":"WebSite","name":"MatchPulse","alternateName":"Al MatchPulse","inLanguage":"en","description":"Follow fixtures, results and tables for Europe’s five major leagues and Botola Pro."}}</script>
{FONTS}
{ICON}
</head>
<body>
{header("index.html")}
{CHIPS}
{AD_LEADER}
{TICKER}
<main class="container">
{HERO}

{STRIP}

  <section class="section">
    <div class="section-head"><h2>Upcoming fixtures</h2><a class="more" href="matches.html">All fixtures →</a></div>
    <div class="match-list" id="home-matches"><p style="color:var(--muted)">Loading…</p></div>
    <p class="data-note"><b>Fixture sources:</b> ESPN (site.api.espn.com) for the five European leagues + FRMF.ma for Botola Pro — Last checked: {BUILD_DATE_EN}. All times UTC.</p>
  </section>

  {offers_html("leaderboard")}

  <section class="section">
    <div class="section-head"><h2>Latest news</h2><a class="more" href="news.html">All news →</a></div>
    <div class="news-grid" id="home-news"></div>
    <p style="color:var(--muted);font-size:.82rem">News is archived by publication date (September 2026) — current numbers and tables are on the tables and fixtures pages.</p>
  </section>

  <section class="section">
    <div class="section-head"><h2>Full league tables</h2><a class="more" href="standings.html">Full tables →</a></div>
    <div class="news-grid" id="home-tables" style="grid-template-columns:repeat(auto-fill,minmax(300px,1fr))"></div>
  </section>

</main>
{footer()}
<script src="assets/js/data-fallback.js"></script>
<script src="assets/js/main.js"></script>
<script src="assets/js/home.js"></script>
</body>
</html>"""
    w(os.path.join(ROOT, "index.html"), index)

    # ---- matches.html (fresh) ----
    matches = f"""<!DOCTYPE html>
<html lang="en" dir="ltr">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Today’s fixtures & live results | MatchPulse</title>
<meta name="description" content="Today’s, tomorrow’s and upcoming fixtures plus results from Europe’s five major leagues and Botola Pro. Last updated: {BUILD_DATE_EN}.">
<meta property="og:title" content="Today’s fixtures — live results | MatchPulse">
<meta property="og:locale" content="en_US">
{FONTS}
{ICON}
</head>
<body>
{header("matches.html")}
{CHIPS}
{AD_LEADER}
{TICKER}
<main class="container">
  <section class="section">
    <div class="section-head"><h1 style="font-size:1.6rem">⚽ Fixtures of the six leagues</h1></div>
    <p class="data-note"><b>Today {en_date(FX_TODAY_DATE) if FX_TODAY_DATE else ""}:</b> {FX_NOTE} All times UTC.</p>
    <div class="tabs">
      <button data-tab="today" class="active">📅 Today {en_date_short(FX_TODAY_DATE) if FX_TODAY_DATE else ""}</button>
      <button data-tab="tomorrow">📅 Tomorrow {en_date_short(FX_TOMORROW_DATE) if FX_TOMORROW_DATE else ""}</button>
      <button data-tab="friday">⏭️ Upcoming</button>
      <button data-tab="upcoming">🗓️ All upcoming</button>
      <button data-tab="results">✅ Latest results</button>
    </div>
    <div id="matches-box"><p style="color:var(--muted);text-align:center">Loading…</p></div>
    {offers_html()}
    <p style="color:var(--muted);font-size:.78rem;margin-top:14px">💡 Live results appear here only from a trusted live data source. No live source is connected right now — this page shows verified scheduled fixtures and the latest results only, no simulation.</p>
  </section>
</main>
{footer()}
<script src="assets/js/data-fallback.js"></script>
<script src="assets/js/main.js"></script>
<script src="assets/js/matches.js"></script>
<script>document.addEventListener("DOMContentLoaded",()=>window.renderTicker("ticker-track"));</script>
</body>
</html>"""
    w(os.path.join(ROOT, "matches.html"), matches)

    # ---- match.html (fresh template) ----
    match = f"""<!DOCTYPE html>
<html lang="en" dir="ltr">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Match details | MatchPulse</title>
<meta name="description" content="Match details: score, events, statistics, lineups and head-to-head — MatchPulse.">
<meta property="og:title" content="Match details | MatchPulse">
<meta property="og:locale" content="en_US">
<script type="application/ld+json">{{"@context":"https://schema.org","@type":"SportsEvent","name":"Manchester City × Fulham","sport":"football","startDate":"2026-11-21T12:30:00Z","location":{{"@type":"Place","name":"Etihad Stadium","address":"Manchester, England"}},"homeTeam":{{"@type":"SportsTeam","name":"Manchester City"}},"awayTeam":{{"@type":"SportsTeam","name":"Fulham"}},"competitor":[{{"@type":"SportsTeam","name":"Manchester City"}},{{"@type":"SportsTeam","name":"Fulham"}}]}}</script>
{FONTS}
{ICON}
</head>
<body>
{header("")}
{CHIPS}
{TICKER}
<main class="container">
  <section class="section">
    <h1 id="match-h1" style="font-size:1.6rem">Match details</h1>
    <div id="match-detail"><p style="color:var(--muted)">Loading…</p></div>
  </section>
</main>
{footer()}
<script src="assets/js/data-fallback.js"></script>
<script src="assets/js/main.js"></script>
<script src="assets/js/match.js"></script>
</body>
</html>"""
    w(os.path.join(ROOT, "match.html"), match)

    # ---- league pages (fresh, static SEO content) ----
    cat_by_league = {"premier-league": "Premier League", "la-liga": "La Liga",
                     "ligue-1": "Ligue 1", "botola": "Botola Pro"}
    for l in LEAGUES:
        lg_fx = [m for m in UPCOMING if m["league"] == l["id"]]
        fx_html = fixtures_list_html(lg_fx) if lg_fx else \
            '<div class="placeholder-box">This league’s upcoming fixture list has not been published in verified form yet — pending verification from an official source.</div>'
        lg_news = [a for a in news["articles"] if a.get("category") == cat_by_league.get(l["id"], "")]
        if lg_news:
            news_html = '<div class="news-grid">' + "".join(
                f'<a href="news/{a["slug"]}.html" class="news-card"><div class="news-thumb">{a["emoji"]}</div>'
                f'<div class="news-body"><div class="news-meta"><span class="cat">{a["category"]}</span><span>{a["date"]}</span></div>'
                f'<h3>{a["title"]}</h3><p>{a["excerpt"]}</p></div></a>'
                for a in lg_news) + "</div>"
        else:
            news_html = '<div class="placeholder-box">No news about this league in the site archive yet.</div>'
        page = f"""<!DOCTYPE html>
<html lang="en" dir="ltr">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{l["name"]} | MatchPulse</title>
<meta name="description" content="{l["meta"]}">
<meta property="og:title" content="{l["name"]} | MatchPulse">
<meta property="og:description" content="{l["meta"]}">
<meta property="og:type" content="website">
<meta property="og:locale" content="en_US">
{FONTS}
{ICON}
</head>
<body>
{header("standings.html")}
{CHIPS}
{AD_LEADER}
{TICKER}
<main class="container page" style="max-width:1100px">
  <h1>{league_logo_img(l["id"])}{l["name"]} <small style="color:var(--muted);font-size:1rem">— Season {l["season"]} • {l["round"]}</small></h1>
  <p class="data-note"><span class="verified-tag">✓ Verified</span> <b>Source:</b> {l["source"]} — <b>Last checked:</b> {BUILD_DATE_EN}. The full table is verified.</p>
  <section class="section" style="padding-top:6px">
    <div class="section-head"><h2>League table</h2><span style="color:var(--muted);font-size:.82rem">{l["next_round"]}</span></div>
    {table_html(l)}
  </section>
  <section class="section">
    <div class="section-head"><h2>Top scorers</h2></div>
    {scorers_html(l)}
  </section>
  <section class="section">
    <div class="section-head"><h2>Fixtures & results</h2><a class="more" href="matches.html">All fixtures →</a></div>
    {fx_html}
  </section>
  {offers_html()}
  <section class="section">
    <div class="section-head"><h2>{l["short"]} news</h2><a class="more" href="news.html">All news →</a></div>
    {news_html}
  </section>
</main>
{footer()}
<script src="assets/js/data-fallback.js"></script>
<script src="assets/js/main.js"></script>
<script>document.addEventListener("DOMContentLoaded",()=>window.renderTicker("ticker-track"));</script>
</body>
</html>"""
        w(os.path.join(ROOT, f"league-{l['id']}.html"), page)

    # ---- patches to copied pages ----
    patch(os.path.join(ROOT, "standings.html"), [
        ('<meta name="description" content="2026-27 league tables for Europe’s five major leagues and Botola Pro — top 5 verified for every league (Last checked 18 November 2026) with each league’s top scorers.">',
         '<meta name="description" content="2026-27 league tables for Europe’s five major leagues and Botola Pro — full tables verified for every league (last checked 18 November 2026) with each league’s top scorers.">'),
        ('<title>League tables — Europe & Botola Pro | MatchPulse</title>',
         '<title>League tables — Europe’s five major leagues & Botola Pro | MatchPulse</title>'),
        ('Last updated: 20 September 2026', 'Last updated: 18 November 2026'),
        ('<div class="scorers" id="scorers"></div>\n  </section>',
         '<div class="scorers" id="scorers"></div>\n  </section>\n  ' + CPA_SLOT),
    ])
    patch(os.path.join(ROOT, "news.html"), [
        ('<meta name="description" content="Latest news football: Europe’s five major leagues, Champions League, the Morocco national team and Botola Pro — daily coverage in English.">',
         '<meta name="description" content="Latest football news: Europe’s five major leagues, the Morocco national team and Botola Pro — daily coverage in English.">'),
        ('      <button data-cat="Champions League">Champions League</button>\n', ''),
        ('Last updated: 20 September 2026', 'Last updated: 18 November 2026'),
        ('    <div class="section-head"><h2>📰 Latest news</h2></div>',
         '    <div class="section-head"><h2>📰 Latest news</h2></div>\n    <p class="data-note">News is archived by publication date (September 2026) — current numbers and tables are on the tables and fixtures pages.</p>'),
        ('    <!-- AdSense: in-feed -->\n    <div class="ad-slot"><div class="ad-infeed">In-feed ad space</div></div>',
         '    <!-- AdSense: in-feed -->\n    <div class="ad-slot"><div class="ad-infeed">In-feed ad space</div></div>\n    ' + CPA_SLOT),
    ])
    patch(os.path.join(ROOT, "about.html"), [
        ('for Europe’s five major leagues and Botola Pro.',
         'for the five European leagues major and Botola Pro.'),
        ('  <p>We rely on trusted sports data providers (such as API-Football) to update results and tables automatically, while is written the news content from by the editorial team based on trusted press sources. We do not publish rumours as facts: any unconfirmed news is stated clearly.</p>',
         '  <p>We rely on trusted, publicly available sports sources to update results and tables, and we cite the source and check date for every number. We do not publish rumours as facts: any unconfirmed news is stated clearly.</p>'),
        ('Last updated: 20 September 2026', 'Last updated: 18 November 2026'),
    ])
    for f in ["contact.html", "privacy.html"]:
        patch(os.path.join(ROOT, f), [('Last updated: 20 September 2026', 'Last updated: 18 November 2026')])
    # news articles: footer date + CPA placeholder in sidebar
    for name in os.listdir(os.path.join(ROOT, "news")):
        p = os.path.join(ROOT, "news", name)
        patch(p, [
            ('Last updated: 20 September 2026', 'Last updated: 18 November 2026'),
            ('<div class="ad-rect">Ad space<br>300 × 250</div>',
             '<div class="ad-rect">Ad space<br>300 × 250</div>\n      <div class="offers-teaser"><a href="../offers.html">🎁 Free offers &amp; rewards <span class="ad-label">#ad</span> — see the 4 live offers &rarr;</a></div>'),
        ])

    # ---- offers.html (live CPA offers) ----
    w(os.path.join(ROOT, "offers.html"),
        offers_page_html().format(BASE=BASE, header=header("offers.html"), footer=footer()))

    # ---- sitemap / robots / render.yaml ----
    urls = ["index.html", "matches.html", "match.html", "standings.html", "news.html",
            "about.html", "contact.html", "privacy.html", "offers.html"] + \
           [f"league-{l['id']}.html" for l in LEAGUES] + \
           [f"news/{a['slug']}.html" for a in news["articles"]]
    sm = ['<?xml version="1.0" encoding="UTF-8"?>',
          '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'] + \
         [f'  <url><loc>{BASE}/{u}</loc><lastmod>{CHECKED}</lastmod></url>' for u in urls] + \
         ['</urlset>']
    w(os.path.join(ROOT, "sitemap.xml"), "\n".join(sm) + "\n")
    w(os.path.join(ROOT, "robots.txt"),
        "User-agent: *\nAllow: /\nDisallow: /tools/\n\n"
        f"Sitemap: {BASE}/sitemap.xml\n")
    w(os.path.join(ROOT, "render.yaml"),
        "services:\n  - type: web\n    name: matchpulse\n    env: static\n"
        "    buildCommand: \"\"\n    staticPublishPath: .\n")
    w(os.path.join(ROOT, "README.md"),
        "# MatchPulse\n\nStatic site in English (HTML/CSS/JS only) — the six leagues only: English, Spanish,\n"
        "Italian, German, French + Botola Pro — 6 leagues only.\n\n"
        f"- Data in `data/*.json` — verified only (last checked {BUILD_DATE_EN}). Source: ESPN + FRMF.ma for Botola Pro.\\n"
        "- Daily update: `python3 tools/daily-update.py` (see `tools/DAILY-README.md`).\\n"
        "- No API-Football (account suspended) — source: ESPN public API, no key.\\n"
        "- Publishing: static site on Render — see `REPORT.md`.\n"
        "- Rebuild: `python3 tools/build-en.py` from inside the folder.\n")

    # ---- Update frozen dates in pages generated from V1 ----
    refresh_dates()


if __name__ == "__main__":
    main()
    print("MatchPulse built in", ROOT)
