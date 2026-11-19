/* MatchPulse — main.js: strict filter: 6 leagues only, no simulation, no other competitions */
(function () {
  "use strict";
  var ALLOWED_IDS = ["premier-league", "la-liga", "serie-a", "bundesliga", "ligue-1", "botola"];
  var ALLOWED_NAMES = ["Premier League", "La Liga", "Serie A",
    "Bundesliga", "Ligue 1", "Botola Pro", "Botola Pro"];
  window.MATCHPULSE_ALLOWED = ALLOWED_IDS;
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
  window.MatchPulseData = {
    async leagues() {
      const d = await loadJSON("data/leagues-en.json");
      if (d && d.leagues) return d;
      return { leagues: FALLBACK.leagues, updated: (typeof FALLBACK !== "undefined" && FALLBACK.updated) || "" };
    },
    async fixtures() {
      const d = await loadJSON("data/fixtures-en.json");
      if (d) return d;
      return FALLBACK.fixtures;
    },
    async news() {
      const d = await loadJSON("data/news-en.json");
      if (d && d.articles) return d.articles;
      return [];
    }
  };

  /* Logos: local files from data/logos.json — a team without a logo shows text only */
  window.MatchPulseLogos = { leagues: {}, byEn: {}, ready: false, promise: null };
  window.loadLogos = function () {
    if (window.MatchPulseLogos.promise) return window.MatchPulseLogos.promise;
    window.MatchPulseLogos.promise = (async function () {
      try {
        const d = await loadJSON("data/logos.json");
        if (d) {
          window.MatchPulseLogos.leagues = d.leagues || {};
          (d.clubs || []).forEach(c => { window.MatchPulseLogos.byEn[c.en] = c.file; });
        }
      } catch (e) {}
      window.MatchPulseLogos.ready = true;
      return window.MatchPulseLogos;
    })();
    return window.MatchPulseLogos.promise;
  };
  window.logoFor = function (teamName) {
    if (!teamName || teamName === "—") return "";
    const f = window.MatchPulseLogos.byEn[teamName];
    if (!f) return "";
    const esc = String(teamName).replace(/"/g, "&quot;");
    return `<img class="team-logo" src="${f}" alt="Logo of ${esc}" loading="lazy" onerror="this.remove()">`;
  };
  window.leagueLogoFor = function (leagueId) {
    const f = window.MatchPulseLogos.leagues[leagueId];
    if (!f) return "";
    return `<img class="league-logo" src="${f}" alt="League logo" loading="lazy" onerror="this.remove()">`;
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
          if (note) { note.textContent = "Please enter a valid email address."; note.style.color = "#ff4d5e"; }
          return;
        }
        if (note) { note.textContent = "Thanks! Your subscription is confirmed. ⚽"; note.style.color = "#22e07a"; }
        input.value = "";
      });
    });
    const closeAd = document.querySelector(".close-ad");
    if (closeAd) closeAd.addEventListener("click", () => {
      document.querySelector(".anchored-ad").style.display = "none";
    });
  });

  /* Ticker: the six leagues only — no obscure leagues */
  window.renderTicker = async function (elId) {
    const el = document.getElementById(elId);
    if (!el) return;
    const fx = await window.MatchPulseData.fixtures();
    const items = [];
    onlyAllowed(fx.live || []).forEach(m => {
      items.push(`<span class="ticker-item"><span class="live-dot">● LIVE ${m.minute}'</span> <b>${m.home} ${m.home_goals} - ${m.away_goals} ${m.away}</b></span>`);
    });
    onlyAllowed(fx.upcoming || []).slice(0, 8).forEach(m => {
      items.push(`<span class="ticker-item">${m.home} × ${m.away} <b>${m.date_label || m.date} ${m.time || ""}</b></span>`);
    });
    const liveCount = onlyAllowed(fx.live || []).length;
    const head = liveCount ? "" : "<span class='ticker-item'>No live matches right now — coming up:</span>";
    el.innerHTML = head + (items.join("") || "<span class='ticker-item'>No fixtures scheduled in the six leagues right now</span>");
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
      <thead><tr><th>#</th><th>Team</th><th>P</th><th>W</th><th>D</th><th>L</th><th>GD</th><th>Pts</th></tr></thead>
      <tbody>${rows}</tbody></table></div>`;
  };

  window.matchRowHTML = function (m) {
    const isLive = m.status === "live";
    const isFin = m.status === "finished";
    const score = isLive || isFin
      ? `<span class="score${isLive ? " live" : ""}">${m.home_goals} - ${m.away_goals}</span>`
      : `<span class="score">${m.time || "—"}</span>`;
    const badge = isLive
      ? `<span class="status-badge live">● LIVE ${m.minute || ""}'</span>`
      : isFin
        ? `<span class="status-badge finished">Full time</span>`
        : `<span class="status-badge upcoming">Not started yet</span>`;
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
