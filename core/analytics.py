"""Analytics cache layer for statistics aggregation."""

import json
import sqlite3
from datetime import datetime
from pathlib import Path

DB_PATH = Path(__file__).parent.parent / 'data' / 'charts.db'


def _upsert_cache(c, key, chart_id):
    """Helper: upsert a single cache entry (uses existing cursor)."""
    c.execute('SELECT count, chart_ids FROM analytics_cache WHERE key = ?', (key,))
    row = c.fetchone()
    
    if row:
        count, ids_json = row
        ids = json.loads(ids_json or '[]')
        if chart_id not in ids:
            ids.append(chart_id)
            count += 1
    else:
        count = 1
        ids = [chart_id]
    
    c.execute('''
        INSERT OR REPLACE INTO analytics_cache (key, count, chart_ids, updated_at)
        VALUES (?, ?, ?, ?)
    ''', (key, count, json.dumps(ids), datetime.now()))


def get_cache(key):
    """Get count + chart_ids for a key."""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('SELECT count, chart_ids FROM analytics_cache WHERE key = ?', (key,))
    row = c.fetchone()
    conn.close()
    if not row:
        return 0, []
    return row[0], json.loads(row[1] or '[]')


def increment_cache(key, chart_id):
    """Add chart_id to a cache cell (idempotent)."""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    _upsert_cache(c, key, chart_id)
    conn.commit()
    conn.close()


def rebuild_cache():
    """Full recalculation from all charts."""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    # Clear old data
    c.execute('DELETE FROM analytics_cache')
    c.execute('DELETE FROM analytics_metadata')
    conn.commit()
    
    # Scan all charts
    c.execute('SELECT id, rasi_chart, retrograde_planets, dob FROM charts ORDER BY id')
    charts = c.fetchall()
    
    for chart_id, rasi_json, retro_json, dob in charts:
        rasi_chart = json.loads(rasi_json or '[]')
        retrograde = json.loads(retro_json or '[]')
        
        # Get lagna sign index
        lagna_sign_idx = 0
        for item in rasi_chart:
            if item[0] == 'L':
                lagna_sign_idx = item[1][0] % 12
                _upsert_cache(c, f'ascendant:{lagna_sign_idx}', chart_id)
                break
        
        # Planets in rashi & house
        for item in rasi_chart:
            if item[0] != 'L':
                planet = item[0]  # '0'-'8' for Sun-Ketu
                sign_idx = item[1][0] % 12
                _upsert_cache(c, f'planet_rashi:{planet}:{sign_idx}', chart_id)
                
                # Calculate house (1-12)
                house_num = ((sign_idx - lagna_sign_idx + 12) % 12) + 1
                _upsert_cache(c, f'planet_house:{planet}:{house_num}', chart_id)
        
        # Retrograde planets
        for planet in retrograde:
            _upsert_cache(c, f'retrograde:{planet}', chart_id)
        
        # Birth month
        month = dob.split('-')[1] if len(dob.split('-')) > 1 else '01'
        _upsert_cache(c, f'month:{month}', chart_id)
        
        # Birth year
        year = dob.split('-')[0] if len(dob.split('-')) > 0 else '2000'
        _upsert_cache(c, f'year:{year}', chart_id)
    
    # Update metadata
    c.execute('INSERT OR REPLACE INTO analytics_metadata (key, value) VALUES (?, ?)',
              ('total_charts', str(len(charts))))
    c.execute('INSERT OR REPLACE INTO analytics_metadata (key, value) VALUES (?, ?)',
              ('last_rebuild', datetime.now().isoformat()))
    
    conn.commit()
    conn.close()


def process_chart(chart_data, chart_id):
    """Process single chart and update cache (called on save)."""
    rasi_chart = chart_data.get('rasi_chart', [])
    retrograde = chart_data.get('retrograde_planets', [])
    
    # Get lagna sign index
    lagna_sign_idx = 0
    for item in rasi_chart:
        if item[0] == 'L':
            lagna_sign_idx = item[1][0] % 12
            increment_cache(f'ascendant:{lagna_sign_idx}', chart_id)
            break
    
    # Planets
    for item in rasi_chart:
        if item[0] != 'L':
            planet = item[0]
            sign_idx = item[1][0] % 12
            increment_cache(f'planet_rashi:{planet}:{sign_idx}', chart_id)
            
            # Calculate house (1-12)
            house_num = ((sign_idx - lagna_sign_idx + 12) % 12) + 1
            increment_cache(f'planet_house:{planet}:{house_num}', chart_id)
    
    # Retrograde
    for planet in retrograde:
        increment_cache(f'retrograde:{planet}', chart_id)
    
    # Birth month & year (from chart metadata)
    meta = chart_data.get('meta', {})
    dob = meta.get('dob', '')
    if dob:
        parts = dob.split('-')
        if len(parts) >= 2:
            month = parts[1]
            increment_cache(f'month:{month}', chart_id)
        if len(parts) >= 1:
            year = parts[0]
            increment_cache(f'year:{year}', chart_id)


def remove_chart_from_cache(chart_id):
    """Remove a chart from all cache entries when it's deleted."""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    # Get all cache entries
    c.execute('SELECT key, count, chart_ids FROM analytics_cache')
    rows = c.fetchall()
    
    for key, count, ids_json in rows:
        ids = json.loads(ids_json or '[]')
        if chart_id in ids:
            ids.remove(chart_id)
            new_count = count - 1
            
            if new_count <= 0:
                # Delete cache entry if no charts remain
                c.execute('DELETE FROM analytics_cache WHERE key = ?', (key,))
            else:
                # Update cache entry with new count
                c.execute('''
                    UPDATE analytics_cache 
                    SET count = ?, chart_ids = ?, updated_at = ?
                    WHERE key = ?
                ''', (new_count, json.dumps(ids), datetime.now(), key))
    
    conn.commit()
    conn.close()
