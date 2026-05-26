

python3 -m venv venv && ./venv/bin/pip install -r requirements.txt

source venv/bin/activate

lsof -ti:5000 | xargs kill -9 2>/dev/null
python3 run.py

```
# 1. Install PostgreSQL
brew install postgresql@16
brew services start postgresql@16

# 2. Create database
createdb vedica

# 3. Create .env file
cp .env.example .env
# Edit .env with your PostgreSQL credentials:
# POSTGRES_URL=postgresql://username:password@localhost:5432/vedica

# 4. Install dependencies
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# 5. Initialize schema
python3 -c "from core.database import init_db; init_db()"

# 6. Run the app
python3 run.py
```


## Bulk Import

python3 cli.py < bulk_import.txt