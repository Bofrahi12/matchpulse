# MatchPulse

Static site in English (HTML/CSS/JS only) — the six leagues only: English, Spanish,
Italian, German, French + Botola Pro — 6 leagues only.

- Data in `data/*.json` — verified only (last checked Sunday 22 November 2026). Source: ESPN + FRMF.ma for Botola Pro.\n- Daily update: `python3 tools/daily-update.py` (see `tools/DAILY-README.md`).\n- No API-Football (account suspended) — source: ESPN public API, no key.\n- Publishing: static site on Render — see `REPORT.md`.
- Rebuild: `python3 tools/build-en.py` from inside the folder.
