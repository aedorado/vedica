from typing import Dict, List, Optional, Any, Set
from dataclasses import dataclass
from enum import Enum

import logging
logger = logging.getLogger(__name__)

class SunYogaType(Enum):
    VESI = "vesi"
    VASI = "vasi"
    OBHAYACHARI = "obhayachari"
    BUDHA_ADITYA = "budha_aditya"

@dataclass
class SunYoga:
    yoga_type: SunYogaType
    description: str
    effect: str
    is_benefic: bool
    strength_score: float = 0.0
    planets_involved: List[str] = None
    houses_involved: List[int] = None
    
    def __post_init__(self):
        if self.planets_involved is None:
            self.planets_involved = []
        if self.houses_involved is None:
            self.houses_involved = []

class SunYogaDetector:
    """Detects solar yogas based on Brihat Parashara Hora Shastra principles."""
    
    # Classical planets for Sun yogas (excluding Moon for these formations)
    BENEFIC_PLANETS = {'Jupiter', 'Venus', 'Mercury'}
    MALEFIC_PLANETS = {'Mars', 'Saturn'}
    YOGA_PLANETS = {'Mars', 'Mercury', 'Jupiter', 'Venus', 'Saturn'}  # Excluding Moon for Sun yogas
    
    def __init__(self, planet_data: Dict[str, Any], house_data: Dict[str, Any]):
        self.planet_data = planet_data
        self.house_data = house_data
        self.detected_yogas = []
        
    def _get_planet_house(self, planet_name: str) -> Optional[int]:
        """Get house number where planet is located."""
        planet_detail = self.planet_data.get(planet_name)
        if not planet_detail:
            return None
        
        house_str = planet_detail.get('HousePlanetOccupiesBasedOnSign', '')
        if house_str.startswith('House'):
            try:
                return int(house_str.replace('House', ''))
            except ValueError:
                return None
        return None
    
    def _get_planets_in_house(self, house_number: int) -> List[str]:
        """Get all planets in a specific house using PlanetsInHouseBasedOnSign."""
        house_key = f'{house_number}'
        house_detail = self.house_data.get(house_key, {})
        return house_detail.get('PlanetsInHouseBasedOnSign', [])
    
    def _house_distance(self, from_house: int, to_house: int) -> int:
        """Calculate Vedic-style inclusive house distance (1-12 system)."""
        return ((to_house - from_house) % 12) + 1
    
    def _get_planet_dignity(self, planet_name: str) -> str:
        """Get planet's dignity (exalted, own sign, debilitated, etc.)"""
        planet_detail = self.planet_data.get(planet_name, {})
        
        exalted = planet_detail.get('IsPlanetExaltedSign', False)
        own_sign = planet_detail.get('IsPlanetInOwnSign', False)
        debilitated = planet_detail.get('IsPlanetDebilitatedSign', False)
        
        if exalted == "True" or exalted == True:
            return 'exalted'
        elif own_sign == "True" or own_sign == True:
            return 'own_sign'
        elif debilitated == "True" or debilitated == True:
            return 'debilitated'
        else:
            return 'neutral'
    
    def _calculate_planet_strength_bonus(self, planet_name: str) -> float:
        """Calculate strength bonus based on planet's dignity."""
        dignity = self._get_planet_dignity(planet_name)
        dignity_bonus = {
            'exalted': 20.0,
            'own_sign': 12.0,
            'debilitated': -8.0,
            'neutral': 0.0
        }
        return dignity_bonus.get(dignity, 0.0)
    
    def detect_vesi_yoga(self) -> Optional[SunYoga]:
        """
        BPHS: Vesi Yoga - Any planet (except Moon) in 2nd house from Sun
        Effect: Balanced, truthful, good speaker, happy, prosperous
        """
        sun_house = self._get_planet_house('Sun')
        if not sun_house:
            return None
            
        second_house = (sun_house % 12) + 1
        planets_in_second = [p for p in self._get_planets_in_house(second_house) 
                           if p in self.YOGA_PLANETS]
        
        if not planets_in_second:
            return None
        
        # Calculate strength based on planets involved
        benefic_count = sum(1 for p in planets_in_second if p in self.BENEFIC_PLANETS)
        malefic_count = len(planets_in_second) - benefic_count
        
        base_strength = 35.0
        strength = base_strength + (benefic_count * 12.0) - (malefic_count * 6.0)
        
        # Add dignity bonuses
        for planet in planets_in_second:
            strength += self._calculate_planet_strength_bonus(planet)
        
        # Special bonus for Mercury (natural significator of speech)
        if 'Mercury' in planets_in_second:
            strength += 8.0
        
        return SunYoga(
            yoga_type=SunYogaType.VESI,
            description=f"Planets {', '.join(planets_in_second)} in 2nd house from Sun (House {second_house})",
            effect="Balanced temperament, truthfulness, eloquent speech, happiness, and prosperity",
            is_benefic=True,
            strength_score=max(strength, 20.0),
            planets_involved=['Sun'] + planets_in_second,
            houses_involved=[sun_house, second_house]
        )
    
    def detect_vasi_yoga(self) -> Optional[SunYoga]:
        """
        BPHS: Vasi Yoga - Any planet (except Moon) in 12th house from Sun
        Effect: Skillful, wealthy, good servant/subordinate, enjoys pleasures
        """
        sun_house = self._get_planet_house('Sun')
        if not sun_house:
            return None
            
        twelfth_house_from_sun = ((sun_house - 2) % 12) + 1
        planets_in_twelfth = [p for p in self._get_planets_in_house(twelfth_house_from_sun) 
                             if p in self.YOGA_PLANETS]
        
        if not planets_in_twelfth:
            return None
        
        # Calculate strength based on planets involved
        benefic_count = sum(1 for p in planets_in_twelfth if p in self.BENEFIC_PLANETS)
        malefic_count = len(planets_in_twelfth) - benefic_count
        
        base_strength = 30.0
        strength = base_strength + (benefic_count * 10.0) - (malefic_count * 5.0)
        
        # Add dignity bonuses
        for planet in planets_in_twelfth:
            strength += self._calculate_planet_strength_bonus(planet)
        
        # Special consideration for Venus (natural significator of luxury/pleasure)
        if 'Venus' in planets_in_twelfth:
            strength += 6.0
        
        return SunYoga(
            yoga_type=SunYogaType.VASI,
            description=f"Planets {', '.join(planets_in_twelfth)} in 12th house from Sun (House {twelfth_house_from_sun})",
            effect="Skillful nature, wealth accumulation, service orientation, and enjoyment of pleasures",
            is_benefic=True,
            strength_score=max(strength, 18.0),
            planets_involved=['Sun'] + planets_in_twelfth,
            houses_involved=[sun_house, twelfth_house_from_sun]
        )
    
    def detect_obhayachari_yoga(self) -> Optional[SunYoga]:
        """
        BPHS: Obhayachari Yoga - Planets (except Moon) in both 2nd and 12th from Sun
        Effect: Combines benefits of Vesi and Vasi - eloquent, wealthy, famous, learned
        """
        sun_house = self._get_planet_house('Sun')
        if not sun_house:
            return None
            
        second_house = (sun_house % 12) + 1
        twelfth_house = ((sun_house - 2) % 12) + 1
        
        planets_in_second = [p for p in self._get_planets_in_house(second_house) 
                           if p in self.YOGA_PLANETS]
        planets_in_twelfth = [p for p in self._get_planets_in_house(twelfth_house) 
                             if p in self.YOGA_PLANETS]
        
        if not planets_in_second or not planets_in_twelfth:
            return None
        
        all_planets = planets_in_second + planets_in_twelfth
        benefic_count = sum(1 for p in all_planets if p in self.BENEFIC_PLANETS)
        malefic_count = len(all_planets) - benefic_count
        
        # Base strength higher than individual yogas
        base_strength = 55.0
        strength = base_strength + (benefic_count * 15.0) - (malefic_count * 8.0)
        
        # Add dignity bonuses
        for planet in all_planets:
            strength += self._calculate_planet_strength_bonus(planet)
        
        # Special bonuses for specific combinations
        if 'Mercury' in all_planets:
            strength += 10.0  # Enhanced communication
        if 'Jupiter' in all_planets:
            strength += 12.0  # Wisdom and learning
        if 'Venus' in all_planets:
            strength += 8.0   # Artistic and luxury
        
        return SunYoga(
            yoga_type=SunYogaType.OBHAYACHARI,
            description=f"Planets in 2nd ({', '.join(planets_in_second)}) and 12th ({', '.join(planets_in_twelfth)}) from Sun",
            effect="Eloquent speaker, wealthy, famous, learned, enjoys royal comforts and respect",
            is_benefic=True,
            strength_score=max(strength, 35.0),
            planets_involved=['Sun'] + all_planets,
            houses_involved=[sun_house, second_house, twelfth_house]
        )
    
    def detect_budha_aditya_yoga(self) -> Optional[SunYoga]:
        """
        BPHS: Budha-Aditya Yoga - Mercury conjunct Sun or very close to Sun
        Effect: Intelligence, learning, good communication, scholarly nature
        Note: Traditional texts mention this yoga when Mercury is not combust
        """
        sun_house = self._get_planet_house('Sun')
        mercury_house = self._get_planet_house('Mercury')
        
        if not sun_house or not mercury_house:
            return None
        
        # Check if Mercury is in the same house as Sun
        if sun_house != mercury_house:
            return None
        
        # Calculate strength based on Mercury's condition
        base_strength = 45.0
        strength = base_strength
        
        # Check Mercury's dignity
        mercury_dignity = self._get_planet_dignity('Mercury')
        strength += self._calculate_planet_strength_bonus('Mercury')
        
        # Check Sun's dignity as well
        strength += self._calculate_planet_strength_bonus('Sun') * 0.5
        
        # Special considerations for combustion (traditionally negative)
        # In classical texts, very close conjunction can cause combustion
        # but the yoga still provides intellectual benefits
        mercury_detail = self.planet_data.get('Mercury', {})
        is_combust = mercury_detail.get('IsPlanetCombust', False)
        is_combust = is_combust == "True" or is_combust == True
        
        if is_combust:
            strength -= 15.0  # Reduce strength for combustion
            combust_note = " (Mercury combust - reduced strength)"
        else:
            strength += 10.0  # Bonus for non-combust Mercury
            combust_note = " (Mercury not combust - enhanced strength)"
        
        # House-based modifications
        if sun_house in {1, 5, 9, 10}:  # Favorable houses for Sun
            strength += 8.0
        elif sun_house in {6, 8, 12}:  # Challenging houses
            strength -= 5.0
        
        return SunYoga(
            yoga_type=SunYogaType.BUDHA_ADITYA,
            description=f"Mercury conjunct Sun in House {sun_house}{combust_note}",
            effect="Sharp intellect, excellent communication skills, scholarly pursuits, and learning abilities",
            is_benefic=True,
            strength_score=max(strength, 25.0),
            planets_involved=['Sun', 'Mercury'],
            houses_involved=[sun_house]
        )
    
    def detect_all_yogas(self) -> List[SunYoga]:
        """Detect all Sun yogas and return sorted by strength."""
        yoga_methods = [
            self.detect_vesi_yoga,
            self.detect_vasi_yoga,
            self.detect_obhayachari_yoga,
            self.detect_budha_aditya_yoga,
        ]
        
        yogas = []
        for method in yoga_methods:
            try:
                yoga = method()
                if yoga:
                    yogas.append(yoga)
            except Exception as e:
                logger.error(f"Error in {method.__name__}: {e}")
                print(f"Error in {method.__name__}: {e}")
        
        self.detected_yogas = sorted(yogas, key=lambda x: x.strength_score, reverse=True)
        return self.detected_yogas
    
    def print_report(self) -> None:
        """Print formatted Sun Yoga report."""
        if not self.detected_yogas:
            self.detect_all_yogas()
        
        print("\n" + "="*70)
        print("SUN YOGA ANALYSIS (BPHS Based)")
        print("="*70)
        
        if not self.detected_yogas:
            print("No Sun Yogas detected.")
            return
        
        benefic_count = sum(1 for y in self.detected_yogas if y.is_benefic)
        malefic_count = len(self.detected_yogas) - benefic_count
        
        print(f"Total Yogas: {len(self.detected_yogas)} | Benefic: {benefic_count} | Malefic: {malefic_count}")
        print()
        
        for i, yoga in enumerate(self.detected_yogas, 1):
            status = "✓ BENEFIC" if yoga.is_benefic else "⚠ MALEFIC"
            print(f"{i}. {yoga.yoga_type.value.upper()} YOGA {status}")
            print(f"   Formation: {yoga.description}")
            print(f"   Effect: {yoga.effect}")
            print(f"   Strength: {yoga.strength_score:.1f}")
            print(f"   Planets: {', '.join(yoga.planets_involved)}")
            if len(yoga.houses_involved) > 1:
                print(f"   Houses: {', '.join(map(str, yoga.houses_involved))}")
            print()
        
        print("="*70)
        print("\nNOTE: Sun yogas are generally benefic and enhance solar qualities")
        print("like leadership, confidence, communication, and intellectual abilities.")
        print("="*70)

# Example usage function
def analyze_sun_yogas(planet_data: Dict[str, Any], house_data: Dict[str, Any]) -> List[SunYoga]:
    """Analyze and return Sun yogas for a chart."""
    detector = SunYogaDetector(planet_data, house_data)
    yogas = detector.detect_all_yogas()
    detector.print_report()
    return yogas
