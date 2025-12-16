"""
Subscription Management Module

Handles subscription tiers, usage tracking, and payment processing.
"""

import os
from typing import Optional, Dict
from datetime import datetime, timedelta
from pathlib import Path
from dotenv import load_dotenv

# Load environment
env_path = Path(__file__).resolve().parent.parent / ".env.commercial"
load_dotenv(env_path)

# Subscription tier definitions
SUBSCRIPTION_TIERS = {
    'free': {
        'name': 'Free',
        'price': 0,
        'videos_per_month': 5,
        'features': [
            '5 videos per month',
            'Standard quality',
            'Basic support',
            'Watermark on videos'
        ]
    },
    'pro': {
        'name': 'Pro',
        'price': 999,  # $9.99 in cents
        'videos_per_month': 50,
        'features': [
            '50 videos per month',
            'HD quality',
            'Priority support',
            'No watermark',
            'Advanced customization'
        ]
    },
    'enterprise': {
        'name': 'Enterprise',
        'price': 4999,  # $49.99 in cents
        'videos_per_month': -1,  # Unlimited
        'features': [
            'Unlimited videos',
            '4K quality',
            '24/7 priority support',
            'No watermark',
            'Advanced customization',
            'API access',
            'Custom branding'
        ]
    }
}


def get_tier_info(tier: str) -> Dict:
    """Get information about a subscription tier"""
    return SUBSCRIPTION_TIERS.get(tier, SUBSCRIPTION_TIERS['free'])


def format_price(cents: int) -> str:
    """Format price in cents to dollar string"""
    if cents == 0:
        return "Free"
    return f"${cents / 100:.2f}"


def get_tier_limit(tier: str) -> int:
    """Get video generation limit for a tier"""
    tier_info = get_tier_info(tier)
    return tier_info['videos_per_month']


def can_generate_video(user_id: int, tier: str) -> tuple[bool, str]:
    """
    Check if user can generate a video based on their tier and usage
    
    Returns:
        tuple: (can_generate: bool, message: str)
    """
    from database import get_connection
    from psycopg2.extras import RealDictCursor
    
    limit = get_tier_limit(tier)
    
    # Unlimited for enterprise
    if limit == -1:
        return True, "Unlimited videos"
    
    # Get current month usage
    current_month = datetime.now().strftime("%Y-%m")
    
    conn = get_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    
    try:
        cur.execute("""
            SELECT videos_generated
            FROM usage_tracking
            WHERE user_id = %s AND month = %s
        """, (user_id, current_month))
        
        result = cur.fetchone()
        current_usage = result['videos_generated'] if result else 0
        
        if current_usage >= limit:
            return False, f"Monthly limit reached ({current_usage}/{limit}). Upgrade to generate more!"
        
        return True, f"Usage: {current_usage}/{limit} videos this month"
        
    finally:
        cur.close()
        conn.close()


def increment_usage(user_id: int):
    """Increment video generation count for current month"""
    from database import get_connection
    
    current_month = datetime.now().strftime("%Y-%m")
    
    conn = get_connection()
    cur = conn.cursor()
    
    try:
        # Insert or update usage
        cur.execute("""
            INSERT INTO usage_tracking (user_id, month, videos_generated, last_reset)
            VALUES (%s, %s, 1, CURRENT_TIMESTAMP)
            ON CONFLICT (user_id, month)
            DO UPDATE SET 
                videos_generated = usage_tracking.videos_generated + 1,
                last_reset = CURRENT_TIMESTAMP
        """, (user_id, current_month))
        
        conn.commit()
        
    except Exception as e:
        conn.rollback()
        raise Exception(f"Failed to increment usage: {e}")
    finally:
        cur.close()
        conn.close()


def get_user_usage(user_id: int) -> Dict:
    """Get user's current month usage statistics"""
    from database import get_connection
    from psycopg2.extras import RealDictCursor
    
    current_month = datetime.now().strftime("%Y-%m")
    
    conn = get_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    
    try:
        cur.execute("""
            SELECT videos_generated, last_reset
            FROM usage_tracking
            WHERE user_id = %s AND month = %s
        """, (user_id, current_month))
        
        result = cur.fetchone()
        
        if result:
            return dict(result)
        else:
            return {'videos_generated': 0, 'last_reset': None}
            
    finally:
        cur.close()
        conn.close()


def create_subscription(user_id: int, tier: str = 'free') -> Dict:
    """Create a new subscription for a user"""
    from database import get_connection
    from psycopg2.extras import RealDictCursor
    
    conn = get_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    
    try:
        cur.execute("""
            INSERT INTO subscriptions (user_id, tier, status)
            VALUES (%s, %s, 'active')
            RETURNING id, user_id, tier, status, created_at
        """, (user_id, tier))
        
        subscription = dict(cur.fetchone())
        conn.commit()
        return subscription
        
    except Exception as e:
        conn.rollback()
        raise Exception(f"Failed to create subscription: {e}")
    finally:
        cur.close()
        conn.close()


def get_user_subscription(user_id: int) -> Optional[Dict]:
    """Get user's current subscription"""
    from database import get_connection
    from psycopg2.extras import RealDictCursor
    
    conn = get_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    
    try:
        cur.execute("""
            SELECT id, user_id, tier, status, stripe_customer_id,
                   stripe_subscription_id, current_period_start,
                   current_period_end, cancel_at_period_end, created_at
            FROM subscriptions
            WHERE user_id = %s
        """, (user_id,))
        
        result = cur.fetchone()
        return dict(result) if result else None
        
    finally:
        cur.close()
        conn.close()


def update_subscription_tier(user_id: int, new_tier: str) -> Dict:
    """Update user's subscription tier"""
    from database import get_connection
    from psycopg2.extras import RealDictCursor
    
    conn = get_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    
    try:
        cur.execute("""
            UPDATE subscriptions
            SET tier = %s, updated_at = CURRENT_TIMESTAMP
            WHERE user_id = %s
            RETURNING id, user_id, tier, status, updated_at
        """, (new_tier, user_id))
        
        subscription = dict(cur.fetchone())
        conn.commit()
        return subscription
        
    except Exception as e:
        conn.rollback()
        raise Exception(f"Failed to update subscription: {e}")
    finally:
        cur.close()
        conn.close()


def record_payment(user_id: int, amount: int, description: str, 
                   stripe_payment_intent_id: str = None) -> Dict:
    """Record a payment transaction"""
    from database import get_connection
    from psycopg2.extras import RealDictCursor
    
    conn = get_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    
    try:
        cur.execute("""
            INSERT INTO payments (user_id, amount, description, 
                                stripe_payment_intent_id, status)
            VALUES (%s, %s, %s, %s, 'completed')
            RETURNING id, user_id, amount, description, created_at
        """, (user_id, amount, description, stripe_payment_intent_id))
        
        payment = dict(cur.fetchone())
        conn.commit()
        return payment
        
    except Exception as e:
        conn.rollback()
        raise Exception(f"Failed to record payment: {e}")
    finally:
        cur.close()
        conn.close()


def get_user_payments(user_id: int) -> list[Dict]:
    """Get user's payment history"""
    from database import get_connection
    from psycopg2.extras import RealDictCursor
    
    conn = get_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    
    try:
        cur.execute("""
            SELECT id, amount, currency, description, status, created_at
            FROM payments
            WHERE user_id = %s
            ORDER BY created_at DESC
        """, (user_id,))
        
        payments = [dict(row) for row in cur.fetchall()]
        return payments
        
    finally:
        cur.close()
        conn.close()
