"""
Planet strength calculation utilities for Vedic astrology.
Specialized class for calculating various types of planetary strengths.
"""

import logging
from typing import Dict, List, Optional, Any
from .planet_analyzer import PlanetAnalyzer

logger = logging.getLogger(__name__)


class PlanetStrengthCalculator:
    """
    Specialized calculator for various types of planetary strengths.
    Uses PlanetAnalyzer for basic planet analysis and builds upon it for strength calculations.
    """
    
    def __init__(self, planet_analyzer: PlanetAnalyzer):
        """Initialize with a PlanetAnalyzer instance."""
        self.analyzer = planet_analyzer
        self.chart_data = planet_analyzer.chart_data
    
    def calculate_basic_strength(self, planet: str, planet_data: Dict[str, Any], sign_status: str) -> float:
        """Calculate basic strength score based on sign status."""
        base_strength_map = {
            "Exalted": 90.0,
            "Own": 80.0,
            "Friend": 60.0,
            "Neutral": 50.0,
            "Enemy": 30.0,
            "Debilitated": 10.0
        }
        return base_strength_map.get(sign_status, 50.0)
    
    def calculate_positional_strength_bonus(self, planet_data: Dict[str, Any]) -> float:
        """Calculate strength bonus based on house position."""
        bonus = 0.0
        planet_house = self.analyzer.get_planet_house(planet_data)
        
        if not planet_house:
            return bonus
        
        # Kendra houses bonus
        if planet_house in [1, 4, 7, 10]:
            if planet_house == 1:  # Lagna - most powerful
                bonus += 15.0
            elif planet_house == 10:  # 10th house - career/reputation
                bonus += 12.0
            else:  # 4th or 7th house
                bonus += 8.0
        
        # Trikona houses bonus
        elif planet_house in [5, 9]:
            bonus += 10.0
        
        # Upachaya houses (growth houses) - moderate bonus
        elif planet_house in [3, 6, 11]:
            bonus += 5.0
        
        # Dusthana houses penalty
        elif planet_house in [6, 8, 12]:
            bonus -= 10.0
        
        # Additional Kendra/Trikona bonuses from chart flags
        if self.analyzer.is_planet_in_kendra(planet_data):
            bonus += 5.0
        
        if self.analyzer.is_planet_in_trikona(planet_data):
            bonus += 8.0
        
        return bonus
    
    def calculate_aspectual_strength_modifier(self, planet_data: Dict[str, Any]) -> float:
        """Calculate strength modifier based on planetary aspects."""
        modifier = 0.0
        
        # Benefic aspects
        if self.analyzer.is_planet_aspected_by_benefics(planet_data):
            modifier += 10.0
        
        # Malefic aspects
        if self.analyzer.is_planet_aspected_by_malefics(planet_data):
            modifier -= 5.0
        
        # Friend aspects
        if self.analyzer.is_planet_aspected_by_friends(planet_data):
            modifier += 8.0
        
        # Enemy aspects
        if self.analyzer.is_planet_aspected_by_enemies(planet_data):
            modifier -= 8.0
        
        return modifier
    
    def calculate_conjunctional_strength_modifier(self, planet_data: Dict[str, Any]) -> float:
        """Calculate strength modifier based on planetary conjunctions."""
        modifier = 0.0
        
        # Benefic conjunctions
        if self.analyzer.has_benefic_conjunctions(planet_data):
            modifier += 8.0
        
        # Malefic conjunctions
        if self.analyzer.has_malefic_conjunctions(planet_data):
            modifier -= 5.0
        
        # Friend conjunctions
        if self.analyzer.has_friend_conjunctions(planet_data):
            modifier += 6.0
        
        # Enemy conjunctions
        if self.analyzer.has_enemy_conjunctions(planet_data):
            modifier -= 8.0
        
        return modifier
    
    def calculate_special_condition_bonus(self, planet: str, planet_data: Dict[str, Any]) -> float:
        """Calculate bonus for special planetary conditions."""
        bonus = 0.0
        
        # Vargottama bonus (same sign in D1 and D9)
        if self.analyzer.is_planet_vargottama(planet_data):
            bonus += 10.0
        
        # Retrograde bonus (for applicable planets)
        if planet in ['Mars', 'Jupiter', 'Saturn'] and self.analyzer.is_planet_retrograde(planet_data):
            bonus += 5.0
        
        # Fortified planet bonus
        if self.analyzer.is_planet_fortified(planet_data):
            bonus += 8.0
        
        # Strong in Navamsha
        if self.analyzer.is_strong_in_navamsha(planet, planet_data):
            bonus += 8.0
        
        # High power percentage bonus
        power_percentage = planet_data.get('PlanetPowerPercentage', 0)
        if power_percentage >= 80:
            bonus += 5.0
        elif power_percentage >= 70:
            bonus += 3.0
        
        return bonus
    
    def calculate_affliction_penalty(self, planet: str, planet_data: Dict[str, Any]) -> float:
        """Calculate penalty for planetary afflictions."""
        penalty = 0.0
        
        # Combustion penalty
        if self.analyzer.is_planet_combust(planet_data):
            # Mercury handles combustion better
            penalty += 15.0 if planet != 'Mercury' else 8.0
        
        # Heavy affliction penalty
        if self.analyzer.is_planet_heavily_afflicted(planet, planet_data):
            penalty += 10.0
        
        # Debilitation penalty (already handled in basic strength, but additional for extreme cases)
        if self.analyzer.is_planet_debilitated(planet_data):
            penalty += 5.0  # Additional penalty beyond the low base score
        
        return penalty
    
    def calculate_comprehensive_strength(self, planet: str, planet_data: Dict[str, Any], 
                                       sign_status: str = None) -> float:
        """Calculate comprehensive strength score for a planet."""
        if not sign_status:
            planet_sign = self.analyzer.get_planet_sign(planet_data)
            sign_status = self.analyzer.get_sign_status(planet, planet_sign, planet_data) if planet_sign else "Neutral"
        
        # Start with basic strength
        strength = self.calculate_basic_strength(planet, planet_data, sign_status)
        
        # Add positional strength bonus
        strength += self.calculate_positional_strength_bonus(planet_data)
        
        # Add aspectual strength modifier
        strength += self.calculate_aspectual_strength_modifier(planet_data)
        
        # Add conjunctional strength modifier
        strength += self.calculate_conjunctional_strength_modifier(planet_data)
        
        # Add special condition bonus
        strength += self.calculate_special_condition_bonus(planet, planet_data)
        
        # Subtract affliction penalty
        strength -= self.calculate_affliction_penalty(planet, planet_data)
        
        # Use Shadbala strength if available and higher
        shadbala_strength = planet_data.get('PlanetShadbalaPinda', 0)
        if shadbala_strength:
            # Normalize Shadbala to percentage (typical range 200-800)
            normalized_shadbala = min((shadbala_strength / 600) * 100, 100)
            strength = max(strength, normalized_shadbala)
        
        # Ensure strength is within bounds
        return max(0.0, min(strength, 100.0))
    
    def calculate_yoga_specific_strength(self, planet: str, planet_data: Dict[str, Any], 
                                       sign_status: str, yoga_requirements: Dict[str, Any]) -> float:
        """Calculate strength specifically for yoga formation requirements."""
        base_strength = self.calculate_comprehensive_strength(planet, planet_data, sign_status)
        
        # Additional bonuses based on yoga-specific requirements
        yoga_bonus = 0.0
        
        # House-specific bonuses for the yoga
        required_houses = yoga_requirements.get('required_houses', [])
        planet_house = self.analyzer.get_planet_house(planet_data)
        
        if planet_house in required_houses:
            # Bonus varies by house importance in the yoga
            if planet_house == 1:  # Lagna is most powerful for most yogas
                yoga_bonus += 10.0
            elif planet_house in [4, 7, 10]:  # Other Kendras
                yoga_bonus += 8.0
            elif planet_house in [5, 9]:  # Trikonas
                yoga_bonus += 6.0
        
        # Sign-specific bonuses for the yoga
        required_sign_statuses = yoga_requirements.get('required_sign_statuses', [])
        if sign_status in required_sign_statuses:
            if sign_status == "Exalted":
                yoga_bonus += 10.0
            elif sign_status == "Own":
                yoga_bonus += 8.0
        
        # Planet-specific adjustments
        planet_adjustments = yoga_requirements.get('planet_specific_adjustments', {})
        planet_adjustment = planet_adjustments.get(planet, 0.0)
        yoga_bonus += planet_adjustment
        
        return min(base_strength + yoga_bonus, 100.0)
    
    def get_strength_breakdown(self, planet: str, planet_data: Dict[str, Any]) -> Dict[str, float]:
        """Get detailed breakdown of strength components."""
        planet_sign = self.analyzer.get_planet_sign(planet_data)
        sign_status = self.analyzer.get_sign_status(planet, planet_sign, planet_data) if planet_sign else "Neutral"
        
        breakdown = {
            'basic_strength': self.calculate_basic_strength(planet, planet_data, sign_status),
            'positional_bonus': self.calculate_positional_strength_bonus(planet_data),
            'aspectual_modifier': self.calculate_aspectual_strength_modifier(planet_data),
            'conjunctional_modifier': self.calculate_conjunctional_strength_modifier(planet_data),
            'special_bonus': self.calculate_special_condition_bonus(planet, planet_data),
            'affliction_penalty': -self.calculate_affliction_penalty(planet, planet_data),
            'shadbala_strength': planet_data.get('PlanetShadbalaPinda', 0),
            'power_percentage': planet_data.get('PlanetPowerPercentage', 0)
        }
        
        # Calculate total
        calculated_total = (breakdown['basic_strength'] + 
                          breakdown['positional_bonus'] + 
                          breakdown['aspectual_modifier'] + 
                          breakdown['conjunctional_modifier'] + 
                          breakdown['special_bonus'] + 
                          breakdown['affliction_penalty'])
        
        # Use higher of calculated or normalized Shadbala
        if breakdown['shadbala_strength']:
            normalized_shadbala = min((breakdown['shadbala_strength'] / 600) * 100, 100)
            breakdown['final_strength'] = max(calculated_total, normalized_shadbala)
        else:
            breakdown['final_strength'] = calculated_total
        
        # Ensure within bounds
        breakdown['final_strength'] = max(0.0, min(breakdown['final_strength'], 100.0))
        
        return breakdown
    
    def compare_planet_strengths(self, planets: List[str]) -> Dict[str, Dict[str, Any]]:
        """Compare strengths of multiple planets."""
        comparison = {}
        
        for planet in planets:
            planet_data = self.analyzer.get_planet_data(planet)
            if planet_data:
                breakdown = self.get_strength_breakdown(planet, planet_data)
                planet_sign = self.analyzer.get_planet_sign(planet_data)
                
                comparison[planet] = {
                    'sign': planet_sign,
                    'house': self.analyzer.get_planet_house(planet_data),
                    'final_strength': breakdown['final_strength'],
                    'strength_breakdown': breakdown,
                    'rank': 0  # Will be filled after sorting
                }
        
        # Rank planets by strength
        sorted_planets = sorted(comparison.items(), 
                              key=lambda x: x[1]['final_strength'], 
                              reverse=True)
        
        for rank, (planet, data) in enumerate(sorted_planets, 1):
            comparison[planet]['rank'] = rank
        
        return comparison