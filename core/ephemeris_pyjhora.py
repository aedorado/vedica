"""
PyJHora Integration - Calculate Vedic Chart Data (D1 Rasi Chart)
"""
import swisseph as swe
import logging
from jhora.horoscope.chart.charts import rasi_chart
from jhora.panchanga.drik import Place, set_ayanamsa_mode, planets_in_retrograde
from jhora.horoscope.dhasa.graha.vimsottari import vimsottari_mahadasa
from jhora.utils import julian_day_number
from datetime import datetime
from core.constants import NAKSHATRAS, NAKSHATRA_LORDS

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

set_ayanamsa_mode('LAHIRI')

# Use Swiss Ephemeris' built-in Lahiri ayanamsha — most accurate, no manual table.
swe.set_sid_mode(swe.SIDM_LAHIRI)

# Planet order: 0=Sun, 1=Moon, 2=Mars, 3=Mercury, 4=Jupiter, 5=Venus, 6=Saturn, 7=Rahu, 8=Ketu, 9=Uranus, 10=Neptune, 11=Pluto
PLANET_COLORS = {
    'Sun': '#f59e0b',
    'Moon': '#94a3b8',
    'Mars': '#ef4444',
    'Mercury': '#10b981',
    'Jupiter': '#f97316',
    'Venus': '#ec4899',
    'Saturn': '#6366f1',
    'Rahu': '#8b5cf6',
    'Ketu': '#14b8a6',
    'Uranus': '#06b6d4',
    'Neptune': '#3b82f6',
    'Pluto': '#71717a'
}

def get_ayanamsha(jd: float) -> float:
    """Return Lahiri ayanamsha (degrees) for a Julian Day Number."""
    return swe.get_ayanamsa_ut(jd)

def parse_timezone(tz_str):
    """Parse timezone string like '+05:30' or '-08:00' into decimal hours"""
    try:
        sign = 1 if tz_str[0] == '+' else -1
        parts = tz_str[1:].split(':')
        hours = int(parts[0])
        minutes = int(parts[1]) if len(parts) > 1 else 0
        return sign * (hours + minutes / 60)
    except:
        return 0

def calculate_chart(name, birth_date_str, birth_time_str, latitude, longitude, timezone_str):
    """
    Calculate raw D1 Rasi chart using PyJHora
    
    Args:
        name: Person's name (unused, kept for signature compatibility)
        birth_date_str: 'YYYY-MM-DD'
        birth_time_str: 'HH:MM'
        latitude: float
        longitude: float
        timezone_str: '+HH:MM' or '-HH:MM'
    
    Returns:
        tuple: (raw_chart, retrograde_planets)
        - raw_chart: [[planet_id/label, (rashi_num, longitude)], ...]
        - retrograde_planets: list of planet IDs (0-8) that are retrograde
    """
    try:

        # Parse inputs
        birth_date = datetime.strptime(birth_date_str, '%Y-%m-%d')
        birth_time = datetime.strptime(birth_time_str, '%H:%M').time()
        tz_offset = parse_timezone(timezone_str)
        
        # Calculate Julian Day Number for UTC time
        jd = julian_day_number(
            (birth_date.year, birth_date.month, birth_date.day),
            (birth_time.hour, birth_time.minute, birth_time.second)
        )
        logger.debug(f"Julian Day: {jd}")

        place_obj = Place(name='place', latitude=latitude, longitude=longitude, timezone=tz_offset)
        chart = rasi_chart(jd, place_obj)
        
        # Get retrograde planets
        retrograde_list = planets_in_retrograde(jd, place_obj)
        
        # Calculate Vimshottari dasha
        try:
            mahadashas = vimsottari_mahadasa(
                jd=jd,
                place=place_obj,
                divisional_chart_factor=1,
                chart_method=1,
                star_position_from_moon=1,
                seed_star=3,
                dhasa_starting_planet=1
            )
            # Convert to serializable format (planet number -> JD)
            logger.info(f"mahadashas={mahadashas}")
            vimshottari_dasha = {str(lord): float(start_jd) for lord, start_jd in mahadashas.items()}
        except Exception as dasha_error:
            logger.warning(f"Failed to calculate vimshottari dasha: {str(dasha_error)}")
            vimshottari_dasha = None
        
        # Return raw chart data, retrograde info, ayanamsha, and dasha
        logger.info(f"Returning chart={chart}, retrograde_list={retrograde_list}, ayanamsha={get_ayanamsha(jd)}, vimshottari_dasha={vimshottari_dasha}")
        return chart, retrograde_list, get_ayanamsha(jd), vimshottari_dasha
    
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise ValueError(f"Failed to calculate chart: {str(e)}")
