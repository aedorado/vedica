"""PostgreSQL database for saved birth charts."""

import psycopg
import json
import os
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

DATABASE_URL = os.getenv('POSTGRES_URL')
if not DATABASE_URL:
    raise ValueError("POSTGRES_URL environment variable not set")


def get_conn():
    """Get PostgreSQL connection."""
    return psycopg.connect(DATABASE_URL)


def save_chart(name, dob, tob, timezone, place, lat, lon, dt_utc, ayanamsha=None, rasi_chart=None, retrograde_planets=None, vargas=None, planet_dignity=None, vimshottari_dasha=None):
    """Save a chart to the database (INSERT)."""
    conn = get_conn()
    c = conn.cursor()
    
    c.execute('''
        INSERT INTO charts (name, dob, tob, timezone, place, latitude, longitude, dt_utc, ayanamsha, rasi_chart, retrograde_planets, vargas, planet_dignity, vimshottari_dasha)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        RETURNING id
    ''', (
        name, dob, tob, timezone, place, lat, lon, dt_utc,
        ayanamsha,
        json.dumps(rasi_chart) if rasi_chart else None,
        json.dumps(retrograde_planets) if retrograde_planets else None,
        json.dumps(vargas) if vargas else None,
        json.dumps(planet_dignity) if planet_dignity else None,
        json.dumps(vimshottari_dasha) if vimshottari_dasha else None
    ))
    
    chart_id = c.fetchone()[0]
    conn.commit()
    conn.close()
    
    return chart_id


def update_chart(chart_id, name=None):
    """Update an existing chart in the database."""
    conn = get_conn()
    c = conn.cursor()
    
    if name is not None:
        c.execute('''
            UPDATE charts SET name = %s WHERE id = %s
        ''', (name, chart_id))
    
    conn.commit()
    conn.close()


def get_all_charts():
    """Fetch all saved charts, ordered by creation date (newest first)."""
    conn = get_conn()
    c = conn.cursor()
    
    c.execute('''
        SELECT id, name, dob, tob, timezone, place, latitude, longitude, dt_utc, created_at
        FROM charts
        ORDER BY created_at DESC
    ''')
    
    rows = c.fetchall()
    columns = [desc[0] for desc in c.description]
    conn.close()
    
    return [dict(zip(columns, row)) for row in rows]


def get_chart(chart_id):
    """Fetch a specific chart by ID."""
    conn = get_conn()
    c = conn.cursor()
    
    c.execute('''
        SELECT * FROM charts WHERE id = %s
    ''', (chart_id,))
    
    row = c.fetchone()
    columns = [desc[0] for desc in c.description]
    conn.close()
    
    if row:
        row_dict = dict(zip(columns, row))
        # Parse JSON fields
        if row_dict.get('rasi_chart'):
            row_dict['rasi_chart'] = json.loads(row_dict['rasi_chart'])
        if row_dict.get('retrograde_planets'):
            row_dict['retrograde_planets'] = json.loads(row_dict['retrograde_planets'])
        if row_dict.get('vargas'):
            row_dict['vargas'] = json.loads(row_dict['vargas'])
        if row_dict.get('planet_dignity'):
            row_dict['planet_dignity'] = json.loads(row_dict['planet_dignity'])
        if row_dict.get('vimshottari_dasha'):
            row_dict['vimshottari_dasha'] = json.loads(row_dict['vimshottari_dasha'])
        return row_dict
    return None


def delete_chart(chart_id):
    """Delete a chart from the database."""
    conn = get_conn()
    c = conn.cursor()
    
    c.execute('DELETE FROM charts WHERE id = %s', (chart_id,))
    
    conn.commit()
    conn.close()


def delete_all_charts():
    """Delete all charts from the database."""
    conn = get_conn()
    c = conn.cursor()
    
    c.execute('DELETE FROM charts')
    count = c.rowcount
    
    conn.commit()
    conn.close()
    
    return count


def search_charts(query):
    """Search charts by name or place."""
    conn = get_conn()
    c = conn.cursor()
    
    search_term = f'%{query}%'
    c.execute('''
        SELECT id, name, dob, tob, timezone, place, latitude, longitude, dt_utc, created_at
        FROM charts
        WHERE name ILIKE %s OR place ILIKE %s
        ORDER BY created_at DESC
    ''', (search_term, search_term))
    
    rows = c.fetchall()
    columns = [desc[0] for desc in c.description]
    conn.close()
    
    return [dict(zip(columns, row)) for row in rows]
