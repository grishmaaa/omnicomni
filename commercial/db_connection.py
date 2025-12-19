"""
Simple database connection wrapper that handles both local and cloud environments
"""
Database Connection Module

Handles PostgreSQL connections with caching for better performance.
"""

import os
import streamlit as st
import psycopg2
from psycopg2 import pool
from pathlib import Path


def get_env(key: str, default=None):
    """Get environment variable from Streamlit secrets or os.getenv"""
    try:
        if hasattr(st, 'secrets') and key in st.secrets:
            return st.secrets[key]
    except:
        pass
    return os.getenv(key, default)


# Initialize connection pool
@st.cache_resource
def get_connection_pool():
    """Get database connection pool (cached)"""
    database_url = get_env("DATABASE_URL")
    
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
