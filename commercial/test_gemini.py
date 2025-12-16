"""Quick test to verify Gemini API key works"""
import os
from pathlib import Path
from dotenv import load_dotenv
import google.generativeai as genai

# Load env
env_path = Path(__file__).parent.parent / ".env.commercial"
load_dotenv(env_path)

api_key = os.getenv("GEMINI_API_KEY")

print("=" * 60)
print("Gemini API Key Test")
print("=" * 60)
print(f"\nAPI Key found: {'Yes' if api_key else 'No'}")

if api_key:
    print(f"Key starts with: {api_key[:10]}...")
    print(f"Key length: {len(api_key)} characters")
    
    print("\nTesting API connection...")
    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('models/gemini-pro')
        
        response = model.generate_content("Say 'API works!'")
        
        print("✅ SUCCESS! API key is valid and working")
        print(f"Response: {response.text}")
        
    except Exception as e:
        print(f"❌ ERROR: {e}")
        print("\nThis means your API key might be invalid or there's a network issue.")
else:
    print("❌ No API key found in .env.commercial")

print("\n" + "=" * 60)
