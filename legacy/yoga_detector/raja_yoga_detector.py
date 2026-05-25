from typing import Dict, List, Set, Optional, Any, Tuple
from dataclasses import dataclass
from enum import Enum
import math

class YogaType(Enum):
    CONJUNCTION = "conjunction"
    MUTUAL_ASPECT = "mutual_aspect"
    SIGN_EXCHANGE = "sign_exchange"

@dataclass
class RajaYoga:
    """Simple Raja Yoga representation."""
    yoga_type: YogaType
    kendra_lord: str
    trikona_lord: str
    kendra_house: int
    trikona_house: int
    description: str = ""
    strength_score: float = 0.0
    additional_info: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.additional_info is None:
            self.additional_info = {}
    
    def __eq__(self, other):
        """Check equality to avoid duplicates."""
        if not isinstance(other, RajaYoga):
            return False
        return (
            self.yoga_type == other.yoga_type and
            self.kendra_lord == other.kendra_lord and
            self.trikona_lord == other.trikona_lord and
            self.kendra_house == other.kendra_house and
            self.trikona_house == other.trikona_house
        )
    
    def __hash__(self):
        """Make hashable for set operations."""
        return hash((
            self.yoga_type,
            self.kendra_lord,
            self.trikona_lord,
            self.kendra_house,
            self.trikona_house
        ))

class SimpleRajaYogaDetector:
    """Enhanced Raja Yoga detector with better conjunction and aspect detection."""
    
    # Constants
    KENDRA_HOUSES = {1, 4, 7, 10}
    TRIKONA_HOUSES = {1, 5, 9}
    
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
    
    def _is_kendra_trikona_combination(self, planet1: str, planet2: str) -> Optional[tuple]:
        """Check if two planets form a valid Kendra-Trikona combination."""
        planet1_houses = self._get_houses_ruled_by_planet(planet1)
        planet2_houses = self._get_houses_ruled_by_planet(planet2)
        
        for house1 in planet1_houses:
            for house2 in planet2_houses:
                # Check if one is Kendra and other is Trikona
                if house1 in self.KENDRA_HOUSES and house2 in self.TRIKONA_HOUSES:
                    return (planet1, planet2, house1, house2)
                elif house2 in self.KENDRA_HOUSES and house1 in self.TRIKONA_HOUSES:
                    return (planet2, planet1, house2, house1)
        
        return None
    
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
    
    def _are_planets_conjunct_by_house(self, planet1: str, planet2: str) -> bool:
        """Check if two planets are in the same house (conjunction by house)."""
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
            # Get degrees - assuming format like "12° 21' 50"
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
        aspects1 = self.PLANETARY_ASPECTS.get(planet1, [7])  # Default to 7th aspect
        distance1_to_2 = self._calculate_house_distance(house1, house2)
        planet1_aspects_planet2 = distance1_to_2 in aspects1
        
        # Check if planet2 aspects planet1
        aspects2 = self.PLANETARY_ASPECTS.get(planet2, [7])  # Default to 7th aspect
        distance2_to_1 = self._calculate_house_distance(house2, house1)
        planet2_aspects_planet1 = distance2_to_1 in aspects2
        
        return planet1_aspects_planet2 and planet2_aspects_planet1
    
    def detect_conjunction_yogas(self) -> List[RajaYoga]:
        """Detect Raja Yogas formed by conjunction - enhanced version."""
        yogas = []
        planets = list(self.planet_data.keys())
        
        # Check all planet pairs for conjunction
        for i, planet1 in enumerate(planets):
            for planet2 in planets[i+1:]:
                # Skip shadow planets for basic conjunction check
                if planet1 in ['Rahu', 'Ketu'] or planet2 in ['Rahu', 'Ketu']:
                    continue
                
                # Check conjunction by house or by degree
                is_conjunct = (self._are_planets_conjunct_by_house(planet1, planet2) or 
                             self._are_planets_conjunct_by_degree(planet1, planet2))
                
                if is_conjunct:
                    kendra_trikona = self._is_kendra_trikona_combination(planet1, planet2)
                    if kendra_trikona:
                        kendra_lord, trikona_lord, kendra_house, trikona_house = kendra_trikona
                        
                        # Get conjunction details
                        conjunction_house = self._get_planet_house_number(planet1)
                        planet1_sign = self.planet_data[planet1].safe_get_nested('PlanetRasiD1Sign', 'Name')
                        planet2_sign = self.planet_data[planet2].safe_get_nested('PlanetRasiD1Sign', 'Name')
                        
                        yoga = RajaYoga(
                            yoga_type=YogaType.CONJUNCTION,
                            kendra_lord=kendra_lord,
                            trikona_lord=trikona_lord,
                            kendra_house=kendra_house,
                            trikona_house=trikona_house,
                            additional_info={
                                'conjunction_house': conjunction_house,
                                'conjunction_sign': planet1_sign,
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
    
    def detect_aspect_yogas(self) -> List[RajaYoga]:
        """Detect Raja Yogas formed by mutual aspects - enhanced version."""
        yogas = []
        planets = list(self.planet_data.keys())
        
        # Check all planet pairs for mutual aspect
        for i, planet1 in enumerate(planets):
            for planet2 in planets[i+1:]:
                # Skip shadow planets for basic aspect check
                if planet1 in ['Rahu', 'Ketu'] or planet2 in ['Rahu', 'Ketu']:
                    continue
                
                if self._do_planets_aspect_each_other(planet1, planet2):
                    kendra_trikona = self._is_kendra_trikona_combination(planet1, planet2)
                    if kendra_trikona:
                        kendra_lord, trikona_lord, kendra_house, trikona_house = kendra_trikona
                        
                        house1 = self._get_planet_house_number(planet1)
                        house2 = self._get_planet_house_number(planet2)
                        
                        yoga = RajaYoga(
                            yoga_type=YogaType.MUTUAL_ASPECT,
                            kendra_lord=kendra_lord,
                            trikona_lord=trikona_lord,
                            kendra_house=kendra_house,
                            trikona_house=trikona_house,
                            additional_info={
                                'aspect_type': 'mutual',
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
    
    def detect_exchange_yogas(self) -> List[RajaYoga]:
        """Detect Raja Yogas formed by sign exchange (Parivartana)."""
        yogas = []
        planets = list(self.planet_data.keys())
        
        for i, planet1 in enumerate(planets):
            for planet2 in planets[i+1:]:
                # Skip shadow planets
                if planet1 in ['Rahu', 'Ketu'] or planet2 in ['Rahu', 'Ketu']:
                    continue
                    
                if self._are_planets_in_exchange(planet1, planet2):
                    kendra_trikona = self._is_kendra_trikona_combination(planet1, planet2)
                    if kendra_trikona:
                        kendra_lord, trikona_lord, kendra_house, trikona_house = kendra_trikona
                        
                        planet1_sign = self.planet_data[planet1].safe_get_nested('PlanetRasiD1Sign', 'Name')
                        planet2_sign = self.planet_data[planet2].safe_get_nested('PlanetRasiD1Sign', 'Name')
                        
                        yoga = RajaYoga(
                            yoga_type=YogaType.SIGN_EXCHANGE,
                            kendra_lord=kendra_lord,
                            trikona_lord=trikona_lord,
                            kendra_house=kendra_house,
                            trikona_house=trikona_house,
                            additional_info={
                                'exchange_type': 'parivartana',
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
    
    def _generate_description(self, yoga: RajaYoga) -> str:
        """Generate human-readable description."""
        type_names = {
            YogaType.CONJUNCTION: "conjunction",
            YogaType.MUTUAL_ASPECT: "mutual aspect", 
            YogaType.SIGN_EXCHANGE: "sign exchange"
        }
        
        return (f"Raja Yoga: {yoga.kendra_lord} (lord of {yoga.kendra_house}th house) "
                f"in {type_names[yoga.yoga_type]} with {yoga.trikona_lord} "
                f"(lord of {yoga.trikona_house}th house)")
    
    def detect_all_raja_yogas(self) -> List[RajaYoga]:
        """Detect all types of Raja Yogas."""
        # Reset detected yogas to avoid cross-method duplicates
        self.detected_yogas.clear()
        
        all_yogas = []
        all_yogas.extend(self.detect_conjunction_yogas())
        all_yogas.extend(self.detect_aspect_yogas())
        all_yogas.extend(self.detect_exchange_yogas())
        
        return all_yogas
    
    def print_yoga_summary(self, yogas: List[RajaYoga] = None) -> None:
        """Print detailed summary of all detected yogas."""
        if yogas is None:
            yogas = self.detect_all_raja_yogas()
        
        print("=" * 80)
        print("RAJA YOGA DETECTION SUMMARY")
        print("=" * 80)
        print(f"Total Raja Yogas Detected: {len(yogas)}")
        print()
        
        if not yogas:
            print("No Raja Yogas detected in this chart.")
            return
        
        # Group by type
        yoga_by_type = {
            YogaType.CONJUNCTION: [],
            YogaType.MUTUAL_ASPECT: [],
            YogaType.SIGN_EXCHANGE: []
        }
        
        for yoga in yogas:
            yoga_by_type[yoga.yoga_type].append(yoga)
        
        # Print by category
        type_headers = {
            YogaType.CONJUNCTION: "CONJUNCTION RAJA YOGAS",
            YogaType.MUTUAL_ASPECT: "MUTUAL ASPECT RAJA YOGAS",
            YogaType.SIGN_EXCHANGE: "SIGN EXCHANGE RAJA YOGAS"
        }
        
        for yoga_type, header in type_headers.items():
            type_yogas = yoga_by_type[yoga_type]
            if type_yogas:
                print(f"\n{header} ({len(type_yogas)} found)")
                print("-" * len(header))
                
                for i, yoga in enumerate(type_yogas, 1):
                    print(f"\n{i}. {yoga.description}")
                    
                    # Print additional details based on type
                    if yoga_type == YogaType.CONJUNCTION:
                        print(f"   Conjunction Location: House {yoga.additional_info.get('conjunction_house')} "
                              f"in {yoga.additional_info.get('conjunction_sign')}")
                        print(f"   Planets: {yoga.additional_info.get('planet1')} & "
                              f"{yoga.additional_info.get('planet2')}")
                    
                    elif yoga_type == YogaType.MUTUAL_ASPECT:
                        print(f"   Aspecting Planets: {yoga.additional_info.get('planet1')} "
                              f"(House {yoga.additional_info.get('planet1_house')}) & "
                              f"{yoga.additional_info.get('planet2')} "
                              f"(House {yoga.additional_info.get('planet2_house')})")
                    
                    elif yoga_type == YogaType.SIGN_EXCHANGE:
                        print(f"   Exchange: {yoga.additional_info.get('planet1')} in "
                              f"{yoga.additional_info.get('planet1_sign')} ↔ "
                              f"{yoga.additional_info.get('planet2')} in "
                              f"{yoga.additional_info.get('planet2_sign')}")
        
        print("\n" + "=" * 80)

# Usage example:
# detector = SimpleRajaYogaDetector(planet_data_objs, house_data_objs)
# raja_yogas = detector.detect_all_raja_yogas()
# detector.print_yoga_summary(raja_yogas)