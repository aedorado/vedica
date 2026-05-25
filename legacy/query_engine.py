"""
Query engine for astrological pattern matching.
Orchestrates parsing, evaluation, and database operations.
"""

import logging
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass

from query_parser import parse_query, CompoundCondition
from condition_evaluator import ConditionEvaluator
from db_adapter import DatabaseAdapter, ChartRecord
from config import QUERY_CONFIG

logger = logging.getLogger(__name__)
logger.setLevel(logging.WARNING)


@dataclass
class QueryResult:
    """Result of a pattern query"""
    chart_id: int
    raw_input: str
    person_name: Optional[str] = None
    birth_time: Optional[str] = None
    location: Optional[str] = None
    created_at: Optional[str] = None
    
    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return {
            'id': self.chart_id,
            'name': self.person_name,
            'raw_input': self.raw_input,
            'birth_time': self.birth_time,
            'location': self.location,
            'created_at': self.created_at,
        }
    
    def __repr__(self) -> str:
        name = self.person_name or "Unknown"
        return f"QueryResult(id={self.chart_id}, name='{name}')"


class QueryEngine:
    """Main query engine for astrological pattern matching"""
    
    def __init__(self, db_path: Optional[str] = None):
        """Initialize query engine with database"""
        self.db = DatabaseAdapter(db_path)
        self.query_cache: Dict = {}
    
    def search(
        self,
        pattern: str,
        limit: Optional[int] = None,
        offset: int = 0
    ) -> Tuple[List[QueryResult], int]:
        """
        Search for charts matching a pattern.
        
        Args:
            pattern: Query pattern string (e.g., "(Su 11H) AND (Ca Lagna)")
            limit: Maximum number of results (None = no limit)
            offset: Pagination offset
            
        Returns:
            Tuple of (matching_charts, total_count)
        """
        logger.info(f"Searching for pattern: {pattern}")
        
        # Parse the query
        try:
            parsed_query = parse_query(pattern)
            logger.debug(f"Parsed query: {parsed_query}")
        except Exception as e:
            logger.error(f"Failed to parse query: {e}")
            raise ValueError(f"Invalid pattern: {e}")
        
        # Load all charts from database
        all_charts, total_count = self.db.get_charts_by_criteria(
            limit=QUERY_CONFIG['max_results']
        )
        
        logger.info(f"Loaded {len(all_charts)} charts from database")
        
        # Filter charts matching the pattern
        matching_charts = []
        for chart in all_charts:
            if chart.planet_data and chart.house_data:
                try:
                    evaluator = ConditionEvaluator(chart.planet_data, chart.house_data)
                    if evaluator.evaluate(parsed_query):
                        matching_charts.append(QueryResult(
                            chart_id=chart.id,
                            raw_input=chart.raw_input,
                        ))
                except Exception as e:
                    logger.warning(f"Error evaluating chart {chart.id}: {e}")
        
        logger.info(f"Found {len(matching_charts)} matching charts")
        
        # Apply pagination
        paginated = matching_charts[offset:offset + (limit or len(matching_charts))]
        
        return paginated, len(matching_charts)
    
    def search_by_name(
        self,
        pattern: str,
        person_name: str,
        limit: Optional[int] = None
    ) -> List[QueryResult]:
        """
        Search for charts by person name matching a pattern.
        
        Args:
            pattern: Query pattern string
            person_name: Person's name to search for
            limit: Maximum results
            
        Returns:
            List of matching charts
        """
        logger.info(f"Searching for '{person_name}' with pattern: {pattern}")
        
        # Parse the query
        try:
            parsed_query = parse_query(pattern)
        except Exception as e:
            raise ValueError(f"Invalid pattern: {e}")
        
        # Load charts for specific person
        charts = self.db.get_charts_by_name(person_name)
        logger.info(f"Found {len(charts)} charts for {person_name}")
        
        # Filter matching pattern
        matching = []
        for chart in charts:
            if chart.planet_data and chart.house_data:
                try:
                    evaluator = ConditionEvaluator(chart.planet_data, chart.house_data)
                    if evaluator.evaluate(parsed_query):
                        matching.append(QueryResult(
                            chart_id=chart.id,
                            raw_input=chart.raw_input,
                        ))
                except Exception as e:
                    logger.warning(f"Error evaluating chart {chart.id}: {e}")
        
        logger.info(f"Found {len(matching)} matching charts for {person_name}")
        
        # Apply limit
        if limit:
            matching = matching[:limit]
        
        return matching
    
    def validate_pattern(self, pattern: str) -> bool:
        """
        Validate if a pattern is valid without searching.
        
        Args:
            pattern: Query pattern string
            
        Returns:
            True if valid, raises exception if invalid
        """
        try:
            parse_query(pattern)
            return True
        except Exception as e:
            logger.error(f"Invalid pattern: {e}")
            raise
    
    def get_pattern_info(self, pattern: str) -> Dict:
        """
        Get information about a parsed pattern (for debugging).
        
        Args:
            pattern: Query pattern string
            
        Returns:
            Dictionary with pattern info
        """
        parsed_query = parse_query(pattern)
        
        return {
            'pattern': pattern,
            'parsed': repr(parsed_query),
            'is_compound': parsed_query.simple_condition is None,
            'operator': parsed_query.operator.value if parsed_query.operator else None,
        }
    
    def list_all_charts(
        self,
        limit: Optional[int] = None,
        offset: int = 0
    ) -> Tuple[List[QueryResult], int]:
        """
        List all charts in database.
        
        Args:
            limit: Max results
            offset: Pagination offset
            
        Returns:
            Tuple of (charts, total_count)
        """
        charts, total_count = self.db.get_charts_by_criteria(
            limit=limit or QUERY_CONFIG['default_page_size'],
            offset=offset
        )
        
        results = [QueryResult(
            chart_id=c.id,
            raw_input=c.raw_input,
        ) for c in charts]
        
        return results, total_count
    
    def get_chart_details(self, chart_id: int) -> Optional[Dict]:
        """
        Get full details for a specific chart.
        
        Args:
            chart_id: Chart ID
            
        Returns:
            Chart details dictionary or None if not found
        """
        chart = self.db.get_chart_by_id(chart_id)
        
        if not chart:
            return None
        
        return {
            'id': chart.id,
            'name': chart.person_name,
            'raw_input': chart.raw_input,
            'birth_time': chart.birth_time,
            'location': chart.location,
            'created_at': chart.created_at,
            'planet_data': chart.planet_data,
            'house_data': chart.house_data,
        }
    
    def statistics(self) -> Dict:
        """
        Get database statistics.
        
        Returns:
            Dictionary with stats
        """
        total_charts = self.db.count_charts()
        
        return {
            'total_charts': total_charts,
            'database_path': self.db.db_path,
            'max_results_per_query': QUERY_CONFIG['max_results'],
        }


def create_engine(db_path: Optional[str] = None) -> QueryEngine:
    """Factory function to create a query engine"""
    return QueryEngine(db_path)
