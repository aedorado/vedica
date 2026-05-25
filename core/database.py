"""SQLite database for saved birth charts."""

import sqlite3
import json
from datetime import datetime
from pathlib import Path

DB_PATH = Path(__file__).parent.parent / 'data' / 'charts.db'


def init_db():
    """Initialize database schema and run migrations."""
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    c.execute('''
        CREATE TABLE IF NOT EXISTS charts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            dob TEXT NOT NULL,
            tob TEXT NOT NULL,
            timezone TEXT NOT NULL,
            place TEXT,
            latitude REAL NOT NULL,
            longitude REAL NOT NULL,
            dt_utc TEXT NOT NULL,
            ayanamsha REAL,
            rasi_chart TEXT,
            retrograde_planets TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    c.execute('''
        CREATE TABLE IF NOT EXISTS analytics_cache (
            id INTEGER PRIMARY KEY,
            key TEXT UNIQUE NOT NULL,
            count INTEGER DEFAULT 0,
            chart_ids TEXT,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    c.execute('''
        CREATE TABLE IF NOT EXISTS analytics_metadata (
            key TEXT PRIMARY KEY,
            value TEXT
        )
    ''')
    
    # Migration: Add vargas column if it doesn't exist
    c.execute("PRAGMA table_info(charts)")
    columns = [col[1] for col in c.fetchall()]
    if 'vargas' not in columns:
        c.execute('ALTER TABLE charts ADD COLUMN vargas TEXT')
    
    # Migration: Add planet_dignity column if it doesn't exist
    c.execute("PRAGMA table_info(charts)")
    columns = [col[1] for col in c.fetchall()]
    if 'planet_dignity' not in columns:
        c.execute('ALTER TABLE charts ADD COLUMN planet_dignity TEXT')
    
    # Migration: Add vimshottari_dasha column if it doesn't exist
    c.execute("PRAGMA table_info(charts)")
    columns = [col[1] for col in c.fetchall()]
    if 'vimshottari_dasha' not in columns:
        c.execute('ALTER TABLE charts ADD COLUMN vimshottari_dasha TEXT')
    
    conn.commit()
    conn.close()


def save_chart(name, dob, tob, timezone, place, lat, lon, dt_utc, ayanamsha=None, rasi_chart=None, retrograde_planets=None, vargas=None, planet_dignity=None, vimshottari_dasha=None):
    """Save a chart to the database (INSERT)."""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    c.execute('''
        INSERT INTO charts (name, dob, tob, timezone, place, latitude, longitude, dt_utc, ayanamsha, rasi_chart, retrograde_planets, vargas, planet_dignity, vimshottari_dasha)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        name, dob, tob, timezone, place, lat, lon, dt_utc,
        ayanamsha,
        json.dumps(rasi_chart) if rasi_chart else None,
        json.dumps(retrograde_planets) if retrograde_planets else None,
        json.dumps(vargas) if vargas else None,
        json.dumps(planet_dignity) if planet_dignity else None,
        json.dumps(vimshottari_dasha) if vimshottari_dasha else None
    ))
    
    chart_id = c.lastrowid
    conn.commit()
    conn.close()
    
    return chart_id


def update_chart(chart_id, name=None):
    """Update an existing chart in the database."""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    if name is not None:
        c.execute('''
            UPDATE charts SET name = ? WHERE id = ?
        ''', (name, chart_id))
    
    conn.commit()
    conn.close()


def get_all_charts():
    """Fetch all saved charts, ordered by creation date (newest first)."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    
    c.execute('''
        SELECT id, name, dob, tob, timezone, place, latitude, longitude, dt_utc, created_at
        FROM charts
        ORDER BY created_at DESC
    ''')
    
    rows = c.fetchall()
    conn.close()
    
    return [dict(row) for row in rows]


def get_chart(chart_id):
    """Fetch a specific chart by ID."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    
    c.execute('''
        SELECT * FROM charts WHERE id = ?
    ''', (chart_id,))
    
    row = c.fetchone()
    conn.close()
    
    if row:
        row_dict = dict(row)
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
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    c.execute('DELETE FROM charts WHERE id = ?', (chart_id,))
    
    conn.commit()
    conn.close()


def delete_all_charts():
    """Delete all charts from the database."""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    c.execute('DELETE FROM charts')
    count = c.rowcount
    
    conn.commit()
    conn.close()
    
    return count


def search_charts(query):
    """Search charts by name or place."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    
    search_term = f'%{query}%'
    c.execute('''
        SELECT id, name, dob, tob, timezone, place, latitude, longitude, dt_utc, created_at
        FROM charts
        WHERE name LIKE ? OR place LIKE ?
        ORDER BY created_at DESC
    ''', (search_term, search_term))
    
    rows = c.fetchall()
    conn.close()
    
    return [dict(row) for row in rows]
