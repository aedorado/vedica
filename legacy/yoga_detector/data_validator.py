import logging
from typing import Dict, List, Set, Tuple, Optional, Any, Union
from dataclasses import dataclass, field
from enum import Enum
from collections import defaultdict
from abc import ABC, abstractmethod

from yogas.vedic_yoga import VedicYoga
from yogas.yoga_type import YogaType

import logging
logger = logging.getLogger(__name__)

class DataValidator:
    """Utility class for validating and sanitizing astrological data."""
    
    @staticmethod
    def validate_planet_data(planet_data: Dict[str, Any]) -> bool:
        """Validate that planet data contains required fields."""
        required_fields = [
            'HousePlanetOccupiesBasedOnSign',
            'PlanetsInConjunction',
            'PlanetsAspectingPlanet'
        ]
        
        for field in required_fields:
            if field not in planet_data:
                logger.warning(f"Missing required field '{field}' in planet data")
                return False
        return True
    
    @staticmethod
    def validate_house_data(house_data: Dict[str, Any]) -> bool:
        """Validate that house data contains required fields."""
        required_fields = ['HouseRasiSign', 'LordOfHouse']
        
        for field in required_fields:
            if field not in house_data:
                logger.warning(f"Missing required field '{field}' in house data")
                return False
        return True
    
    @staticmethod
    def normalize_house_key(house_key: Any) -> Optional[int]:
        """Convert various house key formats to integer."""
        if not house_key:
            return None
            
        try:
            if isinstance(house_key, int):
                return house_key if 1 <= house_key <= 12 else None
            elif isinstance(house_key, str):
                # Handle formats like "House1", "1", etc.
                clean_key = house_key.replace("House", "").strip()
                house_num = int(clean_key)
                return house_num if 1 <= house_num <= 12 else None
        except (ValueError, AttributeError):
            logger.warning(f"Invalid house key format: {house_key}")
            return None
        
        return None
