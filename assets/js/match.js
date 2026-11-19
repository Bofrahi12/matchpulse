/* MatchPulse — match.js: match detail page (?id=) — verified data only, the rest is an explicit placeholder */
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
    const fx = await window.MatchPulseData.fixtures();
    const all = [].concat(fx.live || [], fx.today || [], fx.tomorrow || [], fx.upcoming || [], fx.results || []);
    const m = all.find(x => x.id === id);
    if (!m) {
      box.innerHTML = `<div class="placeholder-box"><h2 style="margin-bottom:8px">Match not found</h2><p>The link is wrong or the match is not in the six leagues. <a href="matches.html" style="color:var(--accent)">← Back to fixtures</a></p></div>`;
      return;
    }
    const isFin = m.status === "finished";
    const score = isFin ? `${m.home_goals} - ${m.away_goals}` : (m.time || "—");
    const status = isFin ? "Full time" : `Upcoming match — ${m.date_label || m.date} ${m.time ? "• " + m.time + " UTC" : "• Kick-off time TBC"}`;
    document.title = `${m.home} × ${m.away} | MatchPulse`;
    const h1 = document.getElementById("match-h1");
    if (h1) h1.textContent = `${m.home} × ${m.away}`;
    const infoVenue = m.venue || m.venue_note || "To be confirmed";
    const infoRef = m.referee || "To be confirmed";
    const infoChan = m.channel || "To be confirmed";
    const infoTime = isFin ? "Full time" : ((m.date_label || m.date || "") + (m.time ? " • " + m.time + " UTC" : " • Kick-off time TBC"));
    function statBar(label, h, a) {
      const t = (h || 0) + (a || 0);
      const hp = t ? Math.round(100 * h / t) : 50;
      return `<div class="stat-row"><span><b>${h}</b></span><div><div style="text-align:center;font-size:.8rem;color:var(--muted)">${label}</div><div class="stat-bar"><i class="h" style="width:${hp}%"></i><i class="a" style="width:${100 - hp}%"></i></div></div><span style="text-align:left"><b>${a}</b></span></div>`;
    }
    const st = m.stats || null;
    const statsHTML = st ? (
      statBar("Possession %", st.possession_home, st.possession_away)
      + statBar("Shots", st.shots_home, st.shots_away)
      + statBar("Shots on target", st.shots_on_target_home, st.shots_on_target_away)
      + statBar("Corners", st.corners_home, st.corners_away)
      + `<p style="color:var(--muted);font-size:.78rem;margin-top:10px">Source: ${esc(st.source || "—")}</p>`
    ) : `<div class="placeholder-box">Statistics are not available for this match yet.<br>They will appear here (possession, shots, corners) once verified from an official source.</div>`;
    const eventsHTML = (m.events && m.events.length) ? m.events.map(e =>
      `<div class="event-row"><span class="ev-min">${esc(e.minute || "")}'</span><span class="ev-type">${esc(e.type || "")}</span><b>${esc(e.player || "")}</b><span style="color:var(--muted)">${esc(e.team || "")}</span></div>`).join("")
      : `<div class="placeholder-box">No verified events for this match yet (goals, cards, substitutions).<br>Events will be added once verified from an official source.</div>`;
    box.innerHTML = `
    <div class="scoreboard">
      <div class="teams"><span class="team-name">${window.logoFor(m.home)}${esc(m.home)}</span>
      <span class="big-score">${score}</span>
      <span class="team-name">${window.logoFor(m.away)}${esc(m.away)}</span></div>
      <div class="status">${m.league_name} • ${status}</div>
      <div class="status" style="font-size:.8rem">Source: ${esc(m.source || "—")} — Last checked: ${esc(fx.updated || "")}</div>
    </div>
    <div class="match-info">
      <span><span class="lbl">🏟️ Stadium:</span><b>${esc(infoVenue)}</b></span>
      <span><span class="lbl">Referee:</span><b>${esc(infoRef)}</b></span>
      <span><span class="lbl">📺 TV channel:</span><b>${esc(infoChan)}</b></span>
      <span><span class="lbl">🕐 Kick-off:</span><b>${esc(infoTime)}</b></span>
    </div>
    <div class="match-tabs">
      <button data-mtab="events" class="active">Events</button>
      <button data-mtab="stats">Statistics</button>
      <button data-mtab="lineups">Lineups</button>
      <button data-mtab="h2h">Head-to-head</button>
    </div>
    <div class="mtab-panel" data-panel="events">
      ${eventsHTML}
    </div>
    <div class="mtab-panel" data-panel="stats" style="display:none">${statsHTML}</div>
    <div class="mtab-panel" data-panel="lineups" style="display:none">
      <div class="placeholder-box">The official lineups are not verified yet — they are published one hour before kick-off from an official source.</div>
    </div>
    <div class="mtab-panel" data-panel="h2h" style="display:none">
      <div class="placeholder-box">The head-to-head record between the two teams is not verified yet — it will be added from an official source.</div>
    </div>
    <p><a href="matches.html" style="color:var(--accent);font-weight:700">← Back to all fixtures</a></p>`;
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
