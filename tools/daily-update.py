#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Almalaeb V2 — التحديث اليومي للبيانات (ESPN public API — بلا مفتاح، بلا اشتراك).

المصدر: ESPN public API (site.api.espn.com + sports.core.api.espn.com).
يغطي الدوريات الأوروبية الخمسة (eng.1, esp.1, ita.1, ger.1, fra.1).
البطولة المغربية غير موجودة في ESPN إطلاقاً (mar.1 → 404) — تُدمج يدوياً من
data/botola-manual.json (انظر تعليمات التحديث اليدوي أسفل هذا الملف).

ما يفعله السكربت كل صباح (بتوقيت المغرب):
  1) يجلب مباريات اليوم + 4 أيام قادمة، ونتائج آخر 14 يوماً، من ESPN scoreboard.
  2) يجلب جدول كل دوري من سجلات الفرق (core API team record) — مرتب بالنقاط/فرق الأهداف.
  3) يجلب الهدافين (core API leaders) ويترجم الأسماء عبر data/player-names.json.
  4) يجلب تفاصيل كل نتيجة منتهية (إحصائيات + أحداث الأهداف + الملعب) من summary.
  5) يدمج البطولة من data/botola-manual.json.
  6) يتحقق من البيانات (عدد الصفوف، النقاط = 3×فوز + تعادل، لا قيم فارغة)،
     ثم يكتب data/leagues.json + data/fixtures.json بشكل ذري، ويعيد البناء
     عبر tools/build-v2.py.

  + النسخة الإنجليزية (MatchPulse) في نفس التشغيل: كل سجل يحمل أيضاً صيغته
    الإنجليزية (team_en / player_en / venue_en / time_utc / date_utc)،
    فيُكتب أيضاً data/leagues-en.json + data/fixtures-en.json (أوقات UTC
    لجمهور USA/UK/EU)، ويُعاد البناء عبر tools/build-en.py.
    --ar-dir / --en-dir يوجّهان الملفات لمجلدين مختلفين (تشغيل واحد يغذي
    الموقعين)؛ --no-build يكتب الملفات فقط بلا بناء.

قواعد السلامة (لا تُكسر أبداً):
  - لا يكتب رقماً لم يجلبه من ESPN أو من botola-manual.json.
  - عند فشل جلب أي دوري كامل: يخرج بخطأ (exit != 0) ويترك البيانات القديمة كما هي.
  - عند فشل تفاصيل مباراة واحدة (summary): تُحفظ النتيجة بلا إحصائيات + تحذير.
  - لا يخترع ترجمة عربية للاعب غير موجود في player-names.json: يعرض الاسم
    اللاتيني كما هو ويسجّل تحذيراً.

تعليمات التحديث اليدوي للبطولة (كل صباح، قبل تشغيل السكربت):
  افتح data/botola-manual.json وحدّث من جدول FRMF.ma (أو ويكيبيديا 2026–27
  Botola Pro المنقولة عن FRMF.ma): حقل updated (تاريخ اليوم)، والجدول الكامل
  (16 فريقاً)، والهدافين العشرة، ومباريات الجولة القادمة (التاريخ + التوقيت
  بتوقيت المغرب)، ونتائج الجولة الأخيرة. إن لم يتغير شيء، يكفي تحديث حقل
  updated. إن كان الملف أقدم من 3 أيام، يطبع السكربت تحذيراً واضحاً في الملخص.

التشغيل:
  cd ~/workspace/almalaeb-v2 && python3 tools/daily-update.py
  (الكـرون اليومي يُنشئه الوكيل الرئيسي — لا تُنشئه من هنا.)
"""
import json
import os
import re
import subprocess
import sys
import unicodedata
import urllib.request
import urllib.error
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timedelta, date

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, "data")
# توقيت المغرب: UTC+1 دائماً إلا في رمضان (UTC+0). تحذير: tzdata هذا الجهاز
# خاطئة للمغرب في 2026 (تعطي +00 في نونبر!) — لذلك لا نعتمد على ZoneInfo هنا.
# نوافذ رمضان (تقريبية — تُحدَّث سنوياً): 2026: 15 فبراير–22 مارس،
# 2027: 7 مارس–7 أبريل، 2028: 25 فبراير–27 مارس.
from datetime import timezone as _tz, timedelta as _td
_MOROCCO_PLUS1 = _tz(_td(hours=1))
_RAMADAN_UTC0 = [("2026-02-15", "2026-03-22"), ("2027-03-07", "2027-04-07"),
                 ("2028-02-25", "2028-03-27")]


def morocco_tz(d):
    iso = d.isoformat() if hasattr(d, "isoformat") else str(d)
    for a, b in _RAMADAN_UTC0:
        if a <= iso <= b:
            return _tz.utc
    return _MOROCCO_PLUS1


TZ = _MOROCCO_PLUS1
TODAY = datetime.now(_MOROCCO_PLUS1).date()
TODAY_ISO = TODAY.isoformat()
AR_MONTHS = ["يناير", "فبراير", "مارس", "أبريل", "مايو", "يونيو",
             "يوليوز", "غشت", "شتنبر", "أكتوبر", "نونبر", "دجنبر"]
AR_WEEKDAYS = ["الاثنين", "الثلاثاء", "الأربعاء", "الخميس", "الجمعة", "السبت", "الأحد"]

LEAGUES = [
    {"id": "premier-league", "espn": "eng.1", "rows": 20},
    {"id": "la-liga",       "espn": "esp.1", "rows": 20},
    {"id": "serie-a",       "espn": "ita.1", "rows": 20},
    {"id": "bundesliga",    "espn": "ger.1", "rows": 18},
    {"id": "ligue-1",       "espn": "fra.1", "rows": 18},
]
BOTOLA_ID = "botola"
FIX_WINDOW_DAYS = 4      # اليوم + 4 أيام (يغطي عطلة نهاية الأسبوع)
RES_WINDOW_DAYS = 14     # نتائج آخر 14 يوماً (آخر جولة مكتملة)
UA = {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AlmalaebV2-daily/1.0"}
SITE = "https://site.api.espn.com/apis/site/v2/sports/soccer"
CORE = "https://sports.core.api.espn.com/v2/sports/soccer"

WARNINGS = []


def warn(msg):
    WARNINGS.append(msg)
    print(f"  ⚠️  {msg}", file=sys.stderr)


def ar_date(iso):
    """2026-11-20 -> 'الجمعة 20 نونبر 2026' ; '20 نونبر' if short=True."""
    d = date.fromisoformat(iso) if isinstance(iso, str) else iso
    return f"{AR_WEEKDAYS[d.weekday()]} {d.day} {AR_MONTHS[d.month - 1]} {d.year}"


def ar_date_short(iso):
    d = date.fromisoformat(iso) if isinstance(iso, str) else iso
    return f"{d.day} {AR_MONTHS[d.month - 1]}"


def ar_range(d1, d2):
    """'21–23 نونبر 2026' أو '30 نونبر – 2 دجنبر 2026'."""
    a, b = date.fromisoformat(d1), date.fromisoformat(d2)
    if a.month == b.month and a.year == b.year:
        return f"{a.day}–{b.day} {AR_MONTHS[a.month - 1]} {a.year}"
    return f"{a.day} {AR_MONTHS[a.month - 1]} – {b.day} {AR_MONTHS[b.month - 1]} {b.year}"


# ------------------------------------------------- English (MatchPulse) ---
# One ESPN fetch feeds BOTH sites: every record below also carries its
# English form (team_en / player_en / venue_en / *_utc …) so main() can
# write data/leagues-en.json + data/fixtures-en.json in the same run.
# MatchPulse times are UTC (audience: USA/UK/Europe); Almalaeb times stay
# Morocco time (UTC+1, UTC+0 in Ramadan). Never invent an English name:
# teams come from data/logos.json, players keep their ESPN Latin spelling.
EN_MONTHS = ["January", "February", "March", "April", "May", "June",
             "July", "August", "September", "October", "November", "December"]
EN_WEEKDAYS = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday",
               "Saturday", "Sunday"]
LEAGUE_EN = {
    "premier-league": ("Premier League", "Premier League", "England"),
    "la-liga": ("La Liga", "La Liga", "Spain"),
    "serie-a": ("Serie A", "Serie A", "Italy"),
    "bundesliga": ("Bundesliga", "Bundesliga", "Germany"),
    "ligue-1": ("Ligue 1", "Ligue 1", "France"),
    "botola": ("Botola Pro", "Botola Pro", "Morocco"),
}
TODAY_UTC = datetime.now(_tz.utc).date()
TODAY_UTC_ISO = TODAY_UTC.isoformat()


def en_date(iso):
    """2026-11-20 -> 'Friday 20 November 2026'."""
    d = date.fromisoformat(iso) if isinstance(iso, str) else iso
    return f"{EN_WEEKDAYS[d.weekday()]} {d.day} {EN_MONTHS[d.month - 1]} {d.year}"


def en_date_short(iso):
    d = date.fromisoformat(iso) if isinstance(iso, str) else iso
    return f"{d.day} {EN_MONTHS[d.month - 1]}"


def en_range(d1, d2):
    """'21–23 November 2026' or '30 November – 2 December 2026'."""
    a, b = date.fromisoformat(d1), date.fromisoformat(d2)
    if a.month == b.month and a.year == b.year:
        return f"{a.day}–{b.day} {EN_MONTHS[a.month - 1]} {a.year}"
    return f"{a.day} {EN_MONTHS[a.month - 1]} – {b.day} {EN_MONTHS[b.month - 1]} {b.year}"


def morocco_offset_hours(d):
    """UTC offset of Morocco time on date d: +1, except Ramadan (0)."""
    return 0 if morocco_tz(d) == _tz.utc else 1


def morocco_to_utc(date_iso, time_str):
    """'2026-11-20','20:30' (Morocco) -> ('2026-11-20','19:30') UTC.
    Non-HH:MM times ('TBC') pass through unchanged."""
    if not time_str or not re.match(r"^\d{2}:\d{2}$", str(time_str)):
        return date_iso, time_str
    d = date.fromisoformat(date_iso)
    hh, mm = map(int, str(time_str).split(":"))
    dt = datetime(d.year, d.month, d.day, hh, mm) - _td(hours=morocco_offset_hours(d))
    return dt.date().isoformat(), dt.strftime("%H:%M")


def fetch(url, timeout=30):
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return json.load(r)


def https(u):
    return u.replace("http://", "https://")


# ------------------------------------------------------------------ maps ---
def load_json(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


LOGOS = load_json(os.path.join(DATA, "logos.json"))
PLAYER_NAMES = load_json(os.path.join(DATA, "player-names.json"))["names"]

STOP = {"fc", "afc", "acf", "ca", "as", "ac", "sc", "sv", "tsg", "rcd", "rc", "us",
        "cf", "cfc", "cd", "ud", "sd", "ss", "ssc", "losc", "estac", "sco", "fsv",
        "real", "club", "de", "la", "le", "di",
        "calcio", "fussball", "olympique", "stade", "ogc", "brestois",
        "alsace", "bc", "milano"}


def _norm(s):
    """تطبيع اسم فريق للمطابقة: إزالة التشكيل (Alavés→alaves)، أحرف صغيرة، حذف البادئات."""
    s = unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode()
    s = s.lower()
    s = re.sub(r"[^a-z0-9 ]", " ", s)
    return " ".join(t for t in s.split() if t not in STOP and not t.isdigit()).strip()


EN2AR = {}
EN2SLUG = {}
for _c in LOGOS["clubs"]:
    EN2AR[_norm(_c["en"])] = _c["ar"]
    EN2SLUG[_norm(_c["en"])] = _c["slug"]
# أسماء ESPN المختلفة جذرياً عن logos.json (Cologne=Köln، Hamburg=Hamburger…)
TEAM_ALIASES = {
    "cologne": "koln",
    "hamburg": "hamburger",
    "lyon": "lyonnais",
    "deportivo": "deportivo coruna",   # ESPN 'Deportivo' = ديبورتيفو لاكورونيا (وليس ألافيس)
    "internazionale": "inter milan",
    "inter": "inter milan",
    "mainz": "fsv mainz",
}
# حالات خاصة لا يطابقها التطبيع إطلاقاً
TEAM_AR_DIRECT = {"brest": "بريست"}
TEAM_SLUG_DIRECT = {"brest": "brest"}


def _resolve_team(espn_name):
    """اسم ESPN -> مفتاح التطبيع في logos.json (أو None)."""
    n = _norm(espn_name)
    if n in TEAM_AR_DIRECT:
        return None  # يُحلّ عبر TEAM_AR_DIRECT مباشرة
    if n in EN2AR:
        return n
    if n in TEAM_ALIASES and _norm(TEAM_ALIASES[n]) in EN2AR:
        return _norm(TEAM_ALIASES[n])
    # مطابقة جزئية وحيدة: الاسم المختصر جزء من اسم واحد فقط (athletic ⊂ athletic bilbao)
    cands = [k for k in EN2AR if k and n and (n in k or k in n)]
    if len(cands) == 1:
        return cands[0]
    return None


def team_ar(espn_name):
    n = _norm(espn_name)
    if n in TEAM_AR_DIRECT:
        return TEAM_AR_DIRECT[n]
    key = _resolve_team(espn_name)
    return EN2AR.get(key) if key else None


def team_slug(espn_name):
    n = _norm(espn_name)
    if n in TEAM_SLUG_DIRECT:
        return TEAM_SLUG_DIRECT[n]
    key = _resolve_team(espn_name)
    if key and key in EN2SLUG:
        return EN2SLUG[key]
    return re.sub(r"[^a-z0-9]+", "-", espn_name.lower()).strip("-")


def player_ar(latin_name):
    if latin_name in PLAYER_NAMES:
        return PLAYER_NAMES[latin_name]
    warn(f"لاعب بلا ترجمة عربية في data/player-names.json: {latin_name} — يُعرض باللاتينية")
    return latin_name


EN2EN = {}
for _c in LOGOS["clubs"]:
    EN2EN[_norm(_c["en"])] = _c["en"]


def team_en(espn_name):
    """Canonical English team name from data/logos.json; falls back to the
    ESPN display name itself (already English — never invented)."""
    key = _resolve_team(espn_name)
    if key and key in EN2EN:
        return EN2EN[key]
    if _norm(espn_name) in TEAM_AR_DIRECT:
        return espn_name  # e.g. 'Brest'
    return espn_name


def venue_en(espn_venue):
    """English venue name: the ESPN fullName as-is (already English)."""
    if not espn_venue:
        return "To be confirmed"
    return espn_venue


# الملاعب: الاسم الإنجليزي (ESPN) -> الاسم العربي المعروض (من بياناتنا الموثقة)
VENUES = {
    "Allianz Arena": "أليانز أرينا، ميونيخ",
    "Allianz Riviera": "أليانز ريفييرا، نيس",
    "Allianz Stadium": "أليانز ستاديوم، تورينو",
    "Anfield": "أنفيلد، ليفربول",
    "Stadio Olimpico": "الملعب الأولمبي، روما",
    "BayArena": "باي أرينا، ليفركوزن",
    "Borussia-Park": "بوروسيا بارك، مونشنغلادباخ",
    "San Siro": "سان سيرو، ميلانو",
    "San Mamés": "سان ماميس، بلباو",
    "St. James' Park": "سانت جيمس بارك، نيوكاسل",
    "Santiago Bernabéu": "سانتياغو برنابيو، مدريد",
    "Signal Iduna Park": "سيغنال إيدونا بارك، دورتموند",
    "Vitality Stadium": "فيتاليتي ستاديوم، بورنموث",
    "Villa Park": "فيلا بارك، برمنغهام",
    "Coventry Building Society Arena": "كوفنتري بيلدينغ سوسايتي أرينا، كوفنتري",
    "MKM Stadium": "ملعب MKM، هال",
    "WWK Arena": "ملعب WWK، أوغسبورغ",
    "Stadion An der Alten Försterei": "ملعب آلته فورستيري، برلين",
    "Stadio Artemio Franchi": "ملعب أرتيميو فرانكي، فلورنسا",
    "Etihad Stadium": "ملعب الاتحاد، مانشستر",
    "Stade Pierre-Mauroy": "ملعب بيير موروا، ليل",
    "Tottenham Hotspur Stadium": "ملعب توتنهام هوتسبير، لندن",
    "Gtech Community Stadium": "ملعب جيتك كوميونيتي، لندن",
    "Stadio Diego Armando Maradona": "ملعب دييغو أرماندو مارادونا، نابولي",
    "Gewiss Stadium": "ملعب غيويس، بيرغامو",
    "Stade de l'Aube": "ملعب لوب، تروا",
    "Stadio Luigi Ferraris": "ملعب لويجي فيراريس، جنوى",
    "MEWA Arena": "ملعب ميوا، ماينز",
    "Stade Vélodrome": "ملعب فيلودروم، مارسيليا",
    "Parc des Princes": "حديقة الأمراء، باريس",
    "Camp Nou": "كامب نو، برشلونة",
    "Emirates Stadium": "ملعب الإمارات، لندن",
    "Stamford Bridge": "ستامفورد بريدج، لندن",
    "London Stadium": "ملعب لندن",
    "Old Trafford": "أولد ترافورد، مانشستر",
    "Stadio Giuseppe Meazza": "سان سيرو، ميلانو",
    # ملاعب إضافية (من نتائج/مباريات نونبر 2026 — أسماء موثقة)
    "American Express Stadium": "ملعب أميكس، برايتون",
    "Balaidos": "بالايدوس، فيغو",
    "Craven Cottage": "كرافن كوتاج، لندن",
    "Decathlon Arena - Stade Pierre-Mauroy": "ملعب بيير موروا، ليل",
    "Deutsche Bank Park": "دويتشه بنك بارك، فرانكفورت",
    "El Sadar": "إل سادار، بامبلونا",
    "El Sardineros": "إل ساردينيرو، سانتاندير",
    "Elland Road": "إيلاند رود، ليدز",
    "Ennio Tardini": "ملعب إنيو تارديني، بارما",
    "Estadi Ciutat de València": "ملعب سيوتات دي فالنسيا، فالنسيا",
    "Estadio Coliseum": "ملعب كوليسيوم، خيتافي",
    "Estadio Martínez Valero": "ملعب مارتينيز فاليرو، إلتشي",
    "Estadio de Vallecas": "ملعب فاييكاس، مدريد",
    "Estadio de la Cerámica": "ملعب لا سيراميكا، فياريال",
    "Europa-Park Stadion": "ملعب أوروبا بارك، فرايبورغ",
    "Giuseppe Sinigaglia": "ملعب جوزيبي سينيغاليا، كومو",
    "Hill Dickinson Stadium": "ملعب هيل ديكنسون، ليفربول",
    "Home Deluxe Arena": "ملعب هوم ديلوكس أرينا، بادربورن",
    "La Rosaleda": "لا روزاليدا، مالقا",
    "MHPArena": "إم إتش بي أرينا، شتوتغارت",
    "Mapei Stadium": "ملعب مابي، ريجيو إميليا",
    "Mendizorrotza": "مينديزوروتزا، فيتوريا",
    "Mestalla Stadium": "ميستايا، فالنسيا",
    "New Balance Arena": "ملعب نيو بالانس أرينا، لايبزيغ",
    "Olimpico": "الملعب الأولمبي، روما",
    "Portman Road": "بورتمان رود، إيبسويتش",
    "PreZero Arena": "بريزيرو أرينا، سينسهايم",
    "RCDE Stadium": "ملعب آر سي دي إي، برشلونة",
    "Ramón Sánchez Pizjuán Stadium": "رامون سانشيز بيزخوان، إشبيلية",
    "Reale Arena": "ريالي أرينا، سان سيباستيان",
    "Red Bull Arena": "ريد بول أرينا، لايبزيغ",
    "Renato Dall'Ara": "ملعب ريناتو دالارا، بولونيا",
    "RheinEnergieStadion": "ملعب راين إنرجي، كولن",
    "Riyadh Air Metropolitano": "ملعب ميتروبوليتانو، مدريد",
    "Roazhon Park": "روازون بارك، رين",
    "Selhurst Park": "سيلهرست بارك، لندن",
    "Spotify Camp Nou": "كامب نو، برشلونة",
    "Stade Bollaert-Delelis": "ملعب بولارت ديليليس، لنس",
    "Stade Francis-Le Blé": "ملعب فرانسيس لو بليه، بريست",
    "Stade Jean Bouin": "ملعب جان بوان، باريس",
    "Stade Louis II": "ملعب لويس الثاني، موناكو",
    "Stade Marie-Marvingt": "ملعب ماري مارفينغ، لومان",
    "Stade Océane": "ملعب أوسيان، لوهافر",
    "Stade Raymond Kopa": "ملعب ريمون كوبا، أنجيه",
    "Stade de l'Abbé-Deschamps": "ملعب آبي ديشان، أوكسير",
    "Stade de la Meinau": "ملعب لامينو، ستراسبورغ",
    "Stade du Moustoir - Yves Allainmat": "ملعب موستوار، لوريان",
    "Stadio Olimpico Grande Torino": "الملعب الأولمبي الكبير، تورينو",
    "Stadio Pier Luigi Penzo": "ملعب بيير لويجي بينزو، البندقية",
    "Stadium Municipal de Toulouse": "الملعب البلدي، تولوز",
    "Stadium of Light": "ملعب النور، سندرلاند",
    "The City Ground": "سيتي غراوند، نوتنغهام",
    "The MKM Stadium": "ملعب MKM، هال",
    "U-Power Stadium": "ملعب يو باور، مونزا",
    "URSAPHARM-Arena an der Kaiserlinde": "ملعب أورسافارم أرينا، إلفرسبرغ",
    "Unipol Domus": "أونيبول دوموس، كالياري",
    "Veltins Arena": "فيلتينس أرينا، غيلسنكيرشن",
    "Volksparkstadion": "فولكسبارك شتاديون، هامبورغ",
    "Weserstadion": "فيزر شتاديون، بريمن",
}


def venue_ar(espn_venue):
    if not espn_venue:
        return "قيد التأكيد"
    if espn_venue in VENUES:
        return VENUES[espn_venue]
    low = espn_venue.lower()
    for k, v in VENUES.items():
        if k.lower() == low:
            return v
    return espn_venue


# حقوق البث في المغرب/الشرق الأوسط (معروفة وثابتة، ليست رقماً يُجلب يومياً)
CHANNEL_EU = "beIN Sports"
CHANNEL_BOTOLA = "Arryadia TNT"

# ------------------------------------------------------------- ESPN fetch --
def parse_event(ev, league_id, league_name):
    """حدث واحد من scoreboard -> قاموس مباراة في مخطط الموقع.
    يحمل القاموس أيضاً الصيغة الإنجليزية (home_en/away_en/venue_en/
    league_name_en/source_en + time_utc/date_utc) لملفات MatchPulse."""
    comp = ev["competitions"][0]
    cs = comp["competitors"]
    home = next(c for c in cs if c["homeAway"] == "home")
    away = next(c for c in cs if c["homeAway"] == "away")
    h_ar, a_ar = team_ar(home["team"]["displayName"]), team_ar(away["team"]["displayName"])
    if not h_ar or not a_ar:
        raise ValueError(f"فريق بلا اسم عربي: {home['team']['displayName']} / {away['team']['displayName']}")
    h_en, a_en = team_en(home["team"]["displayName"]), team_en(away["team"]["displayName"])
    league_name_en = LEAGUE_EN[league_id][0]
    venue_en_name = venue_en((comp.get("venue") or {}).get("fullName"))
    # التاريخ/الوقت بتوقيت المغرب (ESPN يعطي UTC؛ morocco_tz لأن tzdata الجهاز خاطئة)
    dt_utc = datetime.fromisoformat(ev["date"].replace("Z", "+00:00"))
    dt = dt_utc.astimezone(morocco_tz(dt_utc.date()))
    m = {
        "id": f"{team_slug(home['team']['displayName'])}-{team_slug(away['team']['displayName'])}-{dt.date().isoformat()}",
        "home": h_ar, "away": a_ar,
        "home_en": h_en, "away_en": a_en,
        "league": league_id, "league_name": league_name,
        "league_name_en": league_name_en,
        "date": dt.date().isoformat(),
        "date_utc": dt_utc.date().isoformat(),
        "source": f"ESPN (site.api.espn.com) — {ar_date_short(dt.date().isoformat())} {dt.year}",
        "source_en": f"ESPN (site.api.espn.com) — {en_date_short(dt_utc.date().isoformat())} {dt_utc.year}",
        "venue": venue_ar((comp.get("venue") or {}).get("fullName")),
        "venue_en": venue_en_name,
        "channel": CHANNEL_EU,
    }
    st = comp["status"]["type"]
    state, completed = st.get("state"), st.get("completed", False)
    if completed:
        # منتهية — ESPN يستخدم STATUS_FULL_TIME (وليس STATUS_FINAL)
        m["home_goals"] = int(home.get("score", 0))
        m["away_goals"] = int(away.get("score", 0))
        m["status"] = "finished"
        m["espn_event_id"] = ev["id"]
    elif state == "in":
        m["home_goals"] = int(home.get("score", 0))
        m["away_goals"] = int(away.get("score", 0))
        m["status"] = "live"
        m["minute"] = comp["status"].get("displayClock", "").replace("'", "")
        m["espn_event_id"] = ev["id"]
    elif state == "pre":
        m["time"] = dt.strftime("%H:%M")
        m["time_utc"] = dt_utc.strftime("%H:%M")
        m["status"] = "scheduled"
    else:
        # مؤجلة/ملغاة (STATUS_POSTPONED / STATUS_CANCELED…) — لا تُعرض كمباراة قادمة
        return None
    return m


def fetch_scoreboard_day(espn_code, day):
    url = f"{SITE}/{espn_code}/scoreboard?dates={day.strftime('%Y%m%d')}"
    return fetch(url).get("events", [])


def fetch_league_events(lg, old_league):
    """مباريات + نتائج + مباشر لدوري واحد في النوافذ المحددة."""
    days_fix = [TODAY + timedelta(days=i) for i in range(FIX_WINDOW_DAYS + 1)]
    days_res = [TODAY - timedelta(days=i) for i in range(1, RES_WINDOW_DAYS + 1)]
    events = []
    with ThreadPoolExecutor(max_workers=8) as ex:
        futs = {ex.submit(fetch_scoreboard_day, lg["espn"], d): d
                for d in days_fix + days_res}
        for fut in as_completed(futs):
            try:
                events.extend(fut.result())
            except Exception as e:
                raise RuntimeError(f"فشل جلب scoreboard {lg['espn']} يوم {futs[fut]}: {e}")
    upcoming, results, live = [], [], []
    seen = set()
    for ev in events:
        try:
            m = parse_event(ev, lg["id"], old_league["name"])
        except ValueError as e:
            warn(f"{lg['id']}: {e} — تُستبعد المباراة")
            continue
        if m is None:
            continue  # مؤجلة/ملغاة — لا تُعرض
        if m["id"] in seen:
            continue
        seen.add(m["id"])
        if m["status"] == "scheduled":
            upcoming.append(m)
        elif m["status"] == "finished":
            results.append(m)
        elif m["status"] == "live":
            live.append(m)
    upcoming.sort(key=lambda x: (x["date"], x.get("time", "")))
    results.sort(key=lambda x: (x["date"]), reverse=True)
    return upcoming, results, live


def fetch_standings(lg):
    """الجدول من سجلات الفرق (core API) — مرتب بالنقاط ثم فرق الأهداف ثم الأهداف."""
    teams = fetch(f"{CORE}/leagues/{lg['espn']}/seasons/2026/teams?lang=en&region=us&limit=30")["items"]

    def one(t):
        tid = t["$ref"].split("/teams/")[1].split("?")[0]
        team = fetch(f"{CORE}/leagues/{lg['espn']}/seasons/2026/teams/{tid}?lang=en&region=us")
        rec = fetch(https(team["record"]["$ref"]))
        item = rec["items"][0]
        st = {s["name"]: s["value"] for s in item["stats"]}
        ar = team_ar(team["displayName"])
        if not ar:
            raise ValueError(f"فريق بلا اسم عربي في الجدول: {team['displayName']}")
        return {"team": ar, "team_en": team_en(team["displayName"]),
                "p": int(st["gamesPlayed"]), "w": int(st.get("wins", 0)),
                "d": int(st["ties"]), "l": int(st["losses"]),
                "gf": int(st["pointsFor"]), "ga": int(st["pointsAgainst"]),
                "gd": int(st["pointDifferential"]), "pts": int(st["points"])}

    with ThreadPoolExecutor(max_workers=8) as ex:
        rows = list(ex.map(one, teams))
    rows.sort(key=lambda r: (-r["pts"], -r["gd"], -r["gf"], -r["w"]))
    for i, r in enumerate(rows, 1):
        r2 = {"pos": i}
        r2.update(r)
        rows[i - 1] = r2
    if len(rows) != lg["rows"]:
        raise RuntimeError(f"جدول {lg['id']}: {len(rows)} صفاً بدل {lg['rows']}")
    return rows


def fetch_scorers(lg):
    """الهدافون العشرة من core API leaders (يُحلّ $ref اللاعب والفريق)."""
    data = fetch(f"{CORE}/leagues/{lg['espn']}/seasons/2026/types/1/leaders?lang=en&region=us")
    leaders = None
    for cat in data.get("categories", []):
        if cat.get("name") == "goals":
            leaders = cat.get("leaders", [])
            break
    if not leaders:
        raise RuntimeError(f"لا قائمة هدافين من ESPN لـ {lg['id']}")
    def one(ld):
        ath = fetch(https(ld["athlete"]["$ref"]))
        team = fetch(https(ld["team"]["$ref"]))
        team_name = team_ar(team["displayName"])
        if not team_name:
            warn(f"{lg['id']}: فريق هداف بلا اسم عربي: {team['displayName']}")
            return None
        full = ath.get("fullName") or ath.get("displayName")
        return {"player": player_ar(full), "player_en": full,
                "team": team_name, "team_en": team_en(team["displayName"]),
                "goals": int(ld["value"])}
    with ThreadPoolExecutor(max_workers=8) as ex:
        out = [x for x in ex.map(one, leaders[:10]) if x]
    out.sort(key=lambda s: -s["goals"])
    return out[:10]


def fetch_match_details(lg_espn, match):
    """تفاصيل نتيجة منتهية: إحصائيات + أحداث الأهداف/البطاقات + الملعب + الحكم."""
    try:
        s = fetch(f"{SITE}/{lg_espn}/summary?event={match['espn_event_id']}")
    except Exception as e:
        warn(f"تعذّر جلب تفاصيل {match['home']} × {match['away']}: {e}")
        return
    stats = {}
    try:
        for side, key in ((0, "home"), (1, "away")):
            team_stats = s["boxscore"]["teams"][side]["statistics"]
            d = {x["name"]: x.get("displayValue") for x in team_stats}
            def num(name):
                v = d.get(name)
                if v is None:
                    return None
                return int(float(str(v).replace("%", "")))
            stats[f"possession_{key}"] = num("possessionPct")
            stats[f"shots_{key}"] = num("totalShots")
            stats[f"shots_on_target_{key}"] = num("shotsOnTarget")
            stats[f"corners_{key}"] = num("wonCorners")
        if all(v is not None for v in stats.values()):
            stats["source"] = f"ESPN (site.api.espn.com) — {ar_date_short(match['date'])} {match['date'][:4]}"
            stats["source_en"] = f"ESPN (site.api.espn.com) — {en_date_short(match['date'])} {match['date'][:4]}"
            match["stats"] = stats
    except Exception as e:
        warn(f"إحصائيات ناقصة لـ {match['home']} × {match['away']}: {e}")
    try:
        venue = (s.get("gameInfo") or {}).get("venue", {})
        if venue.get("fullName"):
            match["venue"] = venue_ar(venue["fullName"])
            match["venue_en"] = venue_en(venue["fullName"])
        officials = s.get("officials") or []
        if officials:
            match["referee"] = officials[0].get("displayName", "قيد التحقق")
    except Exception:
        pass
    try:
        evs = []
        for ke in s.get("keyEvents", []) or []:
            # الهدف = scoringPlay (علم ESPN نفسه) — أنواعه متعددة: goal،
            # goal---header، goal---penalty، penalty---scored…
            if not ke.get("scoringPlay"):
                continue
            parts = ke.get("participants") or []
            name = ""
            if parts:
                name = ((parts[0].get("athlete") or {}).get("displayName") or "")
            team_name = team_ar((ke.get("team") or {}).get("displayName", "")) or ""
            minute = (ke.get("clock") or {}).get("displayValue", "").replace("'", "")
            evs.append({"minute": minute,
                        "team": team_name,
                        "team_en": team_en((ke.get("team") or {}).get("displayName", "")),
                        "player": player_ar(name) if name else "",
                        "player_en": name,
                        "type": "هدف",
                        "type_en": "Goal"})  # كل أنواع الأهداف (goal / goal---header / goal---penalty…)
        if evs:
            match["events"] = evs
    except Exception as e:
        warn(f"أحداث ناقصة لـ {match['home']} × {match['away']}: {e}")


# ------------------------------------------------------------------ Botola --
def load_botola(old_league):
    """يدمج البطولة من data/botola-manual.json؛ عند أي مشكلة يُبقي القديم + تحذير."""
    path = os.path.join(DATA, "botola-manual.json")
    try:
        manual = load_json(path)
    except Exception as e:
        warn(f"botola-manual.json غير مقروء ({e}) — تُبقى بيانات البطولة القديمة")
        return old_league, [], []
    upd = manual.get("updated", "")
    try:
        age = (TODAY - date.fromisoformat(upd)).days
        if age > 3:
            warn(f"بيانات البطولة اليدوية قديمة ({upd} — منذ {age} أيام) — حدّث data/botola-manual.json")
    except Exception:
        warn("حقل updated في botola-manual.json غير صالح")
    if len(manual.get("table", [])) != 16 or len(manual.get("scorers", [])) != 10:
        warn("botola-manual.json ناقص (الجدول 16 / الهدافون 10) — تُبقى بيانات البطولة القديمة")
        return old_league, [], []
    league = dict(old_league)
    league["table"] = manual["table"]
    league["scorers"] = manual["scorers"]
    league["round"] = manual.get("round", old_league.get("round", ""))
    league["next_round"] = manual.get("next_round", old_league.get("next_round", ""))
    league["source"] = manual.get("source", old_league.get("source", ""))
    league["meta"] = (f"جدول ترتيب البطولة الاحترافية المغربية 2026-27: "
                      f"{manual['table'][0]['team']} متصدر بـ{manual['table'][0]['pts']} نقطة، "
                      f"{manual['table'][1]['team']} {manual['table'][1]['pts']}، "
                      f"{manual['table'][2]['team']} {manual['table'][2]['pts']} — "
                      f"{manual['scorers'][0]['player']} هداف البطولة بـ{manual['scorers'][0]['goals']} أهداف، "
                      f"مباريات {manual.get('next_round', '')} والنتائج.")
    fx = manual.get("fixtures", []) or []
    res = manual.get("results", []) or []
    for m in fx + res:
        m.setdefault("channel", CHANNEL_BOTOLA)
        m.setdefault("source", f"FRMF.ma / ويكيبيديا — {upd}")
    return league, fx, res


def _botola_fixture_en(m):
    """نسخة إنجليزية من مباراة بطولة (نسخة عميقة — لا تمسّ الأصل)."""
    import copy as _copy
    e = _copy.deepcopy(m)
    e["home"] = m.get("home_en") or m["home"]
    e["away"] = m.get("away_en") or m["away"]
    e["league_name"] = "Botola Pro"
    e["venue"] = m.get("venue_en") or "To be confirmed"
    t = m.get("time")
    if t and re.match(r"^\d{2}:\d{2}$", str(t)):
        d_utc, t_utc = morocco_to_utc(m["date"], t)
        e["date"], e["time"] = d_utc, t_utc
        e["id"] = re.sub(r"-\d{4}-\d{2}-\d{2}$", f"-{d_utc}", m["id"])
    else:
        e["time"] = "TBC"
    e["source"] = ("LNFP via h24info.ma (9 November 2026) — resumes 27 November; "
                   "exact kick-off times TBC")
    for k in ("home_en", "away_en", "venue_en", "league_name_en", "time_en"):
        e.pop(k, None)
    return e


def load_botola_en(old_league_en):
    """النسخة الإنجليزية من البطولة (من الحقول *_en في botola-manual.json)."""
    path = os.path.join(DATA, "botola-manual.json")
    try:
        manual = load_json(path)
    except Exception as e:
        if old_league_en is None:
            raise RuntimeError(f"botola-manual.json غير مقروء ({e}) ولا توجد بيانات بطولة إنجليزية قديمة — فشل مغلق")
        warn(f"botola-manual.json غير مقروء ({e}) — تُبقى بيانات البطولة الإنجليزية القديمة")
        return old_league_en, [], []
    if len(manual.get("table", [])) != 16 or len(manual.get("scorers", [])) != 10:
        if old_league_en is None:
            raise RuntimeError("botola-manual.json ناقص (الجدول 16 / الهدافون 10) ولا توجد بيانات بطولة إنجليزية قديمة — فشل مغلق")
        warn("botola-manual.json ناقص (الجدول 16 / الهدافون 10) — تُبقى بيانات البطولة الإنجليزية القديمة")
        return old_league_en, [], []
    if any("team_en" not in r for r in manual["table"]) or \
       any("player_en" not in s for s in manual["scorers"]):
        if old_league_en is None:
            raise RuntimeError("botola-manual.json بلا حقول *_en ولا توجد بيانات بطولة إنجليزية قديمة — فشل مغلق")
        warn("botola-manual.json بلا حقول *_en — تُبقى بيانات البطولة الإنجليزية القديمة")
        return old_league_en, [], []
    league = dict(old_league_en) if old_league_en else {"id": "botola", "season": "2026-27"}
    league["name"], league["short"], league["country"] = LEAGUE_EN["botola"]
    league["table"] = [
        {"pos": r["pos"], "team": r["team_en"], "p": r["p"], "w": r["w"],
         "d": r["d"], "l": r["l"], "gf": r["gf"], "ga": r["ga"], "gd": r["gd"],
         "pts": r["pts"],
         **({"deduction": r["deduction"]} if "deduction" in r else {})}
        for r in manual["table"]]
    league["scorers"] = [{"player": s["player_en"], "team": s["team_en"],
                          "goals": s["goals"]} for s in manual["scorers"]]
    league["round"] = manual.get("round_en", (old_league_en or {}).get("round", ""))
    league["next_round"] = manual.get("next_round_en", (old_league_en or {}).get("next_round", ""))
    league["source"] = manual.get("source_en", (old_league_en or {}).get("source", ""))
    league["meta"] = (f"Botola Pro 2026-27 table: {league['table'][0]['team']} lead with "
                      f"{league['table'][0]['pts']} points, {league['table'][1]['team']} "
                      f"{league['table'][1]['pts']}, {league['table'][2]['team']} "
                      f"{league['table'][2]['pts']} — {league['scorers'][0]['player']} is the top scorer "
                      f"with {league['scorers'][0]['goals']} goals; {league['next_round']} and results.")
    fx = [_botola_fixture_en(m) for m in (manual.get("fixtures", []) or [])]
    res = [_botola_fixture_en(m) for m in (manual.get("results", []) or [])]
    for m in fx + res:
        m.setdefault("channel", CHANNEL_BOTOLA)
    return league, fx, res

# -------------------------------------------------------------- validation --
def validate(leagues, fixtures):
    errs = []
    if len(leagues) != 6:
        errs.append(f"الدوريات: {len(leagues)} بدل 6")
    expected_rows = {"premier-league": 20, "la-liga": 20, "serie-a": 20,
                     "bundesliga": 18, "ligue-1": 18, "botola": 16}
    for lg in leagues:
        n = expected_rows.get(lg["id"])
        if len(lg.get("table", [])) != n:
            errs.append(f"{lg['id']}: الجدول {len(lg.get('table', []))} صفاً بدل {n}")
        for r in lg.get("table", []):
            expect_pts = 3 * r["w"] + r["d"] - r.get("deduction", 0)
            if r["pts"] != expect_pts:
                errs.append(f"{lg['id']} {r['team']}: النقاط {r['pts']} ≠ 3×{r['w']}+{r['d']}-خصم{r.get('deduction', 0)}")
            if r["p"] != r["w"] + r["d"] + r["l"] or r["gd"] != r["gf"] - r["ga"]:
                errs.append(f"{lg['id']} {r['team']}: حسابات الجدول غير متسقة")
            if any(v is None for v in r.values()):
                errs.append(f"{lg['id']} {r['team']}: قيمة فارغة في الجدول")
        if len(lg.get("scorers", [])) != 10:
            errs.append(f"{lg['id']}: الهدافون {len(lg.get('scorers', []))} بدل 10")
        for s in lg.get("scorers", []):
            if not s.get("player") or not s.get("team") or not s.get("goals"):
                errs.append(f"{lg['id']}: هداف ناقص: {s}")
    ids = set()
    for m in fixtures["upcoming"] + fixtures["results"] + fixtures["live"]:
        for k in ("home", "away", "league", "date"):
            if not m.get(k):
                errs.append(f"مباراة ناقصة {k}: {m.get('id')}")
        if m["id"] in ids:
            errs.append(f"مباراة مكررة: {m['id']}")
        ids.add(m["id"])
    for m in fixtures["upcoming"]:
        if not m.get("time"):
            errs.append(f"مباراة قادمة بلا توقيت: {m['id']}")
    for m in fixtures["results"]:
        if m.get("home_goals") is None or m.get("away_goals") is None:
            errs.append(f"نتيجة بلا أهداف: {m['id']}")
    if errs:
        raise RuntimeError("فشل التحقق:\n  - " + "\n  - ".join(errs))


AR2EN_TEAM = {c["ar"]: c["en"] for c in LOGOS["clubs"]}


def to_en_match(m):
    """AR match dict -> clean EN match dict (UTC times, English names).
    Works for EU matches (via *_en fields) and Botola matches (already EN)."""
    e = {"id": m["id"],
         "home": m.get("home_en") or m["home"],
         "away": m.get("away_en") or m["away"],
         "league": m["league"],
         "league_name": m.get("league_name_en") or LEAGUE_EN[m["league"]][0],
         "date": m.get("date_utc") or m["date"],
         "source": m.get("source_en") or m.get("source", ""),
         "venue": m.get("venue_en") or m.get("venue") or "To be confirmed",
         "channel": m.get("channel", ""),
         "status": m["status"]}
    # id carries the date: rebuild it with the UTC date for EN
    e["id"] = re.sub(r"-\d{4}-\d{2}-\d{2}$", f"-{e['date']}", m["id"])
    if m["status"] == "scheduled":
        e["time"] = m.get("time_utc") or m.get("time") or "TBC"
    if m["status"] in ("finished", "live"):
        e["home_goals"] = m.get("home_goals")
        e["away_goals"] = m.get("away_goals")
    if m["status"] == "live":
        e["minute"] = m.get("minute", "")
    if m.get("stats"):
        st = dict(m["stats"])
        st["source"] = m["stats"].get("source_en") or m["stats"].get("source", "")
        st.pop("source_en", None)
        e["stats"] = st
    if m.get("events"):
        e["events"] = [{"minute": ev.get("minute", ""),
                        "team": ev.get("team_en") or ev.get("team", ""),
                        "player": ev.get("player_en") or ev.get("player", ""),
                        "type": "Goal"} for ev in m["events"]]
    if m.get("referee"):
        e["referee"] = m["referee"]
    return e


# -------------------------------------------------------------------- main --
def main(ar_dir=None, en_dir=None, do_build=True):
    """ar_dir: أين تُكتب leagues.json/fixtures.json (افتراضياً data/ هنا).
    en_dir: أين تُكتب leagues-en.json/fixtures-en.json (افتراضياً data/ هنا).
    do_build: إعادة البناء عبر tools/build-en.py (الكرون قد يبني بنفسه)."""
    ar_dir = ar_dir or DATA
    en_dir = en_dir or DATA
    old_leagues = load_json(os.path.join(DATA, "leagues.json"))
    old_fx = load_json(os.path.join(DATA, "fixtures.json"))
    old_by_id = {l["id"]: l for l in old_leagues["leagues"]}
    try:
        old_en = load_json(os.path.join(en_dir, "leagues-en.json"))
        old_en_by_id = {l["id"]: l for l in old_en["leagues"]}
    except Exception:
        old_en_by_id = {}
    new_leagues = []
    new_leagues_en = []
    all_upcoming, all_results, all_live = [], [], []
    changes = []

    for lg in LEAGUES:
        old = old_by_id[lg["id"]]
        print(f"[{lg['id']}] جلب المباريات والنتائج من ESPN…")
        upcoming, results, live = fetch_league_events(lg, old)
        print(f"[{lg['id']}] جلب الجدول (سجلات الفرق)…")
        table = fetch_standings(lg)
        print(f"[{lg['id']}] جلب الهدافين…")
        scorers = fetch_scorers(lg)
        # تفاصيل النتائج (إحصائيات + أحداث) — فشل الواحدة لا يوقف التشغيل
        espn_code = lg["espn"]
        with ThreadPoolExecutor(max_workers=8) as ex:
            list(ex.map(lambda m: fetch_match_details(espn_code, m), results))
        for m in results + upcoming + live:
            m.pop("espn_event_id", None)
        # الجولة: عدد المباريات الملعوبة / الجولة القادمة من تواريخ المباريات
        played = max(r["p"] for r in table)
        lg_fx = [m for m in upcoming if m["league"] == lg["id"]]
        if lg_fx:
            d1, d2 = lg_fx[0]["date"], lg_fx[-1]["date"]
            next_round = f"الجولة {played + 1} — {ar_range(d1, d2)}"
        else:
            next_round = f"الجولة {played + 1} — التاريخ قيد التأكيد"
        top = table[:3]
        meta = (f"جدول ترتيب {old['name']} 2026-27: {top[0]['team']} في الصدارة "
                f"بـ{top[0]['pts']} نقطة، {top[1]['team']} {top[1]['pts']}، "
                f"{top[2]['team']} {top[2]['pts']} — {scorers[0]['player']} هداف الدوري "
                f"بـ{scorers[0]['goals']} أهداف، مباريات {next_round} والنتائج.")
        new_leagues.append({
            "id": lg["id"], "name": old["name"], "short": old["short"],
            "country": old["country"], "season": old.get("season", "2026-27"),
            "round": f"الجولة {played}",
            "next_round": next_round,
            "source": f"ESPN (site.api.espn.com + sports.core.api.espn.com) — {ar_date(TODAY_ISO)} — الهدافون: ESPN",
            "table": table, "scorers": scorers, "meta": meta,
        })
        # ---- النسخة الإنجليزية (MatchPulse) لنفس الدوري ----
        name_en, short_en, country_en = LEAGUE_EN[lg["id"]]
        if lg_fx:
            d1e, d2e = lg_fx[0]["date"], lg_fx[-1]["date"]
            next_round_en = f"Matchweek {played + 1} — {en_range(d1e, d2e)}"
        else:
            next_round_en = f"Matchweek {played + 1} — date to be confirmed"
        table_en = [{"pos": r["pos"], "team": r.get("team_en") or r["team"],
                     "p": r["p"], "w": r["w"], "d": r["d"], "l": r["l"],
                     "gf": r["gf"], "ga": r["ga"], "gd": r["gd"], "pts": r["pts"]}
                    for r in table]
        scorers_en = [{"player": s.get("player_en") or s["player"],
                       "team": s.get("team_en") or s["team"],
                       "goals": s["goals"]} for s in scorers]
        meta_en = (f"{name_en} 2026-27 table: {table_en[0]['team']} lead with "
                   f"{table_en[0]['pts']} points, {table_en[1]['team']} {table_en[1]['pts']}, "
                   f"{table_en[2]['team']} {table_en[2]['pts']} — {scorers_en[0]['player']} is the top scorer "
                   f"with {scorers_en[0]['goals']} goals; {next_round_en} and results.")
        new_leagues_en.append({
            "id": lg["id"], "name": name_en, "short": short_en,
            "country": country_en, "season": old.get("season", "2026-27"),
            "round": f"Matchweek {played}",
            "next_round": next_round_en,
            "source": f"ESPN (site.api.espn.com + sports.core.api.espn.com) — {en_date(TODAY_ISO)} — Top scorers: ESPN",
            "table": table_en, "scorers": scorers_en, "meta": meta_en,
        })
        all_upcoming += upcoming
        all_results += results
        all_live += live
        # ملخص التغييرات مقابل القديم
        old_top = [(r["team"], r["pts"]) for r in old["table"][:3]]
        new_top = [(r["team"], r["pts"]) for r in table[:3]]
        if old_top != new_top:
            changes.append(f"{lg['id']}: الصدارة {old_top} ← {new_top}")
        old_sc = [(s["player"], s["goals"]) for s in old["scorers"][:3]]
        new_sc = [(s["player"], s["goals"]) for s in scorers[:3]]
        if old_sc != new_sc:
            changes.append(f"{lg['id']}: الهدافون {old_sc} ← {new_sc}")

    # البطولة (يدوي)
    print("[botola] دمج البيانات اليدوية…")
    bot_league, bot_fx, bot_res = load_botola(old_by_id[BOTOLA_ID])
    bot_league_en, bot_fx_en, bot_res_en = load_botola_en(old_en_by_id.get(BOTOLA_ID))
    new_leagues.append(bot_league)
    new_leagues_en.append(bot_league_en)
    # EN lists first (EU matches only — before Botola AR fixtures are added)
    all_upcoming_en = [to_en_match(m) for m in all_upcoming]
    all_results_en = [to_en_match(m) for m in all_results]
    all_live_en = [to_en_match(m) for m in all_live]
    all_upcoming += [m for m in bot_fx if m.get("status") != "finished"]
    all_results += [m for m in bot_fx if m.get("status") == "finished"] + bot_res
    all_upcoming_en += [m for m in bot_fx_en if m.get("status") != "finished"]
    all_results_en += [m for m in bot_fx_en if m.get("status") == "finished"] + bot_res_en

    # ترتيب الدوريات كما في الموقع
    order = ["premier-league", "la-liga", "serie-a", "bundesliga", "ligue-1", "botola"]
    new_leagues.sort(key=lambda l: order.index(l["id"]))
    new_leagues_en.sort(key=lambda l: order.index(l["id"]))
    all_upcoming.sort(key=lambda x: (x["date"], x.get("time", "")))
    all_results.sort(key=lambda x: x["date"], reverse=True)
    all_upcoming_en.sort(key=lambda x: (x["date"], x.get("time", "")))
    all_results_en.sort(key=lambda x: x["date"], reverse=True)
    tomorrow = (TODAY + timedelta(days=1)).isoformat()
    tomorrow_utc = (TODAY_UTC + timedelta(days=1)).isoformat()
    today_fx = [m for m in all_upcoming if m["date"] == TODAY_ISO]
    tomorrow_fx = [m for m in all_upcoming if m["date"] == tomorrow]
    today_fx_en = [m for m in all_upcoming_en if m["date"] == TODAY_UTC_ISO]
    tomorrow_fx_en = [m for m in all_upcoming_en if m["date"] == tomorrow_utc]
    next_day = all_upcoming[0]["date"] if all_upcoming else None
    next_day_en = all_upcoming_en[0]["date"] if all_upcoming_en else None
    if today_fx:
        note = (f"{ar_date(TODAY_ISO)}: {len(today_fx)} مباراة اليوم في الدوريات الستة. "
                f"الأوقات بتوقيت المغرب (UTC+1).")
    elif next_day:
        note = (f"{ar_date(TODAY_ISO)}: لا مباريات اليوم في الدوريات الستة. "
                f"العودة {ar_date(next_day)} ({len([m for m in all_upcoming if m['date'] == next_day])} مباريات). "
                f"الأوقات بتوقيت المغرب (UTC+1).")
    else:
        note = f"{ar_date(TODAY_ISO)}: لا مباريات قادمة مسجلة. الأوقات بتوقيت المغرب (UTC+1)."
    if today_fx_en:
        note_en = (f"{en_date(TODAY_UTC_ISO)}: {len(today_fx_en)} matches today in the six leagues. "
                   f"All times UTC.")
    elif next_day_en:
        note_en = (f"{en_date(TODAY_UTC_ISO)}: no matches today in the six leagues. "
                   f"Back {en_date(next_day_en)} ({len([m for m in all_upcoming_en if m['date'] == next_day_en])} matches). "
                   f"All times UTC.")
    else:
        note_en = f"{en_date(TODAY_UTC_ISO)}: no upcoming matches scheduled. All times UTC."

    new_leagues_doc = {
        "updated": TODAY_ISO,
        "leagues": new_leagues,
        "note": f"الجداول الكاملة موثقة لكل دوري (آخر تحقق {ar_date(TODAY_ISO)}). المصدر: ESPN + FRMF.ma للبطولة.",
    }
    new_fx_doc = {
        "updated": TODAY_ISO,
        "today_date": TODAY_ISO,
        "tomorrow_date": tomorrow,
        "note": note,
        "live": all_live,
        "today": today_fx,
        "tomorrow": tomorrow_fx,
        "upcoming": all_upcoming,
        "results": all_results[:60],
    }
    new_leagues_doc_en = {
        "updated": TODAY_UTC_ISO,
        "leagues": new_leagues_en,
        "note": f"Full tables verified for every league (last checked {en_date(TODAY_UTC_ISO)}). Source: ESPN + FRMF.ma for Botola Pro.",
    }
    new_fx_doc_en = {
        "updated": TODAY_UTC_ISO,
        "today_date": TODAY_UTC_ISO,
        "tomorrow_date": tomorrow_utc,
        "note": note_en,
        "live": all_live_en,
        "today": today_fx_en,
        "tomorrow": tomorrow_fx_en,
        "upcoming": all_upcoming_en,
        "results": all_results_en[:60],
    }
    validate(new_leagues, new_fx_doc)
    validate(new_leagues_en, new_fx_doc_en)

    # كتابة ذرية + إعادة البناء (مع استرجاع النسخ القديمة عند فشل البناء)
    # الملفات الأربعة: AR (leagues/fixtures) + EN (leagues-en/fixtures-en)
    writes = [(os.path.join(ar_dir, "leagues.json"), new_leagues_doc),
              (os.path.join(ar_dir, "fixtures.json"), new_fx_doc),
              (os.path.join(en_dir, "leagues-en.json"), new_leagues_doc_en),
              (os.path.join(en_dir, "fixtures-en.json"), new_fx_doc_en)]
    backups = {}
    for p, _ in writes:
        try:
            backups[p] = open(p, encoding="utf-8").read()
        except FileNotFoundError:
            backups[p] = None
    try:
        for p, doc in writes:
            os.makedirs(os.path.dirname(p), exist_ok=True)
            tmp = p + ".tmp"
            with open(tmp, "w", encoding="utf-8") as f:
                json.dump(doc, f, ensure_ascii=False, indent=2)
            os.replace(tmp, p)
        if do_build:
            print("إعادة البناء: python3 tools/build-en.py …")
            r = subprocess.run([sys.executable, os.path.join(ROOT, "tools", "build-en.py")],
                               cwd=ROOT, capture_output=True, text=True, timeout=600)
            if r.returncode != 0:
                raise RuntimeError(f"فشل البناء:\n{r.stdout}\n{r.stderr}")
    except Exception:
        for p, content in backups.items():
            if content is None:
                try:
                    os.remove(p)
                except FileNotFoundError:
                    pass
            else:
                with open(p, "w", encoding="utf-8") as f:
                    f.write(content)
        raise

    # ------------------------------------------------------------- summary --
    print()
    print(f"✅ التحديث اليومي اكتمل — {ar_date(TODAY_ISO)}")
    print(f"   المصدر: ESPN public API (بلا مفتاح) + البطولة يدوياً (data/botola-manual.json)")
    print(f"   مباريات اليوم: {len(today_fx)} | غداً: {len(tomorrow_fx)} | "
          f"قادمة ({FIX_WINDOW_DAYS + 1} أيام): {len(all_upcoming)} | "
          f"نتائج (آخر {RES_WINDOW_DAYS} يوماً): {len(new_fx_doc['results'])} | مباشرة الآن: {len(all_live)}")
    print(f"   نتائج بإحصائيات: {sum(1 for m in new_fx_doc['results'] if m.get('stats'))} | "
          f"بأحداث أهداف: {sum(1 for m in new_fx_doc['results'] if m.get('events'))}")
    print(f"   EN (MatchPulse, UTC): اليوم {len(today_fx_en)} | غداً {len(tomorrow_fx_en)} | "
          f"قادمة {len(all_upcoming_en)} | نتائج {len(new_fx_doc_en['results'])} | مباشرة {len(all_live_en)}")
    if changes:
        print("   تغييرات عن أمس:")
        for c in changes:
            print(f"   - {c}")
    else:
        print("   لا تغيير في الصدارة ولا في أول 3 هدافين عن أمس.")
    if WARNINGS:
        print(f"   تحذيرات ({len(WARNINGS)}):")
        for w in WARNINGS:
            print(f"   - {w}")
    else:
        print("   بلا تحذيرات.")
    return 0


if __name__ == "__main__":
    import argparse
    _ap = argparse.ArgumentParser(description="Almalaeb + MatchPulse daily update (ESPN, no key)")
    _ap.add_argument("--no-build", action="store_true",
                     help="write the 4 data files but do not run tools/build-en.py")
    _ap.add_argument("--ar-dir", default=None,
                     help="where to write leagues.json/fixtures.json (default: this repo's data/)")
    _ap.add_argument("--en-dir", default=None,
                     help="where to write leagues-en.json/fixtures-en.json (default: this repo's data/)")
    _a = _ap.parse_args()
    try:
        sys.exit(main(ar_dir=_a.ar_dir, en_dir=_a.en_dir, do_build=not _a.no_build))
    except Exception as e:
        print(f"❌ فشل التحديث اليومي — البيانات القديمة لم تُمس:\n{e}", file=sys.stderr)
        sys.exit(1)
