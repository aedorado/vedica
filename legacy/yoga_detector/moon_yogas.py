from typing import Dict, List, Optional, Any, Set
from dataclasses import dataclass
from enum import Enum

import logging
logger = logging.getLogger(__name__)

class MoonYogaType(Enum):
    GAJAKESARI = "gajakesari"
    SUNAPHA = "sunapha"
    ANAPHA = "anapha"
    DURDHURA = "durdhura"
    KEMADRUMA = "kemadruma"
    CHANDRA_MANGALA = "chandra_mangala"
    ADHI = "adhi"
    VASUMATI = "vasumati"
    RAJALAKSHANA = "rajalakshana"
    SAKATA = "sakata"
    AMALA = "amala"

@dataclass
class MoonYoga:
    yoga_type: MoonYogaType
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

class MoonYogaDetector:
    """Detects lunar yogas based on Brihat Parashara Hora Shastra principles."""
    
    # Only include classical planets (no Rahu/Ketu for most yogas)
    BENEFIC_PLANETS = {'Jupiter', 'Venus', 'Mercury', 'Moon'}
    MALEFIC_PLANETS = {'Mars', 'Saturn', 'Sun'}
    YOGA_PLANETS = {'Mars', 'Mercury', 'Jupiter', 'Venus', 'Saturn'}  # Excluding Sun for Sunapha/Anapha
    
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
    
    def _is_aspected_by_benefics(self, planet_name) -> bool:
        """Check if planet is aspected by benefics"""
        planet_detail = self.planet_data.get(planet_name)
        if not planet_detail:
            return False
        val = planet_detail.get('IsPlanetAspectedByBeneficPlanets', False)
        return val == "True" or val == True
    
    def _is_kendra_relation(self, house1: int, house2: int) -> bool:
        """Check if houses are in Kendra relation (1, 4, 7, 10) or mutual aspect."""
        distance = self._house_distance(house1, house2)
        return distance in {1, 4, 7, 10}
    
    def _has_mutual_aspect(self, house1: int, house2: int) -> bool:
        """Check if planets in two houses have mutual 7th house aspect."""
        distance = self._house_distance(house1, house2)
        return distance == 7
    
    def detect_gajakesari_yoga(self) -> Optional[MoonYoga]:
        """
        BPHS: Jupiter in Kendra (1st, 4th, 7th, 10th) from Moon or mutual aspect
        Effect: Bestows intelligence, eloquence, skill, longevity, and royal favor
        """
        moon_house = self._get_planet_house('Moon')
        jupiter_house = self._get_planet_house('Jupiter')
        
        if not moon_house or not jupiter_house:
            return None
        
        is_kendra = self._is_kendra_relation(moon_house, jupiter_house)
        is_mutual_aspect = self._has_mutual_aspect(moon_house, jupiter_house)
        
        if not (is_kendra or is_mutual_aspect):
            return None
        
        # Calculate strength based on dignity and formation type
        strength = 65.0 if is_kendra else 55.0  # Kendra is stronger than aspect
        jupiter_detail = self.planet_data.get('Jupiter', {})
        if (jupiter_detail.get('IsPlanetExaltedSign', False) == "True" or 
            jupiter_detail.get('IsPlanetExaltedSign', False) == True):
            strength += 25.0
        elif (jupiter_detail.get('IsPlanetInOwnSign', False) == "True" or 
              jupiter_detail.get('IsPlanetInOwnSign', False) == True):
            strength += 15.0
        
        formation = "Kendra relation" if is_kendra else "mutual aspect"
        
        return MoonYoga(
            yoga_type=MoonYogaType.GAJAKESARI,
            description=f"Jupiter in House {jupiter_house} in {formation} with Moon in House {moon_house}",
            effect="Grants wisdom, wealth, fame, virtuous nature, and respect in society",
            is_benefic=True,
            strength_score=strength,
            planets_involved=['Moon', 'Jupiter'],
            houses_involved=[moon_house, jupiter_house]
        )
    
    def detect_sunapha_yoga(self) -> Optional[MoonYoga]:
        """
        BPHS: Any planet (except Sun) in 2nd house from Moon
        Effect: Self-made wealth, learning, famous, virtuous, and intelligent
        """
        moon_house = self._get_planet_house('Moon')
        if not moon_house:
            return None
            
        second_house = (moon_house % 12) + 1
        planets_in_second = [p for p in self._get_planets_in_house(second_house) 
                           if p in self.YOGA_PLANETS]
        
        if not planets_in_second:
            return None
        
        benefic_count = sum(1 for p in planets_in_second if p in self.BENEFIC_PLANETS)
        strength = 30.0 + (benefic_count * 10.0) - ((len(planets_in_second) - benefic_count) * 5.0)
        
        return MoonYoga(
            yoga_type=MoonYogaType.SUNAPHA,
            description=f"Planets {', '.join(planets_in_second)} in 2nd house from Moon",
            effect="Self-earned wealth, intelligence, good reputation, and material comforts",
            is_benefic=True,
            strength_score=max(strength, 15.0),
            planets_involved=['Moon'] + planets_in_second,
            houses_involved=[moon_house, second_house]
        )
    
    def detect_anapha_yoga(self) -> Optional[MoonYoga]:
        """
        BPHS: Any planet (except Sun) in 12th house from Moon
        Effect: Well-formed organs, material happiness, renown, and enjoyment
        """
        moon_house = self._get_planet_house('Moon')
        if not moon_house:
            return None
            
        twelfth_house_from_moon = ((moon_house - 2) % 12) + 1
        planets_in_twelfth = [p for p in self._get_planets_in_house(twelfth_house_from_moon) 
                             if p in self.YOGA_PLANETS]
        
        if not planets_in_twelfth:
            return None
        
        benefic_count = sum(1 for p in planets_in_twelfth if p in self.BENEFIC_PLANETS)
        strength = 25.0 + (benefic_count * 8.0) - ((len(planets_in_twelfth) - benefic_count) * 4.0)

        m = MoonYoga(
            yoga_type=MoonYogaType.ANAPHA,
            description=f"Planets {', '.join(planets_in_twelfth)} in 12th house from Moon",
            effect="Material happiness, good health, fame, and enjoyment of pleasures",
            is_benefic=True,
            strength_score=max(strength, 15.0),
            planets_involved=['Moon'] + planets_in_twelfth,
            houses_involved=[moon_house, twelfth_house_from_moon]
        )
        return m
    
    def detect_durdhura_yoga(self) -> Optional[MoonYoga]:
        """
        BPHS: Planets (except Sun) in both 2nd and 12th from Moon
        Effect: Combines benefits of Sunapha and Anapha - wealth, happiness, and fame
        """
        moon_house = self._get_planet_house('Moon')
        if not moon_house:
            return None
            
        second_house = (moon_house % 12) + 1
        twelfth_house = ((moon_house - 2) % 12) + 1
        
        planets_in_second = [p for p in self._get_planets_in_house(second_house) 
                           if p in self.YOGA_PLANETS]
        planets_in_twelfth = [p for p in self._get_planets_in_house(twelfth_house) 
                             if p in self.YOGA_PLANETS]
        
        if not planets_in_second or not planets_in_twelfth:
            return None
        
        all_planets = planets_in_second + planets_in_twelfth
        benefic_count = sum(1 for p in all_planets if p in self.BENEFIC_PLANETS)
        strength = 45.0 + (benefic_count * 12.0) - ((len(all_planets) - benefic_count) * 6.0)
        
        return MoonYoga(
            yoga_type=MoonYogaType.DURDHURA,
            description=f"Planets in 2nd ({', '.join(planets_in_second)}) and 12th ({', '.join(planets_in_twelfth)}) from Moon",
            effect="Enjoys vehicle comforts, is liberal, learned, wealthy, and famous",
            is_benefic=True,
            strength_score=max(strength, 25.0),
            planets_involved=['Moon'] + all_planets,
            houses_involved=[moon_house, second_house, twelfth_house]
        )
    
    def detect_kemadruma_yoga(self) -> Optional[MoonYoga]:
        """
        Kemadruma Yoga (BPHS):
        - Forms when no planet (excluding Sun) is in 2nd or 12th from Moon,
        and Moon is neither conjunct nor aspected by other planets.
        - Causes mental disturbance, poverty, isolation.
        - Cancellations occur via various placements/aspects.
        """
        moon_house = self._get_planet_house('Moon')
        if not moon_house:
            return None

        # Core Yoga Condition
        second_from_moon = (moon_house % 12) + 1
        twelfth_from_moon = ((moon_house - 2) % 12) + 1

        # Exclude Sun from check
        planets_2nd = [p for p in self._get_planets_in_house(second_from_moon) if p != 'Sun']
        planets_12th = [p for p in self._get_planets_in_house(twelfth_from_moon) if p != 'Sun']

        # If there are planets in either house, yoga doesn't form
        if planets_2nd or planets_12th:
            return None

        cancellation_reasons = []

        # 1. Moon in Kendra from Lagna
        if moon_house in {1, 4, 7, 10}:
            cancellation_reasons.append("Moon in Kendra from Lagna")

        # 2. Any planet conjunct Moon (except nodes and Sun)
        moon_conjunct = [p for p in self._get_planets_in_house(moon_house) if p != 'Moon']
        if moon_conjunct:
            cancellation_reasons.append(f"Moon is conjunct {', '.join(moon_conjunct)}")

        # 3. Moon aspected by benefics (simplified)
        if self._is_aspected_by_benefics('Moon'):
            cancellation_reasons.append("Moon is aspected by benefics")

        # 4. Any planet in Kendra from Moon (1, 4, 7, 10 from Moon)
        kendra_from_moon = {
            ((moon_house - 1 + offset) % 12) + 1
            for offset in [0, 3, 6, 9]
        }
        for kendra_house in kendra_from_moon:
            if self._get_planets_in_house(kendra_house):
                cancellation_reasons.append(f"Planet in Kendra from Moon (House {kendra_house})")
                break

        # Final Decision
        is_cancelled = bool(cancellation_reasons)
        strength = -15.0 if is_cancelled else -35.0

        return MoonYoga(
            yoga_type=MoonYogaType.KEMADRUMA,
            description=(
                "Kemadruma Yoga formed due to Moon's isolation. " +
                ("Cancelled by: " + "; ".join(cancellation_reasons) if is_cancelled else "No cancellation found.")
            ),
            effect=(
                "Causes poverty, loneliness, mental instability." +
                (" Mitigated by yoga cancellation factors." if is_cancelled else "")
            ),
            is_benefic=False,
            strength_score=strength,
            planets_involved=['Moon'] + moon_conjunct,
            houses_involved=[moon_house, second_from_moon, twelfth_from_moon]
        )

    
    def detect_chandra_mangala_yoga(self) -> Optional[MoonYoga]:
        """
        BPHS: Moon and Mars together or in mutual aspect
        Effect: Wealth through land/property but can cause emotional volatility
        """
        moon_house = self._get_planet_house('Moon')
        mars_house = self._get_planet_house('Mars')
        
        if not moon_house or not mars_house:
            return None
        
        # Check conjunction or 7th house aspect
        is_conjunction = moon_house == mars_house
        is_aspect = self._house_distance(moon_house, mars_house) == 7
        
        if not (is_conjunction or is_aspect):
            return None
        
        connection = "conjunction" if is_conjunction else "mutual aspect"
        strength = 40.0 if is_conjunction else 30.0
        
        return MoonYoga(
            yoga_type=MoonYogaType.CHANDRA_MANGALA,
            description=f"Moon and Mars in {connection}",
            effect="Wealth through real estate and property, but may cause emotional turbulence",
            is_benefic=True,
            strength_score=strength,
            planets_involved=['Moon', 'Mars'],
            houses_involved=[moon_house, mars_house]
        )
    
    def detect_adhi_yoga(self) -> Optional[MoonYoga]:
        """
        BPHS: Benefics (Jupiter, Venus, Mercury) in 6th, 7th, 8th from Moon
        Effect: Polite, trustworthy, easily gets wealth, enjoys happiness
        """
        moon_house = self._get_planet_house('Moon')
        if not moon_house:
            return None
            
        target_houses = [
            ((moon_house + 4) % 12) + 1,  # 6th
            ((moon_house + 5) % 12) + 1,  # 7th  
            ((moon_house + 6) % 12) + 1   # 8th
        ]
        
        benefics_found = []
        for house in target_houses:
            for planet in self._get_planets_in_house(house):
                if planet in {'Jupiter', 'Venus', 'Mercury'}:
                    benefics_found.append(planet)
        
        if not benefics_found:
            return None
        
        strength = 35.0 + (len(benefics_found) * 15.0)
        if 'Jupiter' in benefics_found:
            strength += 10.0
        
        return MoonYoga(
            yoga_type=MoonYogaType.ADHI,
            description=f"Benefic planets {', '.join(benefics_found)} in 6th/7th/8th from Moon",
            effect="Trustworthy nature, ministerial position, happiness, and easy wealth",
            is_benefic=True,
            strength_score=strength,
            planets_involved=['Moon'] + benefics_found,
            houses_involved=[moon_house] + [h for h in target_houses if self._get_planets_in_house(h)]
        )
    
    def detect_vasumati_yoga(self) -> Optional[MoonYoga]:
        """
        Vasumati Yoga:
        Benefic planets in Upachaya houses (3, 6, 10, 11) from Moon or Lagna.
        """
        moon_house = self._get_planet_house('Moon')
        lagna_house = 1  # House 1 is always Lagna

        if not moon_house:
            return None

        def get_upachaya_from(reference: int) -> Dict[int, str]:
            """Returns Upachaya house positions from reference with ordinal labels."""
            return {
                ((reference + 2 - 1) % 12) + 1: "3rd",
                ((reference + 5 - 1) % 12) + 1: "6th",
                ((reference + 9 - 1) % 12) + 1: "10th",
                ((reference + 10 - 1) % 12) + 1: "11th"
            }

        upachaya_from_moon = get_upachaya_from(moon_house)
        upachaya_from_lagna = get_upachaya_from(lagna_house)

        benefics = {}

        for house in range(1, 13):
            planets = self._get_planets_in_house(house)
            for planet in planets:
                if planet in self.BENEFIC_PLANETS and planet != 'Moon':
                    sources = []
                    if house in upachaya_from_moon:
                        sources.append(f"Moon ({upachaya_from_moon[house]})")
                    if house in upachaya_from_lagna:
                        sources.append(f"Lagna ({upachaya_from_lagna[house]})")
                    if sources:
                        benefics[planet] = {
                            'house': house,
                            'sources': sources
                        }

        if not benefics:
            return None

        lines = [
            f"{planet} in House {data['house']}, from " + " and ".join(data['sources'])
            for planet, data in benefics.items()
        ]

        description = (
            "Formation: Benefics in Upachaya (3, 6, 10, 11) from Moon or Lagna: "
            + "; ".join(lines)
        )
        strength = 30.0 + (len(benefics) * 12.0)

        return MoonYoga(
            yoga_type=MoonYogaType.VASUMATI,
            description=description,
            effect="Gradual increase in wealth, prosperity grows with age.",
            is_benefic=True,
            strength_score=strength,
            planets_involved=['Moon'] + list(benefics.keys()),
            houses_involved=[moon_house] + [data['house'] for data in benefics.values()]
        )

    def detect_sakata_yoga(self) -> Optional[MoonYoga]:
        """
        BPHS: Moon in 6th, 8th, or 12th from Jupiter
        Effect: Ups and downs in life like a cart wheel
        """
        moon_house = self._get_planet_house('Moon')
        jupiter_house = self._get_planet_house('Jupiter')
        if not moon_house or not jupiter_house:
            return None
        
        distance = self._house_distance(jupiter_house, moon_house)
        if distance not in {6, 8, 12}:
            return None
        
        # Check cancellation - Moon or Jupiter in Kendra from Lagna
        is_cancelled = moon_house in {1, 4, 7, 10} and jupiter_house in {1, 4, 7, 10}
        strength = -30.0 if not is_cancelled else -10.0
        
        position_map = {6: "6th", 8: "8th", 12: "12th"}
        
        return MoonYoga(
            yoga_type=MoonYogaType.SAKATA,
            description=f"Moon in {position_map[distance]} from Jupiter {'(Cancelled)' if is_cancelled else ''}",
            effect="Fluctuating fortunes and instability" + (" but impact reduced" if is_cancelled else ""),
            is_benefic=False,
            strength_score=strength,
            planets_involved=['Moon', 'Jupiter'],
            houses_involved=[moon_house, jupiter_house]
        )
    
    def detect_amala_yoga(self) -> Optional[MoonYoga]:
        """
        BPHS: Benefic planets in 10th house from Moon or Lagna
        Effect: Lasting fame, purity of mind, prosperity, and happiness
        """
        moon_house = self._get_planet_house('Moon')
        if not moon_house:
            return None

        tenth_from_moon = ((moon_house + 9) % 12) + 1
        tenth_from_lagna = 10

        benefics_found = []
        detailed_positions = []

        # Check 10th from Moon
        planets_tenth_moon = self._get_planets_in_house(tenth_from_moon)
        for planet in planets_tenth_moon:
            if planet in self.BENEFIC_PLANETS and planet != 'Moon':
                benefics_found.append(planet)
                detailed_positions.append(
                    f"{planet} in House {tenth_from_moon}, which is 10th from Moon"
                )

        # Check 10th from Lagna (if different)
        if tenth_from_lagna != tenth_from_moon:
            planets_tenth_lagna = self._get_planets_in_house(tenth_from_lagna)
            for planet in planets_tenth_lagna:
                if planet in self.BENEFIC_PLANETS and planet != 'Moon' and planet not in benefics_found:
                    benefics_found.append(planet)
                    detailed_positions.append(
                        f"{planet} in House {tenth_from_lagna}, which is 10th from Lagna"
                    )

        if not benefics_found:
            return None

        strength = 40.0 + (len(benefics_found) * 15.0)

        return MoonYoga(
            yoga_type=MoonYogaType.AMALA,
            description=(
                "Formation: Benefics in 10th house from Moon or Lagna: " +
                "; ".join(detailed_positions)
            ),
            effect="Lasting fame, virtuous character, prosperity, and good reputation",
            is_benefic=True,
            strength_score=strength,
            planets_involved=['Moon'] + benefics_found,
            houses_involved=[moon_house, tenth_from_moon] + ([tenth_from_lagna] if tenth_from_moon != tenth_from_lagna else [])
        )

    
    def detect_rajalakshana_yoga(self) -> Optional[MoonYoga]:
        """
        BPHS: Rajalakshana Yoga — Jupiter, Venus, Mercury, and Moon in Kendra houses (1, 4, 7, 10) from Lagna
        Effect: Graceful, wealthy, commanding presence, royal virtues and good fortune
        """
        kendra_houses = {1, 4, 7, 10}
        required_planets = {"Jupiter", "Venus", "Mercury", "Moon"}
        
        found_planets = []
        involved_houses = []
        
        for planet in required_planets:
            house = self._get_planet_house(planet)
            if not house:
                continue
            if house in kendra_houses:
                found_planets.append(planet)
                involved_houses.append(house)
        
        if len(found_planets) < 4:
            return None
        
        strength = 70.0 + (len(found_planets) * 5.0)  # modest bump for exactness
        
        return MoonYoga(
            yoga_type=MoonYogaType.RAJALAKSHANA,
            description="All four benefics (Jupiter, Venus, Mercury, Moon) are placed in Kendra houses from Lagna.",
            effect="Bestows charm, wealth, influence, and royal grace.",
            is_benefic=True,
            strength_score=strength,
            planets_involved=found_planets,
            houses_involved=involved_houses
        )


    
    def detect_all_yogas(self) -> List[MoonYoga]:
        """Detect all Moon yogas and return sorted by strength."""
        yoga_methods = [
            self.detect_gajakesari_yoga,
            self.detect_sunapha_yoga,
            self.detect_anapha_yoga,
            self.detect_durdhura_yoga,
            self.detect_kemadruma_yoga,
            self.detect_chandra_mangala_yoga,
            self.detect_adhi_yoga,
            self.detect_vasumati_yoga,
            self.detect_sakata_yoga,
            self.detect_amala_yoga,
            self.detect_rajalakshana_yoga,
        ]
        
        yogas = []
        for method in yoga_methods:
            try:
                yoga = method()
                if yoga:
                    yogas.append(yoga)
            except Exception as e:
                print(f"Error in {method.__name__}: {e}")
        
        self.detected_yogas = sorted(yogas, key=lambda x: x.strength_score, reverse=True)
        return self.detected_yogas
    
    def print_report(self) -> None:
        """Print formatted Moon Yoga report."""
        if not self.detected_yogas:
            self.detect_all_yogas()
        
        print("\n" + "="*70)
        print("MOON YOGA ANALYSIS (BPHS Based)")
        print("="*70)
        
        if not self.detected_yogas:
            print("No Moon Yogas detected.")
            return
        
        benefic_count = sum(1 for y in self.detected_yogas if y.is_benefic)
        malefic_count = len(self.detected_yogas) - benefic_count
        
        print(f"Total Yogas: {len(self.detected_yogas)} | Benefic: {benefic_count} | Malefic: {malefic_count}")
        print()
        
        for i, yoga in enumerate(self.detected_yogas, 1):
            status = "✓ BENEFIC" if yoga.is_benefic else "⚠ MALEFIC"
            print(f"{i}. {yoga.yoga_type.value.upper()} {status}")
            print(f"   Formation: {yoga.description}")
            print(f"   Effect: {yoga.effect}")
            print(f"   Strength: {yoga.strength_score:.1f}")
            print(f"   Planets: {', '.join(yoga.planets_involved)}")
            print()
        
        print("="*70)

# Example usage
def analyze_chart_yogas(planet_data: Dict[str, Any], house_data: Dict[str, Any]) -> List[MoonYoga]:
    """Analyze and return Moon yogas for a chart."""
    detector = MoonYogaDetector(planet_data, house_data)
    yogas = detector.detect_all_yogas()
    detector.print_report()
    return yogas