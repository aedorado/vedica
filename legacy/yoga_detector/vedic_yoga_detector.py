import logging
import os
import json
from tabulate import tabulate
from colorama import Fore, Style
import traceback
from typing import Dict, List, Optional, Any
from collections import defaultdict

# Import the data classes
from .data_validator import DataValidator
from .house_ownership_parser import HouseOwnershipParser
from .raja_yoga_detector import SimpleRajaYogaDetector
from .dhan_yoga_detector import SimpleDhanaYogaDetector
from .vipreet_raja_yoga import SimplifiedVipareetRajaDetector
from .pancha_mahapurusha import PanchMahapurushYogaDetector
from .neech_bhanga_raja_yoga import NeechBhangaYogaDetector
from .parivartan_yoga_detector import ParivartanaYogaDetector
from .nabhasa_yoga_detector import NabhasaYogaDetector
from .malika_yogas_detector import MallikaYogaDetector
from .moon_yogas import MoonYogaDetector
from .sun_yoga_detector import SunYogaDetector

from yogas.vedic_yoga import VedicYoga

from models.planet_detail import PlanetDetails
from models.house_detail import HouseDetail

import logging
logger = logging.getLogger(__name__)

class VedicYogaDetector:
    """
    Main class for detecting various types of Vedic Yogas.
    
    This class coordinates multiple yoga detectors and provides a unified interface
    for comprehensive yoga analysis.
    """
    
    def __init__(self, enable_detailed_logging: bool = False):
        """
        Initialize the Vedic Yoga detector.
        
        Args:
            enable_detailed_logging: Enable detailed debug logging
        """
        self.enable_detailed_logging = enable_detailed_logging
        self.validator = DataValidator()
        self.parser = HouseOwnershipParser()
        
        if enable_detailed_logging:
            logging.getLogger().setLevel(logging.DEBUG)
    
    def detect_all_yogas(self, planet_data_objs: Dict[str, PlanetDetails], 
                         house_data_objs: Dict[str, HouseDetail]) -> Dict[str, List[VedicYoga]]:
        """
        Main method to detect all types of yogas in the chart.
        
        Args:
            planet_data_objs: Dictionary containing planet names as keys and PlanetDetails objects as values
            house_data_objs: Dictionary containing house keys and HouseDetail objects as values
            
        Returns:
            Dictionary with yoga categories as keys and lists of yogas as values
        """
        logger.info("Starting comprehensive Vedic Yoga detection analysis...")
        
        try:
            # Validate input data
            if not self._validate_input_data_objs(planet_data_objs, house_data_objs):
                logger.error("Input data validation failed")
                return {}
            
            # Initialize detectors with the new interface
            # raja_detector = RajaYogaDetector(planet_data_objs, house_data_objs)
            
            # TODO: Refactor other detectors to use the same interface
            # For now, we'll need to build chart_data for the old detectors
            chart_data = self._build_chart_data_from_objects(planet_data_objs, house_data_objs)
            # dhana_detector = DhanaYogaDetector(chart_data)
            # vipreet_ry_detector = VipareetRajaDetector(chart_data)
            # panch_mp_detector = PanchMahapurushDetector(chart_data)
            
            # Detect different types of yogas
            results = {}
            
            # Detect Raja Yogas (using new refactored detector)
            raja_yoga_detector = SimpleRajaYogaDetector(planet_data_objs, house_data_objs)
            raja_yogas = raja_yoga_detector.detect_all_raja_yogas()
            raja_yoga_detector.print_yoga_summary(raja_yogas)

            dhan_yoga_detector = SimpleDhanaYogaDetector(planet_data_objs, house_data_objs)
            dhana_yogas = dhan_yoga_detector.detect_all_dhana_yogas()
            dhan_yoga_detector.print_yoga_summary(dhana_yogas)

            moon_yoga_detector = MoonYogaDetector(planet_data_objs, house_data_objs)
            moon_yoga_detector.detect_all_yogas()
            moon_yoga_detector.print_report()

            sun_yoga_detector = SunYogaDetector(planet_data_objs, house_data_objs)
            sun_yoga_detector.detect_all_yogas()
            sun_yoga_detector.print_report()

            detector = MallikaYogaDetector(planet_data_objs, house_data_objs)
            detector.detect_all_mallika_yogas()
            detector.print_report()

            vipreet_ry_detector = SimplifiedVipareetRajaDetector(planet_data_objs, house_data_objs)
            vr_yogas = vipreet_ry_detector.detect_all_vipareet_raja_yogas()
            vipreet_ry_detector.print_yoga_summary(vr_yogas)

            panch_mp_detector = PanchMahapurushYogaDetector(planet_data_objs, house_data_objs)
            pmp_yogas = panch_mp_detector.detect_panch_mahapurush_yogas()
            panch_mp_detector.print_yoga_summary(pmp_yogas)

            neech_bhanga_detector = NeechBhangaYogaDetector(planet_data_objs, house_data_objs)
            neecha_bhanga_yogas = neech_bhanga_detector.detect_all_neecha_bhanga_yogas()
            neech_bhanga_detector.print_yoga_summary(neecha_bhanga_yogas)

            parivartan_yoga_detector = ParivartanaYogaDetector(planet_data_objs, house_data_objs)
            parivartan_yogas = parivartan_yoga_detector.detect_all_parivartana_yogas()
            parivartan_yoga_detector.print_yoga_summary(parivartan_yogas)

            nabhasa_yoga_detector = NabhasaYogaDetector(planet_data_objs, house_data_objs)
            nabhasa_yogas = nabhasa_yoga_detector.detect_all_yogas()
            nabhasa_yoga_detector.print_yoga_summary(nabhasa_yogas)
            
            return results
            
        except Exception as e:
            logger.error(f"Error during Vedic Yoga detection: {e}")
            print(traceback.format_exc())
            return {}
    
    def _validate_input_data_objs(self, planet_data_objs: Dict[str, PlanetDetails], 
                                  house_data_objs: Dict[str, HouseDetail]) -> bool:
        """Validate that input data objects are complete and properly formatted."""
        if not planet_data_objs or not house_data_objs:
            logger.error("Empty planet or house data objects provided")
            return False
        
        # Validate essential planets exist
        essential_planets = ['Sun', 'Moon', 'Mars', 'Mercury', 'Jupiter', 'Venus', 'Saturn']
        for planet in essential_planets:
            if planet not in planet_data_objs:
                logger.warning(f"Missing data for essential planet: {planet}")
            elif not isinstance(planet_data_objs[planet], PlanetDetails):
                logger.warning(f"Invalid data type for planet {planet}: expected PlanetDetails")
        
        # Validate house data objects
        for house_key, house_obj in house_data_objs.items():
            if not isinstance(house_obj, HouseDetail):
                logger.warning(f"Invalid data type for house {house_key}: expected HouseDetail")
        
        return True

    def _build_chart_data_from_objects(self, planet_data_objs: Dict[str, PlanetDetails], 
                                       house_data_objs: Dict[str, HouseDetail]) -> Dict[str, Any]:
        """
        Build internal data structures from parsed objects for legacy detectors.
        
        NOTE: This method is kept for backward compatibility with detectors that 
        haven't been refactored yet. Once all detectors are refactored, this can be removed.
        """
        chart_data = {
            'house_lords': {},  # house_num -> planet_name
            'planet_lordships': defaultdict(list),  # planet -> [house_nums]
            'house_signs': {},  # house_num -> sign_name
            'planet_signs': {},  # planet -> sign_name
            'planet_houses': {},  # planet -> house_num
            'planet_conjunctions': {},  # planet -> [conjunct_planets]
            'planet_aspects': {},  # planet -> [aspected_planets]
            'planets_aspecting': defaultdict(list),  # planet -> [planets_aspecting_it]
            'house_aspects': defaultdict(list),  # house -> [planets_aspecting_it]
            'sign_lords': {},  # sign -> ruling_planet
            'planet_details': {}  # planet -> PlanetDetails object for additional info
        }
        
        # Process house data objects
        for house_key, house_obj in house_data_objs.items():
            house_num = self._normalize_house_key(house_key)
            if not house_num:
                continue
                
            # Extract house lord - handle both object and dict formats
            lord_name = None
            if hasattr(house_obj, 'LordOfHouse') and house_obj.LordOfHouse:
                if hasattr(house_obj.LordOfHouse, 'Name'):
                    lord_name = house_obj.LordOfHouse.Name
                elif isinstance(house_obj.LordOfHouse, dict) and 'Name' in house_obj.LordOfHouse:
                    lord_name = house_obj.LordOfHouse['Name']
            elif hasattr(house_obj, 'lord') and house_obj.lord:
                lord_name = house_obj.lord
            
            if lord_name:
                chart_data['house_lords'][house_num] = lord_name
                chart_data['planet_lordships'][lord_name].append(house_num)
            
            # Extract house sign - handle both object and dict formats
            sign_name = None
            if hasattr(house_obj, 'HouseRasiSign') and house_obj.HouseRasiSign:
                if hasattr(house_obj.HouseRasiSign, 'Name'):
                    sign_name = house_obj.HouseRasiSign.Name
                elif isinstance(house_obj.HouseRasiSign, dict) and 'Name' in house_obj.HouseRasiSign:
                    sign_name = house_obj.HouseRasiSign['Name']
            elif hasattr(house_obj, 'sign') and house_obj.sign:
                sign_name = house_obj.sign
            
            if sign_name:
                chart_data['house_signs'][house_num] = sign_name
                
                # Also track which planet rules this sign
                if lord_name:
                    chart_data['sign_lords'][sign_name] = lord_name
        
        # Process planet data objects
        for planet_name, planet_obj in planet_data_objs.items():
            # Store the planet details object for reference
            chart_data['planet_details'][planet_name] = planet_obj
            
            # Extract planet's house position - handle both object and attribute formats
            house_num = None
            if hasattr(planet_obj, 'HousePlanetOccupiesBasedOnSign'):
                house_key = planet_obj.HousePlanetOccupiesBasedOnSign
                house_num = self._normalize_house_key(house_key)
            elif hasattr(planet_obj, 'house_num'):
                house_num = planet_obj.house_num
            
            if house_num:
                chart_data['planet_houses'][planet_name] = house_num
            
            # Extract planet's sign position
            sign_name = None
            if hasattr(planet_obj, 'PlanetRasiD1Sign') and planet_obj.PlanetRasiD1Sign:
                if hasattr(planet_obj.PlanetRasiD1Sign, 'Name'):
                    sign_name = planet_obj.PlanetRasiD1Sign.Name
                elif isinstance(planet_obj.PlanetRasiD1Sign, dict) and 'Name' in planet_obj.PlanetRasiD1Sign:
                    sign_name = planet_obj.PlanetRasiD1Sign['Name']
            elif hasattr(planet_obj, 'sign'):
                sign_name = planet_obj.sign
            
            if sign_name:
                chart_data['planet_signs'][planet_name] = sign_name
            
            # Extract conjunctions - compute based on house positions
            conjunctions = []
            if house_num:
                for other_planet, other_house in chart_data['planet_houses'].items():
                    if other_planet != planet_name and other_house == house_num:
                        conjunctions.append(other_planet)
            chart_data['planet_conjunctions'][planet_name] = conjunctions
            
            # Extract aspects from the planet object
            if hasattr(planet_obj, 'PlanetsInAspect') and planet_obj.PlanetsInAspect:
                chart_data['planet_aspects'][planet_name] = planet_obj.PlanetsInAspect
            
            if hasattr(planet_obj, 'PlanetsAspectingPlanet') and planet_obj.PlanetsAspectingPlanet:
                chart_data['planets_aspecting'][planet_name] = planet_obj.PlanetsAspectingPlanet
        
        # Compute BPHS aspects if not already available
        self._compute_bphs_aspects(chart_data)
        
        # Debug output
        if self.enable_detailed_logging:
            self._debug_chart_data(chart_data)
        
        return chart_data

    def _normalize_house_key(self, house_key: str) -> Optional[int]:
        """Normalize house key to integer."""
        if isinstance(house_key, int):
            return house_key if 1 <= house_key <= 12 else None
        
        if isinstance(house_key, str):
            # Handle formats like "House1", "1st", "1", etc.
            house_key = house_key.replace("House", "").replace("st", "").replace("nd", "").replace("rd", "").replace("th", "").strip()
            try:
                house_num = int(house_key)
                return house_num if 1 <= house_num <= 12 else None
            except ValueError:
                return None
        
        return None

    def _compute_bphs_aspects(self, chart_data: Dict[str, Any]):
        """Compute planetary aspects as per BPHS rules."""
        planet_houses = chart_data.get("planet_houses", {})
        house_planets = defaultdict(list)

        for planet, house in planet_houses.items():
            house_planets[house].append(planet)

        ASPECT_OFFSETS = {
            'Sun': [7],
            'Moon': [7],
            'Mercury': [7],
            'Venus': [7],
            'Mars': [4, 7, 8],
            'Jupiter': [5, 7, 9],
            'Saturn': [3, 7, 10],
        }

        # Initialize aspect dictionaries if they don't exist
        if "planet_aspects" not in chart_data:
            chart_data["planet_aspects"] = defaultdict(list)
        if "planets_aspecting" not in chart_data:
            chart_data["planets_aspecting"] = defaultdict(list)
        if "house_aspects" not in chart_data:
            chart_data["house_aspects"] = defaultdict(list)

        for planet, source_house in planet_houses.items():
            if planet in ['Rahu', 'Ketu']:
                continue

            for offset in ASPECT_OFFSETS.get(planet, []):
                target_house = ((source_house + offset - 2) % 12) + 1

                for target_planet in house_planets.get(target_house, []):
                    if target_planet not in ['Rahu', 'Ketu']:
                        if target_planet not in chart_data["planet_aspects"][planet]:
                            chart_data["planet_aspects"][planet].append(target_planet)
                        if planet not in chart_data["planets_aspecting"][target_planet]:
                            chart_data["planets_aspecting"][target_planet].append(planet)

                if planet not in chart_data["house_aspects"][target_house]:
                    chart_data["house_aspects"][target_house].append(planet)

    def _debug_chart_data(self, chart_data: Dict[str, Any]) -> None:
        """Debug chart data by writing to file."""
        output_dir = "../debug_logs"
        os.makedirs(output_dir, exist_ok=True)
        output_path = os.path.join(output_dir, "chart_data_debug.json")
        
        try:
            with open(output_path, "w", encoding="utf-8") as f:
                # Convert objects to serializable format for JSON output
                serializable_chart_data = self._make_serializable(chart_data)
                json.dump(serializable_chart_data, f, indent=2, ensure_ascii=False, default=str)
            logger.info(f"chart_data written to {output_path}")
        except Exception as e:
            logger.error(f"Failed to write chart_data debug file: {e}")

    def _make_serializable(self, obj):
        """Convert objects to serializable format for JSON output."""
        if isinstance(obj, dict):
            return {k: self._make_serializable(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [self._make_serializable(item) for item in obj]
        elif isinstance(obj, (PlanetDetails, HouseDetail)):
            # Convert dataclass objects to dictionaries
            return obj.__dict__ if hasattr(obj, '__dict__') else str(obj)
        elif isinstance(obj, defaultdict):
            return dict(obj)
        else:
            return obj

    def _deduplicate_yogas(self, yogas: List[VedicYoga]) -> List[VedicYoga]:
        """Remove duplicate yogas based on the planets and yoga type involved."""
        yoga_groups = defaultdict(list)
        
        for yoga in yogas:
            # Create a key based on the planets, yoga type, and category
            key = (
                yoga.category,
                yoga.yoga_type,
                tuple(sorted([yoga.primary_planet, yoga.secondary_planet]))
            )
            yoga_groups[key].append(yoga)
        
        unique_yogas = []
        for key, group in yoga_groups.items():
            if len(group) == 1:
                unique_yogas.append(group[0])
            else:
                # If multiple yogas with same planets/type, keep the strongest
                strongest = max(group, key=lambda y: y.strength_score)
                
                # Combine information about all house combinations
                all_combinations = []
                for yoga in group:
                    all_combinations.append(f"{yoga.primary_house}th-{yoga.secondary_house}th")
                
                strongest.additional_info['house_combinations'] = all_combinations
                unique_yogas.append(strongest)
                
                logger.debug(f"Combined {len(group)} similar yogas into one: {strongest.description}")
        
        return unique_yogas
