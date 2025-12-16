"""List available Gemini models"""
import os
from pathlib import Path
from dotenv import load_dotenv
import google.generativeai as genai

# Load env
env_path = Path(__file__).parent / ".env.commercial"
load_dotenv(env_path)

api_key = os.getenv("GEMINI_API_KEY")
genai.configure(api_key=api_key)

print("Available Gemini models:")
for model in genai.list_models():
    if 'generateContent' in model.supported_generation_methods:
        print(f"  - {model.name}")
