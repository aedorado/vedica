#!/usr/bin/env python3
"""
CLI to batch import birth charts from text input.
Format: Name | HH:MM DD/MM/YYYY +TZ | City, Country, longitude, latitude
"""

import sys
from datetime import datetime
from core.ephemeris import calculate_chart
from core.database import save_chart
from core.divisional_charts import compute_major_vargas
from core.analytics import process_chart
from core.divisional_charts import compute_major_vargas



def parse_line(line: str) -> dict:
    """Parse single chart entry line."""
    parts = [p.strip() for p in line.split('|')]
    if len(parts) != 3:
        raise ValueError(f"Expected 3 parts separated by |, got {len(parts)}")
    
    name = parts[0]
    
    # Parse time and date: "HH:MM DD/MM/YYYY"
    time_date = parts[1].split()
    if len(time_date) < 3:
        raise ValueError(f"Expected 'HH:MM DD/MM/YYYY +TZ', got '{parts[1]}'")
    
    time_str = time_date[0]  # HH:MM
    date_str = time_date[1]  # DD/MM/YYYY
    tz_str = time_date[2]    # +HH:MM
    
    # Convert DD/MM/YYYY to YYYY-MM-DD
    d, m, y = date_str.split('/')
    date_normalized = f"{y}-{m}-{d}"
    
    # Parse location: last 2 are lon, lat; everything before is place
    loc_parts = [p.strip() for p in parts[2].split(',')]
    if len(loc_parts) < 4:
        raise ValueError(f"Expected at least 'City, Country, longitude, latitude', got '{parts[2]}'")
    
    # Last 2 are lon, lat
    latitude = float(loc_parts[-1])
    longitude = float(loc_parts[-2])
    
    # Everything else is place (handle multi-part cities like "Barhalganj, Gorakhpur, India")
    place_display = ', '.join(loc_parts[:-2])
    
    return {
        'name': name,
        'date': date_normalized,
        'time': time_str,
        'timezone': tz_str,
        'place': place_display,
        'latitude': latitude,
        'longitude': longitude,
    }


def import_chart(entry: dict) -> str:
    """Calculate and save chart, return chart_id."""
    try:
        result = calculate_chart(
            entry['name'],
            entry['date'],
            entry['time'],
            entry['latitude'],
            entry['longitude'],
            entry['timezone']
        )
        
        # Compute major vargas from rasi_chart
        vargas = None
        rasi_chart = result.get('rasi_chart')
        if rasi_chart:
            try:
                vargas = compute_major_vargas(rasi_chart)
            except Exception as e:
                print(f"  ⚠ Could not compute vargas: {e}")
        
        # Calculate planet dignity
        planet_dignity = None
        if rasi_chart:
            try:
                from core.planet_dignity import calculate_planet_dignity
                planet_dignity = calculate_planet_dignity(rasi_chart)
            except Exception as e:
                print(f"  ⚠ Could not calculate planet dignity: {e}")
        
        # Extract vimshottari dasha
        vimshottari_dasha = result.get('vimshottari_dasha')
        
        chart_id = save_chart(
            entry['name'],
            entry['date'],
            entry['time'],
            entry['timezone'],
            entry['place'],
            entry['latitude'],
            entry['longitude'],
            entry['date'] + ' 00:00 UTC',  # dt_utc placeholder
            ayanamsha=result.get('ayanamsha'),
            rasi_chart=rasi_chart,
            retrograde_planets=result.get('retrograde_planets'),
            vargas=vargas,
            planet_dignity=planet_dignity,
            vimshottari_dasha=vimshottari_dasha
        )
        
        # Update analytics cache
        process_chart(result, chart_id)
        
        return chart_id
    except Exception as e:
        raise Exception(f"Failed to import {entry['name']}: {str(e)}")


def main():
    """Read from stdin, parse, and import charts."""
    count = 0
    errors = []
    
    for line_num, line in enumerate(sys.stdin, 1):
        line = line.strip()
        if not line or line.startswith('#'):
            continue
        
        try:
            entry = parse_line(line)
            chart_id = import_chart(entry)
            print(f"✓ {entry['name']:30} → Chart ID: {chart_id}")
            count += 1
        except Exception as e:
            errors.append(f"Line {line_num}: {str(e)}")
            print(f"✗ {str(e)}")
    
    print(f"\n{count} charts imported successfully")
    if errors:
        print(f"\n{len(errors)} error(s):")
        for err in errors:
            print(f"  {err}")


if __name__ == '__main__':
    main()
