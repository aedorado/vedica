"""
Test with new birth chart and verify retrograde detection.
Pritimayi DD | 07:50 28/11/1996 +05:30 | Mumbai, India, 72.92, 13.04
"""

import swisseph as swe
from swiss_calc_enhanced import (
    parse_birth_data, calculate_planets_sidereal, calculate_ascendant_sidereal,
    format_output
)

def main():
    # New test data
    birth_str = "Pritimayi DD | 07:50 28/11/1996 +05:30 | Mumbai, India, 72.92, 13.04"
    
    print("\n" + "="*80)
    print("TESTING NEW CHART: Pritimayi DD")
    print("="*80)
    
    try:
        print("\n🔄 Parsing birth data...")
        birth_data = parse_birth_data("Pritimayi DD", birth_str, "")
        
        print(f"✅ Birth Data: {birth_data['dt_utc']} UTC")
        print(f"   Location: {birth_data['latitude']}°N, {birth_data['longitude']}°E")
        
        print("\n🪐 Calculating planetary positions...")
        planets = calculate_planets_sidereal(birth_data)
        
        print("\n🏠 Calculating ascendant...")
        asc = calculate_ascendant_sidereal(birth_data)
        
        print("\n📊 Formatting output...")
        format_output(planets, asc)
        
        # Show detailed retrograde info
        print("\n" + "="*80)
        print("RETROGRADE INFORMATION")
        print("="*80)
        
        planet_order = ['Sun', 'Moon', 'Mars', 'Mercury', 'Jupiter', 'Venus', 'Saturn', 'Rahu', 'Ketu', 'Uranus', 'Neptune', 'Pluto']
        
        print(f"{'Planet':<12} {'Retrograde':<12} {'Speed (°/day)':<15}")
        print("-"*80)
        
        for name in planet_order:
            if name in planets and planets[name]:
                p = planets[name]
                retro_str = "🔄 YES [R]" if p['retrograde'] else "Direct"
                speed_str = f"{p['speed']:.6f}°"
                print(f"{name:<12} {retro_str:<12} {speed_str:<15}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    main()
