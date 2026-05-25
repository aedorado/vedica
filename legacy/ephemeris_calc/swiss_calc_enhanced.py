"""
Enhanced Swiss Ephemeris calculator with Vedic astrology features.
Includes: Sidereal zodiac, Nakshatras, Retrograde info, All planets including outer planets.
"""

import swisseph as swe
from datetime import datetime, timedelta
import math

# Dynamic Ayanamsha Calculator
def get_dynamic_ayanamsha(birth_year):
    """Get ayanamsha value for a specific birth year (interpolated)."""
    calibration_points = {
        1900: 22.6434, 1950: 23.2551, 1994: 23.7793, 1996: 23.8139,
        2000: 23.8701, 2050: 24.4818, 2100: 25.0935,
    }
    
    years = sorted(calibration_points.keys())
    if birth_year <= years[0]:
        return calibration_points[years[0]]
    if birth_year >= years[-1]:
        return calibration_points[years[-1]]
    
    year_before = year_after = None
    for year in years:
        if year <= birth_year:
            year_before = year
        if year >= birth_year and year_after is None:
            year_after = year
    
    if year_before == year_after:
        return calibration_points[year_before]
    
    ayanamsha_before = calibration_points[year_before]
    ayanamsha_after = calibration_points[year_after]
    weight = (birth_year - year_before) / (year_after - year_before)
    return ayanamsha_before + weight * (ayanamsha_after - ayanamsha_before)


# Swiss Ephemeris planet codes
PLANET_CODES = {
    'Sun': 0, 'Moon': 1, 'Mercury': 2, 'Venus': 3, 'Mars': 4,
    'Jupiter': 5, 'Saturn': 6, 'Uranus': 7, 'Neptune': 8, 'Pluto': 9,
    'Rahu': 10, 'Ketu': 11
}

# Tropical zodiac signs
ZODIAC_TROPICAL = [
    'Aries', 'Taurus', 'Gemini', 'Cancer', 'Leo', 'Virgo',
    'Libra', 'Scorpio', 'Sagittarius', 'Capricorn', 'Aquarius', 'Pisces'
]

# Sidereal zodiac (same names, different starting point)
ZODIAC_SIDEREAL = ZODIAC_TROPICAL

# 27 Nakshatras (lunar mansions), each 13°20' (800 arc minutes)
NAKSHATRAS = [
    'Ashvini', 'Bharani', 'Krittika', 'Rohini', 'Mrigashirsha', 'Ardra', 'Punarvasu',
    'Pushya', 'Ashlesha', 'Magha', 'P. Phalguni', 'U. Phalguni', 'Hasta',
    'Chitra', 'Swati', 'Vishakha', 'Anuradha', 'Jyeshta', 'Mula',
    'P. Ashadha', 'U. Ashadha', 'Sravana', 'Dhanishta', 'Satabhisa',
    'P. Bhadrapada', 'U. Bhadrapada', 'Revati'
]


def parse_birth_data(name, birth_str, location_str):
    """Parse birth data in format: "Name | HH:MM DD/MM/YYYY ±HH:MM | Place, Longitude, Latitude" """
    parts = birth_str.split('|')
    
    time_part = parts[1].strip()
    time_items = time_part.split()
    time_str, date_str, tz_str = time_items[0], time_items[1], time_items[2]
    
    hour, minute = map(int, time_str.split(':'))
    day, month, year = map(int, date_str.split('/'))
    
    tz_sign = 1 if tz_str[0] == '+' else -1
    tz_hours, tz_mins = map(int, tz_str[1:].split(':'))
    tz_offset = tz_sign * (tz_hours + tz_mins / 60)
    
    location_part = parts[2].strip()
    coords = location_part.split(',')
    # Format: Place, Longitude, Latitude
    longitude = float(coords[-2].strip())
    latitude = float(coords[-1].strip())
    
    # Convert to UTC
    dt_local = datetime(year, month, day, hour, minute, 0)
    dt_utc = dt_local - timedelta(hours=tz_offset)
    
    return {
        'name': name,
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
    
    return swe.julday(year, month, int(day), day - int(day))


def tropical_to_sidereal(tropical_lon, birth_year=1994):
    """Convert tropical longitude to sidereal using dynamic ayanamsha."""
    ayanamsha = get_dynamic_ayanamsha(birth_year)
    sidereal_lon = tropical_lon - ayanamsha
    if sidereal_lon < 0:
        sidereal_lon += 360
    return sidereal_lon


def split_degree(degree):
    """Split degree into sign, degree, minute, second."""
    sign_idx = int(degree / 30)
    deg_in_sign = degree - (sign_idx * 30)
    degree_int = int(deg_in_sign)
    minutes = (deg_in_sign - degree_int) * 60
    minute_int = int(minutes)
    seconds = (minutes - minute_int) * 60
    
    return {
        'sign': ZODIAC_SIDEREAL[sign_idx % 12],
        'sign_idx': sign_idx % 12,
        'degree': degree_int,
        'minute': minute_int,
        'second': seconds,
        'total': degree
    }


def get_nakshatra_pada(sidereal_longitude):
    """Calculate nakshatra (lunar mansion) and pada (quarter) from sidereal longitude."""
    # Each nakshatra is 13°20' (13.333...)
    nakshatra_size = 13 + 20/60  # 13.333...
    nak_idx = int(sidereal_longitude / nakshatra_size) % 27
    
    # Position within nakshatra (0-13.333)
    pos_in_nak = sidereal_longitude - (nak_idx * nakshatra_size)
    
    # Pada: divide into 4 parts of 3°20' each
    pada = int(pos_in_nak / 3.333) + 1
    pada = min(pada, 4)  # Ensure 1-4
    
    return {
        'nakshatra': NAKSHATRAS[nak_idx],
        'nakshatra_idx': nak_idx,
        'pada': pada,
        'position_in_nak': pos_in_nak
    }


def is_retrograde(planet_code, jd):
    """Check if planet is retrograde."""
    # Calculate planet motion direction
    # Positive speed = direct, negative speed = retrograde
    result = swe.calc_ut(jd, planet_code)
    position_data, flags = result
    speed = position_data[3]  # longitude speed
    
    return speed < 0


def calculate_planets_sidereal(birth_data):
    """Calculate all planets in sidereal zodiac with Nakshatra."""
    jd = datetime_to_jd(birth_data['dt_utc'])
    birth_year = birth_data['dt_utc'].year
    
    planets = {}
    rahu_lon = None  # Store Rahu longitude to calculate Ketu as 180° opposite
    
    for name, code in PLANET_CODES.items():
        try:
            result = swe.calc_ut(jd, code)
            position_data, flags = result
            
            tropical_lon = position_data[0]
            latitude = position_data[1]
            distance = position_data[2]
            speed = position_data[3]
            
            # Convert to sidereal using dynamic ayanamsha (based on birth year)
            sidereal_lon = tropical_to_sidereal(tropical_lon, birth_year)
            
            # For Ketu, calculate as 180° opposite of Rahu
            if name == 'Rahu':
                rahu_lon = sidereal_lon
            elif name == 'Ketu' and rahu_lon is not None:
                sidereal_lon = (rahu_lon + 180) % 360
            
            # Split into sign/degree
            position = split_degree(sidereal_lon)
            
            # Get nakshatra and pada
            nak_info = get_nakshatra_pada(sidereal_lon)
            
            # Check retrograde
            retrograde = is_retrograde(code, jd)
            
            planets[name] = {
                'tropical': tropical_lon,
                'sidereal': sidereal_lon,
                'position': position,
                'latitude': latitude,
                'distance': distance,
                'speed': speed,
                'retrograde': retrograde,
                'nakshatra': nak_info['nakshatra'],
                'pada': nak_info['pada']
            }
        except Exception as e:
            print(f"❌ Error calculating {name}: {e}")
            planets[name] = None
    
    return planets


def calculate_ascendant_sidereal(birth_data):
    """Calculate ascendant (house 1 cusp) in sidereal zodiac."""
    jd = datetime_to_jd(birth_data['dt_utc'])
    latitude = birth_data['latitude']
    longitude = birth_data['longitude']
    birth_year = birth_data['dt_utc'].year
    
    try:
        cusps, ascmc = swe.houses(jd, latitude, longitude, b'P')
        
        # Ascendant is ASCMC[0]
        tropical_asc = ascmc[0]
        sidereal_asc = tropical_to_sidereal(tropical_asc, birth_year)
        
        position = split_degree(sidereal_asc)
        nak_info = get_nakshatra_pada(sidereal_asc)
        
        return {
            'tropical': tropical_asc,
            'sidereal': sidereal_asc,
            'position': position,
            'nakshatra': nak_info['nakshatra'],
            'pada': nak_info['pada']
        }
    except Exception as e:
        print(f"❌ Error calculating Ascendant: {e}")
        return None


def format_output(planets, asc):
    """Format output like the reference chart."""
    print("\n" + "="*80)
    print("VEDIC ASTROLOGY BIRTH CHART (SIDEREAL/NIRAYANA)")
    print("="*80)
    print(f"{'Planet':<12} {'Sign':<12} {'Latitude':<15} {'Nakshatra':<18} {'Pada':<5}")
    print("-"*80)
    
    # Print Ascendant first
    if asc:
        lat_str = f"{asc['position']['degree']:02d}°{asc['position']['minute']:02d}'{asc['position']['second']:05.2f}\""
        print(f"{'ASC':<12} {asc['position']['sign']:<12} {lat_str:<15} {asc['nakshatra']:<18} {asc['pada']}")
    
    # Planet order matching reference chart
    planet_order = ['Sun', 'Moon', 'Mars', 'Mercury', 'Jupiter', 'Venus', 'Saturn', 'Rahu', 'Ketu', 'Uranus', 'Neptune', 'Pluto']
    
    for name in planet_order:
        if name in planets and planets[name]:
            p = planets[name]
            pos_str = f"{p['position']['sign']:<12}"
            lat_str = f"{p['position']['degree']:02d}°{p['position']['minute']:02d}'{p['position']['second']:05.2f}\""
            nak_str = f"{p['nakshatra']:<18}"
            pada_str = f"{p['pada']}"
            
            # Add retrograde marker
            if p['retrograde']:
                name_str = f"{name} [R]"
            else:
                name_str = name
            
            print(f"{name_str:<12} {pos_str} {lat_str:<15} {nak_str} {pada_str}")
    
    print("="*80)


def main():
    # Test data
    birth_str = "Anurag Sharma | 12:01 15/03/1994 +05:30 | Dehradun, India, 30.3165, 78.0322"
    
    print("\n🔄 Parsing birth data...")
    birth_data = parse_birth_data("Anurag Sharma", birth_str, "")
    
    print(f"✅ Birth Data: {birth_data['dt_utc']} UTC")
    print(f"   Location: {birth_data['latitude']}°N, {birth_data['longitude']}°E")
    
    print("\n🪐 Calculating planetary positions...")
    planets = calculate_planets_sidereal(birth_data)
    
    print("\n🏠 Calculating ascendant...")
    asc = calculate_ascendant_sidereal(birth_data)
    
    print("\n📊 Formatting output...")
    format_output(planets, asc)


if __name__ == '__main__':
    main()
