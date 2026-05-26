# PostgreSQL Setup & Migration Guide

## Local Development Setup

### 1. Install PostgreSQL
```bash
brew install postgresql@16
brew services start postgresql@16
```

### 2. Create Local Database
```bash
createdb vedica
```

### 3. Create `.env` file
Copy `.env.example` to `.env`:
```bash
cp .env.example .env
```

Update `.env` with your local PostgreSQL credentials:
```
POSTGRES_URL=postgresql://username:password@localhost:5432/vedica
```

To find your username (usually your macOS username):
```bash
whoami
```

### 4. Install Python Dependencies
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 5. Run Migrations
Migrations run automatically on app startup, but you can also run manually:
```bash
flask db upgrade
```

### 6. Start the App
```bash
python3 run.py
```

## Vercel Deployment Setup

### 1. Create PostgreSQL Database on Cloud
- Use Vercel Postgres, Supabase, Railway, Render, etc.
- Copy the connection string

### 2. Add Environment Variable to Vercel
In Vercel dashboard:
- Project Settings → Environment Variables
- Add `POSTGRES_URL` with your cloud database connection string

### 3. Deploy
```bash
git push  # Vercel will auto-deploy
```

Migrations **run automatically on app startup** via `core/migrations.py` - no manual steps needed!

## Migration Workflow

### Creating New Migrations
When you add columns, create tables, etc., create a migration:

```bash
flask db migrate -m "Add user_preferences table"
```

This generates `migrations/versions/xxx_add_user_preferences.py`. Edit it, then:

```bash
flask db upgrade
```

### On Vercel
Migrations run automatically when the app starts (`app.py` calls `run_migrations()`). You don't need to do anything - just push code.

### Viewing Migration History
```bash
flask db history  # Show all migrations
flask db heads    # Show current revision
```

### Reverting Migrations (if needed)
```bash
flask db downgrade -1  # Downgrade by one revision
```

## Testing Locally

### Run the app:
```bash
source venv/bin/activate
python3 run.py
```

### Verify database connection:
```bash
python3 -c "from core.database import get_conn; c = get_conn(); c.execute('SELECT 1'); print('✅ Connected to PostgreSQL')"
```

### Check migrations status:
```bash
flask db current  # Show current applied revision
```

## Troubleshooting

**Error: POSTGRES_URL not set**
- Ensure `.env` file exists and contains `POSTGRES_URL`
- Check that `dotenv` is loaded before accessing the variable

**Error: Connection refused**
- Verify PostgreSQL is running: `brew services list`
- Check database exists: `psql -l | grep vedica`

**Error: Migration not applied**
- Check `alembic_version` table in DB: `psql postgres -c "SELECT * FROM alembic_version;"`
- Force rerun: `flask db stamp head` (marks all as applied - use with caution)

**Error: Conflicting migrations**
- Multiple migration files with same revision - check `migrations/versions/` for duplicates
- Fix by renaming one file's revision ID in both filename and file content

## Best Practices

- ✅ Always create a migration when changing schema
- ✅ Test migrations locally before pushing
- ✅ Include `downgrade()` for reversibility
- ✅ Use meaningful migration names: `002_add_user_profiles.py`
- ✅ Keep migrations small and focused
- ❌ Don't edit applied migrations - create new ones instead
