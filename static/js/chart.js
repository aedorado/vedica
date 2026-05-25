// ─── Kundali chart renderer ────────────────────────────────────────────────

const SIGN_ABBR  = ['Ari','Tau','Gem','Can','Leo','Vir','Lib','Sco','Sag','Cap','Aqu','Pis'];
const PLANET_ABBR = { Sun:'Su',Moon:'Mo',Mars:'Ma',Mercury:'Me',Jupiter:'Ju',Venus:'Ve',Saturn:'Sa',Rahu:'Ra',Ketu:'Ke',Uranus:'Ur',Neptune:'Ne',Pluto:'Pl' };
const PLANET_COLORS = { Sun:'#f59e0b',Moon:'#94a3b8',Mars:'#ef4444',Mercury:'#10b981',Jupiter:'#f97316',Venus:'#ec4899',Saturn:'#6366f1',Rahu:'#8b5cf6',Ketu:'#14b8a6',Uranus:'#06b6d4',Neptune:'#3b82f6',Pluto:'#71717a' };
const PLANET_INDEX = { Sun:0,Moon:1,Mars:2,Mercury:3,Jupiter:4,Venus:5,Saturn:6,Rahu:7,Ketu:8 };
const DIGNITY_MARKERS = { exalted: '^', debilitated: '∨', combust: '×' };
const DIGNITY_COLORS = { exalted: '#22c55e', debilitated: '#ef4444', combust: '#f97316' };

function buildSignPlanets(chartData) {
  const map = {};
  const dignityData = chartData.planet_dignity || {};
  for (const [name, p] of Object.entries(chartData.planets)) {
    if (!p) continue;
    const si = p.position.sign_idx;
    if (!map[si]) map[si] = [];
    
    const planetIdx = PLANET_INDEX[name];
    let dignity = null;
    let dignityMarker = '';
    let dignityColor = '';
    
    if (dignityData.exalted && dignityData.exalted.includes(planetIdx)) {
      dignity = 'exalted';
      dignityMarker = DIGNITY_MARKERS.exalted;
      dignityColor = DIGNITY_COLORS.exalted;
    } else if (dignityData.debilitated && dignityData.debilitated.includes(planetIdx)) {
      dignity = 'debilitated';
      dignityMarker = DIGNITY_MARKERS.debilitated;
      dignityColor = DIGNITY_COLORS.debilitated;
    } else if (dignityData.combust && dignityData.combust.includes(planetIdx)) {
      dignity = 'combust';
      dignityMarker = DIGNITY_MARKERS.combust;
      dignityColor = DIGNITY_COLORS.combust;
    }
    
    map[si].push({ 
      abbr: PLANET_ABBR[name] || name.slice(0,2), 
      retro: p.retrograde, 
      color: PLANET_COLORS[name] || '#ccc',
      dignity: dignity,
      dignityMarker: dignityMarker,
      dignityColor: dignityColor
    });
  }
  return map;
}

// ── South Indian ─────────────────────────────────────────────────────────────
const SI_CELLS = [
  [1,1,11],[1,2,0],[1,3,1],[1,4,2],
  [2,1,10],                [2,4,3],
  [3,1, 9],                [3,4,4],
  [4,1, 8],[4,2,7],[4,3,6],[4,4,5]
];

function renderSouthIndian(container, chartData) {
  const avail = container.parentElement ? container.parentElement.offsetWidth : 0;
  const SIZE = Math.min(420, avail > 60 ? avail - 2 : Math.round(window.innerWidth * 0.85));
  container.style.cssText = `display:grid;grid-template-columns:repeat(4,1fr);grid-template-rows:repeat(4,1fr);width:${SIZE}px;height:${SIZE}px;position:relative;overflow:hidden;`;
  const lagnaIdx = chartData.lagna_sign_idx;
  const signPlanets = buildSignPlanets(chartData);
  SI_CELLS.forEach(([row, col, signIdx]) => {
    const isLagna = signIdx === lagnaIdx;
    let pl = signPlanets[signIdx] || [];
    // Filter out Ascendant planet to avoid duplication with the "ASC" marker
    pl = pl.filter(p => p.abbr !== 'As' && p.abbr !== 'ASC');
    const cell = document.createElement('div');
    cell.className = 'k-cell' + (isLagna ? ' k-lagna' : '');
    cell.style.gridRow = row; cell.style.gridColumn = col;
    cell.innerHTML =
      (isLagna ? `<div class="k-lagna-mark">ASC</div>` : '') +
      `<div class="k-sign" style="text-align:center;width:100%;">${SIGN_ABBR[signIdx]}</div>` +
      `<div class="k-planets" style="display:grid;grid-template-columns:repeat(3,1fr);gap:0.15rem;width:100%;">${pl.map(p=>`<span class="k-planet" style="color:${p.color};">${p.abbr}${p.retro?'℞':''}${p.dignityMarker?`<span style="color:${p.dignityColor};font-size:0.65em;vertical-align:super;font-weight:700;">${p.dignityMarker}</span>`:''}</span>`).join('')}</div>`;
    container.appendChild(cell);
  });
  const center = document.createElement('div');
  center.className = 'k-center'; center.style.gridArea = '2/2/4/4';
  center.innerHTML = `<div class="k-center-inner"><div style="font-size:.65rem;color:var(--accent);">✦</div><div style="font-size:.65rem;color:var(--text3);margin-top:.2rem;">${chartData.name||''}</div></div>`;
  container.appendChild(center);
}

// ── North Indian SVG ─────────────────────────────────────────────────────────
//
// Grid = outer square  +  2 full corner diagonals  +  inner diamond
//
// Outer corners:   TL(0,0)   TC(H,0)   TR(S,0)
//                  LC(0,H)   CX(H,H)   RC(S,H)
//                  BL(0,S)   BC(H,S)   BR(S,S)
//
// Inner diamond corners ON the outer border midpoints: TC, RC, BC, LC
// The diagonals intersect the inner diamond sides at:
//   TLC(Q,Q)   = TL-BR diagonal ∩ inner side LC-TC
//   TRC(Q3,Q)  = TR-BL diagonal ∩ inner side TC-RC
//   BRC(Q3,Q3) = TL-BR diagonal ∩ inner side RC-BC
//   BLC(Q,Q3)  = TR-BL diagonal ∩ inner side BC-LC
//
// 12 cells counter-clockwise from H1 (lagna = top):
//   H1  inner top quad:       TC, TRC, CX, TLC     ← Lagna (apex = TC)
//   H2  outer TL-upper tri:   TL, TC,  TLC
//   H3  outer TL-lower tri:   TL, TLC, LC
//   H4  inner left quad:      LC, TLC, CX, BLC      (apex = LC)
//   H5  outer BL-upper tri:   BL, LC,  BLC
//   H6  outer BL-lower tri:   BC, BL,  BLC
//   H7  inner bottom quad:    BC, BLC, CX, BRC      (apex = BC)
//   H8  outer BR-lower tri:   BR, BC,  BRC
//   H9  outer BR-upper tri:   RC, BR,  BRC
//   H10 inner right quad:     RC, BRC, CX, TRC      (apex = RC)
//   H11 outer TR-lower tri:   TR, RC,  TRC
//   H12 outer TR-upper tri:   TC, TR,  TRC

function renderNorthIndian(container, chartData) {
  const avail = container.parentElement ? container.parentElement.offsetWidth : 0;
  const SIZE = Math.min(420, avail > 60 ? avail - 2 : Math.round(window.innerWidth * 0.85));
  const S = SIZE, H = S/2, Q = S/4, Q3 = 3*S/4;
  container.style.cssText = `display:block;width:${SIZE}px;height:${SIZE}px;`;

  const lagnaIdx   = chartData.lagna_sign_idx;
  const signPlanets = buildSignPlanets(chartData);

  const cs = getComputedStyle(document.documentElement);
  const strokeCol = cs.getPropertyValue('--border2').trim() || '#4a4a6a';
  const bgFill    = getComputedStyle(container).backgroundColor || cs.getPropertyValue('--surface').trim() || '#0f172a';
  const surface2  = cs.getPropertyValue('--surface2').trim() || '#1e293b';
  const textDim   = cs.getPropertyValue('--text3').trim() || '#888';

  const ns = 'http://www.w3.org/2000/svg';
  const svg = document.createElementNS(ns, 'svg');
  svg.setAttribute('width', S); svg.setAttribute('height', S);
  svg.setAttribute('viewBox', `0 0 ${S} ${S}`);
  svg.style.display = 'block';

  // Key points
  const TL=[0,0], TC=[H,0], TR=[S,0];
  const LC=[0,H], CX=[H,H], RC=[S,H];
  const BL=[0,S], BC=[H,S], BR=[S,S];
  // Diagonal ∩ inner-diamond intersection points
  const TLC=[Q,Q], TRC=[Q3,Q], BRC=[Q3,Q3], BLC=[Q,Q3];

  // Background
  const bg = document.createElementNS(ns, 'rect');
  bg.setAttribute('width',S); bg.setAttribute('height',S);
  bg.setAttribute('fill', bgFill);
  bg.setAttribute('stroke', strokeCol); bg.setAttribute('stroke-width','1.5');
  bg.setAttribute('rx','4');
  svg.appendChild(bg);

  // Lines: 2 full diagonals + 4 inner diamond sides
  [
    [TL,BR], [TR,BL],           // corner-to-corner diagonals
    [TC,RC], [RC,BC], [BC,LC], [LC,TC],  // inner diamond
  ].forEach(([a,b]) => {
    const l = document.createElementNS(ns, 'line');
    l.setAttribute('x1',a[0]); l.setAttribute('y1',a[1]);
    l.setAttribute('x2',b[0]); l.setAttribute('y2',b[1]);
    l.setAttribute('stroke', strokeCol); l.setAttribute('stroke-width','1.2');
    svg.appendChild(l);
  });

  // 12 cells, counter-clockwise from lagna (H1 = top inner quad)
  const CELLS = [
    [TC,  TRC, CX,  TLC],  // H1  inner top      ← Lagna (apex=TC)
    [TL,  TC,  TLC     ],  // H2  outer TL upper
    [TL,  TLC, LC      ],  // H3  outer TL lower
    [LC,  TLC, CX,  BLC],  // H4  inner left     (apex=LC)
    [BL,  LC,  BLC     ],  // H5  outer BL upper
    [BC,  BL,  BLC     ],  // H6  outer BL lower
    [BC,  BLC, CX,  BRC],  // H7  inner bottom   (apex=BC)
    [BR,  BC,  BRC     ],  // H8  outer BR lower
    [RC,  BR,  BRC     ],  // H9  outer BR upper
    [RC,  BRC, CX,  TRC],  // H10 inner right    (apex=RC)
    [TR,  RC,  TRC     ],  // H11 outer TR lower
    [TC,  TR,  TRC     ],  // H12 outer TR upper
  ];

  function centroid(pts) {
    return [
      pts.reduce((s,p)=>s+p[0],0)/pts.length,
      pts.reduce((s,p)=>s+p[1],0)/pts.length,
    ];
  }

  // Render planets and rashi numbers in each cell
  const rashiSize = Math.round(S * 0.032);
  const planetSize = Math.round(S * 0.036);
  const lineHeight = Math.round(S * 0.044);

  CELLS.forEach((poly, i) => {
    const signIdx = (lagnaIdx + i) % 12;
    const rashiNum = signIdx + 1;
    let planets = signPlanets[signIdx] || [];
    // Filter out Ascendant planet to avoid duplication with the "As" marker
    planets = planets.filter(p => p.abbr !== 'As' && p.abbr !== 'ASC');
    const isLagna = i === 0;

    // Create a group for this cell to enable hover effects
    const cellGroup = document.createElementNS(ns, 'g');
    cellGroup.setAttribute('class', 'k-cell-group');
    cellGroup.style.cursor = 'pointer';

    // Lagna highlight
    if (isLagna) {
      const hi = document.createElementNS(ns, 'polygon');
      hi.setAttribute('points', poly.map(p=>p.join(',')).join(' '));
      hi.setAttribute('fill', 'rgba(251,191,36,0.15)');
      hi.setAttribute('stroke', '#fbbf24'); hi.setAttribute('stroke-width','1.5');
      cellGroup.appendChild(hi);
    }

    // Add hover background polygon (light highlight on hover)
    const hoverBg = document.createElementNS(ns, 'polygon');
    hoverBg.setAttribute('points', poly.map(p=>p.join(',')).join(' '));
    hoverBg.setAttribute('fill', surface2);
    hoverBg.setAttribute('stroke', 'none');
    hoverBg.style.opacity = '0';
    hoverBg.style.transition = 'opacity 0.2s';
    cellGroup.appendChild(hoverBg);

    const [cx, cy] = centroid(poly);

    // Lagna/Ascendant marker
    if (isLagna) {
      const as = document.createElementNS(ns, 'text');
      as.setAttribute('x', cx + S * 0.06);
      as.setAttribute('y', cy - (planets.length > 0 ? lineHeight * 1.8 : lineHeight * 0.8) - rashiSize * 0.8);
      as.setAttribute('text-anchor', 'middle');
      as.setAttribute('dominant-baseline', 'middle');
      as.setAttribute('font-size', Math.round(S * 0.028));
      as.setAttribute('font-family', 'system-ui,sans-serif');
      as.setAttribute('font-weight', '700');
      as.setAttribute('fill', textDim);  // Use normal text color, not gold
      as.textContent = 'As';
      cellGroup.appendChild(as);
    }

    // Rashi number (small, positioned to avoid planets)
    const rn = document.createElementNS(ns, 'text');
    rn.setAttribute('x', cx - S * 0.05);  // Offset slightly left
    rn.setAttribute('y', cy - (planets.length > 0 ? lineHeight * 1.0 : lineHeight * 0.3));
    rn.setAttribute('text-anchor', 'middle');
    rn.setAttribute('dominant-baseline', 'middle');
    rn.setAttribute('font-size', rashiSize);
    rn.setAttribute('font-family', 'system-ui,sans-serif');
    rn.setAttribute('font-weight', '600');
    rn.setAttribute('fill', isLagna ? '#fbbf24' : textDim);
    rn.textContent = rashiNum;
    cellGroup.appendChild(rn);

    // Planets (multi-column layout: max 3 per column, then wrap right)
    const PLANETS_PER_COL = 3;
    const colWidth = Math.round(S * 0.06);  // Space between columns
    planets.forEach((p, j) => {
      const col = Math.floor(j / PLANETS_PER_COL);
      const row = j % PLANETS_PER_COL;
      const totalInCol = Math.min(PLANETS_PER_COL, planets.length - col * PLANETS_PER_COL);
      
      const pt = document.createElementNS(ns, 'text');
      pt.setAttribute('x', cx + col * colWidth);
      pt.setAttribute('y', cy + (row - (totalInCol - 1) / 2) * lineHeight);
      pt.setAttribute('text-anchor', 'middle');
      pt.setAttribute('dominant-baseline', 'middle');
      pt.setAttribute('font-size', planetSize);
      pt.setAttribute('font-family', 'system-ui,sans-serif');
      pt.setAttribute('font-weight', '600');
      pt.setAttribute('fill', p.color);
      pt.textContent = p.abbr + (p.retro ? '℞' : '') + (p.dignityMarker ? p.dignityMarker : '');
      if (p.dignityMarker && p.dignityColor) {
        pt.setAttribute('fill', p.dignityColor);
      }
      cellGroup.appendChild(pt);
    });

    // Add hover effects
    cellGroup.addEventListener('mouseenter', () => {
      hoverBg.style.opacity = '1';
    });
    cellGroup.addEventListener('mouseleave', () => {
      hoverBg.style.opacity = '0';
    });

    svg.appendChild(cellGroup);
  });

  container.appendChild(svg);
}

// ── Public API ────────────────────────────────────────────────────────────────
function renderKundali(containerId, chartData, style) {
  const c = document.getElementById(containerId);
  if (!c) return;
  c.innerHTML = '';
  if (style === 'south') renderSouthIndian(c, chartData);
  else                   renderNorthIndian(c, chartData);
}

function switchChartStyle(style) {
  document.querySelectorAll('.chart-style-btn').forEach(b => b.classList.remove('active'));
  document.getElementById('btn-' + style).classList.add('active');
  renderKundali('kundali-container', JSON.parse(document.getElementById('chart-json').textContent), style);
}

document.addEventListener('DOMContentLoaded', () => {
  const el = document.getElementById('chart-json');
  if (el) renderKundali('kundali-container', JSON.parse(el.textContent), 'south');
});
