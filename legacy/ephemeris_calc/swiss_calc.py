"""
Calculate planetary positions and house cusps using Swiss Ephemeris.
This bypasses the VedAstro API and uses pyswisseph directly.
"""

import swisseph as swe
from datetime import datetime, timedelta
import math

# Swiss Ephemeris planet codes (0-9 are Sun through Pluto)
PLANET_CODES = {
    'Sun': 0, 'Moon': 1, 'Mercury': 2, 'Venus': 3, 'Mars': 4,
    'Jupiter': 5, 'Saturn': 6, 'Rahu': 10, 'Ketu': 11  # Rahu=True Node, Ketu=South Node
}

# Zodiac signs (0-11)
ZODIAC_NAMES = [
    'Aries', 'Taurus', 'Gemini', 'Cancer', 'Leo', 'Virgo',
    'Libra', 'Scorpio', 'Sagittarius', 'Capricorn', 'Aquarius', 'Pisces'
]

# House cusps (for Placidus system)
HOUSE_NAMES = [f'House{i}' for i in range(1, 13)]


def parse_birth_data(name, birth_str, location_str):
    """
    Parse birth data string.
    Format: "Name | HH:MM DD/MM/YYYY ±HH:MM | Place, Country, Lat, Long"
    Example: "Anurag Sharma | 12:01 15/03/1994 +05:30 | Dehradun, India, 30.3165, 78.0322"
    """
    parts = birth_str.split('|')
    
    # Parse time
    time_part = parts[1].strip()  # "12:01 15/03/1994 +05:30"
    time_items = time_part.split()
    time_str = time_items[0]  # "12:01"
    date_str = time_items[1]  # "15/03/1994"
    tz_str = time_items[2]    # "+05:30"
    
    hour, minute = map(int, time_str.split(':'))
    day, month, year = map(int, date_str.split('/'))
    
    tz_sign = 1 if tz_str[0] == '+' else -1
    tz_hours, tz_mins = map(int, tz_str[1:].split(':'))
    tz_offset = tz_sign * (tz_hours + tz_mins / 60)
    
    # Parse location
    location_part = parts[2].strip()
    coords = location_part.split(',')
    latitude = float(coords[-2].strip())
    longitude = float(coords[-1].strip())
    
    # Create UTC datetime (subtract timezone offset)
    dt = datetime(year, month, day, hour, minute)
    dt_utc = dt - timedelta(hours=tz_offset)
    
    return {
        'name': name,
        'dt_local': dt,
        'dt_utc': dt_utc,
        'latitude': latitude,
        'longitude': longitude,
        'tz_offset': tz_offset
    }


def datetime_to_jd(dt_utc):
    """Convert UTC datetime to Julian Day Number."""
    year = dt_utc.year
    month = dt_utc.month
    day = dt_utc.day + dt_utc.hour / 24.0 + dt_utc.minute / 1440.0 + dt_utc.second / 86400.0
    
    # Simple Julian Day calculation
    a = (14 - month) // 12
    y = year + 4800 - a
    m = month + 12 * a - 3
    jd = day + (153 * m + 2) // 5 + 365 * y + y // 4 - y // 100 + y // 400 - 32045
    return jd


def split_degree(degree):
    """Convert degree float to sign, degree, minute, second."""
    sign_idx = int(degree / 30)
    degree_in_sign = degree % 30
    
    deg_int = int(degree_in_sign)
    minutes_frac = (degree_in_sign - deg_int) * 60
    minutes = int(minutes_frac)
    seconds = (minutes_frac - minutes) * 60
    
    return {
        'sign': ZODIAC_NAMES[sign_idx],
        'degree': deg_int,
        'minute': minutes,
        'second': seconds,
        'total': degree
    }


def calculate_planets(birth_data):
    """Calculate planetary positions using Swiss Ephemeris."""
    jd = datetime_to_jd(birth_data['dt_utc'])
    
    planets = {}
    for name, code in PLANET_CODES.items():
        try:
            # calc_ut returns: (position_tuple, flags)
            # where position_tuple = (lon, lat, distance, lon_vel, lat_vel, dist_vel)
            result = swe.calc_ut(jd, code)
            position_data, flags = result
            
            longitude = position_data[0]  # Tropical longitude
            latitude = position_data[1]
            distance = position_data[2]
            lon_speed = position_data[3]
            
            # Split into sign/degree/minute/second
            planets[name] = {
                'longitude': longitude,
                'position': split_degree(longitude),
                'latitude': latitude,
                'distance': distance,
                'speed': lon_speed
            }
            print(f"✅ {name}: {planets[name]['position']['sign']} {planets[name]['position']['degree']}°{planets[name]['position']['minute']}'{planets[name]['position']['second']:.0f}\"")
        except Exception as e:
            print(f"❌ Error calculating {name}: {e}")
            import traceback
            traceback.print_exc()
            planets[name] = None
    
    return planets


def calculate_houses(birth_data):
    """Calculate house cusps using Placidus system."""
    jd = datetime_to_jd(birth_data['dt_utc'])
    latitude = birth_data['latitude']
    longitude = birth_data['longitude']
    
    try:
        # Placidus house system (code b'P')
        # houses(jd, lat, lon, housetype) returns (cusps, ascmc)
        cusps, ascmc = swe.houses(jd, latitude, longitude, b'P')
        
        houses = {}
        for i in range(12):
            cusp_long = cusps[i]
            houses[i + 1] = {
                'cusp': cusp_long,
                'position': split_degree(cusp_long),
            }
            print(f"✅ House {i+1}: {houses[i+1]['position']['sign']} {houses[i+1]['position']['degree']}°{houses[i+1]['position']['minute']}'")
        
        # Ascendant (ascmc[0]), Midheaven (ascmc[1])
        asc = split_degree(ascmc[0])
        mc = split_degree(ascmc[1])
        print(f"✅ Ascendant: {asc['sign']} {asc['degree']}°{asc['minute']}'")
        print(f"✅ Midheaven: {mc['sign']} {mc['degree']}°{mc['minute']}'")
        
        return houses, ascmc
    except Exception as e:
        print(f"❌ Error calculating houses: {e}")
        import traceback
        traceback.print_exc()
        return None, None


def main():
    # Initialize Swiss Ephemeris
    swe.set_ephe_path('/usr/local/share/swisseph')  # Default path, may need adjustment
    
    # Test data
    birth_input = "Anurag Sharma | 12:01 15/03/1994 +05:30 | Dehradun, India, 30.3165, 78.0322"
    
    print("=" * 70)
    print("SWISS EPHEMERIS CALCULATOR")
    print("=" * 70)
    
    # Parse input
    birth_data = parse_birth_data("Anurag Sharma", birth_input, birth_input)
    print(f"\n📅 Birth Data:")
    print(f"   Name: {birth_data['name']}")
    print(f"   Local: {birth_data['dt_local']} (UTC {birth_data['tz_offset']:+.1f}h)")
    print(f"   UTC: {birth_data['dt_utc']}")
    print(f"   Location: {birth_data['latitude']:.4f}°N, {birth_data['longitude']:.4f}°E")
    print()
    
    # Calculate planets
    print("🪐 PLANETARY POSITIONS:")
    planets = calculate_planets(birth_data)
    print()
    
    # Calculate houses
    print("🏠 HOUSE CUSPS (Placidus):")
    houses, ascmc = calculate_houses(birth_data)
    print()
    
    # Summary
    print("=" * 70)
    print("SUMMARY")
    print("=" * 70)
    for name, data in planets.items():
        if data:
            pos = data['position']
            print(f"{name:10s}: {pos['sign']:12s} {pos['degree']:2d}°{pos['minute']:2d}'{pos['second']:5.1f}\"")
    
    return birth_data, planets, houses, ascmc


if __name__ == '__main__':
    main()
