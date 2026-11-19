#!/usr/bin/env python3
"""MatchPulse — translate the 5 static pages + base CSS + ads.txt in place.

Uses the same transform() as tools/make-build-en.py (UI dict + data-name
maps, boundary-safe), plus exact-string EXTRA replacements for prose the
generic transform cannot render cleanly, plus structural fixes:
- lang/dir, fonts, logo, nav + footer Offers links
- news.html: EN filter categories (must match data/news-en.json),
  window.MalaebData -> window.MatchPulseData, old cpa-slot -> live offers
- standings.html: delete the old cpa-slot placeholder (live offers section
  already inserted by build-en.py after the scorers block)
- style.css: LTR rules (direction, text-align, border/margin sides), Inter
"""
import importlib.util
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))


def load_mod(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


mk = load_mod("mk_en", ROOT / "tools" / "make-build-en.py")
ben = load_mod("build_en", ROOT / "tools" / "build-en.py")
transform = mk.transform
OFFERS_HTML = ben.offers_html()

AR = re.compile(r"[\u0600-\u06FF]")

# ---------------------------------------------------------------- EXTRA
# Exact Arabic -> English, applied BEFORE transform (longest first).
EXTRA = {
    # --- common shell ---
    '<html lang="ar" dir="rtl">': '<html lang="en" dir="ltr">',
    'content="ar_MA"': 'content="en_US"',
    "css2?family=Tajawal:wght@400;500;700;800": "css2?family=Inter:wght@400;500;700;800",
    '<span>الملعب<small>AL MALAEB</small></span>': "<span>MatchPulse<small>LIVE FOOTBALL</small></span>",
    "موقعك المغربي لمتابعة كرة القدم: نتائج مباشرة، جداول الترتيب، وآخر الأخبار.":
        "Your home for football: live scores, league tables and the latest news.",
    "آخر تحديث: الخميس 19 نونبر 2026": "Last updated: Thursday 19 November 2026",
    "الملعب — جميع الحقوق محفوظة.": "MatchPulse — All rights reserved.",
    "مساحة إعلانية — Leaderboard 970×250": "Ad space — Leaderboard 970×250",
    "مساحة إعلانية للهواتف": "Ad space for mobile",
    "مباشر": "LIVE",
    "جارٍ التحميل…": "Loading…",
    "ضع كود إعلانك هنا بعد قبول حسابك": "place your ad code here after your account is approved",
    "الرئيسية": "Home",
    "المباريات": "Matches",
    "الترتيب": "Standings",
    "الأخبار": "News",
    "من نحن": "About us",
    "اتصل بنا": "Contact us",
    "سياسة الخصوصية": "Privacy policy",
    "أقسام الموقع": "Site sections",
    "معلومات": "Information",
    "مباريات اليوم": "Today's matches",
    "جداول الترتيب": "League tables",
    "آخر الأخبار": "Latest news",
    "البطولة المغربية": "Botola Pro",
    "القائمة": "Menu",
    # --- standings ---
    "<title>جداول ترتيب الدوريات الخمسة الكبرى والبطولة المغربية | الملعب</title>":
        "<title>League tables — Europe’s five major leagues &amp; Botola Pro | MatchPulse</title>",
    "جداول ترتيب الدوريات الخمسة الكبرى والبطولة المغربية 2026-27 — الجداول الكاملة موثقة لكل دوري (آخر تحقق الخميس 19 نونبر 2026) مع هدافي كل دوري.":
        "2026-27 league tables for Europe’s five major leagues and Botola Pro — full tables verified for every league (last checked 19 November 2026) with each league’s top scorers.",
    '<meta property="og:title" content="جداول الترتيب | الملعب">':
        '<meta property="og:title" content="League tables | MatchPulse">',
    '<h2 id="league-title">جداول الترتيب</h2>': '<h2 id="league-title">League tables</h2>',
    "<h2>👟 هدّافو الدوري</h2>": "<h2>👟 Top scorers</h2>",
    # --- news ---
    "<title>آخر أخبار كرة القدم | الملعب</title>": "<title>Latest football news | MatchPulse</title>",
    "آخر أخبار كرة القدم: الدوريات الأوروبية الخمسة الكبرى، المنتخب المغربي والبطولة الاحترافية — تغطية يومية بالعربية.":
        "Latest football news: Europe’s five major leagues, the Morocco national team and Botola Pro — daily coverage in English.",
    '<meta property="og:title" content="آخر الأخبار | الملعب">':
        '<meta property="og:title" content="Latest news | MatchPulse">',
    "<h2>📰 آخر الأخبار</h2>": "<h2>📰 Latest news</h2>",
    "الأخبار أرشيف بتاريخ نشرها (شتنبر 2026) — الأرقام والترتيب الحاليان في صفحات الترتيب والمباريات.":
        "News is archived by publication date (September 2026) — current scores and tables are on the matches and standings pages.",
    'data-cat="المنتخب المغربي">المنتخب المغربي': 'data-cat="Morocco National Team">Morocco National Team',
    'data-cat="البطولة المغربية">البطولة المغربية': 'data-cat="Moroccan Botola">Moroccan Botola',
    'data-cat="الدوري الإسباني">الليغا': 'data-cat="La Liga">La Liga',
    'data-cat="الدوري الإنجليزي">البريميرليغ': 'data-cat="Premier League">Premier League',
    'data-cat="الدوري الفرنسي">الليغ 1': 'data-cat="Ligue 1">Ligue 1',
    'data-cat="all" class="active">الكل': 'data-cat="all" class="active">All',
    "لا توجد أخبار في هذا التصنيف حالياً.": "No news in this category right now.",
    "window.MalaebData.news()": "window.MatchPulseData.news()",
    "مساحة إعلانية داخل المحتوى — In-feed": "In-feed ad space",
    # --- about ---
    "<title>من نحن | الملعب</title>": "<title>About us | MatchPulse</title>",
    "تعرف على موقع الملعب: رسالتنا، فريقنا، ومصادر بياناتنا في تغطية كرة القدم.":
        "About MatchPulse: our mission, our team and our data sources for football coverage.",
    "<h1>من نحن</h1>": "<h1>About us</h1>",
    "<p><strong>الملعب</strong> موقع مغربي مستقل متخصص في تغطية كرة القدم باللغة العربية. انطلقنا في شتنبر 2026 بهدف واحد: أن نمنح المشجع العربي — والمغربي خصوصاً — تجربة متابعة سريعة وموثوقة لأهم ما يحدث في عالم الساحرة المستديرة.</p>":
        "<p><strong>MatchPulse</strong> is an independent football site in English. We launched in September 2026 with one goal: to give fans in the USA, the UK and Europe a fast, reliable way to follow everything that matters in the beautiful game.</p>",
    "<h2>ماذا نقدم؟</h2>": "<h2>What we offer</h2>",
    "<li>⚽ <strong>نتائج مباشرة</strong> ومواعيد مباريات اليوم من أهم البطولات.</li>":
        "<li>⚽ <strong>Live scores</strong> and today’s fixtures from the biggest competitions.</li>",
    "<li>📊 <strong>جداول ترتيب محدّثة</strong> للدوريات الأوروبية الخمسة الكبرى والبطولة الاحترافية المغربية.</li>":
        "<li>📊 <strong>Updated league tables</strong> for Europe’s five major leagues and the Moroccan Botola Pro.</li>",
    "<li>📰 <strong>أخبار يومية</strong> بأسلوب واضح ومباشر، مع اهتمام خاص بالمنتخب المغربي وأسود الأطلس.</li>":
        "<li>📰 <strong>Daily news</strong> in a clear, direct style, with special attention to the Morocco national team and the Atlas Lions.</li>",
    "<li>👟 <strong>سباق الهدافين</strong> وإحصائيات مبسطة لكل دوري.</li>":
        "<li>👟 <strong>Top-scorer races</strong> and simple stats for every league.</li>",
    "<h2>مصادر بياناتنا</h2>": "<h2>Our data sources</h2>",
    "<p>نعتمد على مصادر رياضية موثوقة ومتاحة للعموم لتحديث النتائج والجداول، ونذكر مصدر كل رقم وتاريخ التحقق منه. لا ننشر شائعات على أنها حقائق: أي خبر غير مؤكد يُذكر بصيغة واضحة.</p>":
        "<p>We rely on trusted, public sports sources to update results and tables, and we name the source of every figure and the date it was checked. We never present rumours as facts: anything unconfirmed is clearly labelled as such.</p>",
    "<h2>ملاحظة مهمة</h2>": "<h2>Important note</h2>",
    "<p>موقع الملعب <strong>لا يبث المباريات</strong> ولا يوفر أي روابط مشاهدة غير قانونية. نحترم حقوق البث، وندعو جمهورنا لمتابعة المباريات عبر القنوات الرسمية المرخصة في بلدانهم.</p>":
        "<p>MatchPulse <strong>does not stream matches</strong> and provides no illegal viewing links. We respect broadcast rights and ask our readers to watch matches through the official licensed channels in their countries.</p>",
    "<h2>تواصل معنا</h2>": "<h2>Contact us</h2>",
    '<p>يسعدنا تواصلك: اقتراح، تصحيح معلومة، أو شراكة إعلانية — <a href="contact.html" style="color:var(--accent);font-weight:700">صفحة اتصل بنا</a>.</p>':
        '<p>We’d love to hear from you — a suggestion, a correction, or an advertising partnership: <a href="contact.html" style="color:var(--accent);font-weight:700">our contact page</a>.</p>',
    # --- contact ---
    "<title>اتصل بنا | الملعب</title>": "<title>Contact us | MatchPulse</title>",
    "تواصل مع فريق الملعب: اقتراحات، تصحيحات، شراكات إعلانية.":
        "Contact the MatchPulse team: suggestions, corrections, advertising partnerships.",
    "<h1>اتصل بنا</h1>": "<h1>Contact us</h1>",
    '<p style="color:var(--muted)">راسلنا لأي اقتراح، تصحيح معلومة، أو استفسار حول الإعلان في الموقع — نرد عادة خلال 48 ساعة.</p>':
        '<p style="color:var(--muted)">Write to us with any suggestion, correction, or question about advertising on the site — we usually reply within 48 hours.</p>',
    '<label for="c-name">الاسم الكامل *</label>': '<label for="c-name">Full name *</label>',
    '<label for="c-email">البريد الإلكتروني *</label>': '<label for="c-email">Email address *</label>',
    '<label for="c-subject">الموضوع *</label>': '<label for="c-subject">Subject *</label>',
    "<option>اقتراح</option><option>تصحيح معلومة</option><option>إعلان وشراكات</option><option>موضوع آخر</option>":
        "<option>Suggestion</option><option>Correction</option><option>Advertising &amp; partnerships</option><option>Other topic</option>",
    '<label for="c-msg">رسالتك *</label>': '<label for="c-msg">Your message *</label>',
    '<button class="btn" type="submit">إرسال الرسالة</button>': '<button class="btn" type="submit">Send message</button>',
    "💡 هذا النموذج تجريبي (front-end فقط). لاستقبال الرسائل فعلياً اربطه بخدمة مثل Formspree أو Netlify Forms — راجع README.":
        "💡 This form is a demo (front-end only). To actually receive messages, connect it to a service such as Formspree or Netlify Forms — see the README.",
    "⚠ المرجو ملء جميع الحقول المطلوبة.": "⚠ Please fill in all required fields.",
    "⚠ المرجو إدخال بريد إلكتروني صحيح.": "⚠ Please enter a valid email address.",
    '✅ شكراً "+name+"! تم استلام رسالتك بنجاح وسنرد عليك قريباً.':
        '✅ Thanks "+name+"! Your message was received — we will reply soon.',
    # --- privacy ---
    "<title>سياسة الخصوصية | الملعب</title>": "<title>Privacy policy | MatchPulse</title>",
    "سياسة الخصوصية لموقع الملعب: كيف نجمع البيانات ونستخدمها، وملفات تعريف الارتباط والإعلانات.":
        "MatchPulse privacy policy: how we collect and use data, cookies and advertising.",
    "<h1>سياسة الخصوصية</h1>": "<h1>Privacy policy</h1>",
    '<p style="color:var(--muted)">آخر تحديث: الخميس 19 نونبر 2026</p>':
        '<p style="color:var(--muted)">Last updated: Thursday 19 November 2026</p>',
    "<h2>1. البيانات التي نجمعها</h2>": "<h2>1. Data we collect</h2>",
    "<li><strong>بيانات تقدمها طوعاً:</strong> مثل بريدك الإلكتروني عند الاشتراك في النشرة البريدية، أو الاسم والرسالة عند استخدام نموذج الاتصال.</li>":
        "<li><strong>Data you provide voluntarily:</strong> such as your email address when you subscribe to the newsletter, or your name and message when you use the contact form.</li>",
    "<li><strong>بيانات تقنية:</strong> قد نجمع معلومات مجهولة الهوية عن زيارتك (نوع المتصفح، الصفحات المزارة) لأغراض تحسين الموقع عبر أدوات تحليلات.</li>":
        "<li><strong>Technical data:</strong> we may collect anonymous information about your visit (browser type, pages viewed) to improve the site through analytics tools.</li>",
    "<h2>2. كيف نستخدم بياناتك</h2>": "<h2>2. How we use your data</h2>",
    "<p>نستخدم البيانات فقط للأغراض التي جُمعت من أجلها: إرسال النشرة البريدية، الرد على رسائلك، وتحسين تجربة الموقع. لا نبيع بياناتك الشخصية لأي طرف ثالث.</p>":
        "<p>We use data only for the purposes it was collected for: sending the newsletter, replying to your messages, and improving the site. We never sell your personal data to any third party.</p>",
    "<h2>3. ملفات تعريف الارتباط (Cookies)</h2>": "<h2>3. Cookies</h2>",
    "<p>يستخدم الموقع ملفات تعريف ارتباط أساسية للتشغيل، وقد تستخدم خدمات الإعلانات (مثل Google AdSense عند تفعيلها) ملفات خاصة بها لعرض إعلانات مناسبة. يمكنك تعطيل ملفات الارتباط من إعدادات متصفحك.</p>":
        "<p>The site uses essential cookies to work, and advertising services (such as Google AdSense, when enabled) may use their own cookies to show relevant ads. You can disable cookies from your browser settings.</p>",
    "<h2>4. الإعلانات</h2>": "<h2>4. Advertising</h2>",
    "<p>قد نعرض إعلانات من شبكات إعلانية خارجية. هذه الشبكات قد تجمع بيانات مجهولة لأغراض استهداف الإعلانات وفق سياساتها الخاصة.</p>":
        "<p>We may show ads from external advertising networks. These networks may collect anonymous data for ad targeting under their own policies.</p>",
    "<h2>5. حقوقك</h2>": "<h2>5. Your rights</h2>",
    '<p>يمكنك في أي وقت طلب حذف بريدك من النشرة البريدية أو طلب حذف بياناتك، عبر <a href="contact.html" style="color:var(--accent);font-weight:700">صفحة اتصل بنا</a>.</p>':
        '<p>You can ask at any time to remove your email from the newsletter or to delete your data, via <a href="contact.html" style="color:var(--accent);font-weight:700">our contact page</a>.</p>',
    "<h2>6. التغييرات</h2>": "<h2>6. Changes</h2>",
    "<p>قد نحدّث هذه السياسة من وقت لآخر، وسيُذكر تاريخ آخر تحديث أعلى الصفحة.</p>":
        "<p>We may update this policy from time to time, and the last-update date will be shown at the top of the page.</p>",
    # --- style.css comments ---
    "الملعب | Al Malaeb — التصميم الرئيسي": "MatchPulse — Main design",
    "تصميم رياضي داكن، متجاوب، يعتمد RTL بالكامل": "Dark sporty design, responsive, fully LTR-based",
    "أخضر الملعب": "MatchPulse green",
    "ذهبي للتمييز": "gold for highlights",
    "/* خلفية ملعب خافتة */": "/* Faint stadium background */",
    "/* ---------- الترويسة ---------- */": "/* ---------- Header ---------- */",
    "/* ---------- Ticker للمباريات ---------- */": "/* ---------- Matches ticker ---------- */",
    "/* ---------- البطل (Hero) ---------- */": "/* ---------- Hero ---------- */",
    "/* ---------- الأقسام ---------- */": "/* ---------- Sections ---------- */",
    "/* ---------- بطاقات News ---------- */": "/* ---------- News cards ---------- */",
    "/* ---------- النشرة البريدية ---------- */": "/* ---------- Newsletter ---------- */",
    "/* ---------- المقالات ---------- */": "/* ---------- Articles ---------- */",
    "/* ---------- صفحات عامة ---------- */": "/* ---------- General pages ---------- */",
    "/* ---------- التذييل ---------- */": "/* ---------- Footer ---------- */",
    "/* ---------- إعلانات ---------- */": "/* ---------- Ads ---------- */",
    "/* ---------- متجاوب ---------- */": "/* ---------- Responsive ---------- */",
    # --- ads.txt ---
    "# ملف التحقق من البائعين المعتمدين لـ Google AdSense":
        "# Verification file for Google AdSense authorized sellers",
    "# بعد قبول حسابك في AdSense، استبدل السطر التالي بالسطر الذي يعطيك إياه AdSense":
        "# After your AdSense account is approved, replace the line below with the one AdSense gives you",
    "# الصيغة: google.com, pub-0000000000000000, DIRECT, f08c47fec0942fa0":
        "# Format: google.com, pub-0000000000000000, DIRECT, f08c47fec0942fa0",
}

CPA_SLOT_RE = re.compile(r' *<div class="cpa-slot">.*?</div>\n?', re.DOTALL)


def apply_extra(s):
    for k in sorted(EXTRA, key=len, reverse=True):
        if k in s:
            s = s.replace(k, EXTRA[k])
    return s


def add_offers_links(s):
    """Nav + footer Offers links (after the News link), if not present."""
    if 'href="offers.html">Offers</a>' not in s:
        s = s.replace('<li><a href="news.html">News</a></li>',
                      '<li><a href="news.html">News</a></li>\n      <li><a href="offers.html">Offers</a></li>')
        s = s.replace('<li><a href="news.html" class="active">News</a></li>',
                      '<li><a href="news.html" class="active">News</a></li>\n      <li><a href="offers.html">Offers</a></li>')
    if 'href="offers.html">Free offers</a>' not in s:
        s = s.replace('<li><a href="news.html">Latest news</a></li>',
                      '<li><a href="news.html">Latest news</a></li><li><a href="offers.html">Free offers</a></li>')
    return s


def main():
    pages = ["standings.html", "news.html", "about.html", "contact.html", "privacy.html"]
    for name in pages:
        p = ROOT / name
        s = p.read_text(encoding="utf-8")
        s = apply_extra(s)
        s = transform(s)
        s = add_offers_links(s)
        if name == "news.html":
            # old placeholder -> live offers, byte-identical to the build
            # patch's `new` (ad-infeed div + "\n    " + CPA_SLOT), so the
            # build patch is a no-op on re-runs and never duplicates it.
            s, n = CPA_SLOT_RE.subn("    " + OFFERS_HTML + "\n", s, count=1)
            print(f"news.html: cpa-slot replaced with offers ({n})")
        else:
            # standings.html: build already inserted live offers; drop the old placeholder
            s, n = CPA_SLOT_RE.subn("", s, count=1)
            if n:
                print(f"{name}: old cpa-slot removed ({n})")
        p.write_text(s, encoding="utf-8")
        left = AR.findall(s)
        print(f"{name}: Arabic chars left: {len(left)}" + (f" e.g. {''.join(left[:10])}" if left else ""))

    # ---- style.css (base only; the EN additions block is already English) ----
    p = ROOT / "assets" / "css" / "style.css"
    s = p.read_text(encoding="utf-8")
    s = apply_extra(s)
    s = transform(s)
    ltr_fixes = [
        ("direction: rtl;", "direction: ltr;"),
        ('--font: "Tajawal", "Cairo", "Segoe UI", Tahoma, Arial, sans-serif;',
         '--font: "Inter", "Segoe UI", Tahoma, Arial, sans-serif;'),
        ("table.standings td.team { text-align: right;", "table.standings td.team { text-align: left;"),
        ("tr.pos-ucl td:first-child { border-right:", "tr.pos-ucl td:first-child { border-left:"),
        ("tr.pos-rel td:first-child { border-right:", "tr.pos-rel td:first-child { border-left:"),
        ("tr.pos-playoff td:first-child { border-right:", "tr.pos-playoff td:first-child { border-left:"),
        ("blockquote {\n  border-right: 4px solid var(--accent);",
         "blockquote {\n  border-left: 4px solid var(--accent);"),
        (".article-body ul { margin: 0 20px 18px 0; }", ".article-body ul { margin: 0 0 18px 20px; }"),
        (".page ul { margin-right: 20px; }", ".page ul { margin-left: 20px; }"),
    ]
    for old, new in ltr_fixes:
        if old in s:
            s = s.replace(old, new)
        else:
            print(f"  CSS fix NOT FOUND: {old[:60]!r}")
    p.write_text(s, encoding="utf-8")
    left = AR.findall(s)
    print(f"style.css: Arabic chars left: {len(left)}" + (f" e.g. {''.join(left[:10])}" if left else ""))

    # ---- ads.txt ----
    p = ROOT / "ads.txt"
    s = p.read_text(encoding="utf-8")
    s = apply_extra(s)
    p.write_text(s, encoding="utf-8")
    left = AR.findall(s)
    print(f"ads.txt: Arabic chars left: {len(left)}")


if __name__ == "__main__":
    main()
