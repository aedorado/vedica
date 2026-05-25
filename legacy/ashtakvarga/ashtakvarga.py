import pandas as pd

input_data = """
Asc: 10
1H - 
2H - SA
3H - 
4H - JU
5H - RA
6H - 
7H -
8H - MA
9H - MO
10H - 
11H - ME VE KE
12H - SU
"""

# input_data = """
# Asc: 3
# 1H -
# 2H -
# 3H -
# 4H -
# 5H - JU
# 6H - RA
# 7H -
# 8H -
# 9H - SA MA ME
# 10H - VE SU
# 11H - MO
# 12H - KE
# """

SUN_RULES = {
    'ME': [3, 5, 6, 9, 10, 11, 12],
    'MA': [1, 2, 4, 7, 8, 9, 10, 11],
    'MO': [3, 6, 10, 11],
    'SU': [1, 2, 4, 7, 8, 9, 10, 11],
    'JU': [5, 6, 9, 11],
    'VE': [6, 7, 12],
    'SA': [1, 2, 4, 7, 8, 9, 10, 11],
    'AS': [3, 4, 6, 10, 11, 12]
}

MOON_RULES = {
    'SU': [3, 6, 7, 8, 10, 11],
    'MO': [1, 3, 6, 7, 10, 11],
    'MA': [2, 3, 5, 6, 9, 10, 11],
    'ME': [1, 3, 4, 5, 7, 8, 10, 11],
    'JU': [1, 4, 7, 8, 10, 11, 12],
    'VE': [3, 4, 5, 7, 9, 10, 11],
    'SA': [3, 5, 6, 11],
    'AS': [3, 6, 10, 11],
}

MARS_RULES = {
    'SU': [3, 5, 6, 10, 11],
    'MO': [3, 6, 11],
    'MA': [1, 2, 4, 7, 8, 10, 11],
    'ME': [3, 5, 6, 11],
    'JU': [6, 10, 11, 12],
    'VE': [6, 8, 11, 12],
    'SA': [1, 4, 7, 8, 9, 10, 11],
    'AS': [1, 3, 6, 10, 11],
}

MERCURY_RULES = {
    'SU': [5, 6, 9, 11, 12],
    'MO': [2, 4, 6, 8, 10, 11],
    'MA': [1, 2, 4, 7, 8, 9, 10, 11],
    'ME': [1, 3, 5, 6, 9, 10, 11, 12],
    'JU': [6, 8, 11, 12],
    'VE': [1, 2, 3, 4, 5, 8, 9, 11],
    'SA': [1, 2, 4, 7, 8, 9, 10, 11],
    'AS': [1, 2, 4, 6, 8, 10, 11],
}

JUPITER_RULES = {
    'SU': [1, 2, 3, 4, 7, 8, 9, 10, 11],
    'MO': [2, 5, 7, 9, 11],
    'MA': [1, 2, 4, 7, 8, 10, 11],
    'ME': [1, 2, 4, 5, 6, 9, 10, 11],
    'JU': [1, 2, 3, 4, 7, 8, 10, 11],
    'VE': [2, 5, 6, 9, 10, 11],
    'SA': [3, 5, 6, 12],
    'AS': [1, 2, 4, 5, 6, 7, 9, 10, 11],
}

VENUS_RULES = {
    'SU': [8, 11, 12],
    'MO': [1, 2, 3, 4, 5, 8, 9, 11, 12],
    'MA': [3, 4, 6, 9, 11, 12],
    'ME': [3, 5, 6, 9, 11],
    'JU': [5, 8, 9, 10, 11],
    'VE': [1, 2, 3, 4, 5, 8, 9, 10, 11],
    'SA': [3, 4, 5, 8, 9, 10, 11],
    'AS': [1, 2, 3, 4, 5, 8, 9, 11],
}

SATURN_RULES = {
    'SU': [1, 2, 4, 7, 8, 10, 11],
    'MO': [3, 6, 11],
    'MA': [3, 5, 6, 10, 11, 12],
    'ME': [6, 8, 9, 10, 11, 12],
    'JU': [5, 6, 11, 12],
    'VE': [6, 11, 12],
    'SA': [3, 5, 6, 11],
    'AS': [1, 3, 4, 6, 10, 11],
}

SARVASHTAKVARGA_CONTRIBUTIONS = {
    'SU': [3, 3, 3, 3, 2, 3, 4, 5, 3, 5, 7, 2],
    'MO': [2, 3, 5, 2, 2, 5, 2, 2, 2, 3, 7, 1],
    'MA': [4, 5, 3, 4, 3, 3, 4, 4, 4, 6, 7, 2],
    'ME': [3, 1, 5, 2, 6, 6, 1, 2, 5, 5, 7, 3],
    'JU': [2, 1, 1, 2, 3, 4, 2, 4, 2, 4, 7, 4],
    'VE': [2, 3, 3, 3, 4, 4, 2, 3, 4, 3, 6, 3],
    'SA': [3, 2, 4, 4, 4, 3, 3, 4, 4, 4, 6, 1],
    'AS': [5, 3, 5, 5, 2, 6, 1, 2, 2, 6, 7, 1],
}

class PashtakavargaCalculator:
    def __init__(self, chart_data):
        self.chart_data = chart_data
        self.positions = {}
        self.asc_rashi = None
        self.parse_chart()
        self.prashtakvarga = {}
        self.sarvashtakvarga = None
        
    def parse_chart(self):
        """Parse the input chart and return planet positions in rashis"""
        lines = self.chart_data.strip().split('\n')
        
        for line in lines:
            if 'Asc:' in line:
                self.asc_rashi = int(line.split(':')[1].strip())
            elif 'H' in line:
                house = int(line.split('H')[0].strip())
                planets_str = line.split('-')[1].strip()
                if planets_str:
                    planets = planets_str.split()
                    for planet in planets:
                        if planet not in ['RA', 'KE']:
                            rashi = ((self.asc_rashi - 1 + house - 1) % 12) + 1
                            self.positions[planet] = {'house': house, 'rashi': rashi}
        
        self.positions['AS'] = {'house': 1, 'rashi': self.asc_rashi}
    
    def calculate_rashi_from_position(self, position, offset):
        """Calculate rashi number given a position and offset"""
        return ((position - 1 + offset - 1) % 12) + 1
    
    def calculate_prashtakvarga_for_planet(self, planet_code, rules):
        """Calculate Prashtakvarga for a given planet"""
        contributors = ['SA', 'JU', 'MA', 'SU', 'VE', 'ME', 'MO', 'AS']
        rashis = list(range(1, 13))
        
        bindu_table = pd.DataFrame(0, index=contributors, columns=rashis)
        
        for contributor in contributors:
            if contributor not in self.positions:
                continue
                
            contributor_rashi = self.positions[contributor]['rashi']
            benefic_positions = rules.get(contributor, [])
            
            for offset in benefic_positions:
                rashi = self.calculate_rashi_from_position(contributor_rashi, offset)
                bindu_table.loc[contributor, rashi] = 1
        
        self.prashtakvarga[planet_code] = bindu_table
        return bindu_table
    
    def print_prashtakvarga(self, planet_code, planet_name):
        """Print the Prashtakvarga table (Ashtakavarga)"""
        if planet_code not in self.prashtakvarga:
            print(f"Prashtakvarga not calculated for {planet_name}")
            return

        # Copy table and convert to object dtype for mixed types
        bindu_table = self.prashtakvarga[planet_code].copy().astype(object)

        # Compute row totals
        bindu_table['Total'] = bindu_table.sum(axis=1)

        # Compute column totals and add as the last row
        total_row = bindu_table.sum(axis=0)
        bindu_table.loc['Total'] = total_row

        # Prepare display: 'o' for 1, blank for 0 in planet rows, integers otherwise
        display_table = bindu_table.copy()
        for row in display_table.index:
            for col in display_table.columns:
                val = display_table.at[row, col]
                if row == 'Total':
                    # Keep Total row numeric, show 0 as 0
                    display_table.at[row, col] = int(val)
                else:
                    # Planet rows: 'o' for 1, '' for 0, integer otherwise
                    if val == 1:
                        display_table.at[row, col] = 'o'
                    elif val == 0:
                        display_table.at[row, col] = ''
                    else:
                        display_table.at[row, col] = int(val)

        # Print the table
        print(f"\n{planet_name} Prashtakvarga (Ashtakavarga)")
        print("=" * 80)
        print(display_table.to_string())
        print("=" * 80)

    
    def print_positions(self):
        """Print parsed positions"""
        print("Parsed Positions:")
        for planet, pos in sorted(self.positions.items()):
            print(f"{planet}: House {pos['house']}, Rashi {pos['rashi']}")
    
    def calculate_all_prashtakvarga(self):
        """Calculate Prashtakvarga for all 7 planets"""
        self.calculate_prashtakvarga_for_planet('SU', SUN_RULES)
        self.calculate_prashtakvarga_for_planet('MO', MOON_RULES)
        self.calculate_prashtakvarga_for_planet('MA', MARS_RULES)
        self.calculate_prashtakvarga_for_planet('ME', MERCURY_RULES)
        self.calculate_prashtakvarga_for_planet('JU', JUPITER_RULES)
        self.calculate_prashtakvarga_for_planet('VE', VENUS_RULES)
        self.calculate_prashtakvarga_for_planet('SA', SATURN_RULES)
    
    def calculate_sarvashtakvarga(self):
        """Calculate Sarvashtakvarga using direct method"""
        rashis = list(range(1, 13))
        contributors = ['SU', 'MO', 'MA', 'ME', 'JU', 'VE', 'SA', 'AS']
        
        sarva_table = pd.DataFrame(0, index=contributors, columns=rashis)
        
        for contributor in contributors:
            if contributor not in self.positions:
                continue
            
            contributor_rashi = self.positions[contributor]['rashi']
            contributions = SARVASHTAKVARGA_CONTRIBUTIONS[contributor]
            
            for offset in range(12):
                target_rashi = ((contributor_rashi - 1 + offset) % 12) + 1
                sarva_table.loc[contributor, target_rashi] = contributions[offset]
        
        self.sarvashtakvarga = sarva_table
        return sarva_table
    
    def print_sarvashtakvarga(self):
        """Print the Sarvashtakvarga table"""
        if not hasattr(self, 'sarvashtakvarga'):
            print("Sarvashtakvarga not calculated")
            return
        
        print(f"\nSarvashtakvarga")
        print("=" * 80)
        
        result_table = self.sarvashtakvarga.copy()
        result_table['Total'] = result_table.sum(axis=1)
        
        total_row = result_table.sum(axis=0)
        result_table.loc['Total'] = total_row
        
        print(result_table.to_string())
        print("=" * 80)
    
    def print_all_prashtakvarga(self):
        """Print Prashtakvarga for all 7 planets"""
        planet_names = {
            'SU': 'Sun',
            'MO': 'Moon',
            'MA': 'Mars',
            'ME': 'Mercury',
            'JU': 'Jupiter',
            'VE': 'Venus',
            'SA': 'Saturn'
        }
        
        for code, name in planet_names.items():
            if code in self.prashtakvarga:
                self.print_prashtakvarga(code, name)

calc = PashtakavargaCalculator(input_data)
calc.print_positions()
calc.calculate_all_prashtakvarga()
calc.print_all_prashtakvarga()
calc.calculate_sarvashtakvarga()
calc.print_sarvashtakvarga()