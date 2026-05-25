import sqlite3
import hashlib
import json
import os


def init_cache_db(db_path='astro_cache.db'):
    """Initialize the SQLite cache database."""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS astro_cache (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            hash TEXT UNIQUE,
            raw_input TEXT,
            planet_data TEXT,
            house_data TEXT
        )
    ''')
    conn.commit()
    return conn


def generate_hash_from_input(raw_input: str) -> str:
    """
    Generate a SHA-256 hash using the raw input string.
    This ensures uniqueness based on the full original input.
    """
    return hashlib.sha256(raw_input.strip().encode('utf-8')).hexdigest()


def load_from_cache(conn, hash_key):
    """Try to load planetary and house data from the cache."""
    cursor = conn.cursor()
    cursor.execute('SELECT planet_data, house_data FROM astro_cache WHERE hash=?', (hash_key,))
    row = cursor.fetchone()
    if row:
        try:
            return json.loads(row[0]), json.loads(row[1])
        except json.JSONDecodeError:
            return None, None
    return None, None


def save_to_cache(conn, hash_key, raw_input, planet_data, house_data):
    """Save planetary and house data along with raw input to the cache."""
    cursor = conn.cursor()
    cursor.execute('''
        INSERT OR REPLACE INTO astro_cache (hash, raw_input, planet_data, house_data)
        VALUES (?, ?, ?, ?)
    ''', (hash_key, raw_input, json.dumps(planet_data), json.dumps(house_data)))
    conn.commit()

def load_raw_input_by_id(conn, user_id: int) -> str:
    """
    Load raw_input string from the astro_cache table by its integer ID.
    Returns the raw_input string if found, else raises ValueError.
    """
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT planet_data, house_data, raw_input FROM astro_cache WHERE id = ?", (user_id,))
        row = cursor.fetchone()
        if row:
            return row
        else:
            raise ValueError(f"No record found for id {user_id}")
    except sqlite3.Error as db_err:
        raise RuntimeError(f"Database error: {db_err}")

