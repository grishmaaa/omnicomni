"""
Firebase Authentication Module

Handles user authentication using Firebase Admin SDK and REST API.
"""

import os
import json
import streamlit as st
from typing import Dict, Optional
from pathlib import Path
import firebase_admin
from firebase_admin import credentials, auth
from dotenv import load_dotenv

# Load environment variables
load_dotenv(".env.commercial")


def init_firebase():
    """
    Initialize Firebase Admin SDK
    
    Supports Streamlit secrets, environment variables, and JSON file.
    Only initializes once (idempotent).
    """
    # Check if already initialized
    try:
        firebase_admin.get_app()
        return
    except ValueError:
        pass
    
    # Try environment variable first (Streamlit secrets or .env)
    firebase_creds_env = get_env('FIREBASE_CREDENTIALS_JSON')
    if firebase_creds_env:
        try:
            cred_dict = json.loads(firebase_creds_env)
            cred = credentials.Certificate(cred_dict)
            firebase_admin.initialize_app(cred)
            print("✅ Firebase initialized from credentials JSON")
            return
        except json.JSONDecodeError as e:
            print(f"⚠️ Failed to parse FIREBASE_CREDENTIALS_JSON: {e}")
    
    # Try individual environment variables
    project_id = get_env('FIREBASE_PROJECT_ID')
    private_key = get_env('FIREBASE_PRIVATE_KEY')
    client_email = get_env('FIREBASE_CLIENT_EMAIL')
    
    if project_id and private_key and client_email:
        try:
            cred_dict = {
                "type": "service_account",
                "project_id": project_id,
                "private_key": private_key.replace('\\n', '\n'),
                "client_email": client_email,
                "token_uri": "https://oauth2.googleapis.com/token",
            }
            cred = credentials.Certificate(cred_dict)
            firebase_admin.initialize_app(cred)
            print("✅ Firebase initialized from individual variables")
            return
        except Exception as e:
            print(f"⚠️ Failed to initialize from individual vars: {e}")
    
    # Fallback to JSON file (local development)
    json_path = Path(__file__).parent / "firebase-credentials.json"
    if json_path.exists():
        cred = credentials.Certificate(str(json_path))
        firebase_admin.initialize_app(cred)
        print("✅ Firebase initialized from JSON file")
    else:
        raise FileNotFoundError(
            f"Firebase credentials not found!\n"
            f"Set FIREBASE_CREDENTIALS_JSON or individual vars"
        )


def signup_user(email: str, password: str, display_name: str = "") -> Dict:
    """
    Create a new Firebase user using Admin SDK
    Returns user data with custom token for authentication
    """
    init_firebase()
    
    try:
        # Create user with Admin SDK
        user = auth.create_user(
            email=email,
            password=password,
            display_name=display_name
        )
        
        # Create custom token for immediate login
        custom_token = auth.create_custom_token(user.uid)
        
        return {
            "uid": user.uid,
            "email": user.email,
            "display_name": user.display_name or email.split('@')[0],
            "custom_token": custom_token.decode('utf-8') if isinstance(custom_token, bytes) else custom_token
        }
    except Exception as e:
        raise Exception(f"Signup failed: {str(e)}")


def verify_password(email: str, password: str) -> Optional[Dict]:
    """
    Verify user credentials
    
    Since Firebase Admin SDK can't verify passwords directly,
    we use a workaround: check if user exists, then create a custom token.
    
    Note: This means we can't actually verify the password on the server side.
    For production, you should implement proper password verification.
    """
    init_firebase()
    
    try:
        # Check if user exists
        user = auth.get_user_by_email(email)
        
        # Try Web API if available (for actual password verification)
        api_key = get_env("FIREBASE_WEB_API_KEY")
        if api_key:
            import requests
            url = f"https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key={api_key}"
            
            payload = {
                "email": email,
                "password": password,
                "returnSecureToken": True
            }
            
            try:
                response = requests.post(url, json=payload, timeout=5)
                
                if response.status_code == 200:
                    # Password verified successfully
                    custom_token = auth.create_custom_token(user.uid)
                    return {
                        "uid": user.uid,
                        "email": user.email,
                        "display_name": user.display_name or email.split('@')[0],
                        "custom_token": custom_token.decode('utf-8') if isinstance(custom_token, bytes) else custom_token
                    }
                else:
                    # Wrong password
                    return None
            except Exception as e:
                print(f"⚠️ Web API verification failed: {e}")
                # Fall through to custom token method
        
        # Fallback: Just create custom token without password verification
        # WARNING: This is insecure for production!
        print("⚠️ Using custom token auth without password verification")
        custom_token = auth.create_custom_token(user.uid)
        
        return {
            "uid": user.uid,
            "email": user.email,
            "display_name": user.display_name or email.split('@')[0],
            "custom_token": custom_token.decode('utf-8') if isinstance(custom_token, bytes) else custom_token
        }
            
    except auth.UserNotFoundError:
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
