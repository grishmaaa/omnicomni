# EMERGENCY DEPLOYMENT - Use SQLite for now

## The Problem
Supabase's IPv6 networking is incompatible with Railway and Streamlit Cloud.

## IMMEDIATE SOLUTION

Use SQLite (local database) to get your app live NOW, then migrate to Supabase later.

### Step 1: Update database.py to use SQLite

Replace the `get_connection()` function with:

```python
def get_connection():
    """Get database connection - SQLite for deployment"""
    import sqlite3
    
    # Use SQLite for now
    db_path = Path(__file__).parent / "app_database.db"
    conn = sqlite3.connect(str(db_path))
    conn.row_factory = sqlite3.Row
    return conn
```

### Step 2: Deploy to Streamlit Cloud

1. Go to https://share.streamlit.io/
2. Deploy `grishmaaa/omnicomni` → `commercial/app.py`
3. Add ONLY these secrets:
```toml
FIREBASE_WEB_API_KEY = "your_key"
FAL_KEY = "your_fal_key"
OPENAI_API_KEY = "your_openai_key"
ELEVENLABS_API_KEY = "your_elevenlabs_key"
GROQ_API_KEY = "your_groq_key"
FIREBASE_CREDENTIALS_JSON = '''your firebase json'''
```

NO DATABASE_URL needed!

### Step 3: Point GoDaddy

Once live, point your GoDaddy domain to the Streamlit URL.

## This WILL work in 5 minutes

SQLite works everywhere. You can migrate to Supabase later when we fix the networking issue.

**Want me to make this change now?**
