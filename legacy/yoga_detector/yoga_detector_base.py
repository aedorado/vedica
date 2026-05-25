import logging
from typing import Dict, List, Set, Tuple, Optional, Any, Union
from dataclasses import dataclass, field
from enum import Enum
from collections import defaultdict
from abc import ABC, abstractmethod

from yogas.vedic_yoga import VedicYoga
from yogas.yoga_type import YogaType

class YogaDetectorBase(ABC):
    """Abstract base class for all yoga detectors."""
    
    def __init__(self, planet_data_objs, house_data_objs, chart_data: Dict[str, Any] = {}):
        self.planet_data_objs = planet_data_objs
        self.house_data_objs = house_data_objs
        self.chart_data = chart_data
    
    @abstractmethod
    def detect_yogas(self) -> List[VedicYoga]:
        """Detect yogas of this specific type."""
        pass
    
    def _check_planet_relationship(self, planet1: str, planet2: str, 
                                 yoga_type: YogaType, 
                                 house_criteria_func) -> Optional[VedicYoga]:
        """Generic method to check planet relationships based on house criteria."""
        if planet1 == planet2:
            return None  # Cannot form yoga with itself

        if yoga_type == YogaType.CONJUNCTION:
            if self.chart_data.get("planet_houses", {}).get(planet1) != self.chart_data.get("planet_houses", {}).get(planet2):
                return None  # Not truly conjunct

        planet1_houses = self.chart_data['planet_lordships'].get(planet1, [])
        planet2_houses = self.chart_data['planet_lordships'].get(planet2, [])
        
        for house1 in planet1_houses:
            for house2 in planet2_houses:
                result = house_criteria_func(house1, house2, planet1, planet2, yoga_type)
                if result:
                    return result
        
        return None
