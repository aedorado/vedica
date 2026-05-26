"""Initial schema - Create tables

Revision ID: 001_initial_schema
Revises: 
Create Date: 2026-05-25 00:00:00.000000

"""


def upgrade(op):
    """Apply initial schema."""
    # Create charts table
    op.execute('''
        CREATE TABLE IF NOT EXISTS charts (
            id SERIAL PRIMARY KEY,
            name TEXT NOT NULL,
            dob TEXT NOT NULL,
            tob TEXT NOT NULL,
            timezone TEXT NOT NULL,
            place TEXT,
            latitude FLOAT NOT NULL,
            longitude FLOAT NOT NULL,
            dt_utc TEXT NOT NULL,
            ayanamsha FLOAT,
            rasi_chart TEXT,
            retrograde_planets TEXT,
            vargas TEXT,
            planet_dignity TEXT,
            vimshottari_dasha TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Create analytics_cache table
    op.execute('''
        CREATE TABLE IF NOT EXISTS analytics_cache (
            id SERIAL PRIMARY KEY,
            key TEXT NOT NULL UNIQUE,
            count INTEGER DEFAULT 0,
            chart_ids TEXT,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Create analytics_metadata table
    op.execute('''
        CREATE TABLE IF NOT EXISTS analytics_metadata (
            key TEXT PRIMARY KEY,
            value TEXT
        )
    ''')


def downgrade(op):
    """Revert initial schema."""
    op.execute('DROP TABLE IF EXISTS analytics_metadata')
    op.execute('DROP TABLE IF EXISTS analytics_cache')
    op.execute('DROP TABLE IF EXISTS charts')
