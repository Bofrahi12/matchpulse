# MatchPulse — Live Football Scores, Fixtures, Tables & Stats

**Brand:** MatchPulse — live scores, fixtures, tables & stats, updated every day.
**Audience:** USA / UK / Europe. **Language:** English only, LTR.
**Live URL (after deploy):** https://matchpulse.onrender.com
**Status 2026-11-19:** built + verified locally. NOT deployed yet — no GitHub
repo, no Render service (the main agent creates those).

## What it is

The full English version of the Almalaeb sports site (`~/workspace/almalaeb-v2`,
Arabic, live at https://almalaeb.onrender.com). Same data, same pro look
(status badges, match tabs, stat bars, club logos), new brand, English UI,
UTC times, and live CPA offers. **6 leagues only — no Champions League
anywhere** (no UCL table, fixtures, filter, or link; two passing mentions in
news prose were rephrased out on 2026-11-19).

Leagues: Premier League · La Liga · Serie A · Bundesliga · Ligue 1 ·
Botola Pro (Morocco).

## Layout

```
matchpulse/
  index.html  matches.html  standings.html  match.html  offers.html
  league-premier-league.html  league-la-liga.html  league-serie-a.html
  league-bundesliga.html  league-ligue-1.html  league-botola.html
  news.html  news/*.html (8 articles)  about.html  contact.html  privacy.html
  sitemap.xml  robots.txt  ads.txt  render.yaml
  assets/css/style.css  assets/js/main.js  assets/js/standings.js
  assets/js/data-fallback.js  assets/logos/ (club logos)
  data/
    leagues-en.json  fixtures-en.json  news-en.json  offers.json   <- served (0 Arabic)
    botola-manual.json  logos.json  player-names.json              <- AR<->EN maps (build inputs)
  tools/
    daily-update.py     one fetch -> AR + EN files, then rebuilds
    build-en.py         renders the EN site (generated, do not hand-edit)
    make-build-en.py    generates build-en.py from almalaeb build-v2.py
    translate-static.py translates the 5 static pages + base CSS + ads.txt
    DAILY-README.md     daily-update guide (EN)
```

## EN data architecture — one fetch feeds both sites

`tools/daily-update.py` (a copy of the Arabic site's fetcher, extended):

1. Fetches ESPN public API (no key) — scoreboard, records, leaders, summaries.
2. Captures English names **at fetch time** (team/player/stadium/league), then
   translates to Arabic via `data/logos.json` + `data/player-names.json`.
3. Writes **both** in the same run, atomically, with restore-on-failure:
   - Arabic: `data/leagues.json` + `data/fixtures.json` (Morocco time)
   - English: `data/leagues-en.json` + `data/fixtures-en.json` (**UTC**)
   Both go through the same `validate()` (language-neutral checks).
4. Rebuilds the EN site via `tools/build-en.py` (unless `--no-build`).

Flags: `--ar-dir DIR` (where the Arabic files go — the cron MUST point this
at `~/workspace/almalaeb-v2/data`, otherwise the Arabic files land in
`matchpulse/data/`), `--en-dir DIR`, `--no-build`.

`tools/build-en.py` is **generated** by `tools/make-build-en.py` (a transformer
of the Arabic `build-v2.py`): UI phrases translated longest-first, data names
(teams/players/venues/leagues/months/weekdays/cities) whole-word only via
boundary-aware regex, so «كومو» can never corrupt «جياكومو» and «الأحد» can
never corrupt «الأحداث». Regenerate after any change to the transformer:
`python3 tools/make-build-en.py && python3 tools/build-en.py`.

`tools/translate-static.py` translates the 5 static pages
(standings/news/about/contact/privacy), the base CSS (incl. LTR rules:
`direction`, `text-align`, border/margin sides, Inter font) and `ads.txt`,
using the same `transform()` as the builder. It also fixes two real bugs it
found: `news.html` called `window.MalaebData` (undefined on the EN site — now
`window.MatchPulseData`) and `main.js` fetched `data/news.json` (missing — now
`data/news-en.json`; the fix is also in `make-build-en.py` so it survives
regeneration).

## CPA offers — live (4, all verified)

Section "Free offers & rewards" with `#ad` disclosure on the home page,
standings, news, and a dedicated `offers.html` page. No popups, no betting,
no dating, no casino, no psychic. Links are exact CPAlead tracking links for
publisher account 3371268 — never hand-edit a link (CPAlead uses a different
redirect domain per offer); new links only from the CPAlead dashboard.

| # | Offer | Payout | GEO / device | Exact tracking link |
|---|-------|--------|--------------|---------------------|
| 1 ⭐ | Discover Hidden Gems | $0.39 / install | CA/GB/US, iPhone iOS 15.1+, CAP 40/day | https://www.qckclk.com/view.php?id=5547390&pub=3371268 |
| 2 | Free VPN for Windows | $3.90 | US, Desktop only, CAP 20/day | https://www.cdndn.com/view.php?id=5547320&pub=3371268 |
| 3 | CapCut Pro — 7-day trial on PC | $1.17 | CA/DE/FR/GB/US, all devices, no cap | https://www.directcpi.com/view.php?id=5543635&pub=3371268 |
| 4 | Complete 3 surveys | $1.56 | AU/CA/GB/US, all devices, CAP 20/day | https://www.qckclk.com/view.php?id=5547288&pub=3371268 |

### Extra offers checked 2026-11-19 — NONE added (no verified tracking link)

The user asked for more offers. All five candidates were checked against the
real sources (CineScope files, memory records, CPAlead public marketplace,
OfferVault). **Zero could be added: every one lacks a verified exact tracking
link**, and the rule is absolute — no link, no listing.

| Candidate | Payout / GEO (verified) | Why NOT added |
|-----------|------------------------|---------------|
| LifePoints (CPAlead) | $1.64, US, no cap, NET-30 — confirmed in the CineScope report + CPAlead marketplace (rank 14) | No offer ID and no tracking link anywhere (workspace, memory, public marketplace). Needs the CPAlead dashboard (publisher sign-in). |
| Nielsen Pulse (CPAlead) | US, mobile only — confirmed on the CPAlead marketplace (rank 10); **payout is ambiguous: $2.73 in some records, $3.12 in others** (likely two variants) | No offer ID, no tracking link, and the payout itself is unverified. Needs the dashboard. |
| TransUnion (CPAlead) | $8.42, US, no cap, NET-30 — from the CineScope report | No offer ID, no tracking link. Also a credit product with a long form — trust mismatch on a football site. Needs the dashboard. |
| Swagbucks (Adpump 13562) | $23 mobile / $27 desktop per valid lead, US/UK/CA — $23 confirmed by OfferVault (Adpump listing) | No tracking link: Adpump links are per-publisher; his applications (OPERAGX 16563 + Survey Junkie 12861) are still PROCESSING, and Swagbucks was not even among them. Addable only after Adpump approval + requesting the offer. |
| ScholarshipOwl (Adpump 14859) | $7.70 free trial / $16.90 subscription, US — from the 2026-11-18 public scan (not re-confirmed independently) | No tracking link, same Adpump reason as Swagbucks. |

**What unblocks them:** (1) CPAlead — sign in to the publisher dashboard
(account 3371268), open each offer, copy its exact tracking link; then add one
entry per offer to `data/offers.json` and rebuild. (2) Adpump — wait for the
OPERAGX/Survey Junkie approval, then request Swagbucks + ScholarshipOwl and
copy their tracking links the same way. Also seen but deliberately NOT added:
PlataCash (ID 5547403 — tracking link was never obtained; its "$14.60" is a
misleading max-across-10-events figure, not per install).

## Verification (local, 2026-11-19, `python3 -m http.server`)

- **34/34 URLs return 200**: index, matches, standings, match, 6 league
  pages, news, about, contact, privacy, offers, 8 news articles, 4 EN JSONs,
  sitemap, robots, ads.txt, CSS + 3 JS files.
- **Counts match the Arabic site**: upcoming 56, results 48, today 0,
  tomorrow 3, live 0; tables 20/20/20/18/18/16; 10 scorers per league;
  8 news articles.
- **0 Arabic characters** in every served file (all HTML, CSS, JS, EN JSON,
  sitemap, robots, ads.txt). 0 "Champions League" in served files.
- **4/4 CPA links** present and exact on index, offers, standings, news.
- Footer date = today (Thursday 19 November 2026). Sitemap BASE
  https://matchpulse.onrender.com, 23 URLs, offers.html included.
- Build is idempotent: re-running `build-en.py` does not duplicate the offers
  section (verified twice).

**Known non-served Arabic:** the three AR↔EN mapping files
(`data/logos.json`, `data/player-names.json`, `data/botola-manual.json`) keep
Arabic names — they are the translation dictionaries the daily fetch needs,
not linked or fetched by any page. `tools/build-en.py` line 2288 keeps one
intentional Arabic line (`_ar_marker`) — the strip marker must match the
Arabic text in the copied CSS. The Arabic data files (`data/leagues.json`,
`data/fixtures.json`, `data/news.json`) were deleted from this repo on
2026-11-19; the cron must use `--ar-dir ~/workspace/almalaeb-v2/data` so they
are never recreated here.

## Remaining (for the main agent)

1. **GitHub repo** — create `matchpulse` (the stored fine-grained token
   cannot create repos; the user creates it or provides a classic token).
2. **Render static site** — service name `matchpulse`, publish from the repo
   root (`render.yaml` already in the repo, service name `matchpulse`).
3. **Daily cron** — one morning run feeding both sites (see
   `tools/DAILY-README.md` for the exact command and flags), silent unless
   failure or Botola manual file > 3 days old.
4. **Search Console + GA4** — need the user's Google sign-in (same as Almalaeb).
5. **CPA unblock** — CPAlead dashboard links for LifePoints / Nielsen Pulse /
   TransUnion; Adpump approval, then Swagbucks / ScholarshipOwl links.

## Known limits (same as Almalaeb)

No live minute-by-minute scores (morning run only); no referees (ESPN does not
provide them — "To be confirmed"); lineups/H2H are explicit placeholders;
La Liga tiebreak may differ from official on a full tie; Botola fully manual.
