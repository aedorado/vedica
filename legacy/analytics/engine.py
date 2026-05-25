"""
Analytics engine for Vedic Astrology charts.
Generates statistics on Lagna, planet combinations, yogas, strengths, etc.
"""

import sys
import os
import json
from collections import defaultdict
from itertools import combinations
from typing import Dict, List, Tuple

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from db_adapter import DatabaseAdapter
from config import PLANETS, ZODIAC_SIGNS, PLANET_ORDER, PLANET_TO_ABBREVIATION, PLANET_ABBREVIATIONS
from yoga_detector.vedic_yoga_detector import VedicYogaDetector
from yoga_detector.moon_yogas import MoonYogaDetector
from yoga_detector.sun_yoga_detector import SunYogaDetector

# Zodiac sign order: Aries to Pisces
ZODIAC_ORDER = [
    'Aries', 'Taurus', 'Gemini', 'Cancer', 'Leo', 'Virgo',
    'Libra', 'Scorpio', 'Sagittarius', 'Capricorn', 'Aquarius', 'Pisces'
]


class AnalyticsEngine:
    """Generate analytics from chart database"""
    
    def __init__(self, db_path: str = None):
        """Initialize analytics engine"""
        # Use full path if not provided
        if db_path is None:
            parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            db_path = os.path.join(parent_dir, "astro_cache.db")
        
        self.db = DatabaseAdapter(db_path)
        self.charts = self.db.get_all_charts(limit=1000)
        self.stats = {}
    
    def generate_all_stats(self) -> Dict:
        """Generate all analytics statistics"""
        print("📊 Generating analytics...")
        
        self.stats = {
            "total_charts": len(self.charts),
            "lagna": self._analyze_lagna(),
            "combos_2": self._analyze_planet_combos(2),
            "combos_3": self._analyze_planet_combos(3),
            "combos_4": self._analyze_planet_combos(4),
            "combos_5": self._analyze_planet_combos(5),
            "combos_6": self._analyze_planet_combos(6),
            "combustion": self._analyze_combustion(),
            "retrograde": self._analyze_retrograde(),
            "exalted_debilitated": self._analyze_exalted_debilitated(),
            "afflicted": self._analyze_afflicted(),
            "sun_moon_yogas": self._analyze_sun_moon_yogas(),
            "planet_rashi_heatmap": self._analyze_planet_rashi_heatmap(),
            "avastha_matrix": self._analyze_avastha_matrix(),
            "yogas": self._analyze_yogas(),
            "planet_strengths": self._analyze_planet_strengths(),
        }
        
        print("✅ Analytics generated successfully")
        return self.stats
    
    def _analyze_lagna(self) -> Dict:
        """Analyze Lagna (1st house sign) distribution with proper zodiac ordering"""
        lagna_dist = defaultdict(lambda: {"count": 0, "charts": []})
        
        for chart in self.charts:
            if not chart.house_data or "1" not in chart.house_data:
                continue
            
            house_1 = chart.house_data["1"]
            if "HouseRasiSign" not in house_1:
                continue
            
            sign_info = house_1["HouseRasiSign"]
            sign_name = sign_info.get("Name") if isinstance(sign_info, dict) else sign_info
            
            if sign_name:
                lagna_dist[sign_name]["count"] += 1
                lagna_dist[sign_name]["charts"].append(chart.id)
        
        # Return ordered by zodiac sequence
        ordered_lagna = {}
        for sign in ZODIAC_ORDER:
            if sign in lagna_dist:
                ordered_lagna[sign] = dict(lagna_dist[sign])
        
        return ordered_lagna
    
    def _analyze_planet_combos(self, num_planets: int) -> Dict:
        """Analyze N-planet combinations (based on conjunctions in houses - Sign-based)"""
        combos = defaultdict(lambda: {"count": 0, "charts": []})
        
        for chart in self.charts:
            if not chart.planet_data:
                continue
            
            # Group planets by house (Sign-based - traditional Vedic)
            house_planets = defaultdict(list)
            for planet_name, planet_info in chart.planet_data.items():
                house = planet_info.get('HousePlanetOccupiesBasedOnSign')
                if house:
                    house_planets[house].append(planet_name)
            
            # Extract all N-planet combinations from conjunctions
            seen_combos = set()  # Avoid duplicates from same chart
            for house, planets in house_planets.items():
                if len(planets) >= num_planets:
                    # Sort planets using fixed PLANET_ORDER for consistent display
                    ordered_planets = sorted(planets, key=lambda p: PLANET_ORDER.index(p) if p in PLANET_ORDER else 999)
                    # Get all N-planet combinations from this house
                    for combo in combinations(ordered_planets, num_planets):
                        # Use abbreviations for compact display (Su+Mo instead of Sun+Moon)
                        abbr_combo = "+".join(PLANET_TO_ABBREVIATION.get(p, p[:2]) for p in combo)
                        if abbr_combo not in seen_combos:
                            combos[abbr_combo]["count"] += 1
                            combos[abbr_combo]["charts"].append(chart.id)
                            seen_combos.add(abbr_combo)
        
        # Sort by count descending, then by planet order
        def combo_sort_key(item):
            combo_str = item[0]
            count = item[1]["count"]
            # Parse the combo back to get first planet for ordering
            first_planet_abbr = combo_str.split("+")[0]
            first_planet_idx = next((PLANET_ORDER.index(PLANET_ABBREVIATIONS.get(abbr, abbr)) for abbr in [first_planet_abbr] if abbr in PLANET_ABBREVIATIONS), 999)
            return (-count, first_planet_idx)  # Sort by count desc, then by planet order
        
        return dict(sorted(combos.items(), key=combo_sort_key))
    
    def _analyze_planet_rashi_heatmap(self) -> Dict:
        """Create planet × rashi matrix"""
        heatmap = {}
        
        # Initialize matrix: planet → sign → count
        for planet in PLANETS:
            heatmap[planet] = {}
            for sign in ZODIAC_SIGNS:
                heatmap[planet][sign] = 0
        
        # Fill matrix with actual data
        for chart in self.charts:
            if not chart.planet_data:
                continue
            
            for planet_name, planet_info in chart.planet_data.items():
                if planet_name not in PLANETS:
                    continue
                
                # Get planet's sign
                for field in ['PlanetRasiD1Sign', 'RasiSign']:
                    if field in planet_info:
                        sign_info = planet_info[field]
                        sign_name = sign_info.get("Name") if isinstance(sign_info, dict) else sign_info
                        
                        if sign_name and sign_name in ZODIAC_SIGNS:
                            heatmap[planet_name][sign_name] += 1
                        break
        
        return heatmap
    
    def _analyze_avastha_matrix(self) -> Dict:
        """Create planet × avastha matrix"""
        # Define all possible avastas
        avastas = {'Garvita', 'Kshobhita', 'Kshudita', 'Lajjita', 'Mudita', 'Trashita'}
        
        # Initialize matrix: planet → avastha → count
        matrix = {}
        for planet in PLANETS:
            matrix[planet] = {avasta: 0 for avasta in avastas}
        
        # Fill matrix with actual data
        for chart in self.charts:
            if not chart.planet_data:
                continue
            
            for planet_name, planet_info in chart.planet_data.items():
                if planet_name not in PLANETS:
                    continue
                
                # Get planet's avastas
                avasta_str = planet_info.get("PlanetAvasta", "")
                if not avasta_str:
                    continue
                
                # Parse avastas (can be comma-separated, e.g. "KshuditaStarved, MuditaDelighted")
                # Extract the actual avasta name (before the space/descriptor)
                avastas_found = set()
                for token in avasta_str.split(','):
                    token = token.strip()
                    if not token:
                        continue
                    
                    # Extract avasta name: "KshuditaStarved" → "Kshudita"
                    for avasta in avastas:
                        if token.startswith(avasta):
                            avastas_found.add(avasta)
                            break
                
                # Increment count for each found avasta
                for avasta in avastas_found:
                    if avasta in matrix[planet_name]:
                        matrix[planet_name][avasta] += 1
        
        return matrix
    
    def _analyze_combustion(self) -> Dict:
        """Analyze planet combustion (Asta) - planets too close to Sun"""
        combustion_counts = defaultdict(lambda: {"count": 0, "charts": []})
        
        for chart in self.charts:
            if not chart.planet_data:
                continue
            
            for planet_name, planet_info in chart.planet_data.items():
                # Skip Sun and shadow planets (they don't get combust)
                if planet_name in ['Sun', 'Ketu']:
                    continue
                
                # Check if planet is combusted
                is_combust = planet_info.get('IsPlanetCombust')
                
                # Handle True/False strings or actual booleans
                if isinstance(is_combust, str):
                    is_combust = is_combust.lower() == 'true'
                
                if is_combust:
                    combustion_counts[planet_name]["count"] += 1
                    combustion_counts[planet_name]["charts"].append(chart.id)
        
        # Sort by count descending
        return dict(sorted(combustion_counts.items(), key=lambda x: x[1]["count"], reverse=True))
    
    def _analyze_retrograde(self) -> Dict:
        """Analyze retrograde planets - planets moving backwards in zodiac"""
        retrograde_counts = defaultdict(lambda: {"count": 0, "charts": []})
        
        for chart in self.charts:
            if not chart.planet_data:
                continue
            
            for planet_name, planet_info in chart.planet_data.items():
                # Check if planet is retrograde
                is_retrograde = planet_info.get('IsPlanetRetrograde')
                
                # Handle True/False strings or actual booleans
                if isinstance(is_retrograde, str):
                    is_retrograde = is_retrograde.lower() == 'true'
                
                if is_retrograde:
                    retrograde_counts[planet_name]["count"] += 1
                    retrograde_counts[planet_name]["charts"].append(chart.id)
        
        # Sort by count descending
        return dict(sorted(retrograde_counts.items(), key=lambda x: x[1]["count"], reverse=True))
    
    def _analyze_exalted_debilitated(self) -> Dict:
        """Analyze exalted and debilitated planets - strongest vs weakest positions"""
        exalted = defaultdict(lambda: {"count": 0, "charts": []})
        debilitated = defaultdict(lambda: {"count": 0, "charts": []})
        
        for chart in self.charts:
            if not chart.planet_data:
                continue
            
            for planet_name, planet_info in chart.planet_data.items():
                # Check if planet is exalted
                is_exalted = planet_info.get('IsPlanetExaltedSign')
                if isinstance(is_exalted, str):
                    is_exalted = is_exalted.lower() == 'true'
                
                if is_exalted:
                    exalted[planet_name]["count"] += 1
                    exalted[planet_name]["charts"].append(chart.id)
                
                # Check if planet is debilitated
                is_debilitated = planet_info.get('IsPlanetDebilitated')
                if isinstance(is_debilitated, str):
                    is_debilitated = is_debilitated.lower() == 'true'
                
                if is_debilitated:
                    debilitated[planet_name]["count"] += 1
                    debilitated[planet_name]["charts"].append(chart.id)
        
        return {
            "exalted": dict(sorted(exalted.items(), key=lambda x: x[1]["count"], reverse=True)),
            "debilitated": dict(sorted(debilitated.items(), key=lambda x: x[1]["count"], reverse=True))
        }
    
    def _analyze_afflicted(self) -> Dict:
        """Analyze afflicted planets - weak or challenged positions"""
        afflicted = defaultdict(lambda: {"count": 0, "charts": []})
        
        for chart in self.charts:
            if not chart.planet_data:
                continue
            
            for planet_name, planet_info in chart.planet_data.items():
                # Check if planet is afflicted
                is_afflicted = planet_info.get('IsPlanetAfflicted')
                if isinstance(is_afflicted, str):
                    is_afflicted = is_afflicted.lower() == 'true'
                
                if is_afflicted:
                    afflicted[planet_name]["count"] += 1
                    afflicted[planet_name]["charts"].append(chart.id)
        
        return dict(sorted(afflicted.items(), key=lambda x: x[1]["count"], reverse=True))
    
    def _analyze_sun_moon_yogas(self) -> Dict:
        """Analyze Sun and Moon yogas across all charts"""
        sun_yogas = defaultdict(int)
        moon_yogas = defaultdict(int)
        yoga_charts = defaultdict(list)  # Track which charts have each yoga
        
        for chart in self.charts:
            try:
                # Detect Moon yogas
                moon_detector = MoonYogaDetector(chart.planet_data, chart.house_data)
                moon_yogas_detected = moon_detector.detect_all_yogas()
                
                if moon_yogas_detected:
                    for yoga_obj in moon_yogas_detected:
                        if yoga_obj:
                            yoga_type = yoga_obj.yoga_type.value
                            moon_yogas[yoga_type] += 1
                            yoga_charts[f"Moon_{yoga_type}"].append(chart.id)
                
                # Detect Sun yogas
                sun_detector = SunYogaDetector(chart.planet_data, chart.house_data)
                sun_yogas_detected = sun_detector.detect_all_yogas()
                
                if sun_yogas_detected:
                    for yoga_obj in sun_yogas_detected:
                        if yoga_obj:
                            yoga_type = yoga_obj.yoga_type.value
                            sun_yogas[yoga_type] += 1
                            yoga_charts[f"Sun_{yoga_type}"].append(chart.id)
            except Exception as e:
                # Log but continue if a detector fails
                continue
        
        return {
            "sun_yogas": dict(sorted(sun_yogas.items(), key=lambda x: x[1], reverse=True)),
            "moon_yogas": dict(sorted(moon_yogas.items(), key=lambda x: x[1], reverse=True)),
            "yoga_charts": dict(yoga_charts)
        }
    
    def _analyze_yogas(self) -> Dict:
        """Detect yogas in all charts"""
        yoga_counts = defaultdict(int)
        
        for chart in self.charts:
            try:
                detector = VedicYogaDetector(chart.planet_data, chart.house_data)
                yogas = detector.detect_all_yogas()
                
                if yogas:
                    for yoga_type, details in yogas.items():
                        if details.get("found"):
                            yoga_counts[yoga_type] += 1
            except Exception as e:
                continue
        
        return dict(yoga_counts)
    
    def _analyze_planet_strengths(self) -> Dict:
        """Analyze planetary strengths"""
        strength_dist = {
            "strong": defaultdict(int),
            "moderate": defaultdict(int),
            "weak": defaultdict(int),
        }
        
        for chart in self.charts:
            if not chart.planet_data:
                continue
            
            for planet_name, planet_info in chart.planet_data.items():
                if planet_name not in PLANETS:
                    continue
                
                # Get strength category
                is_strong = planet_info.get("IsPlanetStrongInShadbala") == "True"
                is_weak = planet_info.get("IsPlanetDebilitated") == "True"
                
                if is_strong:
                    strength_dist["strong"][planet_name] += 1
                elif is_weak:
                    strength_dist["weak"][planet_name] += 1
                else:
                    strength_dist["moderate"][planet_name] += 1
        
        return {
            "strong": dict(strength_dist["strong"]),
            "moderate": dict(strength_dist["moderate"]),
            "weak": dict(strength_dist["weak"]),
        }
    
    def save_cache(self, filepath: str = None):
        """Save stats to JSON cache"""
        if filepath is None:
            filepath = os.path.join(os.path.dirname(__file__), "cache.json")
        
        with open(filepath, "w") as f:
            json.dump(self.stats, f, indent=2)
        print(f"💾 Cache saved to {filepath}")
    
    def load_cache(self, filepath: str = None) -> Dict:
        """Load stats from cache"""
        if filepath is None:
            filepath = os.path.join(os.path.dirname(__file__), "cache.json")
        
        try:
            with open(filepath, "r") as f:
                self.stats = json.load(f)
            print(f"📂 Cache loaded from {filepath}")
            return self.stats
        except FileNotFoundError:
            print(f"⚠️  Cache file not found: {filepath}")
            return {}


if __name__ == "__main__":
    engine = AnalyticsEngine()
    stats = engine.generate_all_stats()
    engine.save_cache()
    
    # Print summary
    print("\n📊 ANALYTICS SUMMARY")
    print(f"Total Charts: {stats['total_charts']}")
    print(f"Lagna Signs: {len(stats['lagna'])}")
    print(f"2-Planet Combos: {len(stats['combos_2'])}")
    print(f"3-Planet Combos: {len(stats['combos_3'])}")
    print(f"4-Planet Combos: {len(stats['combos_4'])}")
    print(f"Yogas Detected: {len(stats['yogas'])}")
