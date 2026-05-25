"""Getting Good Results from the Ascendant (Lagna) —

1. The lagna lord
and the Karaka of lagna (Sun)
being placed in kendra, trikona, or 2nd, 3rd or 11th house.

2. The lagna lord and Karaka (Sun) being under auspicious influence
meaning
i) auspicious conjunction
ii) auspicious aspect
iii) auspicious kartari.

3. The Karaka Sun or lagna lord being placed with the lords of kendra, trikona, or 11th house.
(Here it is necessary to pay attention to the moolatrikona sign of the lagna lord - it should not fall in Dushthanas)

4. The lagna being under auspicious influence meaning:
i) aspected by benefic planets
ii) conjoined with benefic planets
iii) auspicious kartari.

5. The lords of kendra, trikona, 2nd or 11th house
being placed in the lagna,
whose moolatrikona is also in auspicious places.

6. Where the lagna lord and significator are positioned relative to each other.

7. Where the lagna lord and Moon are positioned relative to each other.

(Note -
Position relative to each other means - 7-7, 2-12, 3-11, 4-10, 5-9 or 6-8 positions.
Here the 2-12 and 6-8 positions will not be called good
but other positions can be called good if the planets are not in the 6th, 8th, and 12th houses.)

----

Getting Inauspicious Results Related to (Lagna) —

1. The lagna lord and Karaka - Sun being placed in the 6th, 8th, and 12th houses.

2. The lagna lord and Karaka - Sun being placed with the lords of 6th, 8th, and 12th houses. Here the rules of companionship must be considered.

3. The lagna lord and Karaka - Sun being under inauspicious influence, meaning inauspicious conjunction, inauspicious aspect, and inauspicious kartari/paap kartari.

4. The lagna being under inauspicious influence, meaning aspected by malefic planets, conjoined with malefic planets. In this, it is necessary to pay attention to the moolatrikona of the planets that conjoin naturally and temporarily. Also pay attention to inauspicious kartari.

5. The lords of 6th, 8th, and 12th houses being placed in the lagna whose moolatrikona is also in inauspicious or sorrowful places.

6. The lagna lord and significator being in 2/12 and 6/8 positions relative to each other will not be called good.

7. The lagna lord and Moon being in 2/12 and 6/8 positions relative to each other will not be called good."""


from typing import Dict, List, Set, Optional, Any, Tuple
from dataclasses import dataclass
from enum import Enum
import math

class InfluenceType(Enum):
    AUSPICIOUS = "auspicious"
    INAUSPICIOUS = "inauspicious"
    NEUTRAL = "neutral"

class PositionType(Enum):
    FAVORABLE = "favorable"
    UNFAVORABLE = "unfavorable"
    NEUTRAL = "neutral"

@dataclass
class LagnaAnalysisResult:
    """Container for Lagna analysis results."""
    criterion: str
    result: bool
    score: float
    details: str
    influence_type: InfluenceType
    supporting_factors: List[str]
    detailed_explanation: str = ""
    
    def __post_init__(self):
        if not self.supporting_factors:
            self.supporting_factors = []

class LagnaAnalyzer:
    """Comprehensive Lagna analysis based on traditional principles with detailed explanations."""
    
    # House categories
    KENDRA_HOUSES = {1, 4, 7, 10}
    TRIKONA_HOUSES = {1, 5, 9}
    UPACHAYA_HOUSES = {3, 6, 10, 11}
    DUSTHANA_HOUSES = {6, 8, 12}
    FAVORABLE_HOUSES = {1, 2, 3, 4, 5, 7, 9, 10, 11}
    
    # Natural benefics and malefics
    NATURAL_BENEFICS = {'Jupiter', 'Venus', 'Mercury', 'Moon'}
    NATURAL_MALEFICS = {'Sun', 'Mars', 'Saturn', 'Rahu', 'Ketu'}
    
    # House significance
    HOUSE_SIGNIFICANCE = {
        1: "Self, personality, health, appearance",
        2: "Wealth, family, speech, values",
        3: "Courage, siblings, communication, efforts",
        4: "Home, mother, comfort, property",
        5: "Intelligence, children, creativity, education",
        6: "Enemies, diseases, debts, service",
        7: "Marriage, partnerships, business",
        8: "Longevity, transformation, hidden knowledge",
        9: "Fortune, dharma, higher learning, father",
        10: "Career, reputation, authority, status",
        11: "Gains, friends, aspirations, income",
        12: "Losses, expenses, spirituality, foreign lands"
    }
    
    # Moolatrikona signs
    MOOLATRIKONA_SIGNS = {
        'Sun': 'Leo', 'Moon': 'Taurus', 'Mars': 'Aries',
        'Mercury': 'Virgo', 'Jupiter': 'Sagittarius',
        'Venus': 'Libra', 'Saturn': 'Aquarius'
    }
    
    # Exaltation signs
    EXALTATION_SIGNS = {
        'Sun': 'Aries', 'Moon': 'Taurus', 'Mars': 'Capricorn',
        'Mercury': 'Virgo', 'Jupiter': 'Cancer',
        'Venus': 'Pisces', 'Saturn': 'Libra'
    }
    
    # Debilitation signs
    DEBILITATION_SIGNS = {
        'Sun': 'Libra', 'Moon': 'Scorpio', 'Mars': 'Cancer',
        'Mercury': 'Pisces', 'Jupiter': 'Capricorn',
        'Venus': 'Virgo', 'Saturn': 'Aries'
    }
    
    # Sign lords
    SIGN_LORDS = {
        'Aries': 'Mars', 'Taurus': 'Venus', 'Gemini': 'Mercury',
        'Cancer': 'Moon', 'Leo': 'Sun', 'Virgo': 'Mercury',
        'Libra': 'Venus', 'Scorpio': 'Mars', 'Sagittarius': 'Jupiter',
        'Capricorn': 'Saturn', 'Aquarius': 'Saturn', 'Pisces': 'Jupiter'
    }
    
    # Planetary aspects
    PLANETARY_ASPECTS = {
        'Sun': [7], 'Moon': [7], 'Mars': [4, 7, 8], 'Mercury': [7],
        'Jupiter': [5, 7, 9], 'Venus': [7], 'Saturn': [3, 7, 10],
        'Rahu': [7], 'Ketu': [7]
    }
    
    def __init__(self, planet_data: Dict[str, Any], house_data: Dict[str, Any]):
        self.planet_data = planet_data
        self.house_data = house_data
        self.house_lords = self._get_house_lords()
        self.lagna_lord = self._get_lagna_lord()
        self.lagna_sign = self._get_lagna_sign()
        self.analysis_results = []
        
    def _get_house_lords(self) -> Dict[int, str]:
        """Extract house lords from house data."""
        house_lords = {}
        for house_key, house_detail in self.house_data.items():
            house_num = int(house_key)
            lord_name = house_detail.safe_get_nested('LordOfHouse', 'Name')
            if lord_name:
                house_lords[house_num] = lord_name
        return house_lords
    
    def _get_lagna_lord(self) -> str:
        """Get the lord of the 1st house (Lagna lord)."""
        return self.house_lords.get(1, "Unknown")
    
    def _get_lagna_sign(self) -> str:
        """Get the sign of the 1st house."""
        house1_data = self.house_data.get('1')
        if house1_data:
            return house1_data.safe_get('HouseRasiSign').Name
        return "Unknown"
    
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
    
    def _get_planet_sign(self, planet_name: str) -> str:
        """Get the sign where a planet is located."""
        planet_detail = self.planet_data.get(planet_name)
        if planet_detail:
            return planet_detail.safe_get_nested('PlanetRasiD1Sign').Name
        return "Unknown"
    
    def _get_houses_ruled_by_planet(self, planet_name: str) -> List[int]:
        """Get houses ruled by a planet."""
        return [house_num for house_num, lord in self.house_lords.items() 
                if lord == planet_name]
    
    def _calculate_house_distance(self, house1: int, house2: int) -> int:
        """Calculate the distance between two houses."""
        # print(house1, house2, ((house1 - house2) % 12) + 1)
        return ((house1 - house2) % 12) + 1 if house1 != house2 else 1
    
    def _get_relative_position(self, house1: int, house2: int) -> str:
        """Get relative position description between two houses."""
        if house1 == house2:
            return "same house"
        
        distance = self._calculate_house_distance(house1, house2)
        reverse_distance = self._calculate_house_distance(house2, house1)
        
        position_names = {
            2: "2nd", 3: "3rd", 4: "4th", 5: "5th", 6: "6th",
            7: "7th", 8: "8th", 9: "9th", 10: "10th", 11: "11th", 12: "12th"
        }
        
        return f"{position_names.get(distance, str(distance))} from each other ({distance}-{reverse_distance})"
    
    def _is_position_favorable(self, house1: int, house2: int) -> bool:
        """Check if relative position between two houses is favorable."""
        if house1 == house2:
            return True
        
        distance = self._calculate_house_distance(house1, house2)
        reverse_distance = self._calculate_house_distance(house2, house1)
        
        # Favorable positions: 7th, 3rd-11th, 4th-10th, 5th-9th
        # Unfavorable: 2nd-12th, 6th-8th
        favorable_pairs = {(3, 11), (4, 10), (5, 9), (7, 7)}
        unfavorable_pairs = {(2, 12), (6, 8)}
        
        current_pair = tuple(sorted([distance, reverse_distance]))
        
        if current_pair in unfavorable_pairs:
            return False
        elif current_pair in favorable_pairs or distance == 7:
            return house1 not in self.DUSTHANA_HOUSES and house2 not in self.DUSTHANA_HOUSES
        
        return True
    
    def _get_planets_aspecting_house(self, house_num: int) -> List[Tuple[str, List[int]]]:
        """Get planets aspecting a specific house with their aspect numbers."""
        aspecting_planets = []
        
        for planet_name, planet_detail in self.planet_data.items():
            planet_house = self._get_planet_house_number(planet_name)
            if planet_house is None:
                continue
                
            aspects = self.PLANETARY_ASPECTS.get(planet_name, [7])
            planet_aspects = []
            
            for aspect in aspects:
                # CORRECTED: Proper house calculation
                # Jupiter in house 5, 5th aspect: 5 + 5 - 1 = 9 ✓
                # Rahu in house 6, 7th aspect: 6 + 7 - 1 = 12 ✓
                target_house = (planet_house + aspect - 1)
                if target_house > 12:
                    target_house = target_house - 12
                
                # print(f"{planet_name} in house {planet_house}, {aspect}th aspect -> house {target_house}")
                
                if target_house == house_num:
                    planet_aspects.append(aspect)
                    
            if planet_aspects:
                aspecting_planets.append((planet_name, planet_aspects))
        
        print(f"House {house_num} aspected by: {aspecting_planets}")
        return aspecting_planets
    
    def _get_planets_in_house(self, house_num: int) -> List[str]:
        """Get planets located in a specific house."""
        planets_in_house = []
        
        for planet_name, planet_detail in self.planet_data.items():
            planet_house = self._get_planet_house_number(planet_name)
            if planet_house == house_num:
                planets_in_house.append(planet_name)
        
        return planets_in_house
    
    def _analyze_auspicious_influence(self, target_house: int, planet_being_analyzed: Optional[str] = None) -> Tuple[InfluenceType, List[str], str]:
        """Analyze if a house is under auspicious, neutral, or inauspicious influence with detailed explanations."""
        supporting_factors = []
        detailed_explanation = []
        benefic_count = 0
        malefic_count = 0
        benefic_strength = 0.0
        malefic_strength = 0.0

        aspecting_planets = self._get_planets_aspecting_house(target_house)
        planets_in_house = [p for p in self._get_planets_in_house(target_house) if p != planet_being_analyzed]

        # Benefic influences
        for planet, aspects in aspecting_planets:
            if planet in self.NATURAL_BENEFICS:
                planet_house = self._get_planet_house_number(planet)
                aspect_str = ', '.join([f"{a}th" for a in aspects])
                supporting_factors.append(f"Aspected by benefic {planet} ({aspect_str} aspect from House {planet_house})")
                detailed_explanation.append(f"{planet} from House {planet_house} casts {aspect_str} aspect on House {target_house}, bringing positive influence")
                benefic_count += 1
                benefic_strength += 1.0  # Can be refined with planetary strength calculations

        for planet in planets_in_house:
            if planet in self.NATURAL_BENEFICS:
                supporting_factors.append(f"Contains benefic {planet}")
                detailed_explanation.append(f"Benefic planet {planet} is directly placed in House {target_house}, enhancing its positive qualities")
                benefic_count += 1
                benefic_strength += 1.5  # Direct placement is stronger than aspect

        # Malefic influences
        for planet, aspects in aspecting_planets:
            if planet in self.NATURAL_MALEFICS:
                planet_house = self._get_planet_house_number(planet)
                aspect_str = ', '.join([f"{a}th" for a in aspects])
                supporting_factors.append(f"Aspected by malefic {planet} ({aspect_str} aspect from House {planet_house})")
                detailed_explanation.append(f"Malefic {planet} from House {planet_house} casts {aspect_str} aspect, creating challenges")
                malefic_count += 1
                malefic_strength += 1.0

        for planet in planets_in_house:
            if planet in self.NATURAL_MALEFICS:
                supporting_factors.append(f"Contains malefic {planet}")
                detailed_explanation.append(f"Malefic planet {planet} is placed in House {target_house}, which may create obstacles")
                malefic_count += 1
                malefic_strength += 1.5

        # Shubh Kartari (Benefic Sandwich)
        house_before = ((target_house - 2) % 12) + 1
        house_after = (target_house % 12) + 1
        benefics_before = [p for p in self._get_planets_in_house(house_before) if p in self.NATURAL_BENEFICS]
        benefics_after = [p for p in self._get_planets_in_house(house_after) if p in self.NATURAL_BENEFICS]
        
        if benefics_before and benefics_after:
            supporting_factors.append(f"Shubh Kartari: benefics in Houses {house_before} and {house_after}")
            detailed_explanation.append(f"House {target_house} is under Shubh Kartari yoga with benefics {', '.join(benefics_before)} in House {house_before} and {', '.join(benefics_after)} in House {house_after}")
            benefic_count += 1
            benefic_strength += 1.0

        # Paap Kartari (Malefic Sandwich)
        malefics_before = [p for p in self._get_planets_in_house(house_before) if p in self.NATURAL_MALEFICS]
        malefics_after = [p for p in self._get_planets_in_house(house_after) if p in self.NATURAL_MALEFICS]
        
        if malefics_before and malefics_after:
            supporting_factors.append(f"Paap Kartari: malefics in Houses {house_before} and {house_after}")
            detailed_explanation.append(f"House {target_house} is under Paap Kartari yoga with malefics {', '.join(malefics_before)} in House {house_before} and {', '.join(malefics_after)} in House {house_after}")
            malefic_count += 1
            malefic_strength += 1.0

        # Determine influence type based on strength comparison
        influence_type = self._determine_influence_category(benefic_count, malefic_count, benefic_strength, malefic_strength)
        
        explanation_text = " | ".join(detailed_explanation) if detailed_explanation else "No significant planetary influences detected"
        return influence_type, supporting_factors, explanation_text

    def _determine_influence_category(self, benefic_count: int, malefic_count: int, 
                                    benefic_strength: float, malefic_strength: float) -> InfluenceType:
        """Determine if influence is auspicious, neutral, or inauspicious based on planetary influences."""
        
        # If no significant influences
        if benefic_count == 0 and malefic_count == 0:
            return InfluenceType.NEUTRAL
        
        # Calculate strength ratio for more nuanced analysis
        if benefic_strength > 0 and malefic_strength > 0:
            ratio = benefic_strength / malefic_strength
            if ratio >= 1.5:  # Significantly more benefic influence
                return InfluenceType.AUSPICIOUS
            elif ratio <= 0.67:  # Significantly more malefic influence (1/1.5)
                return InfluenceType.INAUSPICIOUS
            else:
                return InfluenceType.NEUTRAL
        elif benefic_strength > 0:
            return InfluenceType.AUSPICIOUS
        elif malefic_strength > 0:
            return InfluenceType.INAUSPICIOUS
        else:
            return InfluenceType.NEUTRAL
    

    def _get_planet_dignity(self, planet_name: str) -> str:
        """Get the dignity of a planet in its current sign."""
        planet_sign = self._get_planet_sign(planet_name)
        
        if planet_sign == self.EXALTATION_SIGNS.get(planet_name):
            return "Exalted"
        elif planet_sign == self.DEBILITATION_SIGNS.get(planet_name):
            return "Debilitated"
        elif planet_sign == self.MOOLATRIKONA_SIGNS.get(planet_name):
            return "Moolatrikona"
        elif planet_sign in [sign for sign, lord in self.SIGN_LORDS.items() if lord == planet_name]:
            return "Own Sign"
        else:
            return "Normal"
    
    def analyze_lagna_placement(self) -> LagnaAnalysisResult:
        """Analyze Lagna lord, Sun, and Moon placement in favorable houses."""
        planets = [self.lagna_lord]
        if self.lagna_lord != 'Sun':
            planets.append('Sun')
        if self.lagna_lord != 'Moon':
            planets.append('Moon')
        
        houses = [self._get_planet_house_number(p) for p in planets]
        favorable = [h in self.FAVORABLE_HOUSES if h else False for h in houses]
        
        details = []
        detailed_explanation = []
        supporting_factors = []
        
        for i, (planet, house, fav) in enumerate(zip(planets, houses, favorable)):
            if house:
                sig = self.HOUSE_SIGNIFICANCE.get(house, "Unknown significance")
                dignity = self._get_planet_dignity(planet)
                sign = self._get_planet_sign(planet)
                
                prefix = "Lagna lord " if i == 0 else ""
                details.append(f"{prefix}{planet} in House {house} ({sig})")
                detailed_explanation.append(f"{prefix}{planet} is {dignity} in {sign} sign, placed in House {house} representing {sig}")
                supporting_factors.append(f"{prefix}{planet} in {'favorable' if fav else 'unfavorable'} House {house}")
        
        result = all(favorable)
        score = sum(favorable) / len(favorable) * 100
        
        return LagnaAnalysisResult(
            criterion="(I) Lagna Lord, Sun and Moon in Favorable Houses",
            result=result,
            score=score,
            details=" | ".join(details),
            influence_type=InfluenceType.AUSPICIOUS if result else InfluenceType.INAUSPICIOUS,
            supporting_factors=supporting_factors,
            detailed_explanation=" | ".join(detailed_explanation)
        )
    
    def analyze_auspicious_influence_on_lagna_planets(self) -> LagnaAnalysisResult:
        """Analyze auspicious influence on Lagna lord, Sun, and Moon with detailed breakdown."""
        planets = [self.lagna_lord]
        if self.lagna_lord != 'Sun':
            planets.append('Sun')
        if self.lagna_lord != 'Moon':
            planets.append('Moon')

        supporting_factors = []
        detailed_explanations = []
        auspicious_count = 0
        neutral_count = 0
        inauspicious_count = 0

        for planet in planets:
            house = self._get_planet_house_number(planet)
            if not house:
                detailed_explanations.append(f"{planet} house position unknown.")
                continue

            influence_type, factors, explanation = self._analyze_auspicious_influence(house, planet_being_analyzed=planet)
            
            if influence_type == InfluenceType.AUSPICIOUS:
                auspicious_count += 1
            elif influence_type == InfluenceType.NEUTRAL:
                neutral_count += 1
            else:  # INAUSPICIOUS
                inauspicious_count += 1

            tag = "Lagna lord" if planet == self.lagna_lord else planet
            supporting_factors.extend([f"{tag}: {factor}" for factor in factors])
            detailed_explanations.append(f"{tag} in House {house} ({influence_type.value}): {explanation}")

        # Determine overall result and influence type
        total_planets = len(planets)
        auspicious_percentage = (auspicious_count / total_planets) * 100
        
        # Overall assessment logic
        if auspicious_count >= (total_planets * 0.6):  # 60% or more auspicious
            overall_result = True
            overall_influence = InfluenceType.AUSPICIOUS
            score = auspicious_percentage
        elif inauspicious_count >= (total_planets * 0.6):  # 60% or more inauspicious
            overall_result = False
            overall_influence = InfluenceType.INAUSPICIOUS
            score = (inauspicious_count / total_planets) * 100
        else:  # Mixed or mostly neutral
            overall_result = auspicious_count > inauspicious_count
            overall_influence = InfluenceType.NEUTRAL
            score = 50  # Neutral score

        details = f"Influences: {auspicious_count} auspicious, {neutral_count} neutral, {inauspicious_count} inauspicious out of {total_planets} planets"

        return LagnaAnalysisResult(
            criterion="(II) Auspicious Influence on Lagna Lord, Sun and Moon",
            result=overall_result,
            score=score,
            details=details,
            influence_type=overall_influence,
            supporting_factors=supporting_factors,
            detailed_explanation=" | ".join(detailed_explanations)
        )

    def analyze_lagna_lord_sun_moon_with_kendra_trikona_eleventh_lords(self) -> LagnaAnalysisResult:
        """Analyze if Lagna lord, Sun, and Moon are with Kendra-Trikona or 11th lords."""
        planets = [self.lagna_lord]
        if self.lagna_lord != 'Sun':
            planets.append('Sun')
        if self.lagna_lord != 'Moon':
            planets.append('Moon')
        
        beneficial_lords = {self.house_lords.get(h) for h in self.KENDRA_HOUSES | self.TRIKONA_HOUSES | {11} if self.house_lords.get(h)}
        
        supporting_factors = []
        detailed_explanations = []
        conjunction_count = 0
        
        for planet in planets:
            house = self._get_planet_house_number(planet)
            if not house:
                continue
                
            associated_lords = [p for p in self._get_planets_in_house(house) if p in beneficial_lords and p != planet]
            
            if associated_lords:
                conjunction_count += 1
                lord_details = []
                for lord in associated_lords:
                    assosciated_planet_mooltrikona = None
                    house_types = []
                    for h in self._get_houses_ruled_by_planet(lord):
                        if h in self.KENDRA_HOUSES:
                            house_types.append(f"H{h} (Kendra)")
                            assosciated_planet_mooltrikona = self._analyze_planet_moolatrikona(lord)
                        elif h in self.TRIKONA_HOUSES:
                            house_types.append(f"H{h} (Trikona)")
                            assosciated_planet_mooltrikona = self._analyze_planet_moolatrikona(lord)
                        elif h == 11:
                            house_types.append(f"H{h} (Gains)")
                            assosciated_planet_mooltrikona = self._analyze_planet_moolatrikona(lord)
                    lord_details.append(f"{lord} (lord of {', '.join(house_types)})")
                    if assosciated_planet_mooltrikona:
                        supporting_factors.append(assosciated_planet_mooltrikona)
                
                tag = "Lagna lord" if planet == self.lagna_lord else planet
                supporting_factors.append(f"{tag} with: {', '.join(associated_lords)}")
                detailed_explanations.append(f"{tag} {planet} is conjunct with {', '.join(lord_details)} in House {house}")
        
        result = conjunction_count >= 1
        score = (conjunction_count / len(planets)) * 100

        return LagnaAnalysisResult(
            criterion="(III) Lagna Lord, Sun and Moon with Kendra-Trikona-11th Lords",
            result=result,
            score=score,
            details=f"Beneficial associations found: {conjunction_count}/{len(planets)}",
            influence_type=InfluenceType.AUSPICIOUS if result else InfluenceType.NEUTRAL,
            supporting_factors=supporting_factors,
            detailed_explanation=" | ".join(detailed_explanations) if detailed_explanations else "No beneficial conjunctions found"
        )
    
    def analyze_relative_positions(self) -> List[LagnaAnalysisResult]:
        """Analyze relative positions between key planets with detailed explanations."""
        results = []
        
        lagna_lord_house = self._get_planet_house_number(self.lagna_lord)
        sun_house = self._get_planet_house_number('Sun')
        moon_house = self._get_planet_house_number('Moon')
        
        # Lagna lord and Sun relative position
        if lagna_lord_house and sun_house:
            is_favorable = self._is_position_favorable(lagna_lord_house, sun_house)
            position_desc = self._get_relative_position(lagna_lord_house, sun_house)
            distance = self._calculate_house_distance(lagna_lord_house, sun_house)
            
            detailed_explanation = f"Lagna lord {self.lagna_lord} in House {lagna_lord_house} and Sun in House {sun_house} are {distance} houses apart. "
            
            if is_favorable:
                detailed_explanation += "This is considered a favorable position promoting harmony between self-identity and soul purpose."
            else:
                detailed_explanation += "This position may create some tension between personal desires and soul objectives."
            
            results.append(LagnaAnalysisResult(
                criterion="(VI) Lagna Lord and Sun Relative Position",
                result=is_favorable,
                score=100 if is_favorable else 0,
                details=f"Lagna lord (H{lagna_lord_house}) and Sun (H{sun_house}) are {position_desc}",
                influence_type=InfluenceType.AUSPICIOUS if is_favorable else InfluenceType.INAUSPICIOUS,
                supporting_factors=[f"Position: {position_desc}"],
                detailed_explanation=detailed_explanation
            ))
        
        # Lagna lord and Moon relative position
        if lagna_lord_house and moon_house:
            is_favorable = self._is_position_favorable(lagna_lord_house, moon_house)
            position_desc = self._get_relative_position(lagna_lord_house, moon_house)
            distance = self._calculate_house_distance(lagna_lord_house, moon_house)
            
            detailed_explanation = f"Lagna lord {self.lagna_lord} in House {lagna_lord_house} and Moon in House {moon_house} are {distance} houses apart. "
            
            if is_favorable:
                detailed_explanation += "This favorable position supports emotional stability and mental peace."
            else:
                detailed_explanation += "This position may indicate emotional challenges or mental restlessness."
            
            results.append(LagnaAnalysisResult(
                criterion="(VII) Lagna Lord and Moon Relative Position",
                result=is_favorable,
                score=100 if is_favorable else 0,
                details=f"Lagna lord (H{lagna_lord_house}) and Moon (H{moon_house}) are {position_desc}",
                influence_type=InfluenceType.AUSPICIOUS if is_favorable else InfluenceType.INAUSPICIOUS,
                supporting_factors=[f"Position: {position_desc}"],
                detailed_explanation=detailed_explanation
            ))
        
        return results
    
    def analyze_dusthana_placements(self) -> LagnaAnalysisResult:
        """Analyze if Lagna Lord, Sun, and Moon are in Dusthana houses with detailed explanations."""
        
        # Prepare mapping of planet names to labels
        planet_labels = {
            self.lagna_lord: "Lagna Lord",
            "Sun": "Sun",
            "Moon": "Moon"
        }

        # Remove duplicate planets (e.g., if Lagna Lord is Sun or Moon)
        unique_planets = {}
        for planet, label in planet_labels.items():
            if planet not in unique_planets:
                unique_planets[planet] = label

        dusthana_count = 0
        supporting_factors = []
        detailed_explanations = []

        for planet, label in unique_planets.items():
            house = self._get_planet_house_number(planet)
            if house in self.DUSTHANA_HOUSES:
                dusthana_count += 1
                house_significance = self.HOUSE_SIGNIFICANCE.get(house, "")
                supporting_factors.append(f"{label} {planet} in Dusthana house {house}")
                detailed_explanations.append(
                    f"{label} {planet} in House {house} ({house_significance}) may bring challenges related to {label.lower()}"
                )

        if dusthana_count == 0:
            supporting_factors.append("Lagna Lord, Sun, and Moon all avoid Dusthana houses")
            detailed_explanations.append(
                "All key planets are placed outside Dusthana houses (6th, 8th, 12th), avoiding major afflictions"
            )

        score = ((len(unique_planets) - dusthana_count) / len(unique_planets)) * 100
        result = dusthana_count == 0

        return LagnaAnalysisResult(
            criterion="(VIII) Avoidance of Dusthana Houses",
            result=result,
            score=score,
            details=f"Dusthana placements: {dusthana_count}/{len(unique_planets)}",
            influence_type=InfluenceType.AUSPICIOUS if result else InfluenceType.INAUSPICIOUS,
            supporting_factors=supporting_factors,
            detailed_explanation=" | ".join(detailed_explanations)
        )


    
    def analyze_dusthana_lord_associations(self) -> LagnaAnalysisResult:
        """Check if Lagna Lord, Sun, or Moon are conjunct with Dusthana lords."""
        
        # Map each relevant planet to a label
        planet_labels = {
            self.lagna_lord: "Lagna Lord",
            "Sun": "Sun",
            "Moon": "Moon"
        }

        # Avoid analyzing any planet more than once
        unique_planets = {planet: label for planet, label in planet_labels.items()}

        # Prepare Dusthana lords
        dusthana_lord_details = {
            lord: f"H{h} ({self.HOUSE_SIGNIFICANCE.get(h, '')})"
            for h in self.DUSTHANA_HOUSES
            if (lord := self.house_lords.get(h))
        }

        association_count = 0
        supporting_factors = []
        detailed_explanations = []

        for planet, label in unique_planets.items():
            house = self._get_planet_house_number(planet)
            if not house:
                continue

            co_planets = [p for p in self._get_planets_in_house(house) if p != planet and p in dusthana_lord_details]
            if co_planets:
                association_count += 1
                joined_names = ", ".join(f"{p} (lord of {dusthana_lord_details[p]})" for p in co_planets)
                supporting_factors.append(f"{label} with Dusthana lords: {', '.join(co_planets)}")
                detailed_explanations.append(f"{label} {planet} is conjunct with {joined_names} in House {house}")

        if not supporting_factors:
            supporting_factors.append("No Dusthana lord associations found")
            detailed_explanations.append("Lagna Lord, Sun, and Moon are not conjunct with lords of 6th, 8th, or 12th houses")

        total_planets = len(unique_planets)
        score = ((total_planets - association_count) / total_planets) * 100
        result = association_count == 0

        return LagnaAnalysisResult(
            criterion="(IX) Avoidance of Dusthana Lord Associations",
            result=result,
            score=score,
            details=f"Dusthana associations: {association_count}/{total_planets}",
            influence_type=InfluenceType.AUSPICIOUS if result else InfluenceType.INAUSPICIOUS,
            supporting_factors=supporting_factors,
            detailed_explanation=" | ".join(detailed_explanations)
        )

    def analyze_inauspicious_influence_on_lagna_planets(self) -> LagnaAnalysisResult:
        """Check inauspicious influences on Lagna Lord, Sun, and Moon."""
        
        planet_labels = {
            self.lagna_lord: "Lagna Lord",
            "Sun": "Sun",
            "Moon": "Moon"
        }

        unique_planets = {planet: label for planet, label in planet_labels.items()}

        inauspicious_count = 0
        supporting_factors = []
        detailed_explanations = []

        for planet, label in unique_planets.items():
            house = self._get_planet_house_number(planet)
            if not house:
                continue

            is_inauspicious, factors, explanation = self._analyze_inauspicious_influence(house, target_planet=planet)
            if is_inauspicious:
                inauspicious_count += 1
            supporting_factors.extend([f"{label}: {f}" for f in factors])
            detailed_explanations.append(f"{label} in House {house}: {explanation}")

        total_planets = len(unique_planets)
        score = ((total_planets - inauspicious_count) / total_planets) * 100
        result = inauspicious_count == 0

        return LagnaAnalysisResult(
            criterion="(X) Avoidance of Inauspicious Influence on Lagna Lord, Sun, and Moon",
            result=result,
            score=score,
            details=f"Inauspicious influences found: {inauspicious_count}/{total_planets}",
            influence_type=InfluenceType.AUSPICIOUS if result else InfluenceType.INAUSPICIOUS,
            supporting_factors=supporting_factors,
            detailed_explanation=" | ".join(detailed_explanations)
        )


    
    def _analyze_inauspicious_influence(self, target_house: int, target_planet: Optional[str] = None) -> Tuple[bool, List[str], str]:
        """Analyze if a house is under inauspicious influence with detailed explanations."""
        supporting_factors = []
        detailed_explanation = []
        is_inauspicious = False

        # Check for malefic aspects
        aspecting_planets = self._get_planets_aspecting_house(target_house)
        malefic_aspects = [(p, aspects) for p, aspects in aspecting_planets if p in self.NATURAL_MALEFICS]

        for planet, aspects in malefic_aspects:
            planet_house = self._get_planet_house_number(planet)
            aspect_str = ', '.join([f"{a}th" for a in aspects])
            supporting_factors.append(f"Aspected by malefic {planet} ({aspect_str} aspect from House {planet_house})")
            detailed_explanation.append(
                f"{planet} from House {planet_house} casts {aspect_str} aspect on House {target_house}, creating malefic influence"
            )
            is_inauspicious = True

        # Check for malefic planets in the house (excluding target planet if specified)
        planets_in_house = self._get_planets_in_house(target_house)
        malefics_in_house = [
            p for p in planets_in_house if (p in self.NATURAL_MALEFICS and p != target_planet)
        ]

        for planet in malefics_in_house:
            supporting_factors.append(f"Contains malefic {planet}")
            detailed_explanation.append(
                f"Malefic planet {planet} is directly placed in House {target_house}, creating challenging influences"
            )
            is_inauspicious = True

        # Check for Paap Kartari Yoga (malefics in 2nd and 12th houses from target)
        house_before = ((target_house - 2) % 12) + 1  # 12th from target
        house_after = (target_house % 12) + 1         # 2nd from target

        malefics_before = [p for p in self._get_planets_in_house(house_before) if p in self.NATURAL_MALEFICS]
        malefics_after = [p for p in self._get_planets_in_house(house_after) if p in self.NATURAL_MALEFICS]

        if malefics_before and malefics_after:
            supporting_factors.append(f"Paap Kartari: malefics in Houses {house_before} and {house_after}")
            detailed_explanation.append(
                f"House {target_house} is under Paap Kartari yoga with malefics "
                f"{', '.join(malefics_before)} in House {house_before} and "
                f"{', '.join(malefics_after)} in House {house_after}"
            )
            is_inauspicious = True

        explanation_text = " | ".join(detailed_explanation) if detailed_explanation else \
            "No significant inauspicious influences detected"

        return is_inauspicious, supporting_factors, explanation_text


    def analyze_lagna_auspicious_influence(self) -> LagnaAnalysisResult:
        """Analyze auspicious influence on Lagna (1st house) with detailed breakdown."""
        influence_type, supporting_factors, explanation = self._analyze_auspicious_influence(1)
        
        # Additional analysis for Lagna specifically
        lagna_moolatrikona_analysis = self._analyze_lagna_moolatrikona()
        if lagna_moolatrikona_analysis:
            supporting_factors.append(lagna_moolatrikona_analysis)
        
        # Determine result and score based on influence type
        if influence_type == InfluenceType.AUSPICIOUS:
            result = True
            score = 100
            details = "Lagna under strong benefic influence"
        elif influence_type == InfluenceType.INAUSPICIOUS:
            result = False
            score = 0
            details = "Lagna under strong malefic influence"
        else:  # NEUTRAL
            result = True  # Neutral is considered acceptable for Lagna
            score = 50
            details = "Lagna under mixed/neutral influence"
        
        return LagnaAnalysisResult(
            criterion="(IV) Auspicious Influence on Lagna",
            result=result,
            score=score,
            details=details,
            influence_type=influence_type,
            supporting_factors=supporting_factors,
            detailed_explanation=explanation
        )

    def analyze_lagna_inauspicious_influence(self) -> LagnaAnalysisResult:
        """Analyze inauspicious influence on Lagna (1st house) with detailed breakdown."""
        is_inauspicious, supporting_factors, explanation = self._analyze_inauspicious_influence(1)
        
        return LagnaAnalysisResult(
            criterion="(XI) Avoidance of Inauspicious Influence on Lagna",
            result=not is_inauspicious,
            score=0 if is_inauspicious else 100,
            details="Lagna under malefic influence" if is_inauspicious else "Lagna free from malefic influence",
            influence_type=InfluenceType.INAUSPICIOUS if is_inauspicious else InfluenceType.AUSPICIOUS,
            supporting_factors=supporting_factors,
            detailed_explanation=explanation
        )
    
    def analyze_beneficial_lords_in_lagna(self) -> LagnaAnalysisResult:
        """Analyze if beneficial house lords are placed in Lagna with detailed explanations."""
        planets_in_lagna = self._get_planets_in_house(1)
        
        # Get beneficial lords (Kendra, Trikona, 2nd, 11th house lords)
        beneficial_houses = self.KENDRA_HOUSES | self.TRIKONA_HOUSES | {2, 11}
        beneficial_lords = []
        
        for house_num in beneficial_houses:
            lord = self.house_lords.get(house_num)
            if lord and lord in planets_in_lagna:
                house_types = []
                if house_num in self.KENDRA_HOUSES:
                    house_types.append("Kendra")
                if house_num in self.TRIKONA_HOUSES:
                    house_types.append("Trikona")
                if house_num == 2:
                    house_types.append("Wealth")
                if house_num == 11:
                    house_types.append("Gains")
                
                beneficial_lords.append({
                    'planet': lord,
                    'house': house_num,
                    'types': house_types,
                    'moolatrikona_analysis': self._analyze_planet_moolatrikona(lord)
                })
        
        supporting_factors = []
        detailed_explanations = []
        
        for lord_info in beneficial_lords:
            house_types_str = '/'.join(lord_info['types'])
            supporting_factors.append(f"{lord_info['planet']} (lord of H{lord_info['house']} - {house_types_str}) in Lagna")
            
            explanation = f"{lord_info['planet']}, lord of {lord_info['house']}th house ({house_types_str}), is placed in Lagna"
            if lord_info['moolatrikona_analysis']:
                explanation += f" with {lord_info['moolatrikona_analysis']}"
            detailed_explanations.append(explanation)
        
        result = len(beneficial_lords) > 0
        score = min(len(beneficial_lords) * 25, 100)
        
        if not supporting_factors:
            supporting_factors.append("No beneficial house lords in Lagna")
            detailed_explanations.append("No lords of Kendra, Trikona, 2nd, or 11th houses are placed in the Lagna")
        
        return LagnaAnalysisResult(
            criterion="(V) Beneficial House Lords in Lagna",
            result=result,
            score=score,
            details=f"Beneficial lords in Lagna: {len(beneficial_lords)}",
            influence_type=InfluenceType.AUSPICIOUS if result else InfluenceType.NEUTRAL,
            supporting_factors=supporting_factors,
            detailed_explanation=" | ".join(detailed_explanations)
        )
    
    def analyze_dusthana_lords_in_lagna(self) -> LagnaAnalysisResult:
        """Analyze if Dusthana lords are placed in Lagna (which is inauspicious)."""
        planets_in_lagna = self._get_planets_in_house(1)
        
        dusthana_lords_in_lagna = []
        for house_num in self.DUSTHANA_HOUSES:
            lord = self.house_lords.get(house_num)
            if lord and lord in planets_in_lagna:
                dusthana_lords_in_lagna.append({
                    'planet': lord,
                    'house': house_num,
                    'significance': self.HOUSE_SIGNIFICANCE.get(house_num, ""),
                    'moolatrikona_analysis': self._analyze_planet_moolatrikona(lord)
                })
        
        supporting_factors = []
        detailed_explanations = []
        
        for lord_info in dusthana_lords_in_lagna:
            supporting_factors.append(f"{lord_info['planet']} (lord of H{lord_info['house']}) in Lagna")
            
            explanation = f"{lord_info['planet']}, lord of {lord_info['house']}th house ({lord_info['significance']}), is placed in Lagna"
            if lord_info['moolatrikona_analysis']:
                explanation += f" with {lord_info['moolatrikona_analysis']}"
            detailed_explanations.append(explanation)
        
        result = len(dusthana_lords_in_lagna) == 0
        score = ((3 - len(dusthana_lords_in_lagna)) / 3) * 100
        
        if not supporting_factors:
            supporting_factors.append("No Dusthana lords in Lagna")
            detailed_explanations.append("No lords of 6th, 8th, or 12th houses are placed in the Lagna")
        
        return LagnaAnalysisResult(
            criterion="(XII) Avoidance of Dusthana Lords in Lagna",
            result=result,
            score=score,
            details=f"Dusthana lords in Lagna: {len(dusthana_lords_in_lagna)}",
            influence_type=InfluenceType.AUSPICIOUS if result else InfluenceType.INAUSPICIOUS,
            supporting_factors=supporting_factors,
            detailed_explanation=" | ".join(detailed_explanations)
        )
    
    def _analyze_lagna_moolatrikona(self) -> Optional[str]:
        """Analyze Lagna lord's moolatrikona placement."""
        moolatrikona_sign = self.MOOLATRIKONA_SIGNS.get(self.lagna_lord)
        if not moolatrikona_sign:
            return None
        
        # Find which house contains the moolatrikona sign
        for house_num, house_detail in self.house_data.items():
            house_sign = house_detail.safe_get_nested('HouseRasiSign', 'Name')
            if house_sign == moolatrikona_sign:
                house_num = int(house_num)
                if house_num in self.FAVORABLE_HOUSES:
                    return f"Moolatrikona {moolatrikona_sign} in favorable House {house_num}"
                else:
                    return f"Moolatrikona {moolatrikona_sign} in unfavorable House {house_num}"
        
        return f"Moolatrikona {moolatrikona_sign} position unclear"
    
    def _analyze_planet_moolatrikona(self, planet_name: str) -> Optional[str]:
        """Analyze a planet's moolatrikona placement."""
        moolatrikona_sign = self.MOOLATRIKONA_SIGNS.get(planet_name)
        if not moolatrikona_sign:
            return None
        
        # Find which house contains the moolatrikona sign
        for house_num, house_detail in self.house_data.items():
            house_sign = house_detail.safe_get_nested('HouseRasiSign', 'Name')
            if house_sign == moolatrikona_sign:
                house_num = int(house_num)
                if house_num in self.FAVORABLE_HOUSES:
                    return f"moolatrikona of {planet_name} - {moolatrikona_sign} in favorable House {house_num}"
                else:
                    return f"moolatrikona of {planet_name} - {moolatrikona_sign} in unfavorable House {house_num}"
        
        return f"moolatrikona of {planet_name} - {moolatrikona_sign} position unclear"
    
    
    def calculate_improved_overall_score(self) -> Dict[str, float]:
        """Calculate overall score with separate positive and negative analysis."""
        
        # Separate positive and negative criteria
        positive_criteria = []  # Criteria 1-7: Things that should be present
        negative_criteria = []  # Criteria 8-12: Things that should be avoided
        
        for i, result in enumerate(self.analysis_results, 1):
            if i <= 7:  # First 7 are positive criteria
                positive_criteria.append(result)
            else:  # Last 5 are negative criteria
                negative_criteria.append(result)
        
        # Calculate positive strength score
        positive_total = 0
        positive_weight = 0
        for result in positive_criteria:
            # Weight based on importance and actual achievement
            weight = 1.0  # Base weight
            
            # Increase weight for core criteria
            if "Lagna Lord" in result.criterion or "Sun" in result.criterion:
                weight = 1.5
            elif "Auspicious Influence" in result.criterion:
                weight = 1.3
            elif "Relative Position" in result.criterion:
                weight = 0.8  # Slightly less important
            
            positive_total += result.score * weight
            positive_weight += weight
        
        positive_score = positive_total / positive_weight if positive_weight > 0 else 0
        
        # Calculate negative avoidance score
        negative_total = 0
        negative_weight = 0
        for result in negative_criteria:
            # Weight based on severity of negative influence
            weight = 1.0  # Base weight
            
            # Increase weight for more severe negative influences
            if "Dusthana" in result.criterion:
                weight = 1.4  # Dusthana placements are quite serious
            elif "Inauspicious Influence" in result.criterion:
                weight = 1.2
            
            negative_total += result.score * weight
            negative_weight += weight
        
        negative_score = negative_total / negative_weight if negative_weight > 0 else 0
        
        # Calculate composite score
        # Give 60% weight to positive achievements, 40% to negative avoidance
        composite_score = (positive_score * 0.6) + (negative_score * 0.4)
        
        # Calculate strength rating
        strength_rating = self._get_strength_rating(composite_score)
        
        return {
            'positive_score': round(positive_score, 2),
            'negative_score': round(negative_score, 2), 
            'composite_score': round(composite_score, 2),
            'strength_rating': strength_rating,
            'positive_criteria_count': len(positive_criteria),
            'negative_criteria_count': len(negative_criteria),
            'positive_passed': len([r for r in positive_criteria if r.result]),
            'negative_passed': len([r for r in negative_criteria if r.result])
        }

    def _get_strength_rating(self, score: float) -> str:
        """Get qualitative strength rating based on score."""
        if score >= 85:
            return "Excellent"
        elif score >= 70:
            return "Good"
        elif score >= 55:
            return "Moderate"
        elif score >= 40:
            return "Weak"
        else:
            return "Poor"

    def perform_comprehensive_analysis(self) -> Dict[str, Any]:
        """Enhanced comprehensive analysis with improved scoring."""
        self.analysis_results = []
        
        # Auspicious analysis (Positive criteria)
        self.analysis_results.append(self.analyze_lagna_placement())
        self.analysis_results.append(self.analyze_auspicious_influence_on_lagna_planets())
        self.analysis_results.append(self.analyze_lagna_lord_sun_moon_with_kendra_trikona_eleventh_lords())
        self.analysis_results.append(self.analyze_lagna_auspicious_influence())
        self.analysis_results.append(self.analyze_beneficial_lords_in_lagna())
        
        # Relative position analysis (Positive criteria)
        relative_results = self.analyze_relative_positions()
        self.analysis_results.extend(relative_results)
        
        # Inauspicious analysis (Negative criteria - things to avoid)
        self.analysis_results.append(self.analyze_dusthana_placements())
        self.analysis_results.append(self.analyze_dusthana_lord_associations())
        self.analysis_results.append(self.analyze_inauspicious_influence_on_lagna_planets())
        self.analysis_results.append(self.analyze_lagna_inauspicious_influence())
        self.analysis_results.append(self.analyze_dusthana_lords_in_lagna())
        
        # Calculate improved scores
        scoring_analysis = self.calculate_improved_overall_score()
        
        # Count results by influence type
        auspicious_results = [r for r in self.analysis_results if r.influence_type == InfluenceType.AUSPICIOUS and r.result]
        inauspicious_results = [r for r in self.analysis_results if r.influence_type == InfluenceType.INAUSPICIOUS and r.result]
        
        total_criteria = len(self.analysis_results)
        auspicious_count = len(auspicious_results)
        inauspicious_count = len(inauspicious_results)
        
        return {
            'lagna_lord': self.lagna_lord,
            'lagna_sign': self.lagna_sign,
            'total_criteria_analyzed': total_criteria,
            'auspicious_criteria_met': auspicious_count,
            'inauspicious_criteria_met': inauspicious_count,
            
            # Enhanced scoring
            'scoring_analysis': scoring_analysis,
            'overall_score': scoring_analysis['composite_score'],  # Use composite score
            'strength_rating': scoring_analysis['strength_rating'],
            
            'detailed_results': self.analysis_results,
            'summary': {
                'strength_areas': [r.criterion for r in auspicious_results],
                'challenge_areas': [r.criterion for r in inauspicious_results],
                'neutral_areas': [r.criterion for r in self.analysis_results 
                            if r.influence_type == InfluenceType.NEUTRAL]
            }
        }


    def format_score_with_dot(self, score: float) -> str:
        rounded = round(score)
        if rounded < 50:
            dot = '🔴'
        elif rounded < 75:
            dot = '🟡'
        else:
            dot = '🟢'
        return f"{rounded}/100 {dot}"

    def generate_detailed_report(self) -> str:
        """Generate a comprehensive textual report of the Lagna analysis."""
        if not self.analysis_results:
            analysis = self.perform_comprehensive_analysis()
        else:
            analysis = self.perform_comprehensive_analysis()
        
        report = []
        report.append("=" * 80)
        report.append("COMPREHENSIVE LAGNA ANALYSIS REPORT")
        report.append("=" * 80)
        report.append(f"Lagna Lord: {analysis['lagna_lord']}")
        report.append(f"Lagna Sign: {analysis['lagna_sign']}")
        report.append("")
        
        # Enhanced scoring breakdown
        scoring = analysis['scoring_analysis']
        report.append("SCORING BREAKDOWN:")
        report.append(f"• Positive Achievements: {scoring['positive_score']}/100 ({scoring['positive_passed']}/{scoring['positive_criteria_count']} criteria)")
        report.append(f"• Negative Avoidance: {scoring['negative_score']}/100 ({scoring['negative_passed']}/{scoring['negative_criteria_count']} criteria)")
        report.append(f"• Overall Composite Score: {scoring['composite_score']}/100")
        report.append(f"• Strength Rating: {scoring['strength_rating']}")
        report.append("")
        
        # Summary
        report.append("SUMMARY:")
        report.append(f"• Total Criteria Analyzed: {analysis['total_criteria_analyzed']}")
        report.append(f"• Auspicious Criteria Met: {analysis['auspicious_criteria_met']}")
        report.append(f"• Inauspicious Criteria Avoided: {analysis['inauspicious_criteria_met']}")
        report.append("")
        
        # ALL CRITERIA WITH PASS/FAIL STATUS
        report.append("ALL CRITERIA:")
        for i, result in enumerate(analysis['detailed_results'], 1):
            mark = "✓" if result.result else "✗"
            is_positive = i <= 7  # First 7 are positive criteria
            criterion_indicator = "🟢" if is_positive else "🔴"
            report.append(f"{mark} {criterion_indicator} {result.criterion}")
        report.append("")
        
        # DETAILED ANALYSIS
        report.append("DETAILED ANALYSIS:")
        report.append("-" * 50)
        
        for i, result in enumerate(analysis['detailed_results'], 1):
            is_positive = i <= 7
            criterion_indicator = "🟢" if is_positive else "🔴"
            status = "✓ PASS" if result.result else "✗ FAIL"
            formatted_score = self.format_score_with_dot(result.score)

            # Clear final verdict
            if is_positive and result.result:
                verdict = "✅ GOOD (Positive criterion passed)"
            elif is_positive and not result.result:
                verdict = "❌ BAD (Positive criterion failed)"
            elif not is_positive and result.result:
                verdict = "✅ GOOD (Negative influence avoided)"
            else:
                verdict = "❌ BAD (Negative influence present)"

            report.append(f"{i}. {criterion_indicator} {result.criterion}")
            report.append(f"   Status: {status} | Score: {formatted_score}")
            report.append(f"   Verdict: {verdict}")
            report.append(f"   Details: {result.details}")
            
            if result.supporting_factors:
                report.append("   Supporting Factors:")
                for factor in result.supporting_factors:
                    report.append(f"   • {factor}")
            
            if result.detailed_explanation:
                report.append(f"   Explanation: {result.detailed_explanation}")
            
            report.append("")
        
        return "\n".join(report)
