// ─── Theme toggle ───────────────────────────────────────────────────────────

const THEME_KEY = 'vedica-theme';

function applyTheme(theme) {
  document.documentElement.setAttribute('data-theme', theme);
  localStorage.setItem(THEME_KEY, theme);
  const btn = document.getElementById('theme-toggle');
  if (btn) btn.textContent = theme === 'dark' ? '☀ Light' : '☾ Dark';
}

function toggleTheme() {
  const current = document.documentElement.getAttribute('data-theme') || 'dark';
  applyTheme(current === 'dark' ? 'light' : 'dark');
}

// Apply saved theme immediately
(function () {
  const saved = localStorage.getItem(THEME_KEY) || 'dark';
  applyTheme(saved);
})();


// ─── Place autocomplete ──────────────────────────────────────────────────────

class PlaceAutocomplete {
  constructor({ inputId, listId, latId, lonId, displayId }) {
    this.input    = document.getElementById(inputId);
    this.list     = document.getElementById(listId);
    this.latInput = document.getElementById(latId);
    this.lonInput = document.getElementById(lonId);
    this.displayInput = document.getElementById(displayId);

    if (!this.input) return;

    this._debounceTimer = null;
    this._focused = -1;
    this._results = [];

    this.input.addEventListener('input', () => this._onInput());
    this.input.addEventListener('keydown', (e) => this._onKey(e));
    document.addEventListener('click', (e) => {
      if (!this.input.contains(e.target) && !this.list.contains(e.target)) {
        this._close();
      }
    });
  }

  _onInput() {
    clearTimeout(this._debounceTimer);
    const q = this.input.value.trim();
    if (q.length < 2) { this._close(); return; }
    this._debounceTimer = setTimeout(() => this._fetch(q), 320);
  }

  async _fetch(q) {
    try {
      const res = await fetch(`/api/geocode?q=${encodeURIComponent(q)}`);
      this._results = await res.json();
      this._render();
    } catch (_) { /* network error – silent */ }
  }

  _render() {
    this.list.innerHTML = '';
    this._focused = -1;
    if (!this._results.length) { this._close(); return; }

    this._results.forEach((r, i) => {
      const item = document.createElement('div');
      item.className = 'autocomplete-item';
      item.innerHTML = `
        <span class="place-icon">📍</span>
        <span>${r.display}</span>
        <span class="coords">${r.lat.toFixed(2)}°N ${r.lon.toFixed(2)}°E</span>
      `;
      item.addEventListener('mousedown', (e) => { e.preventDefault(); this._select(i); });
      this.list.appendChild(item);
    });

    this.list.classList.add('open');
  }

  _select(i) {
    const r = this._results[i];
    this.input.value = r.display;
    if (this.latInput)     this.latInput.value = r.lat;
    if (this.lonInput)     this.lonInput.value = r.lon;
    if (this.displayInput) this.displayInput.value = r.display;

    this._close();
    this._showConfirmation(r);
  }

  _showConfirmation(r) {
    let conf = document.getElementById('place-confirmation');
    if (!conf) {
      conf = document.createElement('div');
      conf.id = 'place-confirmation';
      conf.style.cssText = 'font-size:.8rem;color:var(--teal);margin-top:.35rem;';
      this.input.parentNode.appendChild(conf);
    }
    conf.textContent = `✓ ${r.full ? r.full.split(',').slice(0,4).join(',') : r.display}  (${r.lat.toFixed(4)}°N, ${r.lon.toFixed(4)}°E)`;
  }

  _close() { this.list.classList.remove('open'); }

  _onKey(e) {
    const items = this.list.querySelectorAll('.autocomplete-item');
    if (e.key === 'ArrowDown') {
      e.preventDefault();
      this._focused = Math.min(this._focused + 1, items.length - 1);
      this._highlight(items);
    } else if (e.key === 'ArrowUp') {
      e.preventDefault();
      this._focused = Math.max(this._focused - 1, 0);
      this._highlight(items);
    } else if (e.key === 'Enter' && this._focused >= 0) {
      e.preventDefault();
      this._select(this._focused);
    } else if (e.key === 'Escape') {
      this._close();
    }
  }

  _highlight(items) {
    items.forEach((el, i) => el.classList.toggle('focused', i === this._focused));
    if (items[this._focused]) items[this._focused].scrollIntoView({ block: 'nearest' });
  }
}

// Initialise autocomplete when DOM ready
document.addEventListener('DOMContentLoaded', () => {
  new PlaceAutocomplete({
    inputId:   'place-search',
    listId:    'place-list',
    latId:     'lat',
    lonId:     'lon',
    displayId: 'place_display',
  });
});
