"""
Migration management for PostgreSQL database.
Handles running migrations on startup (useful for Vercel/production).
"""

import os
from pathlib import Path
import psycopg
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

MIGRATIONS_DIR = Path(__file__).parent.parent / 'migrations' / 'versions'


class OpExecutor:
    """Simple executor for migration operations."""
    def __init__(self, cursor):
        self.cursor = cursor
    
    def execute(self, sql, *args):
        """Execute raw SQL."""
        self.cursor.execute(sql, args if args else None)


def run_migrations():
    """Run pending database migrations."""
    DATABASE_CONNECTION_STRING = os.getenv('DATABASE_CONNECTION_STRING', '')
    if not DATABASE_CONNECTION_STRING:
        print("⚠️  DATABASE_CONNECTION_STRING not set. Skipping migrations.")
        return False
    
    try:
        conn = psycopg.connect(DATABASE_CONNECTION_STRING)
        cursor = conn.cursor()
        
        # Create alembic_version table if it doesn't exist
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS alembic_version (
                version_num VARCHAR(32) NOT NULL PRIMARY KEY
            )
        ''')
        conn.commit()
        
        # Get applied migrations
        cursor.execute('SELECT version_num FROM alembic_version ORDER BY version_num')
        applied = set(row[0] for row in cursor.fetchall())
        
        # Find all migration files
        if not MIGRATIONS_DIR.exists():
            print("✅ Migrations directory exists but is empty - no migrations to apply")
            cursor.close()
            conn.close()
            return True
        
        migration_files = sorted([f for f in MIGRATIONS_DIR.glob('*.py') if f.name != '__init__.py'])
        
        if not migration_files:
            print("✅ No migration files found")
            cursor.close()
            conn.close()
            return True
        
        # Execute pending migrations
        pending_count = 0
        for migration_file in migration_files:
            # Extract revision ID from filename (e.g., "001_initial_schema.py" -> "001_initial_schema")
            revision_id = migration_file.stem
            
            if revision_id not in applied:
                print(f"  → Applying migration: {migration_file.name}")
                
                try:
                    # Load and execute migration
                    with open(migration_file, 'r') as f:
                        migration_code = f.read()
                    
                    # Execute migration code in a namespace with op executor
                    namespace = {'op': OpExecutor(cursor)}
                    exec(migration_code, namespace)
                    
                    # Call the upgrade function if it exists
                    if 'upgrade' in namespace:
                        namespace['upgrade'](OpExecutor(cursor))
                    
                    # Mark migration as applied
                    cursor.execute('INSERT INTO alembic_version (version_num) VALUES (%s)', (revision_id,))
                    conn.commit()
                    pending_count += 1
                
                except Exception as e:
                    conn.rollback()
                    print(f"  ✗ Migration {revision_id} failed: {e}")
                    raise
        
        cursor.close()
        conn.close()
        
        if pending_count == 0:
            print("✅ Database is up-to-date")
        else:
            print(f"✅ Applied {pending_count} migration(s)")
        
        return True
    
    except Exception as e:
        print(f"❌ Migration error: {e}")
        import traceback
        traceback.print_exc()
        return False
