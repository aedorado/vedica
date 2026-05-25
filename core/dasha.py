"""Vimshottari dasha calculations using PyJHora."""

from jhora.horoscope.dhasa.graha.vimsottari import vimsottari_mahadasa
from jhora.panchanga import drik
import json


def calculate_vimshottari_dasha(jd, latitude, longitude, timezone_offset):
    """
    Calculate Vimshottari mahadasha periods from birth Julian Day.
    
    Args:
        jd: Julian Day number from birth date/time
        latitude: Birth latitude
        longitude: Birth longitude
        timezone_offset: Timezone offset in hours (e.g., +5.5 for IST)
    
    Returns:
        dict: Mapping of planet names to their start dates (Julian Day)
              e.g., {'Sun': 12345.6, 'Moon': 12567.8, ...}
    """
    try:
        place = drik.Place('Birth', latitude, longitude, timezone_offset)
        
        # Call PyJHora's vimsottari_mahadasa
        mahadashas = vimsottari_mahadasa(
            jd=jd,
            place=place,
            divisional_chart_factor=1,
            chart_method=1,
            star_position_from_moon=1,
            seed_star=3,
            dhasa_starting_planet=1
        )
        
        # Convert to serializable format (planet number -> JD)
        result = {}
        for planet_lord, start_jd in mahadashas.items():
            # planet_lord is an integer (0=Sun, 1=Moon, etc.)
            result[str(planet_lord)] = float(start_jd)
        
        return result
    
    except Exception as e:
        print(f"Error calculating vimshottari dasha: {str(e)}")
        return None
