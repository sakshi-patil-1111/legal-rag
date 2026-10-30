import traceback
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.main import app
from app.database.database import Base
from app.models.chat import Conversation, FeatureType, Message, MessageRole
from app.middleware.auth import verify_firebase_token

# Connect to the real local DB
engine = create_engine('sqlite:///nyaay.db')
SessionLocal = sessionmaker(bind=engine)

# Dependency overrides for testing auth
class MockToken:
    def __init__(self, uid):
        self.uid = uid

def mock_auth_user1():
    return MockToken(uid="user1-uid")

def mock_auth_user2():
    return MockToken(uid="user2-uid")

def verify_deletion():
    db = SessionLocal()
    
    # 1. Create a dummy conversation owned by user1
    conv = Conversation(
        user_id="user1-uid",
        title="Dummy Delete Test",
        feature_type=FeatureType.know_kanoon
    )
    db.add(conv)
    db.commit()
    db.refresh(conv)
    
    # Add a dummy message
    msg = Message(
        conversation_id=conv.id,
        role=MessageRole.user,
        content="Test message"
    )
    db.add(msg)
    db.commit()
    
    conv_id = conv.id
    
    try:
        # Override dependency to act as user2
        app.dependency_overrides[verify_firebase_token] = mock_auth_user2
        client = TestClient(app)
        
        # 2. Test Deletion as user2 (Should fail with 404)
        print("--- Testing Deletion with Wrong User ---")
        response = client.delete(f"/api/chat/conversations/{conv_id}")
        if response.status_code == 404:
            print("[SUCCESS] Ownership verification working. User 2 cannot delete User 1's conversation.")
        else:
            print(f"[FAIL] Expected 404, got {response.status_code}")
            return False
            
        # 3. Test Deletion as user1 (Should succeed with 200)
        print("--- Testing Deletion with Correct User ---")
        app.dependency_overrides[verify_firebase_token] = mock_auth_user1
        response = client.delete(f"/api/chat/conversations/{conv_id}")
        
        if response.status_code == 200:
            print("[SUCCESS] Conversation deleted successfully.")
        else:
            print(f"[FAIL] Expected 200, got {response.status_code}")
            return False
            
        # 4. Verify cascade deletion from DB
        deleted_conv = db.query(Conversation).filter(Conversation.id == conv_id).first()
        if deleted_conv is None:
            print("[SUCCESS] Conversation removed from DB.")
        else:
            print("[FAIL] Conversation still in DB.")
            return False
            
        deleted_msg = db.query(Message).filter(Message.conversation_id == conv_id).first()
        if deleted_msg is None:
            print("[SUCCESS] Cascade deletion worked. Messages removed from DB.")
        else:
            print("[FAIL] Messages still in DB.")
            return False
            
        return True
    except Exception as e:
        print("[FAIL] Exception occurred!")
        traceback.print_exc()
        return False
    finally:
        # Clean up overrides
        app.dependency_overrides.clear()
        
        # Clean up if failed
        try:
            c = db.query(Conversation).filter(Conversation.id == conv_id).first()
            if c:
                db.delete(c)
                db.commit()
        except:
            pass
        db.close()

if __name__ == "__main__":
    verify_deletion()
