import logging
import traceback
import json
from typing import Tuple, Optional
from dataclasses import dataclass

from input_parser import parse_user_input
from get_data import get_all_planetary_data, get_all_house_data
from utils import extract_dob
from yoga_detector.vedic_yoga_detector import VedicYogaDetector
from debug_tools import debug_output
from astro_cache import (
    init_cache_db, generate_hash_from_input,
    load_from_cache, save_to_cache, load_raw_input_by_id
)
from parsers.house_data_parser import HouseDataParser
from parsers.planet_data_parser import PlanetDataParser
from dasha.vimshottari import VimshottariDasha
from analyzer.bphs_house_analyzer import BPHSHouseAnalyzer
from analyzer.astro_table import AstroTableGenerator
from analyzer.varga import VargaChartAnalyzer
from analyzer.lagna_analyzer import LagnaAnalyzer
from curses.curse_detector import CurseDetector

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s'
)
logger = logging.getLogger(__name__)

DEFAULT_INPUT = 'ABC | 17:59 29/11/1986 +05:30 | Mumbai, India, 72.92, 13.04'

# Manfred | 08:30 20/01/1997 +03:00 | Kebirigo, Kenya, 72.92, 06.04


@dataclass
class ChartData:
    """Container for parsed chart data"""
    planet_data: dict
    house_data: dict  
    planet_objects: list
    house_objects: list
    dob: Optional[str] = None


class AstroChartProcessor:
    """Main processor for astrological chart analysis"""
    
    def __init__(self):
        self.conn = init_cache_db()
    
    def get_user_input(self) -> str:
        """Get user input with default fallback"""
        print("Enter birth details (or press Enter to use default):")
        user_input = input("> ").strip()
        
        if not user_input:
            print(f"\nUsing default input: {DEFAULT_INPUT}")
            return DEFAULT_INPUT
        return user_input
    
    def load_from_database(self, chart_id: str) -> ChartData:
        """Load chart data from database by ID"""
        try:
            db_data = load_raw_input_by_id(self.conn, int(chart_id))
            planet_data = json.loads(db_data[0])
            house_data = json.loads(db_data[1])
            
            debug_output(planet_data, house_data)
            logger.info(f'Raw Input: {db_data[2]}')
            
            return ChartData(
                planet_data=planet_data,
                house_data=house_data,
                planet_objects=PlanetDataParser(db_data[0]).parse(),
                house_objects=HouseDataParser(db_data[1]).parse(),
                dob=extract_dob(db_data[2])
            )
        except Exception as e:
            logger.error(f"Failed to load from database: {e}")
            raise
    
    def fetch_or_cache_data(self, user_input: str, birth_time) -> Tuple[dict, dict]:
        """Get chart data from cache or fetch fresh data"""
        hash_key = generate_hash_from_input(user_input)
        print("🔍 Checking cache...")
        
        planet_data, house_data = load_from_cache(self.conn, hash_key)
        
        if planet_data and house_data:
            print("✅ Cache hit.\n")
        else:
            print("📡 Fetching fresh data...")
            planet_data = get_all_planetary_data(birth_time)
            house_data = get_all_house_data(birth_time)
            save_to_cache(self.conn, hash_key, user_input, planet_data, house_data)
            print("✅ Data cached.\n")
        
        return planet_data, house_data
    
    def process_new_input(self, user_input: str) -> ChartData:
        """Process new user input and create chart data"""
        name, birth_time = parse_user_input(user_input)
        print("✅ Input parsed successfully.\n")
        
        planet_data, house_data = self.fetch_or_cache_data(user_input, birth_time)
        
        return ChartData(
            planet_data=planet_data,
            house_data=house_data,
            planet_objects=PlanetDataParser(planet_data).parse(),
            house_objects=HouseDataParser(house_data).parse(),
            dob=extract_dob(user_input)
        )
    
    def get_chart_data(self, user_input: str) -> ChartData:
        """Get chart data from either database ID or new input"""
        print("\n📅 Processing birth details...")
        
        if user_input.isdigit():
            return self.load_from_database(user_input)
        else:
            return self.process_new_input(user_input)
    
    def generate_reports(self, chart_data: ChartData) -> None:
        """Generate all astrological reports and analyses"""
        try:
            # 1. Astrological Tables
            print("📊 Generating astrological tables...")
            table_gen = AstroTableGenerator(chart_data.planet_data, chart_data.house_data)
            table_gen.print_all()

            analyzer = VargaChartAnalyzer(chart_data.planet_objects, chart_data.house_objects)
            analyzer.print_complete_analysis([1, 9, 10, 12])
            # analyzer.get_chart(9).print_chart()
            
            # 2. Dasha System
            if chart_data.dob:
                print("\n🕐 Calculating Vimshottari Dasha...")
                moon_sign = chart_data.planet_data['Moon']['PlanetRasiD1Sign']
                dasha_calc = VimshottariDasha(moon_sign, chart_data.dob)
                dasha_calc.print_dasha(levels=3, years_ahead=35)
            
            # 3. House Analysis
            print("\n🏠 Analyzing houses...")
            analyzer = BPHSHouseAnalyzer(chart_data.planet_objects, chart_data.house_objects)
            report = analyzer.generate_comprehensive_report()
            print(report)
            print(analyzer.generate_summary_table())

            # 4. Lagna Analyzer
            lagna_analyzer = LagnaAnalyzer(chart_data.planet_objects, chart_data.house_objects)
            print(lagna_analyzer.generate_detailed_report())
            
            # 5. Yoga Detection
            print("\n🧘 Detecting Vedic Yogas...")
            yogas_detector = VedicYogaDetector(enable_detailed_logging=True)
            yogas_detector.detect_all_yogas(chart_data.planet_objects, chart_data.house_objects)

            # 6. Curses Detection
            print("\n🧙 Detecting Curses...")
            curses_detector_instance = CurseDetector(chart_data.planet_objects, chart_data.house_objects)
            curses_detector_instance.detect_all_curses()
            
        except Exception as e:
            logger.error(f"Error generating reports: {e}")
            print(f"❌ Report generation failed: {e}")
            traceback.print_exc()


def main():
    """Main entry point for astrological chart analysis"""
    processor = AstroChartProcessor()
    
    try:
        # Get user input and process chart data
        user_input = processor.get_user_input()
        chart_data = processor.get_chart_data(user_input)
        
        # Generate all reports
        processor.generate_reports(chart_data)
        
    except KeyboardInterrupt:
        print("\n👋 Analysis interrupted by user")
    except Exception as e:
        logger.error(f"Unexpected error in main: {e}")
        print(f"❌ Analysis failed: {e}")
        traceback.print_exc()
    finally:
        # Clean up database connection if needed
        if hasattr(processor, 'conn') and processor.conn:
            processor.conn.close()


if __name__ == "__main__":
    main()
