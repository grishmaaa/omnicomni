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
    
    Supports both environment variable (for Railway/production) and JSON file (for local dev).
    Only initializes once (idempotent).
    """
    # Check if already initialized
    try:
        firebase_admin.get_app()
        # Already initialized, skip
        return
    except ValueError:
        # Not initialized yet, proceed
        pass
    
    # Try environment variable first (for Railway/production)
    firebase_creds_env = os.getenv('FIREBASE_CREDENTIALS_JSON')
    if firebase_creds_env:
        import json
        try:
            cred_dict = json.loads(firebase_creds_env)
            cred = credentials.Certificate(cred_dict)
            firebase_admin.initialize_app(cred)
            print("✅ Firebase initialized from environment variable")
            return
        except json.JSONDecodeError as e:
            print(f"⚠️ Failed to parse FIREBASE_CREDENTIALS_JSON: {e}")
    
    # Try individual environment variables (simpler alternative)
    project_id = os.getenv('FIREBASE_PROJECT_ID')
    private_key = os.getenv('FIREBASE_PRIVATE_KEY')
    client_email = os.getenv('FIREBASE_CLIENT_EMAIL')
    
    if project_id and private_key and client_email:
        try:
            cred_dict = {
                "type": "service_account",
                "project_id": project_id,
                "private_key": private_key.replace('\\n', '\n'),  # Handle escaped newlines
                "client_email": client_email,
                "token_uri": "https://oauth2.googleapis.com/token",
            }
            cred = credentials.Certificate(cred_dict)
            firebase_admin.initialize_app(cred)
            print("✅ Firebase initialized from individual environment variables")
            return
        except Exception as e:
            print(f"⚠️ Failed to initialize from individual vars: {e}")
    
    # Fallback to JSON file (for local development)
    json_path = Path(__file__).parent / "firebase-credentials.json"
    
    if json_path.exists():
        cred = credentials.Certificate(str(json_path))
        firebase_admin.initialize_app(cred)
        print("✅ Firebase initialized from JSON file")
    else:
        # No credentials found
        raise FileNotFoundError(
            f"Firebase credentials not found!\n"
            f"Set FIREBASE_CREDENTIALS_JSON environment variable or create {json_path}"
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
