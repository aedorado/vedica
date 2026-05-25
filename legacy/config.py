"""
Global configuration and constants for Vedic Astrology analysis.
Centralizes all constants, abbreviations, and settings.
"""

# =====================================================================
# PLANETS
# =====================================================================

# All planets in Vedic astrology
PLANETS = {
    'Sun', 'Moon', 'Mars', 'Mercury', 'Jupiter', 'Venus', 'Saturn', 'Rahu', 'Ketu'
}

# Planet abbreviations (3 characters)
PLANET_ABBREVIATIONS = {
    'Su': 'Sun',
    'Mo': 'Moon',
    'Ma': 'Mars',
    'Me': 'Mercury',
    'Ju': 'Jupiter',
    'Ve': 'Venus',
    'Sa': 'Saturn',
    'Ra': 'Rahu',
    'Ke': 'Ketu',
}

# Reverse mapping for abbreviations
PLANET_TO_ABBREVIATION = {v: k for k, v in PLANET_ABBREVIATIONS.items()}

# Fixed planet sequence for combinations (Vedic order)
PLANET_ORDER = ['Sun', 'Moon', 'Jupiter', 'Mercury', 'Venus', 'Saturn', 'Rahu', 'Ketu']

# =====================================================================
# HOUSES
# =====================================================================

# House numbers
HOUSES = set(range(1, 13))  # 1-12

# House categories
HOUSE_CATEGORIES = {
    'kendra': {1, 4, 7, 10},        # Quadrants
    'trikona': {1, 5, 9},            # Triangles
    'upachaya': {3, 6, 10, 11},      # Increasing houses
    'dusthana': {6, 8, 12},          # Difficult houses
    'maraka': {2, 7},                # Death-inflicting
    'favorable': {1, 2, 3, 4, 5, 7, 9, 10, 11},  # Favorable for most
}

# =====================================================================
# ZODIAC SIGNS (RASHIS)
# =====================================================================

ZODIAC_SIGNS = {
    'Aries', 'Taurus', 'Gemini', 'Cancer', 'Leo', 'Virgo',
    'Libra', 'Scorpio', 'Sagittarius', 'Capricorn', 'Aquarius', 'Pisces'
}

# Zodiac sign abbreviations (2 characters)
ZODIAC_ABBREVIATIONS = {
    'Ar': 'Aries',
    'Ta': 'Taurus',
    'Ge': 'Gemini',
    'Ca': 'Cancer',
    'Le': 'Leo',
    'Vi': 'Virgo',
    'Li': 'Libra',
    'Sc': 'Scorpio',
    'Sa': 'Sagittarius',
    'Cp': 'Capricorn',
    'Aq': 'Aquarius',
    'Pi': 'Pisces',
}

# Reverse mapping for zodiac abbreviations
ZODIAC_TO_ABBREVIATION = {v: k for k, v in ZODIAC_ABBREVIATIONS.items()}

# =====================================================================
# DATABASE CONFIGURATION
# =====================================================================

DATABASE_CONFIG = {
    'path': 'astro_cache.db',
    'version': 2,  # Schema version for migrations
}

# Database table names
DB_TABLES = {
    'cache': 'astro_cache',
}

# =====================================================================
# DATA FIELD MAPPINGS
# =====================================================================

# Map planet data keys for easy access
PLANET_DATA_FIELDS = {
    'sign': 'PlanetRasiD1Sign',           # Sign in D1 (Rashi)
    'house': 'PlanetHouse',               # House number
    'degree': 'PlanetDegreeInSign',       # Degree in sign
    'longitude': 'PlanetLongitude',       # Ecliptic longitude
}

# Map house data keys for easy access
HOUSE_DATA_FIELDS = {
    'sign': 'HouseRasiSign',              # Sign in D1
    'constellation': 'HouseConstellation', # Nakshatra
    'lord': 'LordOfHouse',                # House lord
    'planets': 'PlanetsInHouse',          # Planets present
}

# =====================================================================
# QUERY ENGINE
# =====================================================================

# Query result limits
QUERY_CONFIG = {
    'max_results': 1000,
    'default_page_size': 50,
    'enable_caching': True,
}

# =====================================================================
# LOGGING
# =====================================================================

LOG_FORMAT = '%(asctime)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s'
LOG_LEVEL = 'DEBUG'

# =====================================================================
# HELPERS
# =====================================================================

def normalize_planet(planet_name: str) -> str:
    """Convert abbreviation to full name, or validate full name. Case-insensitive."""
    planet_name_normalized = planet_name.capitalize()  # Mo, Su, etc.
    if planet_name_normalized in PLANET_ABBREVIATIONS:
        return PLANET_ABBREVIATIONS[planet_name_normalized]
    if planet_name in PLANETS:
        return planet_name
    raise ValueError(f"Unknown planet: {planet_name}")


def normalize_zodiac(zodiac_name: str) -> str:
    """Convert abbreviation to full name, or validate full name. Case-insensitive."""
    # Try as abbreviation first (2 chars, capitalize)
    if len(zodiac_name) == 2:
        zodiac_normalized = zodiac_name.capitalize()
        if zodiac_normalized in ZODIAC_ABBREVIATIONS:
            return ZODIAC_ABBREVIATIONS[zodiac_normalized]
    
    # Try as full name
    if zodiac_name in ZODIAC_SIGNS:
        return zodiac_name
    
    raise ValueError(f"Unknown zodiac sign: {zodiac_name}")


def get_house_category(house_num: int) -> list[str]:
    """Return all categories a house belongs to."""
    categories = []
    for cat_name, cat_houses in HOUSE_CATEGORIES.items():
        if house_num in cat_houses:
            categories.append(cat_name)
    return categories
