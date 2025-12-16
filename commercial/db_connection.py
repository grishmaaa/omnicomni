"""
Simple database connection wrapper that handles both local and cloud environments
"""
import os
import psycopg2
from pathlib import Path

def get_connection():
    """
    Get database connection with proper environment handling
    """
    # Get DATABASE_URL from environment (Streamlit secrets or local .env)
    database_url = os.getenv("DATABASE_URL")
    
    if not database_url:
        # Fallback: try loading from .env.commercial for local development
        try:
            from dotenv import load_dotenv
            env_path = Path(__file__).parent / ".env.commercial"
            if env_path.exists():
                load_dotenv(env_path)
                database_url = os.getenv("DATABASE_URL")
        except:
            pass
    
    if not database_url:
        raise ValueError("DATABASE_URL not found in environment or .env.commercial")
    
    # Simple connection without any modifications
    conn = psycopg2.connect(database_url, connect_timeout=10)
    return conn
