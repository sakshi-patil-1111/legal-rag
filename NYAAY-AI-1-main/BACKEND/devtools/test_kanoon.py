import traceback
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.schemas.kanoon import KanoonQueryRequest
from app.services.kanoon_service import kanoon_service

engine = create_engine('sqlite:///nyaay.db')
SessionLocal = sessionmaker(bind=engine)
db = SessionLocal()
request = KanoonQueryRequest(question='Can my landlord evict me without notice?', conversation_id=None)
try:
    print("Testing query...")
    response = kanoon_service.query(request, 'mock-uid', db)
    print("Response:", response)
except Exception as e:
    traceback.print_exc()
