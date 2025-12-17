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
            # Store session for persistence
            if response.session:
                st.session_state.supabase_session = {
                    "access_token": response.session.access_token,
                    "refresh_token": response.session.refresh_token
                }
            
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
        
        # Sign in user - correct method name
        response = supabase.auth.sign_in_with_password({
            "email": email,
            "password": password
        })
        
        if response.user:
            # Store session for persistence
            if response.session:
                st.session_state.supabase_session = {
                    "access_token": response.session.access_token,
                    "refresh_token": response.session.refresh_token
                }
            
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
        # Return None for wrong password, but raise for other errors
        if "Invalid login credentials" in str(e) or "invalid_grant" in str(e):
            return None
        raise e


def restore_session() -> Optional[Dict]:
    """
    Restore user session from stored tokens
    
    Returns:
        dict: User data if session is valid, None otherwise
    """
    try:
        if 'supabase_session' not in st.session_state:
            return None
        
        session_data = st.session_state.supabase_session
        supabase = get_supabase_client()
        
        # Set the session
        supabase.auth.set_session(
            session_data['access_token'],
            session_data['refresh_token']
        )
        
        # Get current user
        user = supabase.auth.get_user()
        
        if user and user.user:
            display_name = user.user.user_metadata.get('display_name', user.user.email.split('@')[0])
            return {
                "uid": user.user.id,
                "email": user.user.email,
                "display_name": display_name
            }
        else:
            # Session expired, clear it
            if 'supabase_session' in st.session_state:
                del st.session_state.supabase_session
            return None
            
    except Exception as e:
        print(f"Session restore error: {e}")
        # Clear invalid session
        if 'supabase_session' in st.session_state:
            del st.session_state.supabase_session
        return None


def logout_user():
    """Sign out current user"""
    try:
        supabase = get_supabase_client()
        supabase.auth.sign_out()
        
        # Clear session data
        if 'supabase_session' in st.session_state:
            del st.session_state.supabase_session
        if 'user' in st.session_state:
            del st.session_state.user
    except Exception as e:
        print(f"Logout error: {e}")


def is_authenticated() -> bool:
    """Check if user is authenticated"""
    # First check if user is in session
    if 'user' in st.session_state and st.session_state.user is not None:
        return True
    
    # Try to restore session from tokens
    user_data = restore_session()
    if user_data:
        st.session_state.user = user_data
        return True
    
    return False


def login_user(user_data: Dict):
    """Store user data in session"""
    st.session_state.user = user_data


def get_current_user() -> Optional[Dict]:
    """Get current authenticated user"""
    return st.session_state.get('user')
