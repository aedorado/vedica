from typing import Dict, List, Set, Optional, Any, Tuple
from dataclasses import dataclass
from enum import Enum

class ParivartanaType(Enum):
    MAHA_PARIVARTANA = "maha_parivartana"      # Between Kendra/Trikona lords
    DAINYA_PARIVARTANA = "dainya_parivartana"  # Involving 6th, 8th, 12th house lords
    KHALA_PARIVARTANA = "khala_parivartana"    # Between remaining houses (2,3,11)

@dataclass
class ParivartanaYoga:
    """
    BPHS Reference: Chapter 30 - Effects of Parivartana (Exchange) Yogas
    
    BPHS defines three types of Parivartana Yogas:
    
    1. MAHA PARIVARTANA (Great Exchange):
       - Between lords of Kendra houses (1,4,7,10) and Trikona houses (1,5,9)
       - Highly auspicious, gives Raja Yoga results
       - Native achieves high status, wealth, and recognition
    
    2. DAINYA PARIVARTANA (Misery Exchange):  
       - Involving lords of Dusthana houses (6,8,12)
       - Generally inauspicious, causes suffering and obstacles
       - However, exchange between two Dusthana lords can reduce mutual harm
    
    3. KHALA PARIVARTANA (Common Exchange):
       - Between lords of remaining houses (2,3,11) with any other
       - Mixed results, neither very good nor very bad
       - Gives moderate results related to the houses involved
    """
    yoga_type: ParivartanaType
    planet1: str
    planet2: str
    house1: int
    house2: int
    planet1_placement_house: int
    planet2_placement_house: int
    description: str = ""
    significance: str = ""
    strength_score: float = 0.0
    additional_info: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.additional_info is None:
            self.additional_info = {}

class ParivartanaYogaDetector:
    """
    Comprehensive Parivartana Yoga detector following BPHS classifications.
    
    BPHS emphasizes that Parivartana Yogas are formed when two planets are
    placed in each other's signs, creating a mutual exchange relationship.
    The effects depend on the nature of the houses whose lords are involved.
    """
    
    # House classifications as per BPHS
    KENDRA_HOUSES = {1, 4, 7, 10}           # Angular houses - most powerful
    TRIKONA_HOUSES = {1, 5, 9}              # Trinal houses - highly auspicious  
    DUSTHANA_HOUSES = {6, 8, 12}            # Houses of suffering
    UPACHAYA_HOUSES = {3, 6, 10, 11}        # Growing houses
    NEUTRAL_HOUSES = {2, 3, 11}             # Remaining houses
    
    # Sign lords as per BPHS
    SIGN_LORDS = {
        'Aries': 'Mars', 'Taurus': 'Venus', 'Gemini': 'Mercury',
        'Cancer': 'Moon', 'Leo': 'Sun', 'Virgo': 'Mercury',
        'Libra': 'Venus', 'Scorpio': 'Mars', 'Sagittarius': 'Jupiter',
        'Capricorn': 'Saturn', 'Aquarius': 'Saturn', 'Pisces': 'Jupiter'
    }
    
    def __init__(self, planet_data: Dict[str, 'PlanetDetails'], house_data: Dict[str, 'HouseDetail']):
        self.planet_data = planet_data
        self.house_data = house_data
        self.house_lords = self._get_house_lords()
        self.detected_yogas = set()
        
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
        """Get all houses ruled by a planet."""
        return [house_num for house_num, lord in self.house_lords.items() 
                if lord == planet_name]
    
    def _get_planet_sign(self, planet_name: str) -> Optional[str]:
        """Get the sign a planet is placed in."""
        planet_detail = self.planet_data.get(planet_name)
        if not planet_detail:
            return None
        return planet_detail.safe_get_nested('PlanetRasiD1Sign', 'Name')
    
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
    
    def _are_planets_in_exchange(self, planet1: str, planet2: str) -> bool:
        """
        Check if two planets are in mutual sign exchange.
        
        BPHS defines exchange as: Planet A is in Planet B's sign AND
        Planet B is in Planet A's sign simultaneously.
        """
        planet1_sign = self._get_planet_sign(planet1)
        planet2_sign = self._get_planet_sign(planet2)
        
        if not planet1_sign or not planet2_sign:
            return False
        
        # Get sign lords
        planet1_sign_lord = self.SIGN_LORDS.get(planet1_sign)
        planet2_sign_lord = self.SIGN_LORDS.get(planet2_sign)
        
        # Check if they are in each other's signs
        return planet1_sign_lord == planet2 and planet2_sign_lord == planet1
    
    def _classify_parivartana_type(self, planet1: str, planet2: str) -> Optional[ParivartanaType]:
        """
        Classify the type of Parivartana Yoga based on BPHS rules.
        
        BPHS Classification:
        - Maha: Exchange between Kendra and Trikona lords (or within them)
        - Dainya: Exchange involving any Dusthana house lord
        - Khala: All other exchanges
        """
        houses1 = self._get_houses_ruled_by_planet(planet1)
        houses2 = self._get_houses_ruled_by_planet(planet2)
        
        if not houses1 or not houses2:
            return None
        
        # Check all combinations of house lordships
        all_houses = set(houses1 + houses2)
        
        # Dainya: If any Dusthana house is involved
        if any(house in self.DUSTHANA_HOUSES for house in all_houses):
            return ParivartanaType.DAINYA_PARIVARTANA
        
        # Maha: If Kendra and/or Trikona houses are involved
        kendra_involved = any(house in self.KENDRA_HOUSES for house in all_houses)
        trikona_involved = any(house in self.TRIKONA_HOUSES for house in all_houses)
        
        if kendra_involved or trikona_involved:
            return ParivartanaType.MAHA_PARIVARTANA
        
        # Khala: All other exchanges
        return ParivartanaType.KHALA_PARIVARTANA
    
    def _calculate_strength_score(self, yoga_type: ParivartanaType, planet1: str, planet2: str, 
                                 houses1: List[int], houses2: List[int]) -> float:
        """
        Calculate strength score for the Parivartana Yoga based on BPHS principles.
        
        Scoring factors:
        - Yoga type (Maha > Khala > Dainya)
        - Planet dignity and strength
        - House significance
        - Mutual aspects and friendships
        """
        base_score = 0.0
        
        # Base score by yoga type
        if yoga_type == ParivartanaType.MAHA_PARIVARTANA:
            base_score = 8.0
        elif yoga_type == ParivartanaType.KHALA_PARIVARTANA:
            base_score = 5.0
        else:  # DAINYA_PARIVARTANA
            base_score = 2.0
        
        # Bonus for beneficial house combinations
        all_houses = set(houses1 + houses2)
        
        # Extra points for Kendra-Trikona combinations
        if (any(h in self.KENDRA_HOUSES for h in all_houses) and 
            any(h in self.TRIKONA_HOUSES for h in all_houses)):
            base_score += 2.0
        
        # Bonus for 1st house involvement (Ascendant lord)
        if 1 in all_houses:
            base_score += 1.0
        
        # Penalty for Dusthana involvement
        dusthana_count = sum(1 for h in all_houses if h in self.DUSTHANA_HOUSES)
        base_score -= dusthana_count * 1.5
        
        # Ensure score is within reasonable bounds
        return max(0.0, min(10.0, base_score))
    
    def _generate_yoga_description(self, yoga_type: ParivartanaType, planet1: str, planet2: str,
                                  houses1: List[int], houses2: List[int]) -> str:
        """Generate detailed description of the Parivartana Yoga."""
        house1_str = ", ".join(map(str, houses1))
        house2_str = ", ".join(map(str, houses2))
        
        if yoga_type == ParivartanaType.MAHA_PARIVARTANA:
            return (f"Maha Parivartana Yoga formed between {planet1} (lord of house {house1_str}) "
                   f"and {planet2} (lord of house {house2_str}). This creates a highly auspicious "
                   f"exchange bestowing Raja Yoga effects, bringing honor, status, and prosperity.")
        
        elif yoga_type == ParivartanaType.DAINYA_PARIVARTANA:
            return (f"Dainya Parivartana Yoga formed between {planet1} (lord of house {house1_str}) "
                   f"and {planet2} (lord of house {house2_str}). This exchange involving Dusthana "
                   f"houses may bring challenges and obstacles, though mutual exchange can reduce "
                   f"some negative effects.")
        
        else:  # KHALA_PARIVARTANA
            return (f"Khala Parivartana Yoga formed between {planet1} (lord of house {house1_str}) "
                   f"and {planet2} (lord of house {house2_str}). This creates a moderate exchange "
                   f"with mixed results depending on the planets' natural significations.")
    
    def _get_yoga_significance(self, yoga_type: ParivartanaType, houses1: List[int], 
                              houses2: List[int]) -> str:
        """Get the astrological significance of the yoga."""
        all_houses = houses1 + houses2
        house_meanings = {
            1: "Self, personality, health", 2: "Wealth, family, speech",
            3: "Courage, siblings, efforts", 4: "Home, mother, comfort",
            5: "Intelligence, children, creativity", 6: "Enemies, diseases, obstacles",
            7: "Partnership, marriage, business", 8: "Longevity, transformation, occult",
            9: "Fortune, dharma, father", 10: "Career, reputation, authority",
            11: "Gains, friends, aspirations", 12: "Losses, spirituality, foreign lands"
        }
        
        significance = f"This yoga influences: {', '.join(house_meanings.get(h, f'House {h}') for h in sorted(set(all_houses)))}"
        
        if yoga_type == ParivartanaType.MAHA_PARIVARTANA:
            significance += ". As a Maha Parivartana, it grants exceptional results in these life areas."
        elif yoga_type == ParivartanaType.DAINYA_PARIVARTANA:
            significance += ". As a Dainya Parivartana, it may create challenges in these areas."
        else:
            significance += ". As a Khala Parivartana, it gives moderate results in these areas."
            
        return significance
    
    def detect_all_parivartana_yogas(self) -> List[ParivartanaYoga]:
        """
        Detect all Parivartana Yogas in the chart.
        
        BPHS Method:
        1. Check all planet pairs for mutual sign exchange
        2. Classify the type based on house lordships
        3. Calculate strength and significance
        """
        yogas = []
        planets = list(self.planet_data.keys())
        
        # Check all planet pairs
        for i in range(len(planets)):
            for j in range(i + 1, len(planets)):
                planet1, planet2 = planets[i], planets[j]
                
                # Skip if we've already detected this combination
                yoga_key = tuple(sorted([planet1, planet2]))
                if yoga_key in self.detected_yogas:
                    continue
                
                # Check if planets are in mutual exchange
                if self._are_planets_in_exchange(planet1, planet2):
                    # Get house positions
                    planet1_house = self._get_planet_house_number(planet1)
                    planet2_house = self._get_planet_house_number(planet2)
                    
                    if planet1_house is None or planet2_house is None:
                        continue
                    
                    # Get houses ruled by each planet
                    houses1 = self._get_houses_ruled_by_planet(planet1)
                    houses2 = self._get_houses_ruled_by_planet(planet2)
                    
                    if not houses1 or not houses2:
                        continue
                    
                    # Classify yoga type
                    yoga_type = self._classify_parivartana_type(planet1, planet2)
                    if not yoga_type:
                        continue
                    
                    # Calculate strength score
                    strength = self._calculate_strength_score(yoga_type, planet1, planet2, houses1, houses2)
                    
                    # Generate description and significance
                    description = self._generate_yoga_description(yoga_type, planet1, planet2, houses1, houses2)
                    significance = self._get_yoga_significance(yoga_type, houses1, houses2)
                    
                    # Create yoga object
                    yoga = ParivartanaYoga(
                        yoga_type=yoga_type,
                        planet1=planet1,
                        planet2=planet2,
                        house1=houses1[0] if houses1 else 0,  # Primary house for planet1
                        house2=houses2[0] if houses2 else 0,  # Primary house for planet2
                        planet1_placement_house=planet1_house,
                        planet2_placement_house=planet2_house,
                        description=description,
                        significance=significance,
                        strength_score=strength,
                        additional_info={
                            'all_houses_ruled_by_planet1': houses1,
                            'all_houses_ruled_by_planet2': houses2,
                            'planet1_sign': self._get_planet_sign(planet1),
                            'planet2_sign': self._get_planet_sign(planet2)
                        }
                    )
                    
                    yogas.append(yoga)
                    self.detected_yogas.add(yoga_key)
        
        # Sort by strength score (strongest first)
        yogas.sort(key=lambda y: y.strength_score, reverse=True)
        return yogas
    
    def print_yoga_summary(self, yogas: List[ParivartanaYoga] = None) -> None:
        """Print detailed summary of all detected Parivartana Yogas - following standard format."""
        if yogas is None:
            yogas = self.detect_all_parivartana_yogas()
        
        print("=" * 80)
        print("PARIVARTANA YOGA DETECTION SUMMARY")
        print("=" * 80)
        print(f"Total Parivartana Yogas Detected: {len(yogas)}")
        print()
        
        if not yogas:
            print("No Parivartana Yogas detected in this chart.")
            return
        
        # Count by type
        maha_count = sum(1 for y in yogas if y.yoga_type == ParivartanaType.MAHA_PARIVARTANA)
        dainya_count = sum(1 for y in yogas if y.yoga_type == ParivartanaType.DAINYA_PARIVARTANA)
        khala_count = sum(1 for y in yogas if y.yoga_type == ParivartanaType.KHALA_PARIVARTANA)
        avg_strength = sum(y.strength_score for y in yogas) / len(yogas) if yogas else 0
        
        print(f"Maha Parivartana (Highly Auspicious): {maha_count}")
        print(f"Dainya Parivartana (Challenging): {dainya_count}")
        print(f"Khala Parivartana (Mixed Results): {khala_count}")
        print(f"Average Strength Score: {avg_strength:.2f}/10")
        print()
        
        # Group by type
        yoga_by_type = {
            ParivartanaType.MAHA_PARIVARTANA: [],
            ParivartanaType.DAINYA_PARIVARTANA: [],
            ParivartanaType.KHALA_PARIVARTANA: []
        }
        
        for yoga in yogas:
            yoga_by_type[yoga.yoga_type].append(yoga)
        
        # Print by category
        type_headers = {
            ParivartanaType.MAHA_PARIVARTANA: "MAHA PARIVARTANA YOGAS (Great Exchange)",
            ParivartanaType.DAINYA_PARIVARTANA: "DAINYA PARIVARTANA YOGAS (Misery Exchange)",
            ParivartanaType.KHALA_PARIVARTANA: "KHALA PARIVARTANA YOGAS (Common Exchange)"
        }
        
        for yoga_type, header in type_headers.items():
            type_yogas = yoga_by_type[yoga_type]
            if type_yogas:
                print(f"\n{header} ({len(type_yogas)} found)")
                print("-" * len(header))
                
                for i, yoga in enumerate(type_yogas, 1):
                    print(f"\n{i}. Exchange: {yoga.planet1} ↔ {yoga.planet2}")
                    print(f"   House Lordships: {yoga.planet1} rules House {yoga.house1}, "
                          f"{yoga.planet2} rules House {yoga.house2}")
                    print(f"   Current Positions: {yoga.planet1} in House {yoga.planet1_placement_house} "
                          f"({yoga.additional_info.get('planet1_sign', 'N/A')}), "
                          f"{yoga.planet2} in House {yoga.planet2_placement_house} "
                          f"({yoga.additional_info.get('planet2_sign', 'N/A')})")
                    print(f"   Strength Score: {yoga.strength_score:.1f}/10")
                    print(f"   Description: {yoga.description}")
                    print(f"   Significance: {yoga.significance}")
                    
                    # Additional house details
                    all_houses1 = yoga.additional_info.get('all_houses_ruled_by_planet1', [])
                    all_houses2 = yoga.additional_info.get('all_houses_ruled_by_planet2', [])
                    if len(all_houses1) > 1 or len(all_houses2) > 1:
                        print(f"   Complete Lordships: {yoga.planet1} rules Houses {all_houses1}, "
                              f"{yoga.planet2} rules Houses {all_houses2}")
        
        print("\n" + "=" * 80)

    def get_yoga_summary(self) -> Dict[str, Any]:
        """Get a summary of all detected Parivartana Yogas (for backward compatibility)."""
        yogas = self.detect_all_parivartana_yogas()
        
        summary = {
            'total_yogas': len(yogas),
            'maha_parivartana_count': sum(1 for y in yogas if y.yoga_type == ParivartanaType.MAHA_PARIVARTANA),
            'dainya_parivartana_count': sum(1 for y in yogas if y.yoga_type == ParivartanaType.DAINYA_PARIVARTANA),
            'khala_parivartana_count': sum(1 for y in yogas if y.yoga_type == ParivartanaType.KHALA_PARIVARTANA),
            'strongest_yoga': yogas[0] if yogas else None,
            'average_strength': sum(y.strength_score for y in yogas) / len(yogas) if yogas else 0,
            'all_yogas': yogas
        }
        
        return summary

    # Helper function to use the detector (for backward compatibility)
    def detect_parivartana_yogas(planet_data: Dict[str, 'PlanetDetails'], 
                            house_data: Dict[str, 'HouseDetail']) -> List[ParivartanaYoga]:
        """
        Convenience function to detect Parivartana Yogas.
        
        Args:
            planet_data: Dictionary of planet details
            house_data: Dictionary of house details
            
        Returns:
            List of detected Parivartana Yogas
        """
        detector = ParivartanaYogaDetector(planet_data, house_data)
        return detector.detect_all_parivartana_yogas()