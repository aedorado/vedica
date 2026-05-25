# 📊 Vedic Analytics Dashboard

Interactive analytics visualization for Vedic Astrology charts.

## Features

✅ **Lagna Distribution** - See which zodiac signs appear as Lagna  
✅ **Planet Combinations** - 2, 3, and 4-planet combinations with frequencies  
✅ **Planet × Rashi Heatmap** - Visualize which planets appear in which signs  
✅ **Yoga Detection** - Count detected yogas across all charts  
✅ **Planetary Strengths** - Distribution of strong/moderate/weak planets  
✅ **Interactive Details** - Click any stat to see matching charts  

## Quick Start

### 1. Generate Analytics Cache

```bash
cd analytics
python3 -c "from engine import AnalyticsEngine; e = AnalyticsEngine(); e.generate_all_stats(); e.save_cache()"
```

### 2. Run Dashboard Server

```bash
python3 api.py
```

Then open: **http://localhost:5000**

## API Endpoints

| Endpoint | Description |
|----------|-------------|
| `GET /` | Main dashboard |
| `GET /api/stats/summary` | Summary stats |
| `GET /api/lagna` | Lagna distribution |
| `GET /api/combos/<num>` | N-planet combinations (2, 3, 4) |
| `GET /api/planet-rashi-heatmap` | Planet × Sign matrix |
| `GET /api/yogas` | Yoga counts |
| `GET /api/strengths` | Planetary strengths |
| `GET /api/charts/by-lagna/<sign>` | Charts with specific Lagna |
| `GET /api/charts/by-combo/<combo>` | Charts with specific combo |
| `GET /api/refresh-cache` | Regenerate analytics |

## Architecture

```
analytics/
├── engine.py           # Analytics generation logic
├── api.py              # Flask REST API server
├── templates/
│   └── dashboard.html  # Frontend UI
└── static/
    ├── css/
    │   └── style.css   # Styling
    └── js/
        └── dashboard.js # Frontend logic
```

## How It Works

1. **Engine** reads all 64 charts from database
2. **Extracts**:
   - Lagna signs from 1st house
   - Planet combinations (2, 3, 4-planet)
   - Planet positions in each sign
   - Yogas using yoga detectors
   - Planetary strengths
3. **Caches** results to `cache.json` for performance
4. **API** serves JSON data to frontend
5. **Dashboard** visualizes with interactive charts

## Data Structure (cache.json)

```json
{
  "total_charts": 64,
  "lagna": {
    "Aries": {"count": 5, "charts": [1, 2, 3, 4, 5]},
    "Cancer": {"count": 3, "charts": [10, 11, 12]}
  },
  "combos_2": {
    "Sun+Moon": {"count": 8, "charts": [1, 5, 10, ...]},
    "Sun+Mars": {"count": 6, "charts": [2, 3, ...]}
  },
  "planet_rashi_heatmap": {
    "Sun": {"Aries": 2, "Taurus": 1, ...},
    "Moon": {"Cancer": 3, "Leo": 1, ...}
  },
  "yogas": {
    "Raja Yoga": 8,
    "Dhan Yoga": 5
  },
  "planet_strengths": {
    "strong": {"Sun": 12, "Moon": 8},
    "moderate": {"Mars": 10},
    "weak": {"Saturn": 5}
  }
}
```

## Future Enhancements

- House-wise planet distribution
- Dosha frequency analysis
- Retrograde planet patterns
- Nakshatra insights
- Temporal analysis (if birth dates available)

## Dependencies

- Flask
- SQLite3 (existing db_adapter)
- Chart.js (frontend)
- Bootstrap 5 (frontend)

No additional Python packages needed!
