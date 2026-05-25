from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Union
import re

class VimshottariDasha:
    # Planet periods in years
    PERIODS = {
        'Sun': 6, 'Moon': 10, 'Mars': 7, 'Rahu': 18, 'Jupiter': 16,
        'Saturn': 19, 'Mercury': 17, 'Ketu': 7, 'Venus': 20
    }
    
    # Nakshatra sequence starting from Ashwini (0°)
    NAKSHATRA_LORDS = [
        'Ketu', 'Venus', 'Sun', 'Moon', 'Mars', 'Rahu', 'Jupiter', 'Saturn', 'Mercury'
    ]
    
    # Nakshatra names for display
    NAKSHATRA_NAMES = [
        'Ashwini', 'Bharani', 'Krittika', 'Rohini', 'Mrigashira', 'Ardra', 'Punarvasu',
        'Pushya', 'Ashlesha', 'Magha', 'Purva Phalguni', 'Uttara Phalguni', 'Hasta',
        'Chitra', 'Swati', 'Vishakha', 'Anuradha', 'Jyeshtha', 'Mula', 'Purva Ashadha',
        'Uttara Ashadha', 'Shravana', 'Dhanishtha', 'Shatabhisha', 'Purva Bhadrapada',
        'Uttara Bhadrapada', 'Revati'
    ]
    
    def __init__(self, moon_data: Dict, birth_date: str):
        """
        Initialize with moon data and birth date
        moon_data format: {'Name': 'SignName', 'DegreesIn': {'TotalDegrees': 'float_value'}}
        """
        self.moon_data = moon_data
        self.birth_date = datetime.strptime(birth_date, "%Y-%m-%d")
        
        # Extract total degrees from moon data
        total_degrees = float(moon_data['DegreesIn']['TotalDegrees'])
        
        # Convert sign-based degrees to absolute degrees (0-360)
        sign_names = ['Aries', 'Taurus', 'Gemini', 'Cancer', 'Leo', 'Virgo',
                     'Libra', 'Scorpio', 'Sagittarius', 'Capricorn', 'Aquarius', 'Pisces']
        
        sign_name = moon_data['Name']
        sign_index = sign_names.index(sign_name)
        
        self.moon_degree = (sign_index * 30) + total_degrees
        self.nakshatra_lord = self._get_nakshatra_lord()
        self.nakshatra_name = self._get_nakshatra_name()
        
    def _get_nakshatra_lord(self) -> str:
        """Calculate nakshatra lord based on moon degree"""
        nakshatra_num = int(self.moon_degree / 13.333333)
        lord_index = nakshatra_num % 9
        return self.NAKSHATRA_LORDS[lord_index]
    
    def _get_nakshatra_name(self) -> str:
        """Get nakshatra name based on moon degree"""
        nakshatra_num = int(self.moon_degree / 13.333333)
        return self.NAKSHATRA_NAMES[nakshatra_num]
    
    def _get_remaining_period(self) -> float:
        """Calculate remaining period of current dasha"""
        nakshatra_num = int(self.moon_degree / 13.333333)
        degree_in_nakshatra = self.moon_degree % 13.333333
        completion_ratio = degree_in_nakshatra / 13.333333
        
        current_lord = self.NAKSHATRA_LORDS[nakshatra_num % 9]
        total_period = self.PERIODS[current_lord]
        
        return total_period * (1 - completion_ratio)
    
    def _get_planet_sequence(self, start_planet: str) -> List[str]:
        """Get sequence of planets starting from given planet"""
        planets = list(self.PERIODS.keys())
        start_idx = planets.index(start_planet)
        return planets[start_idx:] + planets[:start_idx]
    
    def calculate_dasha(self, levels: int = 5) -> List[Dict]:
        """Calculate dasha periods up to specified levels"""
        result = []
        current_date = self.birth_date
        
        # Start with current dasha lord
        main_sequence = self._get_planet_sequence(self.nakshatra_lord)
        remaining_first = self._get_remaining_period()
        
        for i, main_planet in enumerate(main_sequence):
            main_period = remaining_first if i == 0 else self.PERIODS[main_planet]
            main_end = current_date + timedelta(days=main_period * 365.25)
            
            dasha_entry = {
                'planet': main_planet,
                'level': 1,
                'start': current_date,
                'end': main_end,
                'duration_years': main_period,
                'sub_periods': []
            }
            
            if levels > 1:
                self._calculate_sub_periods(dasha_entry, main_planet, main_period, 
                                          current_date, main_end, levels, 2)
            
            result.append(dasha_entry)
            current_date = main_end
            
            # Calculate for 120 years total
            if (current_date - self.birth_date).days > 120 * 365.25:
                break
                
        return result
    
    def _calculate_sub_periods(self, parent: Dict, main_planet: str, 
                             main_duration: float, start_date: datetime, 
                             end_date: datetime, max_levels: int, current_level: int):
        """Recursively calculate sub-periods"""
        if current_level > max_levels:
            return
            
        sub_sequence = self._get_planet_sequence(main_planet)
        current_date = start_date
        
        for sub_planet in sub_sequence:
            sub_duration = (self.PERIODS[sub_planet] / 120) * main_duration
            sub_end = current_date + timedelta(days=sub_duration * 365.25)
            
            if sub_end > end_date:
                sub_end = end_date
                sub_duration = (sub_end - current_date).days / 365.25
            
            sub_entry = {
                'planet': sub_planet,
                'level': current_level,
                'start': current_date,
                'end': sub_end,
                'duration_years': sub_duration,
                'sub_periods': []
            }
            
            if current_level < max_levels:
                self._calculate_sub_periods(sub_entry, sub_planet, sub_duration,
                                          current_date, sub_end, max_levels, current_level + 1)
            
            parent['sub_periods'].append(sub_entry)
            current_date = sub_end
            
            if current_date >= end_date:
                break
    
    def print_dasha(self, levels: int = 2, years_ahead: int = 10):
        """Print dasha periods in tree format with current period highlighting"""
        dasha_periods = self.calculate_dasha(levels)
        cutoff_date = self.birth_date + timedelta(days=years_ahead * 365.25)
        today = datetime.now()
        
        # ANSI color codes
        colors = {
            'reset': '\033[0m',
            'main': '\033[91m',      # Bright Red for Mahadasha
            'antar': '\033[93m',     # Bright Yellow for Antardasha
            'pratyantar': '\033[92m', # Bright Green for Pratyantardasha
            'sookshma': '\033[94m',   # Bright Blue for Sookshma
            'prana': '\033[95m',      # Bright Magenta for Prana
            'header': '\033[96m',     # Cyan for headers
            'dim': '\033[37m'         # Gray for non-current periods
        }
        
        # Find current periods at each level
        current_periods = self._find_current_periods(dasha_periods, today, levels)
        
        # Table width
        table_width = 78
        
        def format_table_row(content, width=table_width):
            """Format a table row with proper padding to maintain border alignment"""
            # Remove ANSI codes when calculating length
            import re
            clean_content = re.sub(r'\033\[[0-9;]*m', '', content)
            padding_needed = width - len(clean_content) - 2  # -2 for the border characters
            return f"║ {content}{' ' * padding_needed}║"
        
        # Header
        print(colors['header'] + "╔" + "═" * table_width + "╗" + colors['reset'])
        print(colors['header'] + "║" + " " * ((table_width - 25) // 2) + "VIMSHOTTARI DASHA PERIODS" + " " * ((table_width - 25 + 1) // 2) + "║" + colors['reset'])
        print(colors['header'] + "╠" + "═" * table_width + "╣" + colors['reset'])
        
        # Data rows with proper formatting
        birth_date_text = f"Birth Date: {self.birth_date.strftime('%Y-%m-%d')}"
        print(colors['header'] + format_table_row(birth_date_text) + colors['reset'])
        
        moon_position_text = f"Moon Position: {self.moon_data['Name']} {self.moon_data['DegreesIn']['DegreeMinuteSecond']}"
        print(colors['header'] + format_table_row(moon_position_text) + colors['reset'])
        
        nakshatra_text = f"Nakshatra: {self.nakshatra_name} (Lord: {self.nakshatra_lord})"
        print(colors['header'] + format_table_row(nakshatra_text) + colors['reset'])
        
        remaining_period_text = f"Remaining {self.nakshatra_lord} Period: {self._get_remaining_period():.2f} years"
        print(colors['header'] + format_table_row(remaining_period_text) + colors['reset'])
        
        current_date_text = f"Current Date: {today.strftime('%Y-%m-%d')}"
        print(colors['header'] + format_table_row(current_date_text) + colors['reset'])
        
        print(colors['header'] + "╚" + "═" * table_width + "╝" + colors['reset'])
        print()
        print(colors['header'] + "Dasha Tree (Next " + str(years_ahead) + " years):" + colors['reset'])
        print(".")
        
        for i, main_dasha in enumerate(dasha_periods):
            if main_dasha['start'] > cutoff_date:
                break
            
            is_last_main = (i == len([d for d in dasha_periods if d['start'] <= cutoff_date]) - 1)
            self._print_tree_period(main_dasha, levels, cutoff_date, "", is_last_main, True, 
                                current_periods, today, colors)
        
        # Footer
        print()
        print(colors['header'] + "─" * 80 + colors['reset'])
        print(colors['header'] + f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}" + colors['reset'])
        print(colors['header'] + "Note: Dates are calculated using standard Vimshottari Dasha system" + colors['reset'])
        print(colors['header'] + "Levels: 1=Mahadasha, 2=Antardasha, 3=Pratyantardasha, 4=Sookshma, 5=Prana" + colors['reset'])
        print(colors['header'] + "Current periods are highlighted in color" + colors['reset'])
        print(colors['header'] + "─" * 80 + colors['reset'])

    def _find_current_periods(self, dasha_periods: List[Dict], current_date: datetime, max_levels: int) -> Dict:
        """Find current periods at each level"""
        current_periods = {}
        
        def find_current_recursive(periods: List[Dict], level: int, path: str = ""):
            for period in periods:
                if period['start'] <= current_date <= period['end']:
                    period_path = f"{path}/{period['planet']}" if path else period['planet']
                    current_periods[level] = {
                        'planet': period['planet'],
                        'path': period_path,
                        'start': period['start'],
                        'end': period['end']
                    }
                    
                    if level < max_levels and period['sub_periods']:
                        find_current_recursive(period['sub_periods'], level + 1, period_path)
                    break
        
        find_current_recursive(dasha_periods, 1)
        return current_periods

    def _print_tree_period(self, period: Dict, max_levels: int, cutoff_date: datetime, 
                       prefix: str, is_last: bool, is_root: bool = False, 
                       current_periods: Dict = None, current_date: datetime = None, 
                       colors: Dict = None):
        """Print periods in tree format with improved alignment and current period highlighting"""

        if period['start'] > cutoff_date:
            return

        # Determine if this period is current
        is_current = current_date and period['start'] <= current_date <= period['end']

        # Level names
        level_names = ["Mahadasha", "Antardasha", "Pratyantardasha", "Sookshma", "Prana"]
        level_name = level_names[period['level'] - 1] if period['level'] <= 5 else f"Level{period['level']}"

        # Duration formatting
        if period['duration_years'] >= 1:
            duration_str = f"{period['duration_years']:.1f}y"
        elif period['duration_years'] >= 1 / 12:
            duration_str = f"{period['duration_years'] * 12:.1f}m"
        else:
            duration_str = f"{period['duration_years'] * 365:.0f}d"

        # Tree connector symbols
        connector = "└─ " if is_last else "├─ "
        branch_prefix = "   " if is_last else "│  "

        # Get color
        color_map = {1: 'main', 2: 'antar', 3: 'pratyantar', 4: 'sookshma', 5: 'prana'}
        level_key = color_map.get(period['level'], 'dim')

        color = colors[level_key] if is_current else colors['dim']
        reset = colors['reset']

        # Format name and date block
        name = f"{period['planet']} {level_name}".ljust(26)
        date_range = f"[{period['start'].strftime('%Y-%m-%d')} to {period['end'].strftime('%Y-%m-%d')}]"
        duration_block = f"({duration_str})"
        current_marker = " ◄ CURRENT" if is_current else ""

        # Print the tree line
        print(f"{prefix}{color}{connector}{name} {date_range} {duration_block}{current_marker}{reset}")

        # Print sub-periods recursively
        if period['level'] < max_levels and period['sub_periods']:
            new_prefix = prefix + branch_prefix
            valid_sub_periods = [sp for sp in period['sub_periods'] if sp['start'] <= cutoff_date]

            for j, sub_period in enumerate(valid_sub_periods):
                is_last_sub = (j == len(valid_sub_periods) - 1)
                self._print_tree_period(
                    sub_period, max_levels, cutoff_date,
                    new_prefix, is_last_sub, False,
                    current_periods, current_date, colors
                )


# Example usage
if __name__ == "__main__":
    # Example with the provided data
    moon_data = {
        'Name': 'Gemini', 
        'DegreesIn': {
            'DegreeMinuteSecond': "16° 22' 27", 
            'TotalDegrees': '16.374166666666667'
        }
    }
    birth_date = "1996-11-28"
    
    dasha_calc = VimshottariDasha(moon_data, birth_date)
    
    # Print dasha tree up to level 3 for next 15 years
    dasha_calc.print_dasha(levels=3, years_ahead=30)