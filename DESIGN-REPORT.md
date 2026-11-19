# MatchPulse — PRO INTERNATIONAL redesign (DESIGN-REPORT)

**Date:** 19 November 2026 — user correction: «باقي الموقع ما كيبانش برو،
الديزاين ضعيف بزاف، خاص ديكشي بروفيسيونال، خاصنا يبان ديزاين إنترناشيونال»
(the old dark design looked like a template, not a top sports site).

## Design direction

Reference standard: **ESPN / BBC Sport / Sky Sports / Flashscore /
Sofascore** — light livescore systems, not dark dashboards. The old design
was dark navy `#0a0e17` with a green accent; the pro references are light,
so the whole system flipped to light.

## The design system

### Palette (one accent, no rainbow)

| Token | Value | Use |
|---|---|---|
| `--bg` | `#eef1f5` | Page background |
| `--card` | `#ffffff` | Cards, tables, rows |
| `--border` | `#dbe2ec` | 1px borders |
| `--text` | `#0f172a` | Headings / team names |
| `--muted` | `#64748b` | Secondary text, dates |
| `--navy` | `#0b1530` | Header, footer (dark navy) |
| `--accent` | `#1d4ed8` | The ONE accent (royal blue): links, active nav, buttons, zone blue |
| `--red` | `#e11d48` | Live only (LIVE badge, live minute, relegation) |
| `--green` | `#16a34a` | Finished / positive |

Header and footer stay dark navy; everything else is white cards on a
light grey page, with a single royal-blue accent. Live is the only red.

### Typography

- **Inter** 400 / 500 / 600 / 700 / 800 / 900 (Google Fonts).
- Page H1 / section H2: 1.06rem, weight 800, with a 4px blue bar before it.
- Match rows: team names .92rem / 600; time .78rem muted; score pill .95rem / 800.
- Tables: header .7rem uppercase letterspaced muted; rows 44px, .88rem.

### Spacing / cards

- Container max 1200px, cards `border: 1px solid #dbe2ec; border-radius:
  10–12px; box-shadow: 0 1px 3px rgba(15,23,42,.06)`.
- Sections separated by 22px; match rows separated by 8px gaps.

## Key components

- **Match rows (Flashscore-style):** time first (78px column: `20 Nov` +
  kick-off time on two lines; live minute in red; `FT` date for finished),
  then home team right-aligned, score in a light pill, away team
  left-aligned, 20px logos. Status badge in the league line
  (`NOT STARTED YET` amber / `Full time` / `● LIVE 67'`).
- **Tables:** sticky-feel light header, 44px rows, zone bars on the
  position cell + legend below the table. Zones (standard qualification
  spots; positions are real data, never invented):
  PL / La Liga / Serie A / Bundesliga — top 4 UCL (blue), bottom 3
  relegated (red); Ligue 1 — top 3 UCL, 4th UCL play-off (gold), 16th
  relegation play-off (gold), 17–18 relegated; Botola — top 2 CAF
  Champions League (blue), 3rd CAF Confederation Cup (gold), 15–16
  relegated. Form dots (W/D/L) are NOT shown: only one round of results
  (48) exists, so there is no form history to display — documented here,
  not fabricated.
- **Live section:** `Live now` block on the homepage above the hero +
  dedicated `live.html` (linked in the nav with a red count badge while
  matches are live). Reads the existing `live` array from
  `data/fixtures-en.json`. Pulsing red LIVE dot, minute, live score.
  Honest empty state — «No live matches right now» + next kickoff
  (FC Bayern Munich vs 1. FC Köln, Friday 20 November 2026, 19:30 UTC)
  + button to fixtures. Never fakes a live score.
- **Hero:** today's featured matches card (no matches today → honest
  «Today's matches: no matches in the six leagues» + next matchday).
- **Date strip:** Today / Tomorrow / next-day cards with match counts.
- **Ads:** restyled into the light system (same 3 formats, same 4 CPA
  links, Sponsored badge + `#ad` kept) + the Mobidea Smartlink unit —
  see `REPORT-ADS.md`.
- **Footer:** dark navy, 3 columns (brand / Sections / Info) + bottom
  bar with «Last updated: Thursday 19 November 2026».

## What changed per page

| Page | Change |
|---|---|
| `index.html` | Light system; Live Now section above hero; time-first match rows; leaderboard ad + 3 minis + Mobidea smartlink; news grid unchanged in content. |
| `live.html` | **New page.** Live scores + next kickoffs; nav Live item (active state). |
| `matches.html` | Time-first rows, tabs (Today / Tomorrow / Results), date strip. |
| `standings.html` | League picker pills (logos 22px); 44px tables with zone bars + legend; top scorers cards. |
| `league-*.html` | Same table treatment, per-league fixtures + results. |
| `match.html` | New scoreboard card (64px logos, big score pill), info bar (stadium / referee / TV / kick-off), pill tabs (Events / Statistics / Lineups / Head-to-head). |
| `news.html` / article pages | Light cards, same content. |
| `offers.html` | Showcase rows in the light system + Mobidea row. |
| `about / contact / privacy` | Light system, same copy. |

## How it is built (so the daily update keeps it)

- Source of truth: `tools/make-build-en.py` — the new light system is the
  `CSS_ADD_EN` block (replaces the old dark additions on every build:
  `main()` now strips any previous `MatchPulse: additions` block and
  re-appends it); `OFFERS_CODE` holds the ad generators + `live_nav_item`
  / `zone_class` / `zone_legend` / `live_section_html` / `live_page_html`
  / `smartlink_html`; `structural()` holds the reps (fonts weights,
  Live nav link, zone classes server + JS, time-first rows server + JS,
  live section insert, `live.html` generation, sitemap + refresh dates).
- Regenerate with `python3 tools/make-build-en.py`, then
  `python3 tools/build-en.py`. The build is idempotent (verified — 1 live
  section, 1 additions block, 1 offers section per page).

## Bugs found on screenshots and fixed in this pass

1. Team/league logos rendered at **intrinsic size** (Arsenal crest ~230px
   tall in the table; giant league logos in the picker) — no CSS rule
   sized `.team-logo` / `.league-logo` outside match rows. Added sizing
   rules: table 22px, league picker 22px, page title 30px, scorers 20px,
   scoreboard 64px.
2. Match page scoreboard, info bar and tabs had **no CSS at all** —
   unstyled stacked spans and default browser buttons. Styled all three
   (scoreboard card, info bar, pill tabs).
3. **Mobile horizontal overflow** at 390px: index 555px (date-strip grid
   cells could not shrink), standings 393px (section H2 was `display:flex`
   so its text could never wrap). Fixed with `min-width: 0` + wrapping
   and `display: block` on section H2s. All 7 pages now 390px clean.
4. Upcoming rows showed the kick-off time **twice** (time column + score
   pill). Score pill for upcoming matches is now `–`.

## Local verification (19 Nov 2026, after final rebuild)

- 13/13 pages 200 on a local server: index, live, matches, standings,
  news, offers, about, contact, privacy, league-premier-league,
  league-botola, sitemap.xml, robots.txt.
- Data intact: 56 upcoming, 48 results, 3 tomorrow, 0 live, tables
  20/20/20/18/18/16. All 4 CPA links unchanged; Mobidea URL present
  exactly as supplied; footer date «Thursday 19 November 2026».
- 0 Arabic characters in served HTML. Sitemap includes `live.html`.
- Screenshots read (desktop 1280px + mobile 390px): index, live,
  standings, league, offers, match, matches — no overflow, no
  misalignment, no stretched badges, contrast checked.

## Not deployed

Per instructions: no push, no Render deploy — the parent deploys after review.
