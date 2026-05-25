"""
Condition evaluator for astrological pattern matching.
Evaluates whether a chart matches specific astrological conditions.
"""

import re
import logging
from typing import Dict, Optional
from query_parser import Condition, ConditionType, CompoundCondition, OperatorType
from config import HOUSE_CATEGORIES

logger = logging.getLogger(__name__)
logger.setLevel(logging.WARNING)  # Reduce verbosity


class ConditionEvaluator:
    """Evaluates astrological conditions against chart data"""
    
    def __init__(self, planet_data: Dict, house_data: Dict):
        """
        Initialize evaluator with chart data.
        
        Args:
            planet_data: Dictionary with planet information (from vedastro)
            house_data: Dictionary with house information (from vedastro)
        """
        self.planet_data = planet_data
        self.house_data = house_data
        self._cache: Dict = {}
    
    def evaluate(self, compound_condition: CompoundCondition) -> bool:
        """
        Evaluate a compound condition against the chart.
        
        Args:
            compound_condition: CompoundCondition AST from parser
            
        Returns:
            Boolean indicating if chart matches condition
        """
        if compound_condition.simple_condition:
            return self._evaluate_simple(compound_condition.simple_condition)
        
        if not compound_condition.conditions:
            return False
        
        # Evaluate left
        left_result = self.evaluate(compound_condition.conditions[0])
        
        # Evaluate right (if compound)
        if len(compound_condition.conditions) > 1:
            right_result = self.evaluate(compound_condition.conditions[1])
            
            if compound_condition.operator == OperatorType.AND:
                return left_result and right_result
            elif compound_condition.operator == OperatorType.OR:
                return left_result or right_result
        
        return left_result
    
    def _evaluate_simple(self, condition: Condition) -> bool:
        """Evaluate a single simple condition"""
        try:
            if condition.type == ConditionType.PLANET_IN_HOUSE:
                return self._check_planet_in_house(condition.primary, condition.secondary)
            
            elif condition.type == ConditionType.ZODIAC_IN_HOUSE:
                return self._check_zodiac_in_house(condition.primary, condition.secondary)
            
            elif condition.type == ConditionType.LAGNA_SIGN:
                return self._check_lagna_sign(condition.primary)
            
            elif condition.type == ConditionType.PLANET_SIGN:
                return self._check_planet_sign(condition.primary, condition.secondary)
            
            elif condition.type == ConditionType.HOUSE_CATEGORY:
                return self._check_planet_in_category(condition.primary, condition.secondary)
            
            else:
                logger.warning(f"Unknown condition type: {condition.type}")
                return False
        
        except Exception as e:
            logger.error(f"Error evaluating condition {condition}: {e}")
            return False
    
    def _get_planet_house(self, planet_name: str) -> Optional[int]:
        """Extract house number for a planet"""
        if planet_name not in self.planet_data:
            return None
        
        planet_info = self.planet_data[planet_name]
        
        # Try different possible field names
        for field in ['HousePlanetOccupiesBasedOnLongitudes', 'HousePlanetOccupiesBasedOnSign', 'PlanetHouse', 'House', 'CurrentHouse']:
            if field in planet_info:
                house_val = planet_info[field]
                if isinstance(house_val, int):
                    return house_val
                if isinstance(house_val, str):
                    # Extract number from "House11" format
                    match = re.search(r'\d+', house_val)
                    if match:
                        return int(match.group())
                    if house_val.isdigit():
                        return int(house_val)
        
        return None
    
    def _get_planet_sign(self, planet_name: str) -> Optional[str]:
        """Extract zodiac sign for a planet"""
        if planet_name not in self.planet_data:
            return None
        
        planet_info = self.planet_data[planet_name]
        
        # Try to get sign from rasi chart (D1)
        for field in ['PlanetRasiD1Sign', 'RasiSign', 'Sign']:
            if field in planet_info:
                sign_info = planet_info[field]
                
                # sign_info might be nested dict with 'Name' key
                if isinstance(sign_info, dict):
                    if 'Name' in sign_info:
                        return sign_info['Name']
                    # Try direct name
                    if 'name' in sign_info:
                        return sign_info['name']
                elif isinstance(sign_info, str):
                    return sign_info
        
        return None
    
    def _get_lagna_sign(self) -> Optional[str]:
        """Extract lagna (1st house) sign"""
        # House data uses string keys: "1", "2", etc.
        house_1 = self.house_data.get("1") or self.house_data.get(1)
        if not house_1:
            return None
        
        # Try different possible field names
        for field in ['HouseRasiSign', 'RasiSign', 'Sign']:
            if field in house_1:
                sign_info = house_1[field]
                
                if isinstance(sign_info, dict):
                    if 'Name' in sign_info:
                        return sign_info['Name']
                    if 'name' in sign_info:
                        return sign_info['name']
                elif isinstance(sign_info, str):
                    return sign_info
        
        return None
    
    def _get_house_sign(self, house_num: int) -> Optional[str]:
        """Extract the sign in a specific house"""
        # House data uses string keys: "1", "2", etc.
        house_info = self.house_data.get(str(house_num)) or self.house_data.get(house_num)
        if not house_info:
            return None
        
        for field in ['HouseRasiSign', 'RasiSign', 'Sign']:
            if field in house_info:
                sign_info = house_info[field]
                
                if isinstance(sign_info, dict):
                    if 'Name' in sign_info:
                        return sign_info['Name']
                    if 'name' in sign_info:
                        return sign_info['name']
                elif isinstance(sign_info, str):
                    return sign_info
        
        return None
    
    def _get_planets_in_house(self, house_num: int) -> list:
        """Extract all planets in a specific house"""
        if house_num not in self.house_data:
            return []
        
        house_info = self.house_data[house_num]
        
        # Try different possible field names
        for field in ['PlanetsInHouse', 'PlanetsPresent', 'Planets']:
            if field in house_info:
                planets = house_info[field]
                
                if isinstance(planets, list):
                    return planets
                elif isinstance(planets, str):
                    # Parse comma-separated string
                    return [p.strip() for p in planets.split(',') if p.strip()]
        
        return []
    
    def _check_planet_in_house(self, planet_name: str, house_num_str: str) -> bool:
        """Check if a planet is in a specific house"""
        try:
            house_num = int(house_num_str)
            planet_house = self._get_planet_house(planet_name)
            
            if planet_house is None:
                return False
            
            result = planet_house == house_num
            return result
        
        except Exception as e:
            logger.error(f"Error checking {planet_name} in house {house_num_str}: {e}")
            return False
    
    def _check_zodiac_in_house(self, zodiac_name: str, house_num_str: str) -> bool:
        """Check if a zodiac sign is in a specific house"""
        try:
            house_num = int(house_num_str)
            house_sign = self._get_house_sign(house_num)
            
            if house_sign is None:
                return False
            
            result = house_sign == zodiac_name
            return result
        
        except Exception as e:
            logger.error(f"Error checking {zodiac_name} in house {house_num_str}: {e}")
            return False
    
    def _check_lagna_sign(self, zodiac_name: str) -> bool:
        """Check if lagna (1st house cusp) is in a specific zodiac sign"""
        try:
            lagna_sign = self._get_lagna_sign()
            
            if lagna_sign is None:
                return False
            
            result = lagna_sign == zodiac_name
            return result
        
        except Exception as e:
            logger.error(f"Error checking lagna sign {zodiac_name}: {e}")
            return False
    
    def _check_planet_sign(self, planet_name: str, zodiac_name: str) -> bool:
        """Check if a planet is in a specific zodiac sign"""
        try:
            planet_sign = self._get_planet_sign(planet_name)
            
            if planet_sign is None:
                return False
            
            result = planet_sign == zodiac_name
            return result
        
        except Exception as e:
            logger.error(f"Error checking {planet_name} in {zodiac_name}: {e}")
            return False
    
    def _check_planet_in_category(self, planet_name: str, category_name: str) -> bool:
        """Check if a planet is in a house category (Kendra, Trikona, etc.)"""
        try:
            if category_name not in HOUSE_CATEGORIES:
                return False
            
            planet_house = self._get_planet_house(planet_name)
            
            if planet_house is None:
                return False
            
            category_houses = HOUSE_CATEGORIES[category_name]
            result = planet_house in category_houses
            return result
        
        except Exception as e:
            logger.error(f"Error checking {planet_name} in {category_name}: {e}")
            return False


def evaluate_condition(
    query: CompoundCondition,
    planet_data: Dict,
    house_data: Dict
) -> bool:
    """
    Convenience function to evaluate a condition against chart data.
    
    Args:
        query: Parsed CompoundCondition from query_parser
        planet_data: Planet data dictionary
        house_data: House data dictionary
        
    Returns:
        Boolean result
    """
    evaluator = ConditionEvaluator(planet_data, house_data)
    return evaluator.evaluate(query)
