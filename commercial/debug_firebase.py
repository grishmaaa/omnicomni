"""
Debug script to verify Firebase credentials are loaded correctly in Streamlit Cloud
Add this to your app temporarily to see what's happening
"""

import streamlit as st
import os
import json

st.title("🔍 Firebase Credentials Debug")

st.write("### Environment Variables Check")

# Check DATABASE_URL
db_url = os.getenv("DATABASE_URL")
st.write(f"✅ DATABASE_URL: {'Set' if db_url else '❌ Missing'}")
if db_url:
    st.code(db_url[:50] + "...")

# Check Firebase Web API Key
web_key = os.getenv("FIREBASE_WEB_API_KEY")
st.write(f"{'✅' if web_key else '❌'} FIREBASE_WEB_API_KEY: {'Set' if web_key else 'Missing'}")
if web_key:
    st.code(web_key)

# Check Firebase Credentials JSON
creds_json = os.getenv("FIREBASE_CREDENTIALS_JSON")
st.write(f"{'✅' if creds_json else '❌'} FIREBASE_CREDENTIALS_JSON: {'Set' if creds_json else 'Missing'}")

if creds_json:
    try:
        creds_dict = json.loads(creds_json)
        st.write("**Parsed JSON fields:**")
        for key in creds_dict.keys():
            if key == "private_key":
                st.write(f"- {key}: {creds_dict[key][:50]}...")
            else:
                st.write(f"- {key}: {creds_dict[key]}")
    except Exception as e:
        st.error(f"❌ Failed to parse JSON: {e}")
        st.code(creds_json[:200])

# Check individual vars
st.write("### Individual Firebase Variables")
project_id = os.getenv("FIREBASE_PROJECT_ID")
client_email = os.getenv("FIREBASE_CLIENT_EMAIL")
private_key = os.getenv("FIREBASE_PRIVATE_KEY")

st.write(f"{'✅' if project_id else '❌'} FIREBASE_PROJECT_ID: {project_id or 'Missing'}")
st.write(f"{'✅' if client_email else '❌'} FIREBASE_CLIENT_EMAIL: {client_email or 'Missing'}")
st.write(f"{'✅' if private_key else '❌'} FIREBASE_PRIVATE_KEY: {'Set' if private_key else 'Missing'}")

if private_key:
    st.code(private_key[:100] + "...")

st.write("---")
st.write("**Next step:** If any values show as 'Missing', add them to Streamlit secrets")
st.write("**If JSON parsing fails:** Check for syntax errors in FIREBASE_CREDENTIALS_JSON")
