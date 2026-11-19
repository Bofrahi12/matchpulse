/* MatchPulse — matches.js: real tabs from data/fixtures-en.json only. No simulation. */
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
  /* Dynamic dates from data/fixtures.json (today_date/tomorrow_date) — no hardcoded dates */
  function dayLabel(iso) {
    if (!iso) return "";
    return new Date(iso + "T12:00:00").toLocaleDateString("en-GB", {weekday: "long", day: "numeric", month: "long", year: "numeric"});
  }
  function shortDay(iso) {
    if (!iso) return "";
    return new Date(iso + "T12:00:00").toLocaleDateString("en-GB", {day: "numeric", month: "long"});
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
      if (t === "today") btn.textContent = "📅 Today " + shortDay(FX.today_date);
      else if (t === "tomorrow") btn.textContent = "📅 Tomorrow " + shortDay(FX.tomorrow_date);
      else if (t === "friday") { const nd = nextDay(); btn.textContent = nd ? "⏭️ " + dayLabel(nd) : "⏭️ Upcoming"; }
    });
  }
  function render() {
    const box = $("matches-box");
    if (!box || !FX) return;
    let html = "";
    const nd = nextDay();
    const back = nd ? ` Back ${dayLabel(nd)}.` : "";
    if (currentTab === "today") {
      html = listHTML(FX.today) || emptyMsg(`No matches today (${dayLabel(FX.today_date)}) in the six leagues.${back}`);
    } else if (currentTab === "tomorrow") {
      html = listHTML(FX.tomorrow) || emptyMsg(`No matches tomorrow (${dayLabel(FX.tomorrow_date)}) in the six leagues.${back}`);
    } else if (currentTab === "friday") {
      const fri = (FX.upcoming || []).filter(m => nd && m.date === nd);
      html = listHTML(fri) || emptyMsg(nd ? `No fixtures scheduled on ${dayLabel(nd)}.` : "No upcoming fixtures scheduled.");
    } else if (currentTab === "upcoming") {
      html = listHTML(FX.upcoming) || emptyMsg("No upcoming fixtures scheduled.");
    } else {
      const r = FX.results || [];
      html = r.length ? listHTML(r) : emptyMsg("No results recorded.");
      if (r.length) {
        const dates = r.map(m => m.date).sort();
        const range = dates[0] === dates[dates.length - 1] ? shortDay(dates[0]) : shortDay(dates[0]) + " – " + shortDay(dates[dates.length - 1]);
        html = `<p class="data-note">Latest results (${range}) — Source: ESPN. All times UTC.</p>` + html;
      }
    }
    box.innerHTML = html;
  }
  document.addEventListener("DOMContentLoaded", async function () {
    await window.loadLogos();
    FX = await window.MatchPulseData.fixtures();
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
