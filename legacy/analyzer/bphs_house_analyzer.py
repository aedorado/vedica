"""
BPHS Compliant House Strength Analysis Algorithm
Based on Brihat Parashara Hora Shastra Classical Principles
"""

from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from enum import Enum

class AnalysisContext(Enum):
    BHAVESH = "bhavesh"      # House lord analysis
    KARAKA = "karaka"        # Natural significator analysis
    GENERAL = "general"      # General planetary strength

class StrengthRating(Enum):
    VERY_BAD = "critical"
    BAD = "weak"
    AVERAGE = "moderate"
    GOOD = "strong"
    EXCELLENT = "exceptional"

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

    STRENGTH_LABELS = {
        StrengthRating.VERY_BAD: "🔴 Critical",
        StrengthRating.BAD: "🟠 Weak",
        StrengthRating.AVERAGE: "🟡 Moderate",
        StrengthRating.GOOD: "🔵 Strong",
        StrengthRating.EXCELLENT: "🟢 Exceptional"
    }
    
    def __init__(self, planets_data: Dict, house_data: Dict):
        self.planets_data = planets_data
        self.house_data = house_data

        self.shadbala_rating_thresholds = {
            AnalysisContext.BHAVESH: {
                # House lords: Sthana+Kala heavy weighting creates higher scores
                # Expected range: 50-220, most planets 90-160
                'excellent': 170,
                'good': 140, 
                'average': 110,
                'bad': 80
            },
            AnalysisContext.KARAKA: {
                # Karaka: Naisargika+Ochcha heavy weighting, more varied distribution
                # Expected range: 40-200, most planets 80-150
                'excellent': 160,
                'good': 130,
                'average': 100, 
                'bad': 70
            },
            AnalysisContext.GENERAL: {
                # General: Balanced weighting, standard distribution
                # Expected range: 50-200, most planets 90-140
                'excellent': 160,
                'good': 130,
                'average': 100,
                'bad': 70
            }
        }
    
    def calculate_varga_strength(self, planet_name: str) -> Tuple[float, str]:
        """Calculate Varga strength using Saptavargaja Bala"""
        planet_data = self.planets_data.get(planet_name, {})
        if not planet_data:
            return 0.0, "Planet data not found"
        
        # Get Saptavargaja Bala (available for all planets)
        saptavargaja_bala = float(planet_data.safe_get('PlanetSaptavargajaBala', 0))
        
        if saptavargaja_bala == 0:
            return 0.0, "Saptavargaja Bala not available"
        
        # Convert to rating system based on traditional Saptavargaja Bala thresholds
        # Maximum possible Saptavargaja Bala is 210 (7 vargas × 30 points each)
        if saptavargaja_bala >= 180:  # 85%+
            rating = StrengthRating.EXCELLENT
        elif saptavargaja_bala >= 135:  # 64%+
            rating = StrengthRating.GOOD
        elif saptavargaja_bala >= 90:   # 43%+
            rating = StrengthRating.AVERAGE
        elif saptavargaja_bala >= 45:   # 21%+
            rating = StrengthRating.BAD
        else:                           # <21%
            rating = StrengthRating.VERY_BAD
        
        # Calculate percentage for clearer understanding
        percentage = (saptavargaja_bala / 210) * 100
        
        explanation = f"Saptavargaja Bala: {saptavargaja_bala:.1f}/210 ({percentage:.1f}%) - {rating.value}"
        
        return saptavargaja_bala, explanation

    def get_ashtakavarga_weight(self, bindu: Optional[int]) -> float:
        """Convert Ashtakavarga Bindu into a scaling weight for influence."""
        if bindu is None:
            return 1.0  # Default neutral weight
        if bindu >= 6:
            return 1.5  # Strong
        elif bindu >= 4:
            return 1.0  # Moderate
        elif bindu >= 2:
            return 0.5  # Weak
        else:
            return 0.2  # Very weak

    def get_strength_rating_from_rupas(self, rupas: float) -> StrengthRating:
        """Convert Rupa values to strength ratings with adjusted thresholds"""
        if rupas > 500:        # Was 600
            return StrengthRating.EXCELLENT
        elif rupas > 400:      # Was 450
            return StrengthRating.GOOD
        elif rupas > 250:      # Was 300
            return StrengthRating.AVERAGE
        elif rupas > 120:      # Was 150
            return StrengthRating.BAD
        else:
            return StrengthRating.VERY_BAD
        
    def get_saptavargaja_rating(self, saptavargaja_bala: float) -> StrengthRating:
        """Convert Saptavargaja Bala to strength ratings with realistic thresholds"""
        # Based on your example: 105.0/210 (50%) should be AVERAGE
        if saptavargaja_bala >= 150:    # 71%+
            return StrengthRating.EXCELLENT
        elif saptavargaja_bala >= 120:  # 57%+
            return StrengthRating.GOOD
        elif saptavargaja_bala >= 90:   # 43%+ - your 105.0 will be GOOD
            return StrengthRating.AVERAGE
        elif saptavargaja_bala >= 60:   # 29%+
            return StrengthRating.BAD
        else:                           # <29%
            return StrengthRating.VERY_BAD
        
    def get_weighted_house_rating(self, bhava_rating: StrengthRating, 
                            bhavesh_rating: StrengthRating, 
                            karaka_rating: StrengthRating) -> StrengthRating:
        """Get weighted house rating with more balanced thresholds"""
        rating_values = {
            StrengthRating.EXCELLENT: 5,
            StrengthRating.GOOD: 4,
            StrengthRating.AVERAGE: 3,
            StrengthRating.BAD: 2,
            StrengthRating.VERY_BAD: 1
        }
        
        weighted_score = (rating_values[bhava_rating] * 0.4 + 
                        rating_values[bhavesh_rating] * 0.35 + 
                        rating_values[karaka_rating] * 0.25)
        
        # More realistic weighted score thresholds
        if weighted_score >= 4.2:      # Was 4.5
            return StrengthRating.EXCELLENT
        elif weighted_score >= 3.2:   # Was 3.5
            return StrengthRating.GOOD
        elif weighted_score >= 2.3:   # Was 2.5 - more balanced distribution
            return StrengthRating.AVERAGE
        elif weighted_score >= 1.5:   # Keep same
            return StrengthRating.BAD
        else:
            return StrengthRating.VERY_BAD
        
    def get_balanced_weighted_house_rating(self, bhava_rating: StrengthRating, 
                                     bhavesh_rating: StrengthRating, 
                                     karaka_rating: StrengthRating) -> StrengthRating:
        """Get weighted house rating with very balanced thresholds"""
        rating_values = {
            StrengthRating.EXCELLENT: 5,
            StrengthRating.GOOD: 4,
            StrengthRating.AVERAGE: 3,
            StrengthRating.BAD: 2,
            StrengthRating.VERY_BAD: 1
        }
        
        weighted_score = (rating_values[bhava_rating] * 0.4 + 
                        rating_values[bhavesh_rating] * 0.35 + 
                        rating_values[karaka_rating] * 0.25)
        
        # Even more balanced - aims for normal distribution
        if weighted_score >= 4.0:      # Top 20%
            return StrengthRating.EXCELLENT
        elif weighted_score >= 3.0:   # Next 30%
            return StrengthRating.GOOD
        elif weighted_score >= 2.1:   # Middle 30%
            return StrengthRating.AVERAGE
        elif weighted_score >= 1.4:   # Next 15%
            return StrengthRating.BAD
        else:                          # Bottom 5%
            return StrengthRating.VERY_BAD

    def get_detailed_shadbala_analysis(self, planet_name: str, context: AnalysisContext = AnalysisContext.GENERAL) -> Tuple[StrengthRating, str, float]:
        """
        Perform enhanced Shadbala analysis with context-specific weighting.

        WEIGHTING STRATEGIES:
        
        BHAVESH (House Lords): Emphasizes positional and temporal strength
        - Sthana Bala (35%): Critical for house rulership effectiveness
        - Kala Bala (25%): Timing and seasonal factors matter for house results
        - Dig Bala (20%): Directional strength affects house manifestation
        - Ochcha Bala (10%): Exaltation contributes but not primary
        - Drik Bala (7%): Aspects received, secondary importance
        - Naisargika Bala (3%): Natural strength, least relevant for house lords
        
        KARAKA (Natural Significators): Emphasizes inherent and natural strength
        - Naisargika Bala (30%): Natural strength is primary for karaka functions
        - Ochcha Bala (25%): Exaltation/debilitation crucial for karaka capacity
        - Sthana Bala (20%): Positional strength supports karaka role
        - Kala Bala (15%): Temporal factors matter but secondary
        - Drik Bala (7%): Aspects affect karaka expression
        - Dig Bala (3%): Directional strength least important for karaka
        
        GENERAL: Balanced weighting for overall planetary assessment
        """
        planet_data = self.planets_data.get(planet_name, {})
        if not planet_data:
            return StrengthRating.VERY_BAD, "Planet data not found", 0.0

        # Extract individual Shadbala components
        sthana_bala = float(planet_data.safe_get('PlanetSthanaBala', 0))
        dig_bala = float(planet_data.safe_get('PlanetDigBala', 0))
        kala_bala = float(planet_data.safe_get('PlanetKalaBala', 0))
        naisargika_bala = float(planet_data.safe_get('PlanetNaisargikaBala', 0))
        drik_bala = float(planet_data.safe_get('PlanetDrikBala', 0))
        ochcha_bala = float(planet_data.safe_get('PlanetOchchaBala', 0))

        # Compute raw total Shadbala
        total_shadbala = sthana_bala + dig_bala + kala_bala + naisargika_bala + drik_bala + ochcha_bala
        raw_rating = self.get_shadbala_rating(total_shadbala)

        # Context-specific weighting
        if context == AnalysisContext.BHAVESH:
            # House lords: Emphasize positional and temporal strength
            weighted_score = (
                sthana_bala * 0.35 +      # Most important for house rulership
                kala_bala * 0.25 +        # Timing matters for house results
                dig_bala * 0.20 +         # Directional strength for manifestation
                ochcha_bala * 0.10 +      # Exaltation helps but secondary
                drik_bala * 0.07 +        # Aspects received
                naisargika_bala * 0.03    # Natural strength least relevant
            )
            context_note = "House Lord Analysis"
            
        elif context == AnalysisContext.KARAKA:
            # Natural significators: Emphasize inherent strength
            weighted_score = (
                naisargika_bala * 0.30 +  # Primary for karaka functions
                ochcha_bala * 0.25 +      # Exaltation crucial for capacity
                sthana_bala * 0.20 +      # Positional strength supports
                kala_bala * 0.15 +        # Temporal factors secondary
                drik_bala * 0.07 +        # Aspects affect expression
                dig_bala * 0.03           # Directional least important
            )
            context_note = "Karaka Analysis"
            
        else:  # GENERAL
            # Balanced approach for overall assessment
            weighted_score = (
                sthana_bala * 0.30 +
                dig_bala * 0.20 +
                kala_bala * 0.20 +
                ochcha_bala * 0.15 +
                drik_bala * 0.10 +
                naisargika_bala * 0.05
            )
            context_note = "General Analysis"

        weighted_rating = self.get_weighted_shadbala_rating(weighted_score, context)

        # Enhanced explanation with context
        breakdown = (
            f"Sthana: {sthana_bala:.1f}, Dig: {dig_bala:.1f}, Kala: {kala_bala:.1f}, "
            f"Ochcha: {ochcha_bala:.1f}, Drik: {drik_bala:.1f}, Naisargika: {naisargika_bala:.1f}"
        )
        
        explanation = (
            f"{context_note} | Total: {total_shadbala:.1f} ({raw_rating.name}), "
            f"Weighted: {weighted_score:.1f} ({weighted_rating.name}) | {breakdown}"
        )

        return weighted_rating, explanation, weighted_score
    
    def calculate_ishta_kashta_strength(self, planet_name: str) -> Tuple[float, str]:
        """Calculate planet strength using Ishta-Kashta scores"""
        planet_data = self.planets_data.get(planet_name, {})
        if not planet_data:
            return 0.0, "Planet data not found"
        
        ishta_score = float(planet_data.safe_get('PlanetIshtaScore', 0))
        kashta_score = float(planet_data.safe_get('PlanetKashtaScore', 0))
        
        total_score = ishta_score + kashta_score
        if total_score == 0:
            return 0.5, "No Ishta-Kashta data"
        
        # Calculate benefic ratio
        benefic_ratio = ishta_score / total_score
        
        # Convert to modifier points
        if benefic_ratio >= 0.75:
            modifier = 3
            rating = "Highly Beneficial"
        elif benefic_ratio >= 0.65:
            modifier = 2
            rating = "Beneficial"
        elif benefic_ratio >= 0.55:
            modifier = 1
            rating = "Mildly Beneficial"
        elif benefic_ratio >= 0.45:
            modifier = 0
            rating = "Neutral"
        elif benefic_ratio >= 0.35:
            modifier = -1
            rating = "Mildly Harmful"
        elif benefic_ratio >= 0.25:
            modifier = -2
            rating = "Harmful"
        else:
            modifier = -3
            rating = "Highly Harmful"
        
        explanation = f"Ishta: {ishta_score:.1f}, Kashta: {kashta_score:.1f}, Ratio: {benefic_ratio:.2f} ({rating})"
        
        return modifier, explanation

    def get_shadbala_rating(self, shadbala: float) -> StrengthRating:
        """Convert Shadbala values to strength ratings with adjusted thresholds"""
        shadbala = float(shadbala)
        # Based on your example: 450.4 should be GOOD
        if shadbala > 500:     # Was 500 (keep)
            return StrengthRating.EXCELLENT
        elif shadbala > 350:   # Was 400 - your 450.4 will now be GOOD
            return StrengthRating.GOOD
        elif shadbala > 250:   # Was 300
            return StrengthRating.AVERAGE
        elif shadbala > 150:   # Was 200
            return StrengthRating.BAD
        else:
            return StrengthRating.VERY_BAD
        
    def get_weighted_shadbala_rating(self, weighted_score: float, context: AnalysisContext) -> StrengthRating:
        """
        Rate weighted Shadbala scores with context-specific thresholds.
        
        Different contexts produce different score distributions:
        - BHAVESH: Higher scores due to Sthana+Kala emphasis
        - KARAKA: More variable due to natural strength variations  
        - GENERAL: Balanced distribution
        
        Args:
            weighted_score: The calculated weighted score
            context: Analysis context determining threshold set
        """
        weighted_score = max(0, float(weighted_score))
        thresholds = self.shadbala_rating_thresholds[context]
        
        if weighted_score > thresholds['excellent']:
            return StrengthRating.EXCELLENT
        elif weighted_score > thresholds['good']:
            return StrengthRating.GOOD
        elif weighted_score > thresholds['average']:
            return StrengthRating.AVERAGE
        elif weighted_score > thresholds['bad']:
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
        """Step 1: Analyze Bhava (House) Strength - Enhanced Version"""
        house_key = str(house_num)
        house_info = self.house_data.get(house_key, {})
        
        # Use direct HouseStrength if available
        house_strength = float(house_info.safe_get('HouseStrength', 0))
        if house_strength > 0:
            base_rating = self.get_strength_rating_from_rupas(house_strength)
            base_explanation = f"Direct House Strength: {house_strength:.1f}"
        else:
            # Fallback to your existing calculation
            base_strength = house_info.safe_get('HouseStrength', 0)
            base_rating = self.get_strength_rating_from_rupas(float(base_strength))
            base_explanation = f"Base: {base_rating.value} ({float(base_strength):.1f} Rupas)"
        
        modifier_points = 0
        explanations = [base_explanation]
        
        # Use HouseNatureScore if available
        nature_score = float(house_info.safe_get('HouseNatureScore', 0))
        if nature_score != 0:
            if nature_score > 0:
                modifier_points += 2
                explanations.append(f"Positive House Nature (+2)")
            else:
                modifier_points -= 1
                explanations.append(f"Negative House Nature (-1)")

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
        
        explanation = "; ".join(explanations)
        return base_rating, explanation, modifier_points
    
    def analyze_bhavesh_strength(self, house_num: int) -> Tuple[StrengthRating, str, int]:
        house_key = str(house_num)
        house_info = self.house_data.get(house_key, {})
        
        lord_info = house_info.safe_get_nested('LordOfHouse')
        if not lord_info:
            return StrengthRating.VERY_BAD, "House lord not found", -10
        
        lord_name = lord_info.Name if hasattr(lord_info, 'Name') else str(lord_info)
        
        # Use enhanced Shadbala analysis
        base_rating, shadbala_explanation, weighted_shadbala = self.get_detailed_shadbala_analysis(lord_name, AnalysisContext.BHAVESH)
        
        # Get Varga strength
        varga_strength, varga_explanation = self.calculate_varga_strength(lord_name)
        
        # Get Ishta-Kashta analysis
        ishta_kashta_points, ishta_kashta_explanation = self.calculate_ishta_kashta_strength(lord_name)
        
        # Get Avasta analysis
        avasta_points, avasta_explanation = self.calculate_avasta_strength(lord_name)
        
        modifier_points = ishta_kashta_points + avasta_points
        
        explanations = [
            f"Lord: {lord_name}",
            shadbala_explanation,
            varga_explanation,
            ishta_kashta_explanation,
            avasta_explanation
        ]
        
        planet_data = self.planets_data.get(lord_info.Name, {})
    
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
        
        explanation = "; ".join(explanations)
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
        
        # Use enhanced Shadbala analysis
        base_rating, shadbala_explanation, weighted_shadbala = self.get_detailed_shadbala_analysis(karaka, AnalysisContext.KARAKA)
        
        # Get Ishta-Kashta analysis
        ishta_kashta_points, ishta_kashta_explanation = self.calculate_ishta_kashta_strength(karaka)
        
        # Get Avasta analysis  
        avasta_points, avasta_explanation = self.calculate_avasta_strength(karaka)
        
        modifier_points = ishta_kashta_points + avasta_points
        
        explanations = [
            f"Karaka: {karaka}",
            shadbala_explanation,
            ishta_kashta_explanation,
            avasta_explanation
        ]
        
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
        
        explanation = "; ".join(explanations)
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
    
    def calculate_avasta_strength(self, planet_name: str) -> Tuple[int, str]:
        """Calculate weighted Avasta (planetary states) strength"""
        planet_data = self.planets_data.get(planet_name, {})
        if not planet_data:
            return 0, "Planet data not found"
        
        avasta_weights = {
            'IsPlanetInMuditaAvasta': 2,      # Delighted (+2)
            'IsPlanetInGarvitaAvasta': 1,     # Proud (+1)
            'IsPlanetInKshuditaAvasta': -3,   # Starved (-3)
            'IsPlanetInLajjitaAvasta': -2,    # Shamed (-2)
            'IsPlanetInKshobhitaAvasta': -1,  # Agitated (-1)
            'IsPlanetInTrashitaAvasta': -2,   # Frightened (-2)
        }
        
        total_points = 0
        active_avastas = []
        
        for avasta_key, weight in avasta_weights.items():
            if planet_data.safe_get(avasta_key, False):
                total_points += weight
                avasta_name = avasta_key.replace('IsPlanetIn', '').replace('Avasta', '')
                active_avastas.append(f"{avasta_name}({weight:+d})")
        
        # Additional Avasta from PlanetAvasta field if available
        planet_avasta = planet_data.safe_get('PlanetAvasta', '')
        if planet_avasta and not active_avastas:
            # Parse the avasta string (e.g., "KshuditaStarved, MuditaDelighted")
            if 'Kshudita' in planet_avasta:
                total_points -= 3
                active_avastas.append("Kshudita(-3)")
            if 'Mudita' in planet_avasta:
                total_points += 2
                active_avastas.append("Mudita(+2)")
        
        explanation = f"Avasta effects: {', '.join(active_avastas) if active_avastas else 'None'}"
        
        return total_points, explanation
    
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
        
        # Calculate overall strength using balanced weighted rating
        overall_strength = self.get_balanced_weighted_house_rating(final_bhava, final_bhavesh, final_karaka)
        
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
        )
    
    def analyze_all_houses(self) -> Dict[int, HouseAnalysisResult]:
        """Analyze all 12 houses"""
        results = {}
        for house_num in range(1, 13):
            results[house_num] = self.analyze_house(house_num)
        return results
    
    def generate_comprehensive_report(self) -> str:
        """Generate a structured and readable house strength analysis report"""

        def format_explanation(text: str) -> str:
            """Split semicolon-separated explanation into bullet points"""
            return '\n'.join(f"- {item.strip()}" for item in text.split(';') if item.strip())

        results = self.analyze_all_houses()

        report = "# 🏠 BPHS COMPLIANT HOUSE STRENGTH ANALYSIS REPORT\n"
        report += "=" * 60 + "\n\n"

        report += "### 🔍 Legend\n"
        report += "- 🟢 **Exceptional**: Top-tier strength\n"
        report += "- 🔵 **Strong**: Generally good\n"
        report += "- 🟡 **Moderate**: Average or mixed influence\n"
        report += "- 🟠 **Weak**: Needs improvement\n"
        report += "- 🔴 **Critical**: Very low strength, potentially harmful\n\n"
        report += "=" * 60 + "\n\n"

        for house_num in range(1, 13):
            result = results[house_num]
            report += f"## 🏡 HOUSE {house_num} ANALYSIS\n"
            report += "-" * 40 + "\n\n"

            report += f"**Overall Assessment:** {self.STRENGTH_LABELS[result.overall_strength]}\n\n"

            report += f"### 🏯 Bhava Strength: {self.STRENGTH_LABELS[result.bhava_strength]}\n"
            report += format_explanation(result.bhava_explanation) + "\n\n"

            report += f"### 🔱 Bhavesh Strength: {self.STRENGTH_LABELS[result.bhavesh_strength]}\n"
            report += format_explanation(result.bhavesh_explanation) + "\n\n"

            report += f"### 🌟 Karaka Strength: {self.STRENGTH_LABELS[result.karaka_strength]}\n"
            report += format_explanation(result.karaka_explanation) + "\n\n"

            if result.key_strengths:
                report += "**✅ Key Strengths:**\n"
                for strength in result.key_strengths:
                    report += f"- {strength}\n"
                report += "\n"

            if result.key_weaknesses:
                report += "**⚠️ Key Weaknesses:**\n"
                for weakness in result.key_weaknesses:
                    report += f"- {weakness}\n"
                report += "\n"

            report += "=" * 60 + "\n\n"

        return report
    
    def generate_summary_table(self) -> str:
        """Generate a house-wise strength summary with emoji and descriptive labels, with significations as 2nd column."""

        HOUSE_SIGNIFICATIONS = {
            1: "Self, Body, Vitality",
            2: "Wealth, Speech, Family",
            3: "Siblings, Courage, Efforts",
            4: "Mother, Home, Emotions",
            5: "Children, Wisdom, Past Life Good Karma",
            6: "Enemies, Debts, Diseases",
            7: "Marriage, Partners, Desires",
            8: "Longevity, Occult, Transformation",
            9: "Luck, Dharma, Father",
            10: "Career, Status, Karma",
            11: "Gains, Hopes, Networks",
            12: "Losses, Liberation, Sleep"
        }

        results = self.analyze_all_houses()

        col_widths = {
            "House": 7,
            "Significations": 40,
            "Bhava": 20,
            "Bhavesh": 20,
            "Karaka": 20,
            "Overall": 20
        }

        def pad(val, width):
            return f"{val:<{width}}"

        # Header
        table = "# 📊 HOUSE STRENGTH SUMMARY TABLE\n"
        table += "Includes Bhava, Bhavesh, Karaka strengths and basic house significations.\n\n"

        header = f"| {pad('House', col_widths['House'])}" \
                f"| {pad('Significations', col_widths['Significations'])}" \
                f"| {pad('Bhava', col_widths['Bhava'])}" \
                f"| {pad('Bhavesh', col_widths['Bhavesh'])}" \
                f"| {pad('Karaka', col_widths['Karaka'])}" \
                f"| {pad('Overall', col_widths['Overall'])}|\n"

        divider = f"|{'-' * (col_widths['House'] + 1)}" \
                f"|{'-' * (col_widths['Significations'] + 1)}" \
                f"|{'-' * (col_widths['Bhava'] + 1)}" \
                f"|{'-' * (col_widths['Bhavesh'] + 2)}" \
                f"|{'-' * (col_widths['Karaka'] + 2)}" \
                f"|{'-' * (col_widths['Overall'] + 1)}|\n"

        table += header + divider

        for house_num in range(1, 13):
            r = results[house_num]
            table += f"| {pad(house_num, col_widths['House'])}" \
                    f"| {pad(HOUSE_SIGNIFICATIONS[house_num], col_widths['Significations'])}" \
                    f"| {pad(self.STRENGTH_LABELS[r.bhava_strength], col_widths['Bhava'])}" \
                    f"| {pad(self.STRENGTH_LABELS[r.bhavesh_strength], col_widths['Bhavesh'])}" \
                    f"| {pad(self.STRENGTH_LABELS[r.karaka_strength], col_widths['Karaka'])}" \
                    f"| {pad(self.STRENGTH_LABELS[r.overall_strength], col_widths['Overall'])}|\n"

        return table


def example_usage(sample_planets_data, sample_house_data):
    analyzer = BPHSHouseAnalyzer(sample_planets_data, sample_house_data)
    
    # Analyze a single house
    result = analyzer.analyze_house(1)
    print(f"House 1 Overall Strength: {result.overall_strength.value}")
    
    # Generate full report
    report = analyzer.generate_comprehensive_report()
    print(report)