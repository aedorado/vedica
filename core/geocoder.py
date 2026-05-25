"""
Geocoding via OpenStreetMap Nominatim (free, no API key required).
Flask proxy to avoid browser CORS issues.
Results are cached in-memory to minimise external requests.
"""

import json
import time
import urllib.request
import urllib.parse
from functools import lru_cache

_USER_AGENT = 'Vedica/1.0 (astrology chart calculator)'
_NOMINATIM_URL = 'https://nominatim.openstreetmap.org/search'
_last_request_time = 0.0  # rate-limit: 1 req/sec


def _fetch(query: str, limit: int = 6) -> list[dict]:
    """Hit Nominatim and return raw results."""
    global _last_request_time
    # Respect 1 req/sec rate limit
    elapsed = time.time() - _last_request_time
    if elapsed < 1.0:
        time.sleep(1.0 - elapsed)
    _last_request_time = time.time()

    params = urllib.parse.urlencode({
        'q': query,
        'format': 'json',
        'limit': limit,
        'addressdetails': 1,
        'accept-language': 'en',
    })
    url = f'{_NOMINATIM_URL}?{params}'
    req = urllib.request.Request(url, headers={'User-Agent': _USER_AGENT})
    with urllib.request.urlopen(req, timeout=5) as resp:
        return json.loads(resp.read())


@lru_cache(maxsize=512)
def search_places(query: str) -> list[dict]:
    """
    Search for a place and return a list of candidates.
    Each result: { display_name, lat, lon, city, country }
    """
    if not query or len(query.strip()) < 2:
        return []
    try:
        raw = _fetch(query.strip())
    except Exception:
        return []

    results = []
    for r in raw:
        addr = r.get('addressdetails') or r.get('address') or {}
        city = (
            addr.get('city') or addr.get('town') or addr.get('village') or
            addr.get('county') or addr.get('state') or ''
        )
        country = addr.get('country', '')
        label = r.get('display_name', '')
        # Build a shorter display label
        parts = [p.strip() for p in label.split(',')]
        short = ', '.join(parts[:3]) if len(parts) >= 3 else label

        results.append({
            'display': short,
            'full': label,
            'city': city,
            'country': country,
            'lat': float(r['lat']),
            'lon': float(r['lon']),
        })
    return results
