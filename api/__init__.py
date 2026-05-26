"""
Vedica REST API endpoints
"""
from flask import Blueprint, request, jsonify
from datetime import datetime, timedelta
import logging
import requests
import json
import os

api_bp = Blueprint('api', __name__)

logger = logging.getLogger(__name__)

# Nominatim geocoding API endpoint
NOMINATIM_API = 'https://nominatim.openstreetmap.org/search'

# Simple file-based chart storage
CHARTS_DIR = 'data/charts'
if not os.path.exists(CHARTS_DIR):
    os.makedirs(CHARTS_DIR)


def _save_chart_file(chart_data):
    """Save chart to file with timestamp-based ID."""
    chart_id = datetime.now().strftime('%Y%m%d_%H%M%S_%f')
    filepath = os.path.join(CHARTS_DIR, f'{chart_id}.json')
    
    with open(filepath, 'w') as f:
        json.dump(chart_data, f, indent=2, default=str)
    
    return chart_id


def _load_all_charts():
    """Load all saved charts from files."""
    charts = []
    if os.path.exists(CHARTS_DIR):
        for filename in sorted(os.listdir(CHARTS_DIR), reverse=True):
            if filename.endswith('.json'):
                filepath = os.path.join(CHARTS_DIR, filename)
                try:
                    with open(filepath, 'r') as f:
                        chart = json.load(f)
                        chart['id'] = filename.replace('.json', '')
                        charts.append(chart)
                except Exception as e:
                    logger.error(f"Error loading chart {filename}: {e}")
    
    return charts


@api_bp.route('/geocode', methods=['GET'])
def geocode():
    """Geocode a place name to coordinates using Nominatim."""
    try:
        q = request.args.get('q', '').strip()
        if not q or len(q) < 2:
            return jsonify({'error': 'Query too short'}), 400
        
        # Query Nominatim
        params = {
            'q': q,
            'format': 'json',
            'limit': 10,
            'addressdetails': 1
        }
        headers = {'User-Agent': 'Vedica/1.0'}
        
        response = requests.get(NOMINATIM_API, params=params, headers=headers, timeout=5)
        if response.status_code != 200:
            return jsonify([]), 200
        
        results = response.json()
        
        # Transform results
        places = []
        for r in results:
            places.append({
                'display': r.get('name', ''),
                'full': r.get('display_name', ''),
                'lat': float(r.get('lat', 0)),
                'lon': float(r.get('lon', 0))
            })
        
        return jsonify(places), 200
        
    except requests.RequestException:
        return jsonify([]), 200
    except Exception as e:
        logger.error(f"Geocode error: {str(e)}")
        return jsonify([]), 200


@api_bp.route('/chart/calculate', methods=['POST'])
def calculate_chart():
    """Calculate a birth chart from JSON request data."""
    try:
        from services.chart_service import ChartService
        
        # Parse JSON request
        data = request.get_json()
        if not data:
            return jsonify({'error': 'Missing JSON body'}), 400
        
        # Extract fields
        name = data.get('name', 'Chart')
        date_str = data.get('date')
        time_str = data.get('time')
        timezone_str = data.get('timezone', '+05:30')
        lat = data.get('latitude')
        lon = data.get('longitude')
        
        # Validate required fields
        if not date_str or not time_str or lat is None or lon is None:
            return jsonify({
                'error': 'Missing required fields: date, time, latitude, longitude'
            }), 400
        
        # Validate coordinate ranges
        if not (-90 <= lat <= 90):
            return jsonify({'error': 'Latitude must be between -90 and 90'}), 400
        if not (-180 <= lon <= 180):
            return jsonify({'error': 'Longitude must be between -180 and 180'}), 400
        
        # Calculate chart using new method signature
        chart_data = ChartService.calculate_chart(
            name=name,
            birth_date_str=date_str,
            birth_time_str=time_str,
            latitude=lat,
            longitude=lon,
            timezone_str=timezone_str
        )
        
        # Extract PyJHora raw data if present
        pyjhora_raw = chart_data.pop('pyjhora_raw', None)
        
        # Add metadata to response
        chart_data['meta'] = {
            'name': name,
            'date': date_str,
            'time': time_str,
            'timezone': timezone_str,
            'latitude': lat,
            'longitude': lon,
        }
        
        # Include PyJHora raw data in response
        if pyjhora_raw:
            chart_data['pyjhora_raw'] = pyjhora_raw
        
        return jsonify(chart_data), 200
        
    except ValueError as ve:
        logger.warning(f"Validation error: {str(ve)}")
        return jsonify({'error': f'Invalid input: {str(ve)}'}), 400
    except Exception as e:
        logger.error(f"Chart calculation error: {str(e)}", exc_info=True)
        return jsonify({'error': 'Internal server error during calculation'}), 500


@api_bp.route('/chart/save', methods=['POST'])
def save_chart():
    """Save a calculated chart to database."""
    try:
        from services.chart_service import ChartService
        
        data = request.get_json()
        if not data:
            return jsonify({'error': 'Missing JSON body'}), 400
        
        # Extract chart data
        name = data.get('meta', {}).get('name', 'Chart')
        dob = data.get('meta', {}).get('date', '')
        tob = data.get('meta', {}).get('time', '')
        timezone = data.get('meta', {}).get('timezone', '+05:30')
        place = data.get('meta', {}).get('place', '')
        latitude = data.get('meta', {}).get('latitude', 0)
        longitude = data.get('meta', {}).get('longitude', 0)
        
        # Validate required fields
        if not dob or not tob:
            return jsonify({'error': 'Missing date or time in chart data'}), 400
        
        # Extract PyJHora raw data if present
        pyjhora_raw = data.pop('pyjhora_raw', None)
        
        # Calculate UTC datetime
        from datetime import datetime, timedelta
        from core.ephemeris import parse_timezone
        
        date_obj = datetime.strptime(dob, '%Y-%m-%d').date()
        time_obj = datetime.strptime(tob, '%H:%M').time()
        tz_offset = parse_timezone(timezone)
        dt_local = datetime.combine(date_obj, time_obj)
        dt_utc = dt_local - timedelta(hours=tz_offset)
        
        # Save to database
        from core.database import save_chart as db_save_chart
        
        # Extract individual fields from data
        ayanamsha = data.get('ayanamsha')
        rasi_chart = data.get('rasi_chart')
        retrograde_planets = data.get('retrograde_planets')
        vargas = data.get('vargas')
        planet_dignity = data.get('planet_dignity')
        
        chart_id = db_save_chart(
            name=name,
            dob=dob,
            tob=tob,
            timezone=timezone,
            place=place,
            lat=latitude,
            lon=longitude,
            dt_utc=dt_utc.isoformat(),
            ayanamsha=ayanamsha,
            rasi_chart=rasi_chart,
            retrograde_planets=retrograde_planets,
            vargas=vargas,
            planet_dignity=planet_dignity
        )
        
        return jsonify({
            'id': chart_id,
            'message': 'Chart saved to database'
        }), 201
        
    except Exception as e:
        logger.error(f"Save chart error: {str(e)}", exc_info=True)
        return jsonify({'error': f'Failed to save chart: {str(e)}'}), 500


@api_bp.route('/charts', methods=['GET'])
def get_all_charts():
    """Get all saved charts from database."""
    try:
        from core.database import get_all_charts as db_get_all_charts
        
        charts_data = db_get_all_charts()
        
        charts = []
        for row in charts_data:
            charts.append({
                'id': row['id'],
                'meta': {
                    'name': row['name'],
                    'date': row['dob'],
                    'time': row['tob'],
                    'timezone': row['timezone'],
                    'place': row['place'],
                    'latitude': row['latitude'],
                    'longitude': row['longitude'],
                },
                'created_at': row['created_at']
            })
        
        return jsonify(charts), 200
        
    except Exception as e:
        logger.error(f"Load charts error: {str(e)}", exc_info=True)
        return jsonify([]), 200


@api_bp.route('/charts/search', methods=['GET'])
def search_charts():
    """Search saved charts by name or place in database."""
    try:
        from core.database import search_charts as db_search_charts, get_all_charts as db_get_all_charts
        
        q = request.args.get('q', '').lower().strip()
        
        if q:
            charts_data = db_search_charts(q)
        else:
            charts_data = db_get_all_charts()
        
        charts = []
        for row in charts_data:
            charts.append({
                'id': row['id'],
                'meta': {
                    'name': row['name'],
                    'date': row['dob'],
                    'time': row['tob'],
                    'timezone': row['timezone'],
                    'place': row['place'],
                    'latitude': row['latitude'],
                    'longitude': row['longitude'],
                },
                'created_at': row['created_at']
            })
        
        return jsonify(charts), 200
        
    except Exception as e:
        logger.error(f"Search charts error: {str(e)}", exc_info=True)
        return jsonify([]), 200


@api_bp.route('/chart/<int:chart_id>', methods=['GET'])
def get_chart(chart_id):
    """Get a specific chart from database by ID."""
    try:
        from core.database import get_chart as db_get_chart
        
        # Use database function to get chart
        chart = db_get_chart(chart_id)
        
        if not chart:
            return jsonify({'error': 'Chart not found'}), 404
        
        # Format response
        response = {
            'id': chart.get('id'),
            'meta': {
                'name': chart.get('name'),
                'date': chart.get('dob'),
                'time': chart.get('tob'),
                'timezone': chart.get('timezone'),
                'place': chart.get('place'),
                'latitude': chart.get('latitude'),
                'longitude': chart.get('longitude'),
            },
            'ayanamsha': chart.get('ayanamsha'),
            'rasi_chart': chart.get('rasi_chart'),
            'retrograde_planets': chart.get('retrograde_planets'),
            'vargas': chart.get('vargas'),
            'planet_dignity': chart.get('planet_dignity'),
            'created_at': chart.get('created_at')
        }
        
        return jsonify(response), 200
        
    except Exception as e:
        logger.error(f"Get chart error: {str(e)}", exc_info=True)
        return jsonify({'error': f'Failed to retrieve chart: {str(e)}'}), 500


@api_bp.route('/chart/<int:chart_id>', methods=['DELETE'])
def delete_chart(chart_id):
    """Delete a saved chart from database."""
    try:
        from core.database import delete_chart as db_delete_chart, get_chart
        from core.analytics import remove_chart_from_cache
        
        # Check if chart exists
        if not get_chart(chart_id):
            return jsonify({'error': 'Chart not found'}), 404
        
        # Remove from analytics cache first
        remove_chart_from_cache(chart_id)
        
        # Delete the chart
        db_delete_chart(chart_id)
        
        return jsonify({'message': 'Chart deleted successfully'}), 200
        
    except Exception as e:
        logger.error(f"Delete chart error: {str(e)}", exc_info=True)
        return jsonify({'error': f'Failed to delete chart: {str(e)}'}), 500


@api_bp.route('/charts/delete-all', methods=['DELETE'])
def delete_all_charts():
    """Delete all saved charts from database (DEV ONLY)."""
    try:
        from core.database import delete_all_charts as db_delete_all
        from core.analytics import rebuild_cache
        
        count = db_delete_all()
        
        # Clear all analytics cache
        rebuild_cache()
        
        return jsonify({
            'message': f'Deleted {count} chart(s)',
            'count': count
        }), 200
        
    except Exception as e:
        logger.error(f"Delete all charts error: {str(e)}", exc_info=True)
        return jsonify({'error': f'Failed to delete charts: {str(e)}'}), 500


# ---------------------------------------------------------------------------
# Analytics endpoints
# ---------------------------------------------------------------------------

@api_bp.route('/analytics', methods=['GET'])
def get_analytics():
    """Get all analytics data for dashboard (cached aggregates)."""
    try:
        from core.database import get_conn
        
        conn = get_conn()
        c = conn.cursor()
        
        c.execute('SELECT key, count, chart_ids FROM analytics_cache')
        rows = c.fetchall()
        conn.close()
        
        data = {}
        for key, count, chart_ids_json in rows:
            data[key] = {
                'count': count,
                'chart_ids': json.loads(chart_ids_json or '[]')
            }
        
        return jsonify(data), 200
        
    except Exception as e:
        logger.error(f"Analytics error: {str(e)}", exc_info=True)
        return jsonify({'error': 'Failed to fetch analytics'}), 500


@api_bp.route('/analytics/rebuild', methods=['POST'])
def rebuild_analytics():
    """Rebuild analytics cache from all charts."""
    try:
        from core.analytics import rebuild_cache
        
        rebuild_cache()
        return jsonify({'ok': True, 'message': 'Analytics cache rebuilt successfully'}), 200
        
    except Exception as e:
        logger.error(f"Analytics rebuild error: {str(e)}", exc_info=True)
        return jsonify({'ok': False, 'error': str(e)}), 500


@api_bp.route('/planet-dignity-heatmap', methods=['GET'])
def planet_dignity_heatmap():
    """Get planet dignity heatmap data - count of charts with each planet/dignity combination."""
    try:
        from core.database import get_conn
        
        conn = get_conn()
        c = conn.cursor()
        
        # Get all charts with planet_dignity data
        c.execute('SELECT id, name, planet_dignity FROM charts WHERE planet_dignity IS NOT NULL')
        rows = c.fetchall()
        conn.close()
        
        # Planet names for display
        planets = ['Sun', 'Moon', 'Mars', 'Mercury', 'Jupiter', 'Venus', 'Saturn', 'Rahu', 'Ketu']
        
        # Dignity types
        dignities = ['exalted', 'deeply_exalted', 'debilitated', 'deeply_debilitated', 
                     'own_sign', 'moola_trikona', 'combust', 'friendly_sign', 'enemy_sign', 'neutral_sign']
        
        # Initialize heatmap: {planet_name: {dignity_type: {count: int, chart_ids: []}}}
        heatmap = {}
        for planet in planets:
            heatmap[planet] = {}
            for dignity in dignities:
                heatmap[planet][dignity] = {'count': 0, 'chart_ids': []}
        
        # Process each chart
        for chart_row in rows:
            chart_id, chart_name, planet_dignity_json = chart_row[0], chart_row[1], chart_row[2]
            try:
                planet_dignity = json.loads(planet_dignity_json)
                
                # For each dignity type, check which planets have it
                for dignity_type, planet_ids in planet_dignity.items():
                    if dignity_type not in dignities or not isinstance(planet_ids, list):
                        continue
                    
                    # planet_ids is a list of planet indices (0-8)
                    for planet_idx in planet_ids:
                        if 0 <= planet_idx < len(planets):
                            planet_name = planets[planet_idx]
                            heatmap[planet_name][dignity_type]['count'] += 1
                            heatmap[planet_name][dignity_type]['chart_ids'].append({
                                'id': chart_id,
                                'name': chart_name
                            })
            except (json.JSONDecodeError, TypeError, KeyError):
                # Skip charts with invalid planet_dignity data
                continue
        
        return jsonify({
            'heatmap': heatmap,
            'planets': planets,
            'dignities': dignities,
            'total_charts': len(rows)
        })
    
    except Exception as e:
        logger.error(f"Planet dignity heatmap error: {str(e)}")
        return jsonify({'error': str(e)}), 500


