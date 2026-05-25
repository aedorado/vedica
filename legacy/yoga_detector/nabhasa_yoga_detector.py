from typing import Dict, List, Optional, Any, Set
from dataclasses import dataclass
from enum import Enum
import logging

logger = logging.getLogger(__name__)

class NabhasaYogaType(Enum):
    # Akriti Yogas - Based on planetary distribution across house types (Kendra, Panapara, Apoklima)
    KAMALA = "kamala"           # All planets in Kendras (1,4,7,10) - Lotus formation
    VAPI = "vapi"               # All planets in Panaparas (2,5,8,11) - Well formation
    SAMUDRA = "samudra"         # All planets in Apoklimas (3,6,9,12) - Ocean formation
    YUPA = "yupa"               # Planets in Kendras and Panaparas only - Sacrificial post formation
    ISHU = "ishu"               # Planets in Kendras and Apoklimas only - Arrow formation  
    SAKTI = "sakti"             # Planets in Panaparas and Apoklimas only - Spear formation
    DANDA = "danda"             # All planets in first 7 houses (1-7) - Staff formation
    NAVA = "nava"               # All planets in last 7 houses (7-12) - Ship formation
    KUTA = "kuta"               # All planets in first 4 houses (1-4) - Hill formation
    CHHATRA = "chhatra"         # All planets in houses 4-10 - Umbrella formation
    CHAPA = "chapa"             # All planets from 4th house in sequence - Bow formation
    ARDHA_CHANDRA = "ardha_chandra"  # All planets in houses 1-7 except one - Half moon formation
    CHAKRA = "chakra"           # All planets in alternate houses - Wheel formation
    GADA = "gada"               # All planets in 6 consecutive houses - Mace formation
    SAKATA = "sakata"           # All planets in 1st and 7th houses only - Cart formation
    VIHAGA = "vihaga"           # All planets in 4th and 10th houses only - Bird formation
    VAJRA = "vajra"             # All planets in 1st, 4th, 7th, 10th houses (benefics in Kendras) - Diamond formation
    YAVA = "yava"               # All planets in 1st, 2nd, 4th, 5th houses - Barley formation
    SRINGATAKA = "sringataka"   # All planets in 1st, 5th, 9th houses (trines) - Ornamental formation
    HALA = "hala"               # All planets in 2nd, 6th, 10th houses - Plough formation
    
    # Sankhya Yogas - Based on number of houses occupied by all 7 planets
    VALLAKI = "vallaki"         # All planets occupy exactly 7 houses - Creeper formation
    DAMINI = "damini"           # All planets occupy exactly 6 houses - Lightning formation
    PASA = "pasa"               # All planets occupy exactly 5 houses - Noose formation
    KEDARA = "kedara"           # All planets occupy exactly 4 houses - Cultivated field formation
    SULA = "sula"               # All planets occupy exactly 3 houses - Trident formation
    YUGA = "yuga"               # All planets occupy exactly 2 houses - Yoke formation
    GOLA = "gola"               # All planets occupy exactly 1 house - Sphere formation
    
    # Asraya Yogas - Based on planetary distribution across sign qualities (Movable, Fixed, Dual)
    RAJJU = "rajju"             # All planets in movable signs (Aries, Cancer, Libra, Capricorn) - Rope formation
    MUSALA = "musala"           # All planets in fixed signs (Taurus, Leo, Scorpio, Aquarius) - Pestle formation
    NALA = "nala"               # All planets in dual signs (Gemini, Virgo, Sagittarius, Pisces) - Reed formation
    
    # Dala Yogas - Based on planetary distribution across chart hemispheres
    SRIK = "srik"               # All planets in 7 consecutive signs - Garland formation (Also known as Mala)
    SARPA = "sarpa"             # All planets in 6 consecutive signs - Serpent formation

class NabhasaCategory(Enum):
    AKRITI = "akriti"
    SANKHYA = "sankhya"
    ASRAYA = "asraya"
    DALA = "dala"

@dataclass
class NabhasaYoga:
    yoga_type: NabhasaYogaType
    category: NabhasaCategory
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

class NabhasaYogaDetector:
    """Detects Nabhasa yogas based on BPHS principles."""
    
    # Classical planets for Nabhasa yogas (7 visible planets, excluding Rahu/Ketu)
    NABHASA_PLANETS = {'Sun', 'Moon', 'Mars', 'Mercury', 'Jupiter', 'Venus', 'Saturn'}
    BENEFIC_PLANETS = {'Jupiter', 'Venus', 'Mercury', 'Moon'}
    MALEFIC_PLANETS = {'Mars', 'Saturn', 'Sun'}
    
    # House classifications
    KENDRA_HOUSES = {1, 4, 7, 10}
    PANAPARA_HOUSES = {2, 5, 8, 11}
    APOKLIMA_HOUSES = {3, 6, 9, 12}
    
    MOVABLE_SIGNS = {1, 4, 7, 10}  # Aries, Cancer, Libra, Capricorn
    FIXED_SIGNS = {2, 5, 8, 11}    # Taurus, Leo, Scorpio, Aquarius
    DUAL_SIGNS = {3, 6, 9, 12}     # Gemini, Virgo, Sagittarius, Pisces
    
    ODD_HOUSES = {1, 3, 5, 7, 9, 11}
    EVEN_HOUSES = {2, 4, 6, 8, 10, 12}
    
    def __init__(self, planet_data: Dict[str, Any], house_data: Dict[str, Any]):
        self.planet_data = planet_data
        self.house_data = house_data
        self.detected_yogas = []
        
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
    
    def _get_planet_sign_number(self, planet_name: str) -> Optional[int]:
        """Get sign number (1-12) for planet."""
        planet_detail = self.planet_data.get(planet_name)
        if not planet_detail:
            return None
        
        sign_detail = planet_detail.safe_get('PlanetRasiD1Sign')
        if sign_detail and hasattr(sign_detail, 'Name'):
            # Map sign names to numbers
            sign_map = {
                'Aries': 1, 'Taurus': 2, 'Gemini': 3, 'Cancer': 4,
                'Leo': 5, 'Virgo': 6, 'Libra': 7, 'Scorpio': 8,
                'Sagittarius': 9, 'Capricorn': 10, 'Aquarius': 11, 'Pisces': 12
            }
            return sign_map.get(sign_detail.Name)
        return None
    
    def _get_nabhasa_planet_positions(self) -> Dict[str, Dict[str, int]]:
        """Get positions of all Nabhasa planets."""
        positions = {}
        for planet in self.NABHASA_PLANETS:
            house = self._get_planet_house(planet)
            sign = self._get_planet_sign_number(planet)
            if house and sign:
                positions[planet] = {'house': house, 'sign': sign}
        return positions
    
    def _calculate_base_strength(self, planets: List[str], base: float) -> float:
        """Calculate strength based on planet dignities and benefic/malefic nature."""
        strength = base
        benefic_count = sum(1 for p in planets if p in self.BENEFIC_PLANETS)
        malefic_count = len(planets) - benefic_count
        
        strength += benefic_count * 8.0 - malefic_count * 4.0
        
        # Add dignity bonuses
        for planet in planets:
            dignity = self._get_planet_dignity(planet)
            if dignity == 'exalted':
                strength += 15.0
            elif dignity == 'own_sign':
                strength += 10.0
            elif dignity == 'debilitated':
                strength -= 6.0
        
        return max(strength, 10.0)
    
    def _get_planet_dignity(self, planet_name: str) -> str:
        """Get planet's dignity."""
        planet_detail = self.planet_data.get(planet_name, {})
        
        if planet_detail.safe_get('IsPlanetExaltedSign', False):
            return 'exalted'
        elif planet_detail.safe_get('IsPlanetInOwnSign', False):
            return 'own_sign'
        elif planet_detail.safe_get('IsPlanetDebilitatedSign', False):
            return 'debilitated'
        else:
            return 'neutral'
    
    # AKRITI YOGAS
    def detect_kamala_yoga(self) -> Optional[NabhasaYoga]:
        """
        BPHS: Kamala (Padma) Yoga - All 7 planets in Kendra houses (1,4,7,10)
        Effect: Wealthy, virtuous, intelligent, long life, famous
        """
        positions = self._get_nabhasa_planet_positions()
        if len(positions) != 7:
            return None
        
        planets_in_kendra = [p for p, pos in positions.items() 
                           if pos['house'] in self.KENDRA_HOUSES]
        
        if len(planets_in_kendra) != 7:
            return None
        
        houses_occupied = list(set(pos['house'] for pos in positions.values()))
        strength = self._calculate_base_strength(planets_in_kendra, 70.0)
        
        # Special bonus for this highly auspicious yoga
        strength += 15.0
        
        return NabhasaYoga(
            yoga_type=NabhasaYogaType.KAMALA,
            category=NabhasaCategory.AKRITI,
            description=f"All 7 planets in Kendra houses: {', '.join(map(str, sorted(houses_occupied)))}",
            effect="Wealthy, virtuous, intelligent, long-lived, famous, enjoys royal comforts",
            is_benefic=True,
            strength_score=strength,
            planets_involved=planets_in_kendra,
            houses_involved=houses_occupied
        )
    
    def detect_vapi_yoga(self) -> Optional[NabhasaYoga]:
        """
        BPHS: Vapi Yoga - All 7 planets in Panapara (2,5,8,11) or Apoklima (3,6,9,12) houses
        Effect: Accumulation of wealth, water-related benefits
        """
        positions = self._get_nabhasa_planet_positions()
        if len(positions) != 7:
            return None
        
        planets_in_panapara = [p for p, pos in positions.items() 
                             if pos['house'] in self.PANAPARA_HOUSES]
        planets_in_apoklima = [p for p, pos in positions.items() 
                             if pos['house'] in self.APOKLIMA_HOUSES]
        
        if len(planets_in_panapara) == 7:
            house_type = "Panapara"
            planets_list = planets_in_panapara
            base_strength = 55.0
        elif len(planets_in_apoklima) == 7:
            house_type = "Apoklima"
            planets_list = planets_in_apoklima
            base_strength = 45.0
        else:
            return None
        
        houses_occupied = list(set(pos['house'] for pos in positions.values()))
        strength = self._calculate_base_strength(planets_list, base_strength)
        
        return NabhasaYoga(
            yoga_type=NabhasaYogaType.VAPI,
            category=NabhasaCategory.AKRITI,
            description=f"All 7 planets in {house_type} houses: {', '.join(map(str, sorted(houses_occupied)))}",
            effect="Accumulation of wealth, benefits from water-related activities, storage of resources",
            is_benefic=True,
            strength_score=strength,
            planets_involved=planets_list,
            houses_involved=houses_occupied
        )
    
    def detect_samudra_yoga(self) -> Optional[NabhasaYoga]:
        """
        BPHS: Samudra Yoga - All 7 planets in even houses (2,4,6,8,10,12)
        Effect: Wealthy like an ocean, virtuous, many comforts
        """
        positions = self._get_nabhasa_planet_positions()
        if len(positions) != 7:
            return None
        
        planets_in_even = [p for p, pos in positions.items() 
                         if pos['house'] in self.EVEN_HOUSES]
        
        if len(planets_in_even) != 7:
            return None
        
        houses_occupied = list(set(pos['house'] for pos in positions.values()))
        strength = self._calculate_base_strength(planets_in_even, 60.0)
        
        return NabhasaYoga(
            yoga_type=NabhasaYogaType.SAMUDRA,
            category=NabhasaCategory.AKRITI,
            description=f"All 7 planets in even houses: {', '.join(map(str, sorted(houses_occupied)))}",
            effect="Wealthy like an ocean, virtuous, enjoys many comforts, magnanimous nature",
            is_benefic=True,
            strength_score=strength,
            planets_involved=planets_in_even,
            houses_involved=houses_occupied
        )
    
    def detect_yupa_yoga(self) -> Optional[NabhasaYoga]:
        """BPHS: Yupa - All planets in 4 kendras"""
        positions = self._get_nabhasa_planet_positions()
        if len(positions) != 7:
            return None
        
        planets_in_kendras = [p for p, pos in positions.items() 
                            if pos['house'] in self.KENDRA_HOUSES]
        
        if len(planets_in_kendras) != 7:
            return None
        
        houses = list(set(pos['house'] for pos in positions.values()))
        strength = self._calculate_base_strength(planets_in_kendras, 85.0)
        
        return NabhasaYoga(
            NabhasaYogaType.YUPA, NabhasaCategory.AKRITI,
            f"All planets in kendras: {sorted(houses)}",
            "Spiritual inclination, religious nature, generous, virtuous",
            True, strength, planets_in_kendras, houses
        )

    def detect_ardha_chandra_yoga(self) -> Optional[NabhasaYoga]:
        """BPHS: Ardha Chandra - Planets in one half of chart"""
        positions = self._get_nabhasa_planet_positions()
        if len(positions) != 7:
            return None
        
        # Check if all planets in houses 1-6 or 7-12
        first_half = {1, 2, 3, 4, 5, 6}
        second_half = {7, 8, 9, 10, 11, 12}
        
        houses_occupied = set(pos['house'] for pos in positions.values())
        
        if houses_occupied.issubset(first_half):
            strength = self._calculate_base_strength(list(positions.keys()), 75.0)
            return NabhasaYoga(
                NabhasaYogaType.ARDHA_CHANDRA, NabhasaCategory.AKRITI,
                f"All planets in first half (houses 1-6): {sorted(houses_occupied)}",
                "Good looks, famous, leader of army, wealthy",
                True, strength, list(positions.keys()), sorted(houses_occupied)
            )
        elif houses_occupied.issubset(second_half):
            strength = self._calculate_base_strength(list(positions.keys()), 65.0)
            return NabhasaYoga(
                NabhasaYogaType.ARDHA_CHANDRA, NabhasaCategory.AKRITI,
                f"All planets in second half (houses 7-12): {sorted(houses_occupied)}",
                "Brave but may face challenges in early life",
                True, strength, list(positions.keys()), sorted(houses_occupied)
            )
        
        return None

    def detect_chakra_yoga(self) -> Optional[NabhasaYoga]:
        """BPHS: Chakra - Planets in alternate houses starting from odd houses"""
        positions = self._get_nabhasa_planet_positions()
        if len(positions) != 7:
            return None
        
        houses_occupied = set(pos['house'] for pos in positions.values())
        odd_houses_occupied = houses_occupied.intersection(self.ODD_HOUSES)
        
        if len(odd_houses_occupied) == len(houses_occupied):
            strength = self._calculate_base_strength(list(positions.keys()), 85.0)
            return NabhasaYoga(
                NabhasaYogaType.CHAKRA, NabhasaCategory.AKRITI,
                f"All planets in odd houses: {sorted(houses_occupied)}",
                "King or equal to king, victorious, owns lands",
                True, strength, list(positions.keys()), sorted(houses_occupied)
            )
        
        return None

    def detect_gada_yoga(self) -> Optional[NabhasaYoga]:
        """BPHS: Gada - Planets in 2 kendras"""
        positions = self._get_nabhasa_planet_positions()
        if len(positions) != 7:
            return None
        
        kendra_houses_occupied = set()
        for pos in positions.values():
            if pos['house'] in self.KENDRA_HOUSES:
                kendra_houses_occupied.add(pos['house'])
        
        if len(kendra_houses_occupied) == 2:
            planets_in_kendras = [p for p, pos in positions.items() 
                                if pos['house'] in self.KENDRA_HOUSES]
            
            if len(planets_in_kendras) == 7:
                strength = self._calculate_base_strength(planets_in_kendras, 75.0)
                return NabhasaYoga(
                    NabhasaYogaType.GADA, NabhasaCategory.AKRITI,
                    f"All planets in 2 kendras: {sorted(kendra_houses_occupied)}",
                    "Endowed with conveyances and fame, performs religious sacrifices",
                    True, strength, planets_in_kendras, sorted(kendra_houses_occupied)
                )
        
        return None

    def detect_sakata_yoga(self) -> Optional[NabhasaYoga]:
        """BPHS: Sakata - Planets in 1st and 7th house (cart formation)"""
        positions = self._get_nabhasa_planet_positions()
        if len(positions) != 7:
            return None
        
        planets_in_1_7 = [p for p, pos in positions.items() 
                        if pos['house'] in {1, 7}]
        
        houses_occupied = set(pos['house'] for pos in positions.values())
        
        if len(planets_in_1_7) == 7 and houses_occupied == {1, 7}:
            strength = self._calculate_base_strength(planets_in_1_7, 50.0)
            return NabhasaYoga(
                NabhasaYogaType.SAKATA, NabhasaCategory.AKRITI,
                "All planets in 1st and 7th houses (cart formation)",
                "Poverty, sorrow, humiliation, fallen from position",
                False, strength, planets_in_1_7, [1, 7]
            )
        
        return None

    def detect_vihaga_yoga(self) -> Optional[NabhasaYoga]:
        """BPHS: Vihaga - Planets in 4th and 10th houses"""
        positions = self._get_nabhasa_planet_positions()
        if len(positions) != 7:
            return None
        
        planets_in_4_10 = [p for p, pos in positions.items() 
                        if pos['house'] in {4, 10}]
        
        houses_occupied = set(pos['house'] for pos in positions.values())
        
        if len(planets_in_4_10) == 7 and houses_occupied == {4, 10}:
            strength = self._calculate_base_strength(planets_in_4_10, 70.0)
            return NabhasaYoga(
                NabhasaYogaType.VIHAGA, NabhasaCategory.AKRITI,
                "All planets in 4th and 10th houses",
                "Quarrelsome, fond of traveling, envoy or messenger",
                False, strength, planets_in_4_10, [4, 10]
            )
        
        return None

    def detect_vajra_yoga(self) -> Optional[NabhasaYoga]:
        """BPHS: Vajra - Benefics in 1st & 7th, malefics in 4th & 10th"""
        positions = self._get_nabhasa_planet_positions()
        if len(positions) != 7:
            return None
        
        benefics_in_1_7 = [p for p, pos in positions.items() 
                        if p in self.BENEFIC_PLANETS and pos['house'] in {1, 7}]
        malefics_in_4_10 = [p for p, pos in positions.items() 
                        if p in self.MALEFIC_PLANETS and pos['house'] in {4, 10}]
        
        if (len(benefics_in_1_7) >= 2 and len(malefics_in_4_10) >= 2 and 
            len(benefics_in_1_7) + len(malefics_in_4_10) == 7):
            
            strength = self._calculate_base_strength(list(positions.keys()), 80.0)
            return NabhasaYoga(
                NabhasaYogaType.VAJRA, NabhasaCategory.AKRITI,
                f"Benefics in 1st/7th: {benefics_in_1_7}, Malefics in 4th/10th: {malefics_in_4_10}",
                "Happy at beginning and end of life, valorous, strong",
                True, strength, list(positions.keys()),
                sorted(set(pos['house'] for pos in positions.values()))
            )
        
        return None
    
    def detect_ishu_yoga(self) -> Optional[NabhasaYoga]:
        """BPHS: Ishu - All planets in 7th house"""
        positions = self._get_nabhasa_planet_positions()
        if len(positions) != 7:
            return None
        
        planets_in_7th = [p for p, pos in positions.items() if pos['house'] == 7]
        
        if len(planets_in_7th) != 7:
            return None
        
        strength = self._calculate_base_strength(planets_in_7th, 70.0)
        
        return NabhasaYoga(
            NabhasaYogaType.ISHU, NabhasaCategory.AKRITI,
            "All 7 planets in 7th house",
            "Quarrelsome, thievish, cruel, adulterous, merciless",
            False, strength, planets_in_7th, [7]
        )

    def detect_sakti_yoga(self) -> Optional[NabhasaYoga]:
        """BPHS: Sakti - All planets in 10th house"""
        positions = self._get_nabhasa_planet_positions()
        if len(positions) != 7:
            return None
        
        planets_in_10th = [p for p, pos in positions.items() if pos['house'] == 10]
        
        if len(planets_in_10th) != 7:
            return None
        
        strength = self._calculate_base_strength(planets_in_10th, 80.0)
        
        return NabhasaYoga(
            NabhasaYogaType.SAKTI, NabhasaCategory.AKRITI,
            "All 7 planets in 10th house",
            "Lazy, poor, diseased, indolent, mean, intent on evil",
            False, strength, planets_in_10th, [10]
        )

    def detect_danda_yoga(self) -> Optional[NabhasaYoga]:
        """BPHS: Danda - All planets in 1st house"""
        positions = self._get_nabhasa_planet_positions()
        if len(positions) != 7:
            return None
        
        planets_in_1st = [p for p, pos in positions.items() if pos['house'] == 1]
        
        if len(planets_in_1st) != 7:
            return None
        
        strength = self._calculate_base_strength(planets_in_1st, 75.0)
        
        return NabhasaYoga(
            NabhasaYogaType.DANDA, NabhasaCategory.AKRITI,
            "All 7 planets in 1st house",
            "Subjected to imprisonment, sickly, distressed, mean",
            False, strength, planets_in_1st, [1]
        )

    def detect_nava_yoga(self) -> Optional[NabhasaYoga]:
        """BPHS: Nava - All planets in 9 houses (any 9 consecutive houses)"""
        positions = self._get_nabhasa_planet_positions()
        if len(positions) != 7:
            return None
        
        houses_occupied = sorted(set(pos['house'] for pos in positions.values()))
        
        # Check if planets occupy exactly 9 consecutive houses
        for start_house in range(1, 13):
            consecutive_houses = []
            for i in range(9):
                house = ((start_house + i - 1) % 12) + 1
                consecutive_houses.append(house)
            
            if set(houses_occupied).issubset(set(consecutive_houses)) and len(houses_occupied) == 9:
                strength = self._calculate_base_strength(list(positions.keys()), 60.0)
                return NabhasaYoga(
                    NabhasaYogaType.NAVA, NabhasaCategory.AKRITI,
                    f"All planets in 9 consecutive houses: {houses_occupied}",
                    "Kingly, famous, happy, pleasure-loving, virtuous",
                    True, strength, list(positions.keys()), houses_occupied
                )
        
        return None

    def detect_kuta_yoga(self) -> Optional[NabhasaYoga]:
        """BPHS: Kuta - All planets in 1st and 7th houses"""
        positions = self._get_nabhasa_planet_positions()
        if len(positions) != 7:
            return None
        
        planets_in_1_7 = [p for p, pos in positions.items() 
                        if pos['house'] in {1, 7}]
        
        if len(planets_in_1_7) != 7:
            return None
        
        houses = sorted(set(pos['house'] for pos in positions.values()))
        if set(houses) != {1, 7}:
            return None
        
        strength = self._calculate_base_strength(planets_in_1_7, 65.0)
        
        return NabhasaYoga(
            NabhasaYogaType.KUTA, NabhasaCategory.AKRITI,
            "All planets in 1st and 7th houses",
            "Liar, jailer, cruel, given to base acts",
            False, strength, planets_in_1_7, [1, 7]
        )

    def detect_chhatra_yoga(self) -> Optional[NabhasaYoga]:
        """BPHS: Chhatra - All planets in 1st and 7th houses (variant interpretation)"""
        positions = self._get_nabhasa_planet_positions()
        if len(positions) != 7:
            return None
        
        # Alternative: planets in 1st, 4th, 7th, 10th (kendras) making umbrella shape
        kendra_count = len([p for p, pos in positions.items() 
                        if pos['house'] in self.KENDRA_HOUSES])
        
        if kendra_count == 7:
            strength = self._calculate_base_strength(list(positions.keys()), 80.0)
            return NabhasaYoga(
                NabhasaYogaType.CHHATRA, NabhasaCategory.AKRITI,
                "Planets forming umbrella pattern in kendras",
                "Happy in middle and later life, helpful to others",
                True, strength, list(positions.keys()), 
                sorted(set(pos['house'] for pos in positions.values()))
            )
        
        return None

    def detect_chapa_yoga(self) -> Optional[NabhasaYoga]:
        """BPHS: Chapa (Bow) - Planets in 1st to 6th houses forming arc"""
        positions = self._get_nabhasa_planet_positions()
        if len(positions) != 7:
            return None
        
        first_half_houses = {1, 2, 3, 4, 5, 6}
        planets_in_first_half = [p for p, pos in positions.items() 
                            if pos['house'] in first_half_houses]
        
        if len(planets_in_first_half) == 7:
            houses = sorted(set(pos['house'] for pos in positions.values()))
            strength = self._calculate_base_strength(planets_in_first_half, 70.0)
            
            return NabhasaYoga(
                NabhasaYogaType.CHAPA, NabhasaCategory.AKRITI,
                f"All planets in first 6 houses: {houses}",
                "Brave, famous, king, victorious in war",
                True, strength, planets_in_first_half, houses
            )
        
        return None
    
    def detect_yava_yoga(self) -> Optional[NabhasaYoga]:
        """BPHS: Yava - Benefics in 4th & 10th, malefics in 1st & 7th"""
        positions = self._get_nabhasa_planet_positions()
        if len(positions) != 7:
            return None
        
        benefics_in_4_10 = [p for p, pos in positions.items() 
                        if p in self.BENEFIC_PLANETS and pos['house'] in {4, 10}]
        malefics_in_1_7 = [p for p, pos in positions.items() 
                        if p in self.MALEFIC_PLANETS and pos['house'] in {1, 7}]
        
        if (len(benefics_in_4_10) >= 2 and len(malefics_in_1_7) >= 2 and 
            len(benefics_in_4_10) + len(malefics_in_1_7) == 7):
            
            strength = self._calculate_base_strength(list(positions.keys()), 70.0)
            return NabhasaYoga(
                NabhasaYogaType.YAVA, NabhasaCategory.AKRITI,
                f"Benefics in 4th/10th: {benefics_in_4_10}, Malefics in 1st/7th: {malefics_in_1_7}",
                "Happiness in middle age, charitable, religious observances",
                True, strength, list(positions.keys()),
                sorted(set(pos['house'] for pos in positions.values()))
            )
        
        return None

    def detect_sringataka_yoga(self) -> Optional[NabhasaYoga]:
        """BPHS: Sringataka - Planets in three kendras"""
        positions = self._get_nabhasa_planet_positions()
        if len(positions) != 7:
            return None
        
        kendra_houses_occupied = set()
        for pos in positions.values():
            if pos['house'] in self.KENDRA_HOUSES:
                kendra_houses_occupied.add(pos['house'])
        
        planets_in_kendras = [p for p, pos in positions.items() 
                            if pos['house'] in self.KENDRA_HOUSES]
        
        if len(kendra_houses_occupied) == 3 and len(planets_in_kendras) == 7:
            strength = self._calculate_base_strength(planets_in_kendras, 75.0)
            return NabhasaYoga(
                NabhasaYogaType.SRINGATAKA, NabhasaCategory.AKRITI,
                f"All planets in 3 kendras: {sorted(kendra_houses_occupied)}",
                "Pleasure-loving, virtuous, kind-hearted, wealthy",
                True, strength, planets_in_kendras, sorted(kendra_houses_occupied)
            )
        
        return None

    def detect_hala_yoga(self) -> Optional[NabhasaYoga]:
        """BPHS: Hala - Planets in movable signs"""
        positions = self._get_nabhasa_planet_positions()
        if len(positions) != 7:
            return None
        
        planets_in_movable = [p for p, pos in positions.items() 
                            if pos['sign'] in self.MOVABLE_SIGNS]
        
        if len(planets_in_movable) == 7:
            houses = sorted(set(pos['house'] for pos in positions.values()))
            strength = self._calculate_base_strength(planets_in_movable, 70.0)
            
            return NabhasaYoga(
                NabhasaYogaType.HALA, NabhasaCategory.AKRITI,
                "All planets in movable signs",
                "Agricultural profession, poor, servile, eaten by others",
                False, strength, planets_in_movable, houses
            )
        
        return None

    # SANKHYA YOGAS
    def detect_vallaki_yoga(self) -> Optional[NabhasaYoga]:
        """
        BPHS: Vallaki Yoga - All 7 planets in 7 different houses
        Effect: Wealthy, vehicle owner, happy, charitable
        """
        positions = self._get_nabhasa_planet_positions()
        if len(positions) != 7:
            return None
        
        houses_occupied = [pos['house'] for pos in positions.values()]
        unique_houses = set(houses_occupied)
        
        if len(unique_houses) != 7:
            return None
        
        strength = self._calculate_base_strength(list(positions.keys()), 50.0)
        
        return NabhasaYoga(
            yoga_type=NabhasaYogaType.VALLAKI,
            category=NabhasaCategory.SANKHYA,
            description=f"All 7 planets in 7 different houses: {', '.join(map(str, sorted(unique_houses)))}",
            effect="Wealthy, owns vehicles, happy disposition, charitable nature",
            is_benefic=True,
            strength_score=strength,
            planets_involved=list(positions.keys()),
            houses_involved=sorted(unique_houses)
        )
    
    def detect_damini_yoga(self) -> Optional[NabhasaYoga]:
        """
        BPHS: Damini Yoga - All 7 planets in 6 different houses
        Effect: Learned, wealthy, skilled in arts, virtuous
        """
        positions = self._get_nabhasa_planet_positions()
        if len(positions) != 7:
            return None
        
        houses_occupied = [pos['house'] for pos in positions.values()]
        unique_houses = set(houses_occupied)
        
        if len(unique_houses) != 6:
            return None
        
        strength = self._calculate_base_strength(list(positions.keys()), 48.0)
        
        return NabhasaYoga(
            yoga_type=NabhasaYogaType.DAMINI,
            category=NabhasaCategory.SANKHYA,
            description=f"All 7 planets in 6 different houses: {', '.join(map(str, sorted(unique_houses)))}",
            effect="Learned, wealthy, skilled in arts, virtuous, good advisor",
            is_benefic=True,
            strength_score=strength,
            planets_involved=list(positions.keys()),
            houses_involved=sorted(unique_houses)
        )
    
    def detect_pasa_yoga(self) -> Optional[NabhasaYoga]:
        """
        BPHS: Pasa Yoga - All 7 planets in 5 different houses
        Effect: Ethical wealth, enjoys friends and servants
        """
        positions = self._get_nabhasa_planet_positions()
        if len(positions) != 7:
            return None
        
        houses_occupied = [pos['house'] for pos in positions.values()]
        unique_houses = set(houses_occupied)
        
        if len(unique_houses) != 5:
            return None
        
        strength = self._calculate_base_strength(list(positions.keys()), 45.0)
        
        return NabhasaYoga(
            yoga_type=NabhasaYogaType.PASA,
            category=NabhasaCategory.SANKHYA,
            description=f"All 7 planets in 5 different houses: {', '.join(map(str, sorted(unique_houses)))}",
            effect="Ethical in making wealth, enjoys friends, relatives and servants",
            is_benefic=True,
            strength_score=strength,
            planets_involved=list(positions.keys()),
            houses_involved=sorted(unique_houses)
        )
    
    def detect_kedara_yoga(self) -> Optional[NabhasaYoga]:
        """
        BPHS: Kedara Yoga - All 7 planets in 4 different houses
        Effect: Fond of agriculture, possesses properties, charitable
        """
        positions = self._get_nabhasa_planet_positions()
        if len(positions) != 7:
            return None
        
        houses_occupied = [pos['house'] for pos in positions.values()]
        unique_houses = set(houses_occupied)
        
        if len(unique_houses) != 4:
            return None
        
        strength = self._calculate_base_strength(list(positions.keys()), 42.0)
        
        return NabhasaYoga(
            yoga_type=NabhasaYogaType.KEDARA,
            category=NabhasaCategory.SANKHYA,
            description=f"All 7 planets in 4 different houses: {', '.join(map(str, sorted(unique_houses)))}",
            effect="Fond of agriculture, possesses properties, charitable, earth-related gains",
            is_benefic=True,
            strength_score=strength,
            planets_involved=list(positions.keys()),
            houses_involved=sorted(unique_houses)
        )
    
    def detect_sula_yoga(self) -> Optional[NabhasaYoga]:
        """
        BPHS: Sula Yoga - All 7 planets in 3 different houses
        Effect: Devoid of wealth, courageous, cruel, battle wounds
        """
        positions = self._get_nabhasa_planet_positions()
        if len(positions) != 7:
            return None
        
        houses_occupied = [pos['house'] for pos in positions.values()]
        unique_houses = set(houses_occupied)
        
        if len(unique_houses) != 3:
            return None
        
        # This is generally considered malefic
        strength = self._calculate_base_strength(list(positions.keys()), 25.0)
        
        return NabhasaYoga(
            yoga_type=NabhasaYogaType.SULA,
            category=NabhasaCategory.SANKHYA,
            description=f"All 7 planets in 3 different houses: {', '.join(map(str, sorted(unique_houses)))}",
            effect="Devoid of wealth, courageous, cruel nature, marks of wounds, struggles",
            is_benefic=False,
            strength_score=strength,
            planets_involved=list(positions.keys()),
            houses_involved=sorted(unique_houses)
        )
    
    def detect_yuga_yoga(self) -> Optional[NabhasaYoga]:
        """
        BPHS: Yuga Yoga - All 7 planets in 2 different houses
        Effect: Poor, ostracized by society, heretical
        """
        positions = self._get_nabhasa_planet_positions()
        if len(positions) != 7:
            return None
        
        houses_occupied = [pos['house'] for pos in positions.values()]
        unique_houses = set(houses_occupied)
        
        if len(unique_houses) != 2:
            return None
        
        # This is generally considered malefic
        strength = self._calculate_base_strength(list(positions.keys()), 20.0)
        
        return NabhasaYoga(
            yoga_type=NabhasaYogaType.YUGA,
            category=NabhasaCategory.SANKHYA,
            description=f"All 7 planets in 2 different houses: {', '.join(map(str, sorted(unique_houses)))}",
            effect="Poor, ostracized by society, heretical views, social struggles",
            is_benefic=False,
            strength_score=strength,
            planets_involved=list(positions.keys()),
            houses_involved=sorted(unique_houses)
        )
    
    def detect_gola_yoga(self) -> Optional[NabhasaYoga]:
        """
        BPHS: Gola Yoga - All 7 planets in 1 house
        Effect: Indigent, dependent on others, miserable
        """
        positions = self._get_nabhasa_planet_positions()
        if len(positions) != 7:
            return None
        
        houses_occupied = [pos['house'] for pos in positions.values()]
        unique_houses = set(houses_occupied)
        
        if len(unique_houses) != 1:
            return None
        
        # This is generally considered malefic
        strength = self._calculate_base_strength(list(positions.keys()), 15.0)
        
        return NabhasaYoga(
            yoga_type=NabhasaYogaType.GOLA,
            category=NabhasaCategory.SANKHYA,
            description=f"All 7 planets in 1 house: {list(unique_houses)[0]}",
            effect="Indigent, dependent on others, miserable, concentrated energy",
            is_benefic=False,
            strength_score=strength,
            planets_involved=list(positions.keys()),
            houses_involved=list(unique_houses)
        )
    
    # ASRAYA YOGAS
    def detect_rajju_yoga(self) -> Optional[NabhasaYoga]:
        """
        BPHS: Rajju Yoga - All 7 planets in movable signs (1,4,7,10)
        Effect: Fond of wandering, charming, good health, fortunate in distant places
        """
        positions = self._get_nabhasa_planet_positions()
        if len(positions) != 7:
            return None
        
        planets_in_movable = [p for p, pos in positions.items() 
                            if pos['sign'] in self.MOVABLE_SIGNS]
        
        if len(planets_in_movable) != 7:
            return None
        
        signs_occupied = list(set(pos['sign'] for pos in positions.values()))
        strength = self._calculate_base_strength(planets_in_movable, 40.0)
        
        return NabhasaYoga(
            yoga_type=NabhasaYogaType.RAJJU,
            category=NabhasaCategory.ASRAYA,
            description=f"All 7 planets in movable signs: {', '.join(map(str, sorted(signs_occupied)))}",
            effect="Fond of wandering, charming personality, good health, fortunate in distant places",
            is_benefic=True,
            strength_score=strength,
            planets_involved=planets_in_movable,
            houses_involved=[]
        )
    
    def detect_musala_yoga(self) -> Optional[NabhasaYoga]:
        """
        BPHS: Musala Yoga - All 7 planets in fixed signs (2,5,8,11)
        Effect: Stubborn, wealthy, proud, stable, fixed in purpose
        """
        positions = self._get_nabhasa_planet_positions()
        if len(positions) != 7:
            return None
        
        planets_in_fixed = [p for p, pos in positions.items() 
                          if pos['sign'] in self.FIXED_SIGNS]
        
        if len(planets_in_fixed) != 7:
            return None
        
        signs_occupied = list(set(pos['sign'] for pos in positions.values()))
        strength = self._calculate_base_strength(planets_in_fixed, 45.0)
        
        return NabhasaYoga(
            yoga_type=NabhasaYogaType.MUSALA,
            category=NabhasaCategory.ASRAYA,
            description=f"All 7 planets in fixed signs: {', '.join(map(str, sorted(signs_occupied)))}",
            effect="Stubborn nature, wealthy, proud, stable, fixed in purpose, enduring",
            is_benefic=True,
            strength_score=strength,
            planets_involved=planets_in_fixed,
            houses_involved=[]
        )
    
    def detect_nala_yoga(self) -> Optional[NabhasaYoga]:
        """
        BPHS: Nala Yoga - All 7 planets in dual signs (3,6,9,12)
        Effect: Changeable, versatile, skilled in many arts
        """
        positions = self._get_nabhasa_planet_positions()
        if len(positions) != 7:
            return None
        
        planets_in_dual = [p for p, pos in positions.items() 
                         if pos['sign'] in self.DUAL_SIGNS]
        
        if len(planets_in_dual) != 7:
            return None
        
        signs_occupied = list(set(pos['sign'] for pos in positions.values()))
        strength = self._calculate_base_strength(planets_in_dual, 35.0)
        
        return NabhasaYoga(
            yoga_type=NabhasaYogaType.NALA,
            category=NabhasaCategory.ASRAYA,
            description=f"All 7 planets in dual signs: {', '.join(map(str, sorted(signs_occupied)))}",
            effect="Changeable nature, versatile, skilled in many arts, adaptable",
            is_benefic=True,
            strength_score=strength,
            planets_involved=planets_in_dual,
            houses_involved=[]
        )
    
    # DALA YOGAS
    def detect_srik_yoga(self) -> Optional[NabhasaYoga]:
        """
        BPHS: Srik (Mala) Yoga - All 7 planets in the first 7 houses (1-7)
        Effect: Virtuous, wealthy, learned, many wives/relationships
        """
        positions = self._get_nabhasa_planet_positions()
        if len(positions) != 7:
            return None
        
        planets_in_first_half = [p for p, pos in positions.items() 
                               if pos['house'] <= 7]
        
        if len(planets_in_first_half) != 7:
            return None
        
        houses_occupied = list(set(pos['house'] for pos in positions.values()))
        strength = self._calculate_base_strength(planets_in_first_half, 50.0)
        
        return NabhasaYoga(
            yoga_type=NabhasaYogaType.SRIK,
            category=NabhasaCategory.DALA,
            description=f"All 7 planets in first 7 houses: {', '.join(map(str, sorted(houses_occupied)))}",
            effect="Virtuous, wealthy, learned, many relationships, garland of virtues",
            is_benefic=True,
            strength_score=strength,
            planets_involved=planets_in_first_half,
            houses_involved=houses_occupied
        )
    
    def detect_sarpa_yoga(self) -> Optional[NabhasaYoga]:
        """
        BPHS: Sarpa Yoga - All 7 planets in the last 6 houses (7-12)
        Effect: Miserable, cruel, sinful, dependent on others
        """
        positions = self._get_nabhasa_planet_positions()
        if len(positions) != 7:
            return None
        
        planets_in_last_six = [p for p, pos in positions.items() 
                             if pos['house'] >= 7]
        
        if len(planets_in_last_six) != 7:
            return None
        
        houses_occupied = list(set(pos['house'] for pos in positions.values()))
        strength = self._calculate_base_strength(planets_in_last_six, 25.0)
        
        return NabhasaYoga(
            yoga_type=NabhasaYogaType.SARPA,
            category=NabhasaCategory.DALA,
            description=f"All 7 planets in last 6 houses: {', '.join(map(str, sorted(houses_occupied)))}",
            effect="Miserable, cruel nature, sinful tendencies, dependent on others",
            is_benefic=False,
            strength_score=strength,
            planets_involved=planets_in_last_six,
            houses_involved=houses_occupied
        )
    
    def detect_all_yogas(self) -> List[NabhasaYoga]:
        """Detect all Nabhasa yogas with proper precedence rules."""
        yoga_methods = [
            # Akriti Yogas
            self.detect_kamala_yoga,
            self.detect_vapi_yoga,
            self.detect_samudra_yoga,
            self.detect_yupa_yoga,
            self.detect_ishu_yoga,
            self.detect_sakti_yoga,
            self.detect_danda_yoga,
            self.detect_nava_yoga,
            self.detect_kuta_yoga,
            self.detect_chhatra_yoga,
            self.detect_chapa_yoga,
            self.detect_ardha_chandra_yoga,
            self.detect_chakra_yoga,
            self.detect_gada_yoga,
            self.detect_sakata_yoga,
            self.detect_vihaga_yoga,
            self.detect_vajra_yoga,
            self.detect_yava_yoga,
            self.detect_sringataka_yoga,
            self.detect_hala_yoga,
            
            # Sankhya Yogas
            self.detect_vallaki_yoga,
            self.detect_damini_yoga,
            self.detect_pasa_yoga,
            self.detect_kedara_yoga,
            self.detect_sula_yoga,
            self.detect_yuga_yoga,
            self.detect_gola_yoga,
            
            # Asraya Yogas
            self.detect_rajju_yoga,
            self.detect_musala_yoga,
            self.detect_nala_yoga,
            
            # Dala Yogas
            self.detect_srik_yoga,
            self.detect_sarpa_yoga,
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
        
        # Apply BPHS precedence rules
        # yogas = self._apply_precedence_rules(yogas)
        
        self.detected_yogas = sorted(yogas, key=lambda x: x.strength_score, reverse=True)
        return self.detected_yogas
    
    def _apply_precedence_rules(self, yogas: List[NabhasaYoga]) -> List[NabhasaYoga]:
        """
        Apply BPHS precedence rules with enhanced logic:
        1. Akriti yogas have highest precedence - they cancel Sankhya and Asraya
        2. Dala yogas cancel Sankhya yogas when both are present
        3. Asraya yogas are cancelled by Akriti but can coexist with others
        4. Among same category yogas, stronger ones may overshadow weaker ones
        5. Some yogas can coexist if they don't conflict in formation logic
        """
        if not yogas:
            return yogas
        
        # Group yogas by category
        category_groups = {
            NabhasaCategory.AKRITI: [],
            NabhasaCategory.SANKHYA: [],
            NabhasaCategory.ASRAYA: [],
            NabhasaCategory.DALA: []
        }
        
        for yoga in yogas:
            category_groups[yoga.category].append(yoga)
        
        final_yogas = []
        
        # Rule 1: If Akriti yogas exist, they take precedence
        if category_groups[NabhasaCategory.AKRITI]:
            akriti_yogas = category_groups[NabhasaCategory.AKRITI]
            
            # Add all Akriti yogas (multiple can coexist as per BPHS)
            final_yogas.extend(akriti_yogas)
            
            # Akriti cancels Sankhya yogas completely
            category_groups[NabhasaCategory.SANKHYA] = []
            
            # Akriti also cancels Asraya yogas
            category_groups[NabhasaCategory.ASRAYA] = []
            
            # Dala yogas can coexist with Akriti in some interpretations
            # but classical texts suggest Akriti dominates
            if category_groups[NabhasaCategory.DALA]:
                # Keep only the strongest Dala yoga if any
                strongest_dala = max(category_groups[NabhasaCategory.DALA], 
                                key=lambda x: x.strength_score)
                if strongest_dala.strength_score > 70:  # Only very strong Dala yogas survive
                    final_yogas.append(strongest_dala)
        
        else:
            # No Akriti yogas present, apply other rules
            
            # Rule 2: Dala yogas cancel Sankhya yogas
            if (category_groups[NabhasaCategory.DALA] and 
                category_groups[NabhasaCategory.SANKHYA]):
                category_groups[NabhasaCategory.SANKHYA] = []
            
            # Add remaining yogas
            for category in [NabhasaCategory.DALA, NabhasaCategory.SANKHYA, NabhasaCategory.ASRAYA]:
                if category_groups[category]:
                    # For multiple yogas in same category, apply strength-based filtering
                    category_yogas = category_groups[category]
                    
                    if len(category_yogas) == 1:
                        final_yogas.extend(category_yogas)
                    else:
                        # Multiple yogas in same category - keep based on strength and compatibility
                        category_yogas.sort(key=lambda x: x.strength_score, reverse=True)
                        
                        if category == NabhasaCategory.SANKHYA:
                            # For Sankhya yogas, typically only one should exist
                            # as they're based on number of houses occupied
                            final_yogas.append(category_yogas[0])
                        
                        elif category == NabhasaCategory.ASRAYA:
                            # Asraya yogas can coexist if they represent different qualities
                            # Check for logical conflicts
                            final_yogas.extend(self._filter_compatible_asraya_yogas(category_yogas))
                        
                        elif category == NabhasaCategory.DALA:
                            # Dala yogas are mutually exclusive (odd/even house distribution)
                            final_yogas.append(category_yogas[0])
        
        # Final strength-based filtering within each category
        # final_yogas = self._apply_strength_based_filtering(final_yogas)
        
        return final_yogas
    
    def _get_strength_based_interpretation_modifier(self, strength_score: float) -> str:
        """Get interpretation modifier based on yoga strength."""
        if strength_score >= 80:
            return "exceptionally strong"
        elif strength_score >= 60:
            return "strong"
        elif strength_score >= 40:
            return "moderate"
        elif strength_score >= 25:
            return "weak but present"
        else:
            return "very weak"

    def _get_yoga_timing_effects(self, yoga: NabhasaYoga) -> str:
        """Get timing-based effects of the yoga."""
        if yoga.category == NabhasaCategory.AKRITI:
            return "Effects manifest throughout life, stronger in middle and later years"
        elif yoga.category == NabhasaCategory.SANKHYA:
            return "Effects vary with planetary periods, stronger during related planet dashas"
        elif yoga.category == NabhasaCategory.ASRAYA:
            return "Effects manifest based on sign lord periods and transits"
        elif yoga.category == NabhasaCategory.DALA:
            return "Effects present throughout life with periodic intensification"
        else:
            return "Timing effects require individual analysis"
    
    def get_yoga_interpretation(self, yoga: NabhasaYoga) -> Dict[str, str]:
        """
        Get comprehensive interpretation of a Nabhasa yoga based on BPHS principles.
        Enhanced with traditional effects, modern applications, and strength considerations.
        """
        base_interpretations = {
            # AKRITI YOGAS (Most auspicious category)
            NabhasaYogaType.KAMALA: {
                'meaning': 'Lotus Formation - Divine blessing, ultimate auspiciousness',
                'traditional_effect': 'Becomes ruler of earth, enjoys all pleasures, righteous, long-lived',
                'characteristics': 'Pure character, spiritual wisdom, natural leadership, magnetic personality',
                'career': 'High government positions, spiritual leadership, royalty, philanthropy, divine service',
                'wealth': 'Abundant wealth from righteous sources, royal treasures, charitable nature',
                'relationships': 'Universally loved and respected, harmonious family life, divine spouse',
                'health': 'Excellent health, long life, natural healing abilities',
                'spirituality': 'High spiritual attainment, divine grace, possible incarnation of divinity',
                'challenges': 'May face tests of character, responsibility of power, expectations of perfection',
                'remedies': 'Lotus meditation, white flower offerings, service to divine causes'
            },
            
            NabhasaYogaType.VAPI: {
                'meaning': 'Well Formation - Source of resources and sustenance',
                'traditional_effect': 'Accumulates wealth like a well holds water, generous, righteous',
                'characteristics': 'Practical wisdom, resource consciousness, patient accumulation, reliability',
                'career': 'Banking, finance, resource management, agriculture, water-related businesses',
                'wealth': 'Steady wealth accumulation, property ownership, savings consciousness',
                'relationships': 'Supportive of family needs, reliable friend, provider mentality',
                'health': 'Good vitality, may need attention to water balance in body',
                'spirituality': 'Devotion through service, practical dharma, community welfare',
                'challenges': 'May become overly attached to material security, hoarding tendencies',
                'remedies': 'Water conservation, well maintenance, charity of water and food'
            },
            
            NabhasaYogaType.SAMUDRA: {
                'meaning': 'Ocean Formation - Boundless resources and magnanimity',
                'traditional_effect': 'Wealth like ocean, commands armies, enjoys royal pleasures',
                'characteristics': 'Magnanimous nature, vast thinking, generous heart, influential presence',
                'career': 'Large enterprises, international business, maritime activities, mass leadership',
                'wealth': 'Ocean-like wealth - vast, deep, ever-flowing, multiple income sources',
                'relationships': 'Wide social influence, patron to many, international connections',
                'health': 'Strong constitution, may need to manage excess and indulgence',
                'spirituality': 'Universal compassion, large-scale dharmic activities, guru potential',
                'challenges': 'Overwhelming responsibilities, difficulty in discrimination, excess tendencies',
                'remedies': 'Ocean worship, large-scale charity, protection of water bodies'
            },
            
            NabhasaYogaType.YUPA: {
                'meaning': 'Sacrificial Post Formation - Religious merit and ceremonial importance',
                'traditional_effect': 'Performs sacrifices, religious inclination, respected by learned',
                'characteristics': 'Religious devotion, ceremonial mindset, traditional values, ritual expertise',
                'career': 'Religious leadership, ceremonial roles, traditional arts, spiritual guidance',
                'wealth': 'Wealth through religious activities, donations, ceremonial services',
                'relationships': 'Respected in religious circles, traditional family values',
                'health': 'Benefits from religious practices, disciplined lifestyle',
                'spirituality': 'Strong ritual practice, traditional path, religious authority',
                'challenges': 'May be rigid in beliefs, orthodox tendencies, ceremonial burdens',
                'remedies': 'Regular yajnas, traditional worship, support to religious institutions'
            },
            
            NabhasaYogaType.ISHU: {
                'meaning': 'Arrow Formation - Sharp focus and targeted achievement',
                'traditional_effect': 'Swift in action, achieves targets, skilled in warfare/competition',
                'characteristics': 'Sharp intellect, focused approach, quick decision-making, goal-oriented',
                'career': 'Military, sports, competitive fields, precision work, strategic roles',
                'wealth': 'Quick gains through skill and precision, competitive earnings',
                'relationships': 'Direct communication, loyal friends, may lack diplomatic skills',
                'health': 'Good reflexes, may be prone to accidents, needs stress management',
                'spirituality': 'One-pointed devotion, sharp discrimination, rapid spiritual progress',
                'challenges': 'Impatience, harsh speech, may hurt others unintentionally',
                'remedies': 'Archery practice, worship of sharp weapons, patience cultivation'
            },
            
            NabhasaYogaType.SAKTI: {
                'meaning': 'Spear Formation - Divine power and piercing ability',
                'traditional_effect': 'Destroys enemies, powerful personality, achieves difficult tasks',
                'characteristics': 'Dynamic power, penetrating insight, transformative abilities, fearless nature',
                'career': 'Surgery, research, investigation, transformative work, power positions',
                'wealth': 'Wealth through overcoming obstacles, breakthrough achievements',
                'relationships': 'Protective of loved ones, may intimidate others, transformative influence',
                'health': 'Strong healing power, ability to overcome diseases, robust constitution',
                'spirituality': 'Tantric inclinations, goddess worship, transformative practices',
                'challenges': 'Aggressive tendencies, making enemies, destructive potential if misused',
                'remedies': 'Goddess worship, martial arts with discipline, anger management'
            },
            
            NabhasaYogaType.DANDA: {
                'meaning': 'Staff Formation - Authority and disciplinary power',
                'traditional_effect': 'Holds authority like a king\'s staff, maintains discipline, punishes wrongdoers',
                'characteristics': 'Natural authority, disciplined approach, justice-oriented, systematic nature',
                'career': 'Administration, law enforcement, judiciary, management, organizational leadership',
                'wealth': 'Steady income through position and authority, structured finances',
                'relationships': 'Respected but may be feared, maintains family discipline',
                'health': 'Benefits from disciplined lifestyle, strong backbone and posture',
                'spirituality': 'Disciplined practice, guru potential, dharmic authority',
                'challenges': 'May be too strict, authoritarian tendencies, inflexibility',
                'remedies': 'Regular meditation, softening practices, service to justice'
            },
            
            # AKRITI YOGAS (continuing the auspicious category)
            NabhasaYogaType.NAVA: {
                'meaning': 'Ship Formation - Navigation through life\'s waters with skill',
                'traditional_effect': 'Earns through water-related activities, skilled navigator, travels across waters',
                'characteristics': 'Navigational skills, adaptability to change, practical wisdom, seafaring nature',
                'career': 'Maritime industry, navigation, fishing, water transport, import-export, travel',
                'wealth': 'Wealth through water-related ventures, shipping, overseas trade, fluid income',
                'relationships': 'Guides others through difficulties, reliable in stormy times, international connections',
                'health': 'Benefits from water therapies, good balance, may need attention to fluid balance',
                'spirituality': 'Spiritual journey like crossing ocean of samsara, pilgrimages across water',
                'challenges': 'May face storms in life, dependency on external conditions, motion sickness',
                'remedies': 'Boat donations, water body protection, navigation deity worship'
            },
            
            NabhasaYogaType.KUTA: {
                'meaning': 'Hill Formation - Steady elevation and natural leadership',
                'traditional_effect': 'Dwells in hills, wealthy, owns lands, respected leader, stable position',
                'characteristics': 'Natural elevation in society, steady growth, solid foundation, leadership qualities',
                'career': 'Real estate, mining, hill station development, leadership positions, elevated roles',
                'wealth': 'Land-based wealth, property in elevated areas, steady accumulation, solid investments',
                'relationships': 'Elevated social position, respected in community, stable family foundation',
                'health': 'Benefits from higher altitudes, strong constitution, grounded health approach',
                'spirituality': 'Mountain meditation, steady spiritual practice, reaching spiritual heights',
                'challenges': 'May become rigid like mountain, slow to adapt, isolation tendencies',
                'remedies': 'Mountain pilgrimage, land conservation, worship of mountain deities'
            },
            
            NabhasaYogaType.CHHATRA: {
                'meaning': 'Umbrella Formation - Protection and royal authority',
                'traditional_effect': 'Protects others like umbrella, enjoys royal status, respected leader',
                'characteristics': 'Protective nature, authority with responsibility, sheltering others, dignified presence',
                'career': 'Government service, protective services, insurance, leadership roles, royal positions',
                'wealth': 'Wealth with responsibility to protect others, royal income, authority-based earnings',
                'relationships': 'Protector of family and community, people seek shelter under guidance',
                'health': 'Natural immunity, protective health measures, benefits from covering/protection',
                'spirituality': 'Divine protection, guru qualities, spiritual authority, protective mantras',
                'challenges': 'Burden of protecting others, responsibility stress, authoritarian tendencies',
                'remedies': 'Umbrella donations, protection of vulnerable, worship of protective deities'
            },
            
            NabhasaYogaType.CHAPA: {
                'meaning': 'Bow Formation - Flexibility with strength and distant reach',
                'traditional_effect': 'Skilled in archery and warfare, defeats enemies from distance, strategic mind',
                'characteristics': 'Strategic thinking, flexibility with strength, long-range planning, warrior spirit',
                'career': 'Military strategy, sports coaching, archery, long-term planning, strategic consulting',
                'wealth': 'Gains through strategic investments, long-term wealth building, competitive earnings',
                'relationships': 'Maintains distance initially, loyal once committed, protective of loved ones',
                'health': 'Good flexibility and strength, benefits from archery/stretching, spinal health',
                'spirituality': 'Disciplined practice, target-oriented spiritual goals, devotion to warrior deities',
                'challenges': 'May keep others at distance, overly strategic in relationships, tension issues',
                'remedies': 'Archery practice, bow donations, worship of Arjuna or warrior deities'
            },
            
            NabhasaYogaType.ARDHA_CHANDRA: {
                'meaning': 'Half Moon Formation - Partial fulfillment and cyclic nature',
                'traditional_effect': 'Partial success, changeable fortune, emotional nature, lunar influence',
                'characteristics': 'Cyclical patterns, emotional depth, partial achievements, waxing-waning fortunes',
                'career': 'Moon-related activities, emotional counseling, tidal businesses, cyclic industries',
                'wealth': 'Fluctuating wealth, lunar cycles affect income, emotional spending patterns',
                'relationships': 'Emotional relationships, caring nature, may have mood swings affecting bonds',
                'health': 'Health fluctuates with lunar cycles, emotional health important, water balance',
                'spirituality': 'Lunar worship, emotional devotion, meditation on moon phases',
                'challenges': 'Incomplete achievements, mood fluctuations, emotional instability',
                'remedies': 'Moon worship, Monday fasting, pearl wearing, emotional balance practices'
            },
            
            NabhasaYogaType.CHAKRA: {
                'meaning': 'Wheel Formation - Continuous motion and worldly involvement',
                'traditional_effect': 'Always in motion, widespread influence, mechanical mind, circular thinking',
                'characteristics': 'Dynamic movement, widespread activities, mechanical aptitude, cyclical thinking',
                'career': 'Transportation, machinery, circular/repetitive work, wheel-based industries',
                'wealth': 'Wealth through movement and machinery, transportation income, cyclical gains',
                'relationships': 'Wide circle of contacts, constantly meeting new people, revolving friendships',
                'health': 'Benefits from regular movement, circular exercises, may suffer from dizziness',
                'spirituality': 'Chakra meditation, wheel symbolism, dharma wheel understanding',
                'challenges': 'Constant restlessness, going in circles, lack of linear progress',
                'remedies': 'Wheel donations, supporting transportation, Vishnu chakra meditation'
            },
            
            NabhasaYogaType.GADA: {
                'meaning': 'Mace Formation - Blunt force and straightforward approach',
                'traditional_effect': 'Powerful personality, direct approach, destroys obstacles, warrior nature',
                'characteristics': 'Direct communication, powerful impact, obstacle removal, straightforward nature',
                'career': 'Heavy machinery, demolition, direct sales, powerful positions, physical work',
                'wealth': 'Wealth through direct means, powerful earnings, obstacle-breaking income',
                'relationships': 'Direct in relationships, powerful presence, may overwhelm sensitive people',
                'health': 'Strong constitution, benefits from weight training, powerful healing capacity',
                'spirituality': 'Hanuman worship, strength-based practices, powerful mantras',
                'challenges': 'Too direct/blunt, may hurt others, heavy-handed approach',
                'remedies': 'Hanuman worship, mace donations, strength used for protection'
            },
            
            NabhasaYogaType.SAKATA: {
                'meaning': 'Cart Formation - Practical utility but dependent on others',
                'traditional_effect': 'Serves others, dependent nature, practical but not leadership, modest life',
                'characteristics': 'Service orientation, practical utility, dependent on others, modest lifestyle',
                'career': 'Service industries, transportation services, utility work, support roles',
                'wealth': 'Modest earnings through service, practical savings, utility-based income',
                'relationships': 'Supportive role in relationships, practical help to others, modest social position',
                'health': 'Practical health approach, may bear burdens affecting health, service improves health',
                'spirituality': 'Karma yoga, service to others, practical spirituality, humble devotion',
                'challenges': 'Over-dependence on others, burden-bearing, lack of independence',
                'remedies': 'Service to others, cart/vehicle donations, independence-building practices'
            },
            
            NabhasaYogaType.VIHAGA: {
                'meaning': 'Bird Formation - Freedom-loving and elevated perspective',
                'traditional_effect': 'Loves freedom, elevated thoughts, may migrate frequently, aerial perspective',
                'characteristics': 'Freedom-loving, elevated thinking, migration tendencies, broad perspective',
                'career': 'Aviation, bird-related work, freedom-oriented careers, elevated positions',
                'wealth': 'Free-flowing wealth, may not accumulate, income from elevated sources',
                'relationships': 'Values freedom in relationships, may avoid commitment, elevated connections',
                'health': 'Benefits from fresh air, elevated places, freedom of movement',
                'spirituality': 'Bird symbolism, freedom in spiritual practice, elevated consciousness',
                'challenges': 'Difficulty with commitment, restless nature, may lack groundedness',
                'remedies': 'Bird feeding, protection of birds, grounding practices with freedom'
            },
            
            NabhasaYogaType.VAJRA: {
                'meaning': 'Diamond/Thunderbolt Formation - Indestructible strength with divine power',
                'traditional_effect': 'Indestructible like diamond, powerful personality, divine protection, leadership',
                'characteristics': 'Unbreakable will, brilliant mind, divine strength, invincible nature',
                'career': 'Diamond industry, electrical work, indestructible materials, powerful positions',
                'wealth': 'Brilliant wealth, indestructible investments, diamond-like valuable possessions',
                'relationships': 'Unbreakable loyalty, brilliant relationships, may be too intense for some',
                'health': 'Indestructible health, brilliant recovery, benefits from diamond/crystal therapy',
                'spirituality': 'Vajrayana practices, Indra worship, indestructible devotion, brilliant realization',
                'challenges': 'May be too intense, inflexible like diamond, overwhelming presence',
                'remedies': 'Diamond donations, Indra worship, softening practices with strength'
            },
            
            NabhasaYogaType.YAVA: {
                'meaning': 'Barley Formation - Nourishment and steady growth',
                'traditional_effect': 'Provides nourishment to others, steady growth, agricultural success, practical wisdom',
                'characteristics': 'Nourishing nature, steady development, practical approach, agricultural mindset',
                'career': 'Agriculture, food industry, nutrition, steady growth businesses, nourishment services',
                'wealth': 'Steady agricultural wealth, nourishment-based income, practical investments',
                'relationships': 'Nourishing to family and friends, practical support, steady relationships',
                'health': 'Benefits from proper nutrition, steady health practices, barley-based diet',
                'spirituality': 'Offering of grains, nourishing others as spiritual practice, steady devotion',
                'challenges': 'May be too practical, slow growth, lack of excitement',
                'remedies': 'Grain donations, feeding the hungry, agricultural support'
            },
            
            NabhasaYogaType.SRINGATAKA: {
                'meaning': 'Ornamental Formation - Decorative nature and artistic expression',
                'traditional_effect': 'Artistic nature, decorative skills, beautiful appearance, creative expression',
                'characteristics': 'Artistic talents, aesthetic sense, decorative abilities, beautiful expression',
                'career': 'Arts and crafts, decoration, jewelry, beauty industry, creative fields',
                'wealth': 'Wealth through artistic work, beautiful possessions, ornamental investments',
                'relationships': 'Brings beauty to relationships, artistic connections, attractive personality',
                'health': 'Benefits from beautiful environment, artistic therapy, aesthetic healing',
                'spirituality': 'Devotion through arts, beautiful worship, aesthetic spiritual practices',
                'challenges': 'May be too focused on appearance, superficial tendencies, vanity',
                'remedies': 'Art donations, temple decoration, inner beauty cultivation'
            },
            
            NabhasaYogaType.HALA: {
                'meaning': 'Plough Formation - Agricultural foundation and hard work',
                'traditional_effect': 'Agricultural success, hard working, foundation builder, earth connection',
                'characteristics': 'Hard working nature, foundation building, agricultural wisdom, earth connection',
                'career': 'Agriculture, construction, foundation work, earth-based industries, hard labor',
                'wealth': 'Wealth through hard work, agricultural income, foundation-based investments',
                'relationships': 'Builds strong relationship foundations, hard working for family, reliable',
                'health': 'Benefits from hard work, earth connection, agricultural lifestyle',
                'spirituality': 'Work as worship, earth-based practices, foundation spiritual disciplines',
                'challenges': 'May overwork, too focused on material foundation, body strain',
                'remedies': 'Plough donations, agricultural charity, balanced work and rest'
            },

            # SANKHYA YOGAS
            NabhasaYogaType.VALLAKI: {
                'meaning': 'Creeper Formation - Steady growth and adaptable prosperity',
                'traditional_effect': 'Happy, wealthy, owns conveyances, charitable, helps relatives',
                'characteristics': 'Adaptable growth, networking abilities, progressive mindset, helpful nature',
                'career': 'Business expansion, franchising, network marketing, growth-oriented ventures',
                'wealth': 'Gradual but steady wealth accumulation, multiple income streams',
                'relationships': 'Extensive network, supportive of extended family, social climber',
                'health': 'Adaptable constitution, benefits from natural remedies, green environment',
                'spirituality': 'Growing devotion, community-based practice, charitable inclinations',
                'challenges': 'May spread too thin, dependency on others, lack of deep roots',
                'remedies': 'Plant care, supporting growth of others, environmental conservation'
            },
            
            NabhasaYogaType.DAMINI: {
                'meaning': 'Lightning Formation - Brilliant flashes of insight and skill',
                'traditional_effect': 'Learned, skilled in arts, quick-witted, respected for knowledge',
                'characteristics': 'Brilliant intelligence, artistic talents, quick learning, innovative thinking',
                'career': 'Arts, education, innovation, consulting, creative fields, knowledge work',
                'wealth': 'Income through talents and knowledge, intellectual property, teaching',
                'relationships': 'Admired for brilliance, inspiring to others, may lack patience with slower minds',
                'health': 'Quick recovery, sharp senses, may have nervous system sensitivity',
                'spirituality': 'Jnana yoga inclination, quick spiritual insights, philosophical bent',
                'challenges': 'Impatience with others, pride in intelligence, inconsistent energy',
                'remedies': 'Regular study, sharing knowledge freely, patience practices'
            },
            
            NabhasaYogaType.PASA: {
                'meaning': 'Noose Formation - Binding through service and loyalty',
                'traditional_effect': 'Serving nature, bound by duties, loyal to superiors, ethical conduct',
                'characteristics': 'Service orientation, loyal nature, ethical conduct, duty-bound mentality',
                'career': 'Civil service, healthcare, social work, support roles, ethical businesses',
                'wealth': 'Modest but steady income, benefits from serving others, ethical earnings',
                'relationships': 'Loyal friend, devoted family member, trusted confidant',
                'health': 'Benefits from service to others, karma yoga for health',
                'spirituality': 'Karma yoga path, devotional service, ethical living',
                'challenges': 'May become bound by duties, difficulty saying no, exploitation by others',
                'remedies': 'Balanced service, setting boundaries, worship of duty deities'
            },
            
            NabhasaYogaType.KEDARA: {
                'meaning': 'Cultivated Field Formation - Fertile ground for growth and prosperity',
                'traditional_effect': 'Agricultural prosperity, landed property, earthy wisdom, nurturing nature',
                'characteristics': 'Practical wisdom, nurturing abilities, patience, connection to earth',
                'career': 'Agriculture, real estate, earth sciences, nutrition, sustainable development',
                'wealth': 'Land-based wealth, agricultural income, property investments, natural resources',
                'relationships': 'Nurturing family environment, community connections, earth-based wisdom',
                'health': 'Benefits from natural lifestyle, earth connection, organic nutrition',
                'spirituality': 'Nature-based spirituality, earth worship, sustainable dharma',
                'challenges': 'May be too materialistic, slow to change, overly conservative',
                'remedies': 'Land conservation, organic farming support, earth-based rituals'
            },
            
            NabhasaYogaType.SULA: {
                'meaning': 'Trident Formation - Sharp but destructive power',
                'traditional_effect': 'Cruel nature, creates conflicts, financial struggles, aggressive tendencies',
                'characteristics': 'Aggressive nature, conflict-prone, sharp but destructive, impulsive actions',
                'career': 'Military, competitive sports, surgery, demolition, conflict resolution',
                'wealth': 'Irregular income, financial conflicts, gains through struggle',
                'relationships': 'Conflicted relationships, aggressive communication, dominance issues',
                'health': 'Prone to injuries, inflammatory conditions, anger-related health issues',
                'spirituality': 'Needs anger transformation, Shiva worship for balance',
                'challenges': 'Destructive tendencies, making enemies, financial instability',
                'remedies': 'Shiva worship, anger management, martial arts with discipline'
            },
            
            NabhasaYogaType.YUGA: {
                'meaning': 'Yoke Formation - Bound by circumstances, restricted freedom',
                'traditional_effect': 'Heretical views, social outcast, dependent on others, unconventional',
                'characteristics': 'Unconventional thinking, social non-conformity, dependent nature, restricted freedom',
                'career': 'Alternative fields, research, unconventional work, dependent employment',
                'wealth': 'Limited financial independence, depends on others, irregular income',
                'relationships': 'Difficulty fitting in, misunderstood by society, few close relationships',
                'health': 'May feel restricted, benefits from freedom of movement and thought',
                'spirituality': 'Unconventional spiritual path, may reject traditional religion',
                'challenges': 'Social isolation, financial dependence, feeling trapped',
                'remedies': 'Gradual social integration, developing skills, finding like-minded community'
            },
            
            NabhasaYogaType.GOLA: {
                'meaning': 'Sphere Formation - Concentrated but limited influence',
                'traditional_effect': 'Very limited resources, depends on others, restricted sphere of influence',
                'characteristics': 'Concentrated focus, limited scope, dependent nature, introspective',
                'career': 'Specialized work, research, contemplative roles, limited public interaction',
                'wealth': 'Very limited wealth, depends on others for support, minimal material needs',
                'relationships': 'Few but deep relationships, difficulty with large groups',
                'health': 'May need support from others, benefits from concentrated healing approaches',
                'spirituality': 'Intense but narrow spiritual focus, contemplative practices',
                'challenges': 'Extreme limitation, dependency on others, lack of worldly success',
                'remedies': 'Gradual expansion of activities, skill development, community support'
            },
            
            # ASRAYA YOGAS
            NabhasaYogaType.RAJJU: {
                'meaning': 'Rope Formation - Mobility and distant connections',
                'traditional_effect': 'Fond of travel, gains from foreign lands, restless nature, charming personality',
                'characteristics': 'Mobile nature, adaptability, charm, international outlook, restless energy',
                'career': 'Travel industry, international business, transportation, foreign services',
                'wealth': 'Gains from distant places, foreign income, mobile assets, travel-related earnings',
                'relationships': 'Relationships across distances, charming personality, many acquaintances',
                'health': 'Benefits from movement and change, may suffer from restlessness',
                'spirituality': 'Pilgrimage inclination, learning from various traditions, mobile practices',
                'challenges': 'Lack of stability, difficulty settling down, superficial relationships',
                'remedies': 'Regular travel for spiritual purposes, grounding practices, stable routines'
            },
            
            NabhasaYogaType.MUSALA: {
                'meaning': 'Pestle Formation - Fixed determination and pride',
                'traditional_effect': 'Proud nature, fixed in opinions, wealthy, respects traditions, stubborn',
                'characteristics': 'Strong determination, pride, traditional values, stubborn nature, fixed opinions',
                'career': 'Established businesses, traditional industries, family enterprises, conservative fields',
                'wealth': 'Stable accumulated wealth, fixed assets, inheritance, traditional investments',
                'relationships': 'Long-term commitments, family pride, traditional relationships',
                'health': 'Strong constitution, benefits from consistent routines, may have rigid habits',
                'spirituality': 'Traditional religious practices, ancestor worship, established paths',
                'challenges': 'Excessive pride, inflexibility, resistance to change, orthodox views',
                'remedies': 'Humility practices, flexibility exercises, respect for all paths'
            },
            
            NabhasaYogaType.NALA: {
                'meaning': 'Reed Formation - Flexibility and versatility',
                'traditional_effect': 'Changeable nature, multiple skills, adaptable, good communication',
                'characteristics': 'Versatile nature, good communication, adaptable, multi-talented, changeable',
                'career': 'Media, communication, consulting, multiple careers, versatile professions',
                'wealth': 'Variable income, multiple sources, gains through versatility and communication',
                'relationships': 'Many acquaintances, adaptable in relationships, good social skills',
                'health': 'Adaptable constitution, benefits from variety, may lack consistency',
                'spirituality': 'Explores various paths, good at explaining concepts, teaching abilities',
                'challenges': 'Lack of focus, inconsistency, difficulty with commitment, scattered energy',
                'remedies': 'Concentration practices, choosing focus areas, commitment exercises'
            },
            
            # DALA YOGAS
            NabhasaYogaType.SRIK: {
                'meaning': 'Garland Formation - Beauty, virtue, and multiple relationships',
                'traditional_effect': 'Virtuous, learned, attractive, wealth, multiple marriages possible',
                'characteristics': 'Attractive personality, virtuous nature, learned, social grace, magnetic charm',
                'career': 'Education, counseling, beauty industry, social work, advisory roles',
                'wealth': 'Good wealth through righteous means, gifts from others, beauty-related income',
                'relationships': 'Attractive to others, multiple relationships, social popularity',
                'health': 'Generally good health, attractive appearance, may need to guard against vanity',
                'spirituality': 'Devotional practices, service to others, dharmic living',
                'challenges': 'Multiple relationship complications, vanity, too many social obligations',
                'remedies': 'Focused relationships, inner beauty cultivation, spiritual practices'
            },
            
            NabhasaYogaType.SARPA: {
                'meaning': 'Serpent Formation - Hidden wisdom but troublesome nature',
                'traditional_effect': 'Secretive, revengeful, miserable, gains through questionable means',
                'characteristics': 'Secretive nature, hidden knowledge, vengeful tendencies, mysterious personality',
                'career': 'Investigation, research, occult sciences, behind-the-scenes work, secret services',
                'wealth': 'Hidden wealth, secretive financial dealings, gains through mysterious means',
                'relationships': 'Trust issues, secretive in relationships, tendency toward revenge',
                'health': 'Hidden health issues, benefits from detoxification, snake-related symbolism',
                'spirituality': 'Occult practices, tantric knowledge, hidden spiritual powers',
                'challenges': 'Vengeful nature, trust issues, secretive tendencies, making enemies',
                'remedies': 'Snake deity worship, forgiveness practices, transparency cultivation'
            }
        }
        
        # Get base interpretation
        interpretation = base_interpretations.get(yoga.yoga_type, {
            'meaning': 'Rare yoga formation requiring individual analysis',
            'traditional_effect': 'Mixed results based on planetary positions and strengths',
            'characteristics': 'Unique personality traits requiring detailed study',
            'career': 'Varied career possibilities based on planetary combinations',
            'wealth': 'Financial patterns depend on planetary strengths and aspects',
            'relationships': 'Relationship patterns require individual chart analysis',
            'health': 'Health tendencies vary with planetary positions',
            'spirituality': 'Spiritual path determined by individual planetary factors',
            'challenges': 'Specific challenges require detailed chart analysis',
            'remedies': 'Remedies should be determined based on individual planetary positions'
        })
        
        # Enhance interpretation based on yoga strength
        strength_modifier = self._get_strength_based_interpretation_modifier(yoga.strength_score)
        
        # Add strength-based modifications
        enhanced_interpretation = interpretation.copy()
        
        if yoga.strength_score >= 80:
            enhanced_interpretation['strength_note'] = "Very strong yoga - effects will be pronounced and beneficial"
        elif yoga.strength_score >= 60:
            enhanced_interpretation['strength_note'] = "Strong yoga - clear positive effects expected"
        elif yoga.strength_score >= 40:
            enhanced_interpretation['strength_note'] = "Moderate yoga - effects present but may be mixed"
        else:
            enhanced_interpretation['strength_note'] = "Weak yoga - subtle effects, may need supporting factors"
        
        # Add benefic/malefic nature
        enhanced_interpretation['nature'] = "Benefic yoga bringing positive results" if yoga.is_benefic else "Challenging yoga requiring careful handling"
        
        # Add timing considerations
        enhanced_interpretation['timing'] = self._get_yoga_timing_effects(yoga)
        
        return enhanced_interpretation
    
    def _filter_compatible_asraya_yogas(self, asraya_yogas: List[NabhasaYoga]) -> List[NabhasaYoga]:
        """Filter Asraya yogas for compatibility - some combinations are impossible."""
        if len(asraya_yogas) <= 1:
            return asraya_yogas
        
        # Rajju (movable), Musala (fixed), and Nala (dual) are mutually exclusive
        # as all planets cannot be in multiple sign qualities simultaneously
        yoga_types = [yoga.yoga_type for yoga in asraya_yogas]
        
        # If multiple Asraya yogas detected, there might be an error in detection
        # Keep the strongest one
        return [max(asraya_yogas, key=lambda x: x.strength_score)]

    def _apply_strength_based_filtering(self, yogas: List[NabhasaYoga]) -> List[NabhasaYoga]:
        """Apply final strength-based filtering to remove very weak yogas."""
        if not yogas:
            return yogas
        
        # Remove yogas with very low strength (below threshold)
        min_strength_threshold = 25.0
        filtered_yogas = [yoga for yoga in yogas if yoga.strength_score >= min_strength_threshold]
        
        # If all yogas are below threshold, keep the strongest one
        if not filtered_yogas and yogas:
            filtered_yogas = [max(yogas, key=lambda x: x.strength_score)]
        
        return filtered_yogas
    
    def print_yoga_summary(self, yogas: List[NabhasaYoga] = None) -> None:
        """Print detailed summary of all detected Nabhasa yogas."""
        if yogas is None:
            yogas = self.detect_all_yogas()
        
        print("=" * 90)
        print("NABHASA YOGA DETECTION SUMMARY")
        print("=" * 90)
        print(f"Total Nabhasa Yogas Detected: {len(yogas)}")
        print()
        
        if not yogas:
            print("No Nabhasa Yogas detected in this chart.")
            print("\nNote: Nabhasa yogas require all 7 classical planets (Sun, Moon, Mars, Mercury,")
            print("Jupiter, Venus, Saturn) to be positioned in specific configurations.")
            return
        
        # Group by category
        yoga_by_category = {
            NabhasaCategory.AKRITI: [],
            NabhasaCategory.SANKHYA: [],
            NabhasaCategory.ASRAYA: [],
            NabhasaCategory.DALA: []
        }
        
        for yoga in yogas:
            yoga_by_category[yoga.category].append(yoga)
        
        # Print by category with detailed interpretations
        category_headers = {
            NabhasaCategory.AKRITI: "AKRITI YOGAS (Shape-based formations)",
            NabhasaCategory.SANKHYA: "SANKHYA YOGAS (Number-based formations)",
            NabhasaCategory.ASRAYA: "ASRAYA YOGAS (Sign quality-based formations)",
            NabhasaCategory.DALA: "DALA YOGAS (Hemisphere-based formations)"
        }
        
        category_descriptions = {
            NabhasaCategory.AKRITI: "Based on planetary distribution across house types (Kendra, Panapara, Apoklima)",
            NabhasaCategory.SANKHYA: "Based on number of houses occupied by all planets",
            NabhasaCategory.ASRAYA: "Based on planetary distribution across sign qualities (Movable, Fixed, Dual)",
            NabhasaCategory.DALA: "Based on planetary distribution across chart hemispheres"
        }
        
        for category, header in category_headers.items():
            category_yogas = yoga_by_category[category]
            if category_yogas:
                print(f"\n{header}")
                print("-" * len(header))
                print(f"Description: {category_descriptions[category]}")
                print()
                
                for i, yoga in enumerate(category_yogas, 1):
                    print(f"{i}. {yoga.yoga_type.value.upper()} YOGA")
                    print(f"   Status: {'✓ BENEFIC' if yoga.is_benefic else '✗ MALEFIC'}")
                    print(f"   Strength Score: {yoga.strength_score:.1f}/100")
                    
                    # NEW: Add formation details
                    print(f"\n   🔹 YOGA FORMATION:")
                    print(f"      How it's formed: {yoga.description}")
                    if yoga.planets_involved:
                        print(f"      Planets Involved: {', '.join(yoga.planets_involved)}")
                    if yoga.houses_involved:
                        print(f"      Houses Involved: {', '.join(map(str, yoga.houses_involved))}")
                    
                    # NEW: Add classical effects prominently
                    print(f"\n   🔹 CLASSICAL EFFECTS:")
                    print(f"      Traditional Result: {yoga.effect}")
                    
                    # Get detailed interpretation
                    interpretation = self.get_yoga_interpretation(yoga)
                    print(f"\n   🔹 DETAILED INTERPRETATION:")
                    print(f"      Meaning: {interpretation['meaning']}")
                    print(f"      Key Characteristics: {interpretation['characteristics']}")
                    print(f"      Career Indicators: {interpretation['career']}")
                    print(f"      Wealth Patterns: {interpretation['wealth']}")
                    print(f"      Relationship Tendencies: {interpretation['relationships']}")
                    print(f"      Health Implications: {interpretation['health']}")
                    print(f"      Spiritual Inclinations: {interpretation['spirituality']}")
                    
                    # NEW: Add challenges and remedies
                    if 'challenges' in interpretation:
                        print(f"      Potential Challenges: {interpretation['challenges']}")
                    if 'remedies' in interpretation:
                        print(f"      Suggested Remedies: {interpretation['remedies']}")
                    
                    print()
        
        # Enhanced summary statistics
        benefic_yogas = [y for y in yogas if y.is_benefic]
        malefic_yogas = [y for y in yogas if not y.is_benefic]
        
        print("\n" + "=" * 90)
        print("NABHASA YOGA ANALYSIS SUMMARY")
        print("=" * 90)
        print(f"Total Yogas Detected: {len(yogas)}")
        print(f"Benefic Yogas: {len(benefic_yogas)} {'✓' if benefic_yogas else ''}")
        print(f"Malefic Yogas: {len(malefic_yogas)} {'⚠' if malefic_yogas else ''}")
        
        if yogas:
            avg_strength = sum(y.strength_score for y in yogas) / len(yogas)
            strongest_yoga = max(yogas, key=lambda x: x.strength_score)
            weakest_yoga = min(yogas, key=lambda x: x.strength_score)
            print(f"Average Strength Score: {avg_strength:.1f}/100")
            print(f"Strongest Yoga: {strongest_yoga.yoga_type.value.title()} (Score: {strongest_yoga.strength_score:.1f})")
            if len(yogas) > 1:
                print(f"Weakest Yoga: {weakest_yoga.yoga_type.value.title()} (Score: {weakest_yoga.strength_score:.1f})")
        
        # NEW: Category-wise breakdown
        print(f"\nCategory-wise Distribution:")
        for category, header in category_headers.items():
            count = len(yoga_by_category[category])
            if count > 0:
                category_name = header.split('(')[0].strip()
                print(f"• {category_name}: {count} yoga{'s' if count > 1 else ''}")
        
        print(f"\n🔹 OVERALL LIFE PATTERN ANALYSIS:")
        if len(benefic_yogas) > len(malefic_yogas):
            print("✓ Predominantly positive Nabhasa influence in the chart")
            print("• Life patterns strongly favor prosperity, virtue, and success")
            print("• Natural tendency toward beneficial outcomes and positive recognition")
            if malefic_yogas:
                print("• Minor challenges present but overshadowed by positive influences")
        elif len(malefic_yogas) > len(benefic_yogas):
            print("⚠ Challenging Nabhasa patterns detected")
            print("• Life may involve significant struggles and obstacles")
            print("• Character development through adversity and hardship")
            print("• Success requires extra effort and proper remedial measures")
        else:
            print("⚖ Balanced Nabhasa influences")
            print("• Mixed life experiences with both opportunities and challenges")
            print("• Success depends on conscious choices and proper guidance")
        
        # NEW: Add strength-based interpretation
        if yogas:
            high_strength_yogas = [y for y in yogas if y.strength_score >= 80]
            medium_strength_yogas = [y for y in yogas if 60 <= y.strength_score < 80]
            low_strength_yogas = [y for y in yogas if y.strength_score < 60]
            
            print(f"\n🔹 YOGA STRENGTH ANALYSIS:")
            if high_strength_yogas:
                print(f"• High Strength Yogas ({len(high_strength_yogas)}): Strong manifestation expected")
            if medium_strength_yogas:
                print(f"• Medium Strength Yogas ({len(medium_strength_yogas)}): Moderate manifestation")
            if low_strength_yogas:
                print(f"• Lower Strength Yogas ({len(low_strength_yogas)}): Subtle influence, may need activation")
        
        print(f"\n🔹 IMPORTANT NOTES:")
        print("• Nabhasa yogas represent broad life patterns and general tendencies")
        print("• They work alongside individual planetary positions, aspects, and other yogas")
        print("• Higher strength scores indicate more prominent manifestation")
        print("• Remedial measures can enhance positive yogas and mitigate challenging ones")
        print("• Consult with qualified astrologer for personalized guidance")
        print("\n" + "=" * 90)

# Usage example:
# detector = NabhasaYogaDetector(planet_data_objs, house_data_objs)
# nabhasa_yogas = detector.detect_all_yogas()
# detector.print_yoga_summary(nabhasa_yogas)