"""
Vedic astrology constants shared across modules.
Includes zodiac signs, nakshatras, planet information, etc.
"""

SIGNS = [
    'Aries', 'Taurus', 'Gemini', 'Cancer', 'Leo', 'Virgo',
    'Libra', 'Scorpio', 'Sagittarius', 'Capricorn', 'Aquarius', 'Pisces',
]

SIGN_SYMBOLS = ['♈', '♉', '♊', '♋', '♌', '♍', '♎', '♏', '♐', '♑', '♒', '♓']

PLANET_NAMES = ['Sun', 'Moon', 'Mars', 'Mercury', 'Jupiter', 'Venus', 'Saturn', 'Rahu', 'Ketu', 'Uranus', 'Neptune', 'Pluto']

NAKSHATRAS = [
    'Ashvini', 'Bharani', 'Krittika', 'Rohini', 'Mrigashirsha', 'Ardra',
    'Punarvasu', 'Pushya', 'Ashlesha', 'Magha', 'P. Phalguni', 'U. Phalguni',
    'Hasta', 'Chitra', 'Swati', 'Vishakha', 'Anuradha', 'Jyeshtha', 'Mula',
    'P. Ashadha', 'U. Ashadha', 'Shravana', 'Dhanishtha', 'Shatabhisha',
    'P. Bhadrapada', 'U. Bhadrapada', 'Revati',
]

# Nakshatra lords for Vimshottari dasha
NAKSHATRA_LORDS = [
    'Ketu', 'Venus', 'Sun', 'Moon', 'Mars', 'Rahu',
    'Jupiter', 'Saturn', 'Mercury', 'Ketu', 'Venus', 'Sun',
    'Moon', 'Mars', 'Rahu', 'Jupiter', 'Saturn', 'Mercury',
    'Ketu', 'Venus', 'Sun', 'Moon', 'Mars', 'Rahu',
    'Jupiter', 'Saturn', 'Mercury',
]

PLANET_DISPLAY_ORDER = [
    'Sun', 'Moon', 'Mars', 'Mercury', 'Jupiter', 'Venus',
    'Saturn', 'Rahu', 'Ketu', 'Uranus', 'Neptune', 'Pluto',
]

SIGN_ABBR = ['Ari', 'Tau', 'Gem', 'Can', 'Leo', 'Vir', 'Lib', 'Sco', 'Sag', 'Cap', 'Aqu', 'Pis']

SIGN_FULL = ['Aries', 'Taurus', 'Gemini', 'Cancer', 'Leo', 'Virgo', 'Libra', 'Scorpio', 'Sagittarius', 'Capricorn', 'Aquarius', 'Pisces']

PLANET_COLORS = {
    'Sun': '#f59e0b', 'Moon': '#e2e8f0', 'Mars': '#ef4444',
    'Mercury': '#10b981', 'Jupiter': '#f97316', 'Venus': '#ec4899',
    'Saturn': '#6366f1', 'Rahu': '#8b5cf6', 'Ketu': '#14b8a6',
    'Uranus': '#06b6d4', 'Neptune': '#3b82f6', 'Pluto': '#71717a',
}

PLANET_GLYPHS = {
    'Sun': '☉', 'Moon': '☽', 'Mars': '♂', 'Mercury': '☿',
    'Jupiter': '♃', 'Venus': '♀', 'Saturn': '♄',
    'Rahu': '☊', 'Ketu': '☋', 'Uranus': '♅', 'Neptune': '♆', 'Pluto': '♇',
}
