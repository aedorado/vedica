from typing import Dict, List, Set, Optional, Any, Tuple
from dataclasses import dataclass
from enum import Enum
import math

class DhanaYogaType(Enum):
    CONJUNCTION = "conjunction"
    MUTUAL_ASPECT = "mutual_aspect"
    SIGN_EXCHANGE = "sign_exchange"
    HOUSE_PLACEMENT = "house_placement"

@dataclass
class DhanaYoga:
    """Simple Dhana Yoga representation."""
    yoga_type: DhanaYogaType
    primary_planet: str
    secondary_planet: Optional[str]
    primary_house: int
    secondary_house: Optional[int]
    description: str = ""
    formation_details: str = ""
    effects: str = ""
    additional_info: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.additional_info is None:
            self.additional_info = {}
    
    def __eq__(self, other):
        """Check equality to avoid duplicates."""
        if not isinstance(other, DhanaYoga):
            return False
        return (
            self.yoga_type == other.yoga_type and
            self.primary_planet == other.primary_planet and
            self.secondary_planet == other.secondary_planet and
            self.primary_house == other.primary_house and
            self.secondary_house == other.secondary_house
        )
    
    def __hash__(self):
        """Make hashable for set operations."""
        return hash((
            self.yoga_type,
            self.primary_planet,
            self.secondary_planet,
            self.primary_house,
            self.secondary_house
        ))

class SimpleDhanaYogaDetector:
    """Simplified Dhana Yoga detector following the Raja Yoga detector pattern."""
    
    # Wealth houses according to BPHS
    WEALTH_HOUSES = {1, 2, 5, 9, 11}
    PRIMARY_WEALTH_HOUSES = {2, 11}  # Core wealth houses
    
    # Benefic planets
    BENEFIC_PLANETS = {'Jupiter', 'Venus', 'Mercury', 'Moon'}
    
    # Sign lords
    SIGN_LORDS = {
        'Aries': 'Mars', 'Taurus': 'Venus', 'Gemini': 'Mercury',
        'Cancer': 'Moon', 'Leo': 'Sun', 'Virgo': 'Mercury',
        'Libra': 'Venus', 'Scorpio': 'Mars', 'Sagittarius': 'Jupiter',
        'Capricorn': 'Saturn', 'Aquarius': 'Saturn', 'Pisces': 'Jupiter'
    }
    
    # Standard planetary aspects
    PLANETARY_ASPECTS = {
        'Sun': [7],
        'Moon': [7],
        'Mars': [4, 7, 8],
        'Mercury': [7],
        'Jupiter': [5, 7, 9],
        'Venus': [7],
        'Saturn': [3, 7, 10],
        'Rahu': [5, 7, 9],
        'Ketu': [5, 7, 9]
    }
    
    # Wealth house combinations
    WEALTH_COMBINATIONS = [
        (2, 11),  # Primary wealth axis - 2nd and 11th
        (1, 2),   # Lagna and 2nd - self and wealth
        (1, 11),  # Lagna and 11th - self and gains
        (2, 5),   # 2nd and 5th - wealth and speculation
        (2, 9),   # 2nd and 9th - wealth and fortune
        (5, 9),   # 5th and 9th - trikona wealth
        (5, 11),  # 5th and 11th - speculation and gains
        (9, 11),  # 9th and 11th - fortune and gains
        (1, 5),   # Lagna and 5th - self and merit
        (1, 9),   # Lagna and 9th - self and fortune
    ]
    
    def __init__(self, planet_data: Dict[str, 'PlanetDetails'], house_data: Dict[str, 'HouseDetail']):
        self.planet_data = planet_data
        self.house_data = house_data
        self.house_lords = self._get_house_lords()
        self.detected_yogas = set()  # To avoid duplicates
        
    def _get_house_lords(self) -> Dict[int, str]:
        """Extract house lords from house data."""
        house_lords = {}
        
        for house_key, house_detail in self.house_data.items():
            house_num = int(house_key)
            lord_name = house_detail.safe_get_nested('LordOfHouse', 'Name')
            if lord_name:
                house_lords[house_num] = lord_name
                
        return house_lords
    
    def _get_houses_ruled_by_planet(self, planet_name: str) -> List[int]:
        """Get houses ruled by a planet."""
        return [house_num for house_num, lord in self.house_lords.items() 
                if lord == planet_name]
    
    def _get_planet_house_number(self, planet_name: str) -> Optional[int]:
        """Get the house number where a planet is located."""
        planet_detail = self.planet_data.get(planet_name)
        if not planet_detail:
            return None
        
        house_str = planet_detail.safe_get('HousePlanetOccupiesBasedOnSign', '')
        if house_str.startswith('House'):
            try:
                return int(house_str.replace('House', ''))
            except ValueError:
                return None
        return None
    
    def _is_wealth_combination(self, planet1: str, planet2: str) -> Optional[Tuple[str, str, int, int]]:
        """Check if two planets form a valid wealth combination."""
        planet1_houses = self._get_houses_ruled_by_planet(planet1)
        planet2_houses = self._get_houses_ruled_by_planet(planet2)
        
        for house1 in planet1_houses:
            for house2 in planet2_houses:
                house_pair = tuple(sorted([house1, house2]))
                
                for combo in self.WEALTH_COMBINATIONS:
                    if house_pair == tuple(sorted(combo)):
                        # Prioritize 2nd and 11th house lords as primary
                        if house2 in self.PRIMARY_WEALTH_HOUSES and house1 not in self.PRIMARY_WEALTH_HOUSES:
                            return (planet2, planet1, house2, house1)
                        else:
                            return (planet1, planet2, house1, house2)
        
        return None
    
    def _are_planets_conjunct_by_house(self, planet1: str, planet2: str) -> bool:
        """Check if two planets are in the same house."""
        house1 = self._get_planet_house_number(planet1)
        house2 = self._get_planet_house_number(planet2)
        
        return house1 is not None and house2 is not None and house1 == house2
    
    def _are_planets_conjunct_by_degree(self, planet1: str, planet2: str, orb: float = 8.0) -> bool:
        """Check if two planets are conjunct by degree (within orb)."""
        planet1_detail = self.planet_data.get(planet1)
        planet2_detail = self.planet_data.get(planet2)
        
        if not planet1_detail or not planet2_detail:
            return False
        
        try:
            deg1_str = planet1_detail.safe_get_nested('PlanetRasiD1Degree', 'DegreeString', '')
            deg2_str = planet2_detail.safe_get_nested('PlanetRasiD1Degree', 'DegreeString', '')
            
            if not deg1_str or not deg2_str:
                return False
            
            deg1 = self._parse_degree_string(deg1_str)
            deg2 = self._parse_degree_string(deg2_str)
            
            if deg1 is None or deg2 is None:
                return False
            
            # Calculate difference considering 360-degree circle
            diff = abs(deg1 - deg2)
            if diff > 180:
                diff = 360 - diff
            
            return diff <= orb
            
        except Exception:
            return False
    
    def _parse_degree_string(self, degree_str: str) -> Optional[float]:
        """Parse degree string like "12° 21' 50" to decimal degrees."""
        try:
            parts = degree_str.replace('°', ' ').replace("'", ' ').replace('"', ' ').split()
            degrees = float(parts[0]) if len(parts) > 0 else 0
            minutes = float(parts[1]) if len(parts) > 1 else 0
            seconds = float(parts[2]) if len(parts) > 2 else 0
            
            return degrees + minutes/60 + seconds/3600
        except:
            return None
    
    def _calculate_house_distance(self, house1: int, house2: int) -> int:
        """Calculate the distance between two houses."""
        return ((house2 - house1) % 12) + 1 if house1 != house2 else 1
    
    def _do_planets_aspect_each_other(self, planet1: str, planet2: str) -> bool:
        """Check if two planets aspect each other based on their positions."""
        house1 = self._get_planet_house_number(planet1)
        house2 = self._get_planet_house_number(planet2)
        
        if house1 is None or house2 is None or house1 == house2:
            return False
        
        # Check if planet1 aspects planet2
        aspects1 = self.PLANETARY_ASPECTS.get(planet1, [7])
        distance1_to_2 = self._calculate_house_distance(house1, house2)
        planet1_aspects_planet2 = distance1_to_2 in aspects1
        
        # Check if planet2 aspects planet1
        aspects2 = self.PLANETARY_ASPECTS.get(planet2, [7])
        distance2_to_1 = self._calculate_house_distance(house2, house1)
        planet2_aspects_planet1 = distance2_to_1 in aspects2
        
        return planet1_aspects_planet2 and planet2_aspects_planet1
    
    def _are_planets_in_exchange(self, planet1: str, planet2: str) -> bool:
        """Check if two planets are in sign exchange."""
        planet1_detail = self.planet_data[planet1]
        planet2_detail = self.planet_data[planet2]
        
        planet1_sign = planet1_detail.safe_get_nested('PlanetRasiD1Sign', 'Name')
        planet2_sign = planet2_detail.safe_get_nested('PlanetRasiD1Sign', 'Name')
        
        if not planet1_sign or not planet2_sign:
            return False
        
        # Check if planet1 is in planet2's sign and vice versa
        planet1_lord = self.SIGN_LORDS.get(planet1_sign)
        planet2_lord = self.SIGN_LORDS.get(planet2_sign)
        
        return planet1_lord == planet2 and planet2_lord == planet1
    
    def detect_conjunction_yogas(self) -> List[DhanaYoga]:
        """Detect Dhana Yogas formed by conjunction."""
        yogas = []
        planets = list(self.planet_data.keys())
        
        for i, planet1 in enumerate(planets):
            for planet2 in planets[i+1:]:
                # Skip shadow planets for basic conjunction check
                if planet1 in ['Rahu', 'Ketu'] or planet2 in ['Rahu', 'Ketu']:
                    continue
                
                # Check conjunction by house or by degree
                is_conjunct = (self._are_planets_conjunct_by_house(planet1, planet2) or 
                             self._are_planets_conjunct_by_degree(planet1, planet2))
                
                if is_conjunct:
                    wealth_combo = self._is_wealth_combination(planet1, planet2)
                    if wealth_combo:
                        primary_planet, secondary_planet, primary_house, secondary_house = wealth_combo
                        
                        conjunction_house = self._get_planet_house_number(planet1)
                        conjunction_sign = self.planet_data[planet1].safe_get_nested('PlanetRasiD1Sign', 'Name')
                        
                        yoga = DhanaYoga(
                            yoga_type=DhanaYogaType.CONJUNCTION,
                            primary_planet=primary_planet,
                            secondary_planet=secondary_planet,
                            primary_house=primary_house,
                            secondary_house=secondary_house,
                            formation_details=f"{primary_planet} (lord of {primary_house}th) conjunct {secondary_planet} (lord of {secondary_house}th)",
                            effects=self._get_wealth_effects(primary_house, secondary_house),
                            additional_info={
                                'conjunction_house': conjunction_house,
                                'conjunction_sign': conjunction_sign,
                                'planet1': planet1,
                                'planet2': planet2
                            }
                        )
                        yoga.description = self._generate_description(yoga)
                        
                        if yoga not in self.detected_yogas:
                            yogas.append(yoga)
                            self.detected_yogas.add(yoga)
        
        return yogas
    
    def detect_aspect_yogas(self) -> List[DhanaYoga]:
        """Detect Dhana Yogas formed by mutual aspects."""
        yogas = []
        planets = list(self.planet_data.keys())
        
        for i, planet1 in enumerate(planets):
            for planet2 in planets[i+1:]:
                # Skip shadow planets for basic aspect check
                if planet1 in ['Rahu', 'Ketu'] or planet2 in ['Rahu', 'Ketu']:
                    continue
                
                if self._do_planets_aspect_each_other(planet1, planet2):
                    wealth_combo = self._is_wealth_combination(planet1, planet2)
                    if wealth_combo:
                        primary_planet, secondary_planet, primary_house, secondary_house = wealth_combo
                        
                        house1 = self._get_planet_house_number(planet1)
                        house2 = self._get_planet_house_number(planet2)
                        
                        yoga = DhanaYoga(
                            yoga_type=DhanaYogaType.MUTUAL_ASPECT,
                            primary_planet=primary_planet,
                            secondary_planet=secondary_planet,
                            primary_house=primary_house,
                            secondary_house=secondary_house,
                            formation_details=f"{primary_planet} (lord of {primary_house}th) in mutual aspect with {secondary_planet} (lord of {secondary_house}th)",
                            effects=self._get_wealth_effects(primary_house, secondary_house),
                            additional_info={
                                'planet1': planet1,
                                'planet2': planet2,
                                'planet1_house': house1,
                                'planet2_house': house2
                            }
                        )
                        yoga.description = self._generate_description(yoga)
                        
                        if yoga not in self.detected_yogas:
                            yogas.append(yoga)
                            self.detected_yogas.add(yoga)
        
        return yogas
    
    def detect_exchange_yogas(self) -> List[DhanaYoga]:
        """Detect Dhana Yogas formed by sign exchange."""
        yogas = []
        planets = list(self.planet_data.keys())
        
        for i, planet1 in enumerate(planets):
            for planet2 in planets[i+1:]:
                # Skip shadow planets
                if planet1 in ['Rahu', 'Ketu'] or planet2 in ['Rahu', 'Ketu']:
                    continue
                    
                if self._are_planets_in_exchange(planet1, planet2):
                    wealth_combo = self._is_wealth_combination(planet1, planet2)
                    if wealth_combo:
                        primary_planet, secondary_planet, primary_house, secondary_house = wealth_combo
                        
                        planet1_sign = self.planet_data[planet1].safe_get_nested('PlanetRasiD1Sign', 'Name')
                        planet2_sign = self.planet_data[planet2].safe_get_nested('PlanetRasiD1Sign', 'Name')
                        
                        yoga = DhanaYoga(
                            yoga_type=DhanaYogaType.SIGN_EXCHANGE,
                            primary_planet=primary_planet,
                            secondary_planet=secondary_planet,
                            primary_house=primary_house,
                            secondary_house=secondary_house,
                            formation_details=f"{primary_planet} (lord of {primary_house}th) and {secondary_planet} (lord of {secondary_house}th) in sign exchange",
                            effects=self._get_wealth_effects(primary_house, secondary_house),
                            additional_info={
                                'planet1': planet1,
                                'planet2': planet2,
                                'planet1_sign': planet1_sign,
                                'planet2_sign': planet2_sign
                            }
                        )
                        yoga.description = self._generate_description(yoga)
                        
                        if yoga not in self.detected_yogas:
                            yogas.append(yoga)
                            self.detected_yogas.add(yoga)
        
        return yogas
    
    def detect_placement_yogas(self) -> List[DhanaYoga]:
        """Detect Dhana Yogas formed by wealth house lords in beneficial placements."""
        yogas = []
        
        # Check each planet's lordship and placement
        for planet_name, planet_detail in self.planet_data.items():
            if planet_name in ['Rahu', 'Ketu']:
                continue
                
            # Get houses ruled by this planet
            ruled_houses = self._get_houses_ruled_by_planet(planet_name)
            
            # Get the house where this planet is placed
            placement_house = self._get_planet_house_number(planet_name)
            
            if placement_house is None:
                continue
            
            # Check if this planet rules any wealth houses
            wealth_houses_ruled = [h for h in ruled_houses if h in self.WEALTH_HOUSES]
            
            for ruled_house in wealth_houses_ruled:
                # Skip if planet is in its own house
                if ruled_house == placement_house:
                    continue
                
                # Check if placement creates a wealth combination
                if self._is_valid_wealth_placement(ruled_house, placement_house):
                    placement_lord = self.house_lords.get(placement_house, "")
                    
                    yoga = DhanaYoga(
                        yoga_type=DhanaYogaType.HOUSE_PLACEMENT,
                        primary_planet=planet_name,
                        secondary_planet=placement_lord,
                        primary_house=ruled_house,
                        secondary_house=placement_house,
                        formation_details=f"{planet_name} (lord of {ruled_house}th) placed in {placement_house}th house",
                        effects=self._get_placement_effects(ruled_house, placement_house),
                        additional_info={
                            'placement_lord': placement_lord,
                            'ruled_houses': ruled_houses
                        }
                    )
                    yoga.description = self._generate_description(yoga)
                    
                    if yoga not in self.detected_yogas:
                        yogas.append(yoga)
                        self.detected_yogas.add(yoga)
        
        return yogas
    
    def detect_benefic_wealth_yogas(self) -> List[DhanaYoga]:
        """Detect simple benefic placement yogas in 2nd or 11th house."""
        yogas = []
        
        for planet_name in self.BENEFIC_PLANETS:
            if planet_name not in self.planet_data:
                continue
                
            placement_house = self._get_planet_house_number(planet_name)
            
            if placement_house in self.PRIMARY_WEALTH_HOUSES:
                yoga = DhanaYoga(
                    yoga_type=DhanaYogaType.HOUSE_PLACEMENT,
                    primary_planet=planet_name,
                    secondary_planet=None,
                    primary_house=placement_house,
                    secondary_house=None,
                    formation_details=f"{planet_name} (benefic) placed in {placement_house}th house",
                    effects=f"Natural benefic in {placement_house}th house enhances wealth potential",
                    additional_info={
                        'benefic_type': 'natural',
                        'wealth_house': placement_house
                    }
                )
                yoga.description = f"Benefic {planet_name} in {placement_house}th house"
                
                if yoga not in self.detected_yogas:
                    yogas.append(yoga)
                    self.detected_yogas.add(yoga)
        
        return yogas
    
    def _is_valid_wealth_placement(self, ruled_house: int, placement_house: int) -> bool:
        """Check if the ruled house and placement house form a valid wealth combination."""
        house_pair = tuple(sorted([ruled_house, placement_house]))
        
        for combo in self.WEALTH_COMBINATIONS:
            if house_pair == tuple(sorted(combo)):
                return True
        
        return False
    
    def _get_wealth_effects(self, house1: int, house2: int) -> str:
        """Get effects of wealth house combinations."""
        effects_map = {
            (2, 11): "Excellent for wealth accumulation and steady income",
            (1, 2): "Strong earning capacity and family wealth",
            (1, 11): "Achievement of desires and substantial gains",
            (2, 5): "Wealth through speculation, investments, and intelligence",
            (2, 9): "Fortune and luck in wealth matters, ancestral wealth",
            (5, 9): "Wealth through merit, wisdom, and divine grace",
            (5, 11): "Gains through speculation, creativity, and children",
            (9, 11): "Income through fortune, teaching, and dharmic activities",
            (1, 5): "Personal merit creates wealth opportunities",
            (1, 9): "Personal fortune and luck in financial matters"
        }
        
        key = tuple(sorted([house1, house2]))
        return effects_map.get(key, "Favorable for wealth and prosperity")
    
    def _get_placement_effects(self, ruled_house: int, placement_house: int) -> str:
        """Get effects of specific house placements."""
        house_effects = {
            1: "Personal magnetism and ability to earn",
            2: "Strengthens wealth accumulation directly",
            5: "Gains through speculation and intelligence", 
            9: "Fortune and luck in wealth matters",
            11: "Excellent for income and gains"
        }
        
        base_effect = house_effects.get(placement_house, "favorable placement")
        return f"Lord of {ruled_house}th in {placement_house}th: {base_effect}"
    
    def _generate_description(self, yoga: DhanaYoga) -> str:
        """Generate human-readable description."""
        type_names = {
            DhanaYogaType.CONJUNCTION: "conjunction",
            DhanaYogaType.MUTUAL_ASPECT: "mutual aspect", 
            DhanaYogaType.SIGN_EXCHANGE: "sign exchange",
            DhanaYogaType.HOUSE_PLACEMENT: "placement"
        }
        
        if yoga.secondary_planet:
            return (f"Dhana Yoga: {yoga.primary_planet} (lord of {yoga.primary_house}th) "
                    f"in {type_names[yoga.yoga_type]} with {yoga.secondary_planet} "
                    f"(lord of {yoga.secondary_house}th)")
        else:
            return (f"Dhana Yoga: {yoga.primary_planet} in {yoga.primary_house}th house")
    
    def detect_all_dhana_yogas(self) -> List[DhanaYoga]:
        """Detect all types of Dhana Yogas."""
        # Reset detected yogas to avoid cross-method duplicates
        self.detected_yogas.clear()
        
        all_yogas = []
        all_yogas.extend(self.detect_conjunction_yogas())
        all_yogas.extend(self.detect_aspect_yogas())
        all_yogas.extend(self.detect_exchange_yogas())
        all_yogas.extend(self.detect_placement_yogas())
        all_yogas.extend(self.detect_benefic_wealth_yogas())
        
        return all_yogas
    
    def print_yoga_summary(self, yogas: List[DhanaYoga] = None) -> None:
        """Print detailed summary of all detected yogas."""
        if yogas is None:
            yogas = self.detect_all_dhana_yogas()
        
        print("=" * 80)
        print("DHANA YOGA DETECTION SUMMARY")
        print("=" * 80)
        print(f"Total Dhana Yogas Detected: {len(yogas)}")
        print()
        
        if not yogas:
            print("No Dhana Yogas detected in this chart.")
            return
        
        # Group by type
        yoga_by_type = {
            DhanaYogaType.CONJUNCTION: [],
            DhanaYogaType.MUTUAL_ASPECT: [],
            DhanaYogaType.SIGN_EXCHANGE: [],
            DhanaYogaType.HOUSE_PLACEMENT: []
        }
        
        for yoga in yogas:
            yoga_by_type[yoga.yoga_type].append(yoga)
        
        # Print by category
        type_headers = {
            DhanaYogaType.CONJUNCTION: "CONJUNCTION DHANA YOGAS",
            DhanaYogaType.MUTUAL_ASPECT: "MUTUAL ASPECT DHANA YOGAS",
            DhanaYogaType.SIGN_EXCHANGE: "SIGN EXCHANGE DHANA YOGAS",
            DhanaYogaType.HOUSE_PLACEMENT: "PLACEMENT DHANA YOGAS"
        }
        
        for yoga_type, header in type_headers.items():
            type_yogas = yoga_by_type[yoga_type]
            if type_yogas:
                print(f"\n{header} ({len(type_yogas)} found)")
                print("-" * len(header))
                
                for i, yoga in enumerate(type_yogas, 1):
                    print(f"\n{i}. {yoga.description}")
                    print(f"   Formation: {yoga.formation_details}")
                    print(f"   Effects: {yoga.effects}")
                    
                    # Print additional details based on type
                    if yoga_type == DhanaYogaType.CONJUNCTION:
                        print(f"   Conjunction Location: House {yoga.additional_info.get('conjunction_house')} "
                              f"in {yoga.additional_info.get('conjunction_sign')}")
                    
                    elif yoga_type == DhanaYogaType.MUTUAL_ASPECT:
                        print(f"   Aspecting Houses: {yoga.additional_info.get('planet1_house')} "
                              f"and {yoga.additional_info.get('planet2_house')}")
                    
                    elif yoga_type == DhanaYogaType.SIGN_EXCHANGE:
                        print(f"   Exchange: {yoga.additional_info.get('planet1_sign')} ↔ "
                              f"{yoga.additional_info.get('planet2_sign')}")
                    
                    elif yoga_type == DhanaYogaType.HOUSE_PLACEMENT:
                        if yoga.secondary_planet:
                            print(f"   Placement: {yoga.primary_house}th lord in {yoga.secondary_house}th house")
                        else:
                            print(f"   Benefic Placement: {yoga.primary_house}th house")
        
        print("\n" + "=" * 80)

# Usage example:
# detector = SimpleDhanaYogaDetector(planet_data_objs, house_data_objs)
# dhana_yogas = detector.detect_all_dhana_yogas()
# detector.print_yoga_summary(dhana_yogas)