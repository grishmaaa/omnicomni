"""
Firebase Authentication Module

Handles user authentication using Firebase Admin SDK.
Provides signup, login, logout, and session management for Streamlit app.
"""

import os
import json
import streamlit as st
from typing import Optional, Dict
from pathlib import Path
import firebase_admin
from firebase_admin import credentials, auth
from dotenv import load_dotenv

# Load environment variables
load_dotenv(".env.commercial")


def init_firebase():
    """
    Initialize Firebase Admin SDK
    
    Uses service account JSON file for credentials.
    Only initializes once (idempotent).
    """
    if not firebase_admin._apps:
        # Try JSON file first (more reliable)
        json_path = Path(__file__).parent / "firebase-credentials.json"
        
        if json_path.exists():
            cred = credentials.Certificate(str(json_path))
            firebase_admin.initialize_app(cred)
            print("✅ Firebase initialized from JSON file")
        else:
            # Fallback to environment variables
            raise FileNotFoundError(
                f"Firebase credentials file not found: {json_path}\n"
                "Please create firebase-credentials.json with your service account key."
            )


def signup_user(email: str, password: str, display_name: str = "") -> Dict:
    """
    Create a new Firebase user
    
    Args:
        email: User's email address
        password: User's password (min 6 characters)
        display_name: Optional display name
        
    Returns:
        dict: User data with uid, email, display_name
        
    Raises:
        Exception: If user creation fails
    """
    init_firebase()
    
    try:
        user = auth.create_user(
            email=email,
            password=password,
            display_name=display_name
        )
        
        return {
            "uid": user.uid,
            "email": user.email,
            "display_name": user.display_name or email.split('@')[0]
        }
    except Exception as e:
        raise Exception(f"Signup failed: {str(e)}")


def verify_password(email: str, password: str) -> Optional[Dict]:
    """
    Verify user credentials
    
    Note: Firebase Admin SDK doesn't support password verification directly.
    This is a workaround using Firebase REST API.
    
    Args:
        email: User's email
        password: User's password
        
    Returns:
        dict: User data if successful, None if failed
    """
    import requests
    
    # Firebase REST API endpoint
    api_key = os.getenv("FIREBASE_WEB_API_KEY")
    if not api_key:
        raise ValueError("FIREBASE_WEB_API_KEY not set in environment")
    
    url = f"https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key={api_key}"
    
    payload = {
        "email": email,
        "password": password,
        "returnSecureToken": True
    }
    
    try:
        response = requests.post(url, json=payload)
        data = response.json()
        
        if response.status_code == 200:
            # Get user details from Firebase Admin
            init_firebase()
            user = auth.get_user_by_email(email)
            
            return {
                "uid": user.uid,
                "email": user.email,
                "display_name": user.display_name or email.split('@')[0]
            }
        else:
            return None
    except Exception as e:
        print(f"Login error: {e}")
        return None


def login_user(email: str, password: str) -> Optional[Dict]:
    """
    Authenticate user and create session
    
    Args:
        email: User's email
        password: User's password
        
    Returns:
        dict: User data if successful, None if failed
    """
    user_data = verify_password(email, password)
    
    if user_data:
        # Store in Streamlit session state
        st.session_state.user = user_data
        return user_data
    
    return None


def logout_user():
    """Clear user session"""
    if 'user' in st.session_state:
        del st.session_state.user


def get_current_user() -> Optional[Dict]:
    """
    Get currently logged-in user from session state
    
    Returns:
        dict: User data or None if not logged in
    """
    return st.session_state.get('user', None)


def is_authenticated() -> bool:
    """Check if user is currently authenticated"""
    return 'user' in st.session_state and st.session_state.user is not None


# Example usage
if __name__ == "__main__":
    # Test Firebase initialization
    init_firebase()
    print("✅ Firebase initialized successfully")
    
    # Test user creation (comment out after first run)
    # user = signup_user("test@example.com", "password123", "Test User")
    # print(f"Created user: {user}")
