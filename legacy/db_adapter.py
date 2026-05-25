"""
Database adapter layer for astro_cache.
Provides clean interface for all database operations.
Separates schema management from business logic.
"""

import sqlite3
import hashlib
import json
import logging
from typing import Optional, List, Dict, Tuple
from dataclasses import dataclass
from datetime import datetime

from config import DATABASE_CONFIG, DB_TABLES

logger = logging.getLogger(__name__)


@dataclass
class ChartRecord:
    """Represents a single chart record from database"""
    id: int
    hash: str
    raw_input: str
    person_name: Optional[str] = None
    birth_time: Optional[str] = None
    location: Optional[str] = None
    planet_data: Optional[Dict] = None
    house_data: Optional[Dict] = None
    created_at: Optional[str] = None
    
    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return {
            'id': self.id,
            'hash': self.hash,
            'raw_input': self.raw_input,
            'person_name': self.person_name,
            'birth_time': self.birth_time,
            'location': self.location,
            'planet_data': self.planet_data,
            'house_data': self.house_data,
            'created_at': self.created_at,
        }


class DatabaseAdapter:
    """Clean database adapter for astro_cache operations"""
    
    def __init__(self, db_path: Optional[str] = None):
        """Initialize adapter with database path"""
        self.db_path = db_path or DATABASE_CONFIG['path']
        self.table_name = DB_TABLES['cache']
        self._ensure_connected()
    
    def _ensure_connected(self):
        """Verify database is accessible"""
        try:
            conn = sqlite3.connect(self.db_path)
            conn.close()
            logger.debug(f"Database connection verified: {self.db_path}")
        except Exception as e:
            logger.error(f"Failed to connect to database: {e}")
            raise
    
    def init_db(self) -> sqlite3.Connection:
        """Initialize the database schema (create tables if needed)"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Check if table exists
        cursor.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name=?", (self.table_name,))
        table_exists = cursor.fetchone() is not None
        
        if not table_exists:
            # Create new table with full schema
            cursor.execute(f'''
                CREATE TABLE IF NOT EXISTS {self.table_name} (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    hash TEXT UNIQUE NOT NULL,
                    raw_input TEXT NOT NULL,
                    person_name TEXT,
                    birth_time TEXT,
                    location TEXT,
                    planet_data TEXT,
                    house_data TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
        else:
            # Migrate existing table: add missing columns
            cursor.execute(f"PRAGMA table_info({self.table_name})")
            existing_columns = {row[1] for row in cursor.fetchall()}
            
            columns_to_add = {
                'person_name': 'TEXT',
                'birth_time': 'TEXT',
                'location': 'TEXT',
                'created_at': "TIMESTAMP DEFAULT CURRENT_TIMESTAMP",
                'updated_at': "TIMESTAMP DEFAULT CURRENT_TIMESTAMP",
            }
            
            for col_name, col_type in columns_to_add.items():
                if col_name not in existing_columns:
                    cursor.execute(f'ALTER TABLE {self.table_name} ADD COLUMN {col_name} {col_type}')
                    logger.info(f"Added column {col_name} to existing table")
        
        # Create indexes for common queries
        cursor.execute(f'''
            CREATE INDEX IF NOT EXISTS idx_hash 
            ON {self.table_name}(hash)
        ''')
        cursor.execute(f'''
            CREATE INDEX IF NOT EXISTS idx_person_name 
            ON {self.table_name}(person_name)
        ''')
        cursor.execute(f'''
            CREATE INDEX IF NOT EXISTS idx_created_at 
            ON {self.table_name}(created_at)
        ''')
        
        conn.commit()
        logger.info(f"Database initialized: {self.db_path}")
        return conn
    
    def get_connection(self) -> sqlite3.Connection:
        """Get a fresh database connection"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row  # Enable column access by name
        return conn
    
    @staticmethod
    def generate_hash(raw_input: str) -> str:
        """Generate SHA-256 hash from input string"""
        return hashlib.sha256(raw_input.strip().encode('utf-8')).hexdigest()
    
    def insert_chart(
        self,
        raw_input: str,
        planet_data: Dict,
        house_data: Dict,
        person_name: Optional[str] = None,
        birth_time: Optional[str] = None,
        location: Optional[str] = None
    ) -> int:
        """Insert a new chart record into database"""
        hash_key = self.generate_hash(raw_input)
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute(f'''
                INSERT OR REPLACE INTO {self.table_name}
                (hash, raw_input, person_name, birth_time, location, planet_data, house_data)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                hash_key,
                raw_input,
                person_name,
                birth_time,
                location,
                json.dumps(planet_data),
                json.dumps(house_data)
            ))
            conn.commit()
            record_id = cursor.lastrowid
            logger.info(f"Chart inserted with ID: {record_id}")
            return record_id
        finally:
            conn.close()
    
    def get_chart_by_id(self, chart_id: int) -> Optional[ChartRecord]:
        """Fetch chart by ID"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute(f'SELECT * FROM {self.table_name} WHERE id = ?', (chart_id,))
            row = cursor.fetchone()
            
            if not row:
                return None
            
            return ChartRecord(
                id=row['id'],
                hash=row['hash'],
                raw_input=row['raw_input'],
                planet_data=json.loads(row['planet_data']) if row['planet_data'] else None,
                house_data=json.loads(row['house_data']) if row['house_data'] else None,
            )
        finally:
            conn.close()
    
    def get_chart_by_hash(self, hash_key: str) -> Optional[ChartRecord]:
        """Fetch chart by hash"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute(f'SELECT * FROM {self.table_name} WHERE hash = ?', (hash_key,))
            row = cursor.fetchone()
            
            if not row:
                return None
            
            return ChartRecord(
                id=row['id'],
                hash=row['hash'],
                raw_input=row['raw_input'],
                planet_data=json.loads(row['planet_data']) if row['planet_data'] else None,
                house_data=json.loads(row['house_data']) if row['house_data'] else None,
            )
        finally:
            conn.close()
    
    def get_charts_by_name(self, person_name: str) -> List[ChartRecord]:
        """Fetch all charts for a person by name"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute(
                f'SELECT * FROM {self.table_name} WHERE person_name = ? ORDER BY id DESC',
                (person_name,)
            )
            rows = cursor.fetchall()
            
            return [ChartRecord(
                id=row['id'],
                hash=row['hash'],
                raw_input=row['raw_input'],
                planet_data=json.loads(row['planet_data']) if row['planet_data'] else None,
                house_data=json.loads(row['house_data']) if row['house_data'] else None,
            ) for row in rows]
        finally:
            conn.close()
    
    def get_all_charts(self, limit: Optional[int] = None) -> List[ChartRecord]:
        """Fetch all charts from database"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            if limit:
                query = f'SELECT * FROM {self.table_name} LIMIT ?'
                cursor.execute(query, (limit,))
            else:
                query = f'SELECT * FROM {self.table_name}'
                cursor.execute(query)
            
            rows = cursor.fetchall()
            
            return [ChartRecord(
                id=row['id'],
                hash=row['hash'],
                raw_input=row['raw_input'],
                planet_data=json.loads(row['planet_data']) if row['planet_data'] else None,
                house_data=json.loads(row['house_data']) if row['house_data'] else None,
            ) for row in rows]
        finally:
            conn.close()
    
    def chart_exists(self, hash_key: str) -> bool:
        """Check if a chart with given hash exists"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute(
                f'SELECT 1 FROM {self.table_name} WHERE hash = ? LIMIT 1',
                (hash_key,)
            )
            return cursor.fetchone() is not None
        finally:
            conn.close()
    
    def count_charts(self) -> int:
        """Get total number of charts in database"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute(f'SELECT COUNT(*) FROM {self.table_name}')
            return cursor.fetchone()[0]
        finally:
            conn.close()
    
    def update_chart_metadata(
        self,
        chart_id: int,
        person_name: Optional[str] = None,
        birth_time: Optional[str] = None,
        location: Optional[str] = None
    ) -> bool:
        """Update metadata for a chart"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            updates = []
            params = []
            
            if person_name is not None:
                updates.append('person_name = ?')
                params.append(person_name)
            if birth_time is not None:
                updates.append('birth_time = ?')
                params.append(birth_time)
            if location is not None:
                updates.append('location = ?')
                params.append(location)
            
            if not updates:
                return False
            
            updates.append('updated_at = CURRENT_TIMESTAMP')
            params.append(chart_id)
            
            query = f'UPDATE {self.table_name} SET {", ".join(updates)} WHERE id = ?'
            cursor.execute(query, params)
            conn.commit()
            
            return cursor.rowcount > 0
        finally:
            conn.close()
    
    def delete_chart(self, chart_id: int) -> bool:
        """Delete a chart record"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute(f'DELETE FROM {self.table_name} WHERE id = ?', (chart_id,))
            conn.commit()
            return cursor.rowcount > 0
        finally:
            conn.close()
    
    def get_charts_by_criteria(
        self,
        limit: int = 50,
        offset: int = 0,
        order_by: str = 'id DESC'
    ) -> Tuple[List[ChartRecord], int]:
        """
        Fetch charts with pagination.
        Returns tuple of (charts, total_count)
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            # Get total count
            cursor.execute(f'SELECT COUNT(*) FROM {self.table_name}')
            total_count = cursor.fetchone()[0]
            
            # Fetch paginated results
            query = f'SELECT * FROM {self.table_name} ORDER BY {order_by} LIMIT ? OFFSET ?'
            cursor.execute(query, (limit, offset))
            rows = cursor.fetchall()
            
            charts = [ChartRecord(
                id=row['id'],
                hash=row['hash'],
                raw_input=row['raw_input'],
                planet_data=json.loads(row['planet_data']) if row['planet_data'] else None,
                house_data=json.loads(row['house_data']) if row['house_data'] else None,
            ) for row in rows]
            
            return charts, total_count
        finally:
            conn.close()
