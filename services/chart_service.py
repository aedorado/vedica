"""
Chart calculation service using Swiss Ephemeris.
Wraps core.ephemeris calculations for API layer.
"""

from core.ephemeris import calculate_chart as core_calculate_chart
from core.database import save_chart as db_save_chart
from core.database import save_yogas_list as db_save_yogas_list

import logging

logger = logging.getLogger(__name__)


class ChartService:
    """Service layer for chart calculations."""
    
    @staticmethod
    def calculate_chart(name, birth_date_str, birth_time_str, latitude, longitude, timezone_str):
        """
        Calculate a birth chart.
        
        Args:
            name: str - person's name
            birth_date_str: str 'YYYY-MM-DD'
            birth_time_str: str 'HH:MM'
            latitude: float (-90 to 90)
            longitude: float (-180 to 180)
            timezone_str: str '+HH:MM' or '-HH:MM'
            
        Returns:
            dict with planets, ascendant, house_cusps, ayanamsha, rasi_chart, etc.
        """
        try:
            # Call core ephemeris calculation
            chart_data = core_calculate_chart(
                name, birth_date_str, birth_time_str, 
                latitude, longitude, timezone_str
            )
            return chart_data
        except Exception as e:
            logger.error(f"Chart calculation failed: {e}", exc_info=True)
            raise
    
    @staticmethod
    def save_chart(name, birth_date_str, birth_time_str, latitude, longitude, timezone_str, place='', chart_data=None):
        """
        Calculate and save a birth chart to database.
        
        Returns:
            dict with chart_id and chart_data
        """
        try:
            from datetime import datetime, timedelta
            from core.ephemeris import parse_timezone
            
            if chart_data is None:
                # Calculate if not provided
                chart_data = ChartService.calculate_chart(
                    name, birth_date_str, birth_time_str,
                    latitude, longitude, timezone_str
                )
            
            # Convert to UTC for storage
            birth_date = datetime.strptime(birth_date_str, '%Y-%m-%d').date()
            birth_time = datetime.strptime(birth_time_str, '%H:%M').time()
            tz_offset = parse_timezone(timezone_str)
            dt_local = datetime.combine(birth_date, birth_time)
            dt_utc = dt_local - timedelta(hours=tz_offset)
            
            # Extract fields from chart_data (use .get() to preserve original data)
            ayanamsha = chart_data.get('ayanamsha', 0)
            rasi_chart = chart_data.get('rasi_chart', None)
            retrograde_planets = chart_data.get('retrograde_planets', None)
            planet_dignity = chart_data.get('planet_dignity', None)
            vimshottari_dasha = chart_data.get('vimshottari_dasha', None)
            yoga_details = chart_data.get('yoga_details', None)
            yogas_in_chart = chart_data.get('yogas_in_chart', None)
            
            # Compute major vargas (D2, D3, D4, D9, D10, D12) from rasi_chart
            vargas = None
            if rasi_chart:
                try:
                    from core.divisional_charts import compute_major_vargas
                    vargas = compute_major_vargas(rasi_chart)
                except Exception as e:
                    logger.warning(f"Could not compute vargas: {e}")
            
            # Save to database
            chart_id = db_save_chart(
                name=name,
                dob=birth_date_str,
                tob=birth_time_str,
                timezone=timezone_str,
                place=place,
                lat=latitude,
                lon=longitude,
                dt_utc=dt_utc.isoformat(),
                ayanamsha=ayanamsha,
                rasi_chart=rasi_chart,
                retrograde_planets=retrograde_planets,
                vargas=vargas,
                planet_dignity=planet_dignity,
                vimshottari_dasha=vimshottari_dasha,
                yogas_in_chart=yogas_in_chart
            )
            
            logger.info(f"Chart saved with ID: {chart_id}")

            db_save_yogas_list(yoga_details)
            
            return {
                'chart_id': chart_id,
                'ayanamsha': ayanamsha,
                'rasi_chart': rasi_chart,
                'retrograde_planets': retrograde_planets,
                'vimshottari_dasha': vimshottari_dasha
            }
        except Exception as e:
            logger.error(f"Save chart failed: {e}", exc_info=True)
            raise
