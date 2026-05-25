"""
Test different ayanamsha systems to match reference output.
Shows how to use Swiss Ephemeris ayanamsha functions.
"""

import swisseph as swe
from datetime import datetime

# Common Ayanamsha systems and their approximate values
AYANAMSHAS = {
    'Lahiri': 23.855556,           # Most common for Vedic astrology (India)
    'Fagan/Bradley': 24.542222,    # Occidental astrology
    'Deluce': 27.825278,
    'Raman': 20.390583,
    'Krishnamurti': 23.562083,
    'Ushashashi': 27.247222,
    'Takao': 24.184167,
    'Sri Yukteshwar': 21.642222,
    'B.V. Raman': 20.390583,
}

# Reference data from user's chart
REFERENCE = {
    'ASC': 'Gemini 09°01\'55"',    # = 69.0319°
    'Sun': 'Pisces 00°40\'34"',    # = 330.6761°
    'Moon': 'Aries 03°17\'28"',    # = 3.2911°
    'Mars': 'Aquarius 12°23\'13"', # = 312.3869°
}

def dms_to_decimal(degrees, minutes, seconds):
    """Convert degrees/minutes/seconds to decimal degrees."""
    return degrees + minutes/60 + seconds/3600

def decimal_to_dms(decimal):
    """Convert decimal degrees to degrees/minutes/seconds."""
    d = int(decimal)
    m = int((decimal - d) * 60)
    s = ((decimal - d) * 60 - m) * 60
    return d, m, s

def tropical_to_sidereal_custom(tropical_lon, ayanamsha):
    """Convert tropical to sidereal with custom ayanamsha."""
    sidereal = tropical_lon - ayanamsha
    if sidereal < 0:
        sidereal += 360
    return sidereal

def test_ayanamsha(ayanamsha_name, ayanamsha_value, jd):
    """Test an ayanamsha against reference data."""
    print(f"\n{'='*70}")
    print(f"Testing: {ayanamsha_name} (Ayanamsha: {ayanamsha_value:.6f}°)")
    print(f"{'='*70}")
    
    # Test with Sun
    result = swe.calc_ut(jd, 0)  # Sun
    position_data, flags = result
    tropical_sun = position_data[0]
    sidereal_sun = tropical_to_sidereal_custom(tropical_sun, ayanamsha_value)
    
    d, m, s = decimal_to_dms(sidereal_sun)
    sign_idx = int(sidereal_sun / 30)
    deg_in_sign = sidereal_sun - (sign_idx * 30)
    
    signs = ['Aries', 'Taurus', 'Gemini', 'Cancer', 'Leo', 'Virgo',
             'Libra', 'Scorpio', 'Sagittarius', 'Capricorn', 'Aquarius', 'Pisces']
    
    d_in_sign = int(deg_in_sign)
    m_in_sign = int((deg_in_sign - d_in_sign) * 60)
    s_in_sign = ((deg_in_sign - d_in_sign) * 60 - m_in_sign) * 60
    
    print(f"Tropical Sun: {tropical_sun:.4f}° = {tropical_sun:.2f}°")
    print(f"Sidereal Sun: {sidereal_sun:.4f}° = {signs[sign_idx]} {d_in_sign:02d}°{m_in_sign:02d}'{s_in_sign:05.2f}\"")
    print(f"Reference:    Pisces 00°40'34\"")
    print(f"Match: {'✅ CLOSE' if 330 < sidereal_sun < 332 else '❌ NO MATCH'}")

def get_swiss_ephemeris_ayanamsha(jd):
    """Get ayanamsha value from Swiss Ephemeris library itself."""
    # Swiss Ephemeris has pre-defined ayanamsha indices
    # SE_ASP_LABELTYPE = 0 (no ayanamsha)
    # You can query using swe.get_ayanamsa()
    
    print("\n" + "="*70)
    print("SWISS EPHEMERIS BUILT-IN AYANAMSHA")
    print("="*70)
    
    try:
        # Query various ayanamsha systems
        ayanamsha_fagan = swe.get_ayanamsa(jd)  # Default/Fagan
        print(f"Default (Fagan): {ayanamsha_fagan:.6f}°")
        
        # Note: Swiss Ephemeris library may have limited ayanamsha support
        # Most Vedic astrology systems use Lahiri
    except Exception as e:
        print(f"Note: {e}")

def main():
    # Birth date: 1994-03-15 06:31:00 UTC
    jd = swe.julday(1994, 3, 15, 6 + 31/60)
    
    print("\n" + "="*70)
    print("AYANAMSHA COMPARISON TEST")
    print(f"Birth: 1994-03-15 06:31:00 UTC")
    print(f"JD: {jd}")
    print("="*70)
    
    # Test each ayanamsha
    for name, value in AYANAMSHAS.items():
        test_ayanamsha(name, value, jd)
    
    # Show Swiss Ephemeris options
    get_swiss_ephemeris_ayanamsha(jd)
    
    print("\n" + "="*70)
    print("RECOMMENDATION")
    print("="*70)
    print("""
If your reference output doesn't match any standard ayanamsha:

1. Check which ayanamsha your reference system uses:
   - VedAstro API documentation
   - Online calculator used to generate reference
   - Astrology software used

2. Once you know the ayanamsha:
   - Update AYANAMSHA_LAHIRI in swiss_calc_enhanced.py
   - Replace: AYANAMSHA_LAHIRI = 23.855556
   - With your value

3. To reverse-engineer the ayanamsha:
   - Take one planet position from reference
   - Calculate difference from tropical longitude
   - That's your ayanamsha value

Example:
   If tropical Sun = 354.296°
   And sidereal Sun = Pisces 00°40' = 330.676°
   Then ayanamsha = 354.296 - 330.676 = 23.62°
    """)

if __name__ == '__main__':
    main()
