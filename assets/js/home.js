/* MatchPulse — home.js: the homepage keeps the international-break message (static hero in HTML) */
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
      const articles = await window.MatchPulseData.news();
      if (articles.length) {
        document.querySelector("#home-news").innerHTML = articles.slice(0, 6).map(newsCard).join("");
      }
    } catch (e) {}
    try {
      const fx = await window.MatchPulseData.fixtures();
      const up = (fx.upcoming || []).filter(window.isAllowedLeague).slice(0, 6);
      document.querySelector("#home-matches").innerHTML = up.length
        ? up.map(window.matchRowHTML).join("")
        : `<p style="color:var(--muted)">No fixtures scheduled right now.</p>`;
    } catch (e) {}
    try {
      const data = await window.MatchPulseData.leagues();
      const pick = ["premier-league", "la-liga", "botola"]
        .map(id => data.leagues.find(l => l.id === id)).filter(Boolean);
      document.querySelector("#home-tables").innerHTML = pick.map(l => `
        <div>
          <div class="section-head" style="margin-bottom:10px">
            <h2 style="font-size:1.05rem">${l.name}</h2>
            <a class="more" href="league-${l.id}.html">Full table →</a>
          </div>
          ${window.standingsTableHTML(l, 5)}
          <p style="color:var(--muted);font-size:.78rem;margin-top:6px">Top 5 — full table on the league page — last checked: ${data.updated || ""}</p>
        </div>`).join("");
    } catch (e) {}
  });
})();
