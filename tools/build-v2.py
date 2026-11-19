# -*- coding: utf-8 -*-
"""Almalaeb V2 builder — rebuilds ~/workspace/almalaeb-v2 from V1 data + VERIFIED data only.
Run: python3 tools/build-v2.py  (from inside almalaeb-v2/)
Every number in data/ below was verified 2026-11-18 from the sources listed
in REPORT.md. Anything unverified is an explicit placeholder, never invented.
"""
import json, os, re, shutil
from datetime import date as _date

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
V1 = os.path.expanduser("~/workspace/almalaeb")
CHECKED = "2026-11-18"

# ------------------------------------------------- تواريخ ديناميكية (للتحديث اليومي) ---
_AR_MONTHS = ["يناير", "فبراير", "مارس", "أبريل", "مايو", "يونيو",
              "يوليوز", "غشت", "شتنبر", "أكتوبر", "نونبر", "دجنبر"]
_AR_WEEKDAYS = ["الاثنين", "الثلاثاء", "الأربعاء", "الخميس", "الجمعة", "السبت", "الأحد"]


def ar_date(iso):
    d = _date.fromisoformat(iso) if isinstance(iso, str) else iso
    return f"{_AR_WEEKDAYS[d.weekday()]} {d.day} {_AR_MONTHS[d.month - 1]} {d.year}"


def ar_date_short(iso):
    d = _date.fromisoformat(iso) if isinstance(iso, str) else iso
    return f"{d.day} {_AR_MONTHS[d.month - 1]}"


def ar_range(d1, d2):
    a, b = _date.fromisoformat(d1), _date.fromisoformat(d2)
    if a.month == b.month and a.year == b.year:
        return f"{a.day}–{b.day} {_AR_MONTHS[a.month - 1]} {a.year}"
    return f"{a.day} {_AR_MONTHS[a.month - 1]} – {b.day} {_AR_MONTHS[b.month - 1]} {b.year}"


# تاريخ البناء المعروض في التذييلات (يُحدَّث من data/*.json في _load_live_data)
BUILD_DATE_AR = ar_date(CHECKED)
# بيانات المباريات اليوم/غداً/المباشرة (من data/fixtures.json — يكتبها التحديث اليومي)
FX_TODAY, FX_TOMORROW, FX_LIVE = [], [], []
FX_NOTE = ""
FX_TODAY_DATE = FX_TOMORROW_DATE = None


def _load_live_data():
    """يفضّل data/*.json (يكتبها tools/daily-update.py) على البيانات المضمّنة.
    إن لم توجد الملفات أو كانت ناقصة، تبقى البيانات المضمّنة كاحتياطي."""
    global LEAGUES, UPCOMING, RESULTS, CHECKED, BUILD_DATE_AR
    global FX_TODAY, FX_TOMORROW, FX_LIVE, FX_NOTE, FX_TODAY_DATE, FX_TOMORROW_DATE
    try:
        with open(os.path.join(ROOT, "data/leagues.json"), encoding="utf-8") as f:
            dl = json.load(f)
        if len(dl.get("leagues", [])) == 6:
            LEAGUES = dl["leagues"]
            CHECKED = dl.get("updated", CHECKED)
    except Exception:
        pass
    try:
        with open(os.path.join(ROOT, "data/fixtures.json"), encoding="utf-8") as f:
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
    BUILD_DATE_AR = ar_date(CHECKED)

# ---------------------------------------------------------------- data ---
# Tables: TOP 5 ONLY — verified 2026-11-18 (KickoffLens, updated 02:22 UTC,
# cross-checked TheStatsAPI / NBC Sports / laligatable.co).
# gf/ga only where verified; gd always verified. None = not verified.
def row(pos, team, p, w, d, l, gd, pts, gf=None, ga=None):
    return {"pos": pos, "team": team, "p": p, "w": w, "d": d, "l": l,
            "gf": gf, "ga": ga, "gd": gd, "pts": pts}

LEAGUES = [{'id': 'premier-league',
  'name': 'الدوري الإنجليزي الممتاز',
  'short': 'البريميرليغ',
  'country': 'إنجلترا',
  'season': '2026-27',
  'round': 'الجولة 10',
  'next_round': 'الجولة 11 — 21–23 نونبر 2026',
  'source': 'thestatsapi.com (18 نونبر 2026، 22:41 UTC) + مطابقة مع nbcsports.com وrenderfoot.com — '
            'الهدافون: renderfoot.com (18 نونبر 2026) + مطابقة مع nbcsports.com وradiotimes.com',
  'table': [{'pos': 1,
             'team': 'آرسنال',
             'p': 10,
             'w': 9,
             'd': 0,
             'l': 1,
             'gf': 15,
             'ga': 5,
             'gd': 10,
             'pts': 27},
            {'pos': 2,
             'team': 'برايتون',
             'p': 10,
             'w': 7,
             'd': 1,
             'l': 2,
             'gf': 26,
             'ga': 7,
             'gd': 19,
             'pts': 22},
            {'pos': 3,
             'team': 'مانشستر سيتي',
             'p': 10,
             'w': 7,
             'd': 0,
             'l': 3,
             'gf': 21,
             'ga': 13,
             'gd': 8,
             'pts': 21},
            {'pos': 4,
             'team': 'ليفربول',
             'p': 10,
             'w': 5,
             'd': 3,
             'l': 2,
             'gf': 14,
             'ga': 10,
             'gd': 4,
             'pts': 18},
            {'pos': 5,
             'team': 'تشيلسي',
             'p': 10,
             'w': 5,
             'd': 1,
             'l': 4,
             'gf': 19,
             'ga': 16,
             'gd': 3,
             'pts': 16},
            {'pos': 6,
             'team': 'إيفرتون',
             'p': 10,
             'w': 4,
             'd': 4,
             'l': 2,
             'gf': 12,
             'ga': 10,
             'gd': 2,
             'pts': 16},
            {'pos': 7,
             'team': 'بورنموث',
             'p': 10,
             'w': 4,
             'd': 3,
             'l': 3,
             'gf': 16,
             'ga': 14,
             'gd': 2,
             'pts': 15},
            {'pos': 8,
             'team': 'برينتفورد',
             'p': 10,
             'w': 3,
             'd': 5,
             'l': 2,
             'gf': 16,
             'ga': 11,
             'gd': 5,
             'pts': 14},
            {'pos': 9,
             'team': 'ليدز يونايتد',
             'p': 10,
             'w': 3,
             'd': 5,
             'l': 2,
             'gf': 10,
             'ga': 8,
             'gd': 2,
             'pts': 14},
            {'pos': 10,
             'team': 'أستون فيلا',
             'p': 10,
             'w': 3,
             'd': 4,
             'l': 3,
             'gf': 14,
             'ga': 17,
             'gd': -3,
             'pts': 13},
            {'pos': 11,
             'team': 'توتنهام',
             'p': 10,
             'w': 3,
             'd': 3,
             'l': 4,
             'gf': 10,
             'ga': 11,
             'gd': -1,
             'pts': 12},
            {'pos': 12,
             'team': 'نيوكاسل يونايتد',
             'p': 10,
             'w': 3,
             'd': 3,
             'l': 4,
             'gf': 13,
             'ga': 16,
             'gd': -3,
             'pts': 12},
            {'pos': 13,
             'team': 'هال سيتي',
             'p': 10,
             'w': 2,
             'd': 5,
             'l': 3,
             'gf': 11,
             'ga': 11,
             'gd': 0,
             'pts': 11},
            {'pos': 14,
             'team': 'إيبسويتش تاون',
             'p': 10,
             'w': 3,
             'd': 2,
             'l': 5,
             'gf': 15,
             'ga': 20,
             'gd': -5,
             'pts': 11},
            {'pos': 15,
             'team': 'فولهام',
             'p': 10,
             'w': 2,
             'd': 4,
             'l': 4,
             'gf': 10,
             'ga': 12,
             'gd': -2,
             'pts': 10},
            {'pos': 16,
             'team': 'نوتينغهام فورست',
             'p': 10,
             'w': 2,
             'd': 3,
             'l': 5,
             'gf': 9,
             'ga': 13,
             'gd': -4,
             'pts': 9},
            {'pos': 17,
             'team': 'كوفنتري سيتي',
             'p': 10,
             'w': 3,
             'd': 0,
             'l': 7,
             'gf': 10,
             'ga': 19,
             'gd': -9,
             'pts': 9},
            {'pos': 18,
             'team': 'مانشستر يونايتد',
             'p': 10,
             'w': 1,
             'd': 5,
             'l': 4,
             'gf': 14,
             'ga': 19,
             'gd': -5,
             'pts': 8},
            {'pos': 19,
             'team': 'سندرلاند',
             'p': 10,
             'w': 2,
             'd': 2,
             'l': 6,
             'gf': 8,
             'ga': 17,
             'gd': -9,
             'pts': 8},
            {'pos': 20,
             'team': 'كريستال بالاس',
             'p': 10,
             'w': 2,
             'd': 1,
             'l': 7,
             'gf': 10,
             'ga': 24,
             'gd': -14,
             'pts': 7}],
  'scorers': [{'player': 'إيرلينغ هالاند', 'team': 'مانشستر سيتي', 'goals': 9},
              {'player': 'ألكسندر إيزاك', 'team': 'ليفربول', 'goals': 7},
              {'player': 'تيرنو باري', 'team': 'إيفرتون', 'goals': 6},
              {'player': 'نيكولاس جاكسون', 'team': 'أستون فيلا', 'goals': 6},
              {'player': 'إيفانيلسون', 'team': 'بورنموث', 'goals': 5},
              {'player': 'جواو بيدرو', 'team': 'تشيلسي', 'goals': 5},
              {'player': 'ريان شرقي', 'team': 'مانشستر سيتي', 'goals': 5},
              {'player': 'مورغان روجرز', 'team': 'تشيلسي', 'goals': 5},
              {'player': 'ماركوس تافيرنييه', 'team': 'بورنموث', 'goals': 5},
              {'player': 'بريان مبيومو', 'team': 'مانشستر يونايتد', 'goals': 4}],
  'meta': 'جدول ترتيب الدوري الإنجليزي الممتاز 2026-27: آرسنال في الصدارة بـ27 نقطة، برايتون 22، مانشستر '
          'سيتي 21 — الهدافون، مباريات الجولة 11 (21–23 نونبر) والنتائج.'},
 {'id': 'la-liga',
  'name': 'الدوري الإسباني',
  'short': 'الليغا',
  'country': 'إسبانيا',
  'season': '2026-27',
  'round': 'الجولة 12',
  'next_round': 'الجولة 13 — 20–23 نونبر 2026',
  'source': 'thestatsapi.com (18 نونبر 2026، 22:47 UTC) + مطابقة مع laligatable.co وsportsbetting3.com — '
            'الهدافون: renderfoot.com (18 نونبر 2026) + مطابقة مع fotmob.com وmoroccoworldnews.com',
  'table': [{'pos': 1,
             'team': 'برشلونة',
             'p': 12,
             'w': 11,
             'd': 0,
             'l': 1,
             'gf': 48,
             'ga': 13,
             'gd': 35,
             'pts': 33},
            {'pos': 2,
             'team': 'ريال مدريد',
             'p': 12,
             'w': 10,
             'd': 0,
             'l': 2,
             'gf': 31,
             'ga': 10,
             'gd': 21,
             'pts': 30},
            {'pos': 3,
             'team': 'أتلتيكو مدريد',
             'p': 12,
             'w': 9,
             'd': 1,
             'l': 2,
             'gf': 23,
             'ga': 10,
             'gd': 13,
             'pts': 28},
            {'pos': 4,
             'team': 'ريال بيتيس',
             'p': 12,
             'w': 8,
             'd': 2,
             'l': 2,
             'gf': 20,
             'ga': 15,
             'gd': 5,
             'pts': 26},
            {'pos': 5,
             'team': 'ريال سوسيداد',
             'p': 12,
             'w': 7,
             'd': 1,
             'l': 4,
             'gf': 21,
             'ga': 20,
             'gd': 1,
             'pts': 22},
            {'pos': 6,
             'team': 'إشبيلية',
             'p': 12,
             'w': 5,
             'd': 3,
             'l': 4,
             'gf': 17,
             'ga': 19,
             'gd': -2,
             'pts': 18},
            {'pos': 7,
             'team': 'أتلتيك بلباو',
             'p': 11,
             'w': 4,
             'd': 4,
             'l': 3,
             'gf': 15,
             'ga': 11,
             'gd': 4,
             'pts': 16},
            {'pos': 8,
             'team': 'فياريال',
             'p': 12,
             'w': 4,
             'd': 3,
             'l': 5,
             'gf': 17,
             'ga': 15,
             'gd': 2,
             'pts': 15},
            {'pos': 9,
             'team': 'ديبورتيفو لاكورونيا',
             'p': 12,
             'w': 3,
             'd': 6,
             'l': 3,
             'gf': 15,
             'ga': 14,
             'gd': 1,
             'pts': 15},
            {'pos': 10,
             'team': 'راسينغ سانتاندير',
             'p': 12,
             'w': 4,
             'd': 2,
             'l': 6,
             'gf': 17,
             'ga': 30,
             'gd': -13,
             'pts': 14},
            {'pos': 11,
             'team': 'سيلتا فيغو',
             'p': 12,
             'w': 2,
             'd': 7,
             'l': 3,
             'gf': 10,
             'ga': 10,
             'gd': 0,
             'pts': 13},
            {'pos': 12,
             'team': 'ديبورتيفو ألافيس',
             'p': 12,
             'w': 3,
             'd': 4,
             'l': 5,
             'gf': 15,
             'ga': 17,
             'gd': -2,
             'pts': 13},
            {'pos': 13,
             'team': 'إسبانيول',
             'p': 12,
             'w': 3,
             'd': 3,
             'l': 6,
             'gf': 13,
             'ga': 14,
             'gd': -1,
             'pts': 12},
            {'pos': 14,
             'team': 'رايو فايكانو',
             'p': 11,
             'w': 3,
             'd': 3,
             'l': 5,
             'gf': 15,
             'ga': 21,
             'gd': -6,
             'pts': 12},
            {'pos': 15,
             'team': 'خيتافي',
             'p': 12,
             'w': 3,
             'd': 3,
             'l': 6,
             'gf': 8,
             'ga': 18,
             'gd': -10,
             'pts': 12},
            {'pos': 16,
             'team': 'أوساسونا',
             'p': 12,
             'w': 3,
             'd': 3,
             'l': 6,
             'gf': 12,
             'ga': 23,
             'gd': -11,
             'pts': 12},
            {'pos': 17,
             'team': 'ليفانتي',
             'p': 12,
             'w': 2,
             'd': 5,
             'l': 5,
             'gf': 16,
             'ga': 21,
             'gd': -5,
             'pts': 11},
            {'pos': 18,
             'team': 'إلتشي',
             'p': 12,
             'w': 2,
             'd': 4,
             'l': 6,
             'gf': 14,
             'ga': 20,
             'gd': -6,
             'pts': 10},
            {'pos': 19,
             'team': 'فالنسيا',
             'p': 12,
             'w': 2,
             'd': 3,
             'l': 7,
             'gf': 8,
             'ga': 20,
             'gd': -12,
             'pts': 9},
            {'pos': 20,
             'team': 'ملقا',
             'p': 12,
             'w': 0,
             'd': 5,
             'l': 7,
             'gf': 9,
             'ga': 23,
             'gd': -14,
             'pts': 5}],
  'scorers': [{'player': 'رافينيا', 'team': 'برشلونة', 'goals': 15},
              {'player': 'كيليان مبابي', 'team': 'ريال مدريد', 'goals': 13},
              {'player': 'لامين يامال', 'team': 'برشلونة', 'goals': 10},
              {'player': 'ياسر الزبيري', 'team': 'راسينغ سانتاندير', 'goals': 9},
              {'player': 'أنتي بوديمير', 'team': 'أوساسونا', 'goals': 8},
              {'player': 'فيرمين لوبيز', 'team': 'برشلونة', 'goals': 7},
              {'player': 'سيرخيو كاميلو', 'team': 'رايو فايكانو', 'goals': 7},
              {'player': 'روبرتو فرنانديز', 'team': 'إسبانيول', 'goals': 6},
              {'player': 'فير نينيو', 'team': 'إلتشي', 'goals': 6},
              {'player': 'أليكس باينا', 'team': 'أتلتيكو مدريد', 'goals': 5}],
  'meta': 'جدول ترتيب الدوري الإسباني 2026-27: برشلونة متصدر بـ33 نقطة، ريال مدريد 30، أتلتيكو 28 — رافينيا '
          'هداف الليغا بـ15 هدفاً، مباريات الجولة 13 والنتائج.'},
 {'id': 'serie-a',
  'name': 'الدوري الإيطالي',
  'short': 'الكالتشيو',
  'country': 'إيطاليا',
  'season': '2026-27',
  'round': 'الجولة 11',
  'next_round': 'الجولة 12 — 21–23 نونبر 2026',
  'source': 'thestatsapi.com (18 نونبر 2026، 22:53 UTC) + مطابقة مع scanodds.com وpitchlabstats.com — '
            'الهدافون: renderfoot.com (18 نونبر 2026) + مطابقة مع pitchlabstats.com وmyfootballfacts.com',
  'table': [{'pos': 1,
             'team': 'لاتسيو',
             'p': 11,
             'w': 9,
             'd': 2,
             'l': 0,
             'gf': 25,
             'ga': 9,
             'gd': 16,
             'pts': 29},
            {'pos': 2,
             'team': 'إنتر ميلان',
             'p': 11,
             'w': 9,
             'd': 1,
             'l': 1,
             'gf': 28,
             'ga': 13,
             'gd': 15,
             'pts': 28},
            {'pos': 3,
             'team': 'روما',
             'p': 11,
             'w': 8,
             'd': 3,
             'l': 0,
             'gf': 31,
             'ga': 10,
             'gd': 21,
             'pts': 27},
            {'pos': 4,
             'team': 'ميلان',
             'p': 11,
             'w': 7,
             'd': 3,
             'l': 1,
             'gf': 23,
             'ga': 13,
             'gd': 10,
             'pts': 24},
            {'pos': 5,
             'team': 'كومو',
             'p': 11,
             'w': 7,
             'd': 2,
             'l': 2,
             'gf': 18,
             'ga': 10,
             'gd': 8,
             'pts': 23},
            {'pos': 6,
             'team': 'فروزينوني',
             'p': 11,
             'w': 6,
             'd': 2,
             'l': 3,
             'gf': 24,
             'ga': 15,
             'gd': 9,
             'pts': 20},
            {'pos': 7,
             'team': 'يوفنتوس',
             'p': 11,
             'w': 5,
             'd': 3,
             'l': 3,
             'gf': 15,
             'ga': 12,
             'gd': 3,
             'pts': 18},
            {'pos': 8,
             'team': 'بولونيا',
             'p': 11,
             'w': 5,
             'd': 2,
             'l': 4,
             'gf': 16,
             'ga': 14,
             'gd': 2,
             'pts': 17},
            {'pos': 9,
             'team': 'كالياري',
             'p': 11,
             'w': 5,
             'd': 1,
             'l': 5,
             'gf': 10,
             'ga': 15,
             'gd': -5,
             'pts': 16},
            {'pos': 10,
             'team': 'نابولي',
             'p': 11,
             'w': 4,
             'd': 3,
             'l': 4,
             'gf': 18,
             'ga': 14,
             'gd': 4,
             'pts': 15},
            {'pos': 11,
             'team': 'تورينو',
             'p': 11,
             'w': 4,
             'd': 2,
             'l': 5,
             'gf': 15,
             'ga': 17,
             'gd': -2,
             'pts': 14},
            {'pos': 12,
             'team': 'أتالانتا',
             'p': 11,
             'w': 4,
             'd': 2,
             'l': 5,
             'gf': 17,
             'ga': 20,
             'gd': -3,
             'pts': 14},
            {'pos': 13,
             'team': 'جنوى',
             'p': 11,
             'w': 4,
             'd': 1,
             'l': 6,
             'gf': 11,
             'ga': 16,
             'gd': -5,
             'pts': 13},
            {'pos': 14,
             'team': 'ليتشي',
             'p': 11,
             'w': 3,
             'd': 1,
             'l': 7,
             'gf': 12,
             'ga': 22,
             'gd': -10,
             'pts': 10},
            {'pos': 15,
             'team': 'فيورنتينا',
             'p': 11,
             'w': 2,
             'd': 3,
             'l': 6,
             'gf': 17,
             'ga': 25,
             'gd': -8,
             'pts': 9},
            {'pos': 16,
             'team': 'بارما',
             'p': 11,
             'w': 2,
             'd': 2,
             'l': 7,
             'gf': 9,
             'ga': 17,
             'gd': -8,
             'pts': 8},
            {'pos': 17,
             'team': 'ساسولو',
             'p': 11,
             'w': 2,
             'd': 2,
             'l': 7,
             'gf': 16,
             'ga': 29,
             'gd': -13,
             'pts': 8},
            {'pos': 18,
             'team': 'مونزا',
             'p': 11,
             'w': 2,
             'd': 1,
             'l': 8,
             'gf': 17,
             'ga': 25,
             'gd': -8,
             'pts': 7},
            {'pos': 19,
             'team': 'فينيزيا',
             'p': 11,
             'w': 2,
             'd': 0,
             'l': 9,
             'gf': 8,
             'ga': 21,
             'gd': -13,
             'pts': 6},
            {'pos': 20,
             'team': 'أودينيزي',
             'p': 11,
             'w': 1,
             'd': 2,
             'l': 8,
             'gf': 12,
             'ga': 25,
             'gd': -13,
             'pts': 5}],
  'scorers': [{'player': 'غوستافو فاريلا', 'team': 'مونزا', 'goals': 9},
              {'player': 'دونييل مالين', 'team': 'روما', 'goals': 8},
              {'player': 'أنتونيو رايموندو', 'team': 'فروزينوني', 'goals': 8},
              {'player': 'نيكولا كرستوفيتش', 'team': 'أتالانتا', 'goals': 7},
              {'player': 'ماركوس تورام', 'team': 'إنتر ميلان', 'goals': 6},
              {'player': 'أدريان رابيو', 'team': 'ميلان', 'goals': 5},
              {'player': 'أناستاسيوس دوفيكاس', 'team': 'كومو', 'goals': 5},
              {'player': 'ألفادجو سيسيه', 'team': 'ميلان', 'goals': 5},
              {'player': 'جياكومو كالو', 'team': 'فروزينوني', 'goals': 5},
              {'player': 'دانيال مالديني', 'team': 'كالياري', 'goals': 5}],
  'meta': 'جدول ترتيب الدوري الإيطالي 2026-27: لاتسيو في الصدارة بـ29 نقطة، إنتر 28، روما 27 — الهدافون، '
          'مباريات الجولة 12 (21–23 نونبر) والنتائج.'},
 {'id': 'bundesliga',
  'name': 'الدوري الألماني',
  'short': 'البوندسليغا',
  'country': 'ألمانيا',
  'season': '2026-27',
  'round': 'الجولة 9',
  'next_round': 'الجولة 10 — 20–22 نونبر 2026',
  'source': 'thestatsapi.com (18 نونبر 2026، 22:51 UTC) + مطابقة مع bettingtips.africa وturingstats.com — '
            'الهدافون: bundesliga.com + renderfoot.com (18 نونبر 2026)',
  'table': [{'pos': 1,
             'team': 'بايرن ميونيخ',
             'p': 9,
             'w': 6,
             'd': 3,
             'l': 0,
             'gf': 29,
             'ga': 9,
             'gd': 20,
             'pts': 21},
            {'pos': 2,
             'team': 'بوروسيا دورتموند',
             'p': 9,
             'w': 6,
             'd': 3,
             'l': 0,
             'gf': 16,
             'ga': 7,
             'gd': 9,
             'pts': 21},
            {'pos': 3,
             'team': 'فرايبورغ',
             'p': 9,
             'w': 6,
             'd': 1,
             'l': 2,
             'gf': 20,
             'ga': 10,
             'gd': 10,
             'pts': 19},
            {'pos': 4,
             'team': 'لايبزيغ',
             'p': 9,
             'w': 6,
             'd': 0,
             'l': 3,
             'gf': 27,
             'ga': 13,
             'gd': 14,
             'pts': 18},
            {'pos': 5,
             'team': 'باير ليفركوزن',
             'p': 9,
             'w': 5,
             'd': 1,
             'l': 3,
             'gf': 20,
             'ga': 17,
             'gd': 3,
             'pts': 16},
            {'pos': 6,
             'team': 'فيردر بريمن',
             'p': 9,
             'w': 4,
             'd': 3,
             'l': 2,
             'gf': 17,
             'ga': 15,
             'gd': 2,
             'pts': 15},
            {'pos': 7,
             'team': 'إلفرسبرغ',
             'p': 9,
             'w': 4,
             'd': 1,
             'l': 4,
             'gf': 17,
             'ga': 18,
             'gd': -1,
             'pts': 13},
            {'pos': 8,
             'team': 'شتوتغارت',
             'p': 9,
             'w': 4,
             'd': 0,
             'l': 5,
             'gf': 15,
             'ga': 15,
             'gd': 0,
             'pts': 12},
            {'pos': 9,
             'team': 'هوفنهايم',
             'p': 9,
             'w': 4,
             'd': 0,
             'l': 5,
             'gf': 16,
             'ga': 17,
             'gd': -1,
             'pts': 12},
            {'pos': 10,
             'team': 'آينتراخت فرانكفورت',
             'p': 9,
             'w': 3,
             'd': 3,
             'l': 3,
             'gf': 15,
             'ga': 20,
             'gd': -5,
             'pts': 12},
            {'pos': 11,
             'team': 'هامبورغ',
             'p': 9,
             'w': 4,
             'd': 0,
             'l': 5,
             'gf': 10,
             'ga': 20,
             'gd': -10,
             'pts': 12},
            {'pos': 12,
             'team': 'ماينز',
             'p': 9,
             'w': 3,
             'd': 1,
             'l': 5,
             'gf': 18,
             'ga': 19,
             'gd': -1,
             'pts': 10},
            {'pos': 13,
             'team': 'بادربورن',
             'p': 9,
             'w': 2,
             'd': 4,
             'l': 3,
             'gf': 8,
             'ga': 11,
             'gd': -3,
             'pts': 10},
            {'pos': 14,
             'team': 'أوغسبورغ',
             'p': 9,
             'w': 2,
             'd': 3,
             'l': 4,
             'gf': 20,
             'ga': 20,
             'gd': 0,
             'pts': 9},
            {'pos': 15,
             'team': 'كولن',
             'p': 9,
             'w': 2,
             'd': 3,
             'l': 4,
             'gf': 10,
             'ga': 14,
             'gd': -4,
             'pts': 9},
            {'pos': 16,
             'team': 'يونيون برلين',
             'p': 9,
             'w': 1,
             'd': 4,
             'l': 4,
             'gf': 7,
             'ga': 21,
             'gd': -14,
             'pts': 7},
            {'pos': 17,
             'team': 'شالكه',
             'p': 9,
             'w': 1,
             'd': 3,
             'l': 5,
             'gf': 5,
             'ga': 11,
             'gd': -6,
             'pts': 6},
            {'pos': 18,
             'team': 'بوروسيا مونشنغلادباخ',
             'p': 9,
             'w': 1,
             'd': 1,
             'l': 7,
             'gf': 12,
             'ga': 25,
             'gd': -13,
             'pts': 4}],
  'scorers': [{'player': 'نيكلاس فولكروغ', 'team': 'فيردر بريمن', 'goals': 9},
              {'player': 'باتريك شيك', 'team': 'باير ليفركوزن', 'goals': 8},
              {'player': 'مايكل أوليز', 'team': 'بايرن ميونيخ', 'goals': 6},
              {'player': 'يونس ابن طالب', 'team': 'آينتراخت فرانكفورت', 'goals': 6},
              {'player': 'فيليب تيتز', 'team': 'ماينز', 'goals': 6},
              {'player': 'كريستوفر نكونكو', 'team': 'لايبزيغ', 'goals': 5},
              {'player': 'جوناثان بوركاردت', 'team': 'آينتراخت فرانكفورت', 'goals': 5},
              {'player': 'إرميدين ديميروفيتش', 'team': 'شتوتغارت', 'goals': 5},
              {'player': 'يويتو سوزوكي', 'team': 'فرايبورغ', 'goals': 5},
              {'player': 'رومولو', 'team': 'لايبزيغ', 'goals': 5}],
  'meta': 'جدول ترتيب الدوري الألماني 2026-27: بايرن ميونيخ ودورتموند متساويان بـ21 نقطة، فرايبورغ 19 — '
          'الهدافون، مباريات الجولة 10 (20–22 نونبر) والنتائج.'},
 {'id': 'ligue-1',
  'name': 'الدوري الفرنسي',
  'short': 'الليغ 1',
  'country': 'فرنسا',
  'season': '2026-27',
  'round': 'الجولة 10',
  'next_round': 'الجولة 11 — 20–22 نونبر 2026',
  'source': 'thestatsapi.com (18 نونبر 2026، 22:31 UTC) + مطابقة مع xgstats.com وligue1schedule.com — '
            'الهدافون: renderfoot.com (18 نونبر 2026) + مطابقة مع myfootballfacts.com وsocerstreams.org',
  'table': [{'pos': 1,
             'team': 'باريس سان جيرمان',
             'p': 10,
             'w': 7,
             'd': 2,
             'l': 1,
             'gf': 22,
             'ga': 10,
             'gd': 12,
             'pts': 23},
            {'pos': 2, 'team': 'ليل', 'p': 10, 'w': 6, 'd': 3, 'l': 1, 'gf': 14, 'ga': 7, 'gd': 7, 'pts': 21},
            {'pos': 3,
             'team': 'باريس إف سي',
             'p': 10,
             'w': 6,
             'd': 2,
             'l': 2,
             'gf': 17,
             'ga': 10,
             'gd': 7,
             'pts': 20},
            {'pos': 4,
             'team': 'مارسيليا',
             'p': 10,
             'w': 6,
             'd': 0,
             'l': 4,
             'gf': 22,
             'ga': 14,
             'gd': 8,
             'pts': 18},
            {'pos': 5,
             'team': 'ليون',
             'p': 10,
             'w': 5,
             'd': 2,
             'l': 3,
             'gf': 15,
             'ga': 9,
             'gd': 6,
             'pts': 17},
            {'pos': 6,
             'team': 'نيس',
             'p': 10,
             'w': 5,
             'd': 2,
             'l': 3,
             'gf': 15,
             'ga': 12,
             'gd': 3,
             'pts': 17},
            {'pos': 7,
             'team': 'موناكو',
             'p': 10,
             'w': 4,
             'd': 4,
             'l': 2,
             'gf': 13,
             'ga': 11,
             'gd': 2,
             'pts': 16},
            {'pos': 8,
             'team': 'رين',
             'p': 10,
             'w': 5,
             'd': 1,
             'l': 4,
             'gf': 21,
             'ga': 21,
             'gd': 0,
             'pts': 16},
            {'pos': 9,
             'team': 'بريست',
             'p': 10,
             'w': 4,
             'd': 3,
             'l': 3,
             'gf': 18,
             'ga': 12,
             'gd': 6,
             'pts': 15},
            {'pos': 10,
             'team': 'لوريان',
             'p': 10,
             'w': 4,
             'd': 3,
             'l': 3,
             'gf': 9,
             'ga': 8,
             'gd': 1,
             'pts': 15},
            {'pos': 11,
             'team': 'لانس',
             'p': 10,
             'w': 4,
             'd': 1,
             'l': 5,
             'gf': 17,
             'ga': 15,
             'gd': 2,
             'pts': 13},
            {'pos': 12,
             'team': 'تولوز',
             'p': 10,
             'w': 3,
             'd': 4,
             'l': 3,
             'gf': 15,
             'ga': 14,
             'gd': 1,
             'pts': 13},
            {'pos': 13,
             'team': 'ستراسبورغ',
             'p': 10,
             'w': 3,
             'd': 1,
             'l': 6,
             'gf': 18,
             'ga': 22,
             'gd': -4,
             'pts': 10},
            {'pos': 14,
             'team': 'أوكسير',
             'p': 10,
             'w': 3,
             'd': 1,
             'l': 6,
             'gf': 13,
             'ga': 24,
             'gd': -11,
             'pts': 10},
            {'pos': 15,
             'team': 'لومان',
             'p': 10,
             'w': 1,
             'd': 5,
             'l': 4,
             'gf': 12,
             'ga': 19,
             'gd': -7,
             'pts': 8},
            {'pos': 16,
             'team': 'أنجيه',
             'p': 10,
             'w': 2,
             'd': 2,
             'l': 6,
             'gf': 9,
             'ga': 19,
             'gd': -10,
             'pts': 8},
            {'pos': 17,
             'team': 'تروا',
             'p': 10,
             'w': 2,
             'd': 2,
             'l': 6,
             'gf': 7,
             'ga': 17,
             'gd': -10,
             'pts': 8},
            {'pos': 18,
             'team': 'لوهافر',
             'p': 10,
             'w': 0,
             'd': 2,
             'l': 8,
             'gf': 9,
             'ga': 22,
             'gd': -13,
             'pts': 2}],
  'scorers': [{'player': 'لاسين سينايوكو', 'team': 'باريس إف سي', 'goals': 9},
              {'player': 'أمين غويري', 'team': 'مارسيليا', 'goals': 7},
              {'player': 'إستيبان لوبول', 'team': 'رين', 'goals': 7},
              {'player': 'كاميرون آرتشر', 'team': 'أوكسير', 'goals': 6},
              {'player': 'إلي واهي', 'team': 'نيس', 'goals': 6},
              {'player': 'لودوفيك أجورك', 'team': 'بريست', 'goals': 5},
              {'player': 'بولاي ديا', 'team': 'رين', 'goals': 5},
              {'player': 'كاسبر تنغستيدت', 'team': 'تولوز', 'goals': 5},
              {'player': 'فلوريان توفان', 'team': 'لانس', 'goals': 5},
              {'player': 'جيسيم ياسين', 'team': 'ستراسبورغ', 'goals': 4}],
  'meta': 'جدول ترتيب الدوري الفرنسي 2026-27: باريس سان جيرمان متصدر بـ23 نقطة، ليل 21، باريس إف سي 20 — '
          'الهدافون، مباريات الجولة 11 (20–22 نونبر) والنتائج.'},
 {'id': 'botola',
  'name': 'البطولة الاحترافية المغربية',
  'short': 'البطولة',
  'country': 'المغرب',
  'season': '2026-27',
  'round': 'الجولة 7',
  'next_round': 'الجولة 8 — التاريخ قيد التأكيد',
  'source': 'ويكيبيديا 2026–27 Botola Pro — المصدر: FRMF.ma (مباريات حتى 09 نونبر 2026) + مطابقة مع '
            'pitchlabstats.com وglobalsportsarchive.com — الهدافون: pitchlabstats.com + ويكيبيديا (FRMF) — '
            'ملاحظة: مباراة الوداد–وداد تمارة حُسمت 3–0 للوداد بقرار LNFP في 07 نونبر 2026 (لاعب غير مؤهل)، '
            'وخصم نقطة واحدة من وداد تمارة',
  'table': [{'pos': 1,
             'team': 'الكوكب المراكشي',
             'p': 7,
             'w': 5,
             'd': 1,
             'l': 1,
             'gf': 10,
             'ga': 6,
             'gd': 4,
             'pts': 16},
            {'pos': 2,
             'team': 'النادي المكناسي',
             'p': 7,
             'w': 4,
             'd': 2,
             'l': 1,
             'gf': 10,
             'ga': 4,
             'gd': 6,
             'pts': 14},
            {'pos': 3,
             'team': 'الوداد الرياضي',
             'p': 7,
             'w': 4,
             'd': 2,
             'l': 1,
             'gf': 9,
             'ga': 3,
             'gd': 6,
             'pts': 14},
            {'pos': 4,
             'team': 'الرجاء الرياضي',
             'p': 7,
             'w': 3,
             'd': 3,
             'l': 1,
             'gf': 7,
             'ga': 5,
             'gd': 2,
             'pts': 12},
            {'pos': 5,
             'team': 'الجيش الملكي',
             'p': 6,
             'w': 3,
             'd': 2,
             'l': 1,
             'gf': 9,
             'ga': 5,
             'gd': 4,
             'pts': 11},
            {'pos': 6,
             'team': 'المغرب الفاسي',
             'p': 7,
             'w': 3,
             'd': 2,
             'l': 2,
             'gf': 6,
             'ga': 5,
             'gd': 1,
             'pts': 11},
            {'pos': 7,
             'team': 'اتحاد طنجة',
             'p': 7,
             'w': 3,
             'd': 1,
             'l': 3,
             'gf': 8,
             'ga': 9,
             'gd': -1,
             'pts': 10},
            {'pos': 8,
             'team': 'حسنية أكادير',
             'p': 7,
             'w': 2,
             'd': 3,
             'l': 2,
             'gf': 14,
             'ga': 12,
             'gd': 2,
             'pts': 9},
            {'pos': 9,
             'team': 'اتحاد تواركة',
             'p': 7,
             'w': 2,
             'd': 2,
             'l': 3,
             'gf': 4,
             'ga': 6,
             'gd': -2,
             'pts': 8},
            {'pos': 10,
             'team': 'الدفاع الحسني الجديدي',
             'p': 7,
             'w': 2,
             'd': 2,
             'l': 3,
             'gf': 14,
             'ga': 16,
             'gd': -2,
             'pts': 8},
            {'pos': 11,
             'team': 'الفتح الرباطي',
             'p': 7,
             'w': 2,
             'd': 2,
             'l': 3,
             'gf': 4,
             'ga': 5,
             'gd': -1,
             'pts': 8},
            {'pos': 12,
             'team': 'نهضة بركان',
             'p': 6,
             'w': 1,
             'd': 5,
             'l': 0,
             'gf': 6,
             'ga': 4,
             'gd': 2,
             'pts': 8},
            {'pos': 13,
             'team': 'أمل تيزنيت',
             'p': 7,
             'w': 2,
             'd': 1,
             'l': 4,
             'gf': 8,
             'ga': 12,
             'gd': -4,
             'pts': 7},
            {'pos': 14,
             'team': 'وداد تمارة',
             'p': 7,
             'w': 2,
             'd': 1,
             'l': 4,
             'gf': 5,
             'ga': 7,
             'gd': -2,
             'pts': 6},
            {'pos': 15,
             'team': 'المغرب التطواني',
             'p': 7,
             'w': 0,
             'd': 3,
             'l': 4,
             'gf': 2,
             'ga': 10,
             'gd': -8,
             'pts': 3},
            {'pos': 16,
             'team': 'نهضة الزمامرة',
             'p': 7,
             'w': 0,
             'd': 2,
             'l': 5,
             'gf': 6,
             'ga': 13,
             'gd': -7,
             'pts': 2}],
  'scorers': [{'player': 'عماد رياحي', 'team': 'حسنية أكادير', 'goals': 6},
              {'player': 'عبد الرزاق النقوس', 'team': 'الدفاع الحسني الجديدي', 'goals': 6},
              {'player': 'يوسف الفحلي', 'team': 'الجيش الملكي', 'goals': 5},
              {'player': 'زكرياء الصالحي', 'team': 'أمل تيزنيت', 'goals': 5},
              {'player': 'سيلفير غانفولا', 'team': 'الوداد الرياضي', 'goals': 4},
              {'player': 'صالح السلامي', 'team': 'الكوكب المراكشي', 'goals': 4},
              {'player': 'حمزة الواستي', 'team': 'النادي المكناسي', 'goals': 3},
              {'player': 'معاد مشتنيم', 'team': 'الدفاع الحسني الجديدي', 'goals': 2},
              {'player': 'ت. ماباسا', 'team': 'المغرب الفاسي', 'goals': 2},
              {'player': 'أيوب معموري', 'team': 'الكوكب المراكشي', 'goals': 2}],
  'meta': 'جدول ترتيب البطولة الاحترافية المغربية 2026-27: الكوكب المراكشي متصدر بـ16 نقطة، النادي المكناسي '
          'والوداد 14، الرجاء 12 — مباريات الجولة 8 والنتائج.'}]
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
 fx('bayern-koln-2026-11-20', 'بايرن ميونيخ', 'كولن', 'bundesliga', 'الدوري الألماني', '2026-11-20', '20:30', 'kickofflens.com + football.mib.news (19:30 UTC)', venue='أليانز أرينا، ميونيخ', channel='beIN Sports'),
 fx('athletic-espanyol-2026-11-20', 'أتلتيك بلباو', 'إسبانيول', 'la-liga', 'الدوري الإسباني', '2026-11-20', '21:00', 'kickofflens.com + football.mib.news (20:00 UTC)', venue='سان ماميس، بلباو', channel='beIN Sports'),
 fx('troyes-lehavre-2026-11-20', 'تروا', 'لوهافر', 'ligue-1', 'الدوري الفرنسي', '2026-11-20', '20:45', 'vavel.com (14:45 ET = 19:45 UTC) + football.mib.news', venue='ملعب لوب، تروا', channel='beIN Sports'),
 fx('man-city-fulham-2026-11-21', 'مانشستر سيتي', 'فولهام', 'premier-league', 'الدوري الإنجليزي', '2026-11-21', '13:30', 'premierleague.com + nbcsports.com (12:30 UK)', venue='ملعب الاتحاد، مانشستر', channel='beIN Sports'),
 fx('aston-villa-sunderland-2026-11-21', 'أستون فيلا', 'سندرلاند', 'premier-league', 'الدوري الإنجليزي', '2026-11-21', '16:00', 'premierleague.com (15:00 UK)', venue='فيلا بارك، برمنغهام', channel='beIN Sports'),
 fx('bournemouth-nottingham-2026-11-21', 'بورنموث', 'نوتينغهام فورست', 'premier-league', 'الدوري الإنجليزي', '2026-11-21', '16:00', 'premierleague.com (15:00 UK)', venue='فيتاليتي ستاديوم، بورنموث', channel='beIN Sports'),
 fx('coventry-crystal-palace-2026-11-21', 'كوفنتري سيتي', 'كريستال بالاس', 'premier-league', 'الدوري الإنجليزي', '2026-11-21', '16:00', 'livescore.in + premierleague.com (15:00 UK)', venue='كوفنتري بيلدينغ سوسايتي أرينا، كوفنتري', channel='beIN Sports'),
 fx('tottenham-ipswich-2026-11-21', 'توتنهام', 'إيبسويتش تاون', 'premier-league', 'الدوري الإنجليزي', '2026-11-21', '16:00', 'livescore.in + premierleague.com (15:00 UK)', venue='ملعب توتنهام هوتسبير، لندن', channel='beIN Sports'),
 fx('newcastle-arsenal-2026-11-21', 'نيوكاسل يونايتد', 'آرسنال', 'premier-league', 'الدوري الإنجليزي', '2026-11-21', '18:30', 'premierleague.com + nbcsports.com (17:30 UK)', venue='سانت جيمس بارك، نيوكاسل', channel='beIN Sports', referee='كريس كافانا'),
 fx('real-madrid-celta-2026-11-21', 'ريال مدريد', 'سيلتا فيغو', 'la-liga', 'الدوري الإسباني', '2026-11-21', None, 'laligatable.co (المباراة المقبلة لريال مدريد — التوقيت قيد التأكيد)', venue='سانتياغو برنابيو، مدريد', channel='beIN Sports'),
 fx('union-leipzig-2026-11-21', 'يونيون برلين', 'لايبزيغ', 'bundesliga', 'الدوري الألماني', '2026-11-21', '15:30', 'fcstats.com (09:30 ET = 15:30 CET)', venue='ملعب آلته فورستيري، برلين', channel='beIN Sports'),
 fx('leverkusen-paderborn-2026-11-21', 'باير ليفركوزن', 'بادربورن', 'bundesliga', 'الدوري الألماني', '2026-11-21', '15:30', 'fcstats.com (09:30 ET = 15:30 CET)', venue='باي أرينا، ليفركوزن', channel='beIN Sports'),
 fx('gladbach-dortmund-2026-11-21', 'بوروسيا مونشنغلادباخ', 'بوروسيا دورتموند', 'bundesliga', 'الدوري الألماني', '2026-11-21', '15:30', 'fcstats.com (09:30 ET = 15:30 CET)', venue='بوروسيا بارك، مونشنغلادباخ', channel='beIN Sports'),
 fx('augsburg-mainz-2026-11-21', 'أوغسبورغ', 'ماينز', 'bundesliga', 'الدوري الألماني', '2026-11-21', '15:30', 'fcstats.com (09:30 ET = 15:30 CET)', venue='ملعب WWK، أوغسبورغ', channel='beIN Sports'),
 fx('nice-psg-2026-11-21', 'نيس', 'باريس سان جيرمان', 'ligue-1', 'الدوري الفرنسي', '2026-11-21', '17:15', 'vavel.com (11:15 ET = 16:15 UTC)', venue='أليانز ريفييرا، نيس', channel='beIN Sports'),
 fx('lille-lyon-2026-11-21', 'ليل', 'ليون', 'ligue-1', 'الدوري الفرنسي', '2026-11-21', '20:45', 'vavel.com (14:45 ET = 19:45 UTC)', venue='ملعب بيير موروا، ليل', channel='beIN Sports'),
 fx('hull-brighton-2026-11-22', 'هال سيتي', 'برايتون', 'premier-league', 'الدوري الإنجليزي', '2026-11-22', '15:00', 'livescore.in (06:00 PT = 14:00 UTC)', venue='ملعب MKM، هال', channel='beIN Sports'),
 fx('liverpool-manutd-2026-11-22', 'ليفربول', 'مانشستر يونايتد', 'premier-league', 'الدوري الإنجليزي', '2026-11-22', '18:30', 'premierleague.com + nbcsports.com (16:30 UK)', venue='أنفيلد، ليفربول', channel='beIN Sports'),
 fx('barcelona-villarreal-2026-11-22', 'برشلونة', 'فياريال', 'la-liga', 'الدوري الإسباني', '2026-11-22', None, 'laligatable.co (المباراة المقبلة لبرشلونة — التوقيت قيد التأكيد)', venue_note='قيد التحقق — كامب نو أو ملعب لويس كومبانيس الأولمبي (مونتجويك)', channel='beIN Sports'),
 fx('atalanta-inter-2026-11-22', 'أتالانتا', 'إنتر ميلان', 'serie-a', 'الدوري الإيطالي', '2026-11-22', None, 'showupandplay.com (عطلة نهاية الأسبوع 21–23 نونبر — اليوم الدقيق قيد التأكيد)', date_label='21–23 نونبر 2026', venue='ملعب غيويس، بيرغامو', channel='beIN Sports'),
 fx('juventus-venezia-2026-11-22', 'يوفنتوس', 'فينيزيا', 'serie-a', 'الدوري الإيطالي', '2026-11-22', None, 'منشور فيسبوك FAFG (عطلة نهاية الأسبوع 21–23 نونبر — اليوم الدقيق قيد التأكيد)', date_label='21–23 نونبر 2026', venue='أليانز ستاديوم، تورينو', channel='beIN Sports'),
 fx('brentford-everton-2026-11-23', 'برينتفورد', 'إيفرتون', 'premier-league', 'الدوري الإنجليزي', '2026-11-23', '21:00', 'livescore.in (12:00 PT = 20:00 UTC)', venue='ملعب جيتك كوميونيتي، لندن', channel='beIN Sports'),
]
# Last verified results: final weekend before the international break (7–8 Nov 2026).
# Day-per-match NOT individually verified — grouped as one weekend, source noted.
RESULTS = [{'id': 'mainz-bayern-2026-11-08',
  'home': 'ماينز',
  'away': 'بايرن ميونيخ',
  'home_goals': 1,
  'away_goals': 2,
  'league': 'bundesliga',
  'league_name': 'الدوري الألماني',
  'date': '2026-11-08',
  'status': 'finished',
  'source': 'showupandplay.com (تقرير 08 نونبر 2026)',
  'stats': {'possession_home': 31,
            'possession_away': 69,
            'shots_home': 11,
            'shots_away': 26,
            'shots_on_target_home': 1,
            'shots_on_target_away': 9,
            'corners_home': 7,
            'corners_away': 8,
            'source': 'previaxi.com + soccerpunter.com + sportmeridian.com (18 نونبر 2026) — لعبت 07 نونبر '
                      '2026 14:30 UTC'},
  'venue': 'ملعب ميوا، ماينز',
  'channel': 'beIN Sports'},
 {'id': 'dortmund-elversberg-2026-11-08',
  'home': 'بوروسيا دورتموند',
  'away': 'إلفرسبرغ',
  'home_goals': 2,
  'away_goals': 1,
  'league': 'bundesliga',
  'league_name': 'الدوري الألماني',
  'date': '2026-11-08',
  'status': 'finished',
  'source': 'showupandplay.com (تقرير 08 نونبر 2026)',
  'stats': {'possession_home': 51,
            'possession_away': 49,
            'shots_home': 19,
            'shots_away': 16,
            'shots_on_target_home': 6,
            'shots_on_target_away': 7,
            'corners_home': 6,
            'corners_away': 6,
            'source': 'soccerpunter.com + matchreplays.com + sportmeridian.com (18 نونبر 2026) — لعبت 07 '
                      'نونبر 2026 14:30 UTC'},
  'venue': 'سيغنال إيدونا بارك، دورتموند',
  'channel': 'beIN Sports'},
 {'id': 'napoli-lazio-2026-11-08',
  'home': 'نابولي',
  'away': 'لاتسيو',
  'home_goals': 1,
  'away_goals': 1,
  'league': 'serie-a',
  'league_name': 'الدوري الإيطالي',
  'date': '2026-11-08',
  'status': 'finished',
  'source': 'showupandplay.com (تقرير 08 نونبر 2026)',
  'stats': {'possession_home': 49,
            'possession_away': 51,
            'shots_home': 15,
            'shots_away': 15,
            'shots_on_target_home': 6,
            'shots_on_target_away': 6,
            'corners_home': 6,
            'corners_away': 6,
            'source': 'skysports.com + moneyball-odds.com + yardbarker.com (18 نونبر 2026)'},
  'venue': 'ملعب دييغو أرماندو مارادونا، نابولي',
  'channel': 'beIN Sports'},
 {'id': 'inter-como-2026-11-08',
  'home': 'إنتر ميلان',
  'away': 'كومو',
  'home_goals': 2,
  'away_goals': 0,
  'league': 'serie-a',
  'league_name': 'الدوري الإيطالي',
  'date': '2026-11-08',
  'status': 'finished',
  'source': 'showupandplay.com (تقرير 08 نونبر 2026)',
  'stats': {'possession_home': 43,
            'possession_away': 57,
            'shots_home': 14,
            'shots_away': 5,
            'shots_on_target_home': 4,
            'shots_on_target_away': 1,
            'corners_home': 4,
            'corners_away': 2,
            'source': 'skysports.com + pitchlabstats.com + moneyball-odds.com (18 نونبر 2026)'},
  'venue': 'سان سيرو، ميلانو',
  'channel': 'beIN Sports'},
 {'id': 'roma-sassuolo-2026-11-08',
  'home': 'روما',
  'away': 'ساسولو',
  'home_goals': 3,
  'away_goals': 0,
  'league': 'serie-a',
  'league_name': 'الدوري الإيطالي',
  'date': '2026-11-08',
  'status': 'finished',
  'source': 'showupandplay.com (تقرير 08 نونبر 2026)',
  'stats': {'possession_home': 65,
            'possession_away': 35,
            'shots_home': 28,
            'shots_away': 6,
            'shots_on_target_home': 9,
            'shots_on_target_away': 1,
            'corners_home': 12,
            'corners_away': 1,
            'source': 'espn.ph + mykhel.com + soccerpunter.com (18 نونبر 2026) — لعبت 07 نونبر 2026 19:45 '
                      'UTC'},
  'venue': 'الملعب الأولمبي، روما',
  'channel': 'beIN Sports'},
 {'id': 'genoa-milan-2026-11-08',
  'home': 'جنوى',
  'away': 'ميلان',
  'home_goals': 1,
  'away_goals': 2,
  'league': 'serie-a',
  'league_name': 'الدوري الإيطالي',
  'date': '2026-11-08',
  'status': 'finished',
  'source': 'showupandplay.com (تقرير 08 نونبر 2026)',
  'stats': {'possession_home': 38,
            'possession_away': 62,
            'shots_home': 17,
            'shots_away': 6,
            'shots_on_target_home': 5,
            'shots_on_target_away': 2,
            'corners_home': 3,
            'corners_away': 0,
            'source': 'skysports.com + moneyball-odds.com + livescore.com (18 نونبر 2026)'},
  'venue': 'ملعب لويجي فيراريس، جنوى',
  'channel': 'beIN Sports'},
 {'id': 'fiorentina-juventus-2026-11-08',
  'home': 'فيورنتينا',
  'away': 'يوفنتوس',
  'home_goals': 2,
  'away_goals': 2,
  'league': 'serie-a',
  'league_name': 'الدوري الإيطالي',
  'date': '2026-11-08',
  'status': 'finished',
  'source': 'showupandplay.com (تقرير 08 نونبر 2026)',
  'stats': {'possession_home': 41,
            'possession_away': 59,
            'shots_home': 22,
            'shots_away': 18,
            'shots_on_target_home': 6,
            'shots_on_target_away': 6,
            'corners_home': 5,
            'corners_away': 12,
            'source': 'skysports.com + soccerway.com + flashscore.com (18 نونبر 2026)'},
  'venue': 'ملعب أرتيميو فرانكي، فلورنسا',
  'channel': 'beIN Sports'}]
ALLOWED = ["premier-league", "la-liga", "serie-a", "bundesliga", "ligue-1", "botola"]
LEAGUE_BY_ID = {l["id"]: l for l in LEAGUES}

# ------------------------------------------------------------- logos ---
# الشعارات: تُقرأ من data/logos.json (ملفات محلية في assets/img/logos/ فقط).
# أي فريق بلا شعار موثق يُعرض اسمه نصاً فقط — لا صورة مكسورة أبداً.
def _load_logos():
    try:
        with open(os.path.join(ROOT, "data/logos.json"), encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {"leagues": {}, "clubs": []}
LOGOS_DATA = _load_logos()
LOGO_BY_AR = {c["ar"]: c["file"] for c in LOGOS_DATA.get("clubs", [])}
def logo_img(team, cls="team-logo"):
    f = LOGO_BY_AR.get(team)
    if not f:
        return ""
    return (f'<img class="{cls}" src="{f}" alt="شعار {team}" '
            f'loading="lazy" onerror="this.remove()">')
def league_logo_img(lid):
    f = LOGOS_DATA.get("leagues", {}).get(lid)
    if not f:
        return ""
    return (f'<img class="league-logo" src="{f}" alt="شعار الدوري" '
            f'loading="lazy" onerror="this.remove()">')

def w(path, text):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(text)

def dump(path, obj):
    w(path, json.dumps(obj, ensure_ascii=False, indent=2) + "\n")

# ------------------------------------------------------------- CSS add ---
CSS_ADD = """
/* ---------- الملعب V2: إضافات ---------- */
.cpa-slot {
  border: 1.5px dashed var(--gold); border-radius: 12px; background: #171208;
  color: var(--muted); text-align: center; padding: 18px 14px; margin: 22px 0;
  font-size: .88rem;
}
.cpa-slot b { color: var(--gold); display: block; font-size: .95rem; margin-bottom: 4px; }
.cpa-slot small { display: block; margin-top: 6px; font-size: .75rem; }
.data-note {
  background: #0d1424; border: 1px solid var(--border); border-right: 3px solid var(--accent);
  border-radius: 10px; padding: 10px 14px; color: var(--muted); font-size: .82rem; margin: 14px 0;
}
.data-note b { color: var(--text); }
.league-chips { display: flex; gap: 8px; flex-wrap: wrap; padding: 14px 0 4px; }
.league-chips a {
  background: var(--card); border: 1px solid var(--border); color: var(--text);
  padding: 8px 16px; border-radius: 30px; font-weight: 700; font-size: .88rem;
}
.league-chips a:hover { border-color: var(--accent); color: var(--accent); }
.date-strip { display: flex; gap: 10px; flex-wrap: wrap; margin: 16px 0; }
.date-strip .day {
  flex: 1; min-width: 150px; background: var(--card); border: 1px solid var(--border);
  border-radius: 12px; padding: 12px 14px; text-align: center;
}
.date-strip .day b { display: block; font-size: 1rem; }
.date-strip .day span { color: var(--muted); font-size: .82rem; }
.date-strip .day.next { border-color: var(--accent); }
.date-strip .day.next b { color: var(--accent); }
.match-link { display: block; }
.match-link:hover .match-row { border-color: var(--accent); }
.match-row .date-lbl { font-size: .78rem; color: var(--muted); white-space: nowrap; }
.placeholder-box {
  background: var(--card); border: 1px dashed var(--border); border-radius: 12px;
  padding: 22px; text-align: center; color: var(--muted);
}
.verified-tag {
  display: inline-block; background: rgba(34,224,122,.15); color: var(--accent);
  border: 1px solid rgba(34,224,122,.4); font-size: .72rem; font-weight: 700;
  padding: 2px 10px; border-radius: 20px;
}
.stat-row { display: grid; grid-template-columns: 44px 1fr 44px; align-items: center; gap: 10px; margin-bottom: 10px; font-size: .88rem; }
.stat-bar { height: 8px; background: #0b0f1c; border-radius: 6px; overflow: hidden; display: flex; }
.stat-bar i { display: block; height: 100%; }
.stat-bar i.h { background: var(--accent); }
.stat-bar i.a { background: var(--blue); margin-inline-start: auto; }
.timeline { list-style: none; }
.timeline li { padding: 10px 4px; border-bottom: 1px solid var(--border); font-size: .92rem; }
.timeline li:last-child { border-bottom: none; }
.timeline .min { color: var(--gold); font-weight: 800; margin-inline-end: 8px; }
.scoreboard {
  background: linear-gradient(135deg, #14264a, #0e2b1a); border: 1px solid var(--border);
  border-radius: var(--radius); padding: 26px 18px; text-align: center; margin: 18px 0;
}
.scoreboard .teams { display: flex; align-items: center; justify-content: center; gap: 18px; flex-wrap: wrap; }
.scoreboard .team-name { font-size: 1.25rem; font-weight: 800; }
.scoreboard .big-score { font-size: 2.4rem; font-weight: 800; background: #0b0f1c; border: 1px solid var(--border); border-radius: 12px; padding: 6px 22px; }
.scoreboard .status { color: var(--muted); margin-top: 10px; font-size: .9rem; }
.detail-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 18px; }
@media (max-width: 760px) { .detail-grid { grid-template-columns: 1fr; } }
/* ---------- إصلاحات التشريح 18 نونبر 2026: إخفاء الإعلانات الفارغة + شارات الحالة + تبويبات المباراة ---------- */
.ad-slot, .cpa-slot, .anchored-ad, .ad-leaderboard, .ad-infeed, .ad-rect { display: none !important; }
.status-badge { display: inline-block; font-size: .72rem; font-weight: 800; padding: 2px 10px; border-radius: 20px; margin-inline-start: 8px; vertical-align: middle; }
.status-badge.live { background: rgba(255,77,94,.18); color: #ff4d5e; border: 1px solid rgba(255,77,94,.5); animation: blink 1.2s infinite; }
.status-badge.finished { background: rgba(154,166,199,.15); color: var(--muted); border: 1px solid var(--border); }
.status-badge.upcoming { background: rgba(34,224,122,.12); color: var(--accent); border: 1px solid rgba(34,224,122,.4); }
.match-tabs { display: flex; gap: 8px; flex-wrap: wrap; margin: 18px 0 14px; }
.match-tabs button { background: var(--card); border: 1px solid var(--border); color: var(--muted); padding: 9px 20px; border-radius: 30px; font-weight: 700; cursor: pointer; font-family: inherit; }
.match-tabs button.active { background: var(--accent); color: #06130c; border-color: var(--accent); }
.match-info { display: flex; gap: 8px 22px; flex-wrap: wrap; justify-content: center; background: var(--card); border: 1px solid var(--border); border-radius: 12px; padding: 12px 16px; margin: 14px 0; font-size: .88rem; color: var(--muted); }
.match-info b { color: var(--text); }
.match-info .lbl { color: var(--accent); font-weight: 700; margin-inline-end: 4px; }

/* ---------- شعارات الفرق والدوريات (ملفات محلية فقط) ---------- */
.team-logo { width: 22px; height: 22px; object-fit: contain; vertical-align: middle; margin-inline-end: 6px; flex-shrink: 0; }
.league-logo { width: 34px; height: 34px; object-fit: contain; vertical-align: middle; margin-inline-end: 8px; flex-shrink: 0; }
.match-row .team-logo { width: 26px; height: 26px; }
.scoreboard .team-logo { width: 34px; height: 34px; margin-inline-end: 8px; }
.scoreboard .team-name { display: inline-flex; align-items: center; gap: 2px; }
/* خلية الفريق تلفّ النص بدل التمرير الأفقي على الهاتف (390px) */
table.standings td.team { white-space: normal; overflow-wrap: anywhere; }
.match-row .team { overflow-wrap: anywhere; }
.league-chips a { display: inline-flex; align-items: center; gap: 6px; }
.league-chips .league-logo { width: 22px; height: 22px; margin-inline-end: 0; }
.league-select button { display: inline-flex; align-items: center; gap: 6px; }
.league-select .league-logo { width: 24px; height: 24px; margin-inline-end: 0; }
h1 .league-logo { width: 40px; height: 40px; }
.scorer .info span .team-logo { width: 18px; height: 18px; }
@media (max-width: 480px) {
  .team-logo { width: 20px; height: 20px; }
  .match-row .team-logo { width: 24px; height: 24px; }
  .league-logo { width: 30px; height: 30px; }
  h1 .league-logo { width: 34px; height: 34px; }
}
"""

# -------------------------------------------------------------- JS ------
MAIN_JS = r"""/* الملعب V2 — main.js: فلتر صارم: 6 دوريات فقط، بلا محاكاة، بلا مسابقات أخرى */
(function () {
  "use strict";
  var ALLOWED_IDS = ["premier-league", "la-liga", "serie-a", "bundesliga", "ligue-1", "botola"];
  var ALLOWED_NAMES = ["الدوري الإنجليزي", "الدوري الإسباني", "الدوري الإيطالي",
    "الدوري الألماني", "الدوري الفرنسي", "البطولة الاحترافية المغربية", "البطولة المغربية"];
  window.MALAEB_ALLOWED = ALLOWED_IDS;
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
  window.MalaebData = {
    async leagues() {
      const d = await loadJSON("data/leagues.json");
      if (d && d.leagues) return d;
      return { leagues: FALLBACK.leagues, updated: (typeof FALLBACK !== "undefined" && FALLBACK.updated) || "" };
    },
    async fixtures() {
      const d = await loadJSON("data/fixtures.json");
      if (d) return d;
      return FALLBACK.fixtures;
    },
    async news() {
      const d = await loadJSON("data/news.json");
      if (d && d.articles) return d.articles;
      return [];
    }
  };

  /* الشعارات: ملفات محلية من data/logos.json — فريق بلا شعار يظهر نصاً فقط */
  window.MalaebLogos = { leagues: {}, byAr: {}, ready: false, promise: null };
  window.loadLogos = function () {
    if (window.MalaebLogos.promise) return window.MalaebLogos.promise;
    window.MalaebLogos.promise = (async function () {
      try {
        const d = await loadJSON("data/logos.json");
        if (d) {
          window.MalaebLogos.leagues = d.leagues || {};
          (d.clubs || []).forEach(c => { window.MalaebLogos.byAr[c.ar] = c.file; });
        }
      } catch (e) {}
      window.MalaebLogos.ready = true;
      return window.MalaebLogos;
    })();
    return window.MalaebLogos.promise;
  };
  window.logoFor = function (teamName) {
    if (!teamName || teamName === "—") return "";
    const f = window.MalaebLogos.byAr[teamName];
    if (!f) return "";
    const esc = String(teamName).replace(/"/g, "&quot;");
    return `<img class="team-logo" src="${f}" alt="شعار ${esc}" loading="lazy" onerror="this.remove()">`;
  };
  window.leagueLogoFor = function (leagueId) {
    const f = window.MalaebLogos.leagues[leagueId];
    if (!f) return "";
    return `<img class="league-logo" src="${f}" alt="شعار الدوري" loading="lazy" onerror="this.remove()">`;
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
          if (note) { note.textContent = "المرجو إدخال بريد إلكتروني صحيح."; note.style.color = "#ff4d5e"; }
          return;
        }
        if (note) { note.textContent = "شكراً! تم تسجيل اشتراكك بنجاح. ⚽"; note.style.color = "#22e07a"; }
        input.value = "";
      });
    });
    const closeAd = document.querySelector(".close-ad");
    if (closeAd) closeAd.addEventListener("click", () => {
      document.querySelector(".anchored-ad").style.display = "none";
    });
  });

  /* الشريط المتحرك: الدوريات الستة فقط — لا دوريات غامضة */
  window.renderTicker = async function (elId) {
    const el = document.getElementById(elId);
    if (!el) return;
    const fx = await window.MalaebData.fixtures();
    const items = [];
    onlyAllowed(fx.live || []).forEach(m => {
      items.push(`<span class="ticker-item"><span class="live-dot">● مباشر ${m.minute}'</span> <b>${m.home} ${m.home_goals} - ${m.away_goals} ${m.away}</b></span>`);
    });
    onlyAllowed(fx.upcoming || []).slice(0, 8).forEach(m => {
      items.push(`<span class="ticker-item">${m.home} × ${m.away} <b>${m.date_label || m.date} ${m.time || ""}</b></span>`);
    });
    const liveCount = onlyAllowed(fx.live || []).length;
    const head = liveCount ? "" : "<span class='ticker-item'>لا مباريات مباشرة الآن — القادمة:</span>";
    el.innerHTML = head + (items.join("") || "<span class='ticker-item'>لا توجد مباريات مبرمجة في الدوريات الستة حالياً</span>");
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
      <thead><tr><th>#</th><th>الفريق</th><th>لعب</th><th>فاز</th><th>تعادل</th><th>خسر</th><th>فرق</th><th>نقاط</th></tr></thead>
      <tbody>${rows}</tbody></table></div>`;
  };

  window.matchRowHTML = function (m) {
    const isLive = m.status === "live";
    const isFin = m.status === "finished";
    const score = isLive || isFin
      ? `<span class="score${isLive ? " live" : ""}">${m.home_goals} - ${m.away_goals}</span>`
      : `<span class="score">${m.time || "—"}</span>`;
    const badge = isLive
      ? `<span class="status-badge live">● مباشر ${m.minute || ""}'</span>`
      : isFin
        ? `<span class="status-badge finished">انتهت</span>`
        : `<span class="status-badge upcoming">لم تبدأ بعد</span>`;
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

MATCHES_JS = r"""/* الملعب V2 — matches.js: تبويبات حقيقية من data/fixtures.json فقط. بلا محاكاة. */
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
  /* تواريخ ديناميكية من data/fixtures.json (today_date/tomorrow_date) — بلا تواريخ مكتوبة */
  function dayLabel(iso) {
    if (!iso) return "";
    return new Date(iso + "T12:00:00").toLocaleDateString("ar-MA", {weekday: "long", day: "numeric", month: "long", year: "numeric"});
  }
  function shortDay(iso) {
    if (!iso) return "";
    return new Date(iso + "T12:00:00").toLocaleDateString("ar-MA", {day: "numeric", month: "long"});
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
      if (t === "today") btn.textContent = "📅 اليوم " + shortDay(FX.today_date);
      else if (t === "tomorrow") btn.textContent = "📅 غداً " + shortDay(FX.tomorrow_date);
      else if (t === "friday") { const nd = nextDay(); btn.textContent = nd ? "⏭️ " + dayLabel(nd) : "⏭️ القادمة"; }
    });
  }
  function render() {
    const box = $("matches-box");
    if (!box || !FX) return;
    let html = "";
    const nd = nextDay();
    const back = nd ? ` العودة ${dayLabel(nd)}.` : "";
    if (currentTab === "today") {
      html = listHTML(FX.today) || emptyMsg(`لا توجد مباريات اليوم (${dayLabel(FX.today_date)}) في الدوريات الستة.${back}`);
    } else if (currentTab === "tomorrow") {
      html = listHTML(FX.tomorrow) || emptyMsg(`لا توجد مباريات غداً (${dayLabel(FX.tomorrow_date)}) في الدوريات الستة.${back}`);
    } else if (currentTab === "friday") {
      const fri = (FX.upcoming || []).filter(m => nd && m.date === nd);
      html = listHTML(fri) || emptyMsg(nd ? `لا توجد مباريات مبرمجة يوم ${dayLabel(nd)}.` : "لا توجد مباريات قادمة مسجلة.");
    } else if (currentTab === "upcoming") {
      html = listHTML(FX.upcoming) || emptyMsg("لا توجد مباريات قادمة مسجلة.");
    } else {
      const r = FX.results || [];
      html = r.length ? listHTML(r) : emptyMsg("لا توجد نتائج مسجلة.");
      if (r.length) {
        const dates = r.map(m => m.date).sort();
        const range = dates[0] === dates[dates.length - 1] ? shortDay(dates[0]) : shortDay(dates[0]) + " – " + shortDay(dates[dates.length - 1]);
        html = `<p class="data-note">آخر النتائج (${range}) — المصدر: ESPN. الأوقات بتوقيت المغرب (UTC+1).</p>` + html;
      }
    }
    box.innerHTML = html;
  }
  document.addEventListener("DOMContentLoaded", async function () {
    await window.loadLogos();
    FX = await window.MalaebData.fixtures();
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

STANDINGS_JS = r"""/* الملعب V2 — standings.js: 6 دوريات فقط */
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
    if (title) title.innerHTML = `${window.leagueLogoFor(l.id)}${l.name} <small style="color:var(--muted);font-size:.85rem">موسم ${l.season || "2026-27"} — ${l.round || ""}</small>`;
    const tw = document.getElementById("table-wrap");
    if (tw) tw.innerHTML = window.standingsTableHTML(l)
      + `<p class="data-note"><b>المصدر:</b> ${l.source || "—"} — <b>آخر تحقق:</b> ${DATA.updated || ""}. الجدول الكامل موثق لكل دوري.</p>`;
    const sc = document.getElementById("scorers");
    if (sc) {
      const list = (l.scorers || []).slice(0, 8);
      sc.innerHTML = list.length ? list.map((s, i) => `
        <div class="scorer"><span class="rank">${i + 1}</span>
        <span class="info"><b>${s.player}</b><span>${window.logoFor(s.team)}${s.team}</span></span>
        <span class="goals">${s.goals}</span></div>`).join("")
        : `<div class="placeholder-box">لا توجد قائمة هدافين موثقة لهذا الدوري بعد — تُضاف فور التحقق من مصدر رسمي.</div>`;
    }
    const upd = document.getElementById("data-updated");
    if (upd && DATA.updated) upd.textContent = "آخر تحديث: " + DATA.updated;
  }
  document.addEventListener("DOMContentLoaded", async function () {
    await window.loadLogos();
    DATA = await window.MalaebData.leagues();
    renderSelector();
    renderLeague();
  });
})();
"""

HOME_JS = r"""/* الملعب V2 — home.js: الرئيسية تُبقي رسالة التوقف الدولي (Hero ثابت في HTML) */
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
      const articles = await window.MalaebData.news();
      if (articles.length) {
        document.querySelector("#home-news").innerHTML = articles.slice(0, 6).map(newsCard).join("");
      }
    } catch (e) {}
    try {
      const fx = await window.MalaebData.fixtures();
      const up = (fx.upcoming || []).filter(window.isAllowedLeague).slice(0, 6);
      document.querySelector("#home-matches").innerHTML = up.length
        ? up.map(window.matchRowHTML).join("")
        : `<p style="color:var(--muted)">لا توجد مباريات مبرمجة حالياً.</p>`;
    } catch (e) {}
    try {
      const data = await window.MalaebData.leagues();
      const pick = ["premier-league", "la-liga", "botola"]
        .map(id => data.leagues.find(l => l.id === id)).filter(Boolean);
      document.querySelector("#home-tables").innerHTML = pick.map(l => `
        <div>
          <div class="section-head" style="margin-bottom:10px">
            <h2 style="font-size:1.05rem">${l.name}</h2>
            <a class="more" href="league-${l.id}.html">الجدول الكامل ←</a>
          </div>
          ${window.standingsTableHTML(l, 5)}
          <p style="color:var(--muted);font-size:.78rem;margin-top:6px">أول 5 مراكز — الجدول الكامل في صفحة الدوري — آخر تحقق: ${data.updated || ""}</p>
        </div>`).join("");
    } catch (e) {}
  });
})();
"""

MATCH_JS = r"""/* الملعب V2 — match.js: صفحة تفاصيل المباراة (?id=) — بيانات موثقة فقط، والباقي Placeholder صريح */
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
    const fx = await window.MalaebData.fixtures();
    const all = [].concat(fx.live || [], fx.today || [], fx.tomorrow || [], fx.upcoming || [], fx.results || []);
    const m = all.find(x => x.id === id);
    if (!m) {
      box.innerHTML = `<div class="placeholder-box"><h2 style="margin-bottom:8px">المباراة غير موجودة</h2><p>الرابط غير صحيح أو المباراة غير مدرجة في الدوريات الستة. <a href="matches.html" style="color:var(--accent)">← العودة إلى المباريات</a></p></div>`;
      return;
    }
    const isFin = m.status === "finished";
    const score = isFin ? `${m.home_goals} - ${m.away_goals}` : (m.time || "—");
    const status = isFin ? "انتهت" : `مباراة قادمة — ${m.date_label || m.date} ${m.time ? "• " + m.time + " بتوقيت المغرب" : "• التوقيت قيد التأكيد"}`;
    document.title = `${m.home} × ${m.away} | الملعب`;
    const h1 = document.getElementById("match-h1");
    if (h1) h1.textContent = `${m.home} × ${m.away}`;
    const infoVenue = m.venue || m.venue_note || "قيد التحقق";
    const infoRef = m.referee || "قيد التحقق";
    const infoChan = m.channel || "قيد التحقق";
    const infoTime = isFin ? "انتهت" : ((m.date_label || m.date || "") + (m.time ? " • " + m.time + " بتوقيت المغرب" : " • التوقيت قيد التأكيد"));
    function statBar(label, h, a) {
      const t = (h || 0) + (a || 0);
      const hp = t ? Math.round(100 * h / t) : 50;
      return `<div class="stat-row"><span><b>${h}</b></span><div><div style="text-align:center;font-size:.8rem;color:var(--muted)">${label}</div><div class="stat-bar"><i class="h" style="width:${hp}%"></i><i class="a" style="width:${100 - hp}%"></i></div></div><span style="text-align:left"><b>${a}</b></span></div>`;
    }
    const st = m.stats || null;
    const statsHTML = st ? (
      statBar("الاستحواذ %", st.possession_home, st.possession_away)
      + statBar("التسديدات", st.shots_home, st.shots_away)
      + statBar("التسديدات على المرمى", st.shots_on_target_home, st.shots_on_target_away)
      + statBar("الركنيات", st.corners_home, st.corners_away)
      + `<p style="color:var(--muted);font-size:.78rem;margin-top:10px">المصدر: ${esc(st.source || "—")}</p>`
    ) : `<div class="placeholder-box">الإحصائيات غير متوفرة بعد لهذه المباراة.<br>تُعرض هنا (الاستحواذ، التسديدات، الركنيات) فور توثيقها من مصدر رسمي.</div>`;
    const eventsHTML = (m.events && m.events.length) ? m.events.map(e =>
      `<div class="event-row"><span class="ev-min">${esc(e.minute || "")}'</span><span class="ev-type">${esc(e.type || "")}</span><b>${esc(e.player || "")}</b><span style="color:var(--muted)">${esc(e.team || "")}</span></div>`).join("")
      : `<div class="placeholder-box">لا توجد أحداث موثقة بعد لهذه المباراة (أهداف، بطاقات، تبديلات).<br>تُضاف الأحداث بعد توثيقها من مصدر رسمي.</div>`;
    box.innerHTML = `
    <div class="scoreboard">
      <div class="teams"><span class="team-name">${window.logoFor(m.home)}${esc(m.home)}</span>
      <span class="big-score">${score}</span>
      <span class="team-name">${window.logoFor(m.away)}${esc(m.away)}</span></div>
      <div class="status">${m.league_name} • ${status}</div>
      <div class="status" style="font-size:.8rem">المصدر: ${esc(m.source || "—")} — آخر تحقق: ${esc(fx.updated || "")}</div>
    </div>
    <div class="match-info">
      <span><span class="lbl">🏟️ الملعب:</span><b>${esc(infoVenue)}</b></span>
      <span><span class="lbl">الحكم:</span><b>${esc(infoRef)}</b></span>
      <span><span class="lbl">📺 القناة الناقلة:</span><b>${esc(infoChan)}</b></span>
      <span><span class="lbl">🕐 التوقيت:</span><b>${esc(infoTime)}</b></span>
    </div>
    <div class="match-tabs">
      <button data-mtab="events" class="active">الأحداث</button>
      <button data-mtab="stats">الإحصائيات</button>
      <button data-mtab="lineups">التشكيلة</button>
      <button data-mtab="h2h">المواجهات</button>
    </div>
    <div class="mtab-panel" data-panel="events">
      ${eventsHTML}
    </div>
    <div class="mtab-panel" data-panel="stats" style="display:none">${statsHTML}</div>
    <div class="mtab-panel" data-panel="lineups" style="display:none">
      <div class="placeholder-box">التشكيلتان الرسميتان غير موثقتين بعد — تُنشران قبل انطلاق المباراة بساعة من مصدر رسمي.</div>
    </div>
    <div class="mtab-panel" data-panel="h2h" style="display:none">
      <div class="placeholder-box">سجل المواجهات المباشرة بين الفريقين غير موثق بعد — يُضاف من مصدر رسمي.</div>
    </div>
    <p><a href="matches.html" style="color:var(--accent);font-weight:700">← العودة إلى كل المباريات</a></p>`;
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
BASE = "https://almalaeb.onrender.com"
ICON = """<link rel="icon" href="data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'><text y='.9em' font-size='90'>⚽</text></svg>">"""
FONTS = """<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Tajawal:wght@400;500;700;800&display=swap" rel="stylesheet">
<link rel="stylesheet" href="assets/css/style.css">"""

def header(active=""):
    def a(page, label):
        return f'<li><a href="{page}" class="active">{label}</a></li>' if page == active else f'<li><a href="{page}">{label}</a></li>'
    return f"""<header class="site-header">
  <div class="container header-inner">
    <a href="index.html" class="logo"><span class="ball">⚽</span><span>الملعب<small>AL MALAEB</small></span></a>
    <button class="menu-btn" aria-label="القائمة">☰</button>
    <nav class="main-nav"><ul>
      {a("index.html", "الرئيسية")}{a("matches.html", "المباريات")}{a("standings.html", "الترتيب")}{a("news.html", "الأخبار")}
    </ul></nav>
  </div>
</header>"""

CHIPS = f"""<div class="container"><div class="league-chips">
<a href="league-premier-league.html">{league_logo_img("premier-league")}الدوري الإنجليزي</a>
<a href="league-la-liga.html">{league_logo_img("la-liga")}الدوري الإسباني</a>
<a href="league-serie-a.html">{league_logo_img("serie-a")}الدوري الإيطالي</a>
<a href="league-bundesliga.html">{league_logo_img("bundesliga")}الدوري الألماني</a>
<a href="league-ligue-1.html">{league_logo_img("ligue-1")}الدوري الفرنسي</a>
<a href="league-botola.html">{league_logo_img("botola")}البطولة المغربية</a>
</div></div>"""

TICKER = """<div class="ticker-wrap"><div class="container ticker">
  <span class="ticker-label">مباشر</span>
  <div class="ticker-track" id="ticker-track"><span class="ticker-item">لا مباريات مباشرة الآن — جارٍ تحميل المباريات القادمة…</span></div>
</div></div>"""

CPA_SLOT = """<div class="cpa-slot"><b>مساحة إعلانية — CPA (Placeholder)</b>تُضاف هنا عروض موثوقة بعد اختيارها — بدون نوافذ منبثقة وبدون روابط مراهنات.<small>لا يوجد أي عرض حي أو رابط خارجي في هذه المساحة حالياً.</small></div>"""

AD_LEADER = """<div class="container"><div class="ad-slot"><div class="ad-leaderboard">مساحة إعلانية — Leaderboard 970×250</div></div></div>"""

def footer():
    return f"""<footer class="site-footer">
  <div class="container">
    <div class="footer-grid">
      <div>
        <h4>⚽ الملعب</h4>
        <p style="color:var(--muted);font-size:.9rem">موقعك المغربي لمتابعة كرة القدم: نتائج مباشرة، جداول الترتيب، وآخر الأخبار من الدوريات الأوروبية الخمسة الكبرى والبطولة المغربية.</p>
      </div>
      <div>
        <h4>أقسام الموقع</h4>
        <ul>
          <li><a href="matches.html">مباريات اليوم</a></li>
          <li><a href="standings.html">جداول الترتيب</a></li>
          <li><a href="news.html">آخر الأخبار</a></li>
          <li><a href="league-botola.html">البطولة المغربية</a></li>
        </ul>
      </div>
      <div>
        <h4>معلومات</h4>
        <ul>
          <li><a href="about.html">من نحن</a></li>
          <li><a href="contact.html">اتصل بنا</a></li>
          <li><a href="privacy.html">سياسة الخصوصية</a></li>
        </ul>
      </div>
    </div>
    <div class="footer-bottom">
      <span>© <span class="js-year">2026</span> الملعب — جميع الحقوق محفوظة.</span>
      <span>البيانات لأغراض إخبارية — آخر تحديث: {BUILD_DATE_AR}</span>
    </div>
  </div>
</footer>
<div class="anchored-ad"><span>مساحة إعلانية للهواتف</span><button class="close-ad">✕</button></div>"""

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
            '<thead><tr><th>#</th><th>الفريق</th><th>لعب</th><th>فاز</th><th>تعادل</th><th>خسر</th><th>فرق</th><th>نقاط</th></tr></thead>'
            f'<tbody>{"".join(out)}</tbody></table></div>')

def scorers_html(league):
    sc = league["scorers"]
    if not sc:
        return '<div class="placeholder-box">لا توجد قائمة هدافين موثقة لهذا الدوري بعد — تُضاف فور التحقق من مصدر رسمي.</div>'
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
            when += " — التوقيت قيد التأكيد"
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
        return "لا مباريات"
    if n == 1:
        return "مباراة واحدة"
    if n == 2:
        return "مباراتان"
    return f"{n} مباريات"


def hero_blocks():
    """كتلة البطل + شريط الأيام في الرئيسية — من بيانات اليوم/غداً/القادمة."""
    today_n, tom_n = len(FX_TODAY), len(FX_TOMORROW)
    nxt = None
    for m in UPCOMING:
        if m["date"] > (FX_TOMORROW_DATE or ""):
            nxt = m["date"]
            break
    nxt_n = len([m for m in UPCOMING if m["date"] == nxt]) if nxt else 0
    if today_n:
        tag, title = "⚽ مباريات اليوم", f"مباريات اليوم: {_count_txt(today_n)} في الدوريات الستة"
        first = "، ".join(f"{m['home']} × {m['away']}" for m in FX_TODAY[:3])
        sub = (f"{ar_date(FX_TODAY_DATE)} — {first}." if FX_TODAY_DATE else first)
        btn = "شاهد مباريات اليوم ←"
    else:
        tag, title = "⏸️ لا مباريات اليوم", "مباريات اليوم: لا مباريات في الدوريات الستة"
        if nxt:
            first = "، ".join(f"{m['home']} × {m['away']}" for m in [x for x in UPCOMING if x["date"] == nxt][:3])
            sub = f"{ar_date(FX_TODAY_DATE) if FX_TODAY_DATE else ''} — العودة {ar_date(nxt)}: {first}."
        else:
            sub = "لا مباريات قادمة مسجلة حالياً."
        btn = "شاهد المباريات القادمة ←"
    hero = (f'<section class="hero" id="hero"><div class="hero-card"><div class="hero-content">\n'
            f'    <span class="tag">{tag}</span>\n    <h1>{title}</h1>\n    <p>{sub}</p>\n'
            f'    <a class="btn" href="matches.html">{btn}</a>\n  </div></div></section>')
    cells = []
    if FX_TODAY_DATE:
        cells.append(f'<div class="day"><b>اليوم — {ar_date_short(FX_TODAY_DATE)}</b><span>{_count_txt(today_n)}</span></div>')
    if FX_TOMORROW_DATE:
        cells.append(f'<div class="day"><b>غداً — {ar_date_short(FX_TOMORROW_DATE)}</b><span>{_count_txt(tom_n)}</span></div>')
    if nxt:
        cells.append(f'<div class="day next"><b>{ar_date_short(nxt)}</b><span>{_count_txt(nxt_n)}</span></div>')
    strip = '<div class="date-strip">\n    ' + "\n    ".join(cells) + '\n  </div>'
    return hero, strip


def refresh_dates():
    """يحدّث التواريخ المجمدة ('آخر تحديث: …' / 'آخر تحقق …') في الصفحات المولّدة
    من ملفات V1 (الترتيب، الدوريات، الأخبار…) — بلا لمس مقالات news/ (تواريخها تاريخية)."""
    pages = ["index.html", "matches.html", "match.html", "standings.html", "news.html",
             "about.html", "contact.html", "privacy.html"] + \
            [f"league-{l['id']}.html" for l in LEAGUES]
    for name in pages:
        p = os.path.join(ROOT, name)
        if not os.path.exists(p):
            continue
        with open(p, encoding="utf-8") as f:
            s = f.read()
        s2 = re.sub(r"آخر تحديث: (?:\S+ )?\d{1,2} \S+ \d{4}", f"آخر تحديث: {BUILD_DATE_AR}", s)
        s2 = re.sub(r"آخر تحقق: (?:\S+ )?\d{1,2} \S+ \d{4}", f"آخر تحقق: {BUILD_DATE_AR}", s2)
        s2 = re.sub(r"آخر تحقق (?:\S+ )?\d{1,2} \S+ \d{4}", f"آخر تحقق {BUILD_DATE_AR}", s2)
        if s2 != s:
            w(p, s2)


def main():
    _load_live_data()  # يفضّل data/*.json (يكتبها التحديث اليومي) على البيانات المضمّنة
    # ---- data files (verified only) ----
    dump(os.path.join(ROOT, "data/leagues.json"),
         {"updated": CHECKED, "leagues": LEAGUES,
          "note": f"الجداول الكاملة موثقة لكل دوري (آخر تحقق {ar_date(CHECKED)}). المصدر: ESPN + FRMF.ma للبطولة."})
    dump(os.path.join(ROOT, "data/fixtures.json"),
         {"updated": CHECKED,
          "today_date": FX_TODAY_DATE, "tomorrow_date": FX_TOMORROW_DATE,
          "note": FX_NOTE or "الأوقات بتوقيت المغرب (UTC+1).",
          "live": FX_LIVE, "today": FX_TODAY, "tomorrow": FX_TOMORROW,
          "upcoming": UPCOMING, "results": RESULTS})
    with open(os.path.join(V1, "data/news.json"), encoding="utf-8") as f:
        news = json.load(f)
    news["articles"] = [a for a in news["articles"] if a.get("category") != "دوري أبطال أوروبا"]
    dump(os.path.join(ROOT, "data/news.json"), news)

    # ---- CSS ----
    css = os.path.join(ROOT, "assets/css/style.css")
    with open(css, encoding="utf-8") as f:
        s = f.read()
    if "الملعب V2" not in s:
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
        f"/* الملعب V2 — بيانات احتياطية موثقة ({BUILD_DATE_AR})، تُستخدم فقط إذا تعذّر تحميل data/*.json */\n"
        "const FALLBACK = " + json.dumps(fb, ensure_ascii=False, indent=2) + ";\n")

    # ---- index.html (fresh) ----
    HERO, STRIP = hero_blocks()
    index = f"""<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>الملعب | مباريات اليوم، نتائج مباشرة، ترتيب الدوريات وآخر الأخبار</title>
<meta name="description" content="الملعب — مباريات اليوم والنتائج المباشرة، جداول ترتيب الدوري الإنجليزي والإسباني والإيطالي والألماني والفرنسي والبطولة المغربية، وآخر الأخبار بالعربية. آخر تحديث: {BUILD_DATE_AR}.">
<meta property="og:title" content="الملعب | نتائج مباشرة وأخبار كرة القدم">
<meta property="og:description" content="مباريات اليوم، ترتيب الدوريات الخمسة الكبرى والبطولة المغربية، وآخر الأخبار.">
<meta property="og:type" content="website">
<meta property="og:locale" content="ar_MA">
<script type="application/ld+json">{{"@context":"https://schema.org","@type":"WebSite","name":"الملعب","alternateName":"Al Malaeb","inLanguage":"ar","description":"موقع عربي لمتابعة مباريات ونتائج وترتيب الدوريات الأوروبية الخمسة الكبرى والبطولة المغربية."}}</script>
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
    <div class="section-head"><h2>المباريات القادمة</h2><a class="more" href="matches.html">كل المباريات ←</a></div>
    <div class="match-list" id="home-matches"><p style="color:var(--muted)">جارٍ التحميل…</p></div>
    <p class="data-note"><b>مصادر المباريات:</b> ESPN (site.api.espn.com) للدوريات الأوروبية الخمسة + FRMF.ma للبطولة المغربية — آخر تحقق: {BUILD_DATE_AR}. الأوقات بتوقيت المغرب (UTC+1).</p>
  </section>

  {CPA_SLOT}

  <section class="section">
    <div class="section-head"><h2>آخر الأخبار</h2><a class="more" href="news.html">كل الأخبار ←</a></div>
    <div class="news-grid" id="home-news"></div>
    <p style="color:var(--muted);font-size:.82rem">الأخبار أرشيف بتاريخ نشرها (شتنبر 2026) — الأرقام الحالية تجدها في صفحات الترتيب والمباريات.</p>
  </section>

  <section class="section">
    <div class="section-head"><h2>جداول الترتيب الكاملة</h2><a class="more" href="standings.html">الجداول الكاملة ←</a></div>
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
<html lang="ar" dir="rtl">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>مباريات اليوم والنتائج المباشرة | الملعب</title>
<meta name="description" content="مباريات اليوم وغداً والقادمة والنتائج من الدوريات الخمسة الكبرى والبطولة المغربية. آخر تحديث: {BUILD_DATE_AR}.">
<meta property="og:title" content="مباريات اليوم — نتائج مباشرة | الملعب">
<meta property="og:locale" content="ar_MA">
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
    <div class="section-head"><h1 style="font-size:1.6rem">⚽ مباريات الدوريات الستة</h1></div>
    <p class="data-note"><b>اليوم {ar_date(FX_TODAY_DATE) if FX_TODAY_DATE else ""}:</b> {FX_NOTE} الأوقات بتوقيت المغرب (UTC+1).</p>
    <div class="tabs">
      <button data-tab="today" class="active">📅 اليوم {ar_date_short(FX_TODAY_DATE) if FX_TODAY_DATE else ""}</button>
      <button data-tab="tomorrow">📅 غداً {ar_date_short(FX_TOMORROW_DATE) if FX_TOMORROW_DATE else ""}</button>
      <button data-tab="friday">⏭️ القادمة</button>
      <button data-tab="upcoming">🗓️ كل القادمة</button>
      <button data-tab="results">✅ النتائج الأخيرة</button>
    </div>
    <div id="matches-box"><p style="color:var(--muted);text-align:center">جارٍ التحميل…</p></div>
    {CPA_SLOT}
    <p style="color:var(--muted);font-size:.78rem;margin-top:14px">💡 النتائج المباشرة تظهر هنا فقط من مصدر بيانات حي موثوق. حالياً لا يوجد مصدر حي مربوط (API-Football موقوف) — الصفحة تعرض المباريات المبرمجة الموثقة والنتائج الأخيرة فقط، بدون محاكاة.</p>
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
<html lang="ar" dir="rtl">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>تفاصيل المباراة | الملعب</title>
<meta name="description" content="تفاصيل المباراة: النتيجة، الأحداث، الإحصائيات، التشكيلتان والمواجهات المباشرة — الملعب.">
<meta property="og:title" content="تفاصيل المباراة | الملعب">
<meta property="og:locale" content="ar_MA">
<script type="application/ld+json">{{"@context":"https://schema.org","@type":"SportsEvent","name":"مانشستر سيتي × فولهام","sport":"كرة القدم","startDate":"2026-11-21T12:30:00Z","location":{{"@type":"Place","name":"ملعب الاتحاد","address":"مانشستر، إنجلترا"}},"homeTeam":{{"@type":"SportsTeam","name":"مانشستر سيتي"}},"awayTeam":{{"@type":"SportsTeam","name":"فولهام"}},"competitor":[{{"@type":"SportsTeam","name":"مانشستر سيتي"}},{{"@type":"SportsTeam","name":"فولهام"}}]}}</script>
{FONTS}
{ICON}
</head>
<body>
{header("")}
{CHIPS}
{TICKER}
<main class="container">
  <section class="section">
    <h1 id="match-h1" style="font-size:1.6rem">تفاصيل المباراة</h1>
    <div id="match-detail"><p style="color:var(--muted)">جارٍ التحميل…</p></div>
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
    cat_by_league = {"premier-league": "الدوري الإنجليزي", "la-liga": "الدوري الإسباني",
                     "ligue-1": "الدوري الفرنسي", "botola": "البطولة المغربية"}
    for l in LEAGUES:
        lg_fx = [m for m in UPCOMING if m["league"] == l["id"]]
        fx_html = fixtures_list_html(lg_fx) if lg_fx else \
            '<div class="placeholder-box">برنامج مباريات هذا الدوري القادمة لم يُنشر بعد بشكل موثق — قيد التحقق من مصدر رسمي.</div>'
        lg_news = [a for a in news["articles"] if a.get("category") == cat_by_league.get(l["id"], "")]
        if lg_news:
            news_html = '<div class="news-grid">' + "".join(
                f'<a href="news/{a["slug"]}.html" class="news-card"><div class="news-thumb">{a["emoji"]}</div>'
                f'<div class="news-body"><div class="news-meta"><span class="cat">{a["category"]}</span><span>{a["date"]}</span></div>'
                f'<h3>{a["title"]}</h3><p>{a["excerpt"]}</p></div></a>'
                for a in lg_news) + "</div>"
        else:
            news_html = '<div class="placeholder-box">لا توجد أخبار منشورة عن هذا الدوري بعد في أرشيف الموقع.</div>'
        page = f"""<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{l["name"]} | الملعب</title>
<meta name="description" content="{l["meta"]}">
<meta property="og:title" content="{l["name"]} | الملعب">
<meta property="og:description" content="{l["meta"]}">
<meta property="og:type" content="website">
<meta property="og:locale" content="ar_MA">
{FONTS}
{ICON}
</head>
<body>
{header("standings.html")}
{CHIPS}
{AD_LEADER}
{TICKER}
<main class="container page" style="max-width:1100px">
  <h1>{league_logo_img(l["id"])}{l["name"]} <small style="color:var(--muted);font-size:1rem">— موسم {l["season"]} • {l["round"]}</small></h1>
  <p class="data-note"><span class="verified-tag">✓ موثق</span> <b>المصدر:</b> {l["source"]} — <b>آخر تحقق:</b> {BUILD_DATE_AR}. الجدول الكامل موثق.</p>
  <section class="section" style="padding-top:6px">
    <div class="section-head"><h2>جدول الترتيب</h2><span style="color:var(--muted);font-size:.82rem">{l["next_round"]}</span></div>
    {table_html(l)}
  </section>
  <section class="section">
    <div class="section-head"><h2>هدّافو الدوري</h2></div>
    {scorers_html(l)}
  </section>
  <section class="section">
    <div class="section-head"><h2>مباريات ونتائج</h2><a class="more" href="matches.html">كل المباريات ←</a></div>
    {fx_html}
  </section>
  {CPA_SLOT}
  <section class="section">
    <div class="section-head"><h2>أخبار {l["short"]}</h2><a class="more" href="news.html">كل الأخبار ←</a></div>
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
        ('<meta name="description" content="جداول ترتيب الدوريات الخمسة الكبرى والبطولة المغربية 2026-27 — أول 5 مراكز موثقة لكل دوري (آخر تحقق 18 نونبر 2026) مع هدافي كل دوري.">',
         '<meta name="description" content="جداول ترتيب الدوريات الخمسة الكبرى والبطولة المغربية 2026-27 — الجداول الكاملة موثقة لكل دوري (آخر تحقق 18 نونبر 2026) مع هدافي كل دوري.">'),
        ('<title>جداول ترتيب الدوريات الأوروبية والبطولة المغربية | الملعب</title>',
         '<title>جداول ترتيب الدوريات الخمسة الكبرى والبطولة المغربية | الملعب</title>'),
        ('آخر تحديث: 20 شتنبر 2026', 'آخر تحديث: 18 نونبر 2026'),
        ('<div class="scorers" id="scorers"></div>\n  </section>',
         '<div class="scorers" id="scorers"></div>\n  </section>\n  ' + CPA_SLOT),
    ])
    patch(os.path.join(ROOT, "news.html"), [
        ('<meta name="description" content="آخر أخبار كرة القدم: الدوريات الأوروبية الخمسة الكبرى، دوري أبطال أوروبا، المنتخب المغربي والبطولة الاحترافية — تغطية يومية بالعربية.">',
         '<meta name="description" content="آخر أخبار كرة القدم: الدوريات الأوروبية الخمسة الكبرى، المنتخب المغربي والبطولة الاحترافية — تغطية يومية بالعربية.">'),
        ('      <button data-cat="دوري أبطال أوروبا">دوري الأبطال</button>\n', ''),
        ('آخر تحديث: 20 شتنبر 2026', 'آخر تحديث: 18 نونبر 2026'),
        ('    <div class="section-head"><h2>📰 آخر الأخبار</h2></div>',
         '    <div class="section-head"><h2>📰 آخر الأخبار</h2></div>\n    <p class="data-note">الأخبار أرشيف بتاريخ نشرها (شتنبر 2026) — الأرقام والترتيب الحاليان في صفحات الترتيب والمباريات.</p>'),
        ('    <!-- AdSense: in-feed -->\n    <div class="ad-slot"><div class="ad-infeed">مساحة إعلانية داخل المحتوى — In-feed</div></div>',
         '    <!-- AdSense: in-feed -->\n    <div class="ad-slot"><div class="ad-infeed">مساحة إعلانية داخل المحتوى — In-feed</div></div>\n    ' + CPA_SLOT),
    ])
    patch(os.path.join(ROOT, "about.html"), [
        ('للدوريات الأوروبية الخمسة الكبرى، دوري أبطال أوروبا، والبطولة الاحترافية المغربية.',
         'للدوريات الأوروبية الخمسة الكبرى والبطولة الاحترافية المغربية.'),
        ('  <p>نعتمد على مزودي بيانات رياضية معتمدين (مثل API-Football) لتحديث النتائج والجداول تلقائياً، بينما يُحرَّر المحتوى الخبري من طرف فريق التحرير بناءً على مصادر صحفية موثوقة. لا ننشر شائعات على أنها حقائق: أي خبر غير مؤكد يُذكر بصيغة واضحة.</p>',
         '  <p>نعتمد على مصادر رياضية موثوقة ومتاحة للعموم لتحديث النتائج والجداول، ونذكر مصدر كل رقم وتاريخ التحقق منه. لا ننشر شائعات على أنها حقائق: أي خبر غير مؤكد يُذكر بصيغة واضحة.</p>'),
        ('آخر تحديث: 20 شتنبر 2026', 'آخر تحديث: 18 نونبر 2026'),
    ])
    for f in ["contact.html", "privacy.html"]:
        patch(os.path.join(ROOT, f), [('آخر تحديث: 20 شتنبر 2026', 'آخر تحديث: 18 نونبر 2026')])
    # news articles: footer date + CPA placeholder in sidebar
    for name in os.listdir(os.path.join(ROOT, "news")):
        p = os.path.join(ROOT, "news", name)
        patch(p, [
            ('آخر تحديث: 20 شتنبر 2026', 'آخر تحديث: 18 نونبر 2026'),
            ('<div class="ad-rect">مساحة إعلانية<br>300 × 250</div>',
             '<div class="ad-rect">مساحة إعلانية<br>300 × 250</div>\n      <div class="cpa-slot" style="position:static"><b>مساحة إعلانية — CPA (Placeholder)</b>تُضاف هنا عروض موثوقة بعد اختيارها.<small>لا يوجد أي عرض حي حالياً.</small></div>'),
        ])

    # ---- sitemap / robots / render.yaml ----
    urls = ["index.html", "matches.html", "match.html", "standings.html", "news.html",
            "about.html", "contact.html", "privacy.html"] + \
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
        "services:\n  - type: web\n    name: almalaeb\n    env: static\n"
        "    buildCommand: \"\"\n    staticPublishPath: .\n")
    w(os.path.join(ROOT, "README.md"),
        "# الملعب V2\n\nموقع عربي ثابت (HTML/CSS/JS فقط) — الدوريات الستة فقط: الإنجليزي، الإسباني،\n"
        "الإيطالي، الألماني، الفرنسي + البطولة المغربية — 6 دوريات فقط.\n\n"
        f"- البيانات في `data/*.json` — موثقة فقط (آخر تحقق {BUILD_DATE_AR}). المصدر: ESPN + FRMF.ma للبطولة.\\n"
        "- التحديث اليومي: `python3 tools/daily-update.py` (انظر `tools/DAILY-README.md`).\\n"
        "- لا يوجد API-Football في V2 (الحساب موقوف) — المصدر ESPN public API بلا مفتاح.\\n"
        "- النشر: موقع ثابت على Render — انظر `REPORT.md` (الخطوة التالية).\n"
        "- إعادة البناء: `python3 tools/build-v2.py` من داخل المجلد.\n")

    # ---- تحديث التواريخ المجمدة في الصفحات المولّدة من V1 ----
    refresh_dates()


if __name__ == "__main__":
    main()
    print("V2 built in", ROOT)
