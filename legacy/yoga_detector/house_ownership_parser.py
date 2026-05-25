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

class HouseOwnershipParser:
    """Handles parsing of house ownership data in various formats."""
    
    @staticmethod
    def parse_owned_houses(raw_data: Any) -> List[int]:
        """Parse house ownership data from various formats."""
        houses = []
        
        if not raw_data:
            return houses
        
        try:
            if isinstance(raw_data, list):
                items = raw_data
            elif isinstance(raw_data, str):
                items = [item.strip() for item in raw_data.split(',') if item.strip()]
            else:
                logger.warning(f"Unexpected house ownership format: {type(raw_data)}")
                return houses
            
            for item in items:
                house_num = HouseOwnershipParser._parse_single_house(item)
                if house_num:
                    houses.append(house_num)
                    
        except Exception as e:
            logger.error(f"Error parsing house ownership data: {e}")
        
        return sorted(list(set(houses)))
    
    @staticmethod
    def _parse_single_house(house_item: Any) -> Optional[int]:
        """Parse a single house item to extract house number."""
        if isinstance(house_item, int):
            return house_item if 1 <= house_item <= 12 else None
        elif isinstance(house_item, str):
            if house_item.lower().startswith("house"):
                num_part = house_item[5:].strip()
            else:
                num_part = house_item.strip()
            
            try:
                house_num = int(num_part)
                return house_num if 1 <= house_num <= 12 else None
            except ValueError:
                logger.warning(f"Could not parse house number from: '{house_item}'")
                return None
        else:
            logger.warning(f"Unexpected house item type: {type(house_item)}")
            return None
