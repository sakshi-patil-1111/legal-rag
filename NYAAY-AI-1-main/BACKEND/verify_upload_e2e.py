import traceback
import json
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.schemas.upload_chat import ChatQueryRequest
from app.services.upload_chat_service import upload_chat_service
from app.models.chat import Conversation, Message, MessageRole
from app.models.document import Document
import uuid

engine = create_engine('sqlite:///nyaay.db')
SessionLocal = sessionmaker(bind=engine)

def verify_upload():
    db = SessionLocal()
    user_uid = "test-e2e-uid-upload"
    document_content = "This is a rental agreement. Rent is $1000 per month."
    doc_id = str(uuid.uuid4())
    question = "What is the rent?"
    
    # Create Document in DB first
    new_doc = Document(
        id=doc_id,
        user_uid=user_uid,
        filename="test_rent.pdf",
        filepath="test_filepath.pdf",
        extracted_text=document_content,
        summary="Rental agreement",
        pages=1
    )
    db.add(new_doc)
    db.commit()
    
    print("--- 1. Testing Upload Chat ---")
    request = ChatQueryRequest(
        conversation_id=None,
        question=question,
        document_id=doc_id
    )
    
    try:
        response = upload_chat_service.query(request, db, user_uid)
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
            
        print("[SUCCESS] Upload Chat query processed and persisted correctly!")
        print("Answer:", response.answer)
        
        # Test Follow-up
        print("\n--- Testing Follow-up Query ---")
        followup_req = ChatQueryRequest(
            conversation_id=response.conversation_id,
            question="Is there anything else I should know?",
            document_id=doc_id
        )
        followup_resp = upload_chat_service.query(followup_req, db, user_uid)
        
        db.refresh(conv)
        if len(conv.messages) < 4:
             print("[FAIL] Follow-up messages not persisted.")
             return False
        print("[SUCCESS] Follow-up query processed and persisted correctly!")
        print("Answer:", followup_resp.answer)
        return True
    except Exception as e:
        print("[FAIL] Exception occurred!")
        traceback.print_exc()
        return False
    finally:
        db.close()

if __name__ == "__main__":
    success = verify_upload()
    if success:
        print("\nAll Upload Chat tests passed.")
