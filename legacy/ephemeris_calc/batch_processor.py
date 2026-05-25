"""
Batch process multiple birth charts
Input format: Name | HH:MM DD/MM/YYYY ±HH:MM | Place, Longitude, Latitude
"""

from swiss_calc_enhanced import parse_birth_data, calculate_planets_sidereal, calculate_ascendant_sidereal

CHARTS = """
Anurag Sharma | 12:01 15/03/1994 +05:30 | Dehradun, India, 78.0322, 30.3165
Pragati Tripathi | 07:50 28/11/1996 +05:30 | Anushaktinagar, India, 72.9232, 19.0385
Prashant Kumar | 04:50 23/08/1996 +05:30 | New Delhi, India, 77.2090, 28.6139
Armaan Jain | 16:02 02/09/2001 +05:30 | Tohana, India, 75.9068, 29.7190
Zeeva | 00:30 02/09/2017 -07:00 | Bellevue, USA, -122.20, 47.61
Manfred | 08:30 20/01/1997 +03:00 | Kebirigo, Kenya, 34.95, -0.63
""".strip().split('\n')

def process_chart(birth_str):
    """Process single chart and return summary."""
    try:
        parts = birth_str.split('|')
        name = parts[0].strip()
        
        birth_data = parse_birth_data(name, birth_str, "")
        planets = calculate_planets_sidereal(birth_data)
        asc = calculate_ascendant_sidereal(birth_data)
        
        # Find retrograde planets
        retrogrades = [p for p in planets if planets[p] and planets[p]['retrograde']]
        
        return {
            'name': name,
            'date': birth_data['dt_utc'].strftime('%Y-%m-%d %H:%M UTC'),
            'sun': f"{planets['Sun']['position']['sign']} {planets['Sun']['position']['degree']}°{planets['Sun']['position']['minute']}'",
            'moon': f"{planets['Moon']['position']['sign']} {planets['Moon']['position']['degree']}°{planets['Moon']['position']['minute']}'",
            'asc': f"{asc['position']['sign']} {asc['position']['degree']}°{asc['position']['minute']}'" if asc else "❌",
            'retrograde_count': len(retrogrades),
            'retrograde': ', '.join(retrogrades) if retrogrades else 'None'
        }
    except Exception as e:
        return {
            'name': birth_str.split('|')[0].strip(),
            'error': str(e)
        }

print("="*90)
print("BATCH PROCESSING BIRTH CHARTS")
print("="*90)
print(f"\n{'Name':<25} {'Date':<20} {'Sun Sign':<15} {'Moon Sign':<15} {'Retro':<15}")
print("-"*90)

for birth_str in CHARTS:
    result = process_chart(birth_str)
    
    if 'error' in result:
        print(f"{result['name']:<25} ❌ {result['error']}")
    else:
        retro_str = f"{result['retrograde_count']} planets"
        print(f"{result['name']:<25} {result['sun']:<15} {result['moon']:<15} {retro_str:<15}")

print("\n" + "="*90)
print("✅ Batch processing complete!")
print("="*90)
