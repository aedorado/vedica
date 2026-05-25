"""
Query parser for astrological pattern matching.
Parses expressions like:
  - (Su 11H) AND (Ca Lagna)
  - (Mo 2H) OR (Le Lagna)
  - (Aq 5H) AND (Ra 8H)
"""

import re
import logging
from dataclasses import dataclass, field
from typing import List, Union, Optional
from enum import Enum

from config import normalize_planet, normalize_zodiac, HOUSES

logger = logging.getLogger(__name__)
logger.setLevel(logging.WARNING)


class OperatorType(Enum):
    """Logical operators"""
    AND = "AND"
    OR = "OR"


class ConditionType(Enum):
    """Types of conditions we can query"""
    PLANET_IN_HOUSE = "PLANET_IN_HOUSE"      # Su 11H
    ZODIAC_IN_HOUSE = "ZODIAC_IN_HOUSE"      # Ca 11H
    LAGNA_SIGN = "LAGNA_SIGN"                # Ca Lagna
    PLANET_SIGN = "PLANET_SIGN"              # Su Ca (planet in sign)
    HOUSE_CATEGORY = "HOUSE_CATEGORY"        # Su Kendra


@dataclass
class Condition:
    """Represents a single condition in the query"""
    type: ConditionType
    primary: str  # Planet or Zodiac
    secondary: str  # House number, House name (Lagna), or Zodiac
    
    def __repr__(self) -> str:
        return f"Condition({self.type.name}, {self.primary}, {self.secondary})"


@dataclass
class CompoundCondition:
    """Represents a compound condition (multiple conditions with AND/OR)"""
    conditions: List['CompoundCondition'] = field(default_factory=list)  # Can be nested
    operator: Optional[OperatorType] = None
    simple_condition: Optional[Condition] = None
    
    def __repr__(self) -> str:
        if self.simple_condition:
            return repr(self.simple_condition)
        op = self.operator.value if self.operator else "?"
        conds = " ".join([repr(c) for c in self.conditions])
        return f"({conds} {op})"


class QueryParser:
    """Parser for astrological query patterns"""
    
    # Tokenization patterns (exclude parens from \S+ to handle them separately)
    TOKEN_PATTERN = r'\(|\)|AND|OR|[^\s\(\)]+'
    
    def __init__(self):
        self.tokens: List[str] = []
        self.pos = 0
    
    def parse(self, query: str) -> CompoundCondition:
        """
        Parse a query string and return a CompoundCondition AST.
        
        Examples:
            - "(Su 11H)" -> Single condition
            - "(Su 11H) AND (Ca Lagna)" -> Two conditions with AND
            - "(Su 11H) OR (Mo 2H) AND (Le Lagna)" -> Multiple with OR/AND
        """
        self._tokenize(query)
        self.pos = 0
        
        if not self.tokens:
            raise ValueError("Empty query")
        
        result = self._parse_or_expression()
        
        if self.pos < len(self.tokens):
            raise ValueError(f"Unexpected tokens at position {self.pos}")
        
        return result
    
    def _tokenize(self, query: str) -> None:
        """Tokenize the query string"""
        self.tokens = re.findall(self.TOKEN_PATTERN, query)
        logger.debug(f"Tokens: {self.tokens}")
    
    def _current_token(self) -> Optional[str]:
        """Peek at current token without consuming"""
        if self.pos < len(self.tokens):
            return self.tokens[self.pos]
        return None
    
    def _consume_token(self) -> Optional[str]:
        """Get and consume current token"""
        token = self._current_token()
        if token is not None:
            self.pos += 1
        return token
    
    def _parse_or_expression(self) -> CompoundCondition:
        """Parse OR expression (lowest precedence)"""
        left = self._parse_and_expression()
        
        while self._current_token() == "OR":
            self._consume_token()  # consume OR
            right = self._parse_and_expression()
            left = CompoundCondition(
                conditions=[left, right],
                operator=OperatorType.OR
            )
        
        return left
    
    def _parse_and_expression(self) -> CompoundCondition:
        """Parse AND expression (higher precedence than OR)"""
        left = self._parse_primary()
        
        while self._current_token() == "AND":
            self._consume_token()  # consume AND
            right = self._parse_primary()
            left = CompoundCondition(
                conditions=[left, right],
                operator=OperatorType.AND
            )
        
        return left
    
    def _parse_primary(self) -> CompoundCondition:
        """Parse primary condition (parenthesized or atom)"""
        token = self._current_token()
        
        if token == "(":
            self._consume_token()  # consume (
            result = self._parse_or_expression()  # recurse
            
            if self._current_token() != ")":
                raise ValueError(f"Expected ), got {self._current_token()}")
            self._consume_token()  # consume )
            
            return result
        else:
            # Parse single condition
            condition = self._parse_condition()
            return CompoundCondition(simple_condition=condition)
    
    def _parse_condition(self) -> Condition:
        """Parse a single condition like 'Su 11H' or 'Ca Lagna'"""
        tokens = []
        
        # Collect tokens until we hit operator or end
        while (self.pos < len(self.tokens) and 
               self._current_token() not in ("AND", "OR", ")", None)):
            tokens.append(self._consume_token())
        
        if len(tokens) < 2:
            raise ValueError(f"Incomplete condition: {tokens}")
        
        primary = tokens[0]
        secondary = tokens[1]
        
        # Determine condition type
        condition_type, primary_normalized, secondary_normalized = \
            self._classify_condition(primary, secondary)
        
        return Condition(
            type=condition_type,
            primary=primary_normalized,
            secondary=secondary_normalized
        )
    
    def _classify_condition(self, primary: str, secondary: str) -> tuple:
        """
        Classify the condition and normalize values.
        Returns (ConditionType, normalized_primary, normalized_secondary)
        """
        # Normalize case for comparison
        secondary_upper = secondary.upper()
        
        # Check if secondary is "Lagna"
        if secondary_upper == "LAGNA":
            # Primary must be zodiac (e.g., "Ca Lagna")
            zodiac = normalize_zodiac(primary)
            return ConditionType.LAGNA_SIGN, zodiac, "Lagna"
        
        # Check if secondary is house number + H (e.g., "11H")
        if secondary_upper.endswith("H"):
            house_str = secondary[:-1]
            if house_str.isdigit():
                house_num = int(house_str)
                if house_num not in HOUSES:
                    raise ValueError(f"Invalid house: {house_num}")
                
                # Check if primary is planet or zodiac
                try:
                    planet = normalize_planet(primary)
                    return (ConditionType.PLANET_IN_HOUSE, planet, str(house_num))
                except ValueError:
                    pass
                
                try:
                    zodiac = normalize_zodiac(primary)
                    return (ConditionType.ZODIAC_IN_HOUSE, zodiac, str(house_num))
                except ValueError:
                    pass
                
                raise ValueError(f"Unknown primary '{primary}' for house condition")
        
        # Check if secondary is zodiac (e.g., "Su Ca" = Sun in Cancer)
        try:
            planet = normalize_planet(primary)
            zodiac = normalize_zodiac(secondary)
            return ConditionType.PLANET_SIGN, planet, zodiac
        except ValueError:
            pass
        
        # Check if secondary is house category (e.g., "Su Kendra")
        categories = ["kendra", "trikona", "upachaya", "dusthana", "maraka", "favorable"]
        if secondary_upper.lower() in categories:
            try:
                planet = normalize_planet(primary)
                return (ConditionType.HOUSE_CATEGORY, planet, secondary.lower())
            except ValueError:
                pass
        
        raise ValueError(
            f"Cannot classify condition: '{primary} {secondary}'. "
            "Expected formats: 'Planet House#' (e.g., Su 11H), "
            "'Zodiac Lagna', 'Planet Sign', or 'Planet Category'"
        )


def parse_query(query: str) -> CompoundCondition:
    """Convenience function to parse a query string"""
    parser = QueryParser()
    return parser.parse(query)


if __name__ == "__main__":
    # Test cases
    test_queries = [
        "(Su 11H)",
        "(Ca Lagna)",
        "(Su 11H) AND (Ca Lagna)",
        "(Mo 2H) OR (Le Lagna)",
        "(Aq 5H) AND (Ra 8H)",
        "(Su Ca) AND (Mo Le)",
        "(Su Kendra) OR (Mo Trikona)",
    ]
    
    for query in test_queries:
        try:
            result = parse_query(query)
            print(f"✅ {query}")
            print(f"   → {result}\n")
        except Exception as e:
            print(f"❌ {query}")
            print(f"   → {e}\n")
