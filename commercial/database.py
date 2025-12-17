"""
PostgreSQL Database Module

Handles all database operations for user management and video metadata storage.
Uses psycopg2 for PostgreSQL connectivity.
"""

import os
import json
from typing import Optional, List, Dict
from datetime import datetime
from pathlib import Path
import psycopg2
from psycopg2.extras import RealDictCursor

# Only load .env in local development (not on Streamlit Cloud)
if not os.getenv("STREAMLIT_RUNTIME_ENV"):
    from dotenv import load_dotenv
    env_path = Path(__file__).parent / ".env.commercial"
    load_dotenv(env_path)




def get_connection():
    """
    Get PostgreSQL database connection
    
    Returns:
        psycopg2.connection: Database connection object
    """
    database_url = os.getenv("DATABASE_URL")
    
    if not database_url:
        raise ValueError("DATABASE_URL environment variable not set")
    
    print(f"DEBUG: Connecting to database...")
    
    conn = psycopg2.connect(
        database_url,
        connect_timeout=10
    )
    
    return conn


def init_db():
    """Initialize database tables"""
    conn = get_connection()
    cursor = conn.cursor()
    
    try:
        # Create users table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id SERIAL PRIMARY KEY,
                uid VARCHAR(255) UNIQUE NOT NULL,
                email VARCHAR(255) UNIQUE NOT NULL,
                display_name VARCHAR(255),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_login TIMESTAMP
            )
        """)
        
        # Subscriptions table
        cur.execute("""
            CREATE TABLE IF NOT EXISTS subscriptions (
                id SERIAL PRIMARY KEY,
                user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
                tier VARCHAR(50) NOT NULL DEFAULT 'free',
                status VARCHAR(50) NOT NULL DEFAULT 'active',
                stripe_customer_id VARCHAR(255),
                stripe_subscription_id VARCHAR(255),
                current_period_start TIMESTAMP,
                current_period_end TIMESTAMP,
                cancel_at_period_end BOOLEAN DEFAULT FALSE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(user_id)
            )
        """)
        
        # Usage tracking table
        cur.execute("""
            CREATE TABLE IF NOT EXISTS usage_tracking (
                id SERIAL PRIMARY KEY,
                user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
                month VARCHAR(7) NOT NULL,
                videos_generated INTEGER DEFAULT 0,
                last_reset TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(user_id, month)
            )
        """)
        
        # Videos table
        cur.execute("""
            CREATE TABLE IF NOT EXISTS videos (
                id SERIAL PRIMARY KEY,
                user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
                topic VARCHAR(500) NOT NULL,
                file_path VARCHAR(1000) NOT NULL,
                thumbnail_path VARCHAR(1000),
                duration_seconds INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                metadata JSONB
            )
        """)
        
        # Generation sessions table
        cur.execute("""
            CREATE TABLE IF NOT EXISTS generation_sessions (
                id SERIAL PRIMARY KEY,
                video_id INTEGER REFERENCES videos(id) ON DELETE CASCADE,
                status VARCHAR(50),
                error_message TEXT,
                started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                completed_at TIMESTAMP
            )
        """)
        
        # Payments table
        cur.execute("""
            CREATE TABLE IF NOT EXISTS payments (
                id SERIAL PRIMARY KEY,
                user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
                stripe_payment_intent_id VARCHAR(255),
                amount INTEGER NOT NULL,
                currency VARCHAR(3) DEFAULT 'usd',
                status VARCHAR(50),
                description TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Invoices table
        cur.execute("""
            CREATE TABLE IF NOT EXISTS invoices (
                id SERIAL PRIMARY KEY,
                user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
                payment_id INTEGER REFERENCES payments(id) ON DELETE CASCADE,
                total DECIMAL(10, 2) NOT NULL,
                items TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Create indexes for better performance
        cur.execute("CREATE INDEX IF NOT EXISTS idx_subscriptions_user_id ON subscriptions(user_id)")
        cur.execute("CREATE INDEX IF NOT EXISTS idx_usage_tracking_user_month ON usage_tracking(user_id, month)")
        cur.execute("CREATE INDEX IF NOT EXISTS idx_videos_user_id ON videos(user_id)")
        cur.execute("CREATE INDEX IF NOT EXISTS idx_payments_user_id ON payments(user_id)")
        
        conn.commit()
        print("✅ Database tables created successfully")
        
    except Exception as e:
        conn.rollback()
        raise Exception(f"Database initialization failed: {e}")
    finally:
        cur.close()
        conn.close()


def create_user(firebase_uid: str, email: str, display_name: str = "") -> Dict:
    """
    Create new user record
    
    Args:
        firebase_uid: Firebase user ID
        email: User's email
        display_name: User's display name
        
    Returns:
        dict: Created user record
    """
    conn = get_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    
    try:
        cur.execute("""
            INSERT INTO users (firebase_uid, email, display_name, last_login)
            VALUES (%s, %s, %s, CURRENT_TIMESTAMP)
            RETURNING id, firebase_uid, email, display_name, created_at
        """, (firebase_uid, email, display_name))
        
        user = dict(cur.fetchone())
        conn.commit()
        return user
        
    except Exception as e:
        conn.rollback()
        raise Exception(f"User creation failed: {e}")
    finally:
        cur.close()
        conn.close()


def get_user_by_uid(firebase_uid: str) -> Optional[Dict]:
    """
    Get user by Firebase UID
    
    Args:
        firebase_uid: Firebase user ID
        
    Returns:
        dict: User record or None if not found
    """
    conn = get_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    
    try:
        cur.execute("""
            SELECT id, firebase_uid, email, display_name, created_at, last_login
            FROM users
            WHERE firebase_uid = %s
        """, (firebase_uid,))
        
        user = cur.fetchone()
        return dict(user) if user else None
        
    finally:
        cur.close()
        conn.close()


def update_last_login(firebase_uid: str):
    """Update user's last login timestamp"""
    conn = get_connection()
    cur = conn.cursor()
    
    try:
        cur.execute("""
            UPDATE users
            SET last_login = CURRENT_TIMESTAMP
            WHERE firebase_uid = %s
        """, (firebase_uid,))
        
        conn.commit()
    finally:
        cur.close()
        conn.close()


def save_video_metadata(
    user_id: int,
    topic: str,
    file_path: str,
    thumbnail_path: str = "",
    duration_seconds: int = 0,
    metadata: Dict = None
) -> Dict:
    """
    Save video metadata to database
    
    Args:
        user_id: User's database ID
        topic: Video topic
        file_path: Path to video file
        thumbnail_path: Path to thumbnail image
        duration_seconds: Video duration
        metadata: Additional metadata (scenes, style, etc.)
        
    Returns:
        dict: Created video record
    """
    conn = get_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    
    try:
        cur.execute("""
            INSERT INTO videos (
                user_id, topic, file_path, thumbnail_path, 
                duration_seconds, metadata
            )
            VALUES (%s, %s, %s, %s, %s, %s)
            RETURNING id, user_id, topic, file_path, thumbnail_path, 
                      duration_seconds, created_at, metadata
        """, (
            user_id, topic, file_path, thumbnail_path,
            duration_seconds, json.dumps(metadata) if metadata else None
        ))
        
        video = dict(cur.fetchone())
        conn.commit()
        return video
        
    except Exception as e:
        conn.rollback()
        raise Exception(f"Video metadata save failed: {e}")
    finally:
        cur.close()
        conn.close()


def get_user_videos(user_id: int) -> List[Dict]:
    """
    Get all videos for a user
    
    Args:
        user_id: User's database ID
        
    Returns:
        list: List of video records
    """
    conn = get_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    
    try:
        cur.execute("""
            SELECT id, user_id, topic, file_path, thumbnail_path,
                   duration_seconds, created_at, metadata
            FROM videos
            WHERE user_id = %s
            ORDER BY created_at DESC
        """, (user_id,))
        
        videos = [dict(row) for row in cur.fetchall()]
        return videos
        
    finally:
        cur.close()
        conn.close()


def create_generation_session(video_id: int) -> int:
    """
    Create generation session tracking record
    
    Args:
        video_id: Video database ID
        
    Returns:
        int: Session ID
    """
    conn = get_connection()
    cur = conn.cursor()
    
    try:
        cur.execute("""
            INSERT INTO generation_sessions (video_id, status)
            VALUES (%s, 'pending')
            RETURNING id
        """, (video_id,))
        
        session_id = cur.fetchone()[0]
        conn.commit()
        return session_id
        
    except Exception as e:
        conn.rollback()
        raise Exception(f"Session creation failed: {e}")
    finally:
        cur.close()
        conn.close()


def update_generation_status(
    session_id: int,
    status: str,
    error_message: str = None
):
    """
    Update generation session status
    
    Args:
        session_id: Session database ID
        status: Status ('pending', 'processing', 'completed', 'failed')
        error_message: Error message if failed
    """
    conn = get_connection()
    cur = conn.cursor()
    
    try:
        if status == 'completed':
            cur.execute("""
                UPDATE generation_sessions
                SET status = %s, completed_at = CURRENT_TIMESTAMP
                WHERE id = %s
            """, (status, session_id))
        else:
            cur.execute("""
                UPDATE generation_sessions
                SET status = %s, error_message = %s
                WHERE id = %s
            """, (status, error_message, session_id))
        
        conn.commit()
    finally:
        cur.close()
        conn.close()


# Example usage and testing
if __name__ == "__main__":
    # Initialize database
    print("Initializing database...")
    init_db()
    
    # Test connection
    conn = get_connection()
    print("✅ Database connection successful")
    conn.close()
