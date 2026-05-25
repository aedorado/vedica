from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from enum import Enum

class MallikaYogaType(Enum):
    LAGNA_MALIKA = "lagna_malika"           # House 1
    DHANA_MALIKA = "dhana_malika"           # House 2
    VIKRAMA_MALIKA = "vikrama_malika"       # House 3
    SUKHA_MALIKA = "sukha_malika"           # House 4 (Matru Malika)
    PUTRA_MALIKA = "putra_malika"           # House 5 (Suta Malika)
    SHATRU_MALIKA = "shatru_malika"         # House 6 (Ripu Malika)
    KALATRA_MALIKA = "kalatra_malika"       # House 7
    RANDHRA_MALIKA = "randhra_malika"       # House 8
    BHAGYA_MALIKA = "bhagya_malika"         # House 9
    KARMA_MALIKA = "karma_malika"           # House 10
    LABHA_MALIKA = "labha_malika"           # House 11 (Aaya Malika)
    VRAYA_MALIKA = "vraya_malika"           # House 12 (Vyaya Malika)

@dataclass
class MallikaYoga:
    yoga_type: MallikaYogaType
    start_house: int
    planets_sequence: List[str]
    houses_sequence: List[int]
    description: str
    effect: str
    strength_score: float
    is_present: bool = True

class MallikaYogaDetector:
    """
    Detects Mallika Yogas based on BPHS principles.
    Mallika Yoga: Seven planets (excluding Rahu, Ketu) occupy seven consecutive houses.
    Creates a garland-like formation, hence the name 'Mallika' (garland).
    """
    
    # Classical seven planets for Mallika Yoga
    MALLIKA_PLANETS = {'Sun', 'Moon', 'Mars', 'Mercury', 'Jupiter', 'Venus', 'Saturn'}
    
    # Yoga effects based on starting house
    YOGA_EFFECTS = {
        1: "Leadership qualities, strong personality, royal favor, respect in society",
        2: "Wealth accumulation, family prosperity, eloquent speech, material comforts",
        3: "Courage, siblings' support, artistic talents, communication skills",
        4: "Property, vehicles, mother's blessings, educational success, happiness",
        5: "Children's welfare, intelligence, spiritual inclination, creativity",
        6: "Victory over enemies, good health, service orientation, problem-solving",
        7: "Marriage happiness, business partnerships, diplomatic skills, travel",
        8: "Longevity, occult knowledge, unexpected gains, transformation ability",
        9: "Fortune, father's blessings, higher learning, spiritual wisdom, dharma",
        10: "Career success, fame, authority, government favor, professional recognition",
        11: "Gains, fulfillment of desires, elder siblings' support, network benefits",
        12: "Spiritual liberation, foreign connections, charitable nature, meditation"
    }
    
    def __init__(self, planet_data: Dict[str, Any], house_data: Dict[str, Any]):
        self.planet_data = planet_data
        self.house_data = house_data
        self.detected_yogas: List[MallikaYoga] = []
        
    def _get_planet_house(self, planet_name: str) -> Optional[int]:
        """Get house number where planet is located."""
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
    
    def _get_planet_positions(self) -> Dict[int, List[str]]:
        """Map house numbers to planets occupying them."""
        house_to_planets = {}
        for planet in self.MALLIKA_PLANETS:
            house = self._get_planet_house(planet)
            if house:
                house_to_planets.setdefault(house, []).append(planet)
        return house_to_planets
    
    def _check_consecutive_houses(self, start_house: int) -> Optional[Dict[int, List[str]]]:
        """Check if 7 consecutive houses from start_house contain all 7 planets."""
        house_positions = self._get_planet_positions()
        consecutive_sequence = {}
        planets_found = set()
        
        for i in range(7):
            current_house = ((start_house - 1 + i) % 12) + 1
            planets_in_house = house_positions.get(current_house, [])
            
            if not planets_in_house:
                return None  # Empty house breaks the sequence
                
            consecutive_sequence[current_house] = planets_in_house
            planets_found.update(planets_in_house)
        
        # Must have all 7 planets in the 7 consecutive houses
        if len(planets_found) == 7 and planets_found == self.MALLIKA_PLANETS:
            return consecutive_sequence
        return None
    
    def _calculate_strength(self, start_house: int, sequence: Dict[int, List[str]]) -> float:
        """Calculate yoga strength based on planet dignities and house significance."""
        base_strength = 50.0
        
        # Bonus for auspicious starting houses
        house_bonuses = {1: 20, 4: 15, 5: 15, 9: 18, 10: 20, 11: 12}
        base_strength += house_bonuses.get(start_house, 5)
        
        # Planet dignity bonuses
        dignity_bonus = 0
        for house, planets in sequence.items():
            for planet in planets:
                planet_detail = self.planet_data.get(planet, {})
                if planet_detail.safe_get('IsPlanetExaltedSign', False):
                    dignity_bonus += 15
                elif planet_detail.safe_get('IsPlanetInOwnSign', False):
                    dignity_bonus += 10
                elif planet_detail.safe_get('IsPlanetDebilitated', False):
                    dignity_bonus -= 8
        
        return base_strength + dignity_bonus
    
    def detect_mallika_yoga(self, start_house: int) -> Optional[MallikaYoga]:
        """Detect Mallika Yoga starting from a specific house."""
        sequence = self._check_consecutive_houses(start_house)
        if not sequence:
            return None
        
        # Create ordered list of planets and houses
        planets_sequence = []
        houses_sequence = []
        for i in range(7):
            house = ((start_house - 1 + i) % 12) + 1
            houses_sequence.append(house)
            planets_sequence.extend(sequence[house])
        
        # Map house number to yoga type
        yoga_types = [
            MallikaYogaType.LAGNA_MALIKA, MallikaYogaType.DHANA_MALIKA, 
            MallikaYogaType.VIKRAMA_MALIKA, MallikaYogaType.SUKHA_MALIKA,
            MallikaYogaType.PUTRA_MALIKA, MallikaYogaType.SHATRU_MALIKA,
            MallikaYogaType.KALATRA_MALIKA, MallikaYogaType.RANDHRA_MALIKA,
            MallikaYogaType.BHAGYA_MALIKA, MallikaYogaType.KARMA_MALIKA,
            MallikaYogaType.LABHA_MALIKA, MallikaYogaType.VRAYA_MALIKA
        ]
        
        yoga_type = yoga_types[start_house - 1]
        strength = self._calculate_strength(start_house, sequence)
        
        # Create planet-house mapping description
        house_details = []
        for house in houses_sequence:
            planets = sequence[house]
            house_details.append(f"H{house}({', '.join(planets)})")
        
        return MallikaYoga(
            yoga_type=yoga_type,
            start_house=start_house,
            planets_sequence=planets_sequence,
            houses_sequence=houses_sequence,
            description=f"Seven planets in consecutive houses: {' → '.join(house_details)}",
            effect=self.YOGA_EFFECTS[start_house],
            strength_score=strength
        )
    
    def detect_all_mallika_yogas(self) -> List[MallikaYoga]:
        """Detect all possible Mallika Yogas (12 variations)."""
        self.detected_yogas = []
        
        for start_house in range(1, 13):
            yoga = self.detect_mallika_yoga(start_house)
            if yoga:
                self.detected_yogas.append(yoga)
        
        # Sort by strength
        self.detected_yogas.sort(key=lambda x: x.strength_score, reverse=True)
        return self.detected_yogas
    
    def create_summary_table(self) -> List[Dict[str, Any]]:
        """Create a comprehensive summary table of all 12 possible Mallika Yogas."""
        present_yogas = {yoga.start_house: yoga for yoga in self.detected_yogas}
        
        yoga_names = [
            "Lagna Malika", "Dhana Malika", "Vikrama Malika", "Sukha Malika",
            "Putra Malika", "Shatru Malika", "Kalatra Malika", "Randhra Malika", 
            "Bhagya Malika", "Karma Malika", "Labha Malika", "Vraya Malika"
        ]
        
        table_data = []
        for house in range(1, 13):
            yoga = present_yogas.get(house)
            end_house = ((house + 5) % 12) + 1 if house <= 6 else house - 7
            formation = f"7 planets in H{house}-H{end_house}" if house <= 6 else f"7 planets in H{house}-H12, H1-H{end_house}"
            
            table_data.append({
                'Yoga': yoga_names[house - 1],
                'Present': '✓' if yoga else '✗',
                'Formation': formation,
                'Effect': self.YOGA_EFFECTS[house],
                'Strength': f"{yoga.strength_score:.1f}" if yoga else "N/A"
            })
        
        return table_data
    
    def print_report(self) -> None:
        """Print comprehensive Mallika Yoga analysis report."""
        if not self.detected_yogas:
            self.detect_all_mallika_yogas()
        
        print("\n" + "="*100)
        print("MALLIKA YOGA ANALYSIS (BPHS Based)")
        print("="*100)
        print("Definition: Seven planets (Sun, Moon, Mars, Mercury, Jupiter, Venus, Saturn)")
        print("           occupy seven consecutive houses, forming a garland-like pattern")
        print("="*100)
        
        # Summary statistics
        total_yogas = len(self.detected_yogas)
        if total_yogas > 0:
            avg_strength = sum(y.strength_score for y in self.detected_yogas) / total_yogas
            max_strength = max(y.strength_score for y in self.detected_yogas)
            print(f"SUMMARY: {total_yogas} Mallika Yoga(s) detected | Avg Strength: {avg_strength:.1f} | Max: {max_strength:.1f}")
        else:
            print("SUMMARY: No Mallika Yogas detected")
        print()
        
        # Comprehensive table
        table_data = self.create_summary_table()
        
        # Print table header
        print(f"{'Yoga':<18} {'Present':<8} {'Formation':<35} {'Strength':<10} {'Effect'}")
        print("-" * 100)
        
        # Print table rows
        for row in table_data:
            effect_truncated = row['Effect'][:100] + "..." if len(row['Effect']) > 100 else row['Effect']
            print(f"{row['Yoga']:<18} {row['Present']:<8} {row['Formation']:<35} {row['Strength']:<10} {effect_truncated}")
        
        print("-" * 100)
        
        # Detailed analysis of detected yogas
        if self.detected_yogas:
            print("\nDETAILED ANALYSIS OF DETECTED YOGAS:")
            print("="*60)
            
            for i, yoga in enumerate(self.detected_yogas, 1):
                yoga_name = yoga.yoga_type.value.replace('_', ' ').title()
                print(f"\n{i}. {yoga_name}")
                print(f"   Formation: {yoga.description}")
                print(f"   Effect: {yoga.effect}")
                print(f"   Strength Score: {yoga.strength_score:.1f}")
                print(f"   Houses Involved: {', '.join(map(str, yoga.houses_sequence))}")
                print(f"   Planets: {', '.join(yoga.planets_sequence)}")
        
        print("\n" + "="*100)
        print("Note: Mallika Yoga is considered highly auspicious and rare.")
        print("      It bestows leadership qualities, wealth, and spiritual growth.")
        print("="*100)

# Usage function
def analyze_mallika_yogas(planet_data: Dict[str, Any], house_data: Dict[str, Any]) -> List[MallikaYoga]:
    """Analyze and return Mallika yogas for a chart."""
    detector = MallikaYogaDetector(planet_data, house_data)
    yogas = detector.detect_all_mallika_yogas()
    detector.print_report()
    return yogas