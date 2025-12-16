"""
Quick test script to verify Groq API key works
"""

import os
from dotenv import load_dotenv
from groq import Groq

# Load environment
load_dotenv(".env.commercial")

api_key = os.getenv("GROQ_API_KEY")

print("=" * 60)
print("Groq API Key Test")
print("=" * 60)
print(f"\nAPI Key found: {'Yes' if api_key else 'No'}")

if api_key:
    print(f"Key starts with: {api_key[:10]}...")
    print(f"Key length: {len(api_key)} characters")
    
    print("\nTesting API connection...")
    try:
        client = Groq(api_key=api_key)
        
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": "Say 'API works!'"}],
            max_tokens=10
        )
        
        print("✅ SUCCESS! API key is valid and working")
        print(f"Response: {response.choices[0].message.content}")
        
    except Exception as e:
        print(f"❌ ERROR: {e}")
        print("\nThis means your API key is still restricted or invalid.")
else:
    print("❌ No API key found in .env.commercial")

print("\n" + "=" * 60)
