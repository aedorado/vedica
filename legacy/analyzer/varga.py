from typing import Dict, List, Optional, Any
import pandas as pd
from dataclasses import dataclass, field
from tabulate import tabulate
import re


@dataclass
class HouseOccupancy:
    """Represents what's in a house for a specific varga chart."""
    house_number: int
    sign: str
    planets: List[str] = field(default_factory=list)
    
    def add_planet(self, planet_name: str):
        """Add a planet to this house."""
        if planet_name not in self.planets:
            self.planets.append(planet_name)
    
    def has_planet(self, planet_name: str) -> bool:
        """Check if a planet is in this house."""
        return planet_name in self.planets
    
    def planet_count(self) -> int:
        """Get number of planets in this house."""
        return len(self.planets)

from dataclasses import dataclass, field
from typing import Dict, List, Optional

@dataclass
class VargaChart:
    """Represents a complete varga chart with houses and their occupants."""
    chart_number: int
    chart_name: str
    houses: Dict[int, 'HouseOccupancy'] = field(default_factory=dict)

    def get_house(self, house_num: int) -> Optional['HouseOccupancy']:
        """Get house occupancy for a specific house."""
        return self.houses.get(house_num)
    
    def get_planet_house(self, planet_name: str) -> Optional[int]:
        """Find which house a planet is in."""
        for house_num, house_occ in self.houses.items():
            if house_occ.has_planet(planet_name):
                return house_num
        return None
    
    def get_planet_sign(self, planet_name: str) -> Optional[str]:
        """Get the sign a planet is in."""
        house_num = self.get_planet_house(planet_name)
        if house_num:
            house_occ = self.get_house(house_num)
            return house_occ.sign if house_occ else None
        return None
    
    def get_planets_in_sign(self, sign_name: str) -> List[str]:
        """Get all planets in a specific sign."""
        planets = []
        for house_occ in self.houses.values():
            if house_occ.sign == sign_name:
                planets.extend(house_occ.planets)
        return planets
    
    def get_empty_houses(self) -> List[int]:
        """Get list of houses with no planets."""
        return [house_num for house_num, house_occ in self.houses.items() 
                if house_occ.planet_count() == 0]
    
    def get_occupied_houses(self) -> List[int]:
        """Get list of houses with planets."""
        return [house_num for house_num, house_occ in self.houses.items() 
                if house_occ.planet_count() > 0]

    def get_planets_in_house(self, house_num: int) -> List[str]:
        """Get all planets in a specific house."""
        house_occ = self.get_house(house_num)
        return house_occ.planets if house_occ else []
    
    def print_chart(self):
        """Prints the Varga chart in a readable format."""
        print(f"Varga Chart {self.chart_number}: {self.chart_name}")
        print("=" * 40)
        for house_num in self.houses.keys():
            house = self.houses[house_num]
            planets_str = ', '.join(house.planets) if house.planets else 'None'
            print(f"House {house_num}: Sign = {house.sign}, Planets = {planets_str}")
        print("=" * 40)


@dataclass
class VargaPosition:
    """Represents a position in a varga chart."""
    chart_number: int
    chart_name: str
    sign: str
    
@dataclass
class PlanetVargaPositions:
    """Represents all varga positions for a planet."""
    planet_name: str
    positions: Dict[int, VargaPosition] = field(default_factory=dict)
    
    def get_position(self, chart_num: int) -> Optional[VargaPosition]:
        return self.positions.get(chart_num)
        
    def get_sign(self, chart_num: int) -> str:
        pos = self.get_position(chart_num)
        return pos.sign if pos else 'N/A'

@dataclass
class HouseVargaPositions:
    """Represents all varga positions for a house."""
    house_number: int
    positions: Dict[int, VargaPosition] = field(default_factory=dict)
    
    def get_position(self, chart_num: int) -> Optional[VargaPosition]:
        return self.positions.get(chart_num)
        
    def get_sign(self, chart_num: int) -> str:
        pos = self.get_position(chart_num)
        return pos.sign if pos else 'N/A'

@dataclass
class VargaAnalysisResult:
    """Complete varga analysis result with both chart-centric and position-centric data."""
    # Chart-centric structure (new)
    charts: Dict[int, VargaChart] = field(default_factory=dict)
    
    # Position-centric structure (original)
    planets: Dict[str, PlanetVargaPositions] = field(default_factory=dict)
    houses: Dict[int, HouseVargaPositions] = field(default_factory=dict)
    
    # Common
    available_charts: List[int] = field(default_factory=list)
    
    def get_chart(self, chart_num: int) -> Optional[VargaChart]:
        """Get a complete varga chart."""
        return self.charts.get(chart_num)
    
    def get_planet_positions_across_charts(self, planet_name: str) -> Dict[int, Dict[str, Any]]:
        """Get a planet's positions across all charts."""
        positions = {}
        for chart_num, chart in self.charts.items():
            house_num = chart.get_planet_house(planet_name)
            sign = chart.get_planet_sign(planet_name)
            if house_num and sign:
                positions[chart_num] = {
                    'house': house_num,
                    'sign': sign,
                    'chart_name': chart.chart_name
                }
        return positions
    
    def get_house_signs_across_charts(self, house_num: int) -> Dict[int, str]:
        """Get what sign a house falls in across all charts."""
        signs = {}
        for chart_num, chart in self.charts.items():
            house_occ = chart.get_house(house_num)
            if house_occ:
                signs[chart_num] = house_occ.sign
        return signs

class VargaChartAnalyzer:
    """Analyzes planetary and house positions across all varga charts (D1-D60)."""
    
    # Varga chart mappings with their names
    VARGA_CHARTS = {
        1: ('Rasi', 'RasiSign'),        # Overridden in _extract_varga_positions
        2: ('Hora', 'HoraD2Sign'),      # Overridden in _extract_varga_positions  
        3: ('Drekkana', 'DrekkanaD3Sign'),
        4: ('Chaturthams', 'ChaturthamshaD4Sign'),
        7: ('Saptams', 'SaptamshaD7Sign'),
        9: ('Navams', 'NavamshaD9Sign'),
        10: ('Dashams', 'DashamamshaD10Sign'),
        12: ('Dwadashams', 'DwadashamshaD12Sign'),
        16: ('Shodashams', 'ShodashamshaD16Sign'),
        20: ('Vimshams', 'VimshamshaD20Sign'),
        24: ('Chaturvimsham', 'ChaturvimshamshaD24Sign'),
        27: ('Bhams', 'BhamshaD27Sign'),
        30: ('Trimshams', 'TrimshamshaD30Sign'),
        40: ('Khavedams', 'KhavedamshaD40Sign'),
        45: ('Akshavedams', 'AkshavedamshaD45Sign'),
        60: ('Shastyams', 'ShashtyamshaD60Sign')
    }
    
    
    def __init__(self, planets_data: Dict[str, Any], houses_data: Dict[str, Any]):
        """Initialize with planets and houses data."""
        self.planets_data = planets_data
        self.houses_data = houses_data
        self.varga_positions = self._extract_varga_positions()
        self.analysis_result = self._create_analysis_result()
    
    def _create_analysis_result(self) -> VargaAnalysisResult:
        """Create the analysis result with the new chart-centric structure."""
        result = VargaAnalysisResult()
        
        # Get all available charts
        available_charts = set()
        for planet_positions in self.varga_positions['planets'].values():
            for chart_num, sign in planet_positions.items():
                if sign != 'N/A':
                    available_charts.add(chart_num)
        
        result.available_charts = sorted(list(available_charts))
        
        # Create VargaChart objects for each available chart
        for chart_num in result.available_charts:
            chart_name = self.VARGA_CHARTS[chart_num][0]
            varga_chart = VargaChart(chart_number=chart_num, chart_name=chart_name)
            
            # Initialize all houses with their signs
            for house_num, house_positions in self.varga_positions['houses'].items():
                house_sign = house_positions.get(chart_num, 'N/A')
                if house_sign != 'N/A':
                    house_occ = HouseOccupancy(
                        house_number=house_num,
                        sign=house_sign
                    )
                    varga_chart.houses[house_num] = house_occ
            
            # Add planets to their respective houses
            for planet_name, planet_positions in self.varga_positions['planets'].items():
                planet_sign = planet_positions.get(chart_num, 'N/A')
                if planet_sign != 'N/A':
                    # Find which house has this sign
                    for house_num, house_occ in varga_chart.houses.items():
                        if house_occ.sign == planet_sign:
                            house_occ.add_planet(planet_name)
                            break
            
            result.charts[chart_num] = varga_chart
        
        return result
    

    def get_chart(self, chart_num: int) -> Optional[VargaChart]:
            """Get a complete varga chart."""
            return self.analysis_result.charts.get(chart_num)
    
    def get_house_occupancy(self, house_num: int, chart_num: int) -> Optional[HouseOccupancy]:
        """Get complete house occupancy info."""
        chart = self.get_chart(chart_num)
        if chart:
            return chart.get_house(house_num)
        return None

    def _extract_varga_positions(self) -> Dict[str, Dict[str, Dict[str, str]]]:
        """Extract all varga chart positions for planets and houses."""
        positions = {'planets': {}, 'houses': {}}
        
        # Special mappings for inconsistent attribute names
        PLANET_ATTR_OVERRIDES = {
            1: 'PlanetRasiD1Sign',    # D1 planet attribute
            2: 'PlanetHoraD2Signs',   # D2 planet attribute (note the 's')
        }
        
        HOUSE_ATTR_OVERRIDES = {
            1: 'HouseRasiSign',       # D1 house attribute (no D1 in name)
            2: 'HouseHoraD2Sign',     # D2 house attribute
        }
        
        # Extract planet positions
        for planet_name, planet_obj in self.planets_data.items():
            positions['planets'][planet_name] = {}
            
            for chart_key, (chart_name, attr_suffix) in self.VARGA_CHARTS.items():
                # Use override if available, otherwise construct normally
                if chart_key in PLANET_ATTR_OVERRIDES:
                    planet_attr = PLANET_ATTR_OVERRIDES[chart_key]
                else:
                    planet_attr = f'Planet{attr_suffix}'
                
                # Try to get the attribute
                sign_detail = getattr(planet_obj, planet_attr, None)
                if sign_detail and hasattr(sign_detail, 'Name'):
                    positions['planets'][planet_name][chart_key] = sign_detail.Name
                else:
                    positions['planets'][planet_name][chart_key] = 'N/A'
        
        # Extract house positions
        for house_num, house_obj in self.houses_data.items():
            positions['houses'][house_num] = {}
            
            for chart_key, (chart_name, attr_suffix) in self.VARGA_CHARTS.items():
                # Use override if available, otherwise construct normally
                if chart_key in HOUSE_ATTR_OVERRIDES:
                    house_attr = HOUSE_ATTR_OVERRIDES[chart_key]
                else:
                    house_attr = f'House{attr_suffix}'
                
                # Try to get the attribute
                sign_detail = getattr(house_obj, house_attr, None)
                if sign_detail and hasattr(sign_detail, 'Name'):
                    positions['houses'][house_num][chart_key] = sign_detail.Name
                else:
                    positions['houses'][house_num][chart_key] = 'N/A'
        
        return positions
    
    def get_chart_positions(self, chart_num: int) -> Dict[str, Any]:
        """Get all positions for a specific varga chart by number."""
        if chart_num not in self.VARGA_CHARTS:
            raise ValueError(f"Invalid chart number. Available: {list(self.VARGA_CHARTS.keys())}")
        
        chart_name = self.VARGA_CHARTS[chart_num][0]
        result = {
            'chart_number': chart_num,
            'chart_name': chart_name,
            'planets': {},
            'houses': {}
        }
        
        for planet_name, planet_data in self.analysis_result.planets.items():
            result['planets'][planet_name] = planet_data.get_sign(chart_num)
        
        for house_num, house_data in self.analysis_result.houses.items():
            result['houses'][house_num] = house_data.get_sign(chart_num)
        
        return result
    
    def get_planet_varga_table(self, chart_nums: Optional[List[int]] = None) -> pd.DataFrame:
        """Generate a comprehensive table of planet positions across specified varga charts."""
        if not self.analysis_result.planets:
            return pd.DataFrame()
        
        # Use specified charts or all available charts
        charts_to_use = chart_nums if chart_nums else self.analysis_result.available_charts
        charts_to_use = [c for c in charts_to_use if c in self.VARGA_CHARTS]
        
        # Create DataFrame with planets as rows and varga charts as columns
        df_data = {}
        
        for chart_num in charts_to_use:
            chart_name = self.VARGA_CHARTS[chart_num][0]
            col_name = f"D{chart_num} ({chart_name})"
            df_data[col_name] = []
        
        planet_names = list(self.analysis_result.planets.keys())
        
        for planet in planet_names:
            for chart_num in charts_to_use:
                chart_name = self.VARGA_CHARTS[chart_num][0]
                col_name = f"D{chart_num} ({chart_name})"
                position = self.analysis_result.planets[planet].get_sign(chart_num)
                df_data[col_name].append(position)
        
        df = pd.DataFrame(df_data, index=planet_names)
        return df
    
    def get_house_varga_table(self, chart_nums: Optional[List[int]] = None) -> pd.DataFrame:
        """Generate a comprehensive table of house positions across specified varga charts."""
        if not self.analysis_result.houses:
            return pd.DataFrame()
        
        # Use specified charts or all available charts
        charts_to_use = chart_nums if chart_nums else self.analysis_result.available_charts
        charts_to_use = [c for c in charts_to_use if c in self.VARGA_CHARTS]
        
        # Create DataFrame with houses as rows and varga charts as columns
        df_data = {}
        
        for chart_num in charts_to_use:
            chart_name = self.VARGA_CHARTS[chart_num][0]
            col_name = f"D{chart_num} ({chart_name})"
            df_data[col_name] = []
        
        house_numbers = sorted(self.analysis_result.houses.keys())
        
        for house_num in house_numbers:
            for chart_num in charts_to_use:
                chart_name = self.VARGA_CHARTS[chart_num][0]
                col_name = f"D{chart_num} ({chart_name})"
                position = self.analysis_result.houses[house_num].get_sign(chart_num)
                df_data[col_name].append(position)
        
        df = pd.DataFrame(df_data, index=[f"House {h}" for h in house_numbers])
        return df
    
    def print_planet_summary(self, chart_nums: Optional[List[int]] = None, tablefmt: str = "grid"):
        """Print a formatted summary of planet positions using tabulate."""
        df = self.get_planet_varga_table(chart_nums)
        if df.empty:
            print("No planet data available.")
            return
        
        charts_display = f" (D{', D'.join(map(str, chart_nums))})" if chart_nums else ""
        print("=" * 80)
        print(f"PLANETARY POSITIONS ACROSS VARGA CHARTS{charts_display}")
        print("=" * 80)
        
        # Convert DataFrame to list format for tabulate
        headers = ['Planet'] + list(df.columns)
        table_data = []
        for planet, row in df.iterrows():
            table_data.append([planet] + list(row))
        
        print(tabulate(table_data, headers=headers, tablefmt=tablefmt))
        print()
    
    def print_house_summary(self, chart_nums: Optional[List[int]] = None, tablefmt: str = "grid"):
        """Print a formatted summary of house positions using tabulate."""
        df = self.get_house_varga_table(chart_nums)
        if df.empty:
            print("No house data available.")
            return
        
        charts_display = f" (D{', D'.join(map(str, chart_nums))})" if chart_nums else ""
        print("=" * 80)
        print(f"HOUSE POSITIONS ACROSS VARGA CHARTS{charts_display}")
        print("=" * 80)
        
        # Convert DataFrame to list format for tabulate
        headers = ['House'] + list(df.columns)
        table_data = []
        for house, row in df.iterrows():
            table_data.append([house] + list(row))
        
        print(tabulate(table_data, headers=headers, tablefmt=tablefmt))
        print()
    
    def get_available_charts(self) -> List[int]:
        """Get list of available varga charts in the data."""
        return self.analysis_result.available_charts
    
    def print_complete_analysis(self, chart_nums: Optional[List[int]] = None, tablefmt: str = "grid"):
        """Print complete analysis with specified or all available data."""
        charts_to_show = chart_nums if chart_nums else self.analysis_result.available_charts
        charts_display = f" (D{', D'.join(map(str, charts_to_show))})" if chart_nums else ""
        
        print("COMPLETE VARGA CHART ANALYSIS")
        print("=" * 80)
        
        available_charts = self.get_available_charts()
        print(f"Available Charts: D{', D'.join(map(str, available_charts))}")
        print()
        
        self.print_planet_summary(charts_to_show, tablefmt)
        self.print_house_summary(charts_to_show, tablefmt)
        
        # Print specific chart details for requested charts
        charts_for_detail = charts_to_show if charts_to_show else available_charts  # Limit to first 3 for brevity
        for chart_num in charts_for_detail:
            self.print_chart_specific_summary(chart_num)
            print("=" * 80, "\n\n")

    def print_chart_specific_summary(self, chart_num: int):
        """Print summary for a specific varga chart."""
        chart = self.get_chart(chart_num)
        if not chart:
            print(f"Chart D{chart_num} not available")
            return
        
        print(f"\nD{chart_num} - {chart.chart_name} Chart Positions")
        print("-" * 50)
        
        # Print houses with planets
        house_data = []
        for house_num in chart.houses.keys():
            house_occ = chart.houses[house_num]
            planets_str = ', '.join(house_occ.planets) if house_occ.planets else ''
            house_data.append([f"House {house_num}", house_occ.sign, planets_str])
        
        print(tabulate(house_data, headers=['House', 'Sign', 'Planets'], tablefmt='simple'))
        
        return {
            'chart_number': chart_num,
            'chart_name': chart.chart_name,
            'houses': {house_num: {'sign': house_occ.sign, 'planets': house_occ.planets} 
                      for house_num, house_occ in chart.houses.items()}
        }
    
# Example usage:
if __name__ == "__main__":
    # Assuming you have your data loaded as:
    # planets_data = {"Sun": sun_planet_obj, "Moon": moon_planet_obj, ...}
    # houses_data = {"1": house1_obj, "2": house2_obj, ...}
    
    # analyzer = VargaChartAnalyzer(planets_data, houses_data)
    
    # Print specific charts only
    # analyzer.print_complete_analysis([1, 7, 9, 10])  # D1, D7, D9, D10 only
    
    # Get specific planet/house positions
    # venus_d9 = analyzer.get_planet_position("Venus", 9)  # Venus in D9
    # house1_d10 = analyzer.get_house_position(1, 10)     # House 1 in D10
    
    # Get all positions for a specific chart
    # d9_positions = analyzer.get_chart_positions(9)  # All D9 positions
    
    # Get tables for specific charts
    # planet_df = analyzer.get_planet_varga_table([1, 9, 10])
    # house_df = analyzer.get_house_varga_table([1, 9, 10])
    
    pass