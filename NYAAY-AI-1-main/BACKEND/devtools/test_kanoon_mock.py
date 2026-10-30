import traceback
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.schemas.kanoon import KanoonQueryRequest
from app.services.kanoon_service import kanoon_service
from app.models.chat import Conversation, Message, MessageRole
import json

engine = create_engine('sqlite:///nyaay.db')
SessionLocal = sessionmaker(bind=engine)
db = SessionLocal()

class MockResponse:
    def __init__(self):
        self.text = json.dumps({
            "answer": "This is a mock answer.",
            "summary": "Mock summary.",
            "similar_cases": "Mock cases.",
            "disclaimer": "Mock disclaimer.",
            "category": "General"
        })

def mock_generate_content(*args, **kwargs):
    return MockResponse()

kanoon_service.client.models.generate_content = mock_generate_content

request = KanoonQueryRequest(question='Can my landlord evict me without notice?', conversation_id=None)
try:
    print("Testing query with mock Gemini...")
    response = kanoon_service.query(request, 'mock-uid', db)
    print("Response:", response)
except Exception as e:
    traceback.print_exc()
