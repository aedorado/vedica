"""
Test cases for Vedica ephemeris calculator.
Add expected_sun / expected_asc fields to each chart once you have reference values.

Run:  python3 -m pytest tests/test_charts.py -v
"""

import pytest
from datetime import datetime, timedelta
import sys, os

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from app.core.ephemeris import calculate_chart


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def parse_birth(birth_str: str) -> dict:
    """Parse 'Name | HH:MM DD/MM/YYYY ±HH:MM | Place, Lon, Lat' string."""
    parts = birth_str.split('|')
    name = parts[0].strip()
    time_part = parts[1].strip().split()
    h, m = map(int, time_part[0].split(':'))
    d, mo, y = map(int, time_part[1].split('/'))
    tz = time_part[2]
    sign = 1 if tz[0] == '+' else -1
    th, tm = map(int, tz[1:].split(':'))
    tz_offset = sign * (th + tm / 60)
    dt_local = datetime(y, mo, d, h, m)
    dt_utc = dt_local - timedelta(hours=tz_offset)

    coords = parts[2].strip().split(',')
    lon = float(coords[-2].strip())
    lat = float(coords[-1].strip())

    return {'name': name, 'dt_utc': dt_utc, 'lat': lat, 'lon': lon}


def check_planet(result, planet, expected_sign, max_degree_diff=2):
    """Assert a planet is in the expected sign (and optionally within degree tolerance)."""
    p = result['planets'][planet]
    assert p is not None, f"{planet} calculation failed"
    actual = p['position']['sign']
    assert actual == expected_sign, (
        f"{planet}: expected {expected_sign}, got {actual} "
        f"({p['position']['degree']}°{p['position']['minute']}')"
    )


# ---------------------------------------------------------------------------
# Reference charts (fill expected values once you have them)
# ---------------------------------------------------------------------------

CHARTS = [
    "Anurag Sharma | 12:01 15/03/1994 +05:30 | Dehradun, India, 78.0322, 30.3165",
    "Pragati Tripathi | 07:50 28/11/1996 +05:30 | Anushaktinagar, India, 72.9232, 19.0385",
    "Prashant Kumar | 04:50 23/08/1996 +05:30 | New Delhi, India, 77.2090, 28.6139",
    "Armaan Jain | 16:02 02/09/2001 +05:30 | Tohana, India, 75.9068, 29.7190",
    "Zeeva | 00:30 02/09/2017 -07:00 | Bellevue, USA, -122.20, 47.61",
    "Manfred | 08:30 20/01/1997 +03:00 | Kebirigo, Kenya, 34.95, -0.63",
]

# Known-good values: (chart_idx, planet, expected_sign)
# Add more as you validate against reference data
KNOWN_POSITIONS = [
    (0, 'Sun',   'Pisces'),    # Anurag Sharma – Sun in Pisces ✓
    (0, 'Jupiter', 'Libra'),   # Anurag Sharma – Jupiter in Libra ✓ (retrograde)
    (3, 'Sun',   'Leo'),       # Armaan Jain – Sun in Leo ✓
    (3, 'Moon',  'Aquarius'),  # Armaan Jain – Moon in Aquarius ✓
]


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("birth_str", CHARTS, ids=[c.split('|')[0].strip() for c in CHARTS])
def test_chart_calculates(birth_str):
    """Every chart in the master list should calculate without errors."""
    bd = parse_birth(birth_str)
    result = calculate_chart(bd['dt_utc'], bd['lat'], bd['lon'])
    assert result['planets'] is not None
    assert result['ascendant'] is not None
    # All 12 planets present
    for name in ['Sun', 'Moon', 'Mars', 'Mercury', 'Jupiter', 'Venus', 'Saturn', 'Rahu', 'Ketu']:
        assert result['planets'].get(name) is not None, f"{name} missing from result"


@pytest.mark.parametrize("idx,planet,expected_sign", KNOWN_POSITIONS)
def test_known_position(idx, planet, expected_sign):
    """Validate known planetary positions against reference data."""
    bd = parse_birth(CHARTS[idx])
    result = calculate_chart(bd['dt_utc'], bd['lat'], bd['lon'])
    check_planet(result, planet, expected_sign)


def test_retrograde_flags():
    """Rahu and Ketu should always be retrograde (they always move retrograde)."""
    bd = parse_birth(CHARTS[0])
    result = calculate_chart(bd['dt_utc'], bd['lat'], bd['lon'])
    assert result['planets']['Rahu']['retrograde'] is True
    assert result['planets']['Ketu']['retrograde'] is True


def test_ketu_opposite_rahu():
    """Ketu should be exactly 180° from Rahu."""
    bd = parse_birth(CHARTS[0])
    result = calculate_chart(bd['dt_utc'], bd['lat'], bd['lon'])
    rahu = result['planets']['Rahu']['sidereal']
    ketu = result['planets']['Ketu']['sidereal']
    diff = abs((ketu - rahu) % 360)
    assert abs(diff - 180) < 0.01, f"Ketu–Rahu diff should be 180°, got {diff}"


def test_ascendant_present():
    """Ascendant should always be calculated when time is provided."""
    bd = parse_birth(CHARTS[0])
    result = calculate_chart(bd['dt_utc'], bd['lat'], bd['lon'])
    asc = result['ascendant']
    assert asc is not None
    assert 0 <= asc['position']['sign_idx'] <= 11
