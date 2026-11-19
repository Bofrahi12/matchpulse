# MatchPulse — Offers redesigned as real ads (REPORT-ADS)

**Date:** 19 November 2026 — user correction: «لا، العروض يبانو بحال إعلان مشي هيدا»
(the old plain list looked like content, not ads).

## What changed

The 4 CPAlead offers are now **sponsored display-ad units**, not content cards.
Nothing else changed: no link, price, geo or data value was touched; tables,
fixtures, news and all non-offers content are identical.

Every ad unit has, like a real display ad:
- an amber **SPONSORED** badge in the top corner + `#ad` on the section,
- a **brand-colour visual tile** with a plain symbol (CSS only — no invented
  logos, no product photos): 💎 Hidden Gems (teal), 🔒 Free VPN (blue),
  🎬 CapCut Pro (violet), 📝 Complete 3 Surveys (amber),
- a **bold promo headline** (the offer name) + a short benefit line,
- geo / device line, and a **big pill CTA button** in the brand colour
  (GET THE APP / DOWNLOAD FREE / START FREE TRIAL / START NOW — the CTA
  text comes from `data/offers.json`, unchanged).

## The 3 ad formats and where each appears

| Format | Where | What it looks like |
|---|---|---|
| **Leaderboard banner** | `index.html` (homepage) | Wide horizontal banner (970×250 style) for the Featured offer (Discover Hidden Gems): big visual, headline, benefit, big CTA — under a centred `ADVERTISEMENT #ad` label. Below it, the other 3 offers as vertical mini ad cards (300×250 style) in a 3-column row. |
| **Box stack** | `standings.html`, `news.html`, `matches.html`, all 6 league pages | Compact stack of the 4 offers as horizontal ad units (visual left, headline + benefit + geo/device, pill CTA right). 2 columns on desktop, 1 column on mobile, CTA full-width on phones. Header: "Sponsored offers #ad". |
| **Showcase rows** | `offers.html` (main ad showcase page) | Large ad units, one per offer: 88px visual tile, tag chip (FEATURED / TOP PAYOUT / FOR CREATORS / QUICK REWARD), headline, benefit, facts line (payout · countries · devices · daily cap) and a full-width CTA button. |

The small link teaser on news-article pages ("see the 4 live offers") was left
as-is — it is a link to the offers page, not an ad unit.

## The 4 offers (unchanged links, prices, geo)

- Discover Hidden Gems — $0.39/install, CA/GB/US, iPhone iOS 15.1+ —
  https://www.qckclk.com/view.php?id=5547390&pub=3371268
- Free VPN for Windows — $3.90, US Desktop only —
  https://www.cdndn.com/view.php?id=5547320&pub=3371268
- CapCut Pro — 7-Day Trial on PC — $1.17, CA/DE/FR/GB/US —
  https://www.directcpi.com/view.php?id=5543635&pub=3371268
- Complete 3 Surveys — $1.56, AU/CA/GB/US —
  https://www.qckclk.com/view.php?id=5547288&pub=3371268

`#ad` disclosure is shown on every placement.

## How it is built (so the daily update keeps it)

- Source of truth: `tools/make-build-en.py` — `OFFERS_CODE` (ad generators:
  `ad_card` / `ad_mini` / `ad_leaderboard` / `offers_html(variant)` /
  `offers_page_html`) + the ad CSS in `CSS_ADD_EN`. It regenerates
  `tools/build-en.py` (run `python3 tools/make-build-en.py`).
- The rebuild is idempotent: re-running `tools/build-en.py` does not
  duplicate any offers section (verified twice — 1 section per page).
- Note: `standings.html` / `news.html` are patched in place, so before the
  first rebuild with the new design the old sections were stripped once.
  The live `assets/css/style.css` was updated with the new ad CSS in the
  same edit (the build only appends CSS once).

## Local verification (19 Nov 2026, after rebuild)

- 8/8 pages 200 on a local server: index, matches, standings, news, offers,
  league-premier-league, data/fixtures-en.json, sitemap.xml.
- Ad markup: index = 1 leaderboard + 3 mini + 4 Sponsored badges;
  standings / news = 4 ad units + 4 Sponsored; offers = 4 showcase rows +
  4 Sponsored; matches + league pages = 4 ad units each.
- All 4 exact tracking links present and unchanged (6 occurrences each
  across the checked pages); footer date still "Thursday 19 November 2026";
  data intact (56 upcoming, 48 results, tables 20/20/20/18/18/16).
- 0 Arabic characters in served files (HTML/CSS/JS; the 3 translation
  dictionaries `logos.json` / `player-names.json` / `botola-manual.json`
  are not served or linked).
- Screenshots checked visually (desktop 1280px + mobile 390px): ads read as
  display ads; one real bug found and fixed — the tag chip stretched
  full-width in the flex column (added `align-self: flex-start`).

## Not deployed

Per instructions: no push, no Render deploy — the parent deploys after review.
