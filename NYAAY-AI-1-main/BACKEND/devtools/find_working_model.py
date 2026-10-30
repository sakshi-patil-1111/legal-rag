import traceback
from google import genai
from google.genai import types
from app.core.config import settings
import json

client = genai.Client(api_key=settings.GEMINI_API_KEY)

models_to_test = [
    'gemini-3.5-flash',
    'gemini-2.5-pro',
    'gemini-2.0-flash-lite',
    'gemini-flash-lite-latest',
    'gemini-pro-latest'
]

for model in models_to_test:
    print(f"Testing model: {model}...")
    try:
        response = client.models.generate_content(
            model=model,
            contents='Say hello',
        )
        print(f"[SUCCESS] {model} returned: {response.text}")
    except Exception as e:
        print(f"[FAIL] {model} failed with: {str(e)[:150]}")
