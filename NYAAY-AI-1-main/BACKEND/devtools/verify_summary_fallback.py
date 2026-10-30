import traceback
import json
from unittest.mock import patch
from app.services.document_service import document_service

def test_summary_fallback():
    print("--- Testing AI Summary Fallback ---")
    
    # Mock the _generate_summary so it forces an exception to test the fallback text
    # Actually, let's test the document_service._generate_summary directly by mocking the client
    
    class MockModels:
        def generate_content(self, *args, **kwargs):
            raise Exception("429 RESOURCE_EXHAUSTED Quota exceeded")
            
    class MockClient:
        models = MockModels()
        
    # Replace the real client with the mock
    original_client = document_service.client
    document_service.client = MockClient()
    
    try:
        print("Calling _generate_summary with mock exception...")
        result = document_service._generate_summary("This is a test legal document.")
        
        print("\n[RESULT]")
        print(result)
        
        if "temporarily unavailable" in result:
            print("\n[SUCCESS] Fallback text returned cleanly without JSON or Exceptions!")
            return True
        else:
            print("\n[FAIL] Fallback text did not match expected user-friendly string.")
            return False
            
    except Exception as e:
        print("[FAIL] Unexpected exception bubbled up:")
        traceback.print_exc()
        return False
    finally:
        document_service.client = original_client

if __name__ == "__main__":
    test_summary_fallback()
