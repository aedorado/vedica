from typing import Dict, Any, Callable
from tabulate import tabulate


class AstroTableGenerator:
    def __init__(self, planet_data: Dict[str, Any], house_data: Dict[str, Any] = None):
        self.planet_data = planet_data
        self.house_data = house_data or {}

        self.STANDARD_SHADBALA_REQUIREMENT = {
            "Sun": 6.0,
            "Moon": 6.0,
            "Mars": 5.0,
            "Mercury": 7.0,
            "Jupiter": 6.5,
            "Venus": 5.5,
            "Saturn": 5.0,
        }

        # Define column extractors for planets
        self.planet_columns = {
            "Planet": lambda name, data: name,
            "Sign": lambda name, data: self._safe_get_nested(data, 'PlanetRasiD1Sign', 'Name'),
            "Degree": lambda name, data: self._safe_get_nested(data, 'PlanetRasiD1Sign', 'DegreesIn', 'DegreeMinuteSecond'),
            "House": lambda name, data: self._safe_get(data, 'HousePlanetOccupiesBasedOnSign'),
            "Lord": lambda name, data: self._safe_get_nested(data, 'PlanetLordOfZodiacSign', 'Name'),
            "Nakshatra": lambda name, data: self._safe_get(data, 'PlanetConstellation'),
            "Retro": lambda name, data: "Yes" if self._safe_get(data, 'IsPlanetRetrograde') == 'True' else "No",
            "Exalted": lambda name, data: "Yes" if self._safe_get(data, 'IsPlanetExaltedSign') == 'True' else "No",
            "BenficToLagna": lambda name, data: "Yes" if self._safe_get(data, 'IsPlanetBeneficToLagna') == 'True' else "No",
            "Aspects Received": lambda name, data: ", ".join(self._safe_get(data, 'PlanetsAspectingPlanet')) if self._safe_get(data, 'PlanetsAspectingPlanet') else "-",
            "Avasta": lambda name, data: self._safe_get(data, 'PlanetAvasta'),
            "Shadbala Ratio": lambda name, data: self._calculate_shadbala_ratio(name, self._safe_get(data, 'PlanetShadbalaPinda')),
        }

        # Define column extractors for houses  
        self.house_columns = {
            "House": lambda house_num, house_data: f"House {house_num}",
            "Sign": lambda house_num, house_data: self._safe_get_nested(house_data, 'HouseRasiSign', 'Name'),
            "Degree": lambda house_num, house_data: self._safe_get_nested(house_data, 'HouseRasiSign', 'DegreesIn', 'DegreeMinuteSecond'),
            "Nakshatra": lambda house_num, house_data: self._safe_get(house_data, 'HouseConstellation'),
            "Lord": lambda house_num, house_data: self._safe_get_nested(house_data, 'LordOfHouse', 'Name'),
            "Planets": lambda house_num, house_data: ", ".join(self._safe_get(house_data, 'PlanetsInHouseBasedOnSign', [])),
            "Aspects Received": lambda name, data: ", ".join(self._safe_get(data, 'PlanetsAspectingHouse')) if self._safe_get(data, 'PlanetsAspectingHouse') else "-",
        }

    def _calculate_shadbala_ratio(self, planet_name, rupa_val):
        try:
            if not rupa_val:
                return "-"
            actual = float(rupa_val)
            required = self.STANDARD_SHADBALA_REQUIREMENT.get(planet_name)
            if required:
                ratio = actual / 60 / required
                return f"{ratio:.2f}"
        except Exception as e:
            return "-"


    def _safe_get(self, data, key, default=''):
        """Safely get value from dict or dataclass object"""
        if hasattr(data, key):  # dataclass object
            return getattr(data, key, default)
        elif isinstance(data, dict):  # dictionary
            return data.get(key, default)
        else:
            return default
    
    def _safe_get_nested(self, data, *keys):
        """Safely get nested value from dict or dataclass objects"""
        current = data
        for key in keys:
            if current is None:
                return ''
            if hasattr(current, key):  # dataclass object
                current = getattr(current, key)
            elif isinstance(current, dict):  # dictionary
                current = current.get(key)
            else:
                return ''
        return str(current) if current is not None else ''

    def debug_data_structure(self):
        """Debug helper to see actual data structure"""
        print("=== DEBUGGING DATA STRUCTURE ===")
        
        # Debug planets
        for planet_name, planet_data in list(self.planet_data.items())[:1]:  # Just check first planet
            print(f"\nPlanet: {planet_name}")
            print(f"Type: {type(planet_data)}")
            if isinstance(planet_data, dict):
                print("Available keys:")
                for key in sorted(planet_data.keys())[:20]:  # Show first 20 keys
                    value = planet_data[key]
                    print(f"  {key}: {type(value)}")
                    if isinstance(value, dict) and 'Name' in value:
                        print(f"    -> Name: {value.get('Name')}")
            break
            
        # Debug houses
        if self.house_data:
            for house_num, house_data in list(self.house_data.items())[:1]:  # Just check first house
                print(f"\nHouse: {house_num}")
                print(f"Type: {type(house_data)}")
                if isinstance(house_data, dict):
                    print("Available keys:")
                    for key in sorted(house_data.keys())[:10]:  # Show first 10 keys
                        value = house_data[key]
                        print(f"  {key}: {type(value)}")
                        if isinstance(value, dict) and 'Name' in value:
                            print(f"    -> Name: {value.get('Name')}")
                break

    def generate_table(self, data: Dict, column_map: Dict[str, Callable], title: str):
        if not data:
            print(f"\n{title}: No data available")
            return
            
        rows = []
        for key, planet_details in data.items():
            try:
                row = []
                for col_name, extractor in column_map.items():
                    try:
                        value = extractor(key, planet_details)
                        row.append(str(value) if value is not None else "")
                    except Exception as e:
                        print(f"Error in column '{col_name}' for {key}: {e}")
                        row.append("ERROR")
                rows.append(row)
            except Exception as e:
                print(f"Error processing {key}: {e}")
                continue

        if rows:
            print(f"\n{'='*len(title)}\n{title}\n{'='*len(title)}")
            print(tabulate(rows, headers=column_map.keys(), tablefmt="fancy_grid"))

    def print_planet_table(self):
        self.generate_table(self.planet_data, self.planet_columns, title="Planet Details")

    def print_house_table(self):
        self.generate_table(self.house_data, self.house_columns, title="House Details")

    def print_all(self):
        # self.debug_data_structure()  # Add debugging
        self.print_planet_table()
        if self.house_data:
            self.print_house_table()


# Usage example:
# generator = AstroTableGenerator(planet_data, house_data)
# generator.print_all()