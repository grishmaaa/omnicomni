"""
Payment Processing Module using Stripe

Handles payment processing, subscription management, and billing history.
"""

import os
import stripe
from typing import Dict, List, Optional
from datetime import datetime
import streamlit as st
from database import get_connection


def get_env(key: str, default=None):
    """Get environment variable from Streamlit secrets or os.getenv"""
    try:
        if hasattr(st, 'secrets') and key in st.secrets:
            return st.secrets[key]
    except:
        pass
    return os.getenv(key, default)


# Initialize Stripe
stripe.api_key = get_env("STRIPE_SECRET_KEY")


def create_payment_intent(amount: int, currency: str = "usd", user_id: str = None) -> Dict:
    """
    Create a Stripe payment intent
    
    Args:
        amount: Amount in cents (e.g., 999 for $9.99)
        currency: Currency code (default: usd)
        user_id: User ID for tracking
        
    Returns:
        dict: Payment intent details including client_secret
    """
    try:
        intent = stripe.PaymentIntent.create(
            amount=amount,
            currency=currency,
            metadata={'user_id': user_id} if user_id else {}
        )
        
        return {
            'client_secret': intent.client_secret,
            'payment_intent_id': intent.id,
            'amount': amount,
            'currency': currency
        }
    except Exception as e:
        raise Exception(f"Payment intent creation failed: {str(e)}")


def create_checkout_session(price_id: str, user_email: str, user_id: str, success_url: str, cancel_url: str) -> str:
    """
    Create a Stripe Checkout session for subscription
    
    Args:
        price_id: Stripe price ID
        user_email: Customer email
        user_id: User ID for tracking
        success_url: URL to redirect after successful payment
        cancel_url: URL to redirect if payment is cancelled
        
    Returns:
        str: Checkout session URL
    """
    try:
        session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[{
                'price': price_id,
                'quantity': 1,
            }],
            mode='subscription',
            customer_email=user_email,
            client_reference_id=user_id,
            success_url=success_url,
            cancel_url=cancel_url,
        )
        
        return session.url
    except Exception as e:
        raise Exception(f"Checkout session creation failed: {str(e)}")


def record_payment(user_id: int, amount: float, payment_intent_id: str, status: str = 'completed') -> int:
    """
    Record a payment in the database
    
    Args:
        user_id: Database user ID
        amount: Payment amount
        payment_intent_id: Stripe payment intent ID
        status: Payment status
        
    Returns:
        int: Payment record ID
    """
    conn = get_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute("""
            INSERT INTO payments (user_id, amount, payment_intent_id, status, created_at)
            VALUES (%s, %s, %s, %s, %s)
            RETURNING id
        """, (user_id, amount, payment_intent_id, status, datetime.now()))
        
        payment_id = cursor.fetchone()[0]
        conn.commit()
        return payment_id
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        cursor.close()
        conn.close()


def get_user_payments(user_id: int) -> List[Dict]:
    """
    Get all payments for a user
    
    Args:
        user_id: Database user ID
        
    Returns:
        list: List of payment records
    """
    conn = get_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute("""
            SELECT id, amount, payment_intent_id, status, created_at
            FROM payments
            WHERE user_id = %s
            ORDER BY created_at DESC
        """, (user_id,))
        
        payments = []
        for row in cursor.fetchall():
            payments.append({
                'id': row[0],
                'amount': row[1],
                'payment_intent_id': row[2],
                'status': row[3],
                'created_at': row[4]
            })
        
        return payments
    finally:
        cursor.close()
        conn.close()


def create_invoice(user_id: int, payment_id: int, items: List[Dict]) -> Dict:
    """
    Create an invoice for a payment
    
    Args:
        user_id: Database user ID
        payment_id: Payment record ID
        items: List of invoice items
        
    Returns:
        dict: Invoice details
    """
    conn = get_connection()
    cursor = conn.cursor()
    
    try:
        # Calculate total
        total = sum(item['amount'] for item in items)
        
        cursor.execute("""
            INSERT INTO invoices (user_id, payment_id, total, items, created_at)
            VALUES (%s, %s, %s, %s, %s)
            RETURNING id
        """, (user_id, payment_id, total, str(items), datetime.now()))
        
        invoice_id = cursor.fetchone()[0]
        conn.commit()
        
        return {
            'invoice_id': invoice_id,
            'total': total,
            'items': items,
            'created_at': datetime.now()
        }
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        cursor.close()
        conn.close()


def get_user_invoices(user_id: int) -> List[Dict]:
    """
    Get all invoices for a user
    
    Args:
        user_id: Database user ID
        
    Returns:
        list: List of invoices
    """
    conn = get_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute("""
            SELECT id, payment_id, total, items, created_at
            FROM invoices
            WHERE user_id = %s
            ORDER BY created_at DESC
        """, (user_id,))
        
        invoices = []
        for row in cursor.fetchall():
            invoices.append({
                'id': row[0],
                'payment_id': row[1],
                'total': row[2],
                'items': row[3],
                'created_at': row[4]
            })
        
        return invoices
    finally:
        cursor.close()
        conn.close()


def init_payment_tables():
    """Initialize payment and invoice tables"""
    conn = get_connection()
    cursor = conn.cursor()
    
    try:
        # Create payments table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS payments (
                id SERIAL PRIMARY KEY,
                user_id INTEGER REFERENCES users(id),
                amount DECIMAL(10, 2) NOT NULL,
                payment_intent_id VARCHAR(255) UNIQUE,
                status VARCHAR(50) DEFAULT 'pending',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Create invoices table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS invoices (
                id SERIAL PRIMARY KEY,
                user_id INTEGER REFERENCES users(id),
                payment_id INTEGER REFERENCES payments(id),
                total DECIMAL(10, 2) NOT NULL,
                items TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        conn.commit()
        print("✅ Payment tables created successfully")
    except Exception as e:
        conn.rollback()
        print(f"❌ Error creating payment tables: {e}")
    finally:
        cursor.close()
        conn.close()
