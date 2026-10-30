import os
from google import genai
from app.core.config import settings

def verify_models():
    api_key = settings.GEMINI_API_KEY
    if not api_key:
        print("Error: GEMINI_API_KEY not found in settings.")
        return
        
    print(f"Using API Key: {api_key[:5]}...{api_key[-5:]}")
    client = genai.Client(api_key=api_key)
    
    print("\nListing available models...")
    try:
        models = client.models.list()
        generate_content_models = []
        all_models = []
        
        for model in models:
            all_models.append(model.name)
            if 'generateContent' in model.supported_actions:
                generate_content_models.append(model.name)
                
        print("\nAll Available Models:")
        for m in sorted(all_models):
            print(f" - {m}")
            
        print("\nModels supporting generateContent:")
        for m in sorted(generate_content_models):
            print(f" - {m}")
            
        if 'models/gemini-2.5-flash' in generate_content_models:
            print("\nRecommended Production Model: gemini-2.5-flash (Available!)")
        elif 'models/gemini-2.0-flash' in generate_content_models:
            print("\nRecommended Production Model: gemini-2.0-flash (Available)")
        elif 'models/gemini-1.5-flash-latest' in generate_content_models:
            print("\nRecommended Production Model: gemini-1.5-flash-latest (Available)")
        else:
            print("\nRecommended Production Model: No suitable flash model found.")
            
    except Exception as e:
        print(f"Error querying models: {e}")

if __name__ == "__main__":
    verify_models()
