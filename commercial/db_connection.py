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
    # Try Streamlit secrets first
    database_url = None
    try:
        import streamlit as st
        if hasattr(st, 'secrets') and 'DATABASE_URL' in st.secrets:
            database_url = st.secrets['DATABASE_URL']
    except:
        pass
    
    # Fall back to environment variable
    if not database_url:
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
