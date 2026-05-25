# Vedica Architecture Guide

A comprehensive guide to the design and structure of the Vedic Astrology Chart Analysis System.

## Overview

**Vedica** is a modular system for analyzing Vedic astrology charts with support for:
- Pattern-based chart queries using human-readable syntax
- Comprehensive astrological analysis (yogas, doshas, dasha periods)
- Efficient caching and database storage
- Interactive CLI and programmatic access

## Core Principles

1. **Modularity**: Each component has a single, well-defined responsibility
2. **Separation of Concerns**: Business logic separated from data access and presentation
3. **Extensibility**: New analyzers and detectors can be added without modifying core code
4. **Testability**: Clean interfaces enable easy unit testing
5. **Documentation**: Self-documenting code with clear patterns and conventions

---

## Architecture Layers

### Layer 1: Configuration & Constants (`config.py`)

**Purpose**: Centralized management of all constants, abbreviations, and settings.

**Key Components**:
- Planet names and abbreviations (Su, Mo, Ma, Me, Ju, Ve, Sa, Ra, Ke)
- Zodiac signs and abbreviations (Ar, Ta, Ge, Ca, Le, Vi, Li, Sc, Sa, Cp, Aq, Pi)
- House definitions and categories (Kendra, Trikona, Upachaya, Dusthana, Maraka)
- Database configuration
- Query engine settings

**Usage Pattern**:
```python
from config import normalize_planet, normalize_zodiac, HOUSE_CATEGORIES
planet = normalize_planet("Su")  # Returns "Sun"
zodiac = normalize_zodiac("Ca")  # Returns "Cancer"
```

**Benefits**:
- Single source of truth for all constants
- Easy to update abbreviations or add new planets
- Enables consistent normalization across the system

---

### Layer 2: Data Access (`db_adapter.py`)

**Purpose**: Clean database interface abstracting SQLite details from business logic.

**Key Components**:
- `DatabaseAdapter`: Main adapter class
- `ChartRecord`: Dataclass representing a chart from database

**Core Responsibilities**:
1. Database initialization and schema management
2. CRUD operations (Create, Read, Update, Delete)
3. Query builders for common patterns
4. Connection pooling and management

**Public Interface**:
```python
adapter = DatabaseAdapter()
chart = adapter.get_chart_by_id(1)
charts = adapter.get_all_charts(limit=50)
charts_by_name = adapter.get_charts_by_name("John Doe")
```

**Schema**:
```
astro_cache table:
├── id (PK)
├── hash (unique)
├── raw_input
├── person_name
├── birth_time
├── location
├── planet_data (JSON)
├── house_data (JSON)
├── created_at
└── updated_at
```

**Indexes**:
- `idx_hash`: For fast cache lookups
- `idx_person_name`: For filtering by person
- `idx_created_at`: For sorting and range queries

---

### Layer 3: Query Language (`query_parser.py`)

**Purpose**: Parse human-readable astrological patterns into an AST (Abstract Syntax Tree).

**Supported Pattern Syntax**:
```
(Su 11H)                          # Planet in House
(Ca Lagna)                        # Zodiac in Lagna
(Su 11H) AND (Ca Lagna)          # Compound with AND
(Mo 2H) OR (Le Lagna)            # Compound with OR
(Su Ca) AND (Mo Le)              # Planet in Zodiac Sign
(Su Kendra) OR (Mo Trikona)      # Planet in House Category
```

**Key Components**:
- `QueryParser`: Main parser with tokenization and AST building
- `Condition`: Simple condition (e.g., "Su 11H")
- `CompoundCondition`: Compound conditions with operators
- `ConditionType`: Enum of condition types

**Parsing Flow**:
```
Input String
    ↓
Tokenization (regex split)
    ↓
Recursive descent parser
├── Parse OR expressions (lowest precedence)
├── Parse AND expressions (higher precedence)
└── Parse primary conditions (atoms)
    ↓
AST (CompoundCondition tree)
```

**Usage**:
```python
from query_parser import parse_query
ast = parse_query("(Su 11H) AND (Ca Lagna)")
# Returns CompoundCondition with nested structure
```

**Precedence**: AND binds tighter than OR (standard precedence)

---

### Layer 4: Condition Evaluation (`condition_evaluator.py`)

**Purpose**: Evaluate whether a chart matches specific conditions.

**Key Components**:
- `ConditionEvaluator`: Main evaluator class
- Condition type evaluators (private methods)

**Supported Condition Types**:
1. `PLANET_IN_HOUSE`: Check if planet is in specific house
2. `ZODIAC_IN_HOUSE`: Check if zodiac sign is in house
3. `LAGNA_SIGN`: Check if lagna (1st house) is in sign
4. `PLANET_SIGN`: Check if planet is in zodiac sign
5. `HOUSE_CATEGORY`: Check if planet is in house category

**Data Extraction Strategy**:
- Flexible field name detection (handles variations in source data)
- Nested dictionary navigation for sign information
- List parsing for planets in houses

**Evaluation Logic**:
```python
evaluator = ConditionEvaluator(planet_data, house_data)
result = evaluator.evaluate(parsed_query)  # Returns True/False
```

**Error Handling**:
- Graceful degradation if fields missing
- Warning logs for debugging
- Returns False on evaluation errors (conservative approach)

---

### Layer 5: Query Engine (`query_engine.py`)

**Purpose**: Orchestrate parsing, evaluation, and database operations.

**Key Components**:
- `QueryEngine`: Main orchestrator
- `QueryResult`: Result dataclass

**Core Capabilities**:
1. `search(pattern)`: Search all charts for pattern matches
2. `search_by_name(pattern, person_name)`: Search specific person
3. `validate_pattern(pattern)`: Validate without searching
4. `list_all_charts()`: List all charts with pagination
5. `get_chart_details(chart_id)`: Get full chart data
6. `statistics()`: Database stats

**Search Flow**:
```
Pattern String
    ↓
Parse (query_parser)
    ↓
Load charts from DB (db_adapter)
    ↓
For each chart:
├── Create evaluator (condition_evaluator)
├── Evaluate condition
└── Add to results if match
    ↓
Return paginated results
```

**Performance Characteristics**:
- O(n) in number of charts (full scan, but can be optimized)
- Caching available for repeated patterns
- Pagination support for large result sets

**Usage**:
```python
engine = create_engine()
results, total = engine.search("(Su 11H) AND (Ca Lagna)")
for result in results:
    print(f"ID: {result.chart_id}, Name: {result.person_name}")
```

---

### Layer 6: Command-Line Interface (`cli.py`)

**Purpose**: User-friendly interactive and batch query interface.

**Available Commands**:
- `search <pattern>`: Search for charts
- `list [limit]`: List all charts
- `info <chart_id>`: Show chart details
- `validate <pattern>`: Validate pattern syntax
- `pattern-info <pattern>`: Debug parsed pattern structure
- `stats`: Show database statistics
- `help`: Show help

**Interface Modes**:
1. **Interactive**: `python cli.py` → REPL
2. **Batch**: `python cli.py search "(Su 11H)"` → execute and exit

**Key Features**:
- Tabular output formatting
- Color-coded error/success messages
- Pagination support
- Pattern validation before search
- Debug information for pattern analysis

---

## System Integration Map

```
┌─────────────────────────────────────────────────────────────────┐
│                     CLI Layer (cli.py)                          │
│              (Interactive and batch commands)                   │
└────────────────────────────┬────────────────────────────────────┘
                             │
┌────────────────────────────▼────────────────────────────────────┐
│                 Query Engine (query_engine.py)                  │
│       (Orchestration and search logic)                          │
└──────────────────────┬──────────────────────┬──────────────────┘
                       │                      │
        ┌──────────────▼──────┐    ┌──────────▼────────────┐
        │                     │    │                       │
    ┌───▼──────────────┐  ┌───▼───┴─────────────┐   ┌─────▼──────────────┐
    │ Query Parser     │  │ Condition Evaluator │   │ Database Adapter   │
    │ (query_parser)   │  │(condition_evaluator)│   │  (db_adapter.py)   │
    └───┬──────────────┘  └─────────────────────┘   └────────┬──────────┘
        │                                                   │
        │                                            ┌──────▼──────────┐
        │                                            │ SQLite Database  │
        │                                            │ (astro_cache.db) │
        │                                            └──────────────────┘
        │
    ┌───▼──────────────────────────────────────────┐
    │ Configuration & Constants (config.py)        │
    │ • Planet names & abbreviations               │
    │ • Zodiac signs & abbreviations               │
    │ • House categories                           │
    └────────────────────────────────────────────┘
```

---

## Data Flow Examples

### Example 1: Simple Query "(Su 11H)"

```
1. CLI: search (Su 11H)
   ↓
2. QueryEngine.search("(Su 11H)")
   ├─ query_parser.parse("(Su 11H)")
   │  └─ Returns: CompoundCondition(
   │        simple_condition=Condition(
   │          type=PLANET_IN_HOUSE,
   │          primary="Sun",
   │          secondary="11"
   │        )
   │      )
   │
   ├─ db_adapter.get_all_charts()
   │  └─ Returns: [ChartRecord(...), ChartRecord(...), ...]
   │
   └─ For each chart:
      ├─ condition_evaluator.evaluate(parsed_query)
      │  └─ Returns: True if Sun is in 11th house, else False
      │
      └─ Add to results if True
   
   ↓
3. Return matching results with ID and name
```

### Example 2: Compound Query "(Su 11H) AND (Ca Lagna)"

```
1. Query: (Su 11H) AND (Ca Lagna)
   ↓
2. Parser builds AST:
   CompoundCondition(
     operator=AND,
     conditions=[
       CompoundCondition(
         simple_condition=Condition(PLANET_IN_HOUSE, "Sun", "11")
       ),
       CompoundCondition(
         simple_condition=Condition(LAGNA_SIGN, "Cancer", "Lagna")
       )
     ]
   )
   ↓
3. Evaluator recursively evaluates:
   ├─ Evaluate left: Sun in 11H → True/False
   ├─ Evaluate right: Lagna is Cancer → True/False
   └─ Return: left AND right
   ↓
4. Only return charts where BOTH conditions are true
```

---

## Extension Points

### Adding New Planets
1. Update `config.py`: Add to `PLANETS` set and `PLANET_ABBREVIATIONS` dict
2. No other changes needed (system uses config)

### Adding New Zodiac Signs
1. Update `config.py`: Add to `ZODIAC_SIGNS` and `ZODIAC_ABBREVIATIONS`
2. No other changes needed

### Adding New Condition Types
1. Add to `ConditionType` enum in `query_parser.py`
2. Add parsing logic in `QueryParser._classify_condition()`
3. Add evaluation logic in `ConditionEvaluator._evaluate_simple()`
4. Test with CLI: `validate <pattern>`

### Adding New Analyzers
1. Create new class inheriting from base analyzer
2. Implement analysis logic
3. Register in `main.py` (or create new orchestrator)
4. No need to modify core query system

---

## Testing Strategy

### Unit Tests Needed:
- `test_config.py`: Normalization functions
- `test_query_parser.py`: Parser with various patterns
- `test_condition_evaluator.py`: Evaluation with mock data
- `test_db_adapter.py`: CRUD operations
- `test_query_engine.py`: Integration tests

### Test Data:
- Sample planet_data/house_data JSON structures
- Fixture charts with known characteristics
- Edge cases (missing fields, malformed data)

---

## Performance Considerations

### Current Limitations:
- O(n) search (loads all charts, evaluates each)
- No full-text search on planet data

### Optimization Opportunities:
1. **Indexed Storage**: Pre-compute and store condition results
   - Create `chart_properties` table with precomputed fields
   - Example: `planet_houses`, `zodiac_in_houses`, `lagna_sign`
   
2. **Query Optimization**: Rewrite queries to SQL
   - Complex parser → SQL WHERE clauses
   - Orders of magnitude faster for large datasets
   
3. **Caching**: Store search results by pattern
   - Enabled via `QUERY_CONFIG['enable_caching']`
   - Invalidate on new inserts

### Scalability:
- Current design supports ~10,000 charts efficiently
- Beyond that, requires optimization above

---

## Dependencies

**External Libraries**:
- `vedastro`: Astrological calculations (core dependency)
- `tabulate`: Table formatting for CLI output
- `sqlite3`: Database (standard library)

**Internal Modules**:
- See system integration map above

---

## File Organization

```
vedica/
├── config.py                  # Constants & settings
├── db_adapter.py              # Database layer
├── query_parser.py            # Query parsing
├── condition_evaluator.py     # Condition evaluation
├── query_engine.py            # Orchestration
├── cli.py                     # Command-line interface
├── ARCHITECTURE.md            # This file
├── AGENTS.md                  # Agent descriptions
│
├── main.py                    # Original entry point (legacy)
├── input_parser.py            # Input parsing
├── get_data.py                # Data fetching
├── utils.py                   # Utilities
├── extractors.py              # Data extraction
│
├── models/                    # Data models
│   ├── common.py
│   ├── planet_detail.py
│   └── house_detail.py
│
├── analyzer/                  # Astrological analyzers
│   ├── bphs_house_analyzer.py
│   ├── lagna_analyzer.py
│   ├── planet_analyzer.py
│   ├── planet_strength.py
│   ├── varga.py
│   └── astro_table.py
│
├── yoga_detector/             # Yoga detection
│   ├── vedic_yoga_detector.py
│   ├── raja_yoga_detector.py
│   ├── dhan_yoga_detector.py
│   ├── malika_yogas_detector.py
│   └── ...
│
├── curses/                    # Curse/dosha detection
│   ├── curse_detector.py
│   ├── snake_curse_detector.py
│   └── ...
│
├── dasha/                     # Dasha period calculations
│   └── vimshottari.py
│
├── parsers/                   # Data parsers
│   ├── planet_data_parser.py
│   └── house_data_parser.py
│
├── ashtakvarga/               # Ashtakvarga analysis
│   └── ashtakvarga.py
│
├── astro_cache.db             # SQLite database
└── myenv/                     # Virtual environment
```

---

## Future Enhancements

1. **Web API**: FastAPI wrapper around query_engine
2. **Advanced Filtering**: Numeric filters (e.g., "Sun with 20+ degrees")
3. **Chart Comparison**: Find similar charts
4. **Yoga Detection Integration**: Query by yoga types
5. **Export Formats**: JSON, CSV, PDF reports
6. **User Management**: Multiple users, private charts
7. **Async Processing**: Background chart analysis
8. **Visualization**: Chart diagrams and dashboards

---

## Glossary

- **AST**: Abstract Syntax Tree - tree representation of parsed query
- **Condition**: Single astrological condition (e.g., "Sun in 11H")
- **Lagna**: 1st house, represents self in Vedic astrology
- **Rashi**: Zodiac sign
- **House**: One of 12 divisions in the chart
- **Dasha**: Time period system in Vedic astrology
- **Yoga**: Auspicious or challenging planetary combination
- **Dosha**: Planetary affliction or curse

---

**Last Updated**: May 2026  
**Version**: 1.0
