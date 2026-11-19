#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""MatchPulse — one-off transformer: tools/build-v2.py (Arabic) -> tools/build-en.py.

Applies, longest-match first:
  1) data-name maps (teams/players/venues/months/weekdays/leagues/countries)
     from data/logos.json, data/player-names.json and daily-update.py VENUES.
  2) a hand-written UI dictionary (Arabic string -> English string).
  3) structural code edits (BASE, lang/dir, EN data files, logos by EN name,
     Inter font, CPA_SLOT -> live OFFERS section, render.yaml name, …).
Then reports every line that still contains Arabic, for manual fixing.
Run: python3 tools/make-build-en.py   (from inside matchpulse/)
"""
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "tools"))
import importlib.util
_spec = importlib.util.spec_from_file_location("du", os.path.join(ROOT, "tools", "daily-update.py"))
du = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(du)

AR = re.compile(r"[\u0600-\u06FF\u0750-\u077F\u08A0-\u08FF]")

# ------------------------------------------------------------------ maps ---
logos = json.load(open(os.path.join(ROOT, "data", "logos.json"), encoding="utf-8"))
TEAM = {c["ar"]: c["en"] for c in logos["clubs"]}
TEAM.update({"الوداد": "Wydad", "الرجاء": "Raja", "سيتي": "City",
             "أتلتيكو": "Atlético", "إنتر": "Inter", "مانشستر": "Manchester"})
players = json.load(open(os.path.join(ROOT, "data", "player-names.json"), encoding="utf-8"))["names"]
PLAYER = {v: k for k, v in players.items()}
PLAYER.update({"رومولو": "Rômulo", "ت. ماباسا": "Tshegofatso Mabasa",
               "حمزة الواستي": "Hamza El Wasti",
               "عبد الرزاق النقوس": "Abderrazak Ennakouss"})

CITY = {"ميونيخ": "Munich", "نيس": "Nice", "تورينو": "Turin", "ليفربول": "Liverpool",
        "روما": "Rome", "ليفركوزن": "Leverkusen", "مونشنغلادباخ": "Mönchengladbach",
        "ميلانو": "Milan", "بلباو": "Bilbao", "نيوكاسل": "Newcastle", "مدريد": "Madrid",
        "دورتموند": "Dortmund", "بورنموث": "Bournemouth", "برمنغهام": "Birmingham",
        "كوفنتري": "Coventry", "هال": "Hull", "أوغسبورغ": "Augsburg", "برلين": "Berlin",
        "فلورنسا": "Florence", "مانشستر": "Manchester", "ليل": "Lille", "لندن": "London",
        "نابولي": "Naples", "بيرغامو": "Bergamo", "تروا": "Troyes", "جنوى": "Genoa",
        "ماينز": "Mainz", "مارسيليا": "Marseille", "باريس": "Paris", "برشلونة": "Barcelona",
        "برايتون": "Brighton", "فيغو": "Vigo", "بامبلونا": "Pamplona",
        "سانتاندير": "Santander", "ليدز": "Leeds", "بارما": "Parma",
        "فالنسيا": "Valencia", "خيتافي": "Getafe", "إلتشي": "Elche",
        "فياريال": "Villarreal", "فرايبورغ": "Freiburg", "كومو": "Como",
        "بادربورن": "Paderborn", "مالقا": "Málaga", "شتوتغارت": "Stuttgart",
        "ريجيو إميليا": "Reggio Emilia", "فيتوريا": "Vitoria", "لايبزيغ": "Leipzig",
        "إيبسويتش": "Ipswich", "سينسهايم": "Sinsheim", "إشبيلية": "Seville",
        "سان سيباستيان": "San Sebastián", "بولونيا": "Bologna", "كولن": "Cologne",
        "رين": "Rennes", "سندرلاند": "Sunderland", "نوتنغهام": "Nottingham",
        "مونزا": "Monza", "إلفرسبرغ": "Elversberg", "كالياري": "Cagliari",
        "غيلسنكيرشن": "Gelsenkirchen", "هامبورغ": "Hamburg", "بريمن": "Bremen",
        "لنس": "Lens", "بريست": "Brest", "موناكو": "Monaco", "لومان": "Le Mans",
        "لوهافر": "Le Havre", "أنجيه": "Angers", "أوكسير": "Auxerre",
        "ستراسبورغ": "Strasbourg", "لوريان": "Lorient", "تولوز": "Toulouse",
        "البندقية": "Venice", "إنجلترا": "England", "مونتجويك": "Montjuïc"}
VENUE = {}
for _en, _ar in du.VENUES.items():
    if "،" in _ar:
        _name, _city = _ar.split("،", 1)
        _city = _city.strip()
        VENUE[_ar] = f"{_en}, {CITY.get(_city, _city)}"
    else:
        VENUE[_ar] = _en
VENUE.update({
    "ملعب الاتحاد": "Etihad Stadium",
    "مانشستر، إنجلترا": "Manchester, England",
})
# Venue NAME map: build-v2.py venues use a Latin comma + (Arabic city | English
# team) after the name, e.g. "أليانز أرينا, ميونيخ" / "ملعب لوب, ESTAC Troyes".
# Map the Arabic name part -> English name; CITY (below) handles the suffix.
VENUE_NAME = {}
for _en, _ar in du.VENUES.items():
    _name = _ar.split("،", 1)[0].strip()
    VENUE_NAME[_name] = _en
VENUE_NAME.update({
    "ملعب Tottenham Hotspur هوتسبير": "Tottenham Hotspur Stadium",
    "كامب نو": "Camp Nou",
    "ملعب لويس كومبانيس الأولمبي": "Estadi Olímpic Lluís Companys",
})

MONTHS = {"يناير": "January", "فبراير": "February", "مارس": "March",
          "أبريل": "April", "مايو": "May", "يونيو": "June", "يوليوز": "July",
          "غشت": "August", "شتنبر": "September", "أكتوبر": "October",
          "نونبر": "November", "دجنبر": "December"}
WEEKDAYS = {"الاثنين": "Monday", "الثلاثاء": "Tuesday", "الأربعاء": "Wednesday",
            "الخميس": "Thursday", "الجمعة": "Friday", "السبت": "Saturday",
            "الأحد": "Sunday"}
LEAGUE = {"الدوري الإنجليزي الممتاز": "Premier League",
          "الدوري الإنجليزي": "Premier League",
          "الدوري الإسباني": "La Liga",
          "الدوري الإيطالي": "Serie A",
          "الدوري الألماني": "Bundesliga",
          "الدوري الفرنسي": "Ligue 1",
          "البطولة الاحترافية المغربية": "Botola Pro",
          "البطولة المغربية": "Botola Pro",
          "البطولة": "Botola Pro",
          "البريميرليغ": "Premier League", "الليغا": "La Liga",
          "الكالتشيو": "Serie A", "البوندسليغا": "Bundesliga",
          "الليغ 1": "Ligue 1",
          "إنجلترا": "England", "إسبانيا": "Spain", "إيطاليا": "Italy",
          "ألمانيا": "Germany", "فرنسا": "France", "المغرب": "Morocco"}

# ------------------------------------------------------- UI dictionary ------
# Longer strings first — applied sorted by length, so "الملعب" is replaced
# before "لعب", "التسديدات على المرمى" before "التسديدات", etc.
UI = {
    "الملعب V2 — بيانات احتياطية موثقة ({BUILD_DATE_AR})، تُستخدم فقط إذا تعذّر تحميل data/*.json":
        "MatchPulse — verified fallback data ({BUILD_DATE_EN}), used only if data/*.json cannot be loaded",
    "الملعب V2 — main.js: فلتر صارم: 6 دوريات فقط، بلا محاكاة، بلا مسابقات أخرى":
        "MatchPulse — main.js: strict filter: 6 leagues only, no simulation, no other competitions",
    "الملعب V2 — matches.js: تبويبات حقيقية من data/fixtures.json فقط. بلا محاكاة.":
        "MatchPulse — matches.js: real tabs from data/fixtures-en.json only. No simulation.",
    "الملعب V2 — match.js: صفحة تفاصيل المباراة (?id=) — بيانات موثقة فقط، والباقي Placeholder صريح":
        "MatchPulse — match.js: match detail page (?id=) — verified data only, the rest is an explicit placeholder",
    "الملعب V2 — standings.js: 6 دوريات فقط": "MatchPulse — standings.js: 6 leagues only",
    "الملعب V2 — home.js: الرئيسية تُبقي رسالة التوقف الدولي (Hero ثابت في HTML)":
        "MatchPulse — home.js: the homepage keeps the international-break message (static hero in HTML)",
    "الملعب V2 builder — rebuilds ~/workspace/almalaeb-v2 from V1 data + VERIFIED data only.":
        "MatchPulse builder — rebuilds ~/workspace/matchpulse from EN data + VERIFIED data only.",
    "إصلاحات التشريح 18 نونبر 2026: إخفاء الإعلانات الفارغة + شارات الحالة + تبويبات المباراة":
        "Teardown fixes 18 November 2026: hide empty ads + status badges + match tabs",
    "النتائج المباشرة تظهر هنا فقط من مصدر بيانات حي موثوق. حالياً لا يوجد مصدر حي مربوط (API-Football موقوف) — الصفحة تعرض المباريات المبرمجة الموثقة والنتائج الأخيرة فقط، بدون محاكاة.":
        "Live results appear here only from a trusted live data source. No live source is connected right now — this page shows verified scheduled fixtures and the latest results only, no simulation.",
    "الأخبار أرشيف بتاريخ نشرها (شتنبر 2026) — الأرقام والترتيب الحاليان في صفحات الترتيب والمباريات.":
        "News is archived by publication date (September 2026) — current numbers and tables are on the tables and fixtures pages.",
    "الأخبار أرشيف بتاريخ نشرها (شتنبر 2026) — الأرقام الحالية تجدها في صفحات الترتيب والمباريات.":
        "News is archived by publication date (September 2026) — current numbers and tables are on the tables and fixtures pages.",
    "ملاحظة: مباراة الوداد–وداد تمارة حُسمت 3–0 للوداد بقرار LNFP في 07 نونبر 2026 (لاعب غير مؤهل)، وخصم نقطة واحدة من وداد تمارة":
        "Note: Wydad vs WS Témara was awarded 3–0 to Wydad by LNFP decision on 7 November 2026 (ineligible player), with one point deducted from WS Témara",
    "برنامج مباريات هذا الدوري القادمة لم يُنشر بعد بشكل موثق — قيد التحقق من مصدر رسمي.":
        "This league's upcoming fixture list has not been published in verified form yet — pending verification from an official source.",
    "لا توجد قائمة هدافين موثقة لهذا الدوري بعد — تُضاف فور التحقق من مصدر رسمي.":
        "No verified top-scorer list for this league yet — it will be added once verified from an official source.",
    "لا توجد أخبار منشورة عن هذا الدوري بعد في أرشيف الموقع.":
        "No news about this league in the site archive yet.",
    "التشكيلتان الرسميتان غير موثقتين بعد — تُنشران قبل انطلاق المباراة بساعة من مصدر رسمي.":
        "The official lineups are not verified yet — they are published one hour before kick-off from an official source.",
    "سجل المواجهات المباشرة بين الفريقين غير موثق بعد — يُضاف من مصدر رسمي.":
        "The head-to-head record between the two teams is not verified yet — it will be added from an official source.",
    "الإحصائيات غير متوفرة بعد لهذه المباراة.":
        "Statistics are not available for this match yet.",
    "تُعرض هنا (الاستحواذ، التسديدات، الركنيات) فور توثيقها من مصدر رسمي.":
        "They will appear here (possession, shots, corners) once verified from an official source.",
    "لا توجد أحداث موثقة بعد لهذه المباراة (أهداف، بطاقات، تبديلات).":
        "No verified events for this match yet (goals, cards, substitutions).",
    "تُضاف الأحداث بعد توثيقها من مصدر رسمي.":
        "Events will be added once verified from an official source.",
    "الملعب — مباريات اليوم والنتائج المباشرة، جداول ترتيب الدوري الإنجليزي والإسباني والإيطالي والألماني والفرنسي والبطولة المغربية، وآخر الأخبار بالعربية. آخر تحديث:":
        "MatchPulse — today's fixtures and live results, tables for the Premier League, La Liga, Serie A, Bundesliga, Ligue 1 and Botola Pro, and the latest news in English. Last updated:",
    "جداول ترتيب الدوريات الخمسة الكبرى والبطولة المغربية 2026-27 — الجداول الكاملة موثقة لكل دوري (آخر تحقق 18 نونبر 2026) مع هدافي كل دوري.":
        "2026-27 league tables for Europe's five major leagues and Botola Pro — full tables verified for every league (last checked 18 November 2026) with each league's top scorers.",
    "مباريات اليوم وغداً والقادمة والنتائج من الدوريات الخمسة الكبرى والبطولة المغربية. آخر تحديث:":
        "Today's, tomorrow's and upcoming fixtures plus results from Europe's five major leagues and Botola Pro. Last updated:",
    "موقعك المغربي لمتابعة كرة القدم: نتائج مباشرة، جداول الترتيب، وآخر الأخبار من الدوريات الأوروبية الخمسة الكبرى والبطولة المغربية.":
        "Your home for football: live results, league tables and the latest news from Europe's five major leagues and Botola Pro.",
    "آخر أخبار كرة القدم: الدوريات الأوروبية الخمسة الكبرى، المنتخب المغربي والبطولة الاحترافية — تغطية يومية بالعربية.":
        "Latest football news: Europe's five major leagues, the Morocco national team and Botola Pro — daily coverage in English.",
    "مباريات اليوم، ترتيب الدوريات الخمسة الكبرى والبطولة المغربية، وآخر الأخبار.":
        "Today's fixtures, tables for Europe's five major leagues and Botola Pro, and the latest news.",
    "موقع عربي لمتابعة مباريات ونتائج وترتيب الدوريات الأوروبية الخمسة الكبرى والبطولة المغربية.":
        "Follow fixtures, results and tables for Europe's five major leagues and Botola Pro.",
    "تفاصيل المباراة: النتيجة، الأحداث، الإحصائيات، التشكيلتان والمواجهات المباشرة — الملعب.":
        "Match details: score, events, statistics, lineups and head-to-head — MatchPulse.",
    "للدوريات الأوروبية الخمسة الكبرى، دوري أبطال أوروبا، والبطولة الاحترافية المغربية.":
        "for Europe's five major leagues and Botola Pro.",
    "مباريات الدوريات الخمسة الكبرى والبطولة المغربية":
        "fixtures of Europe's five major leagues and Botola Pro",
    "مباريات الدوريات الستة": "fixtures of the six leagues",
    "الدوريات الخمسة الكبرى والبطولة المغربية": "Europe's five major leagues and Botola Pro",
    "الدوريات الأوروبية الخمسة الكبرى والبطولة المغربية": "Europe's five major leagues and Botola Pro",
    "الدوريات الأوروبية الخمسة الكبرى": "Europe's five major leagues",
    "للدوريات الأوروبية الخمسة الكبرى والبطولة المغربية — آخر تحقق:":
        "for the five major European leagues and Botola Pro — last checked:",
    "الأوقات بتوقيت المغرب (UTC+1).": "All times UTC.",
    "الأوقات بتوقيت المغرب (UTC+1)": "All times UTC",
    "بتوقيت المغرب (UTC+1)": "UTC",
    "بتوقيت المغرب": "UTC",
    "الجداول الكاملة موثقة لكل دوري (آخر تحقق {ar_date(CHECKED)}). المصدر: ESPN + FRMF.ma للبطولة.":
        "Full tables verified for every league (last checked {en_date(CHECKED)}). Source: ESPN + FRMF.ma for Botola Pro.",
    "الجدول الكامل موثق لكل دوري.": "The full table is verified for every league.",
    "الجدول الكامل موثق.": "The full table is verified.",
    "الجداول الكاملة موثقة لكل دوري": "Full tables verified for every league",
    "أول 5 مراكز — الجدول الكامل في صفحة الدوري — آخر تحقق:": "Top 5 — full table on the league page — last checked:",
    "موسم ${l.season || \"2026-27\"} — ${l.round || \"\"}": "Season ${l.season || \"2026-27\"} — ${l.round || \"\"}",
    "جدول ترتيب الدوري الإنجليزي الممتاز 2026-27:": "Premier League 2026-27 table:",
    "جدول ترتيب الدوري الإسباني 2026-27:": "La Liga 2026-27 table:",
    "جدول ترتيب الدوري الإيطالي 2026-27:": "Serie A 2026-27 table:",
    "جدول ترتيب الدوري الألماني 2026-27:": "Bundesliga 2026-27 table:",
    "جدول ترتيب الدوري الفرنسي 2026-27:": "Ligue 1 2026-27 table:",
    "جدول ترتيب البطولة الاحترافية المغربية 2026-27:": "Botola Pro 2026-27 table:",
    "آخر تحديث: {BUILD_DATE_AR}": "Last updated: {BUILD_DATE_EN}",
    "آخر تحقق: {BUILD_DATE_AR}": "Last checked: {BUILD_DATE_EN}",
    "آخر تحقق {BUILD_DATE_AR}": "Last checked {BUILD_DATE_EN}",
    "آخر تحديث:": "Last updated:",
    "آخر تحقق:": "Last checked:",
    "آخر تحقق": "Last checked",
    "آخر تحديث": "Last updated",
    "لا مباريات مباشرة الآن — القادمة:": "No live matches right now — coming up:",
    "لا توجد مباريات مبرمجة في الدوريات الستة حالياً": "No fixtures scheduled in the six leagues right now",
    "لا توجد مباريات مبرمجة حالياً.": "No fixtures scheduled right now.",
    "لا توجد مباريات قادمة مسجلة.": "No upcoming fixtures scheduled.",
    "لا توجد مباريات قادمة مسجلة حالياً.": "No upcoming fixtures scheduled right now.",
    "لا توجد نتائج مسجلة.": "No results recorded.",
    "لا توجد مباريات اليوم": "No matches today",
    "لا توجد مباريات غداً": "No matches tomorrow",
    "لا مباريات قادمة مسجلة حالياً.": "No upcoming fixtures scheduled right now.",
    "جارٍ تحميل المباريات القادمة…": "Loading upcoming fixtures…",
    "جارٍ التحميل…": "Loading…",
    "مباريات اليوم: لا مباريات في الدوريات الستة": "Today's matches: no matches in the six leagues",
    "مباريات اليوم: {_count_txt(today_n)} في الدوريات الستة": "Today's matches: {_count_txt(today_n)} in the six leagues",
    "مباريات اليوم والنتائج المباشرة | الملعب": "Today's fixtures & live results | MatchPulse",
    "مباريات اليوم — نتائج مباشرة | الملعب": "Today's fixtures — live results | MatchPulse",
    "تفاصيل المباراة | الملعب": "Match details | MatchPulse",
    "الملعب | مباريات اليوم، نتائج مباشرة، ترتيب الدوريات وآخر الأخبار":
        "MatchPulse | Today's fixtures, live scores, league tables & latest news",
    "الملعب | نتائج مباشرة وأخبار كرة القدم": "MatchPulse | Live scores & football news",
    "جداول ترتيب الدوريات الأوروبية والبطولة المغربية | الملعب":
        "League tables — Europe & Botola Pro | MatchPulse",
    "مباريات اليوم:": "Today's matches:",
    "شاهد مباريات اليوم ←": "See today's matches →",
    "شاهد المباريات القادمة ←": "See upcoming fixtures →",
    "كل المباريات ←": "All fixtures →",
    "الجدول الكامل ←": "Full table →",
    "كل الأخبار ←": "All news →",
    "الجداول الكاملة ←": "Full tables →",
    "← العودة إلى كل المباريات": "← Back to all fixtures",
    "← العودة إلى المباريات": "← Back to fixtures",
    "المباراة غير موجودة": "Match not found",
    "الرابط غير صحيح أو المباراة غير مدرجة في الدوريات الستة.":
        "The link is wrong or the match is not in the six leagues.",
    "مباراة قادمة —": "Upcoming match —",
    "المرجو إدخال بريد إلكتروني صحيح.": "Please enter a valid email address.",
    "شكراً! تم تسجيل اشتراكك بنجاح. ⚽": "Thanks! Your subscription is confirmed. ⚽",
    "مساحة إعلانية — Leaderboard 970×250": "Ad space — Leaderboard 970×250",
    "مساحة إعلانية داخل المحتوى — In-feed": "In-feed ad space",
    "مساحة إعلانية للهواتف": "Ad space for mobile",
    "مساحة إعلانية<br>300 × 250": "Ad space<br>300 × 250",
    "مساحة إعلانية": "Ad space",
    "لا يوجد أي عرض حي حالياً.": "No live offers right now.",
    "تُضاف هنا عروض موثوقة بعد اختيارها.": "Trusted offers will be added here after selection.",
    "مساحة إعلانية — CPA (Placeholder)": "Sponsored offers",
    "لا مباريات": "No matches",
    "مباراة واحدة": "1 match",
    "مباراتان": "2 matches",
    "{n} مباريات": "{n} matches",
    "⚽ مباريات اليوم": "⚽ Today's matches",
    "⏸️ لا مباريات اليوم": "⏸️ No matches today",
    "⏭️ القادمة": "⏭️ Upcoming",
    "📅 غداً": "📅 Tomorrow",
    "📅 اليوم": "📅 Today",
    "🗓️ كل القادمة": "🗓️ All upcoming",
    "✅ النتائج الأخيرة": "✅ Latest results",
    "⚽ مباريات الدوريات الستة": "⚽ Fixtures of the six leagues",
    "تفاصيل المباراة": "Match details",
    "مباريات اليوم": "Today's matches",
    "المباريات القادمة": "Upcoming fixtures",
    "جدول الترتيب": "League table",
    "جداول الترتيب الكاملة": "Full league tables",
    "هدّافو الدوري": "Top scorers",
    "جداول الترتيب": "League tables",
    "آخر الأخبار": "Latest news",
    "مباريات ونتائج": "Fixtures & results",
    "المباريات": "Fixtures",
    "الترتيب": "Tables",
    "الأخبار": "News",
    "الرئيسية": "Home",
    "القائمة": "Menu",
    "مباشر": "LIVE",
    "● مباشر": "● LIVE",
    "انتهت": "Full time",
    "لم تبدأ بعد": "Not started yet",
    "قيد التحقق": "To be confirmed",
    "التوقيت قيد التأكيد": "Kick-off time TBC",
    "التاريخ قيد التأكيد": "date to be confirmed",
    "قيد التأكيد": "TBC",
    "الاستحواذ %": "Possession %",
    "التسديدات على المرمى": "Shots on target",
    "التسديدات": "Shots",
    "الركنيات": "Corners",
    "الأحداث": "Events",
    "الإحصائيات": "Statistics",
    "التشكيلة": "Lineups",
    "المواجهات": "Head-to-head",
    "الملعب:": "Stadium:",
    "الحكم:": "Referee:",
    "القناة الناقلة:": "TV channel:",
    "التوقيت:": "Kick-off:",
    "المصدر:": "Source:",
    "✓ موثق": "✓ Verified",
    "الفريق": "Team",
    "لعب": "P",
    "فاز": "W",
    "تعادل": "D",
    "خسر": "L",
    "فرق": "GD",
    "نقاط": "Pts",
    "شعار الدوري": "League logo",
    "شعار {team}": "Logo of {team}",
    "شعار ${esc}": "Logo of ${esc}",
    "العودة": "Back",
    "غداً": "Tomorrow",
    "اليوم": "Today",
    "القادمة": "Upcoming",
    "كل القادمة": "All upcoming",
    "النتائج الأخيرة": "Latest results",
    "من نحن": "About us",
    "اتصل بنا": "Contact",
    "سياسة الخصوصية": "Privacy policy",
    "أقسام الموقع": "Sections",
    "معلومات": "Info",
    "مصادر المباريات:": "Fixture sources:",
    "في الصدارة بـ": "lead with ",
    "متصدر بـ": "lead with ",
    "ودورتموند متساويان بـ21 نقطة": "and Dortmund level on 21 points",
    "هداف الدوري بـ": "top scorer with ",
    "هداف البطولة بـ": "top scorer with ",
    "هدفاً": "goals",
    "الهدافون:": "Top scorers:",
    "مطابقة مع": "cross-checked with",
    "عطلة نهاية الأسبوع 21–23 نونبر — اليوم الدقيق قيد التأكيد":
        "weekend of 21–23 November — exact day TBC",
    "المباراة المقبلة لبرشلونة — التوقيت قيد التأكيد":
        "Barcelona's next match — kick-off time TBC",
    "(المباراة المقبلة لريال مدريد — التوقيت قيد التأكيد)":
        "(Real Madrid's next match — kick-off time TBC)",
    "منشور فيسبوك FAFG": "Facebook post FAFG",
    "وخصم نقطة واحدة من وداد تمارة": "with one point deducted from WS Témara",
    "الهدافون": "Top scorers",
    "لعبت": "played",
    "تقرير": "report",
    "كرة القدم": "football",
    "مباريات": "fixtures",
    "مباراة": "match",
    "نقطة": "points",
    "أهداف": "goals",
    "الملعب V2": "MatchPulse",
    "الملعب": "MatchPulse",
    "،": ",",
    "؛": ";",
    "؟": "?",
    "موسم": "season",
    "للاعب غير مؤهل": "for an ineligible player",
    "لاعب غير مؤهل": "ineligible player",
    "بقرار LNFP في": "by LNFP decision on",
    "حُسمت": "was awarded",
    "الدوري": "league",
    "الأولمبي": "Olympic",
    "الملعب الأولمبي": "Stadio Olimpico",
    "جميع الحقوق محفوظة.": "All rights reserved.",
    "البيانات لأغراض إخبارية": "Data for information only",
    "يفضّل data/*.json (يكتبها tools/daily-update.py) على البيانات المضمّنة.":
        "Prefers data/*.json (written by tools/daily-update.py) over the embedded data.",
    "إن لم توجد الملفات أو كانت ناقصة، تبقى البيانات المضمّنة كاحتياطي.":
        "If the files are missing or incomplete, the embedded data stays as a fallback.",
    "كتلة البطل + شريط الأيام في الرئيسية — من بيانات اليوم/غداً/القادمة.":
        "Hero block + day strip on the homepage — from today/tomorrow/upcoming data.",
    "يحدّث التواريخ المجمدة ('آخر تحديث: …' / 'آخر تحقق …') في الصفحات المولّدة من ملفات V1 (الترتيب، الدوريات، الأخبار…) — بلا لمس مقالات news/ (تواريخها تاريخية).":
        "Updates frozen dates ('Last updated: …' / 'Last checked …') in pages generated from V1 files (tables, leagues, news…) — without touching news/ articles (their dates are historical).",
    "تحديث التواريخ المجمدة في الصفحات المولّدة من V1":
        "Update frozen dates in pages generated from V1",
    "موقع عربي ثابت (HTML/CSS/JS فقط) — الدوريات الستة فقط: الإنجليزي، الإسباني،":
        "Static site in English (HTML/CSS/JS only) — the six leagues only: English, Spanish,",
    "الإيطالي، الألماني، الفرنسي + البطولة المغربية — 6 دوريات فقط.":
        "Italian, German, French + Botola Pro — 6 leagues only.",
    "التحديث اليومي: `python3 tools/daily-update.py` (انظر `tools/DAILY-README.md`).":
        "Daily update: `python3 tools/daily-update.py` (see `tools/DAILY-README.md`).",
    "لا يوجد API-Football في V2 (الحساب موقوف) — المصدر ESPN public API بلا مفتاح.":
        "No API-Football (account suspended) — source: ESPN public API, no key.",
    "النشر: موقع ثابت على Render — انظر `REPORT.md` (الخطوة التالية).":
        "Publishing: static site on Render — see `REPORT.md`.",
    "إعادة البناء: `python3 tools/build-v2.py` من داخل المجلد.":
        "Rebuild: `python3 tools/build-en.py` from inside the folder.",
    "البيانات في `data/*.json` — موثقة فقط (آخر تحقق {BUILD_DATE_AR}). المصدر: ESPN + FRMF.ma للبطولة.":
        "Data in `data/*.json` — verified only (last checked {BUILD_DATE_EN}). Source: ESPN + FRMF.ma for Botola Pro.",
    "أول 5 مراكز موثقة لكل دوري": "top 5 verified for every league",
    "جداول ترتيب الدوريات الخمسة الكبرى والبطولة المغربية | الملعب":
        "League tables — Europe's five major leagues & Botola Pro | MatchPulse",
    " | الملعب": " | MatchPulse",
    "— موسم ": "— Season ",
    "لا مباريات مباشرة الآن": "No live matches right now",
    "دوري أبطال أوروبا": "Champions League",
    "build-v2.py": "build-en.py",
    "almalaeb-v2": "matchpulse",
    "والوداد": "and Wydad",
    "والرجاء": "and Raja",
    "والنتائج": "and results",
    "ملاحظة:": "Note:",
    "للوداد": "to Wydad",
    "وخصم": "with",
    "نقطة واحدة": "one point",
    "حتى": "up to",
    "ويكيبيديا": "Wikipedia",
    "واحدة": "one",
    "من": "from",
    "و": "and",
    "آخر النتائج": "Latest results",
    "في الدوريات الستة": "in the six leagues",
    "الدوريات الستة": "the six leagues",
    "لا توجد مباريات مبرمجة يوم": "No fixtures scheduled on",
    "للدوريات الأوروبية الخمسة": "for the five European leagues",
    "للبطولة المغربية": "for Botola Pro",
    "جداول ترتيب الدوريات الخمسة الكبرى والبطولة المغربية 2026-27":
        "2026-27 league tables for Europe's five major leagues and Botola Pro",
    "مع هدافي كل دوري": "with each league's top scorers",
    "اليوم الدقيق": "exact day",
    'أخبار {l["short"]}': '{l["short"]} news',
    "النتائج": "results",
    "المباراة": "match",
    "المباشرة": "live",
    "مباشرة": "live",
    "الدوريات": "leagues",
    "الأوروبية": "European",
    "الخمسة": "five",
    "الكبرى": "major",
    "هداف": "top scorer",
    "دوري الأبطال": "Champions League",
    "المنتخب المغربي": "the Morocco national team",
    "تغطية يومية بالعربية": "daily coverage in English",
    "آخر أخبار": "Latest news",
    "والبطولة الاحترافية المغربية": "and Botola Pro",
    "كريس كافانا": "Chris Kavanagh",
    "أو": "or",
    "تواريخ ديناميكية": "Dynamic dates",
    "للتحديث اليومي": "for the daily update",
    "تاريخ البناء المعروض في التذييلات": "Build date shown in footers",
    "يُحدَّث": "updated",
    "في": "in",
    "بيانات": "data",
    "يكتبها التحديث اليومي": "written by the daily update",
    "الشعارات": "Logos",
    "تُقرأ": "read",
    "يُعرض": "displayed",
    "أبداً": "ever",
    "ملفات محلية": "local files",
    "فريق بلا شعار موثق": "a team without a verified logo",
    "اسمه نصاً فقط": "its name as text only",
    "لا صورة مكسورة": "no broken image",
    "فريق بلا شعار": "a team without a logo",
    "يظهر نصاً فقط": "shows text only",
    "الشريط المتحرك": "Ticker",
    "فقط": "only",
    "لا دوريات غامضة": "no obscure leagues",
    "بلا تواريخ مكتوبة": "no hardcoded dates",
    "يحدّث التواريخ المجمدة": "Updates frozen dates",
    "في الصفحات المولّدة": "in the generated pages",
    "ملفات V1": "V1 files",
    "بلا لمس": "without touching",
    "مقالات": "articles",
    "تواريخها تاريخية": "their dates are historical",
    "يفضّل": "Prefers",
    "على البيانات المضمّنة": "over the embedded data",
    "على": "on",
    "نعتمد على مصادر رياضية موثوقة ومتاحة للعموم لتحديث النتائج والجداول، ونذكر مصدر كل رقم وتاريخ التحقق منه.":
        "We rely on trusted, publicly available sports sources to update results and tables, and we cite the source and check date for every number.",
    "لا ننشر شائعات على أنها حقائق: أي خبر غير مؤكد يُذكر بصيغة واضحة.":
        "We do not publish rumours as facts: any unconfirmed news is stated clearly.",
    "نعتمد على": "We rely on",
    "مزودي بيانات رياضية معتمدين": "trusted sports data providers",
    "مثل": "such as",
    "لتحديث": "to update",
    "الجداول": "tables",
    "تلقائياً": "automatically",
    "بينما": "while",
    "يُحرَّر": "is written",
    "المحتوى الخبري": "the news content",
    "طرف": "by",
    "فريق التحرير": "the editorial team",
    "بناءً على": "based on",
    "مصادر صحفية موثوقة": "trusted press sources",
    "بيانات المباريات اليوم/غداً/المباشرة": "Today/tomorrow/live fixtures data",
    "أي": "any",
    "والبطولة الاحترافية": "and Botola Pro",
    "والجداول": "and tables",
}



# ---------------------------------------------------------- transform ------
def _apply_plain(text, mapping):
    for k in sorted(mapping, key=len, reverse=True):
        if k and k in text:
            text = text.replace(k, mapping[k])
    return text

def _apply_bounded(text, mapping):
    """Replace whole words only: a key never matches inside a longer word
    (so 'كومو' can't corrupt 'جياكومو', 'لوريان' can't corrupt 'فلوريان',
    'الأحد' can't corrupt 'الأحداث', 'اليوم' can't corrupt 'اليومي')."""
    for k in sorted(mapping, key=len, reverse=True):
        if not k:
            continue
        pat = ""
        if k[0].isalnum():
            pat += r"(?<![\w])"
        pat += re.escape(k)
        if k[-1].isalnum():
            pat += r"(?![\w])"
        text = re.sub(pat, lambda m: mapping[k], text)
    return text

QUOTED = {"لعب": "P", "فاز": "W", "تعادل": "D", "خسر": "L",
          "فرق": "GD", "نقاط": "Pts"}

def _sanitize(mapping):
    """ASCII apostrophes in a translated value would terminate the
    single-quoted string literals of build-v2.py (e.g. venue='Stade de l'Aube').
    Use the typographic apostrophe U+2019 instead — renders identically."""
    return {k: v.replace("'", "\u2019") for k, v in mapping.items()}

def transform(src):
    for _m in (VENUE, VENUE_NAME, TEAM, PLAYER, LEAGUE, MONTHS, WEEKDAYS, CITY):
        _m.update(_sanitize(_m))
    _ui = _sanitize(UI)
    # 1) regex patterns for round names
    src = re.sub(r"مباريات الجولة (\d+)", r"Matchweek \1 fixtures", src)
    src = re.sub(r"الجولة (\d+)", r"Matchweek \1", src)
    src = src.replace("الجولة", "Matchweek")
    # 2) UI multi-word phrases FIRST (plain, longest first) — they contain
    #    words the maps would otherwise corrupt ("المغرب" inside a phrase, …)
    ui_long = {k: v for k, v in _ui.items()
               if (" " in k or k in ("،", "؛", "؟")) and k not in QUOTED}
    src = _apply_plain(src, ui_long)
    # 3) data-name maps, whole-word only
    for m in (VENUE, VENUE_NAME, TEAM, PLAYER, LEAGUE, MONTHS, WEEKDAYS, CITY):
        src = _apply_bounded(src, m)
    # 4) UI single words, whole-word only
    ui_short = {k: v for k, v in _ui.items() if k not in ui_long and k not in QUOTED}
    src = _apply_bounded(src, ui_short)
    # 4b) conjunction "و" attached to a Latin word (" وrenderfoot.com")
    src = re.sub(r" و(?=[A-Za-z])", " and", src)
    # 4c) "بـ15" (with + number) -> "with 15"
    src = re.sub(r"بـ(\d)", r"with \1", src)
    # 5) table headers: quoted strings AND <th>…</th> cells
    for k, v in QUOTED.items():
        src = re.sub(r"(['\"])" + re.escape(k) + r"\1", r"\1" + v + r"\1", src)
        src = re.sub(r"(?<=[>\"'])" + re.escape(k) + r"(?=[<\"'])", v, src)
    return src

# ------------------------------------------------------------- offers ------
OFFERS_CODE = '''
# --- MatchPulse CPA offers (live, from data/offers.json — CPAlead) ---------
OFFERS = json.load(open(os.path.join(ROOT, "data", "offers.json"), encoding="utf-8"))["offers"]

def offers_html():
    """Sponsored offers section (#ad) — rendered on homepage, league, tables,
    news and offers pages. Links are the exact CPAlead tracking URLs."""
    cards = []
    for o in OFFERS:
        cards.append(f"""
    <a class="offer-card" href="{o["url"]}" target="_blank" rel="nofollow sponsored noopener">
      <div class="offer-name">{o["name"]}</div>
      <div class="offer-payout">{o["payout"]}</div>
      <div class="offer-meta">{o["geo"]} &middot; {o["device"]}</div>
      <div class="offer-cta">Claim offer &rarr;</div>
    </a>""")
    return f"""
<section class="offers-section" id="offers">
  <h2>🎁 Free offers &amp; rewards <span class="ad-label">#ad</span></h2>
  <p class="offers-note">Sponsored offers — we may earn a commission if you sign up. Available in the listed countries only. No betting, no dating, no popups.</p>
  <div class="offers-grid">{''.join(cards)}
  </div>
</section>"""

def offers_page_html():
    rows = []
    for o in OFFERS:
        cap = (" &middot; <strong>Daily cap:</strong> " + str(o["cap"])) if o.get("cap") and o["cap"] != "No daily cap" else ""
        rows.append(f"""
    <div class="offer-detail">
      <h3>{o["name"]}</h3>
      <p><strong>Payout:</strong> {o["payout"]} &middot; <strong>Countries:</strong> {o["geo"]} &middot; <strong>Devices:</strong> {o["device"]}{cap}</p>
      <p>{o.get("blurb", "")}</p>
      <a class="btn offer-btn" href="{o["url"]}" target="_blank" rel="nofollow sponsored noopener">{o.get("cta", "Claim this offer")} &rarr;</a>
    </div>""")
    tpl = """<!DOCTYPE html>
<html lang="en" dir="ltr">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Free offers &amp; rewards | MatchPulse</title>
<meta name="description" content="Free sponsored offers for MatchPulse readers: free VPN for Windows, CapCut Pro trial, surveys and more. #ad">
<link rel="canonical" href="{BASE}/offers.html">
<link rel="icon" href="assets/logo.svg" type="image/svg+xml">
<link rel="stylesheet" href="assets/css/style.css">
</head>
<body>
{header}
<main class="wrap page">
  <h1>🎁 Free offers &amp; rewards <span class="ad-label">#ad</span></h1>
  <p class="offers-note">Sponsored offers — we may earn a commission if you sign up. Available in the listed countries only.</p>
  {rows}
</main>
{footer}
<script src="assets/js/data-fallback.js"></script>
<script src="assets/js/main.js"></script>
</body>
</html>"""
    return tpl.replace("{rows}", "".join(rows))
'''

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
/* Offers section (live CPA offers) */
.offers-section { margin: 28px 0; }
.offers-section h2 { font-size: 1.25rem; }
.ad-label { font-size: 11px; color: #64748b; border: 1px solid var(--line); border-radius: 6px; padding: 1px 6px; vertical-align: middle; }
.offers-note { color: #64748b; font-size: 13px; }
.offers-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap: 12px; }
.offer-card { display: block; border: 1px solid var(--line); border-radius: 12px; padding: 14px; background: var(--card); text-decoration: none; color: inherit; }
.offer-card:hover { border-color: var(--accent); }
.offer-name { font-weight: 800; }
.offer-payout { font-size: 1.1rem; font-weight: 800; color: var(--accent); margin: 4px 0; }
.offer-meta { font-size: 12px; color: #64748b; }
.offer-cta { margin-top: 8px; font-weight: 700; }
.offer-detail { border: 1px solid var(--line); border-radius: 12px; padding: 16px; margin: 14px 0; background: var(--card); }
.offer-btn { display: inline-block; margin-top: 8px; }
.offers-teaser { border: 1px solid var(--line); border-radius: 12px; padding: 12px 14px; margin: 14px 0; background: var(--card); font-weight: 700; }
.offers-teaser a { text-decoration: none; color: inherit; }
'''

# --------------------------------------------------------- structural ------
def structural(src):
    def rep(old, new, required=True):
        nonlocal src
        if old not in src:
            if required:
                print(f"  !! structural pattern NOT FOUND: {old[:90]!r}")
            return
        src = src.replace(old, new)

    # --- identity / base ---
    rep('BASE = "https://almalaeb.onrender.com"',
        'BASE = "https://matchpulse.onrender.com"')
    # --- dates ---
    rep('_AR_MONTHS', '_EN_MONTHS')
    rep('_AR_WEEKDAYS', '_EN_WEEKDAYS')
    rep('def ar_date(', 'def en_date(')
    rep('def ar_date_short(', 'def en_date_short(')
    rep('def ar_range(', 'def en_range(')
    rep('ar_date_short(', 'en_date_short(')
    rep('ar_range(', 'en_range(')
    rep('ar_date(', 'en_date(')  # all remaining calls (hero, notes, …)
    rep('BUILD_DATE_AR', 'BUILD_DATE_EN')
    # --- data files: _load_live_data loads (first occurrence each) ---
    rep('"data/leagues.json"', '"data/leagues-en.json"')
    rep('"data/fixtures.json"', '"data/fixtures-en.json"')
    rep('loadJSON("data/news.json")', 'loadJSON("data/news-en.json")')  # main.js news() fetch (was missed: news page would render empty)
    # --- data files: main() dumps ---
    rep('dump(os.path.join(ROOT, "data/leagues.json"),',
        'dump(os.path.join(ROOT, "data/leagues-en.json"),')
    rep('dump(os.path.join(ROOT, "data/fixtures.json"),',
        'dump(os.path.join(ROOT, "data/fixtures-en.json"),')
    rep('dump(os.path.join(ROOT, "data/news.json"), news)',
        'dump(os.path.join(ROOT, "data/news-en.json"), news)')
    # --- news: read the local EN file, not V1 ---
    rep('with open(os.path.join(V1, "data/news.json"), encoding="utf-8") as f:',
        'with open(os.path.join(ROOT, "data/news-en.json"), encoding="utf-8") as f:')
    rep('a.get("category") != "Champions League"',
        'a.get("category") != "Champions League"', required=False)
    # --- logos by EN name ---
    rep('LOGO_BY_AR = {c["ar"]: c["file"] for c in LOGOS_DATA.get("clubs", [])}',
        'LOGO_BY_EN = {c["en"]: c["file"] for c in LOGOS_DATA.get("clubs", [])}')
    src = src.replace('LOGO_BY_AR', 'LOGO_BY_EN')
    src = src.replace('byAr', 'byEn')
    src = src.replace('c.ar', 'c.en')
    src = src.replace('MalaebData', 'MatchPulseData')
    src = src.replace('MALAEB_ALLOWED', 'MATCHPULSE_ALLOWED')
    src = src.replace('window.MalaebLogos', 'window.MatchPulseLogos')
    src = src.replace('Malaeb', 'MatchPulse')
    # --- fonts / lang / dir / locale ---
    src = src.replace('Tajawal', 'Inter')
    src = src.replace('lang="ar" dir="rtl"', 'lang="en" dir="ltr"')
    src = src.replace('lang="ar"', 'lang="en"')
    src = src.replace('dir="rtl"', 'dir="ltr"')
    src = src.replace('toLocaleDateString("ar-MA"', 'toLocaleDateString("en-GB"')
    src = src.replace("toLocaleDateString('ar-MA'", "toLocaleDateString('en-GB'")
    src = src.replace('content="ar_MA"', 'content="en_US"')
    src = src.replace('"alternateName":"Al Malaeb"', '"alternateName":"MatchPulse"')
    src = src.replace('"inLanguage":"ar"', '"inLanguage":"en"')
    # --- header logo + Offers nav item ---
    rep('MatchPulse<small>AL MALAEB</small>', 'MatchPulse<small>LIVE FOOTBALL</small>')
    rep('{a("news.html", "News")}', '{a("news.html", "News")}{a("offers.html", "Offers")}')
    # --- footer: Offers link ---
    rep('<li><a href="news.html">Latest news</a></li>',
        '<li><a href="news.html">Latest news</a></li>\n          <li><a href="offers.html">Free offers</a></li>')
    # --- league page: "News {short}" -> "{short} news" ---
    rep('News {l["short"]}', '{l["short"]} news')
    # --- CPA placeholder -> live offers (whole triple-quoted block) ---
    src = re.sub(r'CPA_SLOT = """.*?"""', 'CPA_SLOT = offers_html()',
                 src, count=1, flags=re.DOTALL)
    # --- CSS additions: whole AR block -> EN block ---
    src = re.sub(r'CSS_ADD = """.*?"""',
                 lambda m: "CSS_ADD_EN = '''" + CSS_ADD_EN + "'''\nCSS_ADD = CSS_ADD_EN",
                 src, count=1, flags=re.DOTALL)
    # --- CSS in main(): strip the old Arabic additions block from style.css ---
    rep('    if "MatchPulse" not in s:\n        w(css, s + CSS_ADD)',
        '    _ar_marker = "/* ---------- الملعب V2"\n'
        '    if _ar_marker in s:\n'
        '        s = s[:s.index(_ar_marker)].rstrip() + "\\n"\n'
        '    if "MatchPulse" not in s:\n'
        '        w(css, s + CSS_ADD)')
    # --- offers.html page + sitemap ---
    rep('    # ---- sitemap / robots / render.yaml ----',
        '    # ---- offers.html (live CPA offers) ----\n'
        '    w(os.path.join(ROOT, "offers.html"),\n'
        '        offers_page_html().format(BASE=BASE, header=header("offers.html"), footer=footer()))\n\n'
        '    # ---- sitemap / robots / render.yaml ----')
    rep('"about.html", "contact.html", "privacy.html"] + \\',
        '"about.html", "contact.html", "privacy.html", "offers.html"] + \\')
    # --- news-article patch: "no live offers" box -> offers teaser ---
    rep('<div class="cpa-slot" style="position:static"><b>Sponsored offers</b>Trusted offers will be added here after selection.<small>No live offers right now.</small></div>',
        '<div class="offers-teaser"><a href="../offers.html">🎁 Free offers &amp; rewards <span class="ad-label">#ad</span> — see the 4 live offers &rarr;</a></div>',
        required=False)
    # --- render.yaml / leftovers ---
    src = src.replace('almalaeb', 'matchpulse')
    # --- build print ---
    rep('print("V2 built in", ROOT)', 'print("MatchPulse built in", ROOT)')
    return src

def main():
    src_path = os.path.join(ROOT, "tools", "build-v2.py")
    dst_path = os.path.join(ROOT, "tools", "build-en.py")
    src = open(src_path, encoding="utf-8").read()
    src = transform(src)
    src = structural(src)
    # inject the offers code before def header(
    marker = "def header("
    src = src.replace(marker, OFFERS_CODE + "\n\n" + marker, 1)
    # {CPA_SLOT} in f-string templates -> {offers_html()}
    src = src.replace("{CPA_SLOT}", "{offers_html()}")
    open(dst_path, "w", encoding="utf-8").write(src)
    print("wrote", dst_path, len(src), "bytes")
    left = [(i + 1, ln) for i, ln in enumerate(src.splitlines()) if AR.search(ln)]
    print("lines still containing Arabic:", len(left))
    for n, ln in left[:100]:
        print(f"  L{n}: {ln.strip()[:170]}")

if __name__ == "__main__":
    main()
