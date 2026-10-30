import traceback
import json
import uuid
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.schemas.kanoon import KanoonQueryRequest
from app.services.kanoon_service import kanoon_service
from app.models.chat import Conversation, Message, MessageRole

# Connect to the real local DB
engine = create_engine('sqlite:///nyaay.db')
SessionLocal = sessionmaker(bind=engine)

def verify_kanoon():
    db = SessionLocal()
    user_uid = "test-e2e-uid-kanoon"
    question = "What are my rights during police questioning in India?"
    
    print("--- 1. Testing Know Your Kanoon ---")
    print(f"Question: {question}")
    request = KanoonQueryRequest(question=question, conversation_id=None)
    
    try:
        # Initial Query
        response = kanoon_service.query(request, user_uid, db)
        print(f"Response success! Conversation ID: {response.conversation_id}")
        
        # Verify persistence
        conv = db.query(Conversation).filter(Conversation.id == response.conversation_id).first()
        if not conv:
            print("[FAIL] Conversation not saved.")
            return False
            
        messages = sorted(conv.messages, key=lambda m: m.created_at)
        if len(messages) < 2:
            print(f"[FAIL] Expected at least 2 messages, found {len(messages)}.")
            return False
            
        user_msg = messages[0]
        assistant_msg = messages[-1]
        
        if user_msg.role != MessageRole.user or user_msg.content != question:
            print("[FAIL] User message incorrectly persisted.")
            return False
            
        try:
            assistant_content = json.loads(assistant_msg.content)
            if "answer" not in assistant_content:
                print("[FAIL] Assistant message missing 'answer' field.")
                return False
        except:
            print("[FAIL] Assistant message is not valid JSON.")
            return False
            
        print("[SUCCESS] Kanoon query processed and persisted correctly!")
        print("Summary of answer:", response.summary)
        
        # Test Follow-up
        print("\n--- Testing Follow-up Query ---")
        followup_req = KanoonQueryRequest(question="Can you summarize that in one sentence?", conversation_id=response.conversation_id)
        followup_resp = kanoon_service.query(followup_req, user_uid, db)
        
        db.refresh(conv)
        if len(conv.messages) < 4:
             print("[FAIL] Follow-up messages not persisted.")
             return False
        print("[SUCCESS] Follow-up query processed and persisted correctly!")
        return True
    except Exception as e:
        print("[FAIL] Exception occurred!")
        traceback.print_exc()
        return False
    finally:
        db.close()

if __name__ == "__main__":
    kanoon_success = verify_kanoon()
    
    if kanoon_success:
        print("\nAll Kanoon tests passed. Run Upload chat tests separately if needed.")
