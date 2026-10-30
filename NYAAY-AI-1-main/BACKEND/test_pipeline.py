import os
import sys

# Ensure backend directory is in path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.core.config import settings
from app.knowledge.ingestion import ingestion_pipeline
from app.ai.orchestrator import rag_orchestrator
from app.knowledge.vector_store import vector_store

def verify_pipeline():
    print("=== Phase 1: Ingestion Pipeline ===")
    sample_text = """
The Bharatiya Nyaya Sanhita (BNS) is the criminal code of India.
Section 101: Murder. Whoever commits murder shall be punished with death or imprisonment for life, and shall also be liable to fine.
Section 102: Culpable homicide not amounting to murder.
Section 103: Punishment for murder.
This is a test document to verify the chunking, embedding, and storage pipeline.
"""
    
    metadata = {
        "document_id": "test_doc_1",
        "document_type": "statute",
        "source_name": "Test Law",
        "tenant_id": "global"
    }
    
    try:
        print("Triggering ingestion pipeline...")
        ingestion_pipeline.process_document(sample_text, metadata)
        print("Ingestion Successful!")
    except Exception as e:
        print(f"Ingestion Failed: {e}")
        return False
        
    print("\n=== Phase 2: ChromaDB Verification ===")
    try:
        count = vector_store.collection.count()
        print(f"Total Chunks in DB: {count}")
        if count == 0:
            print("DB is empty after ingestion!")
            return False
            
        items = vector_store.collection.peek(1)
        print("Sample Metadata stored:", items['metadatas'][0])
    except Exception as e:
        print(f"ChromaDB Check Failed: {e}")
        return False
        
    print("\n=== Phase 3: Retrieval & Generation ===")
    try:
        print("Asking question: 'What is the punishment for murder?'")
        response = rag_orchestrator.trigger_pipeline(
            question="What is the punishment for murder?",
            filters={"tenant_id": "global"}
        )
        print("\nAnswer received:")
        print(response.get("answer"))
        print("\nCitations:")
        for c in response.get("citations", []):
            print(f"- {c['marker']} {c['metadata'].get('source_name')}: {c['text_snippet'][:50]}...")
            
    except Exception as e:
        print(f"Retrieval & Generation Failed: {e}")
        import traceback
        traceback.print_exc()
        return False
        
    return True

if __name__ == "__main__":
    success = verify_pipeline()
    if success:
        print("\n[SUCCESS] All core pipeline components verified successfully.")
    else:
        print("\n[FAILED] Pipeline verification failed.")
