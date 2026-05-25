# Vedica Agents Guide

This document describes the specialized agents (analyzers, detectors, calculators) that perform astrological analysis in the Vedica system.

## What is an Agent?

In Vedica, an **Agent** is a specialized module that:
- Analyzes specific aspects of an astrological chart
- Operates independently but can coordinate with other agents
- Produces structured output/insights
- Can be composed with other agents for complex analysis

Agents can be thought of as specialized domain experts that focus on a specific area of astrology.

---

## Agent Categories

### 1. Analysis Agents (analyzer/ directory)

These agents perform detailed astrological analysis.

#### **LagnaAnalyzer** (`analyzer/lagna_analyzer.py`)
- **Purpose**: Comprehensive 1st house and Lagna analysis
- **Responsibility**: Evaluates Lagna strength, planetary placements in Lagna, aspects
- **Input**: `planet_objects`, `house_objects` (ChartData)
- **Output**: Lagna strength analysis, benefic/malefic influences
- **Key Methods**: 
  - `analyze_lagna_strength()` - Rate Lagna strength (weak/moderate/strong)
  - `analyze_lagna_placements()` - Planets in Lagna and their effects
  - `analyze_lagna_aspects()` - Aspects to Lagna

#### **BPHSHouseAnalyzer** (`analyzer/bphs_house_analyzer.py`)
- **Purpose**: House analysis based on BPHS (Brihat Parashara Hora Shastra)
- **Responsibility**: Analyze each house's significations, planetary effects, and results
- **Input**: `planet_objects`, `house_objects`
- **Output**: House-by-house analysis report
- **House Categories Recognized**:
  - Kendra: 1, 4, 7, 10 (Angular, powerful)
  - Trikona: 1, 5, 9 (Triangular, most auspicious)
  - Upachaya: 3, 6, 10, 11 (Growth houses)
  - Dusthana: 6, 8, 12 (Difficult houses)
  - Maraka: 2, 7 (Death-inflicting)

#### **PlanetAnalyzer** (`analyzer/planet_analyzer.py`)
- **Purpose**: Individual planet strength and characteristics
- **Responsibility**: Evaluate planetary strength using Shadbala, dignity, aspects
- **Input**: Individual planet data, house data
- **Output**: Planet strength scores, characteristics
- **Key Metrics**:
  - Strength (Shadbala calculation)
  - Dignity (Own house, exalted, debilitated)
  - Aspects and influences

#### **PlanetStrength** (`analyzer/planet_strength.py`)
- **Purpose**: Calculate planetary strength using traditional systems
- **Responsibility**: Compute Shadbala and other strength measures
- **Input**: Planet position data
- **Output**: Numerical strength values (0-100 scale typically)

#### **VargaChartAnalyzer** (`analyzer/varga.py`)
- **Purpose**: Multi-chart analysis (D1, D2, D9, D10, etc.)
- **Responsibility**: Analyze planetary positions across different divisional charts
- **Input**: Planet data for multiple divisions
- **Output**: Comparative analysis across charts
- **Supported Divisions**:
  - D1 (Rashi) - General chart
  - D2 (Hora) - Wealth
  - D3 (Drekkana) - Siblings
  - D4 (Chaturshamsa) - Vehicles/property
  - D9 (Navamsa) - Marriage/dharma
  - D10 (Dashamsa) - Career
  - D12 (Dwadhashamsa) - Parents
  - And more...

#### **AstroTableGenerator** (`analyzer/astro_table.py`)
- **Purpose**: Generate organized astrological tables
- **Responsibility**: Present chart data in tabular format for easy reference
- **Input**: Planet and house data
- **Output**: Formatted tables (ASCII/grid format)
- **Typical Output**:
  - Planetary positions
  - House cusps
  - Aspects table
  - Sign/house summary

---

### 2. Detection Agents (yoga_detector/ directory)

These agents detect specific astrological combinations and yogas.

#### **VedicYogaDetector** (`yoga_detector/vedic_yoga_detector.py`)
- **Purpose**: Master detector coordinating all yoga detection
- **Responsibility**: Orchestrate all specialized yoga detectors
- **Detectors Coordinated**:
  - Raja Yoga Detector
  - Dhan Yoga Detector
  - Moon Yogas Detector
  - Sun Yoga Detector
  - Nabhasa Yoga Detector
  - Pancha Mahapurusha Detector
  - Parivartan Yoga Detector
  - Neech Bhanga Raja Yoga Detector
  - Malika Yogas Detector
  - Vipreet Raja Yoga Detector

#### **RajaYogaDetector** (`yoga_detector/raja_yoga_detector.py`)
- **Purpose**: Detect royal/powerful yogas
- **Yogas Detected**:
  - Lakshmi Yoga: Trikona lord in Kendra
  - Gajakesari Yoga: Jupiter in Kendra to Moon
  - Panch Mahapurusha: Planets in own/exalted sign in Kendra

#### **DhanYogaDetector** (`yoga_detector/dhan_yoga_detector.py`)
- **Purpose**: Detect wealth-generating yogas
- **Indicators**:
  - 2nd and 11th house strength
  - Jupiter and Venus placements
  - Wealth-generating combinations

#### **MoonYogaDetector** (`yoga_detector/moon_yogas.py`)
- **Purpose**: Detect yogas involving the Moon
- **Yogas Detected**:
  - Chandra Mangal Yoga
  - Chandra Shubha Yoga
  - Emotional balance indicators

#### **SunYogaDetector** (`yoga_detector/sun_yoga_detector.py`)
- **Purpose**: Detect Sun-related yogas
- **Focus Areas**:
  - Sun strength for authority/power
  - Father-related indications
  - Karmic strength

#### **NabhasaYogaDetector** (`yoga_detector/nabhasa_yoga_detector.py`)
- **Purpose**: Detect house-based yogas
- **Yogas Detected**:
  - Chakra Yoga: Planets in all 12 houses
  - Raja Yoga (house variation)
  - Graha Yoga: Planetary collections
  - Parivartana: Mutual exchanges

#### **PanchaMahapurushaDetector** (`yoga_detector/pancha_mahapurusha.py`)
- **Purpose**: Detect 5 great person yogas
- **Yogas Detected**:
  - Hamsa Yoga (Jupiter in Kendra, own/exalted)
  - Malavya Yoga (Venus in Kendra, own/exalted)
  - Shasha Yoga (Saturn in Kendra, own/exalted)
  - Ruchaka Yoga (Mars in Kendra, own/exalted)
  - Bhadra Yoga (Mercury in Kendra, own/exalted)

#### **ParivaratanYogaDetector** (`yoga_detector/parivartan_yoga_detector.py`)
- **Purpose**: Detect mutual exchange yogas
- **Yoga Type**: Lords of two houses exchange positions
- **Strength**: Varies by houses involved

#### **NeechBhangaRajaYogaDetector** (`yoga_detector/neech_bhanga_raja_yoga.py`)
- **Purpose**: Detect cancellation of debilitation
- **Condition**: Debilitated planet gains strength through specific combinations

#### **MalikaYogasDetector** (`yoga_detector/malika_yogas_detector.py`)
- **Purpose**: Detect chain-like yogas (consecutive house placements)
- **Pattern**: Planets in consecutive houses with specific characteristics

#### **VipreetRajaYogaDetector** (`yoga_detector/vipreet_raja_yoga.py`)
- **Purpose**: Detect "reverse" royal yogas in difficult houses
- **Principle**: Malefics in 6, 8, 12 can create positive outcomes
- **Note**: Requires careful interpretation

---

### 3. Curse/Dosha Agents (curses/ directory)

These agents detect planetary afflictions and doshas.

#### **CurseDetectorBase** (`curses/curse_detector_base.py`)
- **Purpose**: Base class for all curse detectors
- **Responsibility**: Define common interface and methods
- **Common Methods**:
  - `detect_curse()` - Check if curse present
  - `get_severity()` - Rate severity (mild/moderate/severe)
  - `get_remedies()` - Suggest remedies

#### **CurseDetector** (`curses/curse_detector.py`)
- **Purpose**: Master detector coordinating all curse detectors
- **Detectors Coordinated**:
  - Snake Curse Detector
  - Sage Curse Detector
  - Evil Spirit Curse Detector
  - Father Curse Detector
  - Mother Curse Detector
  - Brother Curse Detector
  - Spouse Curse Detector

#### **SnakeCurseDetector** (`curses/snake_curse_detector.py`)
- **Purpose**: Detect Nag Dosha (serpent curse)
- **Indicators**:
  - Rahu-Ketu placement
  - Saturn afflictions
  - Specific house combinations

#### **SageCurseDetector** (`curses/sage_curse_detector.py`)
- **Purpose**: Detect Brahmin curse effect
- **Indicators**: 
  - Specific planetary combinations
  - Age of person triggering doshas

#### **EvilSpiritCurseDetector** (`curses/evil_spirit_curse_detector.py`)
- **Purpose**: Detect demonic or negative entity influences

#### **FatherCurseDetector** (`curses/father_curse_detector.py`)
- **Purpose**: Detect paternal curse effects
- **Focus**: Sun placement, 9th house, father-related issues

#### **MotherCurseDetector** (`curses/mother_curse_detector.py`)
- **Purpose**: Detect maternal curse effects
- **Focus**: Moon placement, 4th house, mother-related issues

#### **BrotherCurseDetector** (`curses/brother_curse_detector.py`)
- **Purpose**: Detect sibling curse effects
- **Focus**: 3rd house, Mercury placements

#### **SpouseCurseDetector** (`curses/spouse_curse_detector.py`)
- **Purpose**: Detect marital curse effects
- **Focus**: 7th house, Venus, Mars combinations

---

### 4. Time Period Agents (dasha/ directory)

These agents calculate time periods and transits.

#### **VimshottariDasha** (`dasha/vimshottari.py`)
- **Purpose**: Calculate Vimshottari Dasha periods
- **System**: 120-year cycle divided among 9 planets
- **Input**: Moon sign and birth date
- **Output**: Dasha timings and sub-periods
- **Key Methods**:
  - `get_dasha_period(date)` - Find active Dasha at date
  - `print_dasha(levels, years_ahead)` - Print Dasha timeline
  - `calculate_balance()` - Calculate birth Dasha balance

---

### 5. Support Agents

#### **DataValidator** (`yoga_detector/data_validator.py`)
- **Purpose**: Validate chart data integrity
- **Responsibility**: Check for missing/invalid fields
- **Usage**: Before analysis begins

#### **HouseOwnershipParser** (`yoga_detector/house_ownership_parser.py`)
- **Purpose**: Determine house ownerships
- **Calculates**: Which planet rules which house

#### **HouseTypesAnalyzer** (`yoga_detector/house_types.py`)
- **Purpose**: Classify house types and characteristics
- **Categories**: Trikona, Kendra, Dusthana, etc.

---

## Agent Interaction Patterns

### Pattern 1: Master-Worker (Coordination)
```
VedicYogaDetector (master)
├── RajaYogaDetector
├── DhanYogaDetector
├── MoonYogaDetector
└── ... other detectors

Usage: Master coordinates and combines results
```

### Pattern 2: Sequential Processing
```
Input Chart Data
  ↓
DataValidator (validate)
  ↓
BPHSHouseAnalyzer (analyze houses)
  ↓
VedicYogaDetector (detect yogas)
  ↓
CurseDetector (detect doshas)
  ↓
VimshottariDasha (calculate periods)
  ↓
Output: Comprehensive Report
```

### Pattern 3: Independent Analysis
```
Planet → PlanetAnalyzer
Moon → MoonYogaDetector
Sun → SunYogaDetector
Parallel execution, independent results
```

### Pattern 4: Hierarchical Detection
```
CurseDetector (master)
└── For each person-type:
    ├── FatherCurseDetector
    ├── MotherCurseDetector
    ├── BrotherCurseDetector
    └── SpouseCurseDetector
    
Results combined into single report
```

---

## Agent Development Guide

### Creating a New Detector

1. **Inherit from Base**:
   ```python
   from curses.curse_detector_base import CurseDetectorBase
   
   class MyDetector(CurseDetectorBase):
       def __init__(self, planet_objects, house_objects):
           self.planets = planet_objects
           self.houses = house_objects
   ```

2. **Implement Core Methods**:
   ```python
   def detect(self) -> bool:
       """Detect if condition present"""
       return self._check_condition()
   
   def get_severity(self) -> str:
       """Return: 'none', 'mild', 'moderate', 'severe'"""
       if not self.detect():
           return 'none'
       # Calculate severity
       return 'moderate'
   
   def get_remedies(self) -> list:
       """Return list of suggested remedies"""
       return ['Remedy 1', 'Remedy 2', ...]
   ```

3. **Register in Master**:
   ```python
   # In appropriate master detector
   self.detectors.append(MyDetector(planets, houses))
   ```

4. **Add Tests**:
   ```python
   # test_my_detector.py
   def test_detection():
       # Create test chart data
       detector = MyDetector(test_planets, test_houses)
       assert detector.detect() == True
   ```

### Creating a New Analyzer

Similar approach:
```python
class MyAnalyzer:
    def __init__(self, planet_objects, house_objects):
        self.planets = planet_objects
        self.houses = house_objects
    
    def analyze(self) -> Dict:
        """Return analysis results"""
        return {
            'metric1': value1,
            'metric2': value2,
        }
    
    def print_analysis(self):
        """Print human-readable output"""
        results = self.analyze()
        for key, val in results.items():
            print(f"{key}: {val}")
```

---

## Common Data Structures

### ChartData (from main.py)
```python
@dataclass
class ChartData:
    planet_data: dict        # Raw planet data from vedastro
    house_data: dict         # Raw house data from vedastro
    planet_objects: list     # Parsed planet objects
    house_objects: list      # Parsed house objects
    dob: Optional[str]       # Date of birth
```

### Planet Object
```python
{
    'name': 'Sun',
    'house': 1,
    'sign': 'Aries',
    'degree': 15.5,
    'retrograde': False,
    'speed': 1.0,
    # ... more fields
}
```

### House Object
```python
{
    'number': 1,
    'sign': 'Aries',
    'lord': 'Mars',
    'planets': ['Sun', 'Mercury'],
    # ... more fields
}
```

---

## Agent Usage Examples

### Example 1: Single Detector Usage
```python
from curses.snake_curse_detector import SnakeCurseDetector

detector = SnakeCurseDetector(planet_objects, house_objects)

if detector.detect():
    severity = detector.get_severity()
    remedies = detector.get_remedies()
    print(f"Nag Dosha found: {severity}")
    for remedy in remedies:
        print(f"  - {remedy}")
```

### Example 2: Master Detector Usage
```python
from yoga_detector.vedic_yoga_detector import VedicYogaDetector

detector = VedicYogaDetector(chart_data)
results = detector.detect_all_yogas()

for yoga_type, details in results.items():
    if details['found']:
        print(f"✓ {yoga_type}: {details['description']}")
```

### Example 3: Sequential Analysis
```python
from analyzer.bphs_house_analyzer import BPHSHouseAnalyzer
from curses.curse_detector import CurseDetector

# Analyze houses
house_analyzer = BPHSHouseAnalyzer(planets, houses)
house_report = house_analyzer.generate_comprehensive_report()

# Detect curses
curse_detector = CurseDetector(planets, houses)
curse_report = curse_detector.detect_all_curses()

# Combine reports
full_report = house_report + "\n\n" + curse_report
```

### Example 4: With Query Engine
```python
from query_engine import create_engine
from yoga_detector.vedic_yoga_detector import VedicYogaDetector

# Find all charts matching pattern
engine = create_engine()
results, _ = engine.search("(Su 11H) AND (Ju Kendra)")

# Analyze each match for yogas
for chart in results:
    yogas = VedicYogaDetector(chart_data).detect_all_yogas()
    if yogas:
        print(f"Chart {chart.chart_id}: {len(yogas)} yogas detected")
```

---

## Agent Coordination Rules

1. **Independence**: Each agent should work independently
2. **No Direct Dependencies**: Agents shouldn't call each other
3. **Shared Input**: All use same chart data source
4. **Master Pattern**: Use master detector for coordination
5. **Error Handling**: Graceful degradation on missing data

---

## Performance Considerations

- **Parallel Execution**: Independent analyzers can run in parallel
- **Lazy Evaluation**: Calculate only when needed
- **Caching**: Cache expensive calculations
- **Incremental Analysis**: Don't re-analyze if data hasn't changed

---

## Future Agent Ideas

- **Transit Analyzer**: Predict future events based on transits
- **Compatibility Analyzer**: Compare two charts for compatibility
- **Timing Predictor**: Predict auspicious times for events
- **Health Analyzer**: Health predictions from chart
- **Career Advisor**: Career suggestions based on chart
- **Relationship Analyzer**: Detailed relationship analysis

---

## Troubleshooting Agents

### Agent Returns No Results
1. Check data validity: `DataValidator.validate()`
2. Check log output for errors
3. Verify input data structure matches expectations

### Agent Crashes
1. Add error handling to agent
2. Check for missing required fields in input data
3. Add debug logging: `logger.debug(f"State: {state}")`

### Inconsistent Results
1. Verify planet/house coordinate calculations
2. Check timezone handling in time calculations
3. Ensure consistent sign abbreviations

---

**Last Updated**: May 2026  
**Version**: 1.0
