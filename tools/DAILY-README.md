# MatchPulse — daily data update

## The idea in one line

Every morning `tools/daily-update.py` fetches from the **ESPN public API (no key,
no subscription)** today's matches + 4 days ahead, results from the last 14 days,
tables, top scorers, and details for every result (stats + goal events + stadium)
for the five European leagues, merges the Moroccan Botola from
`data/botola-manual.json` (manual — ESPN does not cover Botola at all:
`mar.1` returns 404), and rebuilds the whole site.

**One fetch feeds BOTH sites.** The same run writes the Arabic files
(`data/leagues.json` + `data/fixtures.json`) and the English files
(`data/leagues-en.json` + `data/fixtures-en.json`). English names are captured
at ESPN fetch time, before translation to Arabic — never translated back from
Arabic.

## Daily run

```bash
cd ~/workspace/matchpulse && python3 tools/daily-update.py
```

- **When:** every morning Morocco time, **before 12:00** (best ~09:00 — after
  the night's tables/results are out, before visitor peak).
- **Duration:** ~3 minutes (~300 ESPN requests, parallel).
- **Cron command** (created by the main agent — not from here). One run feeds
  both repos; the Arabic files must go to the Arabic repo, never into
  `matchpulse/data/`:

```cron
0 9 * * * cd /home/hatch/workspace/matchpulse && /usr/bin/python3 -u tools/daily-update.py --ar-dir /home/hatch/workspace/almalaeb-v2/data >> /tmp/matchpulse-daily.log 2>&1
```

Then rebuild + push the Arabic site (`~/workspace/almalaeb-v2`,
`tools/build-v2.py` + its push) and push this repo — or keep the existing
Arabic cron as-is and add a second EN cron that runs the same fetch with
`--ar-dir ~/workspace/almalaeb-v2/data` (the fetch is idempotent; running it
twice a day just re-fetches identical data).

**Flags:** `--no-build` (write the 4 data files, skip the rebuild),
`--ar-dir DIR` (where the Arabic files go; default: own `data/`),
`--en-dir DIR` (where the English files go; default: own `data/`).

## What the script fetches (and how)

| Data | Source | Method |
|---|---|---|
| Upcoming / results / live | `site.api.espn.com/.../scoreboard?dates=YYYYMMDD` | Day by day: today..+4 for fixtures, last 14 days for results |
| Table | `sports.core.api.espn.com/.../teams/{id}/record` | Each team's record (P/W/D/L/GF/GA/pts), then sort: pts → GD → GF → wins |
| Top scorers | `.../seasons/2026/types/1/leaders` | Top 10, resolving player + team links |
| Result details | `site.api.espn.com/.../summary?event={id}` | Possession/shots/corners + goal events + cards + stadium |
| Botola | `data/botola-manual.json` | Merged as-is — no automatic fetch |

**Goal events:** a goal is detected by ESPN's own `scoringPlay == true` flag —
not by filtering the event type (goal types vary: `goal`, `goal---header`,
`goal---penalty`, `penalty---scored`…; a `startswith("goal")` filter used to
drop penalties).

**Name translation:** teams via `data/logos.json` (English name → Arabic, with
normalisation that strips diacritics/prefixes + an exceptions map for radically
different names such as Cologne=Köln). Players via `data/player-names.json`
(157 names, 19 Nov 2026). Any new player missing from the map is shown by
their Latin name as-is + a warning in the summary — never invent a translation.
Add the Arabic name to the map manually when one appears.

**Stadiums:** an English → Arabic map inside the script (~90 stadiums). A
stadium missing from the map is shown by its English name as-is (correct,
not invented).

**Times:** English files use **UTC** (audience USA/UK/Europe), labelled
"All times UTC". Arabic files stay Morocco time (UTC+1, UTC+0 in Ramadan;
this machine's tzdata for Africa/Casablanca is wrong, so the script uses a
fixed +1 offset with a Ramadan table 2026–2028 — update yearly).

**Channels:** `beIN Sports` for the five European leagues, `Arryadia TNT`
for Botola — the rights holders in Morocco/Middle East (fixed, not fetched).

## Botola — manual update (5 minutes every morning)

Before running the script, open `data/botola-manual.json` and update from the
**FRMF.ma** table (or Wikipedia 2026–27 Botola Pro, sourced from FRMF.ma).
**Update BOTH the Arabic fields and the `_en` fields** (team_en, player_en,
home_en/away_en, venue_en, round_en, next_round_en, source_en):

1. Field `updated` — today's date.
2. The full table (16 teams: pos, P, W, D, L, GF, GA, pts). If there is a
   points deduction (e.g. Témara: −1 by LNFP decision), add `"deduction": 1`
   to the team's row.
3. The top 10 scorers (player, team, goals).
4. Next-round fixtures (date + time, Morocco time) and last-round results.
5. If nothing changed, updating `updated` is enough.

If the file is older than 3 days the script prints a clear warning in the
summary. Note: disciplinary decisions (e.g. Wydad–Témara awarded 3-0 with a
point deducted) are not reflected by aggregators immediately — FRMF.ma is the
reference source.

## Safety — what happens on failure?

- **A whole league fetch fails** (network/ESPN): the script exits with an
  error (`exit 1`) and **never touches the old data** — the site stays on
  yesterday's data.
- **One match's details fail** (summary): the result is saved without stats +
  a warning, and the run continues.
- **Validation fails** (wrong row count, pts ≠ 3×W+D−deduction, empty value,
  duplicate match): no writing, no build, `exit 1`.
- **Build fails**: the old data copies are restored automatically.
- Writes are atomic (temp file + `os.replace`) — never a half-written file.

## Outputs after every run

- `data/leagues-en.json` + `data/fixtures-en.json` (English, UTC) and
  `data/leagues.json` + `data/fixtures.json` (Arabic, Morocco time — written
  to `--ar-dir`).
- Full rebuild via `tools/build-en.py` (pages + `data-fallback.js`).
- Printed summary: matches today/tomorrow/upcoming/results, results with
  stats and events, changes in the lead and top 3 scorers, and warnings.

## Known limits (not fixed by this script)

- **Morocco time — technical note:** this machine's tzdata is wrong for
  Morocco in 2026 (it gives `Africa/Casablanca` = UTC+0 in November; the
  correct value is UTC+1) — so the script uses a fixed +1 offset with a
  Ramadan exception (UTC+0) via the `RAMADAN_UTC0` table at the top of the
  file (2026–2028). **Update the table every year** (Ramadan moves ~11 days
  earlier per year). If the machine's tzdata is ever fixed, the behaviour
  stays correct.
- **No live minute-by-minute scores**: the script runs once in the morning;
  matches in progress appear in `live` only if the run happens during a match.
- **No referees**: ESPN summary does not provide referees — the referee slot
  stays "To be confirmed".
- **No lineups, no head-to-head (H2H)**: the match-page tabs stay explicit
  placeholders.
- **Tiebreak sorting**: sorted by points, then goal difference, then goals.
  La Liga uses head-to-head first when points are level — on a full tie
  (points + GD + goals) the order may differ from the official one; rare, and
  corrected manually if it appears.
- **Botola is fully manual** — no free reliable source covers it automatically
  (checked: ESPN 404, football-data.org does not cover it on the free tier).
