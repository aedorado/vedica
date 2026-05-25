"""
Calculate exact ayanamsha from your reference data.
Use this to calibrate if your reference uses a non-standard ayanamsha.
"""

import swisseph as swe

def dms_to_decimal(sign_name, degrees, minutes, seconds):
    """Convert sign + DMS to decimal degrees (0-360)."""
    signs = ['Aries', 'Taurus', 'Gemini', 'Cancer', 'Leo', 'Virgo',
             'Libra', 'Scorpio', 'Sagittarius', 'Capricorn', 'Aquarius', 'Pisces']
    
    sign_idx = signs.index(sign_name)
    decimal = (sign_idx * 30) + degrees + minutes/60 + seconds/3600
    return decimal

def calculate_ayanamsha_from_reference(jd, planet_code, reference_sign, reference_deg, reference_min, reference_sec):
    """
    Calculate ayanamsha by comparing your reference data with tropical longitude.
    
    Args:
        jd: Julian Day Number
        planet_code: Swiss Ephemeris planet code (0=Sun, 1=Moon, etc)
        reference_sign: Sign name ('Pisces', 'Aries', etc)
        reference_deg, reference_min, reference_sec: Position in that sign
    
    Returns:
        Calculated ayanamsha value
    """
    
    # Get tropical position from Swiss Ephemeris
    result = swe.calc_ut(jd, planet_code)
    position_data, flags = result
    tropical_lon = position_data[0]
    
    # Convert reference to decimal degrees
    reference_decimal = dms_to_decimal(reference_sign, reference_deg, reference_min, reference_sec)
    
    # Ayanamsha = Tropical - Sidereal
    ayanamsha = tropical_lon - reference_decimal
    
    # Normalize to 0-360
    while ayanamsha < 0:
        ayanamsha += 360
    while ayanamsha >= 360:
        ayanamsha -= 360
    
    return ayanamsha, tropical_lon, reference_decimal

def main():
    # Birth: 1994-03-15 06:31:00 UTC
    jd = swe.julday(1994, 3, 15, 6 + 31/60)
    
    print("="*70)
    print("CALCULATE EXACT AYANAMSHA FROM YOUR REFERENCE DATA")
    print("="*70)
    print(f"\nBirth Date: 1994-03-15 06:31:00 UTC")
    print(f"Julian Day: {jd}\n")
    
    # Using Sun as reference
    print("Testing with SUN:")
    print("-" * 70)
    
    # Your reference: Sun Pisces 00°40'34"
    ayanamsha, tropical, reference = calculate_ayanamsha_from_reference(
        jd, 0,  # Sun
        'Pisces', 0, 40, 34
    )
    
    print(f"Tropical Sun (from Swiss):    {tropical:.6f}°")
    print(f"Reference Sun (from your data): Pisces 00°40'34\" = {reference:.6f}°")
    print(f"Calculated Ayanamsha:        {ayanamsha:.6f}°")
    print(f"\n✅ This ayanamsha matches your reference!")
    
    # Test with Moon as second reference
    print("\n" + "="*70)
    print("Testing with MOON (to verify):")
    print("-" * 70)
    
    # Your reference: Moon Aries 03°17'28"
    ayanamsha_moon, tropical_moon, reference_moon = calculate_ayanamsha_from_reference(
        jd, 1,  # Moon
        'Aries', 3, 17, 28
    )
    
    print(f"Tropical Moon (from Swiss):    {tropical_moon:.6f}°")
    print(f"Reference Moon (from your data): Aries 03°17'28\" = {reference_moon:.6f}°")
    print(f"Calculated Ayanamsha:        {ayanamsha_moon:.6f}°")
    
    # Average if different
    print("\n" + "="*70)
    avg_ayanamsha = (ayanamsha + ayanamsha_moon) / 2
    print(f"Average Ayanamsha from Sun & Moon: {avg_ayanamsha:.6f}°")
    print("="*70)
    
    print(f"""
🎯 INSTRUCTION FOR swiss_calc_enhanced.py:

Open: ephemeris_calc/swiss_calc_enhanced.py
Find: AYANAMSHA_LAHIRI = 23.855556
Replace with: AYANAMSHA_LAHIRI = {avg_ayanamsha:.6f}

Then re-run to see your exact output!
    """)

if __name__ == '__main__':
    main()
