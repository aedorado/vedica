from flask import Blueprint, render_template, request, jsonify
from datetime import datetime, timedelta
import sqlite3
import json
import logging

from core.ephemeris import calculate_chart, _convert_julian_date_to_datetime
from core.geocoder import search_places
from core.database import save_chart, get_all_charts, get_chart, delete_chart, search_charts
from core.analytics import process_chart, rebuild_cache
from core.constants import SIGNS

bp = Blueprint('main', __name__)
logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Helper Functions
# ---------------------------------------------------------------------------

def pyjhora_to_template_format(varga_list):
    """
    Convert PyJHora varga format [[planet_id, [sign_idx, lon]], ...] 
    to template format {planet_name: {position: {sign_idx: n}, retrograde: bool}, ...}
    """
    if not varga_list:
        return {}
    
    planet_map = {
        'L': 'Ascendant', '0': 'Sun', '1': 'Moon', '2': 'Mars',
        '3': 'Mercury', '4': 'Jupiter', '5': 'Venus', '6': 'Saturn',
        '7': 'Rahu', '8': 'Ketu'
    }
    
    result = {}
    for planet_id, coords in varga_list:
        planet_name = planet_map.get(str(planet_id), f'Planet{planet_id}')
        sign_idx, lon = coords
        result[planet_name] = {
            'position': {'sign_idx': sign_idx, 'decimal': lon},
            'retrograde': False
        }
    
    return result


# ---------------------------------------------------------------------------
# Pages
# ---------------------------------------------------------------------------

@bp.route('/')
def index():
    return render_template('index.html')


@bp.route('/chart', methods=['POST'])
def chart():
    try:
        name = request.form.get('name', '').strip() or 'Unknown'
        date_str = request.form.get('dob', '')        # YYYY-MM-DD
        time_str = request.form.get('tob', '')        # HH:MM
        tz_str = request.form.get('timezone', '+05:30')
        lat = float(request.form['lat'])
        lon = float(request.form['lon'])
        place_name = request.form.get('place_display', '')

        # Parse local datetime
        dt_local = datetime.strptime(f'{date_str} {time_str}', '%Y-%m-%d %H:%M')

        # Parse timezone offset
        sign = 1 if tz_str[0] == '+' else -1
        tz_h, tz_m = map(int, tz_str[1:].split(':'))
        tz_offset = sign * (tz_h + tz_m / 60)
        dt_utc = dt_local - timedelta(hours=tz_offset)

        result = calculate_chart(dt_utc, lat, lon)
        result['meta'] = {
            'name': name,
            'dob': date_str,
            'tob': time_str,
            'timezone': tz_str,
            'place': place_name,
            'lat': lat,
            'lon': lon,
            'dt_utc': dt_utc.strftime('%Y-%m-%d %H:%M UTC'),
        }
        
        # Save to database
        chart_id = save_chart(name, date_str, time_str, tz_str, place_name, lat, lon,
                              dt_utc.strftime('%Y-%m-%d %H:%M UTC'), result)
        result['chart_id'] = chart_id
        
        # Update analytics cache
        process_chart(result, chart_id)
        
        return render_template('chart.html', data=result)

    except (KeyError, ValueError) as e:
        return render_template('index.html', error=f'Invalid input: {e}'), 400


@bp.route('/analytics')
def analytics():
    return render_template('analytics.html')


@bp.route('/saved')
def saved_charts():
    """Page to view all saved charts."""
    return render_template('saved_charts.html')


@bp.route('/chart/<int:chart_id>')
def view_saved_chart(chart_id):
    """View a saved chart by ID."""
    chart = get_chart(chart_id)
    if not chart:
        return render_template('index.html', error='Chart not found'), 404
    
    # Construct data dict from database fields
    data = {
        'chart_id': chart_id,
        'ayanamsha': chart.get('ayanamsha'),
        'rasi_chart': chart.get('rasi_chart'),
        'retrograde_planets': chart.get('retrograde_planets'),
        'vargas': chart.get('vargas') or {},
        'meta': {
            'name': chart['name'],
            'date': chart['dob'],
            'time': chart['tob'],
            'timezone': chart['timezone'],
            'place': chart['place'],
            'lat': chart['latitude'],
            'lon': chart['longitude'],
            'latitude': chart['latitude'],
            'longitude': chart['longitude'],
            'dt_utc': chart['dt_utc'],
        }
    }
    
    # Convert vargas from PyJHora format to template format
    vargas = data['vargas']
    all_divisors_converted = {}
    for div_key, varga_list in vargas.items():
        all_divisors_converted[div_key] = pyjhora_to_template_format(varga_list)
    
    # Get ascendant from D1 (rasi_chart)
    ascendant_sign_idx = 0
    if chart.get('rasi_chart') and len(chart['rasi_chart']) > 0:
        # Lagna is usually the first item
        for planet_id, coords in chart['rasi_chart']:
            if str(planet_id) == 'L':
                ascendant_sign_idx = coords[0]
                break
    
    # Build divisional_charts structure for template compatibility
    data['divisional_charts'] = {
        'all_divisors': all_divisors_converted,
        'major_charts': {
            'D2': all_divisors_converted.get('2'),
            'D3': all_divisors_converted.get('3'),
            'D4': all_divisors_converted.get('4'),
            'D7': all_divisors_converted.get('7'),
            'D9': all_divisors_converted.get('9'),
            'D10': all_divisors_converted.get('10'),
            'D12': all_divisors_converted.get('12'),
            'D16': all_divisors_converted.get('16'),
            'D20': all_divisors_converted.get('20'),
            'D24': all_divisors_converted.get('24'),
            'D27': all_divisors_converted.get('27'),
            'D30': all_divisors_converted.get('30'),
            'D40': all_divisors_converted.get('40'),
            'D45': all_divisors_converted.get('45'),
            'D60': all_divisors_converted.get('60'),
        }
    }
    
    # Add lagna_sign_idx for chart rendering
    data['lagna_sign_idx'] = ascendant_sign_idx

    # Pass vimshottari dasha data to template (with processed human-readable dates)
    raw_dasha = chart.get('vimshottari_dasha')
    data['vimshottari_dasha'] = {
        'raw': raw_dasha,
        'processed': _convert_julian_date_to_datetime(raw_dasha)
    } if raw_dasha else {}
    data['planet_dignity'] = chart.get('planet_dignity')
    
    return render_template('chart.html', data=data)


# ---------------------------------------------------------------------------
# API endpoints
# ---------------------------------------------------------------------------

@bp.route('/api/geocode')
def geocode():
    q = request.args.get('q', '').strip()
    results = search_places(q) if q else []
    return jsonify(results)


@bp.route('/api/calculate', methods=['POST'])
def api_calculate():
    """JSON API for programmatic use / tests."""
    data = request.get_json(force=True)
    try:
        dt_utc = datetime.strptime(data['dt_utc'], '%Y-%m-%dT%H:%M:%S')
        lat = float(data['lat'])
        lon = float(data['lon'])
        result = calculate_chart(dt_utc, lat, lon)
        # Make JSON-serialisable
        result.pop('display_order', None)
        return jsonify({'ok': True, 'result': result})
    except Exception as e:
        return jsonify({'ok': False, 'error': str(e)}), 400


# ---------------------------------------------------------------------------
# Saved Charts API
# ---------------------------------------------------------------------------

@bp.route('/api/charts')
def api_charts():
    """Get all saved charts."""
    charts = get_all_charts()
    return jsonify(charts)


@bp.route('/api/charts/search')
def api_search_charts():
    """Search saved charts by name or place."""
    query = request.args.get('q', '').strip()
    if not query:
        charts = get_all_charts()
    else:
        charts = search_charts(query)
    return jsonify(charts)


@bp.route('/api/charts/<int:chart_id>')
def api_get_chart(chart_id):
    """Get a specific saved chart."""
    chart = get_chart(chart_id)
    if not chart:
        return jsonify({'error': 'Chart not found'}), 404
    return jsonify(chart)


@bp.route('/api/charts/<int:chart_id>', methods=['DELETE'])
def api_delete_chart(chart_id):
    """Delete a saved chart."""
    delete_chart(chart_id)
    return jsonify({'ok': True})


# ---------------------------------------------------------------------------
# Divisional Charts API
# ---------------------------------------------------------------------------

@bp.route('/api/charts/<int:chart_id>/divisional/<int:divisor>')
def api_divisional_chart(chart_id, divisor):
    """
    Get a specific divisional chart for a saved chart.
    
    Args:
        chart_id: ID of saved chart
        divisor: Divisional number (2, 3, 4, 9, 10, 12, 27, 60, etc.)
    
    Returns:
        Divisional chart data with planets and ascendant
    """
    chart = get_chart(chart_id)
    if not chart:
        return jsonify({'error': 'Chart not found'}), 404
    
    data = chart['chart_data']
    dc = data.get('divisional_charts', {})
    
    # Get all divisor planets
    all_divisors = dc.get('all_divisors', {})
    if divisor not in all_divisors:
        return jsonify({'error': f'Divisional chart D{divisor} not calculated'}), 400
    
    planets = all_divisors[divisor]
    
    # Get major chart details (with house cusps and ascendant) if available
    major_charts = dc.get('major_charts', {})
    chart_details = major_charts.get(divisor, {})
    
    return jsonify({
        'chart_id': chart_id,
        'divisor': divisor,
        'planets': planets,
        'ascendant': chart_details.get('ascendant'),
        'house_cusps': chart_details.get('house_cusps', []),
        'meta': data.get('meta', {}),
    })


@bp.route('/api/charts/<int:chart_id>/divisional-summary')
def api_divisional_summary(chart_id):
    """Get summary of all divisional charts for a saved chart."""
    chart = get_chart(chart_id)
    if not chart:
        return jsonify({'error': 'Chart not found'}), 404
    
    data = chart['chart_data']
    dc = data.get('divisional_charts', {})
    
    return jsonify({
        'chart_id': chart_id,
        'all_divisors': list(dc.get('all_divisors', {}).keys()),
        'summary': dc.get('summary', {}),
        'meta': data.get('meta', {}),
    })


@bp.route('/api/charts/<int:chart_id>/all-divisional')
def api_all_divisional_charts(chart_id):
    """Get all divisional charts at once."""
    chart = get_chart(chart_id)
    if not chart:
        return jsonify({'error': 'Chart not found'}), 404
    
    data = chart['chart_data']
    dc = data.get('divisional_charts', {})
    
    return jsonify({
        'chart_id': chart_id,
        'all_divisors': dc.get('all_divisors', {}),
        'major_charts': dc.get('major_charts', {}),
        'summary': dc.get('summary', {}),
        'meta': data.get('meta', {}),
    })


# ---------------------------------------------------------------------------
# Analytics API
# ---------------------------------------------------------------------------

@bp.route('/api/analytics')
def api_analytics():
    """Get all analytics data for dashboard."""
    from core.database import DB_PATH
    
    conn = sqlite3.connect(str(DB_PATH))
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
    
    return jsonify(data)


@bp.route('/api/analytics/rebuild', methods=['POST'])
def api_rebuild_analytics():
    """Rebuild analytics cache from all charts."""
    try:
        rebuild_cache()
        return jsonify({'ok': True, 'message': 'Analytics cache rebuilt'})
    except Exception as e:
        return jsonify({'ok': False, 'error': str(e)}), 500

