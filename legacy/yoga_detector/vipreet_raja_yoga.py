from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from enum import Enum

class VipareetType(Enum):
    HARSHA = "Harsha"     # 6th lord in 8th or 12th
    SARALA = "Sarala"     # 8th lord in 6th or 12th  
    VIMALA = "Vimala"     # 12th lord in 6th or 8th

@dataclass
class VipareetRajaYoga:
    """Simplified Vipareet Raja Yoga representation."""
    vipareet_type: VipareetType
    dusthana_lord: str
    dusthana_house: int
    placement_house: int
    description: str = ""
    planet_strength: str = "Moderate"
    yoga_strength: str = "Moderate"
    planet_sign: str = ""
    additional_info: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.additional_info is None:
            self.additional_info = {}
    
    def __eq__(self, other):
        if not isinstance(other, VipareetRajaYoga):
            return False
        return (
            self.vipareet_type == other.vipareet_type and
            self.dusthana_lord == other.dusthana_lord and
            self.dusthana_house == other.dusthana_house and
            self.placement_house == other.placement_house
        )
    
    def __hash__(self):
        return hash((
            self.vipareet_type,
            self.dusthana_lord,
            self.dusthana_house,
            self.placement_house
        ))

class SimplifiedVipareetRajaDetector:
    """
    Simplified Vipareet Raja Yoga detector using PlanetDetails and HouseDetail classes.
    
    BPHS (Brihat Parashara Hora Shastra) Definition of Vipareet Raja Yoga:
    =====================================================================
    
    From BPHS Chapter 41 (Raja Yogas), Verses 42-44:
    
    "If the lord of the 6th house is posited in the 8th or 12th house, 
     Harsha Yoga is formed."
    
    "If the lord of the 8th house is posited in the 6th or 12th house, 
     Sarala Yoga is formed."
    
    "If the lord of the 12th house is posited in the 6th or 8th house, 
     Vimala Yoga is formed."
    
    "One born in Harsha Yoga will be troubled by diseases in his early years, 
     but will be happy later, will have good wealth, be victorious over enemies, 
     be virtuous, skilful and will enjoy life."
    
    "One born in Sarala Yoga will be long-lived, fearless, learned, celebrated, 
     prosperous, equipped with good wife and children, and will destroy his enemies."
    
    "One born in Vimala Yoga will be frugal, happy, independent, kind, virtuous, 
     famous, learned, and will enjoy excellent wealth."
    
    Implementation Fidelity to BPHS:
    ================================
    
    ✅ EXACT MATCH: Core yoga definitions (dusthana lord placements)
    ✅ EXACT MATCH: Three yoga types (Harsha, Sarala, Vimala)
    ✅ EXACT MATCH: House combinations as specified in classical texts
    
    ⚡ ENHANCEMENTS BEYOND BPHS:
    - Strength assessment using Shadbala principles
    - Consideration of planetary afflictions/conjunctions
    - Paradoxical strength evaluation (weaker dusthana lord = stronger yoga)
    - Integration with modern astrological software data structures
    
    📚 CLASSICAL PRINCIPLE PRESERVED:
    The fundamental principle that "evil placed in evil gives good results" 
    (dusthana lords in dusthana houses) is maintained exactly as per BPHS.
    
    Note: BPHS doesn't provide strength gradations for these yogas, so our
    strength assessment is based on logical extensions of classical principles
    combined with Shadbala and affliction concepts from the same text.
    """
    
    DUSTHANA_HOUSES = {6, 8, 12}
    
    def __init__(self, planet_data: Dict[str, 'PlanetDetails'], house_data: Dict[str, 'HouseDetail']):
        self.planet_data = planet_data
        self.house_data = house_data
        self.house_lords = self._extract_house_lords()
        
    def _extract_house_lords(self) -> Dict[int, str]:
        """Extract house lords from house data."""
        house_lords = {}
        
        for house_key, house_detail in self.house_data.items():
            house_num = int(house_key)
            lord_name = house_detail.safe_get_nested('LordOfHouse', 'Name')
            if lord_name:
                house_lords[house_num] = lord_name
                
        return house_lords
    
    def _get_planet_house(self, planet_name: str) -> Optional[int]:
        """Get house number where planet is placed."""
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
    
    def _get_planet_sign(self, planet_name: str) -> str:
        """Get planet's sign."""
        planet_detail = self.planet_data.get(planet_name)
        if not planet_detail:
            return ""
        
        sign_detail = planet_detail.safe_get_nested('PlanetRasiD1Sign')
        return sign_detail.Name if sign_detail else ""
    
    def _assess_planet_strength(self, planet_name: str) -> str:
        """Assess planet strength using available boolean flags."""
        planet_detail = self.planet_data.get(planet_name)
        if not planet_detail:
            return "Moderate"
        
        # Check for strong conditions
        if (planet_detail.safe_get('IsPlanetExaltedSign', False) or
            planet_detail.safe_get('IsPlanetInOwnSign', False) or
            planet_detail.safe_get('IsPlanetInMoolatrikona', False) or
            planet_detail.safe_get('IsPlanetStrongInShadbala', False)):
            return "Strong"
        
        # Check for weak conditions  
        if (planet_detail.safe_get('IsPlanetDebilitated', False) or
            planet_detail.safe_get('IsPlanetCombust', False) or
            planet_detail.safe_get('IsPlanetAfflicted', False)):
            return "Weak"
        
        return "Moderate"
    
    def _calculate_yoga_strength(self, planet_name: str, dusthana_house: int, placement_house: int) -> str:
        """Calculate Vipareet Raja Yoga strength."""
        strength_points = 0
        planet_detail = self.planet_data.get(planet_name)
        
        if not planet_detail:
            return "Moderate"
        
        # Vipareet Raja Yoga is paradoxically stronger when dusthana lord is weaker
        planet_strength = self._assess_planet_strength(planet_name)
        if planet_strength == "Weak":
            strength_points += 2
        elif planet_strength == "Moderate":
            strength_points += 1
        
        # Placement in another dusthana house strengthens the yoga
        if placement_house in self.DUSTHANA_HOUSES:
            strength_points += 1
        
        # Additional afflictions can strengthen Vipareet Raja Yoga
        if planet_detail.safe_get('IsPlanetAspectedByMaleficPlanets', False):
            strength_points += 1
        
        # Conjunction with malefics can strengthen the yoga
        if planet_detail.safe_get('IsPlanetConjunctWithMaleficPlanets', False):
            strength_points += 1
        
        if strength_points >= 4:
            return "Very Strong"
        elif strength_points >= 3:
            return "Strong"
        elif strength_points >= 2:
            return "Moderate"
        else:
            return "Weak"
    
    def _create_yoga(self, vipareet_type: VipareetType, dusthana_house: int, 
                     placement_house: int) -> Optional[VipareetRajaYoga]:
        """Create a Vipareet Raja Yoga object."""
        dusthana_lord = self.house_lords.get(dusthana_house)
        
        if not dusthana_lord:
            return None
        
        lord_house = self._get_planet_house(dusthana_lord)
        if lord_house != placement_house:
            return None
        
        planet_strength = self._assess_planet_strength(dusthana_lord)
        yoga_strength = self._calculate_yoga_strength(dusthana_lord, dusthana_house, placement_house)
        planet_sign = self._get_planet_sign(dusthana_lord)
        
        yoga = VipareetRajaYoga(
            vipareet_type=vipareet_type,
            dusthana_lord=dusthana_lord,
            dusthana_house=dusthana_house,
            placement_house=placement_house,
            planet_strength=planet_strength,
            yoga_strength=yoga_strength,
            planet_sign=planet_sign
        )
        
        yoga.description = (f"{vipareet_type.value} Yoga: {dusthana_lord} "
                          f"(lord of {dusthana_house}th house) in {placement_house}th house")
        
        return yoga
    
    def detect_harsha_yoga(self) -> List[VipareetRajaYoga]:
        """Detect Harsha Yoga - 6th lord in 8th or 12th house."""
        yogas = []
        
        for placement_house in {8, 12}:
            yoga = self._create_yoga(VipareetType.HARSHA, 6, placement_house)
            if yoga:
                yogas.append(yoga)
        
        return yogas
    
    def detect_sarala_yoga(self) -> List[VipareetRajaYoga]:
        """Detect Sarala Yoga - 8th lord in 6th or 12th house."""
        yogas = []
        
        for placement_house in {6, 12}:
            yoga = self._create_yoga(VipareetType.SARALA, 8, placement_house)
            if yoga:
                yogas.append(yoga)
        
        return yogas
    
    def detect_vimala_yoga(self) -> List[VipareetRajaYoga]:
        """Detect Vimala Yoga - 12th lord in 6th or 8th house."""
        yogas = []
        
        for placement_house in {6, 8}:
            yoga = self._create_yoga(VipareetType.VIMALA, 12, placement_house)
            if yoga:
                yogas.append(yoga)
        
        return yogas
    
    def detect_all_vipareet_raja_yogas(self) -> List[VipareetRajaYoga]:
        """Detect all types of Vipareet Raja Yogas."""
        all_yogas = []
        all_yogas.extend(self.detect_harsha_yoga())
        all_yogas.extend(self.detect_sarala_yoga())
        all_yogas.extend(self.detect_vimala_yoga())
        
        # Remove duplicates while preserving order
        unique_yogas = []
        seen = set()
        for yoga in all_yogas:
            if yoga not in seen:
                unique_yogas.append(yoga)
                seen.add(yoga)
        
        return unique_yogas
    
    def print_yoga_summary(self, yogas: List[VipareetRajaYoga] = None) -> None:
        """Print comprehensive summary of detected Vipareet Raja Yogas."""
        if yogas is None:
            yogas = self.detect_all_vipareet_raja_yogas()
        
        print("=" * 85)
        print("VIPAREET RAJA YOGA DETECTION SUMMARY")
        print("=" * 85)
        print(f"Total Vipareet Raja Yogas Found: {len(yogas)}")
        print()
        
        if not yogas:
            print("❌ No Vipareet Raja Yogas detected in this chart.")
            print("\nVipareet Raja Yogas form when dusthana lords (6th, 8th, 12th)")
            print("are placed in other dusthana houses, converting malefic")
            print("influences into beneficial results.")
            return
        
        # Group yogas by type
        yoga_groups = {
            VipareetType.HARSHA: [],
            VipareetType.SARALA: [],
            VipareetType.VIMALA: []
        }
        
        for yoga in yogas:
            yoga_groups[yoga.vipareet_type].append(yoga)
        
        # Print each yoga type
        type_info = {
            VipareetType.HARSHA: {
                'title': '🏆 HARSHA YOGA (6th lord in 8th/12th house)',
                'meaning': 'Victory over enemies, good health, overcoming obstacles',
                'benefits': 'Triumph in competitions, recovery from illness, debt freedom'
            },
            VipareetType.SARALA: {
                'title': '🔬 SARALA YOGA (8th lord in 6th/12th house)', 
                'meaning': 'Protection from dangers, research abilities, occult knowledge',
                'benefits': 'Safety from accidents, investigative skills, mystical insights'
            },
            VipareetType.VIMALA: {
                'title': '💰 VIMALA YOGA (12th lord in 6th/8th house)',
                'meaning': 'Financial gains through foreign sources, spiritual growth',
                'benefits': 'Foreign income, expenditure control, spiritual advancement'
            }
        }
        
        for yoga_type, info in type_info.items():
            group_yogas = yoga_groups[yoga_type]
            if not group_yogas:
                continue
                
            print(f"\n{info['title']}")
            print("─" * len(info['title']))
            print(f"📖 Meaning: {info['meaning']}")
            print(f"✨ Benefits: {info['benefits']}")
            print()
            
            for i, yoga in enumerate(group_yogas, 1):
                print(f"{i}. {yoga.description}")
                print(f"   🪐 Planet: {yoga.dusthana_lord} in {yoga.planet_sign}")
                print(f"   💪 Planet Strength: {yoga.planet_strength}")
                print(f"   ⭐ Yoga Strength: {yoga.yoga_strength}")
                
                # Add interpretation based on strength
                if yoga.yoga_strength in ["Strong", "Very Strong"]:
                    print(f"   🎯 Effect: Powerful and clearly manifested benefits")
                elif yoga.yoga_strength == "Moderate":
                    print(f"   🎯 Effect: Noticeable positive results")
                else:
                    print(f"   🎯 Effect: Subtle beneficial influences")
                print()
        
        print("💡 Note: Vipareet Raja Yogas work paradoxically - the weaker the")
        print("   dusthana lord, the stronger the yoga's beneficial effects!")
        print("=" * 85)
    
    def get_yoga_effects_summary(self) -> Dict[str, Any]:
        """Get a structured summary of yoga effects for external use."""
        yogas = self.detect_all_vipareet_raja_yogas()
        
        summary = {
            'total_yogas': len(yogas),
            'yogas_by_type': {
                'harsha': len([y for y in yogas if y.vipareet_type == VipareetType.HARSHA]),
                'sarala': len([y for y in yogas if y.vipareet_type == VipareetType.SARALA]),
                'vimala': len([y for y in yogas if y.vipareet_type == VipareetType.VIMALA])
            },
            'strongest_yoga': None,
            'detailed_yogas': []
        }
        
        if yogas:
            # Find strongest yoga
            strength_order = {"Very Strong": 4, "Strong": 3, "Moderate": 2, "Weak": 1}
            strongest = max(yogas, key=lambda y: strength_order.get(y.yoga_strength, 0))
            summary['strongest_yoga'] = {
                'type': strongest.vipareet_type.value,
                'planet': strongest.dusthana_lord,
                'strength': strongest.yoga_strength,
                'description': strongest.description
            }
            
            # Add detailed info for all yogas
            for yoga in yogas:
                summary['detailed_yogas'].append({
                    'type': yoga.vipareet_type.value,
                    'planet': yoga.dusthana_lord,
                    'planet_sign': yoga.planet_sign,
                    'dusthana_house': yoga.dusthana_house,
                    'placement_house': yoga.placement_house,
                    'planet_strength': yoga.planet_strength,
                    'yoga_strength': yoga.yoga_strength,
                    'description': yoga.description
                })
        
        return summary

# Usage examples:
"""
# Initialize detector
detector = SimplifiedVipareetRajaDetector(planet_data_objs, house_data_objs)

# Get all yogas
all_yogas = detector.detect_all_vipareet_raja_yogas()

# Print detailed summary
detector.print_yoga_summary()

# Get structured data for external use
effects_summary = detector.get_yoga_effects_summary()
print(f"Total yogas: {effects_summary['total_yogas']}")

# Detect specific yoga types
harsha_yogas = detector.detect_harsha_yoga()
sarala_yogas = detector.detect_sarala_yoga()
vimala_yogas = detector.detect_vimala_yoga()
"""