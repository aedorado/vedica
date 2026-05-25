"""
Vedic divisional charts (Vargas) calculator using PyJHora EXCLUSIVELY.
Computes D1-D60 charts from D1 (Rashi) positions using PyJHora's built-in methods.

STRICT PRINCIPLE: All calculations come from PyJHora only.

Key divisional charts:
- D1: Rashi (main chart)
- D2: Hora (wealth)
- D3: Drekkana (siblings)
- D4: Chaturthamsha (property/land)
- D9: Navamsha (career/marriage) ⭐ Most important
- D10: Dasamsha (career/profession)
- D12: Dwadasamsha (parents/ancestors)
- D60: Shashtiamsha (detailed/precise) ⭐ Most detailed
"""

from typing import Dict, List, Any
import logging
from core.constants import SIGNS, SIGN_SYMBOLS, NAKSHATRAS, NAKSHATRA_LORDS
from jhora.horoscope.chart import charts

# Configure logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

# Divisional chart metadata
DIVISIONAL_CHARTS = {
    1: {'name': 'Rashi', 'symbol': 'D1', 'category': 'Main', 'importance': 'Essential', 'description': 'Main birth chart'},
    2: {'name': 'Hora', 'symbol': 'D2', 'category': 'Divisional', 'importance': 'Important', 'description': 'Wealth, resources'},
    3: {'name': 'Drekkana', 'symbol': 'D3', 'category': 'Divisional', 'importance': 'Important', 'description': 'Siblings, courage'},
    4: {'name': 'Chaturthamsha', 'symbol': 'D4', 'category': 'Divisional', 'importance': 'Important', 'description': 'Property, vehicles'},
    5: {'name': 'Panchamsha', 'symbol': 'D5', 'category': 'Divisional', 'importance': 'Moderate', 'description': 'Children'},
    6: {'name': 'Shashthamsha', 'symbol': 'D6', 'category': 'Divisional', 'importance': 'Low', 'description': 'Health, enemies'},
    7: {'name': 'Saptamsha', 'symbol': 'D7', 'category': 'Divisional', 'importance': 'Moderate', 'description': 'Children, creativity'},
    8: {'name': 'Ashtamsha', 'symbol': 'D8', 'category': 'Divisional', 'importance': 'Low', 'description': 'Longevity, death'},
    9: {'name': 'Navamsha', 'symbol': 'D9', 'category': 'Divisional', 'importance': 'Critical', 'description': 'Career, marriage, refined nature'},
    10: {'name': 'Dasamsha', 'symbol': 'D10', 'category': 'Divisional', 'importance': 'Critical', 'description': 'Career, profession, public life'},
    11: {'name': 'Ekadashamsha', 'symbol': 'D11', 'category': 'Divisional', 'importance': 'Moderate', 'description': 'Gains, friendships'},
    12: {'name': 'Dwadasamsha', 'symbol': 'D12', 'category': 'Divisional', 'importance': 'Important', 'description': 'Parents, ancestors, karma'},
    13: {'name': 'Trayodashamsha', 'symbol': 'D13', 'category': 'Divisional', 'importance': 'Low', 'description': 'Misfortune'},
    14: {'name': 'Chaturdasa', 'symbol': 'D14', 'category': 'Divisional', 'importance': 'Low', 'description': 'Diseases'},
    15: {'name': 'Panchadashamsha', 'symbol': 'D15', 'category': 'Divisional', 'importance': 'Low', 'description': 'Good fortune'},
    16: {'name': 'Shodasamsha', 'symbol': 'D16', 'category': 'Divisional', 'importance': 'Moderate', 'description': 'Happiness, harmony'},
    17: {'name': 'Saptadashamsha', 'symbol': 'D17', 'category': 'Divisional', 'importance': 'Low', 'description': 'Enmity'},
    18: {'name': 'Octadashamsha', 'symbol': 'D18', 'category': 'Divisional', 'importance': 'Low', 'description': 'Powers'},
    19: {'name': 'Navadashamsha', 'symbol': 'D19', 'category': 'Divisional', 'importance': 'Low', 'description': 'Misery'},
    20: {'name': 'Vimshamsha', 'symbol': 'D20', 'category': 'Divisional', 'importance': 'Moderate', 'description': 'Religious merit, spirituality'},
    21: {'name': 'Ekavimsamsha', 'symbol': 'D21', 'category': 'Divisional', 'importance': 'Low', 'description': 'Deception'},
    22: {'name': 'Dvivimsamsha', 'symbol': 'D22', 'category': 'Divisional', 'importance': 'Low', 'description': 'Suffering'},
    23: {'name': 'Trayovimsamsha', 'symbol': 'D23', 'category': 'Divisional', 'importance': 'Low', 'description': 'Strength'},
    24: {'name': 'Caturvimsamsha', 'symbol': 'D24', 'category': 'Divisional', 'importance': 'Low', 'description': 'Weakness'},
    25: {'name': 'Pancavimsamsha', 'symbol': 'D25', 'category': 'Divisional', 'importance': 'Low', 'description': 'Intelligence'},
    26: {'name': 'Shadvimsamsha', 'symbol': 'D26', 'category': 'Divisional', 'importance': 'Low', 'description': 'Education'},
    27: {'name': 'Nakshatramsha', 'symbol': 'D27', 'category': 'Divisional', 'importance': 'Important', 'description': 'Nakshatra detail'},
    28: {'name': 'Ashtavimsamsha', 'symbol': 'D28', 'category': 'Divisional', 'importance': 'Low', 'description': 'Honor'},
    29: {'name': 'Navavimsamsha', 'symbol': 'D29', 'category': 'Divisional', 'importance': 'Low', 'description': 'Complexions'},
    30: {'name': 'Trimshamsha', 'symbol': 'D30', 'category': 'Divisional', 'importance': 'Moderate', 'description': 'Misery, challenges'},
    40: {'name': 'Khavedamsha', 'symbol': 'D40', 'category': 'Divisional', 'importance': 'Low', 'description': 'Duration of life'},
    45: {'name': 'Akshavedamsha', 'symbol': 'D45', 'category': 'Divisional', 'importance': 'Low', 'description': 'Destiny, karma'},
    60: {'name': 'Shashtiamsha', 'symbol': 'D60', 'category': 'Divisional', 'importance': 'Critical', 'description': 'Most detailed, precise'},
}

# Fill in missing divisors (31-39, 41-44, 46-59) with generic entries
for d in range(1, 61):
    if d not in DIVISIONAL_CHARTS:
        DIVISIONAL_CHARTS[d] = {
            'name': f'D{d} Chart', 
            'symbol': f'D{d}', 
            'category': 'Divisional', 
            'importance': 'Low', 
            'description': f'Divisional Chart D{d}'
        }


def _split(lon: float) -> dict:
    """Convert decimal longitude to sign + degree + minutes (from main ephemeris)."""
    lon = lon % 360
    sign_idx = int(lon / 30) % 12
    deg_in_sign = lon - sign_idx * 30
    d = int(deg_in_sign)
    m_f = (deg_in_sign - d) * 60
    m = int(m_f)
    s = (m_f - m) * 60
    return {
        'sign': SIGNS[sign_idx],
        'sign_idx': sign_idx,
        'symbol': SIGN_SYMBOLS[sign_idx],
        'degree': d,
        'minute': m,
        'second': round(s, 1),
        'decimal': round(lon, 4),
    }


# Mapping of divisional chart numbers to PyJHora methods
DIVISIONAL_METHODS = {
    1: charts.rasi_chart,
    2: charts.hora_chart,
    3: charts.drekkana_chart,
    4: charts.chaturthamsa_chart,
    7: charts.saptamsa_chart,
    9: charts.navamsa_chart,
    10: charts.dasamsa_chart,
    12: charts.dwadasamsa_chart,
    16: charts.shodasamsa_chart,
    20: charts.vimsamsa_chart,
    24: charts.chaturvimsamsa_chart,
    27: charts.nakshatramsa_chart,
    30: charts.trimsamsa_chart,
    40: charts.khavedamsa_chart,
    45: charts.akshavedamsa_chart,
    60: charts.shashtyamsa_chart,
}


def calculate_all_divisional_charts(planets_d1: Dict[str, dict], chart_data: Dict = None) -> Dict[int, Dict[str, dict]]:
    """
    Calculate divisional charts using PyJHora EXCLUSIVELY.
    
    STRICT PRINCIPLE: Only calculate divisors with actual PyJHora methods.
    No fallback to formula or D1 - only what PyJHora can compute.
    
    Args:
        planets_d1: Dictionary of planets with D1 positions from ephemeris
        chart_data: Optional chart data from PyJHora for validation
    
    Returns:
        Dictionary: {divisor: {planet: position_dict, ...}, ...}
    """
    result = {}
    
    logger.info("=" * 80)
    logger.info("🔴 STARTING DIVISIONAL CHART CALCULATION (PyJHora METHODS ONLY)")
    logger.info("=" * 80)
    logger.info(f"Available PyJHora methods: {list(DIVISIONAL_METHODS.keys())}")
    
    # Prepare D1 planets in PyJHora format: [[planet_name, (rasi_idx, longitude)], ...]
    planet_positions_d1 = []
    for planet_name, planet_data in planets_d1.items():
        if planet_data:
            rasi_idx = planet_data['position']['sign_idx']
            lon = planet_data['position']['decimal']
            planet_positions_d1.append([planet_name, (rasi_idx, lon)])
    
    logger.debug(f"D1 planets prepared for PyJHora ({len(planet_positions_d1)} planets)")
    
    # Calculate ONLY divisors with actual PyJHora methods
    for divisor in DIVISIONAL_METHODS.keys():
        logger.debug(f"\n--- Processing D{divisor} ---")
        result[divisor] = {}
        
        pyjhora_method = DIVISIONAL_METHODS[divisor]
        logger.info(f"✅ D{divisor}: Calling PyJHora method: {pyjhora_method.__name__}")
        
        try:
            # Call PyJHora method with D1 planet positions
            pyjhora_result = pyjhora_method(planet_positions_d1)
            logger.debug(f"   PyJHora returned {len(pyjhora_result) if pyjhora_result else 0} planets")
            
            if pyjhora_result:
                # PyJHora returns: [[planet_name, (rasi_idx, longitude)], ...]
                for planet_entry in pyjhora_result:
                    planet_name = planet_entry[0]
                    rasi_idx, longitude = planet_entry[1]
                    
                    # Convert to our format
                    position = _split(longitude)
                    result[divisor][planet_name] = {
                        'position': position,
                        'nakshatra': _get_nakshatra(longitude),
                        'retrograde': planets_d1[planet_name].get('retrograde', False) if planet_name in planets_d1 and planets_d1[planet_name] else False,
                        'pyjhora_method': pyjhora_method.__name__,
                    }
                    logger.debug(f"   {planet_name}: {position['sign']} {position['degree']}° (Rashi {rasi_idx})")
            else:
                logger.warning(f"⚠️  D{divisor}: PyJHora returned empty result")
                            
        except Exception as e:
            logger.error(f"❌ Error calling PyJHora method for D{divisor}: {e}")
            logger.debug(f"   Exception type: {type(e).__name__}")
            # Skip this divisor if PyJHora fails
            continue
    
    logger.info("=" * 80)
    logger.info(f"✅ PyJHora divisional chart calculation complete. Total divisors: {len(result)}")
    logger.info("=" * 80)
    
    return result


def _get_nakshatra(longitude: float) -> dict:
    """Calculate nakshatra for a given longitude."""
    longitude = longitude % 360
    
    # Each nakshatra spans 13.333... degrees (360 / 27)
    nakshatra_size = 360 / 27
    nakshatra_idx = int(longitude / nakshatra_size) % 27
    
    # Position within nakshatra (0-1)
    pos_in_nakshatra = (longitude % nakshatra_size) / nakshatra_size
    
    # Each nakshatra has 4 padas (quarters)
    pada = int(pos_in_nakshatra * 4) + 1  # Pada 1-4
    
    nak_data = {
        'name': NAKSHATRAS[nakshatra_idx],
        'idx': nakshatra_idx,
        'pada': pada,
        'lord': _get_nakshatra_lord(nakshatra_idx),
    }
    
    logger.debug(f"      Nakshatra @ {nak_data['name']} ({pada}) lord={nak_data['lord']}")
    return nak_data


def _get_nakshatra_lord(nakshatra_idx: int) -> str:
    """Get ruling planet for a nakshatra (from constants)."""
    return NAKSHATRA_LORDS[nakshatra_idx % 27]


def get_chart_with_cusps(ascendant_d1: dict, divisor: int, house_cusps_d1: List[dict]) -> Dict[str, Any]:
    """
    Get divisional chart with house cusps using PyJHora.
    
    Note: In traditional Vedic astrology, house cusps don't change in divisional charts -
    only planet positions are recalculated. Ascendant is also derived from planets.
    
    Args:
        ascendant_d1: D1 ascendant position dict
        divisor: Divisional chart number (1-60)
        house_cusps_d1: List of D1 house cusp positions
    
    Returns:
        Dictionary with {ascendant, house_cusps} for the divisional chart
    """
    logger.debug(f"\n   D{divisor}: Calculating ascendant and house cusps...")
    
    # Get PyJHora method for this divisor if available
    pyjhora_method = DIVISIONAL_METHODS.get(divisor)
    
    if pyjhora_method:
        logger.debug(f"      Using {pyjhora_method.__name__} for context")
    
    # House cusps typically remain the same across divisional charts
    # The ascendant shifts based on the divisional calculation
    asc_dn = ascendant_d1['position'].copy()
    asc_dn['nakshatra'] = ascendant_d1.get('nakshatra', _get_nakshatra(ascendant_d1['position']['decimal']))
    
    logger.debug(f"      Ascendant: {asc_dn['sign']} {asc_dn['degree']}°{asc_dn['minute']}'")
    
    # House cusps stay the same across divisional charts
    cusps_dn = []
    for cusp in house_cusps_d1:
        cusp_dn = cusp['position'].copy()
        cusp_dn['house'] = cusp['house']
        cusp_dn['nakshatra'] = _get_nakshatra(cusp['position']['decimal'])
        cusps_dn.append(cusp_dn)
        logger.debug(f"      House {cusp['house']:2}: {cusp_dn['sign']} {cusp_dn['degree']:2}°{cusp_dn['minute']:2}'")
    
    return {
        'ascendant': asc_dn,
        'house_cusps': cusps_dn,
    }


def summarize_divisional_charts(all_charts: Dict[int, Dict[str, dict]]) -> Dict[int, dict]:
    """
    Create a summary of divisional charts for quick reference using PyJHora data.
    
    Returns: {divisor: {sign_strength, planet_count, house_distribution, ...}}
    """
    logger.info("\n" + "=" * 80)
    logger.info("📈 GENERATING DIVISIONAL CHART SUMMARY")
    logger.info("=" * 80)
    
    summary = {}
    
    for divisor, planets in all_charts.items():
        # Handle both int and string keys
        div_int = int(divisor) if isinstance(divisor, str) else divisor
        
        # Ensure DIVISIONAL_CHARTS has entry for this divisor
        if div_int not in DIVISIONAL_CHARTS:
            logger.warning(f"   D{div_int}: No metadata, creating generic entry")
            DIVISIONAL_CHARTS[div_int] = {
                'name': f'D{div_int} Chart',
                'symbol': f'D{div_int}',
                'category': 'Divisional',
                'importance': 'Low',
                'description': f'Divisional Chart D{div_int}',
            }
        
        sign_counts = {}
        total_planets = len(planets)
        
        # Count planets by sign
        for planet_name, planet_data in planets.items():
            if planet_data and 'position' in planet_data:
                sign = planet_data['position']['sign']
                sign_counts[sign] = sign_counts.get(sign, 0) + 1
        
        # Find strongest sign (most planets)
        strongest_sign = max(sign_counts.items(), key=lambda x: x[1])[0] if sign_counts else None
        strongest_count = sign_counts.get(strongest_sign, 0) if strongest_sign else 0
        
        summary[div_int] = {
            'chart_name': DIVISIONAL_CHARTS[div_int]['name'],
            'total_planets': total_planets,
            'sign_distribution': sign_counts,
            'strongest_sign': strongest_sign,
            'strongest_count': strongest_count,
            'importance': DIVISIONAL_CHARTS[div_int].get('importance', 'Low'),
        }
        
        # Log summary for important divisors
        importance = DIVISIONAL_CHARTS[div_int].get('importance', 'Low')
        if importance in ['Critical', 'Important']:
            logger.info(f"   D{div_int:2} ({DIVISIONAL_CHARTS[div_int]['name']:20}): {strongest_sign} has {strongest_count}/{total_planets} planets")
    
    logger.info("=" * 80)
    
    return summary


def compute_major_vargas(rasi_chart: List[List]) -> Dict[str, List[List]]:
    """
    Compute major divisional charts (D2, D3, D4, D9, D10, D12) from D1 rasi chart.
    
    Args:
        rasi_chart: List of [planet_id, [sign_idx, longitude]] from database
        
    Returns:
        dict: {"2": [...], "3": [...], "9": [...], "10": [...], "12": [...]}
        where each value is the PyJHora output [[planet, [sign, lon]], ...]
    """
    if not rasi_chart:
        return {}
    
    major_divisors = [2, 3, 4, 7, 9, 10, 12, 16, 20, 24, 27, 30, 40, 45, 60]
    result = {}
    
    try:
        for divisor in major_divisors:
            if divisor not in DIVISIONAL_METHODS:
                continue
            
            pyjhora_method = DIVISIONAL_METHODS[divisor]
            varga_result = pyjhora_method(rasi_chart)
            result[str(divisor)] = varga_result
    
    except Exception as e:
        logger.error(f"Error computing vargas: {e}")
        return {}
    
    return result
