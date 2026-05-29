"""
Vedic astrology ephemeris calculator using PyJHora (pyjhora).
"""

import logging
from datetime import datetime, timedelta
from jhora.utils import jd_to_gregorian, julian_day_to_date_time_string
from core.planet_dignity import calculate_planet_dignity
from core.ephemeris_pyjhora import calculate_chart as calculate_chart_pyjhora

# Configure logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

def _convert_julian_date_to_datetime(vimshottari_dasha):
    """Convert JD dasha data to human-readable format using PyJHora."""
    if not vimshottari_dasha:
        return None
    
    PLANET_NAMES = ['Sun', 'Moon', 'Mars', 'Mercury', 'Jupiter', 'Venus', 'Saturn', 'Rahu', 'Ketu']
    DASHA_YEARS = {0: 6, 1: 10, 2: 7, 3: 17, 4: 16, 5: 20, 6: 19, 7: 18, 8: 7}
    
    processed = {}
    try:
        for planet_idx_str, start_jd in vimshottari_dasha.items():
            planet_idx = int(planet_idx_str)
            planet_name = PLANET_NAMES[planet_idx]
            years = DASHA_YEARS[planet_idx]
            
            # Use PyJHora's formatted string (includes datetime)
            dt_str = julian_day_to_date_time_string(float(start_jd))
            start_date = dt_str.split()[0]  # Extract YYYY-MM-DD
            start_time = ' '.join(dt_str.split()[1:])  # Extract HH:MM:SS AM/PM
            
            # Parse to datetime, add years for end date
            start_dt = datetime.strptime(start_date, '%Y-%m-%d')
            end_dt = start_dt.replace(year=start_dt.year + years)
            
            processed[planet_name] = {
                'years': years,
                'start_jd': float(start_jd),
                'start_date': start_date,
                'start_time': start_time,
                'start_datetime': dt_str,
                'end_date': end_dt.strftime('%Y-%m-%d'),
            }
    except Exception as e:
        logger.warning(f"Error converting dasha: {e}")
        return None
    
    return processed

def parse_timezone(tz_str):
    """Parse timezone string like '+05:30' or '-08:00' into decimal hours."""
    try:
        sign = 1 if tz_str[0] == '+' else -1
        parts = tz_str[1:].split(':')
        hours = int(parts[0])
        minutes = int(parts[1]) if len(parts) > 1 else 0
        return sign * (hours + minutes / 60)
    except Exception as e:
        logger.error(f"Error parsing timezone '{tz_str}': {e}")
        return 0


 # Helper function to populate yoga_details and yogas_in_chart from yogas dict
def extract_yoga_details_and_yogas_in_chart(yogas_dict):
    yoga_details_list = []
    yogas_in_chart_dict = {}
    # yogas_dict: {chart_num: (yoga_dict, ...other stuff)}
    for chart_key, chart_val in yogas_dict.items():
        # chart_val is a tuple, first element is the yoga dict
        if isinstance(chart_val, tuple) and len(chart_val) > 0 and isinstance(chart_val[0], dict):
            yoga_dict = chart_val[0]
            for code, vals in yoga_dict.items():
                chart = vals[0] if len(vals) > 0 else str(chart_key)
                name = vals[1] if len(vals) > 1 else code
                condition = vals[2] if len(vals) > 2 else ""
                effect = vals[3] if len(vals) > 3 else ""
                yoga_details_list.append({
                    "code": code,
                    "name": name,
                    "condition": condition,
                    "effect": effect,
                })
                if chart not in yogas_in_chart_dict:
                    yogas_in_chart_dict[chart] = []
                if code not in yogas_in_chart_dict[chart]:
                    yogas_in_chart_dict[chart].append(code)
    return yoga_details_list, yogas_in_chart_dict

def calculate_chart(name, birth_date_str, birth_time_str, latitude, longitude, timezone_str):
    """
    Calculate D1 Rasi chart using Swiss Ephemeris.
    
    Args:
        name: Person's name
        birth_date_str: 'YYYY-MM-DD'
        birth_time_str: 'HH:MM'
        latitude: float (-90 to 90)
        longitude: float (-180 to 180)
        timezone_str: '+HH:MM' or '-HH:MM'
    
    Returns:
        dict with chart data (planets, ascendant, house_cusps, ayanamsha, etc.)
        Also includes 'rasi_chart' field for storing PyJHora rasi_chart output
    """
    try:
        logger.info("=" * 80)
        logger.info(f"🟢 CALCULATING D1 CHART FOR {name}")
        logger.info(f"   DOB: {birth_date_str} {birth_time_str} {timezone_str}")
        logger.info(f"   Location: {latitude}°, {longitude}°")
        logger.info("=" * 80)
        
        # Get PyJHora raw data (PRIMARY calculator)
        rasi_chart = None
        retrograde_planets = None
        vimshottari_dasha = None
        try:
            rasi_chart, retrograde_planets, ayanamsha, vimshottari_dasha, yogas = calculate_chart_pyjhora(name, birth_date_str, birth_time_str, latitude, longitude, timezone_str)
            logger.debug(f"PyJHora calculation successful. Retrograde planets: {retrograde_planets}")
            if vimshottari_dasha:
                logger.debug(f"Vimshottari dasha calculated: {len(vimshottari_dasha)} periods")
        except Exception as e:
            logger.warning(f"PyJHora not available or failed: {e}")
            logger.info("=" * 80)
            logger.info("❌ PYJHORA FAILED - NO CHART DATA")
            logger.info("=" * 80)
            raise
        
        logger.info("=" * 80)
        logger.info("✅ D1 CHART CALCULATION COMPLETE")
        logger.info("=" * 80)

        # Compute planet dignities (exaltation, debilitation, mooltrikona, combustion, sign relationships)
        planet_dignity = {}
        if rasi_chart:
            try:
                planet_dignity = calculate_planet_dignity(rasi_chart)
                logger.debug(f"Planet dignities computed: {planet_dignity}")
            except Exception as e:
                logger.warning(f"Could not compute planet dignities: {e}")

        yoga_details, yogas_in_chart = extract_yoga_details_and_yogas_in_chart(yogas)

        return {
            'meta': {
                'name': name,
                'date': birth_date_str,
                'time': birth_time_str,
                'timezone': timezone_str,
                'latitude': latitude,
                'longitude': longitude,
            },
            'ayanamsha': round(ayanamsha, 4),
            'rasi_chart': rasi_chart,
            'retrograde_planets': retrograde_planets,
            'planet_dignity': planet_dignity,
            'vimshottari_dasha': vimshottari_dasha,
            'yoga_details': yoga_details,
            'yogas_in_chart': yogas_in_chart,
        }
    
    except Exception as e:
        logger.error(f"Chart calculation error: {str(e)}", exc_info=True)
        raise

