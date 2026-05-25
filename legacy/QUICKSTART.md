# Quick Start Guide

## Setup (One-time)

```bash
# Activate virtual environment
source myenv/bin/activate

# Initialize database (if needed)
python -c "from db_adapter import DatabaseAdapter; DatabaseAdapter().init_db()"
```

## Run Interactive CLI

```bash
python cli.py
```

Then type commands:
```
vedica> search (Su 11H)
vedica> search (Ca Lagna) AND (Mo 2H)
vedica> list 50
vedica> info 1
vedica> stats
vedica> help
vedica> exit
```

## Run Single Command (Batch)

```bash
python cli.py search "(Su 11H)"
python cli.py search "(Ca Lagna) AND (Mo 2H)"
python cli.py list 100
python cli.py info 1
```

## Use in Python

```python
from query_engine import create_engine

engine = create_engine()

# Search
results, total = engine.search("(Su 11H) AND (Ca Lagna)")
for r in results:
    print(f"ID: {r.chart_id}, Name: {r.person_name}")

# List all
charts, total = engine.list_all_charts(limit=50)

# Get details
details = engine.get_chart_details(1)
print(details)

# Stats
print(engine.statistics())
```

## Query Patterns

```
(Su 11H)                    # Sun in 11th house
(Ca Lagna)                  # Cancer Lagna
(Su 11H) AND (Ca Lagna)    # Both conditions
(Mo 2H) OR (Le Lagna)      # Either condition
(Su Ca)                     # Sun in Cancer sign
(Su Kendra)                 # Sun in Kendra houses
```

## Planet Abbreviations

Su=Sun, Mo=Moon, Ma=Mars, Me=Mercury, Ju=Jupiter, Ve=Venus, Sa=Saturn, Ra=Rahu, Ke=Ketu

## Zodiac Abbreviations

Ar=Aries, Ta=Taurus, Ge=Gemini, Ca=Cancer, Le=Leo, Vi=Virgo, Li=Libra, Sc=Scorpio, Sa=Sagittarius, Cp=Capricorn, Aq=Aquarius, Pi=Pisces

## House Categories

Kendra=1,4,7,10 | Trikona=1,5,9 | Upachaya=3,6,10,11 | Dusthana=6,8,12 | Maraka=2,7
