/**
 * Divisional Charts Display - Renders all divisional (Varga) charts
 * D2, D3, D9, D10, D12, D27, D60, etc.
 */

console.log('[divisional.js] Script loaded');

// Chart metadata
const DIVISIONAL_CHART_INFO = {
  1: { name: 'Rashi', symbol: 'D1', desc: 'Main birth chart', category: 'Main' },
  2: { name: 'Hora', symbol: 'D2', desc: 'Wealth, resources', category: 'Divisional' },
  3: { name: 'Drekkana', symbol: 'D3', desc: 'Siblings, courage', category: 'Divisional' },
  4: { name: 'Chaturthamsha', symbol: 'D4', desc: 'Property, vehicles', category: 'Divisional' },
  5: { name: 'Panchamsha', symbol: 'D5', desc: 'Children', category: 'Divisional' },
  7: { name: 'Saptamsha', symbol: 'D7', desc: 'Children, creativity', category: 'Divisional' },
  9: { name: 'Navamsha', symbol: 'D9', desc: 'Career, marriage (CRITICAL)', category: 'Divisional', critical: true },
  10: { name: 'Dasamsha', symbol: 'D10', desc: 'Career, profession (CRITICAL)', category: 'Divisional', critical: true },
  12: { name: 'Dwadasamsha', symbol: 'D12', desc: 'Parents, ancestors', category: 'Divisional' },
  16: { name: 'Shodasamsha', symbol: 'D16', desc: 'Happiness, harmony', category: 'Divisional' },
  20: { name: 'Vimshamsha', symbol: 'D20', desc: 'Religious merit, spirituality', category: 'Divisional' },
  27: { name: 'Nakshatramsha', symbol: 'D27', desc: 'Nakshatra detail', category: 'Divisional' },
  30: { name: 'Trimshamsha', symbol: 'D30', desc: 'Misery, challenges', category: 'Divisional' },
  40: { name: 'Khavedamsha', symbol: 'D40', desc: 'Duration of life', category: 'Divisional' },
  45: { name: 'Akshavedamsha', symbol: 'D45', desc: 'Destiny, karma', category: 'Divisional' },
  60: { name: 'Shashtiamsha', symbol: 'D60', desc: 'Most detailed, precise (CRITICAL)', category: 'Divisional', critical: true },
};

const PLANET_DISPLAY_ORDER = [
  'Sun', 'Moon', 'Mars', 'Mercury', 'Jupiter', 'Venus',
  'Saturn', 'Rahu', 'Ketu', 'Uranus', 'Neptune', 'Pluto',
];

const PLANET_SYMBOLS = {
  'Sun': '☉', 'Moon': '☽', 'Mars': '♂', 'Mercury': '☿',
  'Jupiter': '♃', 'Venus': '♀', 'Saturn': '♄',
  'Rahu': '☊', 'Ketu': '☋', 'Uranus': '♅', 'Neptune': '♆', 'Pluto': '♇',
};

const PLANET_COLORS = {
  'Sun': '#f59e0b', 'Moon': '#e2e8f0', 'Mars': '#ef4444',
  'Mercury': '#10b981', 'Jupiter': '#f97316', 'Venus': '#ec4899',
  'Saturn': '#6366f1', 'Rahu': '#8b5cf6', 'Ketu': '#14b8a6',
  'Uranus': '#06b6d4', 'Neptune': '#3b82f6', 'Pluto': '#71717a',
};

// Global divisional data
let divisionalData = null;
let currentDivisionalChart = 1;

// Initialize on page load
document.addEventListener('DOMContentLoaded', () => {
  try {
    const scriptTag = document.getElementById('divisional-data');
    if (scriptTag) {
      divisionalData = JSON.parse(scriptTag.textContent);
      // Show D1 (Rashi) by default
      showDivisionalChart(1);
      
      // Add click handlers to divisional chart tabs
      document.querySelectorAll('.divisional-tab').forEach(btn => {
        btn.addEventListener('click', (e) => {
          const divisor = parseInt(btn.getAttribute('data-divisor'));
          showDivisionalChart(divisor);
        });
      });
    }
  } catch (err) {
    console.error('Error initializing divisional charts:', err);
  }
});

/**
 * Display a specific divisional chart
 */
function showDivisionalChart(divisor) {
  currentDivisionalChart = divisor;

  if (!divisionalData) {
    console.error('Divisional data not loaded');
    return;
  }

  // Update active tab
  document.querySelectorAll('.divisional-tab').forEach((btn) => {
    const btnDivisor = parseInt(btn.getAttribute('data-divisor'));
    if (btnDivisor === divisor) {
      btn.style.background = 'var(--accent)';
      btn.style.color = '#fff';
      btn.style.border = '1px solid var(--accent)';
    } else {
      btn.style.background = 'var(--surface)';
      btn.style.color = 'var(--text)';
      btn.style.border = '1px solid var(--border)';
    }
  });

  const content = document.getElementById('divisional-content');
  const info = DIVISIONAL_CHART_INFO[divisor];

  if (!info) {
    content.innerHTML = `<div style="color:red; text-align:center; padding:2rem;">Unknown divisional chart D${divisor}</div>`;
    return;
  }

  // Special case for D1 (render from main chart data)
  if (divisor === 1) {
    renderD1Chart(content);
    return;
  }

  const allDivisors = divisionalData.divisional_charts.all_divisors || {};
  const majorCharts = divisionalData.divisional_charts.major_charts || {};

  if (!allDivisors[divisor]) {
    content.innerHTML = `<div style="color:orange; text-align:center; padding:2rem;">D${divisor} not calculated</div>`;
    return;
  }

  const planets = allDivisors[divisor];
  const chartDetails = majorCharts[divisor] || {};

  // Render divisional chart HTML
  renderDivisionalChart(content, divisor, info, planets, chartDetails);
}

/**
 * Render D1 (Rashi/main chart) data
 */
function renderD1Chart(container) {
  const d1 = divisionalData.divisional_charts.all_divisors[1];
  const info = DIVISIONAL_CHART_INFO[1];
  const meta = divisionalData.divisional_charts.summary[1] || {};

  if (!d1) {
    container.innerHTML = '<div style="color:red;">D1 data not available</div>';
    return;
  }

  let html = `
    <div style="margin-bottom:1.5rem;">
      <h4 style="margin:0 0 0.5rem 0; font-size:1rem;">${info.name} (${info.symbol})</h4>
      <p style="color:var(--text3); font-size:0.9rem; margin:0;">${info.desc}</p>
    </div>

    <div class="planet-grid" style="display:grid; grid-template-columns:repeat(auto-fill, minmax(280px,1fr)); gap:1rem;">
  `;

  PLANET_DISPLAY_ORDER.forEach(planet => {
    if (d1[planet]) {
      const p = d1[planet];
      const pos = p.position;
      const retroClass = p.retrograde ? ' <span style="color:var(--red); font-weight:700;"> ℞</span>' : '';
      
      html += `
        <div style="background:var(--surface); border:1px solid var(--border); border-radius:8px; padding:1rem;">
          <div style="display:flex; align-items:center; gap:0.5rem; margin-bottom:0.5rem;">
            <span style="font-size:1.4rem; color:${PLANET_COLORS[planet]};">${PLANET_SYMBOLS[planet]}</span>
            <div>
              <div style="font-weight:600; color:var(--text2);">${planet}${retroClass}</div>
              <div style="font-size:0.8rem; color:var(--text3);">${p.nakshatra.name}</div>
            </div>
          </div>
          <div style="font-size:0.95rem; color:var(--text2);">
            ${pos.sign} ${pos.degree}°${pos.minute}'
          </div>
        </div>
      `;
    }
  });

  html += `</div>`;
  container.innerHTML = html;
}

/**
 * Render any divisional chart (D2, D3, D9, etc.)
 */
function renderDivisionalChart(container, divisor, info, planets, chartDetails) {
  let html = `
    <div style="margin-bottom:1.5rem;">
      <h4 style="margin:0 0 0.5rem 0; font-size:1rem;">
        ${info.name} (${info.symbol})
        ${info.critical ? ' <span style="color:var(--red); font-weight:700;">★</span>' : ''}
      </h4>
      <p style="color:var(--text3); font-size:0.9rem; margin:0;">${info.desc}</p>
    </div>
  `;

  // Show ascendant if available
  if (chartDetails.ascendant) {
    const asc = chartDetails.ascendant.position;
    html += `
      <div style="background:rgba(251,191,36,0.1); border:1px solid rgba(251,191,36,0.3); border-radius:8px; padding:1rem; margin-bottom:1rem;">
        <div style="font-size:0.9rem; color:var(--text3); margin-bottom:0.5rem;">Ascendant</div>
        <div style="font-size:1.1rem; font-weight:700; color:var(--gold2);">
          ${asc.sign} ${asc.degree}°${asc.minute}'
        </div>
      </div>
    `;
  }

  // Render planets grid
  html += `<div class="planet-grid" style="display:grid; grid-template-columns:repeat(auto-fill, minmax(280px,1fr)); gap:1rem;">`;

  PLANET_DISPLAY_ORDER.forEach(planet => {
    if (planets[planet]) {
      const p = planets[planet];
      const pos = p.position;
      const retroClass = p.retrograde ? ' <span style="color:var(--red); font-weight:700;"> ℞</span>' : '';

      html += `
        <div style="background:var(--surface); border:1px solid var(--border); border-radius:8px; padding:1rem;">
          <div style="display:flex; align-items:center; gap:0.5rem; margin-bottom:0.5rem;">
            <span style="font-size:1.4rem; color:${PLANET_COLORS[planet]};">${PLANET_SYMBOLS[planet]}</span>
            <div>
              <div style="font-weight:600; color:var(--text2);">${planet}${retroClass}</div>
              <div style="font-size:0.8rem; color:var(--text3);">${p.nakshatra.name}</div>
            </div>
          </div>
          <div style="font-size:0.95rem; color:var(--text2);">
            ${pos.sign} ${pos.degree}°${pos.minute}'
          </div>
        </div>
      `;
    }
  });

  html += `</div>`;

  // Show house cusps if available
  if (chartDetails.house_cusps && chartDetails.house_cusps.length > 0) {
    html += `
      <div style="margin-top:1.5rem; padding-top:1.5rem; border-top:1px solid var(--border);">
        <h5 style="margin:0 0 1rem 0; font-size:0.95rem; color:var(--text2);">⌂ House Cusps</h5>
        <div style="display:grid; grid-template-columns:repeat(auto-fill, minmax(140px,1fr)); gap:0.8rem;">
    `;

    chartDetails.house_cusps.forEach(h => {
      html += `
        <div style="background:var(--surface2); border:1px solid var(--border); border-radius:6px; padding:0.6rem 0.8rem; font-size:0.85rem;">
          <div style="color:var(--text3);">House ${h.house}</div>
          <div style="font-weight:600; color:var(--text2);">${h.position.sign} ${h.position.degree}°</div>
        </div>
      `;
    });

    html += `</div></div>`;
  }

  container.innerHTML = html;
}
