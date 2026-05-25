def extract_planet_positions(all_planet_data):
    result = {}
    for planet, data in all_planet_data.items():
        house, sign, degree = None, None, None
        if data and isinstance(data, dict):
            house_str = data.get('HousePlanetOccupiesBasedOnSign')
            if isinstance(house_str, str) and 'House' in house_str:
                house = int(house_str.replace('House', ''))
            sign_data = data.get('PlanetRasiD1Sign', {})
            if isinstance(sign_data, dict):
                sign = sign_data.get('Name')
                degree = sign_data.get('DegreesIn', {}).get('DegreeMinuteSecond')
        result[planet] = {'house': house, 'sign': sign, 'degree': degree, 'raw_data': data}
    return result

def extract_house_rashis(all_house_data):
    result = {}
    for i, data in all_house_data.items():
        rasi = None
        if data and isinstance(data, dict):
            rasi_data = data.get('HouseRasiSign')
            if isinstance(rasi_data, dict):
                rasi = rasi_data.get('Name')
        result[i] = rasi
    return result

# extractors.py

def extract_planet_positions(all_planet_data):
    """Extract house positions from planet data"""
    planet_positions = {}

    print("\n=== 🔍 EXTRACTING PLANETARY POSITIONS ===")
    
    for planet_name, data in all_planet_data.items():
        if data:
            try:
                house_num = None
                sign = None
                degree = None
                
                if isinstance(data, dict):
                    # Extract house from VedAstro format: "House10" -> 10
                    house_str = data.get('HousePlanetOccupiesBasedOnSign')
                    if house_str and isinstance(house_str, str) and 'House' in house_str:
                        house_num = int(house_str.replace('House', ''))
                    elif isinstance(house_str, (int, float)):
                        house_num = int(house_str)
                    
                    # Extract zodiac sign
                    sign_data = data.get('PlanetRasiD1Sign')
                    if isinstance(sign_data, dict) and 'Name' in sign_data:
                        sign = sign_data['Name']
                        degree = sign_data.get('DegreesIn', {}).get('DegreeMinuteSecond')
                
                planet_positions[planet_name] = {
                    'house': house_num,
                    'sign': sign,
                    'degree': degree,
                    'raw_data': data
                }
                
                print(f"  {planet_name}: House {house_num}, Sign {sign}, Degree {degree}")
                
            except Exception as e:
                print(f"❌ Error extracting position for {planet_name}: {e}")
                planet_positions[planet_name] = {'house': None, 'sign': None, 'raw_data': data}
    
    return planet_positions


def extract_house_rashis(all_house_data):
    """Extract Rashi sign lords for each house"""
    house_rashis = {}

    # print("\n=== 🔍 EXTRACTING HOUSE LORDS ===")
    
    for house_num, data in all_house_data.items():
        if data:
            try:
                lord = None
                if isinstance(data, dict):
                    # Look for house rashi in VedAstro format
                    lord_data = data.get('HouseRasiSign')
                    if isinstance(lord_data, dict) and 'Name' in lord_data:
                        lord = lord_data['Name']
                    elif isinstance(lord_data, str):
                        lord = lord_data
                
                house_rashis[house_num] = lord
                # print(f"  House {house_num}: {lord}")
                
            except Exception as e:
                print(f"❌ Error extracting lord for House {house_num}: {e}")
                house_rashis[house_num] = None
    
    return house_rashis


def print_extracted_summary(planet_positions, house_rashis):
    """Print summary of extracted data"""
    print("\n=== 📊 EXTRACTED POSITIONS SUMMARY ===")

    print("\n🌌 Planet Positions:")
    for planet, data in planet_positions.items():
        house = data.get('house', 'Unknown')
        sign = data.get('sign', 'Unknown')
        print(f"{planet}: House {house}, Sign {sign}")

    print("\n🏠 House Rashis:")
    for house, lord in house_rashis.items():
        print(f"House {house}: {lord}")
