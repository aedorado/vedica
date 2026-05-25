"""
Vedica Astrology API - Flask app factory
"""
from flask import Flask, render_template, request, jsonify, redirect, url_for
from flask_cors import CORS
import logging
import logging.handlers
import os
from datetime import datetime, timedelta


def create_app():
    """Create and configure Flask application."""
    app = Flask(__name__, 
                template_folder='templates',
                static_folder='static', 
                static_url_path='/static')
    app.secret_key = 'vedica-dev-secret'
    
    # Enable CORS for API calls
    CORS(app)
    
    # Configure logging
    _configure_logging()
    
    # Register API blueprints
    from api import api_bp
    app.register_blueprint(api_bp, url_prefix='/api')
    
    # Template route - Form input
    @app.route('/')
    def index():
        return render_template('index.html')
    
    # Template route - Calculate and render chart
    @app.route('/chart', methods=['POST'])
    def calculate_chart_template():
        """Calculate chart from form submission and render template."""
        try:
            from services.chart_service import ChartService
            
            # Parse form data
            name = request.form.get('name', 'Chart')
            dob_str = request.form.get('dob', '')
            tob_str = request.form.get('tob', '')
            timezone_str = request.form.get('timezone', '+05:30')
            lat_str = request.form.get('lat', '')
            lon_str = request.form.get('lon', '')
            place = request.form.get('place_display', '')
            
            # Validate required fields
            if not dob_str or not tob_str or not lat_str or not lon_str:
                return render_template('index.html', 
                                     error='Missing required fields: date, time, location')
            
            # Parse inputs
            latitude = float(lat_str)
            longitude = float(lon_str)
            
            # Calculate chart with new method signature
            chart_data = ChartService.calculate_chart(
                name=name,
                birth_date_str=dob_str,
                birth_time_str=tob_str,
                latitude=latitude,
                longitude=longitude,
                timezone_str=timezone_str
            )
            
            # Auto-save chart to database
            chart_id = None
            rasi_chart = chart_data.get('rasi_chart')
            retrograde_planets = chart_data.get('retrograde_planets', [])
            planet_dignity = chart_data.get('planet_dignity', {})
            ayanamsha = chart_data.get('ayanamsha', 0)
            vimshottari_dasha_raw = chart_data.get('vimshottari_dasha', {})
            try:
                save_result = ChartService.save_chart(
                    name=name,
                    birth_date_str=dob_str,
                    birth_time_str=tob_str,
                    latitude=latitude,
                    longitude=longitude,
                    timezone_str=timezone_str,
                    place=place,
                    chart_data=chart_data
                )
                chart_id = save_result.get('chart_id')
                logging.info(f"✅ Chart auto-saved with ID: {chart_id}")
            except Exception as e:
                logging.error(f"Auto-save failed: {str(e)}", exc_info=True)
                # Don't fail the whole request if save fails, just log it
            
            # Prepare template data (pass raw data for FE processing)
            from core.constants import PLANET_COLORS, PLANET_GLYPHS
            from core.ephemeris import _convert_julian_date_to_datetime
            
            # Ensure meta has all required fields
            meta = chart_data.get('meta', {})
            meta.update({
                'name': name,
                'date': dob_str,
                'time': tob_str,
                'timezone': timezone_str,
                'place': place,
                'latitude': latitude,
                'longitude': longitude,
            })
            
            data = {
                'meta': meta,
                'rasi_chart': rasi_chart,  # Raw PyJHora data for FE processing
                'retrograde_planets': retrograde_planets,  # Retrograde list for FE
                'planet_dignity': planet_dignity,  # Planet dignity data (extracted before save)
                'ayanamsha': ayanamsha,
                'planets': {},  # Empty - will be populated by FE JS
                'ascendant': None,  # Empty - will be populated by FE JS
                'house_cusps': [],  # Empty - PyJHora doesn't calc houses
                'display_order': ['Sun', 'Moon', 'Mars', 'Mercury', 'Jupiter', 'Venus', 'Saturn', 'Rahu', 'Ketu'],
                'auto_saved': chart_id is not None,  # Flag indicating chart was auto-saved
                'vimshottari_dasha': {
                    'raw': vimshottari_dasha_raw,
                    'processed': _convert_julian_date_to_datetime(vimshottari_dasha_raw),
                    'birth_date': dob_str
                } if vimshottari_dasha_raw else {}
            }
            
            # Pass colors and glyphs as additional context
            return render_template('chart.html', data=data, colors=PLANET_COLORS, glyphs=PLANET_GLYPHS)
            
        except Exception as e:
            logging.error(f"Chart calculation error: {str(e)}", exc_info=True)
            return render_template('index.html', 
                                 error=f'Calculation error: {str(e)}'), 400
    
    # Template route - Saved charts
    @app.route('/saved')
    def saved_charts():
        """Display saved charts template."""
        return render_template('saved_charts.html')
    
    # Template route - View specific saved chart
    @app.route('/chart/<int:chart_id>')
    def view_chart(chart_id):
        """Display a specific saved chart by ID."""
        try:
            from core.database import get_chart
            from core.constants import PLANET_COLORS, PLANET_GLYPHS
            import json
            
            chart_record = get_chart(chart_id)
            if not chart_record:
                return render_template('index.html', error=f'Chart {chart_id} not found')
            
            # Parse stored JSON fields
            rasi_chart = chart_record.get('rasi_chart')
            if isinstance(rasi_chart, str):
                rasi_chart = json.loads(rasi_chart)
            
            retrograde_planets = chart_record.get('retrograde_planets')
            if isinstance(retrograde_planets, str):
                retrograde_planets = json.loads(retrograde_planets)
            elif not retrograde_planets:
                retrograde_planets = []
            
            # Parse planet dignity
            planet_dignity = chart_record.get('planet_dignity')
            if isinstance(planet_dignity, str):
                planet_dignity = json.loads(planet_dignity)
            elif not planet_dignity:
                planet_dignity = {}
            
            # Parse vargas
            vargas = chart_record.get('vargas')
            if isinstance(vargas, str):
                vargas = json.loads(vargas)
            elif not vargas:
                vargas = {}
            
            # Helper: Convert PyJHora format to template format
            def pyjhora_to_template_format(varga_list):
                """Convert [[planet_id, [sign_idx, lon]], ...] to {planet_name: {...}, ...}"""
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
            
            # Convert vargas to template format
            all_divisors_converted = {}
            for div_key, varga_list in vargas.items():
                all_divisors_converted[div_key] = pyjhora_to_template_format(varga_list)
            
            # Get ascendant sign index from D1 (rasi_chart)
            ascendant_sign_idx = 0
            if rasi_chart and len(rasi_chart) > 0:
                for planet_id, coords in rasi_chart:
                    if str(planet_id) == 'L':
                        ascendant_sign_idx = coords[0]
                        break
            
            # Prepare template data (pass raw data for FE processing)
            meta = {
                'name': chart_record['name'],
                'date': chart_record['dob'],
                'time': chart_record['tob'],
                'timezone': chart_record['timezone'],
                'place': chart_record['place'] or '',
                'latitude': chart_record['latitude'],
                'longitude': chart_record['longitude'],
            }
            
            data = {
                'meta': meta,
                'rasi_chart': rasi_chart,  # Raw PyJHora data for FE processing
                'retrograde_planets': retrograde_planets,  # Retrograde list for FE
                'planet_dignity': chart_record.get('planet_dignity') or {},  # Planet dignity data
                'ayanamsha': chart_record.get('ayanamsha', 0),
                'planets': {},  # Empty - will be populated by FE JS
                'ascendant': None,  # Empty - will be populated by FE JS
                'house_cusps': [],  # Empty - PyJHora doesn't calc houses
                'display_order': ['Sun', 'Moon', 'Mars', 'Mercury', 'Jupiter', 'Venus', 'Saturn', 'Rahu', 'Ketu'],
                'auto_saved': False,  # This is a saved view, not freshly calculated
                'lagna_sign_idx': ascendant_sign_idx,
                'divisional_charts': {
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
            }

            # Add vimshottari dasha with processed human-readable dates
            from core.ephemeris import _convert_julian_date_to_datetime
            raw_dasha = chart_record.get('vimshottari_dasha')
            data['vimshottari_dasha'] = {
                'raw': raw_dasha,
                'processed': _convert_julian_date_to_datetime(raw_dasha),
                'birth_date': chart_record.get('dob')
            } if raw_dasha else {}
            
            return render_template('chart.html', data=data, colors=PLANET_COLORS, glyphs=PLANET_GLYPHS)
        except Exception as e:
            logging.error(f"Error viewing chart {chart_id}: {str(e)}", exc_info=True)
            return render_template('index.html', error=f'Error loading chart: {str(e)}')
    
    # Template route - Analytics
    @app.route('/analytics')
    def analytics():
        """Display analytics template."""
        return render_template('analytics.html')
    
    return app


def _configure_logging():
    """Configure comprehensive logging."""
    log_dir = 'logs'
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
    
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.DEBUG)
    
    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.DEBUG)
    console_formatter = logging.Formatter(
        '%(asctime)s | %(name)-25s | %(levelname)-8s | %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    console_handler.setFormatter(console_formatter)
    root_logger.addHandler(console_handler)
    
    # File handler
    file_handler = logging.handlers.RotatingFileHandler(
        os.path.join(log_dir, 'vedica.log'),
        maxBytes=10485760,  # 10MB
        backupCount=5
    )
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(console_formatter)
    root_logger.addHandler(file_handler)
    
    logger = logging.getLogger(__name__)
    logger.info("=" * 80)
    logger.info("🚀 VEDICA API STARTING")
    logger.info("=" * 80)

