from typing import Dict, List, Set, Optional, Any, Tuple
from dataclasses import dataclass
from enum import Enum

class NeechBhangaType(Enum):
    EXALTED_LORD_IN_KENDRA = "exalted_lord_in_kendra"
    DEBILITATED_LORD_IN_KENDRA = "debilitated_lord_in_kendra"
    DISPOSITOR_IN_KENDRA_TRIKONA = "dispositor_in_kendra_trikona"
    MUTUAL_ASPECT_WITH_EXALTED = "mutual_aspect_with_exalted"
    CONJUNCTION_WITH_EXALTED = "conjunction_with_exalted"
    ASPECT_FROM_OWN_LORD = "aspect_from_own_lord"
    CONJUNCTION_WITH_OWN_LORD = "conjunction_with_own_lord"

@dataclass
class NeechBhangaYoga:
    """
    BPHS Reference: Chapter 41 - Neecha Bhanga Raja Yoga
    
    BPHS states several conditions for Neecha Bhanga:
    1. Lord of the sign of debilitation is in a Kendra from Lagna or Moon
    2. Lord of exaltation sign is in a Kendra from Lagna or Moon  
    3. Planet debilitated is aspected by or conjoined with its own lord
    4. Planet debilitated is aspected by or conjoined with lord of exaltation sign
    5. Debilitated planet is in a Kendra or Trikona from Lagna
    """
    yoga_type: NeechBhangaType
    debilitated_planet: str
    debilitated_house: int
    debilitated_sign: str
    cancelling_planet: str
    cancelling_factor: str
    description: str = ""
    strength_score: float = 0.0
    additional_info: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.additional_info is None:
            self.additional_info = {}

class NeechBhangaYogaDetector:
    """
    Enhanced Neecha Bhanga Yoga detector following BPHS principles.
    
    BPHS states that when a planet is debilitated, the native may face challenges,
    but if Neecha Bhanga occurs, it not only cancels the bad effects but can give
    Raja Yoga results, especially if the debilitated planet is a functional benefic.
    """
    
    # Debilitation signs as per BPHS
    DEBILITATION_SIGNS = {
        'Sun': 'Libra',
        'Moon': 'Scorpio', 
        'Mars': 'Cancer',
        'Mercury': 'Pisces',
        'Jupiter': 'Capricorn',
        'Venus': 'Virgo',
        'Saturn': 'Aries'
    }
    
    # Exaltation signs as per BPHS
    EXALTATION_SIGNS = {
        'Sun': 'Aries',
        'Moon': 'Taurus',
        'Mars': 'Capricorn', 
        'Mercury': 'Virgo',
        'Jupiter': 'Cancer',
        'Venus': 'Pisces',
        'Saturn': 'Libra'
    }
    
    # Sign lords as per BPHS
    SIGN_LORDS = {
        'Aries': 'Mars', 'Taurus': 'Venus', 'Gemini': 'Mercury',
        'Cancer': 'Moon', 'Leo': 'Sun', 'Virgo': 'Mercury',
        'Libra': 'Venus', 'Scorpio': 'Mars', 'Sagittarius': 'Jupiter',
        'Capricorn': 'Saturn', 'Aquarius': 'Saturn', 'Pisces': 'Jupiter'
    }
    
    KENDRA_HOUSES = {1, 4, 7, 10}
    TRIKONA_HOUSES = {1, 5, 9}
    
    # Planetary aspects as per BPHS
    PLANETARY_ASPECTS = {
        'Sun': [7], 'Moon': [7], 'Mercury': [7], 'Venus': [7],
        'Mars': [4, 7, 8], 'Jupiter': [5, 7, 9], 'Saturn': [3, 7, 10],
        'Rahu': [5, 7, 9], 'Ketu': [5, 7, 9]
    }
    
    def __init__(self, planet_data: Dict[str, 'PlanetDetails'], house_data: Dict[str, 'HouseDetail']):
        self.planet_data = planet_data
        self.house_data = house_data
        self.detected_yogas = set()
        
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
    
    def _get_planet_sign(self, planet_name: str) -> Optional[str]:
        """Get the sign a planet is placed in."""
        planet_detail = self.planet_data.get(planet_name)
        if not planet_detail:
            return None
        return planet_detail.safe_get_nested('PlanetRasiD1Sign', 'Name')
    
    def _is_planet_debilitated(self, planet_name: str) -> bool:
        """Check if a planet is in its debilitation sign as per BPHS."""
        if planet_name not in self.DEBILITATION_SIGNS:
            return False
        
        planet_sign = self._get_planet_sign(planet_name)
        return planet_sign == self.DEBILITATION_SIGNS[planet_name]
    
    def _is_planet_exalted(self, planet_name: str) -> bool:
        """Check if a planet is in its exaltation sign as per BPHS."""
        if planet_name not in self.EXALTATION_SIGNS:
            return False
            
        planet_sign = self._get_planet_sign(planet_name)
        return planet_sign == self.EXALTATION_SIGNS[planet_name]
    
    def _calculate_house_distance(self, house1: int, house2: int) -> int:
        """Calculate the distance between two houses."""
        return ((house2 - house1) % 12) + 1 if house1 != house2 else 1
    
    def _does_planet_aspect(self, aspecting_planet: str, aspected_house: int) -> bool:
        """Check if a planet aspects a particular house."""
        planet_house = self._get_planet_house_number(aspecting_planet)
        if planet_house is None:
            return False
        
        aspects = self.PLANETARY_ASPECTS.get(aspecting_planet, [7])
        distance = self._calculate_house_distance(planet_house, aspected_house)
        return distance in aspects
    
    def _are_planets_conjunct(self, planet1: str, planet2: str) -> bool:
        """Check if two planets are conjunct (in same house)."""
        house1 = self._get_planet_house_number(planet1)
        house2 = self._get_planet_house_number(planet2)
        return house1 is not None and house2 is not None and house1 == house2
    
    def _detect_type1_neecha_bhanga(self, debilitated_planet: str) -> List[NeechBhangaYoga]:
        """
        BPHS Rule: Lord of the sign of debilitation is in a Kendra from Lagna or Moon.
        
        This is considered one of the strongest forms of Neecha Bhanga as the 
        dispositor (sign lord) being well-placed can significantly uplift the debilitated planet.
        """
        yogas = []
        debilitated_sign = self._get_planet_sign(debilitated_planet)
        if not debilitated_sign:
            return yogas
        
        sign_lord = self.SIGN_LORDS.get(debilitated_sign)
        if not sign_lord:
            return yogas
        
        lord_house = self._get_planet_house_number(sign_lord)
        if lord_house and lord_house in self.KENDRA_HOUSES:
            debilitated_house = self._get_planet_house_number(debilitated_planet)
            
            yoga = NeechBhangaYoga(
                yoga_type=NeechBhangaType.DISPOSITOR_IN_KENDRA_TRIKONA,
                debilitated_planet=debilitated_planet,
                debilitated_house=debilitated_house,
                debilitated_sign=debilitated_sign,
                cancelling_planet=sign_lord,
                cancelling_factor=f"Dispositor {sign_lord} in Kendra house {lord_house}",
                additional_info={
                    'dispositor': sign_lord,
                    'dispositor_house': lord_house,
                    'cancellation_strength': 'Strong'
                }
            )
            yoga.description = self._generate_description(yoga)
            yogas.append(yoga)
            
        return yogas
    
    def _detect_type2_neecha_bhanga(self, debilitated_planet: str) -> List[NeechBhangaYoga]:
        """
        BPHS Rule: Lord of exaltation sign is in a Kendra from Lagna or Moon.
        
        When the lord of the exaltation sign is well-placed, it can help 
        the debilitated planet achieve its highest potential.
        """
        yogas = []
        exaltation_sign = self.EXALTATION_SIGNS.get(debilitated_planet)
        if not exaltation_sign:
            return yogas
        
        exalt_lord = self.SIGN_LORDS.get(exaltation_sign)
        if not exalt_lord:
            return yogas
        
        lord_house = self._get_planet_house_number(exalt_lord)
        if lord_house and lord_house in self.KENDRA_HOUSES:
            debilitated_house = self._get_planet_house_number(debilitated_planet)
            debilitated_sign = self._get_planet_sign(debilitated_planet)
            
            yoga = NeechBhangaYoga(
                yoga_type=NeechBhangaType.EXALTED_LORD_IN_KENDRA,
                debilitated_planet=debilitated_planet,
                debilitated_house=debilitated_house,
                debilitated_sign=debilitated_sign,
                cancelling_planet=exalt_lord,
                cancelling_factor=f"Exaltation lord {exalt_lord} in Kendra house {lord_house}",
                additional_info={
                    'exaltation_lord': exalt_lord,
                    'exaltation_lord_house': lord_house,
                    'exaltation_sign': exaltation_sign,
                    'cancellation_strength': 'Strong'
                }
            )
            yoga.description = self._generate_description(yoga)
            yogas.append(yoga)
            
        return yogas
    
    def _detect_type3_neecha_bhanga(self, debilitated_planet: str) -> List[NeechBhangaYoga]:
        """
        BPHS Rule: Debilitated planet is aspected by or conjoined with its own lord.
        
        When the debilitated planet receives aspect or conjunction from its own
        sign lord, it creates a strong protective influence.
        """
        yogas = []
        debilitated_sign = self._get_planet_sign(debilitated_planet)
        if not debilitated_sign:
            return yogas
        
        sign_lord = self.SIGN_LORDS.get(debilitated_sign)
        if not sign_lord or sign_lord == debilitated_planet:
            return yogas
        
        debilitated_house = self._get_planet_house_number(debilitated_planet)
        if not debilitated_house:
            return yogas
        
        # Check conjunction
        if self._are_planets_conjunct(debilitated_planet, sign_lord):
            yoga = NeechBhangaYoga(
                yoga_type=NeechBhangaType.CONJUNCTION_WITH_OWN_LORD,
                debilitated_planet=debilitated_planet,
                debilitated_house=debilitated_house,
                debilitated_sign=debilitated_sign,
                cancelling_planet=sign_lord,
                cancelling_factor=f"Conjunction with own lord {sign_lord}",
                additional_info={
                    'own_lord': sign_lord,
                    'connection_type': 'conjunction',
                    'cancellation_strength': 'Very Strong'
                }
            )
            yoga.description = self._generate_description(yoga)
            yogas.append(yoga)
        
        # Check aspect
        elif self._does_planet_aspect(sign_lord, debilitated_house):
            yoga = NeechBhangaYoga(
                yoga_type=NeechBhangaType.ASPECT_FROM_OWN_LORD,
                debilitated_planet=debilitated_planet,
                debilitated_house=debilitated_house,
                debilitated_sign=debilitated_sign,
                cancelling_planet=sign_lord,
                cancelling_factor=f"Aspect from own lord {sign_lord}",
                additional_info={
                    'own_lord': sign_lord,
                    'connection_type': 'aspect',
                    'cancellation_strength': 'Strong'
                }
            )
            yoga.description = self._generate_description(yoga)
            yogas.append(yoga)
            
        return yogas
    
    def _detect_type4_neecha_bhanga(self, debilitated_planet: str) -> List[NeechBhangaYoga]:
        """
        BPHS Rule: Debilitated planet aspected by or conjoined with exalted planet.
        
        When an exalted planet aspects or conjoins a debilitated planet,
        it can transmit its positive energy and cancel the debilitation.
        """
        yogas = []
        debilitated_house = self._get_planet_house_number(debilitated_planet)
        debilitated_sign = self._get_planet_sign(debilitated_planet)
        
        if not debilitated_house or not debilitated_sign:
            return yogas
        
        # Check all planets for exaltation
        for planet_name in self.planet_data.keys():
            if planet_name == debilitated_planet or planet_name in ['Rahu', 'Ketu']:
                continue
                
            if self._is_planet_exalted(planet_name):
                # Check conjunction
                if self._are_planets_conjunct(debilitated_planet, planet_name):
                    yoga = NeechBhangaYoga(
                        yoga_type=NeechBhangaType.CONJUNCTION_WITH_EXALTED,
                        debilitated_planet=debilitated_planet,
                        debilitated_house=debilitated_house,
                        debilitated_sign=debilitated_sign,
                        cancelling_planet=planet_name,
                        cancelling_factor=f"Conjunction with exalted {planet_name}",
                        additional_info={
                            'exalted_planet': planet_name,
                            'exalted_sign': self._get_planet_sign(planet_name),
                            'connection_type': 'conjunction',
                            'cancellation_strength': 'Very Strong'
                        }
                    )
                    yoga.description = self._generate_description(yoga)
                    yogas.append(yoga)
                
                # Check aspect
                elif self._does_planet_aspect(planet_name, debilitated_house):
                    yoga = NeechBhangaYoga(
                        yoga_type=NeechBhangaType.MUTUAL_ASPECT_WITH_EXALTED,
                        debilitated_planet=debilitated_planet,
                        debilitated_house=debilitated_house,
                        debilitated_sign=debilitated_sign,
                        cancelling_planet=planet_name,
                        cancelling_factor=f"Aspect from exalted {planet_name}",
                        additional_info={
                            'exalted_planet': planet_name,
                            'exalted_sign': self._get_planet_sign(planet_name),
                            'connection_type': 'aspect',
                            'cancellation_strength': 'Strong'
                        }
                    )
                    yoga.description = self._generate_description(yoga)
                    yogas.append(yoga)
                    
        return yogas
    
    def _generate_description(self, yoga: NeechBhangaYoga) -> str:
        """Generate human-readable description for the yoga."""
        return (f"Neecha Bhanga: {yoga.debilitated_planet} debilitated in "
                f"{yoga.debilitated_sign} (House {yoga.debilitated_house}) - "
                f"{yoga.cancelling_factor}")
    
    def detect_all_neecha_bhanga_yogas(self) -> List[NeechBhangaYoga]:
        """
        Detect all types of Neecha Bhanga Yogas as per BPHS.
        
        BPHS emphasizes that these yogas are particularly powerful when:
        1. The debilitated planet is a functional benefic for the ascendant
        2. The cancelling factor is strong (exalted, in own sign, or in Kendra)
        3. Multiple cancellation factors are present
        """
        self.detected_yogas.clear()
        all_yogas = []
        
        # Find all debilitated planets
        debilitated_planets = []
        for planet_name in self.planet_data.keys():
            if planet_name in ['Rahu', 'Ketu']:  # Skip shadow planets
                continue
            if self._is_planet_debilitated(planet_name):
                debilitated_planets.append(planet_name)
        
        # Apply all detection methods for each debilitated planet
        for planet in debilitated_planets:
            all_yogas.extend(self._detect_type1_neecha_bhanga(planet))
            all_yogas.extend(self._detect_type2_neecha_bhanga(planet))
            all_yogas.extend(self._detect_type3_neecha_bhanga(planet))
            all_yogas.extend(self._detect_type4_neecha_bhanga(planet))
        
        # Remove duplicates while preserving order
        unique_yogas = []
        seen = set()
        for yoga in all_yogas:
            key = (yoga.debilitated_planet, yoga.yoga_type, yoga.cancelling_planet)
            if key not in seen:
                seen.add(key)
                unique_yogas.append(yoga)
        
        return unique_yogas
    
    def print_yoga_summary(self, yogas: List[NeechBhangaYoga] = None) -> None:
        """Print detailed summary of all detected Neecha Bhanga Yogas."""
        if yogas is None:
            yogas = self.detect_all_neecha_bhanga_yogas()
        
        print("=" * 80)
        print("NEECHA BHANGA YOGA DETECTION SUMMARY")
        print("=" * 80)
        print(f"Total Neecha Bhanga Yogas Detected: {len(yogas)}")
        print()
        
        if not yogas:
            print("No Neecha Bhanga Yogas detected in this chart.")
            return
        
        # Group by debilitated planet
        yogas_by_planet = {}
        for yoga in yogas:
            planet = yoga.debilitated_planet
            if planet not in yogas_by_planet:
                yogas_by_planet[planet] = []
            yogas_by_planet[planet].append(yoga)
        
        for planet, planet_yogas in yogas_by_planet.items():
            print(f"\n{planet.upper()} DEBILITATION CANCELLATIONS ({len(planet_yogas)} found)")
            print("-" * 50)
            
            for i, yoga in enumerate(planet_yogas, 1):
                print(f"\n{i}. {yoga.description}")
                print(f"   Type: {yoga.yoga_type.value.replace('_', ' ').title()}")
                print(f"   Cancelling Factor: {yoga.cancelling_factor}")
                print(f"   Strength: {yoga.additional_info.get('cancellation_strength', 'Medium')}")
                
                # Additional details based on type
                if 'dispositor' in yoga.additional_info:
                    print(f"   Dispositor: {yoga.additional_info['dispositor']} in House {yoga.additional_info['dispositor_house']}")
                elif 'exalted_planet' in yoga.additional_info:
                    print(f"   Exalted Planet: {yoga.additional_info['exalted_planet']} in {yoga.additional_info['exalted_sign']}")
                elif 'own_lord' in yoga.additional_info:
                    print(f"   Connection: {yoga.additional_info['connection_type'].title()} with {yoga.additional_info['own_lord']}")
        
        print(f"\n{'='*80}")
        print("BPHS NOTE: Neecha Bhanga Raja Yoga occurs when debilitation is cancelled.")
        print("The native may initially face challenges but will eventually rise to great heights.")
        print("Multiple cancellations for the same planet create exceptionally powerful results.")
        print("=" * 80)

# Usage example:
# detector = NeechBhangaYogaDetector(planet_data, house_data)
# neecha_bhanga_yogas = detector.detect_all_neecha_bhanga_yogas()
# detector.print_yoga_summary(neecha_bhanga_yogas)