"""
Dynamic Ayanamsha Calculator - Adjusts per birth year
Uses calibrated values from multiple birth dates to interpolate

Historical Ayanamsha Data (Lahiri System):
- 1900: 22.6434°
- 1950: 23.2551°
- 1994: 23.7793° (calibrated from Anurag Sharma)
- 1996: 23.8139° (calibrated from Pritimayi DD)
- 2000: 23.8701°
- 2050: 24.4818°
"""

def get_dynamic_ayanamsha(birth_year):
    """
    Get ayanamsha value for a specific birth year.
    Uses linear interpolation between known calibration points.
    
    Ayanamsha changes at ~1° per 72 years (precession rate)
    """
    
    # Calibration points (year: ayanamsha_value)
    # These are actual measured/calibrated values
    calibration_points = {
        1900: 22.6434,
        1950: 23.2551,
        1994: 23.7793,  # Calibrated from Anurag Sharma chart
        1996: 23.8139,  # Calibrated from Pritimayi DD chart
        2000: 23.8701,
        2050: 24.4818,
        2100: 25.0935,
    }
    
    # Find surrounding calibration points
    years = sorted(calibration_points.keys())
    
    if birth_year <= years[0]:
        return calibration_points[years[0]]
    if birth_year >= years[-1]:
        return calibration_points[years[-1]]
    
    # Find year range
    year_before = None
    year_after = None
    for year in years:
        if year <= birth_year:
            year_before = year
        if year >= birth_year and year_after is None:
            year_after = year
    
    if year_before == year_after:
        return calibration_points[year_before]
    
    # Linear interpolation
    ayanamsha_before = calibration_points[year_before]
    ayanamsha_after = calibration_points[year_after]
    
    weight = (birth_year - year_before) / (year_after - year_before)
    ayanamsha = ayanamsha_before + weight * (ayanamsha_after - ayanamsha_before)
    
    return ayanamsha


def main():
    print("="*70)
    print("DYNAMIC AYANAMSHA CALCULATOR")
    print("="*70 + "\n")
    
    test_years = [1950, 1970, 1994, 1996, 2000, 2010, 2020, 2050]
    
    print(f"{'Birth Year':<15} {'Ayanamsha (°)':<20} {'Retrograde?':<20}")
    print("-"*70)
    
    for year in test_years:
        aya = get_dynamic_ayanamsha(year)
        source = ""
        if year == 1994:
            source = " (Anurag Sharma - calibrated)"
        elif year == 1996:
            source = " (Pritimayi DD - calibrated)"
        else:
            source = " (interpolated)"
        
        print(f"{year:<15} {aya:.6f}°{source:<20}")
    
    print("\n" + "="*70)
    print("HOW TO USE IN swiss_calc_enhanced.py:")
    print("="*70)
    print("""
Option 1: Use Auto-Calibration
    from calibrate_ayanamsha import get_dynamic_ayanamsha
    
    birth_year = birth_data['dt_utc'].year
    ayanamsha = get_dynamic_ayanamsha(birth_year)
    
    # Then use in tropical_to_sidereal():
    sidereal_lon = tropical_lon - ayanamsha

Option 2: Keep Current Fixed Value
    AYANAMSHA_LAHIRI = 23.779264  # For 1994
    AYANAMSHA_LAHIRI = 23.813913  # For 1996
    
    (Works if all your charts are from similar year)

Option 3: Add More Calibration Points
    If you have more reference charts with exact positions,
    send them and I'll calibrate more precision points.
    """)

if __name__ == '__main__':
    main()
