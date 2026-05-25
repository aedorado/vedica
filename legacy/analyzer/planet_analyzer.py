"""
Generic planet analysis utilities for Vedic astrology.
Contains reusable methods for analyzing planet conditions, strengths, and relationships.
"""

import logging
from typing import Dict, List, Optional, Any
from abc import ABC, abstractmethod

logger = logging.getLogger(__name__)


class PlanetAnalyzer:
    """
    Generic analyzer for planet conditions and strengths.
    This class provides reusable methods for analyzing planets across different yoga detectors.
    """
    
    # Own signs for each planet
    OWN_SIGNS = {
        'Mars': ['Aries', 'Scorpio'],
        'Mercury': ['Gemini', 'Virgo'],
        'Jupiter': ['Sagittarius', 'Pisces'],
        'Venus': ['Taurus', 'Libra'],
        'Saturn': ['Capricorn', 'Aquarius'],
        'Sun': ['Leo'],
        'Moon': ['Cancer']
    }
    
    # Exaltation signs for each planet
    EXALTATION_SIGNS = {
        'Mars': 'Capricorn',
        'Mercury': 'Virgo',
        'Jupiter': 'Cancer',
        'Venus': 'Pisces',
        'Saturn': 'Libra',
        'Sun': 'Aries',
        'Moon': 'Taurus'
    }
    
    # Debilitation signs for each planet
    DEBILITATION_SIGNS = {
        'Mars': 'Cancer',
        'Mercury': 'Pisces',
        'Jupiter': 'Capricorn',
        'Venus': 'Virgo',
        'Saturn': 'Aries',
        'Sun': 'Libra',
        'Moon': 'Scorpio'
    }
    
    # Friend signs for each planet (simplified)
    FRIEND_SIGNS = {
        'Mars': ['Leo', 'Sagittarius', 'Pisces'],
        'Mercury': ['Taurus', 'Libra', 'Sagittarius', 'Pisces'],
        'Jupiter': ['Aries', 'Cancer', 'Leo', 'Scorpio'],
        'Venus': ['Gemini', 'Virgo', 'Capricorn', 'Aquarius'],
        'Saturn': ['Taurus', 'Gemini', 'Virgo', 'Libra'],
        'Sun': ['Aries', 'Sagittarius', 'Pisces'],
        'Moon': ['Taurus', 'Gemini', 'Cancer', 'Virgo', 'Libra', 'Sagittarius', 'Pisces']
    }
    
    def __init__(self, chart_data: Dict[str, Any]):
        """Initialize with chart data."""
        self.chart_data = chart_data
    
    # === Basic Planet Data Extraction ===
    
    def get_planet_house(self, planet_data: Dict[str, Any]) -> Optional[int]:
        """Get the house number where planet is located."""
        house_based_on_longitudes = planet_data.get('HousePlanetOccupiesBasedOnLongitudes')
        if house_based_on_longitudes:
            # Extract number from "House10" format
            return int(house_based_on_longitudes.replace('House', ''))
        return None
    
    def get_planet_sign(self, planet_data: Dict[str, Any]) -> Optional[str]:
        """Get the zodiac sign where planet is located."""
        rasi_sign_data = planet_data.get('PlanetRasiD1Sign')
        if rasi_sign_data and 'Name' in rasi_sign_data:
            return rasi_sign_data['Name']
        return None
    
    def get_navamsha_sign(self, planet_data: Dict[str, Any]) -> Optional[str]:
        """Get the Navamsha (D9) sign of the planet."""
        navamsha_data = planet_data.get('PlanetNavamshaD9Sign')
        if navamsha_data and 'Name' in navamsha_data:
            return navamsha_data['Name']
        return None
    
    def get_planet_data(self, planet: str) -> Optional[Dict[str, Any]]:
        """Extract planet data from chart_data structure."""
        # First try the expected format
        if 'planets' in self.chart_data and planet in self.chart_data['planets']:
            return self.chart_data['planets'][planet]
        
        # Fallback: build from available sources
        return self._build_planet_data_from_available_sources(planet)

    def _build_planet_data_from_available_sources(self, planet: str) -> Optional[Dict[str, Any]]:
        """Build planet data from available chart data sources."""
        planet_data = {}
        
        # Get house from planet_houses
        if 'planet_houses' in self.chart_data and planet in self.chart_data['planet_houses']:
            house = self.chart_data['planet_houses'][planet]
            planet_data['HousePlanetOccupiesBasedOnLongitudes'] = f'House{house}'
        
        # Get sign from planet_signs  
        if 'planet_signs' in self.chart_data and planet in self.chart_data['planet_signs']:
            sign = self.chart_data['planet_signs'][planet]
            planet_data['PlanetRasiD1Sign'] = {'Name': sign}
            
            # Determine sign status
            if sign in self.OWN_SIGNS.get(planet, []):
                planet_data['IsPlanetInOwnSign'] = True
            elif sign == self.EXALTATION_SIGNS.get(planet):
                planet_data['IsPlanetExaltedSign'] = True
        
        return planet_data if planet_data else None
    
    # === Sign Status Analysis ===
    
    def get_sign_status(self, planet: str, planet_sign: str, planet_data: Dict[str, Any]) -> Optional[str]:
        """Determine if planet is in own sign, exalted, debilitated, etc."""
        # Check if planet is exalted
        if self.is_planet_exalted(planet_data) or planet_sign == self.EXALTATION_SIGNS.get(planet):
            return "Exalted"
        
        # Check if planet is debilitated
        if self.is_planet_debilitated(planet_data) or planet_sign == self.DEBILITATION_SIGNS.get(planet):
            return "Debilitated"
        
        # Check if planet is in own sign
        if self.is_planet_in_own_sign(planet_data) or planet_sign in self.OWN_SIGNS.get(planet, []):
            return "Own"
        
        # Check if planet is in friend sign
        if self.is_planet_in_friend_sign(planet_data) or planet_sign in self.FRIEND_SIGNS.get(planet, []):
            return "Friend"
        
        # Check if planet is in enemy sign
        if self.is_planet_in_enemy_sign(planet_data):
            return "Enemy"
        
        return "Neutral"
    
    # === Basic Planet Conditions ===
    
    def is_planet_combust(self, planet_data: Dict[str, Any]) -> bool:
        """Check if planet is combust."""
        return planet_data.get('IsPlanetCombust', False)
    
    def is_planet_retrograde(self, planet_data: Dict[str, Any]) -> bool:
        """Check if planet is retrograde."""
        return planet_data.get('IsPlanetRetrograde', False)
    
    def is_planet_exalted(self, planet_data: Dict[str, Any]) -> bool:
        """Check if planet is exalted."""
        return planet_data.get('IsPlanetExaltedSign', False)
    
    def is_planet_debilitated(self, planet_data: Dict[str, Any]) -> bool:
        """Check if planet is debilitated."""
        return planet_data.get('IsPlanetDebilitated', False)
    
    def is_planet_in_own_sign(self, planet_data: Dict[str, Any]) -> bool:
        """Check if planet is in own sign."""
        return planet_data.get('IsPlanetInOwnSign', False)
    
    def is_planet_in_friend_sign(self, planet_data: Dict[str, Any]) -> bool:
        """Check if planet is in friend sign."""
        return planet_data.get('IsPlanetInFriendSign', False)
    
    def is_planet_in_enemy_sign(self, planet_data: Dict[str, Any]) -> bool:
        """Check if planet is in enemy sign."""
        return planet_data.get('IsPlanetInEnemySign', False)
    
    def is_planet_fortified(self, planet_data: Dict[str, Any]) -> bool:
        """Check if planet is fortified."""
        return planet_data.get('IsPlanetFortified', False)
    
    # === Aspectual Analysis ===
    
    def is_planet_aspected_by_benefics(self, planet_data: Dict[str, Any]) -> bool:
        """Check if planet is aspected by benefic planets."""
        return planet_data.get('IsPlanetAspectedByBeneficPlanets', False)
    
    def is_planet_aspected_by_malefics(self, planet_data: Dict[str, Any]) -> bool:
        """Check if planet is aspected by malefic planets."""
        return planet_data.get('IsPlanetAspectedByMaleficPlanets', False)
    
    def is_planet_aspected_by_enemies(self, planet_data: Dict[str, Any]) -> bool:
        """Check if planet is aspected by enemy planets."""
        return planet_data.get('IsPlanetAspectedByEnemyPlanets', False)
    
    def is_planet_aspected_by_friends(self, planet_data: Dict[str, Any]) -> bool:
        """Check if planet is aspected by friendly planets."""
        return planet_data.get('IsPlanetAspectedByFriendPlanets', False)
    
    # === Conjunctional Analysis ===
    
    def has_benefic_conjunctions(self, planet_data: Dict[str, Any]) -> bool:
        """Check if planet has conjunctions with benefic planets."""
        return planet_data.get('IsPlanetConjunctWithBeneficPlanets', False)
    
    def has_malefic_conjunctions(self, planet_data: Dict[str, Any]) -> bool:
        """Check if planet has conjunctions with malefic planets."""
        return planet_data.get('IsPlanetConjunctWithMaleficPlanets', False)
    
    def has_enemy_conjunctions(self, planet_data: Dict[str, Any]) -> bool:
        """Check if planet has conjunctions with enemy planets."""
        return planet_data.get('IsPlanetConjunctWithEnemyPlanets', False)
    
    def has_friend_conjunctions(self, planet_data: Dict[str, Any]) -> bool:
        """Check if planet has conjunctions with friendly planets."""
        return planet_data.get('IsPlanetConjunctWithFriendPlanets', False)
    
    # === House Position Analysis ===
    
    def is_planet_in_kendra(self, planet_data: Dict[str, Any]) -> bool:
        """Check if planet is in Kendra houses (1, 4, 7, 10)."""
        return planet_data.get('IsPlanetInKendra', False)
    
    def is_planet_in_trikona(self, planet_data: Dict[str, Any]) -> bool:
        """Check if planet is in Trikona houses (1, 5, 9)."""
        return planet_data.get('IsPlanetInTrikona', False)
    
    def is_planet_in_upachaya(self, planet_data: Dict[str, Any]) -> bool:
        """Check if planet is in Upachaya houses (3, 6, 10, 11)."""
        return planet_data.get('IsPlanetInUpachaya', False)
    
    def is_planet_in_dusthana(self, planet_data: Dict[str, Any]) -> bool:
        """Check if planet is in Dusthana houses (6, 8, 12)."""
        return planet_data.get('IsPlanetInDusthana', False)
    
    # === Divisional Chart Analysis ===
    
    def is_planet_vargottama(self, planet_data: Dict[str, Any]) -> bool:
        """Check if planet is Vargottama (same sign in D1 and D9)."""
        d1_sign = self.get_planet_sign(planet_data)
        d9_sign = self.get_navamsha_sign(planet_data)
        
        return d1_sign and d9_sign and d1_sign == d9_sign
    
    def is_strong_in_navamsha(self, planet: str, planet_data: Dict[str, Any]) -> bool:
        """Check if planet is strong in Navamsha chart."""
        navamsha_sign = self.get_navamsha_sign(planet_data)
        if not navamsha_sign:
            return False
        
        # Check if exalted in Navamsha
        if navamsha_sign == self.EXALTATION_SIGNS.get(planet):
            return True
        
        # Check if in own sign in Navamsha
        if navamsha_sign in self.OWN_SIGNS.get(planet, []):
            return True
        
        # Check if in friendly sign in Navamsha
        if navamsha_sign in self.FRIEND_SIGNS.get(planet, []):
            return True
        
        return False
    
    # === Strength Assessment ===
    
    def assess_positional_strength(self, planet_data: Dict[str, Any]) -> str:
        """Assess positional strength based on sign and house placement."""
        if self.is_planet_exalted(planet_data):
            return 'Very Strong'
        elif self.is_planet_in_own_sign(planet_data):
            return 'Very Strong'
        elif self.is_planet_in_friend_sign(planet_data):
            return 'Strong'
        elif self.is_planet_debilitated(planet_data):
            return 'Weak'
        elif self.is_planet_in_enemy_sign(planet_data):
            return 'Weak'
        else:
            return 'Moderate'
    
    def assess_aspectual_strength(self, planet_data: Dict[str, Any]) -> str:
        """Assess strength based on planetary aspects."""
        aspected_by_benefics = self.is_planet_aspected_by_benefics(planet_data)
        aspected_by_malefics = self.is_planet_aspected_by_malefics(planet_data)
        
        if aspected_by_benefics and not aspected_by_malefics:
            return 'Strong'
        elif aspected_by_malefics and not aspected_by_benefics:
            return 'Weak'
        else:
            return 'Moderate'
    
    def assess_conjunctional_strength(self, planet_data: Dict[str, Any]) -> str:
        """Assess strength based on planetary conjunctions."""
        conjunct_with_benefics = self.has_benefic_conjunctions(planet_data)
        conjunct_with_malefics = self.has_malefic_conjunctions(planet_data)
        
        if conjunct_with_benefics and not conjunct_with_malefics:
            return 'Strong'
        elif conjunct_with_malefics and not conjunct_with_benefics:
            return 'Weak'
        else:
            return 'Moderate'
    
    def assess_divisional_strength(self, planet: str, planet_data: Dict[str, Any]) -> str:
        """Assess strength in divisional charts, primarily Navamsha."""
        # Check Vargottama
        if self.is_planet_vargottama(planet_data):
            return 'Strong'
        
        # Check Navamsha strength
        if self.is_strong_in_navamsha(planet, planet_data):
            return 'Strong'
        
        return 'Moderate'
    
    # === Affliction Analysis ===
    
    def is_planet_heavily_afflicted(self, planet: str, planet_data: Dict[str, Any]) -> bool:
        """Check if planet is heavily afflicted by malefics."""
        # Check if aspected by malefics
        aspected_by_malefics = self.is_planet_aspected_by_malefics(planet_data)
        
        # Check if conjunct with malefics
        conjunct_with_malefics = self.has_malefic_conjunctions(planet_data)
        
        # Check if aspected by enemy planets
        aspected_by_enemies = self.is_planet_aspected_by_enemies(planet_data)
        
        # Check if conjunct with enemy planets
        conjunct_with_enemies = self.has_enemy_conjunctions(planet_data)
        
        # Consider heavily afflicted if multiple negative influences
        affliction_count = sum([
            aspected_by_malefics,
            conjunct_with_malefics,
            aspected_by_enemies,
            conjunct_with_enemies
        ])
        
        return affliction_count >= 2
    
    def is_yoga_viable_basic(self, planet: str, planet_data: Dict[str, Any]) -> bool:
        """Basic viability check for yoga formation."""
        # Check if planet is debilitated
        if self.is_planet_debilitated(planet_data):
            return False
        
        # Check if planet is heavily afflicted
        if self.is_planet_heavily_afflicted(planet, planet_data):
            return False
        
        return True
    
    # === Comprehensive Analysis ===
    
    def get_detailed_strength_analysis(self, planet: str, planet_data: Dict[str, Any]) -> Dict[str, Any]:
        """Get detailed strength analysis for the planet."""
        analysis = {
            'shadbala_strength': planet_data.get('PlanetShadbalaPinda', 0),
            'positional_strength': self.assess_positional_strength(planet_data),
            'aspectual_strength': self.assess_aspectual_strength(planet_data),
            'conjunctional_strength': self.assess_conjunctional_strength(planet_data),
            'divisional_strength': self.assess_divisional_strength(planet, planet_data),
            'power_percentage': planet_data.get('PlanetPowerPercentage', 0),
            'is_fortified': self.is_planet_fortified(planet_data),
            'is_combust': self.is_planet_combust(planet_data),
            'is_retrograde': self.is_planet_retrograde(planet_data),
            'is_vargottama': self.is_planet_vargottama(planet_data),
            'overall_assessment': 'Strong'  # Will be determined based on factors
        }
        
        # Determine overall assessment
        strong_factors = 0
        if analysis['positional_strength'] in ['Strong', 'Very Strong']:
            strong_factors += 1
        if analysis['aspectual_strength'] == 'Strong':
            strong_factors += 1
        if analysis['conjunctional_strength'] == 'Strong':
            strong_factors += 1
        if analysis['divisional_strength'] == 'Strong':
            strong_factors += 1
        if analysis['is_fortified']:
            strong_factors += 1
        
        if strong_factors >= 4:
            analysis['overall_assessment'] = 'Very Strong'
        elif strong_factors >= 3:
            analysis['overall_assessment'] = 'Strong'
        elif strong_factors >= 2:
            analysis['overall_assessment'] = 'Moderate'
        else:
            analysis['overall_assessment'] = 'Weak'
        
        return analysis
    
    def get_planet_conditions_summary(self, planet: str, planet_data: Dict[str, Any]) -> Dict[str, Any]:
        """Get a comprehensive summary of planet conditions."""
        planet_sign = self.get_planet_sign(planet_data)
        planet_house = self.get_planet_house(planet_data)
        
        return {
            'planet': planet,
            'sign': planet_sign,
            'house': planet_house,
            'sign_status': self.get_sign_status(planet, planet_sign, planet_data) if planet_sign else None,
            'navamsha_sign': self.get_navamsha_sign(planet_data),
            'is_exalted': self.is_planet_exalted(planet_data),
            'is_own_sign': self.is_planet_in_own_sign(planet_data),
            'is_debilitated': self.is_planet_debilitated(planet_data),
            'is_combust': self.is_planet_combust(planet_data),
            'is_retrograde': self.is_planet_retrograde(planet_data),
            'is_vargottama': self.is_planet_vargottama(planet_data),
            'is_fortified': self.is_planet_fortified(planet_data),
            'is_in_kendra': self.is_planet_in_kendra(planet_data),
            'is_in_trikona': self.is_planet_in_trikona(planet_data),
            'aspected_by_benefics': self.is_planet_aspected_by_benefics(planet_data),
            'aspected_by_malefics': self.is_planet_aspected_by_malefics(planet_data),
            'has_benefic_conjunctions': self.has_benefic_conjunctions(planet_data),
            'has_malefic_conjunctions': self.has_malefic_conjunctions(planet_data),
            'power_percentage': planet_data.get('PlanetPowerPercentage', 0),
            'shadbala_strength': planet_data.get('PlanetShadbalaPinda', 0)
        }