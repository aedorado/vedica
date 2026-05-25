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
    
    def __post_init__(self):
        if not self.supporting_factors:
            self.supporting_factors = []

class LagnaAnalyzer:
    """Comprehensive Lagna analysis based on traditional principles."""
    
    # House categories
    KENDRA_HOUSES = {1, 4, 7, 10}
    TRIKONA_HOUSES = {1, 5, 9}
    UPACHAYA_HOUSES = {3, 6, 10, 11}
    DUSTHANA_HOUSES = {6, 8, 12}
    FAVORABLE_HOUSES = {1, 2, 3, 4, 5, 7, 9, 10, 11}
    
    # Natural benefics and malefics
    NATURAL_BENEFICS = {'Jupiter', 'Venus', 'Mercury', 'Moon'}
    NATURAL_MALEFICS = {'Sun', 'Mars', 'Saturn', 'Rahu', 'Ketu'}
    
    # Moolatrikona signs
    MOOLATRIKONA_SIGNS = {
        'Sun': 'Leo',
        'Moon': 'Taurus', 
        'Mars': 'Aries',
        'Mercury': 'Virgo',
        'Jupiter': 'Sagittarius',
        'Venus': 'Libra',
        'Saturn': 'Aquarius'
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
        'Rahu': [5, 7, 9], 'Ketu': [5, 7, 9]
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
            return house1_data.safe_get_nested('HouseRasiSign', 'Name', 'Unknown')
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
            return planet_detail.safe_get_nested('PlanetRasiD1Sign', 'Name', 'Unknown')
        return "Unknown"
    
    def _get_houses_ruled_by_planet(self, planet_name: str) -> List[int]:
        """Get houses ruled by a planet."""
        return [house_num for house_num, lord in self.house_lords.items() 
                if lord == planet_name]
    
    def _calculate_house_distance(self, house1: int, house2: int) -> int:
        """Calculate the distance between two houses."""
        return ((house2 - house1) % 12) + 1 if house1 != house2 else 1
    
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
            # Also check that neither planet is in 6th, 8th, or 12th house
            return house1 not in self.DUSTHANA_HOUSES and house2 not in self.DUSTHANA_HOUSES
        
        return True  # Neutral positions
    
    def _get_planets_aspecting_house(self, house_num: int) -> List[str]:
        """Get planets aspecting a specific house."""
        aspecting_planets = []
        
        for planet_name, planet_detail in self.planet_data.items():
            planet_house = self._get_planet_house_number(planet_name)
            if planet_house is None:
                continue
                
            aspects = self.PLANETARY_ASPECTS.get(planet_name, [7])
            for aspect in aspects:
                target_house = ((planet_house + aspect - 1) % 12) + 1
                if target_house == house_num:
                    aspecting_planets.append(planet_name)
                    break
        
        return aspecting_planets
    
    def _get_planets_in_house(self, house_num: int) -> List[str]:
        """Get planets located in a specific house."""
        planets_in_house = []
        
        for planet_name, planet_detail in self.planet_data.items():
            planet_house = self._get_planet_house_number(planet_name)
            if planet_house == house_num:
                planets_in_house.append(planet_name)
        
        return planets_in_house
    
    def _analyze_auspicious_influence(self, target_house: int) -> Tuple[bool, List[str]]:
        """Analyze if a house is under auspicious influence."""
        supporting_factors = []
        is_auspicious = False
        
        # Check for benefic planets aspecting
        aspecting_planets = self._get_planets_aspecting_house(target_house)
        benefic_aspects = [p for p in aspecting_planets if p in self.NATURAL_BENEFICS]
        
        if benefic_aspects:
            supporting_factors.append(f"Aspected by benefics: {', '.join(benefic_aspects)}")
            is_auspicious = True
        
        # Check for benefic planets in the house
        planets_in_house = self._get_planets_in_house(target_house)
        benefics_in_house = [p for p in planets_in_house if p in self.NATURAL_BENEFICS]
        
        if benefics_in_house:
            supporting_factors.append(f"Contains benefics: {', '.join(benefics_in_house)}")
            is_auspicious = True
        
        # Check for malefic influences
        malefic_aspects = [p for p in aspecting_planets if p in self.NATURAL_MALEFICS]
        malefics_in_house = [p for p in planets_in_house if p in self.NATURAL_MALEFICS]
        
        if malefic_aspects:
            supporting_factors.append(f"Aspected by malefics: {', '.join(malefic_aspects)}")
        
        if malefics_in_house:
            supporting_factors.append(f"Contains malefics: {', '.join(malefics_in_house)}")
        
        return is_auspicious, supporting_factors
    
    def analyze_lagna_placement(self) -> LagnaAnalysisResult:
        """Analyze Lagna lord and Sun placement in favorable houses."""
        lagna_lord_house = self._get_planet_house_number(self.lagna_lord)
        sun_house = self._get_planet_house_number('Sun')
        
        favorable_houses = self.FAVORABLE_HOUSES
        
        lagna_lord_favorable = lagna_lord_house in favorable_houses if lagna_lord_house else False
        sun_favorable = sun_house in favorable_houses if sun_house else False
        
        result = lagna_lord_favorable and sun_favorable
        
        details = []
        if lagna_lord_house:
            details.append(f"Lagna lord {self.lagna_lord} in House {lagna_lord_house}")
        if sun_house:
            details.append(f"Sun in House {sun_house}")
        
        supporting_factors = []
        if lagna_lord_favorable:
            supporting_factors.append(f"Lagna lord in favorable house {lagna_lord_house}")
        if sun_favorable:
            supporting_factors.append(f"Sun in favorable house {sun_house}")
        
        score = (int(lagna_lord_favorable) + int(sun_favorable)) / 2 * 100
        
        return LagnaAnalysisResult(
            criterion="Lagna Lord and Sun in Favorable Houses",
            result=result,
            score=score,
            details=" | ".join(details),
            influence_type=InfluenceType.AUSPICIOUS if result else InfluenceType.INAUSPICIOUS,
            supporting_factors=supporting_factors
        )
    
    def analyze_auspicious_influence_on_lagna_planets(self) -> LagnaAnalysisResult:
        """Analyze auspicious influence on Lagna lord and Sun."""
        lagna_lord_house = self._get_planet_house_number(self.lagna_lord)
        sun_house = self._get_planet_house_number('Sun')
        
        supporting_factors = []
        auspicious_count = 0
        
        # Analyze Lagna lord
        if lagna_lord_house:
            is_auspicious, factors = self._analyze_auspicious_influence(lagna_lord_house)
            if is_auspicious:
                auspicious_count += 1
                supporting_factors.extend([f"Lagna lord: {factor}" for factor in factors])
        
        # Analyze Sun
        if sun_house:
            is_auspicious, factors = self._analyze_auspicious_influence(sun_house)
            if is_auspicious:
                auspicious_count += 1
                supporting_factors.extend([f"Sun: {factor}" for factor in factors])
        
        result = auspicious_count >= 1
        score = (auspicious_count / 2) * 100
        
        return LagnaAnalysisResult(
            criterion="Auspicious Influence on Lagna Lord and Sun",
            result=result,
            score=score,
            details=f"Auspicious influences found: {auspicious_count}/2",
            influence_type=InfluenceType.AUSPICIOUS if result else InfluenceType.NEUTRAL,
            supporting_factors=supporting_factors
        )
    
    def analyze_lagna_lord_sun_with_kendra_trikona_lords(self) -> LagnaAnalysisResult:
        """Analyze if Lagna lord and Sun are with Kendra-Trikona lords."""
        lagna_lord_house = self._get_planet_house_number(self.lagna_lord)
        sun_house = self._get_planet_house_number('Sun')
        
        # Get Kendra and Trikona lords
        kendra_trikona_lords = set()
        for house_num in self.KENDRA_HOUSES | self.TRIKONA_HOUSES:
            lord = self.house_lords.get(house_num)
            if lord:
                kendra_trikona_lords.add(lord)
        
        # Add 11th house lord
        lord_11 = self.house_lords.get(11)
        if lord_11:
            kendra_trikona_lords.add(lord_11)
        
        supporting_factors = []
        conjunction_count = 0
        
        # Check Lagna lord associations
        if lagna_lord_house:
            planets_with_lagna_lord = self._get_planets_in_house(lagna_lord_house)
            associated_lords = [p for p in planets_with_lagna_lord if p in kendra_trikona_lords and p != self.lagna_lord]
            if associated_lords:
                conjunction_count += 1
                supporting_factors.append(f"Lagna lord with: {', '.join(associated_lords)}")
        
        # Check Sun associations
        if sun_house:
            planets_with_sun = self._get_planets_in_house(sun_house)
            associated_lords = [p for p in planets_with_sun if p in kendra_trikona_lords and p != 'Sun']
            if associated_lords:
                conjunction_count += 1
                supporting_factors.append(f"Sun with: {', '.join(associated_lords)}")
        
        result = conjunction_count >= 1
        score = (conjunction_count / 2) * 100
        
        return LagnaAnalysisResult(
            criterion="Lagna Lord and Sun with Kendra-Trikona Lords",
            result=result,
            score=score,
            details=f"Beneficial associations found: {conjunction_count}/2",
            influence_type=InfluenceType.AUSPICIOUS if result else InfluenceType.NEUTRAL,
            supporting_factors=supporting_factors
        )
    
    def analyze_relative_positions(self) -> List[LagnaAnalysisResult]:
        """Analyze relative positions between key planets."""
        results = []
        
        lagna_lord_house = self._get_planet_house_number(self.lagna_lord)
        sun_house = self._get_planet_house_number('Sun')
        moon_house = self._get_planet_house_number('Moon')
        
        # Lagna lord and Sun relative position
        if lagna_lord_house and sun_house:
            is_favorable = self._is_position_favorable(lagna_lord_house, sun_house)
            position_desc = self._get_relative_position(lagna_lord_house, sun_house)
            
            results.append(LagnaAnalysisResult(
                criterion="Lagna Lord and Sun Relative Position",
                result=is_favorable,
                score=100 if is_favorable else 0,
                details=f"Lagna lord (H{lagna_lord_house}) and Sun (H{sun_house}) are {position_desc}",
                influence_type=InfluenceType.AUSPICIOUS if is_favorable else InfluenceType.INAUSPICIOUS,
                supporting_factors=[f"Position: {position_desc}"]
            ))
        
        # Lagna lord and Moon relative position
        if lagna_lord_house and moon_house:
            is_favorable = self._is_position_favorable(lagna_lord_house, moon_house)
            position_desc = self._get_relative_position(lagna_lord_house, moon_house)
            
            results.append(LagnaAnalysisResult(
                criterion="Lagna Lord and Moon Relative Position",
                result=is_favorable,
                score=100 if is_favorable else 0,
                details=f"Lagna lord (H{lagna_lord_house}) and Moon (H{moon_house}) are {position_desc}",
                influence_type=InfluenceType.AUSPICIOUS if is_favorable else InfluenceType.INAUSPICIOUS,
                supporting_factors=[f"Position: {position_desc}"]
            ))
        
        return results
    
    def analyze_dusthana_placements(self) -> LagnaAnalysisResult:
        """Analyze if Lagna lord and Sun are in Dusthana houses (6, 8, 12)."""
        lagna_lord_house = self._get_planet_house_number(self.lagna_lord)
        sun_house = self._get_planet_house_number('Sun')
        
        lagna_lord_dusthana = lagna_lord_house in self.DUSTHANA_HOUSES if lagna_lord_house else False
        sun_dusthana = sun_house in self.DUSTHANA_HOUSES if sun_house else False
        
        dusthana_count = int(lagna_lord_dusthana) + int(sun_dusthana)
        result = dusthana_count == 0  # Good result if neither is in Dusthana
        
        supporting_factors = []
        if lagna_lord_dusthana:
            supporting_factors.append(f"Lagna lord in Dusthana house {lagna_lord_house}")
        if sun_dusthana:
            supporting_factors.append(f"Sun in Dusthana house {sun_house}")
        
        if not supporting_factors:
            supporting_factors.append("Neither Lagna lord nor Sun in Dusthana houses")
        
        score = ((2 - dusthana_count) / 2) * 100
        
        return LagnaAnalysisResult(
            criterion="Avoidance of Dusthana Houses",
            result=result,
            score=score,
            details=f"Dusthana placements: {dusthana_count}/2",
            influence_type=InfluenceType.AUSPICIOUS if result else InfluenceType.INAUSPICIOUS,
            supporting_factors=supporting_factors
        )
    
    def analyze_dusthana_lord_associations(self) -> LagnaAnalysisResult:
        """Analyze if Lagna lord and Sun are with Dusthana lords."""
        lagna_lord_house = self._get_planet_house_number(self.lagna_lord)
        sun_house = self._get_planet_house_number('Sun')
        
        # Get Dusthana lords
        dusthana_lords = set()
        for house_num in self.DUSTHANA_HOUSES:
            lord = self.house_lords.get(house_num)
            if lord:
                dusthana_lords.add(lord)
        
        supporting_factors = []
        association_count = 0
        
        # Check Lagna lord associations
        if lagna_lord_house:
            planets_with_lagna_lord = self._get_planets_in_house(lagna_lord_house)
            associated_dusthana = [p for p in planets_with_lagna_lord if p in dusthana_lords and p != self.lagna_lord]
            if associated_dusthana:
                association_count += 1
                supporting_factors.append(f"Lagna lord with Dusthana lords: {', '.join(associated_dusthana)}")
        
        # Check Sun associations
        if sun_house:
            planets_with_sun = self._get_planets_in_house(sun_house)
            associated_dusthana = [p for p in planets_with_sun if p in dusthana_lords and p != 'Sun']
            if associated_dusthana:
                association_count += 1
                supporting_factors.append(f"Sun with Dusthana lords: {', '.join(associated_dusthana)}")
        
        result = association_count == 0  # Good result if no associations
        score = ((2 - association_count) / 2) * 100
        
        if not supporting_factors:
            supporting_factors.append("No associations with Dusthana lords found")
        
        return LagnaAnalysisResult(
            criterion="Avoidance of Dusthana Lord Associations",
            result=result,
            score=score,
            details=f"Dusthana lord associations: {association_count}/2",
            influence_type=InfluenceType.AUSPICIOUS if result else InfluenceType.INAUSPICIOUS,
            supporting_factors=supporting_factors
        )
    
    def perform_comprehensive_analysis(self) -> Dict[str, Any]:
        """Perform comprehensive Lagna analysis."""
        print("Performing Comprehensive Lagna Analysis...")
        print("=" * 80)
        
        all_results = []
        
        # Favorable aspects analysis
        print("\n🌟 FAVORABLE FACTORS ANALYSIS")
        print("-" * 50)
        
        favorable_analyses = [
            self.analyze_lagna_placement(),
            self.analyze_auspicious_influence_on_lagna_planets(),
            self.analyze_lagna_lord_sun_with_kendra_trikona_lords(),
        ]
        
        favorable_analyses.extend(self.analyze_relative_positions())
        
        for analysis in favorable_analyses:
            all_results.append(analysis)
            self._print_analysis_result(analysis)
        
        # Unfavorable aspects analysis
        print("\n⚠️  UNFAVORABLE FACTORS ANALYSIS")
        print("-" * 50)
        
        unfavorable_analyses = [
            self.analyze_dusthana_placements(),
            self.analyze_dusthana_lord_associations(),
        ]
        
        for analysis in unfavorable_analyses:
            all_results.append(analysis)
            self._print_analysis_result(analysis)
        
        # Overall summary
        self._print_overall_summary(all_results)
        
        return {
            'lagna_sign': self.lagna_sign,
            'lagna_lord': self.lagna_lord,
            'analysis_results': all_results,
            'overall_score': self._calculate_overall_score(all_results),
            'favorable_count': len([r for r in all_results if r.influence_type == InfluenceType.AUSPICIOUS and r.result]),
            'unfavorable_count': len([r for r in all_results if r.influence_type == InfluenceType.INAUSPICIOUS and not r.result])
        }
    
    def _print_analysis_result(self, result: LagnaAnalysisResult):
        """Print individual analysis result."""
        status = "✅ POSITIVE" if result.result else "❌ NEGATIVE"
        influence_icon = {"auspicious": "🌟", "inauspicious": "⚠️", "neutral": "⚪"}.get(result.influence_type.value, "")
        
        print(f"\n{influence_icon} {result.criterion}")
        print(f"   Status: {status} (Score: {result.score:.1f}/100)")
        print(f"   Details: {result.details}")
        
        if result.supporting_factors:
            print("   Supporting Factors:")
            for factor in result.supporting_factors:
                print(f"   • {factor}")
    
    def _calculate_overall_score(self, results: List[LagnaAnalysisResult]) -> float:
        """Calculate overall Lagna strength score."""
        if not results:
            return 0.0
        
        total_score = sum(r.score for r in results)
        return total_score / len(results)
    
    def _print_overall_summary(self, results: List[LagnaAnalysisResult]):
        """Print overall analysis summary."""
        overall_score = self._calculate_overall_score(results)
        
        favorable_results = [r for r in results if r.influence_type == InfluenceType.AUSPICIOUS and r.result]
        unfavorable_results = [r for r in results if r.influence_type == InfluenceType.INAUSPICIOUS and not r.result]
        
        print("\n" + "=" * 80)
        print("📊 OVERALL LAGNA ANALYSIS SUMMARY")
        print("=" * 80)
        print(f"Lagna Sign: {self.lagna_sign}")
        print(f"Lagna Lord: {self.lagna_lord}")
        print(f"Overall Score: {overall_score:.1f}/100")
        print(f"Favorable Factors: {len(favorable_results)}")
        print(f"Unfavorable Factors: {len(unfavorable_results)}")
        
        # Strength categorization
        if overall_score >= 80:
            strength_category = "Excellent"
            strength_icon = "🌟🌟🌟"
        elif overall_score >= 60:
            strength_category = "Good"
            strength_icon = "🌟🌟"
        elif overall_score >= 40:
            strength_category = "Average"
            strength_icon = "🌟"
        else:
            strength_category = "Weak"
            strength_icon = "⚠️"
        
        print(f"Lagna Strength: {strength_category} {strength_icon}")
        
        if favorable_results:
            print(f"\n✅ Key Strengths:")
            for result in favorable_results:
                print(f"   • {result.criterion}")
        
        if unfavorable_results:
            print(f"\n❌ Areas of Concern:")
            for result in unfavorable_results:
                print(f"   • {result.criterion}")
        
        print("=" * 80)

# Usage example with your existing data structure:
# 
# # Assuming you have planet_data_objs and house_data_objs from your existing code
# analyzer = LagnaAnalyzer(planet_data_objs, house_data_objs)
# comprehensive_analysis = analyzer.perform_comprehensive_analysis()
# 
# # You can also run individual analyses:
# placement_analysis = analyzer.analyze_lagna_placement()
# influence_analysis = analyzer.analyze_auspicious_influence_on_lagna_planets()
# relative_position_analyses = analyzer.analyze_relative_positions()



# Hmm, this is good, but i was expecting a more comprehensive result

# ================================================================================
# 📊 OVERALL LAGNA ANALYSIS SUMMARY
# ================================================================================
# Lagna Sign: None
# Lagna Lord: Mercury
# Overall Score: 71.4/100
# Favorable Factors: 5
# Unfavorable Factors: 2
# Lagna Strength: Good 🌟🌟
# ✅ Key Strengths:
#    • Lagna Lord and Sun in Favorable Houses
#    • Auspicious Influence on Lagna Lord and Sun
#    • Lagna Lord and Sun with Kendra-Trikona Lords
#    • Lagna Lord and Moon Relative Position
#    • Avoidance of Dusthana Houses
# ❌ Areas of Concern:
#    • Lagna Lord and Sun Relative Position
#    • Avoidance of Dusthana Lord Associations

# Eg. Lagna Lord and Sun in Favorable Houses - here we can tell which houses
#  Auspicious Influence on Lagna Lord and Sun - here we can tell what are the influences
#  Lagna Lord and Sun with Kendra-Trikona Lords - we can elaborate this
# Lagna Lord and Moon Relative Position- we can specify what etc. 
# similarly, expand all points

# Also i hope we are checking all the points that I gave, not a single criteria must be missed