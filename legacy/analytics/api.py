"""
Flask API for analytics dashboard.
Serves JSON data for frontend visualization.
"""

import sys
import os
import json
from flask import Flask, render_template, jsonify, request, Response

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from engine import AnalyticsEngine
from db_adapter import DatabaseAdapter
from dasha.vimshottari import VimshottariDasha
from parsers.planet_data_parser import PlanetDataParser
from parsers.house_data_parser import HouseDataParser
from yoga_detector.moon_yogas import MoonYogaDetector
from yoga_data import get_yoga_info
from yoga_detector.sun_yoga_detector import SunYogaDetector
from yoga_detector.raja_yoga_detector import SimpleRajaYogaDetector
from yoga_detector.dhan_yoga_detector import SimpleDhanaYogaDetector
from yoga_detector.pancha_mahapurusha import PanchMahapurushYogaDetector
from yoga_detector.parivartan_yoga_detector import ParivartanaYogaDetector
from yoga_detector.nabhasa_yoga_detector import NabhasaYogaDetector
from yoga_detector.malika_yogas_detector import MallikaYogaDetector
from yoga_detector.neech_bhanga_raja_yoga import NeechBhangaYogaDetector
from yoga_detector.vipreet_raja_yoga import SimplifiedVipareetRajaDetector

app = Flask(__name__, template_folder="templates", static_folder="static")
engine = AnalyticsEngine()
# Use absolute path to database
db_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "astro_cache.db")
db = DatabaseAdapter(db_path)

# Global cache
STATS_CACHE = {}


@app.before_request
def load_cache():
    """Load cache on first request"""
    global STATS_CACHE
    # Use absolute path
    cache_file = os.path.join(os.path.dirname(__file__), "cache.json")
    
    if not STATS_CACHE and os.path.exists(cache_file):
        STATS_CACHE = engine.load_cache(cache_file)
    elif not STATS_CACHE:
        STATS_CACHE = engine.generate_all_stats()
        engine.save_cache(cache_file)


@app.route("/")
def dashboard():
    """Serve main dashboard"""
    return render_template("dashboard.html")


@app.route("/yoga-browser")
def yoga_browser():
    """Serve yoga browser page"""
    return render_template("yoga_browser.html")


@app.route("/chart/<int:chart_id>")
def chart_detail(chart_id):
    """Display individual chart in North Indian format"""
    chart = db.get_chart_by_id(chart_id)
    if not chart:
        return "Chart not found", 404
    
    name, birth_time, location = parse_raw_input(chart.raw_input)
    
    return render_template("chart_detail.html", 
                          chart_id=chart_id,
                          name=name,
                          birth_time=birth_time,
                          location=location,
                          planet_data=chart.planet_data,
                          house_data=chart.house_data)


def _format_duration(duration_years, level):
    """Format duration based on dasha level"""
    if level == 1:  # Mahadasha: years
        return f"{duration_years:.2f} Y"
    
    elif level == 2:  # Antardasha: Y, M, D
        years = int(duration_years)
        months_decimal = (duration_years - years) * 12
        months = int(months_decimal)
        days_decimal = (months_decimal - months) * 30
        days = int(days_decimal)
        return f"{years}Y {months}M {days}D"
    
    elif level == 3:  # Pratyantar: Days
        days = int(duration_years * 365.25)
        return f"{days} days"
    
    elif level == 4:  # Sookshma: Days
        days = int(duration_years * 365.25)
        return f"{days} days"
    
    else:  # Prana: Days/Hours
        total_hours = duration_years * 365.25 * 24
        days = int(total_hours // 24)
        hours = int(total_hours % 24)
        if days > 0:
            return f"{days}d {hours}h"
        else:
            return f"{hours} hours"


def _convert_dasha_to_json(dasha_entry, current_date=None):
    """Convert dasha entry with datetime objects to JSON-serializable format"""
    from datetime import datetime as dt
    
    if current_date is None:
        current_date = dt.now()
    
    # Determine if this dasha is current
    is_current = False
    days_remaining = 0
    
    start = dasha_entry.get('start')
    end = dasha_entry.get('end')
    
    if start and end:
        is_current = start <= current_date <= end
        if is_current:
            days_remaining = max(0, int((end - current_date).total_seconds() / 86400))
    
    level = dasha_entry.get('level', 1)
    duration_years = dasha_entry.get('duration_years', 0)
    
    result = {
        'planet': dasha_entry.get('planet', 'Unknown'),
        'level': level,
        'duration_years': round(duration_years, 4),
        'duration_formatted': _format_duration(duration_years, level),
        'start_date': start.strftime("%d/%m/%Y") if start else "N/A",
        'end_date': end.strftime("%d/%m/%Y") if end else "N/A",
        'is_current': is_current,
        'days_remaining': days_remaining,
        'sub_periods': []
    }
    
    # Recursively convert sub-periods
    if dasha_entry.get('sub_periods'):
        for sub in dasha_entry['sub_periods']:
            result['sub_periods'].append(_convert_dasha_to_json(sub, current_date))
    
    return result


def _detect_chart_yogas(planet_data_raw, house_data_raw):
    """Detect all yogas for a chart using yoga detectors"""
    yogas = {
        'moon_yogas': [],
        'sun_yogas': [],
        'raja_yogas': [],
        'dhana_yogas': [],
        'pancha_mahapurusha': [],
        'parivartan_yogas': [],
        'nabhasa_yogas': [],
        'malika_yogas': [],
        'neech_bhanga': [],
        'vipreet_raja': []
    }
    
    try:
        # Parse planet and house data to proper objects
        planet_parser = PlanetDataParser(planet_data_raw if isinstance(planet_data_raw, str) else json.dumps(planet_data_raw))
        house_parser = HouseDataParser(house_data_raw if isinstance(house_data_raw, str) else json.dumps(house_data_raw))
        
        planet_objects = planet_parser.parse()
        house_objects = house_parser.parse()
        
        # Detect Moon Yogas
        try:
            moon_detector = MoonYogaDetector(planet_data_raw if isinstance(planet_data_raw, dict) else json.loads(planet_data_raw),
                                            house_data_raw if isinstance(house_data_raw, dict) else json.loads(house_data_raw))
            moon_yogas = moon_detector.detect_all_yogas()
            for yoga in moon_yogas:
                yogas['moon_yogas'].append({
                    'name': yoga.yoga_type.value,
                    'description': yoga.description,
                    'effect': yoga.effect,
                    'benefic': yoga.is_benefic,
                    'strength': yoga.strength_score
                })
        except Exception as e:
            print(f"Moon yoga detection error: {e}")
        
        # Detect Sun Yogas
        try:
            sun_detector = SunYogaDetector(planet_data_raw if isinstance(planet_data_raw, dict) else json.loads(planet_data_raw),
                                         house_data_raw if isinstance(house_data_raw, dict) else json.loads(house_data_raw))
            sun_yogas = sun_detector.detect_all_yogas()
            for yoga in sun_yogas:
                yogas['sun_yogas'].append({
                    'name': yoga.yoga_type.value,
                    'description': yoga.description,
                    'effect': yoga.effect,
                    'benefic': yoga.is_benefic,
                    'strength': yoga.strength_score
                })
        except Exception as e:
            print(f"Sun yoga detection error: {e}")
        
        # Detect Raja Yogas
        try:
            raja_detector = SimpleRajaYogaDetector(planet_objects, house_objects)
            raja_yogas = raja_detector.detect_all_raja_yogas()
            for yoga in raja_yogas:
                yogas['raja_yogas'].append({
                    'name': yoga.yoga_type.value if hasattr(yoga.yoga_type, 'value') else str(yoga.yoga_type),
                    'description': yoga.description,
                    'benefic': True,
                    'strength': yoga.strength_score
                })
        except Exception as e:
            print(f"Raja yoga detection error: {e}")
        
        # Detect Dhana Yogas
        try:
            dhana_detector = SimpleDhanaYogaDetector(planet_objects, house_objects)
            dhana_yogas = dhana_detector.detect_all_dhana_yogas()
            for yoga in dhana_yogas:
                yogas['dhana_yogas'].append({
                    'name': yoga.yoga_type.value if hasattr(yoga.yoga_type, 'value') else str(yoga.yoga_type),
                    'description': yoga.formation_details or yoga.description,
                    'benefic': True,
                    'strength': 0.65  # Default strength for Dhana yogas
                })
        except Exception as e:
            print(f"Dhana yoga detection error: {e}")
        
        # Detect Pancha Mahapurusha
        try:
            pmp_detector = PanchMahapurushYogaDetector(planet_objects, house_objects)
            pmp_yogas = pmp_detector.detect_panch_mahapurush_yogas()
            for yoga in pmp_yogas:
                yogas['pancha_mahapurusha'].append({
                    'name': yoga.yoga_type.value if hasattr(yoga.yoga_type, 'value') else str(yoga.yoga_type),
                    'description': yoga.description,
                    'benefic': True,
                    'strength': yoga.strength_score
                })
        except Exception as e:
            print(f"Pancha Mahapurusha detection error: {e}")
        
        # Detect Parivartan Yogas
        try:
            parivartan_detector = ParivartanaYogaDetector(planet_objects, house_objects)
            parivartan_yogas = parivartan_detector.detect_all_parivartana_yogas()
            for yoga in parivartan_yogas:
                yogas['parivartan_yogas'].append({
                    'name': yoga.yoga_type.value if hasattr(yoga.yoga_type, 'value') else str(yoga.yoga_type),
                    'description': yoga.description,
                    'benefic': True,
                    'strength': yoga.strength_score
                })
        except Exception as e:
            print(f"Parivartan yoga detection error: {e}")
        
        # Detect Nabhasa Yogas
        try:
            nabhasa_detector = NabhasaYogaDetector(planet_objects, house_objects)
            nabhasa_yogas = nabhasa_detector.detect_all_yogas()
            for yoga in nabhasa_yogas:
                yogas['nabhasa_yogas'].append({
                    'name': yoga.yoga_type.value if hasattr(yoga.yoga_type, 'value') else str(yoga.yoga_type),
                    'description': yoga.description,
                    'strength': yoga.strength_score
                })
        except Exception as e:
            print(f"Nabhasa yoga detection error: {e}")
        
        # Detect Malika Yogas
        try:
            malika_detector = MallikaYogaDetector(planet_objects, house_objects)
            malika_yogas = malika_detector.detect_all_mallika_yogas()
            for yoga in malika_yogas:
                yogas['malika_yogas'].append({
                    'name': yoga.yoga_type.value if hasattr(yoga.yoga_type, 'value') else str(yoga.yoga_type),
                    'description': yoga.description,
                    'strength': yoga.strength_score
                })
        except Exception as e:
            print(f"Malika yoga detection error: {e}")
        
        # Detect Neech Bhanga
        try:
            nb_detector = NeechBhangaYogaDetector(planet_objects, house_objects)
            nb_yogas = nb_detector.detect_all_neecha_bhanga_yogas()
            for yoga in nb_yogas:
                yogas['neech_bhanga'].append({
                    'name': yoga.yoga_type.value if hasattr(yoga.yoga_type, 'value') else str(yoga.yoga_type),
                    'description': yoga.description,
                    'strength': yoga.strength_score
                })
        except Exception as e:
            print(f"Neech bhanga detection error: {e}")
        
        # Detect Vipreet Raja Yogas
        try:
            vr_detector = SimplifiedVipareetRajaDetector(planet_objects, house_objects)
            vr_yogas = vr_detector.detect_all_vipareet_raja_yogas()
            for yoga in vr_yogas:
                # Map strength string to numeric value
                strength_map = {'Weak': 0.3, 'Moderate': 0.65, 'Strong': 0.9}
                strength_val = strength_map.get(yoga.yoga_strength, 0.65)
                
                yogas['vipreet_raja'].append({
                    'name': yoga.vipareet_type.value if hasattr(yoga.vipareet_type, 'value') else str(yoga.vipareet_type),
                    'description': yoga.description,
                    'strength': strength_val
                })
        except Exception as e:
            print(f"Vipreet raja yoga detection error: {e}")
    
    except Exception as e:
        print(f"Error in yoga detection: {e}")
        import traceback
        traceback.print_exc()
    
    return yogas


@app.route("/api/chart/<int:chart_id>")
def api_chart_detail(chart_id):
    """Get detailed chart data for API"""
    chart = db.get_chart_by_id(chart_id)
    if not chart:
        return jsonify({"error": "Chart not found"}), 404
    
    name, birth_time, location = parse_raw_input(chart.raw_input)
    
    # Calculate Vimshottari Dasha
    dasha_periods = []
    try:
        from datetime import datetime as dt
        
        # Extract birth date from birth_time (format: "HH:MM DD/MM/YYYY +HH:MM")
        parts = birth_time.split()
        date_str = parts[1]  # "DD/MM/YYYY"
        day, month, year = date_str.split('/')
        birth_date_str = f"{year}-{month}-{day}"
        
        # Extract moon data
        moon_data = chart.planet_data.get('Moon', {})
        moon_rashi = moon_data.get('PlanetRasiD1Sign', {})
        
        if moon_rashi and 'DegreesIn' in moon_rashi:
            # Initialize VimshottariDasha
            vimshottari = VimshottariDasha(moon_rashi, birth_date_str)
            
            # Get all 5 levels of dasha
            dashas = vimshottari.calculate_dasha(levels=5)
            
            # Convert to JSON and limit to 10 main dashas
            for dasha in dashas[:10]:
                dasha_periods.append(_convert_dasha_to_json(dasha, dt.now()))
    except Exception as e:
        # Log error but don't fail the API call
        print(f"Dasha calculation error: {e}")
        import traceback
        traceback.print_exc()
        dasha_periods = []
    
    # Detect Yogas
    yogas = _detect_chart_yogas(chart.planet_data, chart.house_data)
    
    return jsonify({
        "id": chart_id,
        "name": name,
        "birth_time": birth_time,
        "location": location,
        "planet_data": chart.planet_data,
        "house_data": chart.house_data,
        "dasha_periods": dasha_periods,
        "yogas": yogas
    })


@app.route("/api/stats/summary")
def api_summary():
    """Get summary statistics"""
    return jsonify({
        "total_charts": STATS_CACHE.get("total_charts", 0),
        "lagna_count": len(STATS_CACHE.get("lagna", {})),
        "combos_2_count": len(STATS_CACHE.get("combos_2", {})),
        "combos_3_count": len(STATS_CACHE.get("combos_3", {})),
        "combos_4_count": len(STATS_CACHE.get("combos_4", {})),
        "combos_5_count": len(STATS_CACHE.get("combos_5", {})),
        "combos_6_count": len(STATS_CACHE.get("combos_6", {})),
        "combustion_count": len(STATS_CACHE.get("combustion", {})),
        "retrograde_count": len(STATS_CACHE.get("retrograde", {})),
        "exalted_count": len(STATS_CACHE.get("exalted_debilitated", {}).get("exalted", {})),
        "debilitated_count": len(STATS_CACHE.get("exalted_debilitated", {}).get("debilitated", {})),
        "afflicted_count": len(STATS_CACHE.get("afflicted", {})),
        "sun_yogas_count": len(STATS_CACHE.get("sun_moon_yogas", {}).get("sun_yogas", {})),
        "moon_yogas_count": len(STATS_CACHE.get("sun_moon_yogas", {}).get("moon_yogas", {})),
        "yogas_count": len(STATS_CACHE.get("yogas", {})),
    })


@app.route("/api/lagna")
def api_lagna():
    """Get Lagna distribution"""
    lagna_data = STATS_CACHE.get("lagna", {})
    
    # Format for chart
    return jsonify({
        "type": "lagna",
        "data": lagna_data,
        "total": len(lagna_data)
    })


@app.route("/api/combos/<int:num_planets>")
def api_combos(num_planets):
    """Get N-planet combinations"""
    key = f"combos_{num_planets}"
    combos = STATS_CACHE.get(key, {})
    
    # Return top 20
    top_combos = dict(list(combos.items())[:20])
    
    response_data = {
        "type": f"{num_planets}-planet",
        "data": top_combos,
        "total": len(combos),
        "showing": len(top_combos)
    }
    
    # Use sort_keys=False to preserve dict insertion order
    return Response(
        json.dumps(response_data, sort_keys=False),
        mimetype='application/json'
    )


@app.route("/api/planet-rashi-heatmap")
def api_heatmap():
    """Get planet × rashi heatmap"""
    return jsonify(STATS_CACHE.get("planet_rashi_heatmap", {}))


@app.route("/api/avastha-matrix")
def api_avastha_matrix():
    """Get planet × avastha matrix"""
    return jsonify(STATS_CACHE.get("avastha_matrix", {}))


@app.route("/api/yogas")
def api_yogas():
    """Get yoga counts"""
    yogas = STATS_CACHE.get("yogas", {})
    
    # Sort by count
    sorted_yogas = dict(sorted(yogas.items(), key=lambda x: x[1], reverse=True))
    
    return jsonify({
        "type": "yogas",
        "data": sorted_yogas,
        "total": len(yogas)
    })


@app.route("/api/combustion")
def api_combustion():
    """Get planet combustion (Asta) analysis"""
    combustion = STATS_CACHE.get("combustion", {})
    
    return jsonify({
        "type": "combustion",
        "data": combustion,
        "total": len(combustion)
    })


@app.route("/api/retrograde")
def api_retrograde():
    """Get retrograde planets analysis"""
    retrograde = STATS_CACHE.get("retrograde", {})
    
    return jsonify({
        "type": "retrograde",
        "data": retrograde,
        "total": len(retrograde)
    })


@app.route("/api/exalted-debilitated")
def api_exalted_debilitated():
    """Get exalted and debilitated planets analysis"""
    exalted_debilitated = STATS_CACHE.get("exalted_debilitated", {})
    
    return jsonify({
        "type": "exalted_debilitated",
        "exalted": exalted_debilitated.get("exalted", {}),
        "debilitated": exalted_debilitated.get("debilitated", {}),
        "total_exalted": len(exalted_debilitated.get("exalted", {})),
        "total_debilitated": len(exalted_debilitated.get("debilitated", {}))
    })


@app.route("/api/afflicted")
def api_afflicted():
    """Get afflicted planets analysis"""
    afflicted = STATS_CACHE.get("afflicted", {})
    
    return jsonify({
        "type": "afflicted",
        "data": afflicted,
        "total": len(afflicted)
    })


@app.route("/api/sun-moon-yogas")
def api_sun_moon_yogas():
    """Get Sun and Moon yoga analysis"""
    sun_moon = STATS_CACHE.get("sun_moon_yogas", {})
    
    return jsonify({
        "type": "sun_moon_yogas",
        "sun_yogas": sun_moon.get("sun_yogas", {}),
        "moon_yogas": sun_moon.get("moon_yogas", {}),
        "total_sun_yogas": len(sun_moon.get("sun_yogas", {})),
        "total_moon_yogas": len(sun_moon.get("moon_yogas", {}))
    })


@app.route("/api/strengths")
def api_strengths():
    """Get planet strength distribution"""
    return jsonify(STATS_CACHE.get("planet_strengths", {}))


@app.route("/api/charts/by-lagna/<lagna_sign>")
def api_charts_by_lagna(lagna_sign):
    """Get charts with specific Lagna"""
    lagna_data = STATS_CACHE.get("lagna", {})
    
    if lagna_sign not in lagna_data:
        return jsonify({"error": "Lagna not found"}), 404
    
    chart_ids = lagna_data[lagna_sign]["charts"]
    charts_info = []
    
    for chart_id in chart_ids:
        chart = db.get_chart_by_id(chart_id)
        if chart:
            name, birth_time, location = parse_raw_input(chart.raw_input)
            charts_info.append({
                "id": chart.id,
                "name": name,
                "birth_time": birth_time,
                "location": location,
            })
    
    return jsonify({
        "lagna": lagna_sign,
        "count": len(charts_info),
        "charts": charts_info
    })


@app.route("/api/charts/by-combo/<path:combo>")
def api_charts_by_combo(combo):
    """Get charts with specific planet combo"""
    # Determine combo type (2, 3, or 4)
    planet_count = combo.count("+") + 1
    key = f"combos_{planet_count}"
    
    combos_data = STATS_CACHE.get(key, {})
    
    if combo not in combos_data:
        return jsonify({"error": "Combo not found"}), 404
    
    chart_ids = combos_data[combo]["charts"]
    charts_info = []
    
    for chart_id in chart_ids:
        chart = db.get_chart_by_id(chart_id)
        if chart:
            name, birth_time, location = parse_raw_input(chart.raw_input)
            charts_info.append({
                "id": chart.id,
                "name": name,
                "birth_time": birth_time,
                "location": location,
            })
    
    return jsonify({
        "combo": combo,
        "planets": planet_count,
        "count": len(charts_info),
        "charts": charts_info
    })


@app.route("/api/charts/by-combustion/<planet>")
def api_charts_by_combustion(planet):
    """Get charts with combustion of specific planet"""
    combustion_data = STATS_CACHE.get("combustion", {})
    
    if planet not in combustion_data:
        return jsonify({"error": "Combustion data not found"}), 404
    
    chart_ids = combustion_data[planet]["charts"]
    charts_info = []
    
    for chart_id in chart_ids:
        chart = db.get_chart_by_id(chart_id)
        if chart:
            name, birth_time, location = parse_raw_input(chart.raw_input)
            charts_info.append({
                "id": chart.id,
                "name": name,
                "birth_time": birth_time,
                "location": location,
            })
    
    return jsonify({
        "planet": planet,
        "combustion_type": "asta",
        "count": len(charts_info),
        "charts": charts_info
    })


@app.route("/api/charts/by-retrograde/<planet>")
def api_charts_by_retrograde(planet):
    """Get charts with retrograde planet"""
    retrograde_data = STATS_CACHE.get("retrograde", {})
    
    if planet not in retrograde_data:
        return jsonify({"error": "Retrograde data not found"}), 404
    
    chart_ids = retrograde_data[planet]["charts"]
    charts_info = []
    
    for chart_id in chart_ids:
        chart = db.get_chart_by_id(chart_id)
        if chart:
            name, birth_time, location = parse_raw_input(chart.raw_input)
            charts_info.append({
                "id": chart.id,
                "name": name,
                "birth_time": birth_time,
                "location": location,
            })
    
    return jsonify({
        "planet": planet,
        "retrograde_type": "vakra",
        "count": len(charts_info),
        "charts": charts_info
    })


@app.route("/api/charts/by-exalted/<planet>")
def api_charts_by_exalted(planet):
    """Get charts with exalted planet"""
    exalted_debilitated = STATS_CACHE.get("exalted_debilitated", {})
    exalted_data = exalted_debilitated.get("exalted", {})
    
    if planet not in exalted_data:
        return jsonify({"error": "Exalted data not found"}), 404
    
    chart_ids = exalted_data[planet]["charts"]
    charts_info = []
    
    for chart_id in chart_ids:
        chart = db.get_chart_by_id(chart_id)
        if chart:
            name, birth_time, location = parse_raw_input(chart.raw_input)
            charts_info.append({
                "id": chart.id,
                "name": name,
                "birth_time": birth_time,
                "location": location,
            })
    
    return jsonify({
        "planet": planet,
        "dignity_type": "exalted",
        "count": len(charts_info),
        "charts": charts_info
    })


@app.route("/api/charts/by-debilitated/<planet>")
def api_charts_by_debilitated(planet):
    """Get charts with debilitated planet"""
    exalted_debilitated = STATS_CACHE.get("exalted_debilitated", {})
    debilitated_data = exalted_debilitated.get("debilitated", {})
    
    if planet not in debilitated_data:
        return jsonify({"error": "Debilitated data not found"}), 404
    
    chart_ids = debilitated_data[planet]["charts"]
    charts_info = []
    
    for chart_id in chart_ids:
        chart = db.get_chart_by_id(chart_id)
        if chart:
            name, birth_time, location = parse_raw_input(chart.raw_input)
            charts_info.append({
                "id": chart.id,
                "name": name,
                "birth_time": birth_time,
                "location": location,
            })
    
    return jsonify({
        "planet": planet,
        "dignity_type": "debilitated",
        "count": len(charts_info),
        "charts": charts_info
    })


@app.route("/api/charts/by-afflicted/<planet>")
def api_charts_by_afflicted(planet):
    """Get charts with afflicted planet"""
    afflicted_data = STATS_CACHE.get("afflicted", {})
    
    if planet not in afflicted_data:
        return jsonify({"error": "Afflicted data not found"}), 404
    
    chart_ids = afflicted_data[planet]["charts"]
    charts_info = []
    
    for chart_id in chart_ids:
        chart = db.get_chart_by_id(chart_id)
        if chart:
            name, birth_time, location = parse_raw_input(chart.raw_input)
            charts_info.append({
                "id": chart.id,
                "name": name,
                "birth_time": birth_time,
                "location": location,
            })
    
    return jsonify({
        "planet": planet,
        "affliction_type": "afflicted",
        "count": len(charts_info),
        "charts": charts_info
    })


@app.route("/api/charts/by-sun-yoga/<yoga_name>")
def api_charts_by_sun_yoga(yoga_name):
    """Get charts with specific Sun yoga"""
    sun_moon = STATS_CACHE.get("sun_moon_yogas", {})
    yoga_charts = sun_moon.get("yoga_charts", {})
    
    key = f"Sun_{yoga_name}"
    if key not in yoga_charts:
        return jsonify({"error": "Sun yoga not found"}), 404
    
    chart_ids = yoga_charts[key]
    charts_info = []
    
    for chart_id in chart_ids:
        chart = db.get_chart_by_id(chart_id)
        if chart:
            name, birth_time, location = parse_raw_input(chart.raw_input)
            charts_info.append({
                "id": chart.id,
                "name": name,
                "birth_time": birth_time,
                "location": location,
            })
    
    return jsonify({
        "yoga": yoga_name,
        "yoga_type": "sun",
        "count": len(charts_info),
        "charts": charts_info
    })


@app.route("/api/charts/by-moon-yoga/<yoga_name>")
def api_charts_by_moon_yoga(yoga_name):
    """Get charts with specific Moon yoga"""
    sun_moon = STATS_CACHE.get("sun_moon_yogas", {})
    yoga_charts = sun_moon.get("yoga_charts", {})
    
    key = f"Moon_{yoga_name}"
    if key not in yoga_charts:
        return jsonify({"error": "Moon yoga not found"}), 404
    
    chart_ids = yoga_charts[key]
    charts_info = []
    
    for chart_id in chart_ids:
        chart = db.get_chart_by_id(chart_id)
        if chart:
            name, birth_time, location = parse_raw_input(chart.raw_input)
            charts_info.append({
                "id": chart.id,
                "name": name,
                "birth_time": birth_time,
                "location": location,
            })
    
    return jsonify({
        "yoga": yoga_name,
        "yoga_type": "moon",
        "count": len(charts_info),
        "charts": charts_info
    })


@app.route("/api/refresh-cache")
def api_refresh_cache():
    """Regenerate cache"""
    global STATS_CACHE
    STATS_CACHE = engine.generate_all_stats()
    engine.save_cache()
    
    return jsonify({"status": "Cache refreshed", "total_charts": STATS_CACHE["total_charts"]})


@app.route("/api/yoga/info/<yoga_name>")
def api_yoga_info(yoga_name):
    """Get yoga formation and effects info"""
    info = get_yoga_info(yoga_name)
    return jsonify(info)


@app.route("/api/yoga/stats")
def api_yoga_stats():
    """Get statistics for all yogas across all charts"""
    all_charts = db.get_all_charts()
    yoga_stats = {}
    chart_yoga_map = {}
    
    for chart in all_charts:
        try:
            yogas = _detect_chart_yogas(chart.planet_data, chart.house_data)
            chart_yoga_map[chart.id] = yogas
            
            # Flatten all yogas and count
            for category, yoga_list in yogas.items():
                for yoga in yoga_list:
                    yoga_name = yoga.get('name', 'Unknown').lower()
                    if yoga_name not in yoga_stats:
                        yoga_stats[yoga_name] = {
                            'count': 0,
                            'charts': [],
                            'category': category,
                            'info': get_yoga_info(yoga.get('name', 'Unknown'))
                        }
                    yoga_stats[yoga_name]['count'] += 1
                    yoga_stats[yoga_name]['charts'].append(chart.id)
        except Exception as e:
            print(f"Error processing chart {chart.id}: {e}")
    
    # Sort by count
    sorted_stats = dict(sorted(yoga_stats.items(), key=lambda x: x[1]['count'], reverse=True))
    
    return jsonify({
        "total_yogas": len(sorted_stats),
        "total_charts": len(all_charts),
        "yogas": sorted_stats
    })


@app.route("/api/yoga/<yoga_name>/charts")
def api_yoga_charts(yoga_name):
    """Get all charts with a specific yoga"""
    all_charts = db.get_all_charts()
    charts_with_yoga = []
    
    yoga_lower = yoga_name.lower()
    
    for chart in all_charts:
        try:
            yogas = _detect_chart_yogas(chart.planet_data, chart.house_data)
            
            # Check all categories for this yoga
            found = False
            for category, yoga_list in yogas.items():
                for yoga in yoga_list:
                    if yoga.get('name', '').lower() == yoga_lower:
                        found = True
                        break
                if found:
                    break
            
            if found:
                name, birth_time, location = parse_raw_input(chart.raw_input)
                charts_with_yoga.append({
                    'id': chart.id,
                    'name': name,
                    'birth_time': birth_time,
                    'location': location
                })
        except Exception as e:
            print(f"Error processing chart {chart.id}: {e}")
    
    return jsonify({
        "yoga": yoga_name,
        "count": len(charts_with_yoga),
        "charts": charts_with_yoga
    })


@app.route("/api/charts/by-planet-rashi/<planet>/<rashi>")
def api_charts_by_planet_rashi(planet, rashi):
    """Get charts with specific planet in specific rashi"""
    all_charts = db.get_all_charts()
    charts_with_placement = []
    
    for chart in all_charts:
        try:
            if not chart.planet_data or not isinstance(chart.planet_data, dict):
                continue
            
            # Look for the planet in planet_data (it's a dict keyed by planet name)
            if planet in chart.planet_data:
                p_info = chart.planet_data[planet]
                # The sign is stored in PlanetRasiD1Sign.Name
                planet_rasi = p_info.get('PlanetRasiD1Sign', {})
                if isinstance(planet_rasi, dict):
                    sign = planet_rasi.get('Name', '')
                else:
                    sign = ''
                
                if sign.lower() == rashi.lower():
                    name, birth_time, location = parse_raw_input(chart.raw_input)
                    degree_info = p_info.get('PlanetRasiD1Sign', {}).get('DegreesIn', {})
                    degree = degree_info.get('TotalDegrees', 'N/A') if isinstance(degree_info, dict) else 'N/A'
                    charts_with_placement.append({
                        'id': chart.id,
                        'name': name,
                        'birth_time': birth_time,
                        'location': location,
                        'degree': degree
                    })
        except Exception as e:
            print(f"Error processing chart {chart.id}: {e}")
    
    return jsonify({
        "planet": planet,
        "rashi": rashi,
        "count": len(charts_with_placement),
        "charts": charts_with_placement
    })


@app.route("/api/charts/by-planet-avasta/<planet>/<avasta>")
def api_charts_by_planet_avasta(planet, avasta):
    """Get charts with specific planet in specific avasta"""
    all_charts = db.get_all_charts()
    charts_with_avasta = []
    
    # Define avastas list for validation
    valid_avastas = {'Garvita', 'Kshobhita', 'Kshudita', 'Lajjita', 'Mudita', 'Trashita'}
    
    for chart in all_charts:
        try:
            if not chart.planet_data or not isinstance(chart.planet_data, dict):
                continue
            
            # Look for the planet in planet_data
            if planet in chart.planet_data:
                p_info = chart.planet_data[planet]
                # Make sure p_info is a dict
                if not isinstance(p_info, dict):
                    continue
                avasta_str = p_info.get('PlanetAvasta', '')
                
                if not avasta_str:
                    continue
                
                # Check if the desired avasta is present in this planet's avastas
                # Parse avastas (can be comma-separated, e.g. "KshuditaStarved, MuditaDelighted")
                avastas_found = set()
                for token in avasta_str.split(','):
                    token = token.strip()
                    if not token:
                        continue
                    
                    # Extract avasta name: "KshuditaStarved" → "Kshudita"
                    for valid_avasta in valid_avastas:
                        if token.startswith(valid_avasta):
                            avastas_found.add(valid_avasta)
                            break
                
                # If the requested avasta is found, add to results
                if avasta in avastas_found:
                    name, birth_time, location = parse_raw_input(chart.raw_input)
                    charts_with_avasta.append({
                        'id': chart.id,
                        'name': name,
                        'birth_time': birth_time,
                        'location': location
                    })
        except Exception as e:
            print(f"Error processing chart {chart.id}: {e}")
    
    return jsonify({
        "planet": planet,
        "avasta": avasta,
        "count": len(charts_with_avasta),
        "charts": charts_with_avasta
    })


def parse_raw_input(raw_input: str) -> tuple:
    """Parse raw_input to extract name, birth_time, location"""
    if not raw_input:
        return ("N/A", "N/A", "N/A")
    
    parts = [p.strip() for p in raw_input.split("|")]
    
    name = parts[0] if len(parts) > 0 else "N/A"
    birth_time = parts[1] if len(parts) > 1 else "N/A"
    location = parts[2] if len(parts) > 2 else "N/A"
    
    return (name, birth_time, location)


if __name__ == "__main__":
    app.run(debug=True, port=5000)
