"""
Planet dignity calculator - exaltation, debilitation, mooltrikona, combustion, sign relationships.
Uses PyJHora constants and functions exclusively.
"""

import logging
from typing import Dict, List
from jhora.const import (
    moola_trikona_range_of_planets,
    planet_deep_exaltation_longitudes,
    planet_deep_exaltation_tolerance,
    friendly_planets,
    enemy_planets,
)
from jhora.horoscope.chart.charts import planets_in_combustion as pyjhora_planets_in_combustion

logger = logging.getLogger(__name__)

# Planet names (0-8: Sun-Ketu)
PLANET_NAMES = ['Sun', 'Moon', 'Mars', 'Mercury', 'Jupiter', 'Venus', 'Saturn', 'Rahu', 'Ketu']

# Exaltation signs for each planet (sign index 0-11)
# Map: planet_id -> exaltation_sign_idx
EXALTATION_SIGNS = {
    0: 0,    # Sun exalted in Aries
    1: 1,    # Moon exalted in Taurus
    2: 9,    # Mars exalted in Capricorn
    3: 5,    # Mercury exalted in Virgo
    4: 3,    # Jupiter exalted in Cancer
    5: 11,   # Venus exalted in Pisces
    6: 6,    # Saturn exalted in Libra
}

# Debilitation signs (opposite of exaltation)
DEBILITATION_SIGNS = {
    0: 6,    # Sun debilitated in Libra
    1: 7,    # Moon debilitated in Scorpio
    2: 3,    # Mars debilitated in Cancer
    3: 11,   # Mercury debilitated in Pisces
    4: 9,    # Jupiter debilitated in Capricorn
    5: 5,    # Venus debilitated in Virgo
    6: 0,    # Saturn debilitated in Aries
}

# Sign rulers (sign_idx -> planet_idx)
# Each sign is ruled by one of the 7 classical planets
SIGN_RULERS = {
    0: 2,    # Aries (0) ruled by Mars (2)
    1: 5,    # Taurus (1) ruled by Venus (5)
    2: 3,    # Gemini (2) ruled by Mercury (3)
    3: 1,    # Cancer (3) ruled by Moon (1)
    4: 0,    # Leo (4) ruled by Sun (0)
    5: 3,    # Virgo (5) ruled by Mercury (3)
    6: 5,    # Libra (6) ruled by Venus (5)
    7: 2,    # Scorpio (7) ruled by Mars (2)
    8: 4,    # Sagittarius (8) ruled by Jupiter (4)
    9: 6,    # Capricorn (9) ruled by Saturn (6)
    10: 6,   # Aquarius (10) ruled by Saturn (6)
    11: 4,   # Pisces (11) ruled by Jupiter (4)
}

# Planet own signs (planet_idx -> list of sign indices)
# Each classical planet rules certain signs
PLANET_OWN_SIGNS = {
    0: [4],        # Sun rules Leo (4)
    1: [3],        # Moon rules Cancer (3)
    2: [0, 7],     # Mars rules Aries (0) and Scorpio (7)
    3: [2, 5],     # Mercury rules Gemini (2) and Virgo (5)
    4: [8, 11],    # Jupiter rules Sagittarius (8) and Pisces (11)
    5: [1, 6],     # Venus rules Taurus (1) and Libra (6)
    6: [9, 10],    # Saturn rules Capricorn (9) and Aquarius (10)
}


def calculate_planet_dignity(rasi_chart: List[List]) -> Dict[str, List]:
    """
    Calculate planet dignities from D1 rasi chart using PyJHora.
    
    Args:
        rasi_chart: [[planet_id, [sign_idx, longitude]], ...]
                   where planet_id = 'L' (lagna), '0'-'8' (planets as strings)
    
    Returns:
        {
            'exalted': [planet_ids],           # In exaltation sign
            'deeply_exalted': [planet_ids],    # At exact exaltation point (±1°)
            'debilitated': [planet_ids],       # In debilitation sign
            'deeply_debilitated': [planet_ids],# At exact debilitation point (±1°)
            'own_sign': [planet_ids],          # In own sign (but NOT moola_trikona)
            'moola_trikona': [planet_ids],     # Own sign + specific degree range (more powerful)
            'combust': [planet_ids],
            'enemy_sign': [planet_ids],
            'neutral_sign': [planet_ids],
            'friendly_sign': [planet_ids],
        }
    """
    if not rasi_chart:
        return {}
    
    result = {
        'exalted': [],
        'deeply_exalted': [],
        'debilitated': [],
        'deeply_debilitated': [],
        'own_sign': [],
        'moola_trikona': [],
        'combust': [],
        'enemy_sign': [],
        'neutral_sign': [],
        'friendly_sign': [],
    }
    
    # Get combustion planets using PyJHora's built-in function
    combustion_planet_indices = []
    try:
        combustion_planet_indices = pyjhora_planets_in_combustion(rasi_chart, use_absolute_longitude=True)
        logger.debug(f"PyJHora combustion detection: {combustion_planet_indices}")
    except Exception as e:
        logger.warning(f"Could not compute combustion using PyJHora: {e}")
        combustion_planet_indices = []
    
    # Process each planet
    for item in rasi_chart:
        planet_id = item[0]
        sign_idx, longitude = item[1]
        
        # Skip lagna
        if planet_id == 'L':
            continue
        
        # Convert planet_id to int (0-8)
        try:
            p_idx = int(planet_id)
        except ValueError:
            continue
        
        if p_idx < 0 or p_idx > 8:
            continue
        
        # Check exaltation SIGN (broader check)
        if _is_in_exaltation_sign(p_idx, sign_idx):
            result['exalted'].append(planet_id)
        
        # Check deep exaltation (exact point, narrow tolerance)
        if _is_deeply_exalted(p_idx, sign_idx, longitude):
            result['deeply_exalted'].append(planet_id)
        
        # Check debilitation SIGN (broader check)
        if _is_in_debilitation_sign(p_idx, sign_idx):
            result['debilitated'].append(planet_id)
        
        # Check deep debilitation (exact point, narrow tolerance)
        if _is_deeply_debilitated(p_idx, sign_idx, longitude):
            result['deeply_debilitated'].append(planet_id)
        
        # Check moola trikona (takes precedence over plain own sign)
        in_moola_trikona = _is_moola_trikona(p_idx, sign_idx, longitude)
        in_own_sign = False
        if in_moola_trikona:
            result['moola_trikona'].append(planet_id)
        # Check own sign (only if NOT in moola trikona)
        elif _is_in_own_sign(p_idx, sign_idx):
            result['own_sign'].append(planet_id)
            in_own_sign = True
        
        # Check combustion using PyJHora result (returns integer planet indices)
        if p_idx in combustion_planet_indices:
            result['combust'].append(planet_id)
        
        # Check sign relationship (only for planets 0-6, not nodes, and NOT in own sign or moola trikona)
        if p_idx < 7 and not in_own_sign and not in_moola_trikona:
            relationship = _get_sign_relationship(p_idx, sign_idx)
            if relationship == 'enemy':
                result['enemy_sign'].append(planet_id)
            elif relationship == 'neutral':
                result['neutral_sign'].append(planet_id)
            elif relationship == 'friend':
                result['friendly_sign'].append(planet_id)
    
    return result


def _is_in_exaltation_sign(planet_idx: int, sign_idx: int) -> bool:
    """Check if planet is in its exaltation sign (broader check)."""
    return planet_idx in EXALTATION_SIGNS and EXALTATION_SIGNS[planet_idx] == sign_idx


def _is_deeply_exalted(planet_idx: int, sign_idx: int, longitude: float) -> bool:
    """Check if planet is at exact exaltation degree (deep exaltation, within ±1°)."""
    # First check: must be in exaltation sign
    if not _is_in_exaltation_sign(planet_idx, sign_idx):
        return False
    
    if planet_idx >= len(planet_deep_exaltation_longitudes):
        return False
    
    exalt_lon = planet_deep_exaltation_longitudes[planet_idx]
    tolerance = planet_deep_exaltation_tolerance  # Usually ±1°
    
    # Get degree within the sign (0-30)
    deg_in_sign = longitude % 30
    exalt_deg_in_sign = exalt_lon % 30
    
    # Calculate difference
    diff = abs(deg_in_sign - exalt_deg_in_sign)
    if diff > 15:
        diff = 30 - diff
    
    return diff <= tolerance


def _is_in_debilitation_sign(planet_idx: int, sign_idx: int) -> bool:
    """Check if planet is in its debilitation sign (broader check)."""
    return planet_idx in DEBILITATION_SIGNS and DEBILITATION_SIGNS[planet_idx] == sign_idx


def _is_deeply_debilitated(planet_idx: int, sign_idx: int, longitude: float) -> bool:
    """Check if planet is at exact debilitation degree (within ±1°)."""
    # First check: must be in debilitation sign
    if not _is_in_debilitation_sign(planet_idx, sign_idx):
        return False
    
    if planet_idx >= len(planet_deep_exaltation_longitudes):
        return False
    
    exalt_lon = planet_deep_exaltation_longitudes[planet_idx]
    tolerance = planet_deep_exaltation_tolerance
    
    # Debilitation point is opposite of exaltation (180° away in the zodiac)
    # Get degree within sign for both exaltation and debilitation points
    exalt_deg_in_sign = exalt_lon % 30
    debil_deg_in_sign = (exalt_deg_in_sign + 15) % 30  # Opposite degree within sign
    
    # Get degree within the sign
    deg_in_sign = longitude % 30
    
    # Calculate difference
    diff = abs(deg_in_sign - debil_deg_in_sign)
    if diff > 15:
        diff = 30 - diff
    
    return diff <= tolerance


def _is_in_own_sign(planet_idx: int, sign_idx: int) -> bool:
    """Check if planet is in its own sign (rashi)."""
    return planet_idx in PLANET_OWN_SIGNS and sign_idx in PLANET_OWN_SIGNS[planet_idx]


def _is_moola_trikona(planet_idx: int, sign_idx: int, longitude: float) -> bool:
    """Check if planet is in moola trikona (own sign + specific degree range)."""
    if planet_idx not in moola_trikona_range_of_planets:
        return False
    
    sign, start_deg, end_deg = moola_trikona_range_of_planets[planet_idx]
    
    # Must be in correct sign
    if sign_idx != sign:
        return False
    
    # Must be in degree range
    deg_in_sign = longitude % 30
    return start_deg <= deg_in_sign <= end_deg


def _get_sign_relationship(planet_idx: int, sign_idx: int) -> str:
    """
    Get relationship of planet to sign based on the sign's ruler.
    
    In Vedic astrology, a planet's relationship to a sign is based on its relationship
    to the sign's ruler planet. For example:
    - Saturn in Taurus is checked against Venus (Taurus' ruler)
    - If Saturn and Venus are friendly, Saturn is in a friendly sign
    
    Args:
        planet_idx: Index of planet (0-8)
        sign_idx: Index of sign (0-11)
    
    Returns: 'friend', 'enemy', or 'neutral'
    """
    if planet_idx >= len(friendly_planets):
        return 'neutral'
    
    # Get the ruler of this sign
    if sign_idx not in SIGN_RULERS:
        return 'neutral'
    
    ruler_idx = SIGN_RULERS[sign_idx]
    
    # Check if planet is in its own sign (planet's own sign is defined as sign matching planet index)
    # Sun rules Leo(4), Moon rules Cancer(3), Mars rules Aries(0) and Scorpio(7), etc.
    if planet_idx < 7:  # Classical planets only
        own_signs = [s for s, r in SIGN_RULERS.items() if r == planet_idx]
        if sign_idx in own_signs:
            return 'friend'  # Own sign is strongest friend
    
    # Get friendly and enemy planets for this planet
    print("frined etc")
    print(planet_idx, sign_idx, friendly_planets, enemy_planets)
    friends = friendly_planets[planet_idx]
    enemies = enemy_planets[planet_idx]
    
    # Check relationship with the sign's ruler
    if ruler_idx in friends:
        return 'friend'
    elif ruler_idx in enemies:
        return 'enemy'
    else:
        return 'neutral'
