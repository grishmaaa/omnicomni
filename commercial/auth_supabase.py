"""
Supabase Authentication Module

Handles user authentication using Supabase Auth.
Replaces Firebase authentication to avoid JWT signature issues.
"""

import os
from typing import Dict, Optional
from supabase import create_client, Client
import streamlit as st


def get_env(key: str, default=None):
    """Get environment variable from Streamlit secrets or os.getenv"""
    try:
        if hasattr(st, 'secrets') and key in st.secrets:
            return st.secrets[key]
    except:
        pass
    return os.getenv(key, default)


def get_supabase_client() -> Client:
    """Get Supabase client instance"""
    url = get_env("SUPABASE_URL")
    key = get_env("SUPABASE_ANON_KEY")
    
    if not url or not key:
        raise ValueError("SUPABASE_URL and SUPABASE_ANON_KEY must be set")
    
    return create_client(url, key)


def signup_user(email: str, password: str, display_name: str = "") -> Dict:
    """
    Create a new user with Supabase Auth
    
    Args:
        email: User's email
        password: User's password (min 6 characters)
        display_name: Optional display name
        
    Returns:
        dict: User data with uid, email, display_name
    """
    try:
        supabase = get_supabase_client()
        
        # Sign up user
        response = supabase.auth.sign_up({
            "email": email,
            "password": password,
            "options": {
                "data": {
                    "display_name": display_name or email.split('@')[0]
                }
            }
        })
        
        if response.user:
            return {
                "uid": response.user.id,
                "email": response.user.email,
                "display_name": display_name or email.split('@')[0]
            }
        else:
            raise Exception("Signup failed - no user returned")
            
    except Exception as e:
        raise Exception(f"Signup failed: {str(e)}")


def verify_password(email: str, password: str) -> Optional[Dict]:
    """
    Verify user credentials with Supabase Auth
    
    Args:
        email: User's email
        password: User's password
        
    Returns:
        dict: User data if successful, None if failed
    """
    try:
        supabase = get_supabase_client()
        
        # Sign in user
        response = supabase.auth.sign_in_with_password({
            "email": email,
            "password": password
        })
        
        if response.user:
            display_name = response.user.user_metadata.get('display_name', email.split('@')[0])
            return {
                "uid": response.user.id,
                "email": response.user.email,
                "display_name": display_name
            }
        else:
            return None
            
    except Exception as e:
        print(f"Login error: {e}")
        return None


def logout_user():
    """Sign out current user"""
    try:
        supabase = get_supabase_client()
        supabase.auth.sign_out()
    except Exception as e:
        print(f"Logout error: {e}")


def is_authenticated() -> bool:
    """Check if user is authenticated"""
    return 'user' in st.session_state and st.session_state.user is not None


def login_user(user_data: Dict):
    """Store user data in session"""
    st.session_state.user = user_data


def get_current_user() -> Optional[Dict]:
    """Get current authenticated user"""
    return st.session_state.get('user')
