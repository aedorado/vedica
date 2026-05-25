"""Base class for curse detection."""

import logging
from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class CurseRecord:
    """Data class to represent a detected curse."""
    curse_type: str
    curse_name: str
    severity: str  # "high", "medium", "low"
    houses_involved: List[int]
    planets_involved: List[str]
    lords_involved: List[str]
    description: str
    remedies: Optional[List[str]] = None


class CurseDetectorBase(ABC):
    """Abstract base class for curse detectors."""

    def __init__(self, planet_data_objs: Dict, house_data_objs: Dict):
        """
        Initialize curse detector.
        
        Args:
            planet_data_objs: Dictionary of planet objects
            house_data_objs: Dictionary of house objects
        """
        self.planet_data_objs = planet_data_objs
        self.house_data_objs = house_data_objs
        self.detected_curses: List[CurseRecord] = []

    def get_planet_house(self, planet_name: str) -> Optional[int]:
        """Get the house a planet is placed in."""
        try:
            planet_obj = self.planet_data_objs.get(planet_name)
            if planet_obj:
                house_str = getattr(planet_obj, 'HousePlanetOccupiesBasedOnSign', '')
                if house_str and house_str.startswith('House'):
                    return int(house_str.replace('House', ''))
        except Exception as e:
            logger.error(f"Error getting planet house for {planet_name}: {e}")
        return None

    def get_planet_sign(self, planet_name: str) -> Optional[str]:
        """Get the rasi sign of a planet."""
        try:
            planet_obj = self.planet_data_objs.get(planet_name)
            if planet_obj:
                rasi_sign = getattr(planet_obj, 'PlanetRasiD1Sign', None)
                if rasi_sign and hasattr(rasi_sign, 'Name'):
                    return rasi_sign.Name
                elif isinstance(rasi_sign, str):
                    return rasi_sign
        except Exception as e:
            logger.error(f"Error getting planet sign for {planet_name}: {e}")
        return None

    def get_house_lord(self, house_number: int) -> Optional[str]:
        """Get the lord of a house."""
        try:
            house_key = str(house_number)
            if house_key in self.house_data_objs:
                house_obj = self.house_data_objs[house_key]
                lord_obj = getattr(house_obj, 'LordOfHouse', None)
                if lord_obj and hasattr(lord_obj, 'Name'):
                    return lord_obj.Name
        except Exception as e:
            logger.error(f"Error getting house lord for house {house_number}: {e}")
        return None

    def is_planet_debilitated(self, planet_name: str) -> bool:
        """Check if a planet is debilitated."""
        try:
            planet_obj = self.planet_data_objs.get(planet_name)
            if planet_obj:
                return getattr(planet_obj, 'IsPlanetDebilitated', False)
        except Exception as e:
            logger.error(f"Error checking debilitation for {planet_name}: {e}")
        return False

    def is_planet_in_house(self, planet_name: str, house_number: int) -> bool:
        """Check if a planet is in a specific house."""
        planet_house = self.get_planet_house(planet_name)
        return planet_house == house_number if planet_house else False

    def is_planet_in_houses(self, planet_name: str, house_numbers: List[int]) -> bool:
        """Check if a planet is in any of the given houses."""
        return any(self.is_planet_in_house(planet_name, h) for h in house_numbers)

    def is_planets_together(self, planet1: str, planet2: str) -> bool:
        """Check if two planets are together (in same house)."""
        house1 = self.get_planet_house(planet1)
        house2 = self.get_planet_house(planet2)
        return house1 == house2 if (house1 and house2) else False

    def are_multiple_planets_together(self, planets: List[str]) -> bool:
        """Check if multiple planets are together in the same house."""
        if not planets:
            return False
        houses = [self.get_planet_house(p) for p in planets]
        if None in houses:
            return False
        return len(set(houses)) == 1

    def is_planet_aspected_by(self, planet_name: str, aspecting_planets: List[str]) -> bool:
        """Check if a planet is aspected by any of the given planets."""
        try:
            planet_obj = self.planet_data_objs.get(planet_name)
            if not planet_obj:
                return False
            
            aspecting_planets_set = set(aspecting_planets)
            planets_aspecting = getattr(planet_obj, 'PlanetsAspectingPlanet', [])
            return any(p in planets_aspecting for p in aspecting_planets_set)
        except Exception as e:
            logger.error(f"Error checking aspects for {planet_name}: {e}")
        return False

    def get_lagna_sign(self) -> Optional[str]:
        """Get the lagna (1st house) sign."""
        try:
            if '1' in self.house_data_objs:
                house_obj = self.house_data_objs['1']
                rasi_sign = getattr(house_obj, 'HouseRasiSign', None)
                if rasi_sign and hasattr(rasi_sign, 'Name'):
                    return rasi_sign.Name
        except Exception as e:
            logger.error(f"Error getting lagna sign: {e}")
        return None

    def get_sign_lord(self, sign_name: str) -> Optional[str]:
        """Get the lord of a given zodiac sign."""
        sign_lords = {
            "Aries": "Mars",
            "Taurus": "Venus",
            "Gemini": "Mercury",
            "Cancer": "Moon",
            "Leo": "Sun",
            "Virgo": "Mercury",
            "Libra": "Venus",
            "Scorpio": "Mars",
            "Sagittarius": "Jupiter",
            "Capricorn": "Saturn",
            "Aquarius": "Saturn",
            "Pisces": "Jupiter"
        }
        return sign_lords.get(sign_name)

    def get_nth_lord(self, house_number: int) -> Optional[str]:
        """
        Get the lord of the Nth house by getting the lord of the sign in that house.
        """
        try:
            house_key = str(house_number)
            if house_key in self.house_data_objs:
                house_obj = self.house_data_objs[house_key]
                rasi_sign = getattr(house_obj, 'HouseRasiSign', None)
                if rasi_sign and hasattr(rasi_sign, 'Name'):
                    return self.get_sign_lord(rasi_sign.Name)
        except Exception as e:
            logger.error(f"Error getting {house_number}th lord: {e}")
        return None

    def add_curse(self, curse_record: CurseRecord) -> None:
        """Add a detected curse to the list."""
        self.detected_curses.append(curse_record)
        logger.info(f"Curse detected: {curse_record.curse_name} (Severity: {curse_record.severity})")

    @abstractmethod
    def detect_curses(self) -> List[CurseRecord]:
        """Detect curses of this type. To be implemented by subclasses."""
        pass

    def print_curse_summary(self) -> None:
        """Print a summary of detected curses."""
        if not self.detected_curses:
            print("  ✓ No curses detected.")
            return

        print(f"\n  📋 Curses Found: {len(self.detected_curses)}")
        for i, curse in enumerate(self.detected_curses, 1):
            print(f"\n  {i}. {curse.curse_name}")
            print(f"     Severity: {curse.severity.upper()}")
            print(f"     Type: {curse.curse_type}")
            print(f"     Houses: {', '.join(map(str, curse.houses_involved))}")
            print(f"     Planets: {', '.join(curse.planets_involved)}")
            print(f"     Description: {curse.description}")
            if curse.remedies:
                print(f"     Remedies: {', '.join(curse.remedies)}")
