/* ─── Vedica – Vimshottari Dasha Engine ─────────────────────────────────── */

const VIMS_ORDER = ['Sun','Moon','Mars','Rahu','Jupiter','Saturn','Mercury','Ketu','Venus'];
const VIMS_YEARS = { Sun:6, Moon:10, Mars:7, Rahu:18, Jupiter:16, Saturn:19, Mercury:17, Ketu:7, Venus:20 };
const VIMS_GLYPHS = { Sun:'☉', Moon:'☽', Mars:'♂', Rahu:'☊', Jupiter:'♃', Saturn:'♄', Mercury:'☿', Ketu:'☋', Venus:'♀' };
const VIMS_COLORS = {
  Sun:'#f59e0b', Moon:'#e2e8f0', Mars:'#ef4444', Rahu:'#8b5cf6',
  Jupiter:'#f97316', Saturn:'#6366f1', Mercury:'#10b981', Ketu:'#14b8a6', Venus:'#ec4899'
};
const DASHA_LEVEL_NAMES = ['Mahadasha','Antardasha','Pratyantar','Sookshma','Prana'];
const MS_PER_YEAR = 365.25 * 24 * 3600 * 1000;
const TOTAL_YEARS = 120;

let _birthMs = null; // set in renderDasha, used by lazy toggle handlers

// ─── Core calculation ──────────────────────────────────────────────────────

function calcSubPeriods(lordName, startMs, endMs) {
  const startIdx = VIMS_ORDER.indexOf(lordName);
  const parentDurMs = endMs - startMs;
  const periods = [];
  let cur = startMs;
  for (let i = 0; i < 9; i++) {
    const sub = VIMS_ORDER[(startIdx + i) % 9];
    const durMs = parentDurMs * (VIMS_YEARS[sub] / TOTAL_YEARS);
    const end = cur + durMs;
    periods.push({ planet: sub, start: cur, end });
    cur = end;
  }
  return periods;
}

// Returns the active chain [maha, antar, pratyantar, sookshma, prana] at `nowMs`
function getDashaChain(dashaProcessed, nowMs) {
  // Build mahadashas array sorted by start date
  const mahas = Object.entries(dashaProcessed)
    .map(([planet, d]) => ({ planet, start: Date.parse(d.start_date), end: Date.parse(d.end_date), years: d.years }))
    .sort((a, b) => a.start - b.start);

  // Find active maha
  const maha = mahas.find(m => nowMs >= m.start && nowMs < m.end) || mahas[mahas.length - 1];
  const chain = [maha];

  let prev = maha;
  for (let level = 1; level < 5; level++) {
    const subs = calcSubPeriods(prev.planet, prev.start, prev.end);
    const active = subs.find(s => nowMs >= s.start && nowMs < s.end) || subs[subs.length - 1];
    chain.push(active);
    prev = active;
  }
  return chain;
}

function fmtDate(ms) {
  const d = new Date(ms);
  return d.toLocaleDateString('en-IN', { day: 'numeric', month: 'short', year: 'numeric' });
}

function fmtDateShort(ms) {
  const d = new Date(ms);
  return d.toLocaleDateString('en-IN', { month: 'short', year: 'numeric' });
}

function fmtDateDDMMYYYY(ms) {
  const d = new Date(ms);
  const day = String(d.getDate()).padStart(2, '0');
  const month = String(d.getMonth() + 1).padStart(2, '0');
  const year = d.getFullYear();
  return `${day}-${month}-${year}`;
}

function progressPct(start, end, now) {
  return Math.min(100, Math.max(0, Math.round((now - start) / (end - start) * 100)));
}

function timeLeft(endMs, nowMs) {
  const diff = endMs - nowMs;
  if (diff <= 0) return 'Completed';
  const days = Math.floor(diff / (24 * 3600 * 1000));
  if (days > 365) return `${Math.floor(days / 365)}y ${Math.floor((days % 365) / 30)}m`;
  if (days > 30) return `${Math.floor(days / 30)}m ${days % 30}d`;
  return `${days}d`;
}

function formatDuration(ms) {
  const totalDays = Math.floor(ms / (24 * 3600 * 1000));
  const years = Math.floor(totalDays / 365.25);
  const remainingDays = Math.floor(totalDays % 365.25);
  const months = Math.floor(remainingDays / 30);
  const days = Math.floor(remainingDays % 30);
  let parts = [];
  if (years) parts.push(`${years}y`);
  if (months) parts.push(`${months}m`);
  if (days && !years) parts.push(`${days}d`);
  return parts.join(' ') || '0d';
}

// ─── Render ────────────────────────────────────────────────────────────────

function renderDasha(dashaData) {
  const container = document.getElementById('dasha-container');
  if (!container) return;

  const processed = dashaData?.processed;
  if (!processed || Object.keys(processed).length === 0) {
    container.innerHTML = `<div style="color:var(--text3);text-align:center;padding:2rem;">Dasha data not available for this chart. Recalculate to generate.</div>`;
    return;
  }

  const now = Date.now();
  _birthMs = dashaData.birth_date ? Date.parse(dashaData.birth_date) : null;
  const birthMs = _birthMs;

  // Build mahadasha array sorted chronologically
  const allMahas = Object.entries(processed)
    .map(([planet, d]) => ({ planet, start: Date.parse(d.start_date), end: Date.parse(d.end_date), years: d.years, startRaw: d.start_date, endRaw: d.end_date }))
    .sort((a, b) => a.start - b.start);

  // Include dashas that were active at or after birth (e.g. Rahu may start before birth but still relevant)
  let mahas = allMahas;
  if (birthMs) {
    mahas = allMahas.filter(m => m.end > birthMs);
  }

  const chain = getDashaChain(processed, now);
  const totalSpan = mahas[mahas.length - 1].end - mahas[0].start;

  // ── Current Dasha Status Banner ──────────────────────────────────────────
  const currentBanner = buildCurrentBanner(chain, now);

  // ── Mahadasha Timeline Bar ───────────────────────────────────────────────
  const timeline = buildTimeline(mahas, now, totalSpan, birthMs);

  // ── Accordion: all 9 mahadashas ──────────────────────────────────────────
  const accordion = buildAccordion(mahas, chain, now, birthMs);

  container.innerHTML = `
    <div class="dasha-wrap">
      ${currentBanner}
      ${timeline}
      ${accordion}
    </div>
  `;

  // Attach expand/collapse handlers
  container.querySelectorAll('.dasha-maha-header').forEach(header => {
    header.addEventListener('click', () => toggleMaha(header));
  });
  container.querySelectorAll('.dasha-antar-header').forEach(header => {
    header.addEventListener('click', e => { e.stopPropagation(); toggleAntar(header); });
  });
}

// ─── Current Banner ────────────────────────────────────────────────────────

function buildCurrentBanner(chain, now) {
  const [maha, antar, pratyantar, sookshma, prana] = chain;
  const pct = progressPct(maha.start, maha.end, now);

  const crumbs = chain.map((c, i) => {
    const g = VIMS_GLYPHS[c.planet];
    const col = VIMS_COLORS[c.planet];
    const sep = i < chain.length - 1 ? `<span style="color:var(--text3);margin:0 .3rem;">›</span>` : '';
    return `<span style="color:${col};font-weight:700;">${g} ${c.planet}</span>${sep}`;
  }).join('');

  const mahaLeft = timeLeft(maha.end, now);
  const antarLeft = timeLeft(antar.end, now);

  return `
  <div class="dasha-banner">
    <div style="display:flex;align-items:center;gap:.5rem;flex-wrap:wrap;margin-bottom:.75rem;">
      <span class="dasha-badge" style="background:rgba(139,92,246,.15);border-color:rgba(139,92,246,.3);color:var(--accent2);">NOW</span>
      <div style="font-size:.85rem;color:var(--text2);">${crumbs}</div>
    </div>

    <div style="display:grid;grid-template-columns:1fr 1fr;gap:.75rem;margin-bottom:1rem;">
      <div class="dasha-stat-card">
        <div class="dasha-stat-label">Mahadasha</div>
        <div class="dasha-stat-value" style="color:${VIMS_COLORS[maha.planet]};">${VIMS_GLYPHS[maha.planet]} ${maha.planet}</div>
        <div class="dasha-stat-meta">${fmtDateShort(maha.start)} – ${fmtDateShort(maha.end)}</div>
        <div class="dasha-progress-bar" style="margin-top:.5rem;">
          <div class="dasha-progress-fill" style="width:${pct}%;background:${VIMS_COLORS[maha.planet]};"></div>
        </div>
        <div style="font-size:.7rem;color:var(--text3);margin-top:.3rem;">${pct}% done · ${mahaLeft} remaining</div>
      </div>
      <div class="dasha-stat-card">
        <div class="dasha-stat-label">Antardasha</div>
        <div class="dasha-stat-value" style="color:${VIMS_COLORS[antar.planet]};">${VIMS_GLYPHS[antar.planet]} ${antar.planet}</div>
        <div class="dasha-stat-meta">${fmtDate(antar.start)} – ${fmtDate(antar.end)}</div>
        <div class="dasha-progress-bar" style="margin-top:.5rem;">
          <div class="dasha-progress-fill" style="width:${progressPct(antar.start,antar.end,now)}%;background:${VIMS_COLORS[antar.planet]};"></div>
        </div>
        <div style="font-size:.7rem;color:var(--text3);margin-top:.3rem;">${antarLeft} remaining</div>
      </div>
    </div>

    <div style="display:flex;flex-wrap:wrap;gap:.5rem;">
      ${[['Pratyantar', pratyantar], ['Sookshma', sookshma], ['Prana', prana]].map(([label, d]) => `
        <div class="dasha-mini-card">
          <span style="display:inline-block;width:8px;height:8px;border-radius:50%;background:#10b981;margin-right:.4rem;vertical-align:middle;"></span>
          <span style="color:var(--text3);font-size:.65rem;text-transform:uppercase;letter-spacing:.06em;">${label}</span>
          <span style="color:${VIMS_COLORS[d.planet]};font-weight:700;font-size:.82rem;margin-left:.4rem;">${VIMS_GLYPHS[d.planet]} ${d.planet}</span>
          <span style="color:var(--text3);font-size:.7rem;margin-left:.4rem;">${fmtDate(d.start)} – ${fmtDate(d.end)}</span>
        </div>
      `).join('')}
    </div>
  </div>`;
}

// ─── Timeline Bar ──────────────────────────────────────────────────────────

function buildTimeline(mahas, now, totalSpan, birthMs) {
  // Clip display to birth date — the timeline starts at birth, not at first dasha start
  const displayStart = birthMs ? Math.max(birthMs, mahas[0].start) : mahas[0].start;
  const displayEnd = mahas[mahas.length - 1].end;
  const displaySpan = displayEnd - displayStart;

  const nowPct = Math.min(100, Math.max(0, (now - displayStart) / displaySpan * 100));
  const startLabel = birthMs ? new Date(birthMs).getFullYear() : new Date(displayStart).getFullYear();
  const endLabel = new Date(displayEnd).getFullYear();

  const bars = mahas.map((m, idx) => {
    // Clip each bar to the displayStart (trims pre-birth portion of first dasha)
    const visStart = Math.max(m.start, displayStart);
    const visEnd = m.end;
    const widthPct = (visEnd - visStart) / displaySpan * 100;
    const isActive = now >= m.start && now < m.end;
    const isPast = now >= m.end;
    const opacity = isPast ? '0.35' : '1';
    const durationYears = Math.round((m.end - m.start) / MS_PER_YEAR * 10) / 10;
    // For first mahadasha, show birth date as start date if it's partial
    const isFirstPartial = idx === 0 && birthMs && m.start < birthMs && m.end > birthMs;
    const displayStartDate = isFirstPartial ? fmtDate(birthMs) : fmtDate(m.start);
    return `
      <div class="dasha-tl-bar" style="width:${widthPct}%;opacity:${opacity};" data-planet="${m.planet}">
        <div class="dasha-tl-fill" style="background:${VIMS_COLORS[m.planet]};${isActive ? 'filter:brightness(1.2);' : ''}"></div>
        <div class="dasha-tl-label">${VIMS_GLYPHS[m.planet]}<span class="dasha-tl-name">${m.planet}</span></div>
        <div class="dasha-tl-tooltip">${fmtDateDDMMYYYY(isFirstPartial ? birthMs : m.start)} to ${fmtDateDDMMYYYY(m.end)} (${durationYears} years)</div>
      </div>`;
  }).join('');

  return `
  <div class="dasha-timeline-wrap">
    <div style="font-size:.72rem;text-transform:uppercase;letter-spacing:.08em;color:var(--text3);margin-bottom:.6rem;">Mahadasha Timeline</div>
    <div class="dasha-timeline" style="position:relative;">
      ${bars}
      <div class="dasha-tl-now" style="left:${nowPct}%;" title="Today">
        <div class="dasha-tl-now-line"></div>
        <div class="dasha-tl-now-dot"></div>
      </div>
    </div>
    <div style="position:relative;height:1.1rem;margin-top:.3rem;font-size:.68rem;color:var(--text3);">
      <span style="position:absolute;left:0;">${startLabel}</span>
      <span style="position:absolute;left:${nowPct}%;transform:translateX(-50%);color:var(--accent2);font-weight:600;white-space:nowrap;">▲ Now</span>
      <span style="position:absolute;right:0;">${endLabel}</span>
    </div>
  </div>`;
}

// ─── Accordion ────────────────────────────────────────────────────────────

function buildAccordion(mahas, chain, now, birthMs) {
  const activeMahaIdx = mahas.findIndex(m => now >= m.start && now < m.end);

  const items = mahas.map((maha, mi) => {
    const isActive = mi === activeMahaIdx;
    const isPast = now >= maha.end;
    const isPartial = birthMs && maha.start < birthMs && maha.end > birthMs;
    const displayStart = isPartial ? birthMs : maha.start;
    const pct = progressPct(maha.start, maha.end, now);
    const statusDot = isActive ? `<span class="dasha-dot-active"></span>` : (isPast ? `<span class="dasha-dot-past"></span>` : `<span class="dasha-dot-future"></span>`);
    
    // Balance at birth: only for first mahadasha that contains birth
    const isFirstMaha = mi === 0;
    const balanceAtBirth = isFirstMaha && birthMs && maha.start < birthMs && maha.end > birthMs
      ? maha.end - birthMs
      : null;

    // Pre-build antardasha list for active maha
    const antarItems = isActive ? buildAntarList(maha, chain[1], now, birthMs) : '';

    return `
    <div class="dasha-maha-item ${isActive ? 'is-active' : ''}" data-planet="${maha.planet}" data-start="${maha.start}" data-end="${maha.end}">
      <div class="dasha-maha-header" data-open="${isActive ? 'true' : 'false'}">
        <div style="display:flex;align-items:center;gap:.6rem;flex:1;min-width:0;">
          ${statusDot}
          <span style="font-size:1.1rem;color:${VIMS_COLORS[maha.planet]};">${VIMS_GLYPHS[maha.planet]}</span>
          <span style="font-weight:700;color:${isActive ? VIMS_COLORS[maha.planet] : 'var(--text)'};">${maha.planet}</span>
          <span style="color:var(--text3);font-size:.78rem;">${maha.years} yrs${balanceAtBirth ? ` <span style="color:var(--text4);">(${formatDuration(balanceAtBirth)} balance)</span>` : ''}</span>
          ${isActive ? `<span class="dasha-badge" style="background:rgba(139,92,246,.12);border-color:rgba(139,92,246,.3);color:var(--accent2);">Active</span>` : ''}
        </div>
        <div style="display:flex;align-items:center;gap:1rem;flex-shrink:0;">
          <div style="text-align:right;">
            <div style="font-size:.78rem;color:var(--text2);">${fmtDateShort(displayStart)} – ${fmtDateShort(maha.end)}</div>
            ${isPartial ? `<div style="font-size:.65rem;color:var(--text3);">from birth</div>` : ''}
            ${isActive ? `<div style="font-size:.68rem;color:var(--text3);">${pct}% · ${timeLeft(maha.end,now)} left</div>` : ''}
          </div>
          ${isActive ? `
          <div style="width:48px;height:48px;position:relative;flex-shrink:0;">
            <svg viewBox="0 0 36 36" style="width:100%;height:100%;transform:rotate(-90deg);">
              <circle cx="18" cy="18" r="15.9" fill="none" stroke="var(--border)" stroke-width="2.5"/>
              <circle cx="18" cy="18" r="15.9" fill="none" stroke="${VIMS_COLORS[maha.planet]}" stroke-width="2.5"
                stroke-dasharray="${pct} ${100-pct}" stroke-linecap="round"/>
            </svg>
            <span style="position:absolute;inset:0;display:flex;align-items:center;justify-content:center;font-size:.6rem;font-weight:700;color:${VIMS_COLORS[maha.planet]};">${pct}%</span>
          </div>` : ''}
          <span class="dasha-chevron" style="color:var(--text3);font-size:.9rem;transition:transform .25s;">▼</span>
        </div>
      </div>

      <div class="dasha-maha-body" style="${isActive ? '' : 'display:none;'}">
        ${isActive
          ? antarItems
          : `<div class="dasha-antar-placeholder" data-maha-planet="${maha.planet}" data-maha-start="${maha.start}" data-maha-end="${maha.end}" data-birth="${birthMs||''}"></div>`}
      </div>
    </div>`;
  }).join('');

  return `
  <div class="dasha-accordion">
    <div style="font-size:.72rem;text-transform:uppercase;letter-spacing:.08em;color:var(--text3);margin-bottom:.75rem;padding:0 .25rem;">All Mahadasha Periods</div>
    ${items}
  </div>`;
}

// ─── Antardasha List ───────────────────────────────────────────────────────

function buildAntarList(maha, activeAntar, now, birthMs) {
  let antars = calcSubPeriods(maha.planet, maha.start, maha.end);
  // Filter out antardasha sub-periods that ended before birth
  if (birthMs) antars = antars.filter(a => a.end > birthMs);
  const activeAntarPlanet = activeAntar?.planet;
  // Find which antar was active at birth (for special marking)
  const birthAntarPlanet = birthMs ? antars.find(a => a.start <= birthMs && a.end > birthMs)?.planet : null;

  const items = antars.map(antar => {
    const isActive = antar.planet === activeAntarPlanet && now >= antar.start && now < antar.end;
    const isPast = now >= antar.end;
    const pct = progressPct(antar.start, antar.end, now);
    const statusDot = isActive ? `<span class="dasha-dot-active" style="width:.45rem;height:.45rem;"></span>` : (isPast ? `<span class="dasha-dot-past" style="width:.45rem;height:.45rem;"></span>` : `<span class="dasha-dot-future" style="width:.45rem;height:.45rem;"></span>`);

    // Pre-calc pratyantar if active
    const isPartialAntar = birthMs && antar.start < birthMs && antar.end > birthMs;
    const antarDisplayStart = isPartialAntar ? birthMs : antar.start;
    const pratyanBody = isActive ? buildPratyanList(antar, now, false, birthMs) : `<div class="dasha-pratyan-placeholder" data-planet="${antar.planet}" data-start="${antar.start}" data-end="${antar.end}" data-birth="${birthMs||''}"></div>`;

    return `
    <div class="dasha-antar-item ${isActive ? 'is-active' : ''}">
      <div class="dasha-antar-header" data-open="${isActive ? 'true' : 'false'}">
        <div style="display:flex;align-items:center;gap:.5rem;flex:1;min-width:0;">
          ${statusDot}
          <span style="color:${VIMS_COLORS[antar.planet]};font-size:.9rem;">${VIMS_GLYPHS[antar.planet]}</span>
          <span style="font-weight:600;font-size:.85rem;color:${isActive ? VIMS_COLORS[antar.planet] : 'var(--text)'};">${antar.planet}</span>
          ${isActive ? `<span class="dasha-badge" style="font-size:.6rem;background:rgba(139,92,246,.1);border-color:rgba(139,92,246,.25);color:var(--accent3);">Active</span>` : ''}
          ${(!isActive && antar.planet === birthAntarPlanet) ? `<span class="dasha-badge" style="font-size:.6rem;background:rgba(20,184,166,.1);border-color:rgba(20,184,166,.3);color:#14b8a6;">At Birth</span>` : ''}
        </div>
        <div style="display:flex;align-items:center;gap:.75rem;flex-shrink:0;">
          <div style="text-align:right;font-size:.72rem;color:var(--text2);">
            ${fmtDate(antarDisplayStart)} – ${fmtDate(antar.end)}
            ${isActive ? `<div style="color:var(--text3);">${timeLeft(antar.end,now)} left</div>` : ''}
          </div>
          ${isActive ? `
          <div style="display:flex;align-items:center;gap:.4rem;">
            <div class="dasha-progress-bar" style="width:50px;">
              <div class="dasha-progress-fill" style="width:${pct}%;background:${VIMS_COLORS[antar.planet]};"></div>
            </div>
            <span style="font-size:.65rem;font-weight:700;color:${VIMS_COLORS[antar.planet]};">${pct}%</span>
          </div>` : ''}
          <span class="dasha-chevron" style="color:var(--text3);font-size:.75rem;transition:transform .25s;">▼</span>
        </div>
      </div>
      <div class="dasha-antar-body" style="${isActive ? '' : 'display:none;'}">
        ${pratyanBody}
      </div>
    </div>`;
  }).join('');

  return `<div class="dasha-antar-list">${items}</div>`;
}

// ─── Pratyantar List (with Sookshma + Prana inline) ───────────────────────

function buildPratyanList(antar, now, showAll, birthMs) {
  const pratyans = calcSubPeriods(antar.planet, antar.start, antar.end);
  // Filter pre-birth pratyantars; for active antar also filter completed ones
  let visible = birthMs ? pratyans.filter(p => p.end > birthMs) : pratyans;
  if (!showAll) visible = visible.filter(p => now < p.end);
  // Find the first pratyantar active at birth (for At Birth badge)
  const birthPratyanPlanet = birthMs ? visible.find(p => p.start <= birthMs && p.end > birthMs)?.planet : null;

  const items = visible.map(p => {
    const isActive = now >= p.start && now < p.end;
    const isAtBirth = birthMs && p.planet === birthPratyanPlanet && p.start < birthMs;
    const displayStart = isAtBirth ? birthMs : p.start;

    let sookshmaHtml = '';
    if (isActive) {
      const sookshmas = calcSubPeriods(p.planet, p.start, p.end);
      const pastS   = sookshmas.filter(s => now >= s.end);
      const activeS = sookshmas.find(s => now >= s.start && now < s.end);
      const futureS = sookshmas.filter(s => now < s.start);

      const chip = (s, dim) => `<span style="display:inline-flex;align-items:center;gap:.22rem;padding:.18rem .45rem;border:1px solid ${dim ? 'var(--border)' : VIMS_COLORS[s.planet]+'30'};border-radius:4px;font-size:.67rem;color:${dim ? 'var(--text3)' : VIMS_COLORS[s.planet]};opacity:${dim ? '.45' : '.85'};">
        ${VIMS_GLYPHS[s.planet]} ${s.planet}<span style="opacity:.6;font-size:.6rem;margin-left:.15rem;">${fmtDate(s.start)}</span></span>`;

      let activeSHtml = '';
      if (activeS) {
        const pranas = calcSubPeriods(activeS.planet, activeS.start, activeS.end);
        const pranaChips = pranas.map(pr => {
          const prActive = now >= pr.start && now < pr.end;
          return `<span class="dasha-prana-chip ${prActive ? 'prana-active' : ''}" style="${prActive ? `background:${VIMS_COLORS[pr.planet]}15;color:${VIMS_COLORS[pr.planet]};border-color:${VIMS_COLORS[pr.planet]}40;font-weight:700;` : 'color:var(--text3);border-color:var(--border);'}">
            ${VIMS_GLYPHS[pr.planet]} ${pr.planet}<span style="font-size:.58rem;opacity:.65;margin-left:.2rem;">${fmtDate(pr.start)}</span>
            ${prActive ? `<span class="dasha-dot-active" style="width:.35rem;height:.35rem;margin-left:.2rem;flex-shrink:0;"></span>` : ''}
          </span>`;
        }).join('');

        activeSHtml = `
        <div style="margin:.35rem 0;padding:.4rem .55rem;background:${VIMS_COLORS[activeS.planet]}08;border:1px solid ${VIMS_COLORS[activeS.planet]}30;border-radius:6px;">
          <div style="display:flex;align-items:center;gap:.35rem;margin-bottom:.4rem;">
            <span class="dasha-dot-active" style="width:.45rem;height:.45rem;flex-shrink:0;"></span>
            <span style="color:${VIMS_COLORS[activeS.planet]};font-size:.85rem;">${VIMS_GLYPHS[activeS.planet]}</span>
            <span style="font-weight:700;font-size:.78rem;color:${VIMS_COLORS[activeS.planet]};">${activeS.planet}</span>
            <span style="font-size:.65rem;color:var(--text3);">${fmtDate(activeS.start)} – ${fmtDate(activeS.end)}</span>
            <span style="font-size:.58rem;text-transform:uppercase;letter-spacing:.06em;color:var(--text3);margin-left:auto;">Sookshma · active</span>
          </div>
          <div style="font-size:.58rem;text-transform:uppercase;letter-spacing:.07em;color:var(--text3);margin-bottom:.3rem;">Prana Dasha</div>
          <div style="display:flex;flex-wrap:wrap;gap:.28rem;">${pranaChips}</div>
        </div>`;
      }

      sookshmaHtml = `
      <div style="margin:.4rem 0 .1rem .4rem;padding:.35rem .5rem;border-left:1px dashed var(--border);">
        <div style="font-size:.58rem;text-transform:uppercase;letter-spacing:.07em;color:var(--text3);margin-bottom:.35rem;">Sookshma Dasha</div>
        ${pastS.length ? `<div style="display:flex;flex-wrap:wrap;gap:.28rem;margin-bottom:.3rem;">${pastS.map(s => chip(s, true)).join('')}</div>` : ''}
        ${activeSHtml}
        ${futureS.length ? `<div style="display:flex;flex-wrap:wrap;gap:.28rem;margin-top:.3rem;">${futureS.map(s => chip(s, false)).join('')}</div>` : ''}
      </div>`;
    }

    return `
    <div class="dasha-pratyan-row ${isActive ? 'is-active' : ''}" style="border-left:2px solid ${isActive ? VIMS_COLORS[p.planet] : 'var(--border)'};padding:.35rem .6rem;margin:.2rem 0;border-radius:0 4px 4px 0;${isActive ? `background:${VIMS_COLORS[p.planet]}08;` : ''}">
      <div style="display:flex;align-items:center;gap:.4rem;flex-wrap:wrap;">
        ${isActive ? `<span class="dasha-dot-active"></span>` : ''}
        <span style="color:${VIMS_COLORS[p.planet]};font-size:.85rem;">${VIMS_GLYPHS[p.planet]}</span>
        <span style="font-size:.78rem;font-weight:600;color:${isActive ? VIMS_COLORS[p.planet] : 'var(--text)'};">${p.planet}</span>
        <span style="font-size:.68rem;color:var(--text3);">${fmtDate(displayStart)} – ${fmtDate(p.end)}</span>
        ${isActive ? `<span class="dasha-badge" style="font-size:.58rem;background:${VIMS_COLORS[p.planet]}15;border-color:${VIMS_COLORS[p.planet]}40;color:${VIMS_COLORS[p.planet]};">Pratyantar</span>` : ''}
        ${isAtBirth ? `<span class="dasha-badge" style="font-size:.58rem;background:rgba(20,184,166,.1);border-color:rgba(20,184,166,.3);color:#14b8a6;">At Birth</span>` : ''}
      </div>
      ${sookshmaHtml}
    </div>`;
  }).join('');

  return `<div style="padding:.5rem .25rem .25rem .75rem;">${items}</div>`;
}

// ─── Toggle handlers ──────────────────────────────────────────────────────

function toggleMaha(header) {
  const item = header.closest('.dasha-maha-item');
  const body = item.querySelector('.dasha-maha-body');
  const chevron = header.querySelector('.dasha-chevron');
  const isOpen = header.dataset.open === 'true';

  if (!isOpen) {
    // Lazy-render antardasha if not yet done
    const placeholder = body.querySelector('.dasha-antar-placeholder');
    if (placeholder) {
      const planet = placeholder.dataset.mahaPlanet;
      const start = Number(placeholder.dataset.mahaStart);
      const end = Number(placeholder.dataset.mahaEnd);
      const bMs = Number(placeholder.dataset.birth) || _birthMs || null;
      placeholder.outerHTML = buildAntarList({ planet, start, end }, null, Date.now(), bMs);

      // Re-attach antardasha handlers
      body.querySelectorAll('.dasha-antar-header').forEach(h => {
        h.addEventListener('click', e => { e.stopPropagation(); toggleAntar(h); });
      });
    }
    body.style.display = '';
    chevron.style.transform = 'rotate(180deg)';
    header.dataset.open = 'true';
  } else {
    body.style.display = 'none';
    chevron.style.transform = '';
    header.dataset.open = 'false';
  }
}

function toggleAntar(header) {
  const item = header.closest('.dasha-antar-item');
  const body = item.querySelector('.dasha-antar-body');
  const chevron = header.querySelector('.dasha-chevron');
  const isOpen = header.dataset.open === 'true';

  if (!isOpen) {
    // Lazy-render pratyantar if not yet done
    const placeholder = body.querySelector('.dasha-pratyan-placeholder');
    if (placeholder) {
      const planet = placeholder.dataset.planet;
      const start = Number(placeholder.dataset.start);
      const end = Number(placeholder.dataset.end);
      const bMs = Number(placeholder.dataset.birth) || _birthMs || null;
      placeholder.outerHTML = buildPratyanList({ planet, start, end }, Date.now(), true, bMs); // showAll for historical
    }
    body.style.display = '';
    chevron.style.transform = 'rotate(180deg)';
    header.dataset.open = 'true';
  } else {
    body.style.display = 'none';
    chevron.style.transform = '';
    header.dataset.open = 'false';
  }
}

// ─── Bootstrap ────────────────────────────────────────────────────────────

document.addEventListener('DOMContentLoaded', () => {
  const el = document.getElementById('dasha-data');
  if (!el) return;
  try {
    const data = JSON.parse(el.textContent);
    renderDasha(data);
  } catch (e) {
    console.error('[Dasha] Error rendering:', e);
  }
});
