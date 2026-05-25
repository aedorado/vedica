from typing import Dict, List, Set, Optional, Any, Tuple
from dataclasses import dataclass
from enum import Enum
import math

class PanchMahapurushYogaType(Enum):
    """The five great person yogas as described in BPHS."""
    RUCHAKA = "ruchaka"      # Mars
    BHADRA = "bhadra"        # Mercury  
    HAMSA = "hamsa"          # Jupiter
    MALAVYA = "malavya"      # Venus
    SASA = "sasa"            # Saturn

@dataclass
class PanchMahapurushYoga:
    """
    Represents a Panch Mahapurush Yoga.
    
    BPHS Definition: These yogas are formed when Mars, Mercury, Jupiter, Venus, or Saturn
    are in their own sign, exaltation sign, and placed in a Kendra (1st, 4th, 7th, 10th house).
    Each yoga bestows specific qualities and status to the native.
    """
    yoga_type: PanchMahapurushYogaType
    planet: str
    house: int
    sign: str
    formation_type: str  # "own_sign", "exaltation", "moolatrikona"
    strength_score: float = 0.0
    description: str = ""
    effects: str = ""
    additional_info: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.additional_info is None:
            self.additional_info = {}

class PanchMahapurushYogaDetector:
    """
    Detects Panch Mahapurush Yogas according to BPHS principles.
    
    BPHS Chapter 77: "If Mars is in a Kendra in his own Rasi or in exaltation, 
    Ruchaka Yoga is formed. One born in Ruchaka Yoga will be proud, powerful,
    virtuous, valorous, charming, long-lived and will have a strong physique."
    
    Similar rules apply for Mercury (Bhadra), Jupiter (Hamsa), Venus (Malavya), 
    and Saturn (Sasa) yogas.
    
    Implementation closely follows BPHS by:
    1. Checking if qualifying planets are in Kendra houses (1,4,7,10)
    2. Verifying the planet is in own sign, exaltation, or moolatrikona
    3. Considering strength factors like combustion, retrogradation
    4. Providing traditional interpretations for each yoga
    """
    
    # Kendra houses as per BPHS
    KENDRA_HOUSES = {1, 4, 7, 10}
    
    # Planet configurations for Panch Mahapurush Yogas
    YOGA_CONFIGURATIONS = {
        PanchMahapurushYogaType.RUCHAKA: {
            'planet': 'Mars',
            'own_signs': ['Aries', 'Scorpio'],
            'exaltation_sign': 'Capricorn',
            'moolatrikona_sign': 'Aries',
            'moolatrikona_range': (0, 12),  # 0-12 degrees in Aries
            'effects': 'Proud, powerful, virtuous, valorous, charming, long-lived, strong physique'
        },
        PanchMahapurushYogaType.BHADRA: {
            'planet': 'Mercury',
            'own_signs': ['Gemini', 'Virgo'],
            'exaltation_sign': 'Virgo',
            'moolatrikona_sign': 'Virgo',
            'moolatrikona_range': (16, 20),  # 16-20 degrees in Virgo
            'effects': 'Learned, eloquent, skilled in arts, good advisor, wealthy, long-lived'
        },
        PanchMahapurushYogaType.HAMSA: {
            'planet': 'Jupiter',
            'own_signs': ['Sagittarius', 'Pisces'],
            'exaltation_sign': 'Cancer',
            'moolatrikona_sign': 'Sagittarius',
            'moolatrikona_range': (0, 10),  # 0-10 degrees in Sagittarius
            'effects': 'Righteous, learned, handsome, popular, devotional, blessed with good family'
        },
        PanchMahapurushYogaType.MALAVYA: {
            'planet': 'Venus',
            'own_signs': ['Taurus', 'Libra'],
            'exaltation_sign': 'Pisces',
            'moolatrikona_sign': 'Libra',
            'moolatrikona_range': (0, 15),  # 0-15 degrees in Libra
            'effects': 'Beautiful, wealthy, virtuous, learned, blessed with conveyances and luxuries'
        },
        PanchMahapurushYogaType.SASA: {
            'planet': 'Saturn',
            'own_signs': ['Capricorn', 'Aquarius'],
            'exaltation_sign': 'Libra',
            'moolatrikona_sign': 'Aquarius',
            'moolatrikona_range': (0, 20),  # 0-20 degrees in Aquarius
            'effects': 'Leader, powerful, commands respect, wealthy, long-lived, strong character'
        }
    }
    
    def __init__(self, planet_data: Dict[str, 'PlanetDetails'], house_data: Dict[str, 'HouseDetail']):
        """
        Initialize the detector with planet and house data.
        
        Args:
            planet_data: Dictionary of planet names to PlanetDetails objects
            house_data: Dictionary of house numbers to HouseDetail objects
        """
        self.planet_data = planet_data
        self.house_data = house_data
    
    def _get_planet_house_number(self, planet_name: str) -> Optional[int]:
        """Extract house number where planet is located."""
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
        """Get the sign where planet is located."""
        planet_detail = self.planet_data.get(planet_name)
        if not planet_detail:
            return None
        
        return planet_detail.safe_get_nested('PlanetRasiD1Sign', 'Name')
    
    def _get_planet_degree(self, planet_name: str) -> Optional[float]:
        """Get planet's degree position in its sign."""
        planet_detail = self.planet_data.get(planet_name)
        if not planet_detail:
            return None
        
        try:
            degree_str = planet_detail.safe_get_nested('PlanetRasiD1Degree', 'DegreeString', '')
            if degree_str:
                return self._parse_degree_string(degree_str)
        except:
            pass
        
        return None
    
    def _parse_degree_string(self, degree_str: str) -> Optional[float]:
        """Parse degree string like '12° 21' 50' to decimal degrees."""
        try:
            parts = degree_str.replace('°', ' ').replace("'", ' ').replace('"', ' ').split()
            degrees = float(parts[0]) if len(parts) > 0 else 0
            minutes = float(parts[1]) if len(parts) > 1 else 0
            seconds = float(parts[2]) if len(parts) > 2 else 0
            
            return degrees + minutes/60 + seconds/3600
        except:
            return None
    
    def _is_planet_combust(self, planet_name: str) -> bool:
        """Check if planet is combust (too close to Sun)."""
        planet_detail = self.planet_data.get(planet_name)
        if not planet_detail:
            return False
        return planet_detail.safe_get('IsPlanetCombust', False)
    
    def _is_planet_retrograde(self, planet_name: str) -> bool:
        """Check if planet is retrograde."""
        planet_detail = self.planet_data.get(planet_name)
        if not planet_detail:
            return False
        
        return planet_detail.safe_get('IsPlanetRetrograde', False)
    
    def _is_planet_debilitated(self, planet_name: str) -> bool:
        """Check if planet is debilitated."""
        planet_detail = self.planet_data.get(planet_name)
        if not planet_detail:
            return False
        
        return planet_detail.safe_get('IsPlanetDebilitated', False)
    
    def _check_formation_type(self, yoga_config: Dict, planet_sign: str, planet_degree: Optional[float]) -> Optional[str]:
        """
        Determine the type of formation (own sign, exaltation, moolatrikona).
        
        BPHS allows formation in:
        1. Own sign (Swakshetra)
        2. Exaltation sign (Uccha)
        3. Moolatrikona (within specific degree range)
        """
        # Check exaltation
        if planet_sign == yoga_config['exaltation_sign']:
            return 'exaltation'
        
        # Check own signs
        if planet_sign in yoga_config['own_signs']:
            # Check if it's moolatrikona (own sign with specific degree range)
            if (planet_sign == yoga_config['moolatrikona_sign'] and 
                planet_degree is not None):
                min_deg, max_deg = yoga_config['moolatrikona_range']
                if min_deg <= planet_degree <= max_deg:
                    return 'moolatrikona'
            return 'own_sign'
        
        return None
    
    def _calculate_yoga_strength(self, planet_name: str, formation_type: str, house: int) -> float:
        """
        Calculate yoga strength based on various factors.
        
        Strength factors considered:
        1. Formation type (exaltation > moolatrikona > own sign)
        2. House position (1st house strongest in kendras)
        3. Planet's natural strength
        4. Afflictions (combustion, debilitation reduce strength)
        """
        base_strength = 0.0
        
        # Formation type scoring
        formation_scores = {
            'exaltation': 10.0,
            'moolatrikona': 8.0,
            'own_sign': 6.0
        }
        base_strength += formation_scores.get(formation_type, 0.0)
        
        # House position scoring (1st house is strongest kendra)
        house_scores = {1: 4.0, 10: 3.0, 7: 2.0, 4: 1.0}
        base_strength += house_scores.get(house, 0.0)
        
        # Planet's shadbala strength if available
        planet_detail = self.planet_data.get(planet_name)
        if planet_detail:
            shadbala_strength = planet_detail.safe_get('PlanetShadbalaPinda', 0.0)
            if float(shadbala_strength) > 0:
                base_strength += min(float(shadbala_strength) / 100, 3.0)  # Normalize to max 3 points
        
        # Affliction penalties
        if self._is_planet_combust(planet_name):
            base_strength *= 0.5  # Severe reduction for combustion
        
        if self._is_planet_debilitated(planet_name):
            base_strength *= 0.3  # Very severe reduction for debilitation
        
        # Slight bonus for retrograde benefics (controversial, but some texts support this)
        if self._is_planet_retrograde(planet_name) and planet_name in ['Jupiter', 'Venus', 'Mercury']:
            base_strength += 0.5
        
        return round(base_strength, 2)
    
    def _generate_description(self, yoga: PanchMahapurushYoga) -> str:
        """Generate descriptive text for the yoga."""
        config = self.YOGA_CONFIGURATIONS[yoga.yoga_type]
        
        formation_desc = {
            'exaltation': f"in exaltation in {yoga.sign}",
            'moolatrikona': f"in moolatrikona in {yoga.sign}",
            'own_sign': f"in own sign {yoga.sign}"
        }
        
        return (f"{yoga.yoga_type.value.title()} Yoga: {yoga.planet} {formation_desc[yoga.formation_type]} "
                f"in {yoga.house}{'st' if yoga.house == 1 else 'th' if yoga.house not in [2,3] else ('nd' if yoga.house == 2 else 'rd')} house")
    
    def detect_panch_mahapurush_yogas(self) -> List[PanchMahapurushYoga]:
        """
        Detect all Panch Mahapurush Yogas in the chart.
        
        Returns:
            List of detected PanchMahapurushYoga objects
        """
        detected_yogas = []
        
        for yoga_type, config in self.YOGA_CONFIGURATIONS.items():
            planet_name = config['planet']
            
            # Get planet's position
            house = self._get_planet_house_number(planet_name)
            sign = self._get_planet_sign(planet_name)
            degree = self._get_planet_degree(planet_name)
            
            # Skip if planet data is incomplete
            if house is None or sign is None:
                continue
            
            # Check if planet is in Kendra house
            if house not in self.KENDRA_HOUSES:
                continue
            
            # Check formation type (own sign, exaltation, moolatrikona)
            formation_type = self._check_formation_type(config, sign, degree)
            if formation_type is None:
                continue
            
            # BPHS consideration: Severely afflicted planets may not give full yoga effects
            # But we still detect the yoga and note the affliction
            strength = self._calculate_yoga_strength(planet_name, formation_type, house)
            
            yoga = PanchMahapurushYoga(
                yoga_type=yoga_type,
                planet=planet_name,
                house=house,
                sign=sign,
                formation_type=formation_type,
                strength_score=strength,
                effects=config['effects'],
                additional_info={
                    'degree': degree,
                    'is_combust': self._is_planet_combust(planet_name),
                    'is_retrograde': self._is_planet_retrograde(planet_name),
                    'is_debilitated': self._is_planet_debilitated(planet_name),
                    'planet_strength': self.planet_data.get(planet_name, {}).safe_get('PlanetStrength', 0.0)
                }
            )
            
            yoga.description = self._generate_description(yoga)
            detected_yogas.append(yoga)
        
        # Sort by strength score (strongest first)
        detected_yogas.sort(key=lambda y: y.strength_score, reverse=True)
        
        return detected_yogas
    
    def print_yoga_summary(self, yogas: List[PanchMahapurushYoga] = None) -> None:
        """Print detailed summary of detected Panch Mahapurush Yogas."""
        if yogas is None:
            yogas = self.detect_panch_mahapurush_yogas()
        
        print("=" * 85)
        print("PANCH MAHAPURUSH YOGA DETECTION SUMMARY")
        print("=" * 85)
        print("Based on Brihat Parashara Hora Shastra principles")
        print(f"Total Panch Mahapurush Yogas Detected: {len(yogas)}")
        print()
        
        if not yogas:
            print("No Panch Mahapurush Yogas detected in this chart.")
            print("\nNote: These yogas require Mars, Mercury, Jupiter, Venus, or Saturn")
            print("to be in Kendra houses (1,4,7,10) in their own sign or exaltation.")
            return
        
        for i, yoga in enumerate(yogas, 1):
            print(f"{i}. {yoga.description}")
            print(f"   Strength Score: {yoga.strength_score}/17.0")
            print(f"   Formation: {yoga.formation_type.replace('_', ' ').title()}")
            
            # Show degree if available
            if yoga.additional_info.get('degree'):
                print(f"   Degree: {yoga.additional_info['degree']:.2f}°")
            
            # Show afflictions/enhancements
            afflictions = []
            if yoga.additional_info.get('is_combust'):
                afflictions.append("Combust")
            if yoga.additional_info.get('is_debilitated'):
                afflictions.append("Debilitated")
            if yoga.additional_info.get('is_retrograde'):
                afflictions.append("Retrograde")
            
            if afflictions:
                print(f"   Conditions: {', '.join(afflictions)}")
            
            print(f"   Traditional Effects: {yoga.effects}")
            
            # Strength interpretation
            if yoga.strength_score >= 12:
                strength_desc = "Very Strong - Full yoga effects expected"
            elif yoga.strength_score >= 8:
                strength_desc = "Strong - Good yoga effects"
            elif yoga.strength_score >= 5:
                strength_desc = "Moderate - Some yoga effects"
            else:
                strength_desc = "Weak - Limited yoga effects due to afflictions"
            
            print(f"   Interpretation: {strength_desc}")
            print()
        
        print("=" * 85)
        print("Note: Strength is reduced by combustion, debilitation, and other afflictions.")
        print("BPHS emphasizes that afflicted planets may not give full yoga results.")
        print("=" * 85)

# Usage example:
# detector = PanchMahapurushYogaDetector(planet_data_objs, house_data_objs)
# panch_mahapurush_yogas = detector.detect_panch_mahapurush_yogas()
# detector.print_yoga_summary(panch_mahapurush_yogas)