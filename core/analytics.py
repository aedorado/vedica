"""Analytics cache layer for statistics aggregation."""

import json
from datetime import datetime
from .database import get_conn
import logging
import threading

logger = logging.getLogger(__name__)


def _upsert_cache(c, key, chart_id):
    """Helper: upsert a single cache entry (uses existing cursor)."""
    c.execute('SELECT count, chart_ids FROM analytics_cache WHERE key = %s', (key,), prepare=False)
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
        INSERT INTO analytics_cache (key, count, chart_ids, updated_at)
        VALUES (%s, %s, %s, %s)
        ON CONFLICT (key) DO UPDATE SET count = %s, chart_ids = %s, updated_at = %s
    ''', (key, count, json.dumps(ids), datetime.now(), count, json.dumps(ids), datetime.now()), prepare=False)


def get_cache(key):
    """Get count + chart_ids for a key."""
    conn = get_conn()
    c = conn.cursor()
    c.execute('SELECT count, chart_ids FROM analytics_cache WHERE key = %s', (key,))
    row = c.fetchone()
    conn.close()
    if not row:
        return 0, []
    return row[0], json.loads(row[1] or '[]')


def increment_cache(key, chart_id):
    """Add chart_id to a cache cell (idempotent)."""
    conn = get_conn()
    c = conn.cursor()
    _upsert_cache(c, key, chart_id)
    conn.commit()
    conn.close()


def _process_chart_data(rasi_chart, retrograde, dob, chart_id, upsert_fn):
    """
    Process chart data and extract analytics keys.
    
    Args:
        rasi_chart: List of [planet_id, (sign_idx, longitude)]
        retrograde: List of retrograde planet IDs
        dob: Date of birth string 'YYYY-MM-DD'
        chart_id: Chart ID for logging
        upsert_fn: Callback function(key, chart_id) to store cache entry
    """
    # Get lagna sign index
    lagna_sign_idx = None
    for item in rasi_chart:
        if item[0] == 'L':
            lagna_sign_idx = item[1][0] % 12
            upsert_fn(f'ascendant:{lagna_sign_idx}', chart_id)
            break
    
    if lagna_sign_idx is None:
        logger.warning(f'   ⚠️  Lagna (L) not found in rasi_chart!')
        return
    
    # Planets in rashi & house
    for item in rasi_chart:
        if item[0] != 'L':
            planet = item[0]
            sign_idx = item[1][0] % 12
            upsert_fn(f'planet_rashi:{planet}:{sign_idx}', chart_id)
            
            # Calculate house (1-12)
            house_num = ((sign_idx - lagna_sign_idx + 12) % 12) + 1
            upsert_fn(f'planet_house:{planet}:{house_num}', chart_id)
    
    # Retrograde planets
    for planet in retrograde:
        upsert_fn(f'retrograde:{planet}', chart_id)
    
    # Planet Conjunctions (2+ planets in same sign)
    sign_planets = {}  # {sign_idx: [planet_list]}
    for item in rasi_chart:
        if item[0] != 'L':
            planet = item[0]
            sign_idx = item[1][0] % 12
            if sign_idx not in sign_planets:
                sign_planets[sign_idx] = []
            sign_planets[sign_idx].append(planet)
    
    # Store conjunctions (2+ planets in same sign)
    for sign_idx, planets_in_sign in sign_planets.items():
        if len(planets_in_sign) >= 2:
            sorted_planets = sorted(planets_in_sign)
            planets_str = ','.join(map(str, sorted_planets))
            conjunction_size = len(planets_in_sign)
            upsert_fn(f'conjunction:{conjunction_size}:{planets_str}', chart_id)
    
    # Birth month & year
    if dob:
        parts = dob.split('-')
        if len(parts) >= 2:
            month = parts[1]
            upsert_fn(f'month:{month}', chart_id)
        if len(parts) >= 1:
            year = parts[0]
            upsert_fn(f'year:{year}', chart_id)


def rebuild_cache():
    """Full recalculation from all charts."""
    logger.info('🔄 Starting analytics cache rebuild...')
    conn = get_conn()
    c = conn.cursor()

    # Clear old data
    c.execute('DELETE FROM analytics_cache')
    c.execute('DELETE FROM analytics_metadata')
    conn.commit()

    # Scan all charts
    c.execute('SELECT id, rasi_chart, retrograde_planets, dob FROM charts ORDER BY id')
    charts = c.fetchall()
    logger.info(f'🔢 Found {len(charts)} charts to process for analytics.')

    for chart_row in charts:
        chart_id, rasi_json, retro_json, dob = chart_row[0], chart_row[1], chart_row[2], chart_row[3]
        rasi_chart = json.loads(rasi_json or '[]')
        retrograde = json.loads(retro_json or '[]')

        # Use shared processing logic with callback
        def upsert_with_cursor(key, cid):
            _upsert_cache(c, key, cid)

        _process_chart_data(rasi_chart, retrograde, dob, chart_id, upsert_with_cursor)

    # Update metadata
    c.execute('INSERT INTO analytics_metadata (key, value) VALUES (%s, %s) ON CONFLICT (key) DO UPDATE SET value = %s',
              ('total_charts', str(len(charts)), str(len(charts))))
    c.execute('INSERT INTO analytics_metadata (key, value) VALUES (%s, %s) ON CONFLICT (key) DO UPDATE SET value = %s',
              ('last_rebuild', datetime.now().isoformat(), datetime.now().isoformat()))

    conn.commit()
    conn.close()
    logger.info('✅ Analytics cache rebuild complete.')


def process_chart(chart_data, chart_id):
    """Process single chart and update cache (called on save)."""
    rasi_chart = chart_data.get('rasi_chart', [])
    retrograde = chart_data.get('retrograde_planets', [])
    
    meta = chart_data.get('meta', {})
    dob = meta.get('dob') or meta.get('date', '')
    
    logger.info(f'🔍 process_chart START: chart_id={chart_id}')
    
    # Batch all updates in single transaction (much faster than opening connection for each key)
    conn = get_conn()
    c = conn.cursor()
    
    def upsert_with_cursor(key, cid):
        _upsert_cache(c, key, cid)
    
    _process_chart_data(rasi_chart, retrograde, dob, chart_id, upsert_with_cursor)
    
    conn.commit()
    conn.close()
    
    logger.info(f'🎯 process_chart COMPLETE: chart_id={chart_id}')


def remove_chart_from_cache(chart_id):
    """Remove a chart from all cache entries when it's deleted."""
    conn = get_conn()
    c = conn.cursor()
    
    # Get all cache entries
    c.execute('SELECT key, count, chart_ids FROM analytics_cache')
    rows = c.fetchall()
    
    for row in rows:
        key, count, ids_json = row[0], row[1], row[2]
        ids = json.loads(ids_json or '[]')
        if chart_id in ids:
            ids.remove(chart_id)
            new_count = count - 1
            
            if new_count <= 0:
                # Delete cache entry if no charts remain
                c.execute('DELETE FROM analytics_cache WHERE key = %s', (key,))
            else:
                # Update cache entry with new count
                c.execute('''
                    UPDATE analytics_cache 
                    SET count = %s, chart_ids = %s, updated_at = %s
                    WHERE key = %s
                ''', (new_count, json.dumps(ids), datetime.now(), key))
    
    conn.commit()
    conn.close()


def process_chart_async(chart_data, chart_id, timeout=30):
    """
    Async version: Process chart in background thread with timeout.
    Returns immediately (fire-and-forget).
    If timeout expires, hourly cron will catch it in full rebuild.
    
    Args:
        chart_data: Chart data dict
        chart_id: Chart ID
        timeout: Max seconds to wait (default 30s for Vercel)
    """
    def _process_with_error_handling():
        try:
            process_chart(chart_data, chart_id)
            logger.info(f'⚡ Async analytics completed for chart {chart_id}')
        except Exception as e:
            logger.error(f'⚠️  Async analytics failed for chart {chart_id}: {e}', exc_info=True)
    
    # Start background thread (daemon so it doesn't block app shutdown)
    thread = threading.Thread(target=_process_with_error_handling, daemon=True)
    thread.start()
    
    # Log that we're processing async
    logger.info(f'🔄 Async analytics queued for chart {chart_id} (timeout: {timeout}s)')
    
    # Optional: Could wait with timeout here, but fire-and-forget is safer for Vercel
    # thread.join(timeout=timeout)
