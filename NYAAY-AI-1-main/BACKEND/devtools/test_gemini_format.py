import traceback
from google import genai
from app.core.config import settings

client = genai.Client(api_key=settings.GEMINI_API_KEY)

print("Testing str")
try:
    client.models.generate_content(model='gemini-2.5-flash', contents='hello')
except Exception as e:
    traceback.print_exc()

print("Testing dict")
try:
    client.models.generate_content(model='gemini-2.5-flash', contents=[{'role': 'user', 'parts': [{'text': 'hello'}]}])
except Exception as e:
    traceback.print_exc()
