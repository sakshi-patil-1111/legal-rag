import traceback
from google import genai
from google.genai import types
from app.core.config import settings
import json

client = genai.Client(api_key=settings.GEMINI_API_KEY)

system_instruction = """You MUST respond strictly in the following JSON format:
{
    "answer": "Detailed explanation of the legal concept using Markdown",
    "summary": "A short one-to-two sentence summary",
    "similar_cases": "Markdown formatted section titled 'Similar Cases Verdicts' containing verdicts with reasoning in a simplified and short manner",
    "disclaimer": "This information is for educational purposes only and does not constitute legal advice. Please consult a qualified lawyer for legal matters.",
    "category": "e.g., Property Law, Constitutional Law, Criminal Law, etc."
}"""

print("Testing model generation...")
try:
    response = client.models.generate_content(
        model='gemini-2.5-flash',
        contents='Can my landlord evict me without notice?',
        config=types.GenerateContentConfig(
            system_instruction=system_instruction,
            response_mime_type="application/json",
        )
    )
    print("Response raw:", response.text)
    data = json.loads(response.text)
    print("Parsed JSON:", data.keys())
    
    from app.schemas.kanoon import KanoonQueryResponse
    # Mock conversation ID
    resp = KanoonQueryResponse(conversation_id="123", **data)
    print("Pydantic model success:", resp.conversation_id)
except Exception as e:
    traceback.print_exc()
