"""
BPHS Compliant House Strength Analysis Algorithm
Based on Brihat Parashara Hora Shastra Classical Principles
"""

from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from enum import Enum

class StrengthRating(Enum):
    EXCELLENT = "Excellent"
    GOOD = "Good"
    AVERAGE = "Average"
    BAD = "Bad"
    VERY_BAD = "Very Bad"

@dataclass
class HouseAnalysisResult:
    bhava_strength: StrengthRating
    bhavesh_strength: StrengthRating
    karaka_strength: StrengthRating
    overall_strength: StrengthRating
    bhava_explanation: str
    bhavesh_explanation: str
    karaka_explanation: str
    key_strengths: List[str]
    key_weaknesses: List[str]
    remedial_suggestions: List[str]

class BPHSHouseAnalyzer:
    """BPHS Compliant House Strength Analysis"""
    
    # Natural Karakas for each house (BPHS Classification)
    NATURAL_KARAKAS = {
        1: ["Sun"],                    # Atmakaraka - Soul/Self
        2: ["Jupiter"],                # Dhankaraka - Wealth/Speech
        3: ["Mars"],                   # Bhratikaraka - Siblings/Courage
        4: ["Moon"],                   # Matrikaraka - Mother/Mind/Home
        5: ["Jupiter"],                # Putrakaraka - Children/Intelligence
        6: ["Mars", "Saturn"],         # Rogakaraka - Disease/Enemies
        7: ["Venus"],                  # Kalatra karaka - Spouse/Partnerships
        8: ["Saturn"],                 # Ayushkaraka - Longevity/Occult
        9: ["Jupiter"],                # Dharmakaraka - Father/Dharma/Guru
        10: ["Sun", "Mercury"],        # Karmakaraka - Career/Fame
        11: ["Jupiter"],               # Labhakaraka - Gains/Fulfillment
        12: ["Saturn"]                 # Vyayakaraka - Loss/Liberation/Foreign
    }
    
    # House classifications
    KENDRA_HOUSES = {1, 4, 7, 10}
    TRIKONA_HOUSES = {1, 5, 9}
    UPACHAYA_HOUSES = {3, 6, 10, 11}
    DUSTHANA_HOUSES = {6, 8, 12}
    MARAKA_HOUSES = {2, 7}
    
    # Natural benefics and malefics
    NATURAL_BENEFICS = {"Jupiter", "Venus", "Mercury"}  # Mercury context-dependent
    NATURAL_MALEFICS = {"Sun", "Mars", "Saturn", "Rahu", "Ketu"}
    
    def __init__(self, planets_data: Dict, house_data: Dict):
        self.planets_data = planets_data
        self.house_data = house_data
    
    def get_strength_rating_from_rupas(self, rupas: float) -> StrengthRating:
        """Convert Rupa values to strength ratings based on BPHS"""
        if rupas > 600:
            return StrengthRating.EXCELLENT
        elif rupas > 450:
            return StrengthRating.GOOD
        elif rupas > 300:
            return StrengthRating.AVERAGE
        elif rupas > 150:
            return StrengthRating.BAD
        else:
            return StrengthRating.VERY_BAD
    
    def get_shadbala_rating(self, shadbala: float) -> StrengthRating:
        """Convert Shadbala values to strength ratings"""
        shadbala = float(shadbala)
        if shadbala > 500:
            return StrengthRating.EXCELLENT
        elif shadbala > 400:
            return StrengthRating.GOOD
        elif shadbala > 300:
            return StrengthRating.AVERAGE
        elif shadbala > 200:
            return StrengthRating.BAD
        else:
            return StrengthRating.VERY_BAD
    
    def is_planet_benefic_contextual(self, planet: str) -> bool:
        """Determine if planet is benefic considering context"""
        if planet in self.NATURAL_BENEFICS:
            if planet == "Mercury":
                # Mercury benefic when not with malefics
                planet_data = self.planets_data.get(planet, {})
                return not planet_data.safe_get('IsPlanetConjunctWithMaleficPlanets', False)
            return True
        elif planet == "Moon":
            # Moon benefic when more than 50% illuminated (approximation)
            planet_data = self.planets_data.get(planet, {})
            paksha_bala = float(planet_data.safe_get('PlanetPakshaBala', 0))
            return paksha_bala > 30  # Approximation for bright moon
        return False
    
    def analyze_bhava_strength(self, house_num: int) -> Tuple[StrengthRating, str, int]:
        """Step 1: Analyze Bhava (House) Strength"""
        house_key = str(house_num)
        house_info = self.house_data.get(house_key, {})
        
        # Base strength from HouseStrength
        base_strength = house_info.safe_get('HouseStrength', 0)
        base_rating = self.get_strength_rating_from_rupas(float(base_strength))
        
        modifier_points = 0
        explanations = []
        
        # Step 2: Analyze planets in house
        planets_in_house = house_info.safe_get('PlanetsInHouseBasedOnSign', [])
        benefic_count = 0
        malefic_count = 0
        
        for planet in planets_in_house:
            planet_data = self.planets_data.get(planet, {})
            
            if self.is_planet_benefic_contextual(planet):
                modifier_points += 2
                benefic_count += 1
            else:
                modifier_points -= 1
                malefic_count += 1
            
            # Exaltation/Debilitation
            if planet_data.safe_get('IsPlanetExaltedSign', False):
                modifier_points += 3
                explanations.append(f"{planet} exalted (+3)")
            elif planet_data.safe_get('IsPlanetDebilitated', False):
                modifier_points -= 3
                explanations.append(f"{planet} debilitated (-3)")
            
            # Own sign/Moolatrikona
            if planet_data.safe_get('IsPlanetInOwnSign', False):
                modifier_points += 2
                explanations.append(f"{planet} in own sign (+2)")
            elif planet_data.safe_get('IsPlanetInMoolatrikona', False):
                modifier_points += 1
                explanations.append(f"{planet} in Moolatrikona (+1)")
        
        if benefic_count > 0:
            explanations.append(f"{benefic_count} benefic(s) in house (+{benefic_count*2})")
        if malefic_count > 0:
            explanations.append(f"{malefic_count} malefic(s) in house (-{malefic_count})")
        
        # Step 3: Analyze aspecting planets
        aspecting_planets = house_info.safe_get('PlanetsAspectingHouse', [])
        
        for planet in aspecting_planets:
            planet_data = self.planets_data.get(planet, {})
            
            if self.is_planet_benefic_contextual(planet):
                modifier_points += 2
                explanations.append(f"{planet} (benefic) aspects (+2)")
            else:
                modifier_points -= 1
                explanations.append(f"{planet} (malefic) aspects (-1)")
            
            # Exalted/debilitated aspects
            if planet_data.safe_get('IsPlanetExaltedSign', False):
                modifier_points += 2
                explanations.append(f"Exalted {planet} aspects (+2)")
            elif planet_data.safe_get('IsPlanetDebilitated', False):
                modifier_points -= 2
                explanations.append(f"Debilitated {planet} aspects (-2)")
        
        # Step 4: House classification
        if house_num in self.KENDRA_HOUSES:
            modifier_points += 2
            explanations.append("Kendra house (+2)")
        if house_num in self.TRIKONA_HOUSES:
            modifier_points += 3
            explanations.append("Trikona house (+3)")
        if house_num in self.UPACHAYA_HOUSES:
            modifier_points += 1
            explanations.append("Upachaya house (+1)")
        if house_num in self.DUSTHANA_HOUSES:
            modifier_points -= 2
            explanations.append("Dusthana house (-2)")
        if house_num in self.MARAKA_HOUSES:
            modifier_points -= 1
            explanations.append("Maraka house (-1)")
        if house_num == 1:
            modifier_points += 1
            explanations.append("First house - most important (+1)")
        
        explanation = f"Base: {base_rating.value} ({float(base_strength):.1f} Rupas). " + "; ".join(explanations)
        
        return base_rating, explanation, modifier_points
    
    def analyze_bhavesh_strength(self, house_num: int) -> Tuple[StrengthRating, str, int]:
        """Step 2: Analyze Bhavesh (House Lord) Strength"""
        house_key = str(house_num)
        house_info = self.house_data.get(house_key, {})
        
        # Get house lord
        lord_info = house_info.safe_get_nested('LordOfHouse')
        if not lord_info:
            return StrengthRating.VERY_BAD, "House lord not found", -10
        
        lord_name = lord_info.Name
        planet_data = self.planets_data.get(lord_info.Name, {})
        # print("ABC", lord_name, self.planets_data.keys())
        
        if not planet_data:
            return StrengthRating.VERY_BAD, f"Data for lord {lord_name} not found", -10
        
        # Base Shadbala strength
        shadbala = planet_data.safe_get('PlanetShadbalaPinda', 0)
        base_rating = self.get_shadbala_rating(shadbala)
        
        modifier_points = 0
        explanations = [f"Lord: {lord_name}"]
        
        # Step 3: Positional strength
        if planet_data.safe_get('IsPlanetInOwnSign', False):
            modifier_points += 3
            explanations.append("In own sign (+3)")
        elif planet_data.safe_get('IsPlanetExaltedSign', False):
            modifier_points += 4
            explanations.append("In exaltation (+4)")
        elif planet_data.safe_get('IsPlanetInMoolatrikona', False):
            modifier_points += 2
            explanations.append("In Moolatrikona (+2)")
        elif planet_data.safe_get('IsPlanetInFriendSign', False):
            modifier_points += 1
            explanations.append("In friend's sign (+1)")
        elif planet_data.safe_get('IsPlanetInEnemySign', False):
            modifier_points -= 1
            explanations.append("In enemy's sign (-1)")
        elif planet_data.safe_get('IsPlanetDebilitated', False):
            modifier_points -= 4
            explanations.append("In debilitation (-4)")
        
        # Step 4: House position of lord
        lord_house = planet_data.safe_get('HousePlanetOccupiesBasedOnSign', '')
        if lord_house:
            lord_house_num = int(lord_house.replace('House', '')) if 'House' in lord_house else 0
            
            if lord_house_num == house_num:
                modifier_points += 2
                explanations.append("In own house (+2)")
            elif lord_house_num in self.KENDRA_HOUSES:
                modifier_points += 2
                explanations.append("In Kendra (+2)")
            elif lord_house_num in self.TRIKONA_HOUSES:
                modifier_points += 3
                explanations.append("In Trikona (+3)")
            elif lord_house_num in self.UPACHAYA_HOUSES:
                modifier_points += 1
                explanations.append("In Upachaya (+1)")
            elif lord_house_num in self.DUSTHANA_HOUSES:
                modifier_points -= 2
                explanations.append("In Dusthana (-2)")
        
        # Step 5: Aspectual strength
        if planet_data.safe_get('IsPlanetAspectedByBeneficPlanets', False):
            modifier_points += 1
            explanations.append("Aspected by benefics (+1)")
        if planet_data.safe_get('IsPlanetAspectedByMaleficPlanets', False):
            modifier_points -= 1
            explanations.append("Aspected by malefics (-1)")
        
        if planet_data.safe_get('IsPlanetConjunctWithBeneficPlanets', False):
            modifier_points += 1
            explanations.append("Conjunct benefics (+1)")
        if planet_data.safe_get('IsPlanetConjunctWithMaleficPlanets', False):
            modifier_points -= 1
            explanations.append("Conjunct malefics (-1)")
        
        # Step 6: Planetary states (Avasta)
        if not planet_data.safe_get('IsPlanetAfflicted', True):
            modifier_points += 1
            explanations.append("Unafflicted (+1)")
        else:
            modifier_points -= 2
            explanations.append("Afflicted (-2)")
        
        if planet_data.safe_get('IsPlanetCombust', False):
            modifier_points -= 3
            explanations.append("Combust (-3)")
        
        if planet_data.safe_get('IsPlanetRetrograde', False):
            if lord_name in ["Jupiter", "Venus", "Mercury"]:
                modifier_points += 1
                explanations.append(f"Retrograde {lord_name} (+1)")
            else:
                modifier_points -= 1
                explanations.append(f"Retrograde {lord_name} (-1)")
        
        # Specific Avasta states
        if planet_data.safe_get('IsPlanetInLajjitaAvasta', False):
            modifier_points -= 2
            explanations.append("Lajjita (Shamed) (-2)")
        if planet_data.safe_get('IsPlanetInGarvitaAvasta', False):
            modifier_points += 1
            explanations.append("Garvita (Proud) (+1)")
        if planet_data.safe_get('IsPlanetInKshobhitaAvasta', False):
            modifier_points -= 1
            explanations.append("Kshobhita (Agitated) (-1)")
        if planet_data.safe_get('IsPlanetInKshuditaAvasta', False):
            modifier_points -= 2
            explanations.append("Kshudita (Starved) (-2)")
        
        explanation = f"Base: {base_rating.value} ({float(shadbala):.1f} Rupas). " + "; ".join(explanations)
        
        return base_rating, explanation, modifier_points
    
    def analyze_karaka_strength(self, house_num: int) -> Tuple[StrengthRating, str, int]:
        """Step 3: Analyze Karaka (Significator) Strength"""
        karakas = self.NATURAL_KARAKAS.get(house_num, [])
        if not karakas:
            return StrengthRating.AVERAGE, "No natural karaka defined", 0
        
        # For houses with multiple karakas, take the strongest one
        best_rating = StrengthRating.VERY_BAD
        best_explanation = ""
        best_points = -10
        
        for karaka in karakas:
            rating, explanation, points = self._analyze_single_karaka(karaka, house_num)
            if points > best_points:
                best_rating = rating
                best_explanation = explanation
                best_points = points
        
        return best_rating, best_explanation, best_points
    
    def _analyze_single_karaka(self, karaka: str, house_num: int) -> Tuple[StrengthRating, str, int]:
        """Analyze individual karaka strength"""
        planet_data = self.planets_data.get(karaka, {})
        if not planet_data:
            return StrengthRating.VERY_BAD, f"Karaka {karaka} data not found", -10
        
        # Base Shadbala
        shadbala = planet_data.safe_get('PlanetShadbalaPinda', 0)
        base_rating = self.get_shadbala_rating(shadbala)
        
        modifier_points = 0
        explanations = [f"Karaka: {karaka}"]
        
        # Sign position
        if planet_data.safe_get('IsPlanetInOwnSign', False):
            modifier_points += 3
            explanations.append("In own sign (+3)")
        elif planet_data.safe_get('IsPlanetExaltedSign', False):
            modifier_points += 4
            explanations.append("In exaltation (+4)")
        elif planet_data.safe_get('IsPlanetInMoolatrikona', False):
            modifier_points += 2
            explanations.append("In Moolatrikona (+2)")
        elif planet_data.safe_get('IsPlanetInFriendSign', False):
            modifier_points += 1
            explanations.append("In friend's sign (+1)")
        elif planet_data.safe_get('IsPlanetInEnemySign', False):
            modifier_points -= 1
            explanations.append("In enemy's sign (-1)")
        elif planet_data.safe_get('IsPlanetDebilitated', False):
            modifier_points -= 4
            explanations.append("In debilitation (-4)")
        
        # House position relative to signified house
        karaka_house = planet_data.safe_get('HousePlanetOccupiesBasedOnSign', '')
        if karaka_house:
            karaka_house_num = int(karaka_house.replace('House', '')) if 'House' in karaka_house else 0
            
            if karaka_house_num == house_num:
                modifier_points += 2
                explanations.append("In signified house (+2)")
            else:
                # Calculate relative position
                relative_pos = (karaka_house_num - house_num) % 12
                if relative_pos == 0:
                    pass  # Same house, already handled
                elif relative_pos in [4, 7, 10]:  # Kendra
                    modifier_points += 1
                    explanations.append("In Kendra from signified house (+1)")
                elif relative_pos in [5, 9]:  # Trikona
                    modifier_points += 2
                    explanations.append("In Trikona from signified house (+2)")
                elif relative_pos in [6, 8]:  # 6th, 8th
                    modifier_points -= 2
                    explanations.append("In 6th/8th from signified house (-2)")
                elif relative_pos in [3, 11]:  # 3rd, 11th
                    modifier_points += 1
                    explanations.append("In 3rd/11th from signified house (+1)")
        
        # Special karaka considerations
        if karaka == "Sun" and planet_data.safe_get('IsPlanetCombust', False):
            # Sun can't be combust, but check if it's combusting others
            modifier_points -= 1
            explanations.append("Combusting other planets (-1)")
        
        if karaka == "Moon":
            paksha_bala = float(planet_data.safe_get('PlanetPakshaBala', 0))
            if paksha_bala > 45:
                modifier_points += 1
                explanations.append("Bright Moon (+1)")
            elif paksha_bala < 15:
                modifier_points -= 1
                explanations.append("Dark Moon (-1)")
        
        # General afflictions for karakas
        if planet_data.safe_get('IsPlanetCombust', False):
            modifier_points -= 3
            explanations.append("Combust karaka (-3)")
        
        if planet_data.safe_get('IsPlanetRetrograde', False):
            if karaka == "Jupiter":
                modifier_points -= 1
                explanations.append("Retrograde Jupiter affects wisdom (-1)")
            # Other retrograde rules as per standard
        
        # Rahu/Ketu conjunction (karaka eclipse)
        conjunctions = planet_data.safe_get('PlanetsInConjunction', [])
        if 'Rahu' in conjunctions or 'Ketu' in conjunctions:
            modifier_points -= 2
            explanations.append("Karaka eclipsed by Rahu/Ketu (-2)")
        
        explanation = f"Base: {base_rating.value} ({float(shadbala):.1f} Rupas). " + "; ".join(explanations)
        
        return base_rating, explanation, modifier_points
    
    def adjust_rating_by_points(self, base_rating: StrengthRating, points: int) -> StrengthRating:
        """Adjust rating based on modifier points"""
        ratings = [StrengthRating.VERY_BAD, StrengthRating.BAD, StrengthRating.AVERAGE, 
                  StrengthRating.GOOD, StrengthRating.EXCELLENT]
        
        current_index = ratings.index(base_rating)
        
        if points >= 3:
            adjustment = min(1, len(ratings) - 1 - current_index)
        elif points <= -3:
            adjustment = max(-1, -current_index)
        else:
            adjustment = 0
        
        return ratings[current_index + adjustment]
    
    def calculate_overall_strength(self, bhava_rating: StrengthRating, 
                                 bhavesh_rating: StrengthRating, 
                                 karaka_rating: StrengthRating) -> StrengthRating:
        """Calculate weighted average: Bhava (40%), Bhavesh (35%), Karaka (25%)"""
        rating_values = {
            StrengthRating.VERY_BAD: 1,
            StrengthRating.BAD: 2,
            StrengthRating.AVERAGE: 3,
            StrengthRating.GOOD: 4,
            StrengthRating.EXCELLENT: 5
        }
        
        weighted_score = (rating_values[bhava_rating] * 0.4 + 
                         rating_values[bhavesh_rating] * 0.35 + 
                         rating_values[karaka_rating] * 0.25)
        
        if weighted_score >= 4.5:
            return StrengthRating.EXCELLENT
        elif weighted_score >= 3.5:
            return StrengthRating.GOOD
        elif weighted_score >= 2.5:
            return StrengthRating.AVERAGE
        elif weighted_score >= 1.5:
            return StrengthRating.BAD
        else:
            return StrengthRating.VERY_BAD
    
    def get_remedial_suggestions(self, house_num: int, overall_rating: StrengthRating) -> List[str]:
        """Provide remedial suggestions for weak houses"""
        if overall_rating in [StrengthRating.GOOD, StrengthRating.EXCELLENT]:
            return []
        
        suggestions = []
        house_key = str(house_num)
        house_info = self.house_data.get(house_key, {})
        
        # Get house lord for remedies
        lord_info = house_info.safe_get_nested('LordOfHouse')
        lord_name = lord_info.get('Name', '') if isinstance(lord_info, dict) else str(lord_info)
        
        if lord_name:
            suggestions.append(f"Strengthen house lord {lord_name} through appropriate gemstones, mantras, and charity")
        
        # Karaka-based remedies
        karakas = self.NATURAL_KARAKAS.get(house_num, [])
        for karaka in karakas:
            suggestions.append(f"Worship and strengthen karaka {karaka} through devotional practices")
        
        # House-specific remedies
        if house_num in self.DUSTHANA_HOUSES:
            suggestions.append("Perform regular charity and spiritual practices to mitigate dusthana effects")
        
        if house_num == 1:
            suggestions.append("Focus on personal development, health, and spiritual practices")
        elif house_num == 4:
            suggestions.append("Honor mother, maintain good relationships with family, and invest in property")
        elif house_num == 7:
            suggestions.append("Work on partnership harmony and relationship skills")
        elif house_num == 10:
            suggestions.append("Focus on career development and professional skills")
        
        return suggestions
    
    def analyze_house(self, house_num: int) -> HouseAnalysisResult:
        """Complete analysis of a single house"""
        # Analyze each component
        bhava_rating, bhava_explanation, bhava_points = self.analyze_bhava_strength(house_num)
        bhavesh_rating, bhavesh_explanation, bhavesh_points = self.analyze_bhavesh_strength(house_num)
        karaka_rating, karaka_explanation, karaka_points = self.analyze_karaka_strength(house_num)
        
        # Apply point adjustments
        final_bhava = self.adjust_rating_by_points(bhava_rating, bhava_points)
        final_bhavesh = self.adjust_rating_by_points(bhavesh_rating, bhavesh_points)
        final_karaka = self.adjust_rating_by_points(karaka_rating, karaka_points)
        
        # Calculate overall strength
        overall_strength = self.calculate_overall_strength(final_bhava, final_bhavesh, final_karaka)
        
        # Identify key strengths and weaknesses
        strengths = []
        weaknesses = []
        
        if final_bhava in [StrengthRating.GOOD, StrengthRating.EXCELLENT]:
            strengths.append("Strong house foundation (Bhava)")
        elif final_bhava in [StrengthRating.BAD, StrengthRating.VERY_BAD]:
            weaknesses.append("Weak house foundation (Bhava)")
        
        if final_bhavesh in [StrengthRating.GOOD, StrengthRating.EXCELLENT]:
            strengths.append("Strong house lord (Bhavesh)")
        elif final_bhavesh in [StrengthRating.BAD, StrengthRating.VERY_BAD]:
            weaknesses.append("Weak house lord (Bhavesh)")
        
        if final_karaka in [StrengthRating.GOOD, StrengthRating.EXCELLENT]:
            strengths.append("Strong natural significator (Karaka)")
        elif final_karaka in [StrengthRating.BAD, StrengthRating.VERY_BAD]:
            weaknesses.append("Weak natural significator (Karaka)")
        
        # Get remedial suggestions
        remedies = self.get_remedial_suggestions(house_num, overall_strength)
        
        return HouseAnalysisResult(
            bhava_strength=final_bhava,
            bhavesh_strength=final_bhavesh,
            karaka_strength=final_karaka,
            overall_strength=overall_strength,
            bhava_explanation=bhava_explanation,
            bhavesh_explanation=bhavesh_explanation,
            karaka_explanation=karaka_explanation,
            key_strengths=strengths,
            key_weaknesses=weaknesses,
            remedial_suggestions=remedies
        )
    
    def analyze_all_houses(self) -> Dict[int, HouseAnalysisResult]:
        """Analyze all 12 houses"""
        results = {}
        for house_num in range(1, 13):
            results[house_num] = self.analyze_house(house_num)
        return results
    
    def generate_comprehensive_report(self) -> str:
        """Generate a comprehensive report for all houses"""
        results = self.analyze_all_houses()
        
        report = "# BPHS COMPLIANT HOUSE STRENGTH ANALYSIS REPORT\n"
        report += "=" * 50 + "\n\n"
        
        for house_num in range(1, 13):
            result = results[house_num]
            report += f"## HOUSE {house_num} ANALYSIS\n"
            report += "-" * 30 + "\n\n"
            
            report += f"**Overall Assessment: {result.overall_strength.value}**\n\n"
            
            report += f"### Bhava Strength: {result.bhava_strength.value}\n"
            report += f"{result.bhava_explanation}\n\n"
            
            report += f"### Bhavesh Strength: {result.bhavesh_strength.value}\n"
            report += f"{result.bhavesh_explanation}\n\n"
            
            report += f"### Karaka Strength: {result.karaka_strength.value}\n"
            report += f"{result.karaka_explanation}\n\n"
            
            if result.key_strengths:
                report += "**Key Strengths:**\n"
                for strength in result.key_strengths:
                    report += f"• {strength}\n"
                report += "\n"
            
            if result.key_weaknesses:
                report += "**Key Weaknesses:**\n"
                for weakness in result.key_weaknesses:
                    report += f"• {weakness}\n"
                report += "\n"
            
            if result.remedial_suggestions:
                report += "**Remedial Suggestions:**\n"
                for suggestion in result.remedial_suggestions:
                    report += f"• {suggestion}\n"
                report += "\n"
            
            report += "\n" + "=" * 50 + "\n\n"
        
        return report
    
def example_usage(sample_planets_data, sample_house_data):
    analyzer = BPHSHouseAnalyzer(sample_planets_data, sample_house_data)
    
    # Analyze a single house
    result = analyzer.analyze_house(1)
    print(f"House 1 Overall Strength: {result.overall_strength.value}")
    
    # Generate full report
    report = analyzer.generate_comprehensive_report()
    print(report)