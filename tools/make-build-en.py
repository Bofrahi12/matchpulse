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
# AD-STYLE presentation (redesign 19 Nov 2026, user order: offers must LOOK
# like ads, not a list): sponsored ad units with a SPONSORED badge, a brand-
# colour visual tile (plain symbol, no invented logos, no product photos), a
# bold promo headline, a benefit line and a big CTA button. Links / payouts /
# geo come straight from data/offers.json and are NEVER edited here.
_OFFERS_DOC = json.load(open(os.path.join(ROOT, "data", "offers.json"), encoding="utf-8"))
OFFERS = _OFFERS_DOC["offers"]
# Mobidea Mainstream Smartlink — DISABLED by default. The user's activated
# Dashboard link is UNVERIFIED (old bundle used cpdperfomance.com/smartlink?
# lp=713; the activated link is on a different domain; Mobidea login was
# blocked 2026-11-15). NEVER guess the URL: the slot renders ONLY when
# data/offers.json mobidea_smartlink.enabled=true AND url is a verified link.
SMARTLINK = _OFFERS_DOC.get("mobidea_smartlink", {})

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

def smartlink_html():
    """Mobidea Smartlink ad unit — same ad system (Sponsored badge + #ad).
    Returns "" unless enabled AND a verified URL is set in data/offers.json."""
    url = (SMARTLINK.get("url") or "").strip()
    if not SMARTLINK.get("enabled") or not url:
        return ""
    return f"""
    <a class="ad-unit ad-smartlink" href="{url}" target="_blank" rel="nofollow sponsored noopener" style="--ad:#f97316">
      <span class="ad-sponsored">Sponsored</span>
      <span class="ad-visual" aria-hidden="true">🔗</span>
      <span class="ad-body">
        <span class="ad-tag">{SMARTLINK.get("tag", "Smartlink")}</span>
        <span class="ad-headline">{SMARTLINK.get("label", "More free offers")}</span>
        <span class="ad-benefit">{SMARTLINK.get("blurb", "")}</span>
        <span class="ad-meta">Sponsored &middot; Worldwide</span>
      </span>
      <span class="ad-cta">{SMARTLINK.get("cta", "See offers")} &rarr;</span>
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
  {smartlink_html()}
  <p class="offers-note">Sponsored offers — we may earn a commission if you sign up. Available in the listed countries only. No betting, no dating, no popups.</p>
</section>"""
    return f"""
<section class="offers-section" id="offers">
  <h2>Sponsored offers <span class="ad-label">#ad</span></h2>
  <p class="offers-note">Sponsored offers — we may earn a commission if you sign up. Available in the listed countries only. No betting, no dating, no popups.</p>
  <div class="ad-stack">{''.join(ad_card(o) for o in OFFERS)}{smartlink_html()}
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
    if smartlink_html():
        rows.append(smartlink_html())
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

# --- Live scores + table zones (PRO redesign 19 Nov 2026) ------------------
def live_nav_item(active=""):
    """Nav 'Live' link with a red count badge while matches are in progress."""
    n = len(FX_LIVE)
    cls = "active" if active == "live.html" else ""
    dot = '<span class="live-dot"></span>' if n else ""
    cnt = f' <span class="live-count">{n}</span>' if n else ""
    return f'<li><a href="live.html" class="{cls} live-nav">{dot}Live{cnt}</a></li>'

def zone_class(lid, pos, n):
    """Table zone colour per league (standard qualification rules — positions
    are real data; zones are the leagues' official qualification spots):
    PL/LaLiga/Serie A/Bundesliga top 4 = Champions League, bottom 3 relegated;
    Ligue 1 top 3 = UCL, 4th = UCL qualifying play-off, 16th = relegation
    play-off, 17-18 relegated; Botola top 2 = CAF Champions League, 3rd = CAF
    Confederation Cup, bottom 2 relegated."""
    if lid == "ligue-1":
        if pos <= 3:
            return "pos-ucl"
        if pos in (4, 16):
            return "pos-playoff"
        if pos >= 17:
            return "pos-rel"
    elif lid == "botola":
        if pos <= 2:
            return "pos-ucl"
        if pos == 3:
            return "pos-playoff"
        if pos >= 15:
            return "pos-rel"
    else:
        if pos <= 4:
            return "pos-ucl"
        if pos >= n - 2:
            return "pos-rel"
    return ""

def zone_legend(lid):
    items = {
        "ligue-1": [("pos-ucl", "Champions League"), ("pos-playoff", "Play-off (UCL qualifying / relegation)"), ("pos-rel", "Relegation")],
        "botola": [("pos-ucl", "CAF Champions League"), ("pos-playoff", "CAF Confederation Cup"), ("pos-rel", "Relegation")],
    }.get(lid, [("pos-ucl", "Champions League"), ("pos-rel", "Relegation")])
    dots = "".join(f'<span class="zone-item"><i class="zone-dot {c}"></i>{label}</span>' for c, label in items)
    return f'<div class="zone-legend">{dots}</div>'

def next_kickoff():
    """Earliest upcoming fixture (date, then time) — never invented."""
    if not UPCOMING:
        return None
    s = sorted(UPCOMING, key=lambda m: (m.get("date", ""), m.get("time") or "99:99"))
    return s[0] if s else None

def live_row_html(m):
    """One live match row: pulsing LIVE badge + minute + live score."""
    minute = (str(m.get("minute") or "")).strip()
    score = f'{m.get("home_goals", 0)} - {m.get("away_goals", 0)}'
    return (f'<a class="match-link" href="match.html?id={m["id"]}"><div class="match-row live-row">'
            f'<span class="lg">{m["league_name"]}<span class="status-badge live">● LIVE {minute}&prime;</span></span>'
            f'<span class="live-minute"><span class="live-dot"></span>{minute}&prime;</span>'
            f'<span class="team">{logo_img(m["home"])}{m["home"]}</span>'
            f'<span class="score live">{score}</span>'
            f'<span class="team away">{logo_img(m["away"])}{m["away"]}</span>'
            f'</div></a>')

def live_section_html():
    """Homepage 'Live Now' section — real live matches only; honest empty
    state (next kickoff) when nothing is live. Never fakes a live score."""
    live = FX_LIVE or []
    if live:
        rows = "".join(live_row_html(m) for m in live)
        return (f'<section class="section live-section" id="live">'
                f'<div class="section-head"><h2><span class="live-dot"></span>Live now</h2>'
                f'<a class="more" href="live.html">{len(live)} live &rarr;</a></div>'
                f'<div class="match-list">{rows}</div></section>')
    nxt = next_kickoff()
    nxt_html = ""
    if nxt:
        nxt_html = (f'<p class="live-next">Next kickoff: <b>{nxt["home"]} vs {nxt["away"]}</b>'
                    f' — {en_date(nxt["date"])} &middot; {nxt.get("time") or "TBC"} UTC</p>')
    return (f'<section class="section live-section" id="live">'
            f'<div class="section-head"><h2><span class="live-dot live-dot-idle"></span>Live now</h2>'
            f'<a class="more" href="live.html">Live scores &rarr;</a></div>'
            f'<div class="live-empty"><p><b>No live matches right now.</b></p>{nxt_html}'
            f'<a class="btn" href="matches.html">See upcoming fixtures &rarr;</a></div></section>')

def live_page_html():
    """Dedicated live-scores page (live.html)."""
    live = FX_LIVE or []
    if live:
        rows = "".join(live_row_html(m) for m in live)
        body = (f'<p class="data-note"><b>{len(live)} match(es) in progress</b> — scores from ESPN, '
                f'updated with each daily data refresh. Last updated: {BUILD_DATE_EN}.</p>'
                f'<div class="match-list">{rows}</div>')
        sub = f"{len(live)} live"
    else:
        nxt = next_kickoff()
        nxt_html = ""
        if nxt:
            nxt_html = (f'<p class="live-next">Next kickoff: <b>{nxt["home"]} vs {nxt["away"]}</b>'
                        f' — {en_date(nxt["date"])} &middot; {nxt.get("time") or "TBC"} UTC</p>')
        up5 = fixtures_list_html(UPCOMING[:5]) if UPCOMING else ""
        body = (f'<div class="live-empty"><p><b>No live matches right now.</b></p>{nxt_html}</div>'
                f'<div class="section-head" style="margin-top:22px"><h2>Next kickoffs</h2>'
                f'<a class="more" href="matches.html">All fixtures &rarr;</a></div>{up5}')
        sub = "No live matches"
    tpl = """<!DOCTYPE html>
<html lang="en" dir="ltr">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Live scores | MatchPulse</title>
<meta name="description" content="Live football scores from Europe's five major leagues and Botola Pro — in progress now. All times UTC.">
<link rel="canonical" href="{BASE}/live.html">
<link rel="icon" href="assets/logo.svg" type="image/svg+xml">
<link rel="stylesheet" href="assets/css/style.css">
</head>
<body>
{header}
{CHIPS}
{TICKER}
<main class="container">
  <section class="section">
    <div class="section-head"><h2>Live scores</h2><span style="color:var(--muted);font-size:.82rem">{sub}</span></div>
    {body}
  </section>
</main>
{footer}
<script src="assets/js/data-fallback.js"></script>
<script src="assets/js/main.js"></script>
</body>
</html>"""
    return tpl.format(BASE=BASE, header=header("live.html"), footer=footer(), body=body, sub=sub, CHIPS=CHIPS, TICKER=TICKER)
'''

CSS_ADD_EN = '''
/* ---------- MatchPulse: additions ---------- */
/* PRO INTERNATIONAL design system (19 Nov 2026) — references: Flashscore,
   Sofascore, BBC Sport, ESPN. Light livescore system: light grey page,
   white cards, dark navy header, ONE royal-blue accent. This block is the
   single source of truth — build-en.py main() strips the old block and
   re-appends this one on every build. The dark base above is kept only as
   fallback; everything below overrides it. */
/* Hide empty ad slots (teardown fixes 18 Nov 2026) — the live CPA offers
   section (.offers-*) is NOT hidden. */
.ad-slot, .anchored-ad, .ad-leaderboard, .ad-infeed, .ad-rect { display: none !important; }

/* ---------- tokens ---------- */
:root {
  --bg: #eef1f5; --bg-soft: #e6ebf1; --card: #ffffff; --card-2: #f8fafc;
  --border: #dbe2ec; --line: #dbe2ec;
  --text: #0f172a; --muted: #64748b; --muted-2: #94a3b8;
  --accent: #1d4ed8; --accent-dark: #1e40af; --accent-soft: #dbeafe;
  --navy: #0b1530; --gold: #b45309; --red: #e11d48; --red-dark: #be123c;
  --green: #16a34a; --blue: #2563eb;
  --radius: 10px;
  --shadow: 0 1px 2px rgba(15,23,42,.06), 0 1px 3px rgba(15,23,42,.05);
  --shadow-lg: 0 8px 24px rgba(15,23,42,.10);
  --font: "Inter","Segoe UI",system-ui,-apple-system,sans-serif;
}
body { font-family: var(--font); background: var(--bg); color: var(--text); line-height: 1.55; }
body::before { display: none; }
.container { width: min(1200px, 94%); }

/* ---------- header ---------- */
.site-header { background: var(--navy); border-bottom: none; box-shadow: 0 1px 0 rgba(0,0,0,.2); }
.header-inner { padding: 10px 0; }
.logo { color: #fff; font-size: 1.35rem; letter-spacing: -.01em; }
.logo .ball {
  width: 38px; height: 38px; border: none;
  background: linear-gradient(135deg, #2563eb, #1e40af);
  box-shadow: 0 0 0 2px rgba(255,255,255,.14); font-size: 1.1rem;
}
.logo small { color: #94a3b8; font-size: .62rem; letter-spacing: 2px; }
.main-nav a { color: #cbd5e1; font-size: .92rem; padding: 8px 13px; border-radius: 8px; }
.main-nav a:hover { color: #fff; background: rgba(255,255,255,.09); }
.main-nav a.active { color: #fff; background: var(--accent); }
.menu-btn { background: transparent; border: 1px solid rgba(255,255,255,.25); color: #fff; }
.live-nav { display: inline-flex; align-items: center; gap: 6px; }
.live-count { background: var(--red); color: #fff; font-size: 11px; font-weight: 800; border-radius: 999px; padding: 1px 7px; line-height: 1.5; }

/* ---------- league chips ---------- */
.league-chips { display: flex; gap: 8px; overflow-x: auto; padding: 12px 0 2px; scrollbar-width: none; }
.league-chips::-webkit-scrollbar { display: none; }
.league-chips a {
  flex: 0 0 auto; display: inline-flex; align-items: center; gap: 7px;
  background: #fff; border: 1px solid var(--border); border-radius: 999px;
  padding: 7px 14px; font-size: .86rem; font-weight: 600; color: var(--text); white-space: nowrap;
}
.league-chips a:hover { border-color: var(--accent); color: var(--accent); }
.league-chips img, .league-chips svg { width: 18px; height: 18px; object-fit: contain; }

/* ---------- ticker ---------- */
.ticker-wrap { background: #fff; border-bottom: 1px solid var(--border); }
.ticker-label { background: var(--red); }
.ticker-item { color: var(--muted); }
.ticker-item b { color: var(--text); }

/* ---------- hero ---------- */
.hero { padding: 18px 0 4px; }
.hero-card {
  background: #fff; border: 1px solid var(--border); box-shadow: var(--shadow);
  min-height: 0; border-radius: 12px;
}
.hero-card::before { display: none; }
.hero-content { padding: 26px 28px; max-width: 720px; }
.tag {
  background: var(--accent-soft); color: var(--accent-dark);
  font-size: .72rem; font-weight: 800; letter-spacing: .06em; text-transform: uppercase;
  padding: 4px 12px; border-radius: 999px; margin-bottom: 12px;
}
.tag.gold { background: #fef3c7; color: #92400e; }
.hero-content h1 { font-size: clamp(1.35rem, 3vw, 1.7rem); line-height: 1.3; letter-spacing: -.015em; color: var(--text); margin-bottom: 8px; }
.hero-content p { color: var(--muted); font-size: .95rem; margin-bottom: 16px; }
.btn {
  background: var(--accent); color: #fff; font-weight: 700; font-size: .92rem;
  padding: 11px 22px; border-radius: 8px; box-shadow: none;
}
.btn:hover { transform: none; background: var(--accent-dark); box-shadow: 0 4px 14px rgba(29,78,216,.3); }
.btn.ghost { background: #fff; color: var(--text); border: 1px solid var(--border); box-shadow: none; }
.btn.ghost:hover { border-color: var(--accent); color: var(--accent); box-shadow: none; }

/* ---------- date strip ---------- */
.date-strip { display: grid; grid-template-columns: repeat(3, 1fr); gap: 12px; margin: 14px 0 2px; }
.date-strip .day {
  background: #fff; border: 1px solid var(--border); border-radius: var(--radius);
  padding: 12px 16px; display: flex; align-items: center; justify-content: space-between; gap: 10px;
  box-shadow: var(--shadow); min-width: 0; flex-wrap: wrap;
}
.date-strip .day b { font-size: .9rem; font-weight: 700; color: var(--text); min-width: 0; }
.date-strip .day span { font-size: 1.25rem; font-weight: 800; color: var(--accent); }
.date-strip .day.next span { color: var(--text); }

/* ---------- sections ---------- */
.section { padding: 22px 0; }
.section-head { margin-bottom: 14px; }
.section-head h2 { font-size: 1.06rem; font-weight: 800; letter-spacing: .01em; color: var(--text); display: block; min-width: 0; }
.section-head h2::before { width: 4px; height: 20px; background: var(--accent); border-radius: 2px; display: inline-block; vertical-align: -3px; margin-right: 8px; }
.section-head a.more { color: var(--accent); font-weight: 700; font-size: .88rem; }

/* ---------- news cards ---------- */
.news-grid { gap: 16px; }
.news-card { background: #fff; border: 1px solid var(--border); border-radius: 12px; box-shadow: var(--shadow); }
.news-card:hover { transform: translateY(-2px); border-color: #c7d2fe; box-shadow: var(--shadow-lg); }
.news-thumb { height: 140px; font-size: 2.4rem; background: linear-gradient(135deg, #dbeafe, #eff6ff); }
.news-body { padding: 14px 16px; }
.news-meta .cat { color: var(--accent); font-size: .72rem; letter-spacing: .05em; text-transform: uppercase; }
.news-card h3 { font-size: .98rem; line-height: 1.45; color: var(--text); }
.news-card p { color: var(--muted); font-size: .86rem; }

/* ---------- match rows (Flashscore-style) ---------- */
.match-list { gap: 8px; }
.match-link { display: block; }
.match-row {
  display: grid; grid-template-columns: 78px 1fr auto 1fr; align-items: center; gap: 10px;
  background: #fff; border: 1px solid var(--border); border-radius: var(--radius);
  padding: 10px 14px; box-shadow: var(--shadow);
}
.match-link:hover .match-row, a:hover > .match-row { border-color: #93c5fd; }
.match-row .lg {
  grid-column: 1 / -1; font-size: .68rem; font-weight: 700; letter-spacing: .06em;
  text-transform: uppercase; color: var(--muted-2);
  display: flex; align-items: center; justify-content: space-between; gap: 8px;
}
.match-row .team { font-weight: 600; font-size: .92rem; color: var(--text); min-width: 0; }
.match-row .team:not(.away) { text-align: right; }
.match-row .team.away { text-align: left; }
.match-row .team img { width: 20px; height: 20px; object-fit: contain; vertical-align: -4px; }
.match-row .team:not(.away) img { margin-inline-start: 7px; margin-inline-end: 0; }
.match-row .team.away img { margin-inline-end: 7px; }
.match-row .score {
  background: #f1f5f9; border: none; border-radius: 6px; color: var(--text);
  padding: 3px 11px; font-weight: 800; font-size: .95rem; min-width: 66px; text-align: center;
}
.match-row .score.live { background: #fff1f2; color: var(--red-dark); border: 1px solid #fecdd3; }
.match-row .time { font-size: .78rem; color: var(--muted); white-space: nowrap; line-height: 1.35; }
.match-row .time.live-min { color: var(--red); font-weight: 800; font-size: .85rem; }

/* status badges */
.status-badge { display: inline-block; padding: 2px 9px; border-radius: 999px; font-size: 11px; font-weight: 700; letter-spacing: .02em; }
.status-badge.live, .status-live { background: var(--red); color: #fff; }
.status-badge.live { animation: livepulse 1.6s infinite; }
.status-badge.finished, .status-ft { background: #e2e8f0; color: #475569; }
.status-badge.upcoming, .status-tbc { background: #fef3c7; color: #92400e; }
@keyframes livepulse { 0%,100% { opacity: 1; } 50% { opacity: .55; } }

/* ---------- live section ---------- */
.live-section { margin-top: 18px; }
.live-dot { display: inline-block; width: 9px; height: 9px; border-radius: 50%; background: var(--red); margin-inline-end: 7px; animation: livepulse 1.4s infinite; }
.live-dot-idle { background: #cbd5e1; animation: none; }
.live-minute { display: inline-flex; align-items: center; gap: 6px; font-weight: 800; color: var(--red); font-size: .85rem; white-space: nowrap; }
.live-empty {
  background: #fff; border: 1px dashed #cbd5e1; border-radius: 12px;
  padding: 22px 20px; text-align: center; color: var(--muted);
}
.live-empty p { margin-bottom: 6px; }
.live-empty p b { color: var(--text); }
.live-next { font-size: .92rem; }
.live-empty .btn { margin-top: 12px; }
.live-count { background: var(--red); color: #fff; font-size: 11px; font-weight: 800; border-radius: 999px; padding: 1px 7px; }

/* ---------- tabs ---------- */
.tabs button {
  background: #fff; border: 1px solid var(--border); color: #475569;
  padding: 8px 18px; font-size: .88rem;
}
.tabs button.active { background: var(--accent); color: #fff; border-color: var(--accent); }
.league-select button { background: #fff; border: 1px solid var(--border); color: var(--text); }
.league-select button.active { background: var(--accent); color: #fff; border-color: var(--accent); }

/* ---------- tables ---------- */
.table-wrap { background: #fff; border: 1px solid var(--border); border-radius: 12px; box-shadow: var(--shadow); overflow-x: auto; }
table.standings { font-size: .88rem; min-width: 560px; }
table.standings th {
  background: #f8fafc; color: var(--muted); font-size: .7rem; letter-spacing: .05em;
  text-transform: uppercase; padding: 11px 8px; border-bottom: 1px solid var(--border);
}
table.standings td { padding: 0 8px; height: 44px; border-top: 1px solid #eef2f7; color: var(--text); }
table.standings td.team { text-align: left; font-weight: 600; font-size: .92rem; white-space: nowrap; }
table.standings td b { font-size: .95rem; }
table.standings tr:hover td { background: #f8fafc; }

/* ---------- logo sizing (never intrinsic size outside match rows) ---------- */
.standings td.team img { width: 22px; height: 22px; object-fit: contain; vertical-align: -4px; margin-right: 7px; }
.league-select button img { width: 22px; height: 22px; object-fit: contain; vertical-align: -5px; margin-right: 7px; }
#league-title img { width: 30px; height: 30px; object-fit: contain; display: inline-block; vertical-align: -7px; margin-right: 8px; }
.scorer .info img { width: 20px; height: 20px; object-fit: contain; vertical-align: -4px; margin-right: 5px; }
/* ---------- match page: scoreboard, info, tabs (base had no rules) ---------- */
.scoreboard { background: #fff; border: 1px solid var(--border); border-radius: 12px; box-shadow: var(--shadow); padding: 26px 20px 18px; text-align: center; margin-bottom: 16px; }
.scoreboard .teams { display: flex; align-items: center; justify-content: center; gap: 20px; }
.scoreboard .team-name { display: flex; flex-direction: column; align-items: center; gap: 10px; font-weight: 800; font-size: 1.05rem; width: 220px; }
.scoreboard .team-name img { width: 64px; height: 64px; object-fit: contain; }
.scoreboard .big-score { font-size: 1.9rem; font-weight: 900; background: #f1f5f9; border-radius: 10px; padding: 8px 18px; white-space: nowrap; }
.scoreboard .status { color: var(--muted); font-size: .9rem; margin-top: 14px; }
.match-info { display: flex; flex-wrap: wrap; gap: 8px 26px; background: #fff; border: 1px solid var(--border); border-radius: 12px; padding: 14px 18px; margin-bottom: 16px; font-size: .92rem; }
.match-info .lbl { color: var(--muted); margin-right: 5px; }
.match-tabs button { padding: 8px 16px; border: 1px solid var(--border); border-radius: 999px; background: #fff; color: #475569; cursor: pointer; font-weight: 700; font-size: .88rem; font-family: inherit; }
.match-tabs button.active { background: var(--accent); color: #fff; border-color: var(--accent); }
table.standings tr.pos-ucl td:first-child { border-left: 3px solid var(--blue); }
table.standings tr.pos-rel td:first-child { border-left: 3px solid var(--red); }
table.standings tr.pos-playoff td:first-child { border-left: 3px solid #d97706; }
.zone-legend { display: flex; flex-wrap: wrap; gap: 6px 18px; margin-top: 10px; font-size: .8rem; color: var(--muted); }
.zone-item { display: inline-flex; align-items: center; gap: 6px; }
.zone-dot { width: 10px; height: 10px; border-radius: 3px; display: inline-block; }
.zone-dot.pos-ucl { background: var(--blue); }
.zone-dot.pos-rel { background: var(--red); }
.zone-dot.pos-playoff { background: #d97706; }

/* ---------- scorers ---------- */
.scorer { background: #fff; border: 1px solid var(--border); border-radius: var(--radius); box-shadow: var(--shadow); }
.scorer .rank { background: #eff6ff; border: none; color: var(--accent); }
.scorer .info b { color: var(--text); }
.scorer .info span { color: var(--muted); }
.scorer .goals { color: var(--accent); }

/* ---------- notes / misc ---------- */
.data-note {
  background: #eff6ff; border: 1px solid #dbeafe; border-left: 3px solid var(--accent);
  border-radius: 8px; padding: 10px 14px; font-size: .84rem; color: #334155;
}
.verified-tag { display: inline-block; background: #dcfce7; color: #166534; font-size: 11px; font-weight: 800; border-radius: 999px; padding: 2px 9px; }
.placeholder-box { background: #fff; border: 1px dashed #cbd5e1; border-radius: var(--radius); padding: 20px; color: var(--muted); text-align: center; }

/* ---------- newsletter / forms ---------- */
.newsletter { background: var(--navy); border: none; }
.newsletter h2 { color: #fff; }
.newsletter p { color: #cbd5e1; }
.newsletter input { background: #fff; border: 1px solid #cbd5e1; color: var(--text); }
.newsletter input:focus { border-color: var(--accent); }
.form-note { color: #93c5fd; }
.contact-form input, .contact-form textarea, .contact-form select {
  background: #fff; border: 1px solid #cbd5e1; color: var(--text);
}
.contact-form input:focus, .contact-form textarea:focus { border-color: var(--accent); box-shadow: 0 0 0 3px rgba(29,78,216,.15); }
.contact-form label { color: var(--text); }

/* ---------- articles / pages ---------- */
.article-hero { background: linear-gradient(135deg, #dbeafe, #eff6ff); border: 1px solid var(--border); }
.article-body { color: #334155; }
.article-body h2 { color: var(--text); }
.article-body blockquote { background: #f8fafc; border-left: 4px solid var(--accent); color: var(--text); }
.page h1 { font-size: 1.55rem; color: var(--text); }
.page h2 { color: var(--text); }
.page p, .page li { color: #334155; }

/* ---------- footer ---------- */
.site-footer { background: var(--navy); border-top: none; margin-top: 40px; padding: 36px 0 28px; }
.footer-grid h4 { color: #fff; }
.footer-grid a { color: #94a3b8; }
.footer-grid a:hover { color: #fff; }
.footer-grid p { color: #94a3b8; }
.footer-bottom { border-top: 1px solid rgba(255,255,255,.12); color: #7d8aa5; }

/* ---------- match page ---------- */
.match-tabs { display: flex; gap: 8px; margin: 16px 0; flex-wrap: wrap; }
.match-tab { padding: 8px 14px; border: 1px solid var(--border); border-radius: 999px; background: #fff; color: #475569; cursor: pointer; font-weight: 700; font-size: .88rem; }
.match-tab.active { background: var(--accent); color: #fff; border-color: var(--accent); }
.stat-row { display: grid; grid-template-columns: 44px 1fr 44px; align-items: center; gap: 10px; margin: 10px 0; }
.stat-bar { height: 8px; background: #e2e8f0; border-radius: 999px; overflow: hidden; position: relative; }
.stat-bar i { position: absolute; top: 0; bottom: 0; }
.stat-bar i.home { left: 0; background: var(--accent); }
.stat-bar i.away { right: 0; background: #94a3b8; }

/* ---------- sponsored ads (light theme — same units, same links) ---------- */
.offers-section { margin: 28px 0; }
.offers-section h2 { font-size: 1.06rem; font-weight: 800; color: var(--text); }
.ad-label { font-size: 11px; color: #64748b; border: 1px solid #cbd5e1; border-radius: 6px; padding: 1px 6px; vertical-align: middle; background: #fff; }
.offers-note { color: #64748b; font-size: 13px; }
.ad-kicker { text-align: center; font-size: 11px; letter-spacing: 3px; color: #94a3b8; text-transform: uppercase; margin: 0 0 8px; }
.ad-tag { display: inline-block; align-self: flex-start; font-size: 11px; font-weight: 800; letter-spacing: 1px; text-transform: uppercase; color: var(--ad, #1d4ed8); border: 1px solid var(--ad, #1d4ed8); border-radius: 999px; padding: 2px 8px; margin-bottom: 6px; background: #fff; }
.ad-unit, .ad-leaderboard-unit {
  position: relative; display: flex; gap: 16px; align-items: center; padding: 18px;
  border-radius: 12px; background: #fff; border: 1px solid var(--border);
  border-top: 3px solid var(--ad, #1d4ed8); box-shadow: var(--shadow);
  text-decoration: none; color: inherit; overflow: hidden;
}
.ad-unit:hover, .ad-leaderboard-unit:hover, .ad-mini:hover { border-color: var(--ad, #1d4ed8); box-shadow: var(--shadow-lg); }
.ad-sponsored { position: absolute; top: 0; right: 0; background: #f59e0b; color: #111; font-size: 10px; font-weight: 800; letter-spacing: 1px; text-transform: uppercase; padding: 3px 9px; border-radius: 0 0 0 8px; }
.ad-visual { flex: 0 0 56px; width: 56px; height: 56px; border-radius: 12px; display: flex; align-items: center; justify-content: center; font-size: 28px; background: var(--ad, #1d4ed8); }
.ad-body { flex: 1; min-width: 0; display: flex; flex-direction: column; }
.ad-headline { font-weight: 800; font-size: 1.05rem; line-height: 1.25; color: var(--text); }
.ad-benefit { font-size: .9rem; color: #475569; margin-top: 3px; }
.ad-meta { font-size: 12px; color: #64748b; margin-top: 5px; }
.ad-cta { flex: 0 0 auto; background: var(--ad, #1d4ed8); color: #fff; font-weight: 800; text-transform: uppercase; letter-spacing: .4px; font-size: .85rem; padding: 12px 18px; border-radius: 999px; white-space: nowrap; text-align: center; }
.ad-stack { display: grid; gap: 12px; }
@media (min-width: 700px) { .ad-stack { grid-template-columns: 1fr 1fr; } }
@media (max-width: 640px) { .ad-unit { flex-wrap: wrap; } .ad-unit .ad-cta { width: 100%; } }
.ad-leaderboard-wrap { margin: 28px 0; }
.ad-leaderboard-unit { padding: 22px; border-radius: 12px; }
.ad-leaderboard-unit .ad-visual { flex-basis: 72px; width: 72px; height: 72px; font-size: 36px; border-radius: 16px; }
.ad-leaderboard-unit .ad-headline { font-size: 1.35rem; }
.ad-leaderboard-unit .ad-cta { padding: 14px 26px; font-size: 1rem; }
.ad-grid { display: grid; gap: 12px; margin-top: 12px; }
@media (min-width: 700px) { .ad-grid { grid-template-columns: repeat(3, 1fr); } }
.ad-mini { position: relative; display: flex; flex-direction: column; gap: 6px; padding: 18px 16px 16px; border-radius: 12px; background: #fff; border: 1px solid var(--border); border-top: 3px solid var(--ad, #1d4ed8); box-shadow: var(--shadow); text-decoration: none; color: inherit; overflow: hidden; }
.ad-mini .ad-visual { width: 52px; height: 52px; font-size: 26px; margin-top: 4px; }
.ad-mini .ad-cta { margin-top: 8px; }
.ad-mini .ad-headline { color: var(--text); }
.ad-mini .ad-benefit { color: #475569; }
.ad-showcase { position: relative; display: flex; gap: 18px; padding: 22px 20px; border-radius: 12px; background: #fff; border: 1px solid var(--border); border-top: 3px solid var(--ad, #1d4ed8); box-shadow: var(--shadow); margin: 16px 0; overflow: hidden; }
.ad-showcase .ad-visual { flex: 0 0 88px; width: 88px; height: 88px; font-size: 44px; border-radius: 16px; }
.ad-showcase .ad-headline { font-size: 1.3rem; margin: 2px 0 0; color: var(--text); }
.ad-showcase .ad-benefit { font-size: .95rem; color: #475569; }
.ad-facts { font-size: .85rem; color: #475569; margin: 8px 0 0; }
.ad-cta-btn { display: inline-block; margin-top: 14px; background: var(--ad, #1d4ed8); color: #fff; font-weight: 800; text-transform: uppercase; letter-spacing: .4px; font-size: .95rem; padding: 13px 24px; border-radius: 999px; text-decoration: none; }
.ad-cta-btn:hover { filter: brightness(1.12); }
@media (max-width: 640px) { .ad-showcase, .ad-leaderboard-unit { flex-wrap: wrap; } .ad-leaderboard-unit .ad-cta, .ad-cta-btn { width: 100%; text-align: center; } }
.offers-teaser { border: 1px solid var(--border); border-radius: 12px; padding: 12px 14px; margin: 14px 0; background: #fff; font-weight: 700; box-shadow: var(--shadow); }
.offers-teaser a { text-decoration: none; color: var(--text); }
/* Mobidea Smartlink slot — same ad system, same Sponsored badge + #ad.
   Rendered ONLY when data/offers.json mobidea_smartlink.enabled=true AND a
   verified url is set. Default: hidden. */
.ad-smartlink .ad-visual { background: #f97316; }

/* ---------- responsive ---------- */
@media (max-width: 900px) {
  .article-layout { grid-template-columns: 1fr; }
  .ad-rect { position: static; min-height: 120px; }
  .footer-grid { grid-template-columns: 1fr 1fr; }
}
@media (max-width: 760px) {
  .main-nav { display: none; position: absolute; top: 100%; right: 0; left: 0; background: var(--navy); border-bottom: 1px solid rgba(255,255,255,.12); }
  .main-nav.open { display: block; }
  .main-nav ul { flex-direction: column; padding: 10px; }
  .menu-btn { display: block; margin-inline-start: auto; }
  .newsletter form { flex-direction: column; }
  .hero-content { padding: 20px; }
  .date-strip { grid-template-columns: repeat(3, 1fr); gap: 8px; }
  .date-strip .day { padding: 10px 12px; }
  .date-strip .day b { font-size: .8rem; }
  .date-strip .day span { font-size: 1.05rem; }
}
@media (max-width: 640px) {
  .match-row { grid-template-columns: 58px 1fr auto 1fr; padding: 9px 10px; gap: 7px; }
  .match-row .team { font-size: .8rem; }
  .match-row .score { min-width: 44px; padding: 3px 8px; font-size: .88rem; }
  .match-row .team img { width: 18px; height: 18px; }
  .match-row .score { min-width: 56px; padding: 3px 8px; font-size: .9rem; }
  .hero-content h1 { font-size: 1.3rem; }
  .section { padding: 18px 0; }
  .footer-grid { grid-template-columns: 1fr; }
}
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
    # --- PRO redesign (19 Nov 2026): fonts, CSS refresh, Live nav, zones,
    #     match-row time-first, live section + live.html, sitemap ---------
    rep('family=Inter:wght@400;500;700;800', 'family=Inter:wght@400;500;600;700;800;900')
    # --- CSS in main(): refresh the MatchPulse additions block each build ---
    rep('    _ar_marker = "/* ---------- الملعب V2"\n'
        '    if _ar_marker in s:\n'
        '        s = s[:s.index(_ar_marker)].rstrip() + "\\n"\n'
        '    if "MatchPulse" not in s:\n'
        '        w(css, s + CSS_ADD)',
        '    _ar_marker = "/* ---------- الملعب V2"\n'
        '    if _ar_marker in s:\n'
        '        s = s[:s.index(_ar_marker)].rstrip() + "\\n"\n'
        '    _mp_marker = "/* ---------- MatchPulse: additions"\n'
        '    if _mp_marker in s:\n'
        '        s = s[:s.index(_mp_marker)].rstrip() + "\\n"\n'
        '    w(css, s + CSS_ADD)')
    # --- header: Live nav item (with red count badge while matches are live) ---
    rep('{a("index.html", "Home")}', '{a("index.html", "Home")}{live_nav_item(active)}')
    # --- table zones (server-side tables, league pages) ---
    rep('        cls = "pos-ucl" if r["pos"] <= 4 else ("pos-rel" if (league["id"] == "botola" and r["pos"] >= 15) or (league["id"] != "botola" and r["pos"] >= 18) else "")',
        '        cls = zone_class(league["id"], r["pos"], len(league["table"]))')
    rep('''f'<tbody>{"".join(out)}</tbody></table></div>')''',
        '''f'<tbody>{"".join(out)}</tbody></table></div>' + zone_legend(league["id"]))''')
    # --- table zones (JS tables: standings page + homepage minis) ---
    rep('''  window.posClass = function (pos, leagueId) {
    if (pos <= 4) return "pos-ucl";
    if (leagueId === "botola") return pos >= 15 ? "pos-rel" : "";
    if (pos >= 18) return "pos-rel";
    return "";
  };''',
        '''  window.posClass = function (pos, leagueId, n) {
    if (leagueId === "ligue-1") {
      if (pos <= 3) return "pos-ucl";
      if (pos === 4 || pos === 16) return "pos-playoff";
      if (pos >= 17) return "pos-rel";
      return "";
    }
    if (leagueId === "botola") {
      if (pos <= 2) return "pos-ucl";
      if (pos === 3) return "pos-playoff";
      if (pos >= 15) return "pos-rel";
      return "";
    }
    if (pos <= 4) return "pos-ucl";
    if (pos >= (n || 20) - 2) return "pos-rel";
    return "";
  };''')
    rep('window.posClass(r.pos, league.id)', 'window.posClass(r.pos, league.id, league.table.length)')
    # --- match rows: time first (Flashscore-style) + live minute in red ---
    rep('''    const time = isLive
      ? `<span class="time">${m.minute || ""}'</span>`
      : `<span class="time">${m.date_label || m.date || ""} ${m.time || ""}</span>`;''',
        '''    const shortDate = iso => iso ? new Date(iso + "T12:00:00").toLocaleDateString("en-GB", {day: "numeric", month: "short"}) : "";
    const time = isLive
      ? `<span class="time live-min">${m.minute || ""}'</span>`
      : isFin
        ? `<span class="time">${shortDate(m.date)}</span>`
        : `<span class="time">${shortDate(m.date)}<br>${m.time || "TBC"}</span>`;''')
    rep('''    const score = isLive || isFin
      ? `<span class="score${isLive ? " live" : ""}">${m.home_goals} - ${m.away_goals}</span>`
      : `<span class="score">${m.time || "—"}</span>`;''',
        '''    const score = isLive || isFin
      ? `<span class="score${isLive ? " live" : ""}">${m.home_goals} - ${m.away_goals}</span>`
      : `<span class="score">–</span>`;''')
    rep('''    const inner = `<div class="match-row">
      <span class="lg">${m.league_name || ""}${badge}</span>
      <span class="team">${window.logoFor(m.home)}${m.home}</span>${score}<span class="team away">${window.logoFor(m.away)}${m.away}</span>${time}
    </div>`;''',
        '''    const inner = `<div class="match-row">
      <span class="lg">${m.league_name || ""}${badge}</span>
      ${time}<span class="team">${window.logoFor(m.home)}${m.home}</span>${score}<span class="team away">${window.logoFor(m.away)}${m.away}</span>
    </div>`;''')
    rep('''        score = f'{m["home_goals"]} - {m["away_goals"]}' if m["status"] == "finished" else (m.get("time") or "—")
        when = f'{m.get("date_label") or m["date"]} {m.get("time") or ""}'.strip()
        if m.get("time") is None:
            when += " — Kick-off time TBC"
        inner = (f'<div class="match-row"><span class="lg">{m["league_name"]}</span>'
                 f'<span class="team">{logo_img(m["home"])}{m["home"]}</span><span class="score">{score}</span>'
                 f'<span class="team away">{logo_img(m["away"])}{m["away"]}</span><span class="time">{when}</span></div>')''',
        '''        score = f'{m["home_goals"]} - {m["away_goals"]}' if m["status"] == "finished" else "–"
        ds = f'{int(m["date"][8:10])} {["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"][int(m["date"][5:7]) - 1]}'
        when = f'{ds}<br>{m.get("time") or "TBC"}' if m["status"] != "finished" else ds
        inner = (f'<div class="match-row"><span class="lg">{m["league_name"]}</span>'
                 f'<span class="time">{when}</span>'
                 f'<span class="team">{logo_img(m["home"])}{m["home"]}</span><span class="score">{score}</span>'
                 f'<span class="team away">{logo_img(m["away"])}{m["away"]}</span></div>')''')
    # --- homepage: Live Now section above the hero ---
    rep('<main class="container">\n{HERO}', '<main class="container">\n{live_section_html()}\n{HERO}')
    # --- live.html page (after offers.html generation) ---
    rep('''    # ---- offers.html (live CPA offers) ----
    w(os.path.join(ROOT, "offers.html"),
        offers_page_html().format(BASE=BASE, header=header("offers.html"), footer=footer()))''',
        '''    # ---- offers.html (live CPA offers) ----
    w(os.path.join(ROOT, "offers.html"),
        offers_page_html().format(BASE=BASE, header=header("offers.html"), footer=footer()))
    # ---- live.html (live scores) ----
    w(os.path.join(ROOT, "live.html"), live_page_html())''')
    # --- sitemap + refresh_dates: add live.html ---
    # (The "...privacy.html"] + \ pattern appears in both lists, and rep()
    #  replaces all occurrences — so this one rep covers sitemap AND dates.)
    rep('"about.html", "contact.html", "privacy.html", "offers.html"] + \\',
        '"about.html", "contact.html", "privacy.html", "offers.html", "live.html"] + \\')
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
    # homepage: featured offer as a leaderboard banner, not the box stack
    src = src.replace(
        '  {offers_html()}\n\n  <section class="section">\n    <div class="section-head"><h2>Latest news</h2>',
        '  {offers_html("leaderboard")}\n\n  <section class="section">\n    <div class="section-head"><h2>Latest news</h2>', 1)
    open(dst_path, "w", encoding="utf-8").write(src)
    print("wrote", dst_path, len(src), "bytes")
    left = [(i + 1, ln) for i, ln in enumerate(src.splitlines()) if AR.search(ln)]
    print("lines still containing Arabic:", len(left))
    for n, ln in left[:100]:
        print(f"  L{n}: {ln.strip()[:170]}")

if __name__ == "__main__":
    main()
