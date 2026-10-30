import os
import sys
import time

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.config import settings
from app.knowledge.ingestion import ingestion_pipeline
from app.ai.orchestrator import rag_orchestrator
from app.knowledge.vector_store import vector_store

def run_tests():
    print("=== NYAAY AI 2.0 FINAL VALIDATION ===")
    
    # 1. Corpus stats
    count = vector_store.collection.count()
    print(f"\n[Phase 1] Corpus Stats: Total Chunks = {count}")
    
    # 2. Upload isolation test
    print("\n[Phase 4] Upload & Chat Isolation Test")
    rental_agreement = """
    RENTAL AGREEMENT
    1. The Landlord, Mr. Sharma, agrees to rent the property at 101 MG Road to the Tenant, Mr. Verma.
    2. The rent is 20,000 INR per month.
    3. Notice period for eviction is 30 days.
    """
    try:
        ingestion_pipeline.process_document(rental_agreement, {
            "document_id": "rental_123",
            "document_type": "user_upload",
            "source_name": "rental_agreement.txt",
            "tenant_id": "user_test_999"
        })
        print("Rental agreement ingested.")
        
        start = time.time()
        res = rag_orchestrator.trigger_pipeline(
            "What is the notice period?",
            filters={"document_id": "rental_123"}
        )
        latency = time.time() - start
        print(f"Q: What is the notice period? (Latency: {latency:.2f}s)")
        print(f"A: {res.get('answer')}")
        print(f"Citations: {[c['marker'] for c in res.get('citations', [])]}")
        
    except Exception as e:
        print(f"Upload test failed: {e}")
        
    # 3. Conversational Memory Test
    print("\n[Phase 3] Conversational Memory Validation")
    history = [
        {"role": "user", "parts": [{"text": "Can a landlord evict a tenant without notice?"}]},
        {"role": "model", "parts": [{"text": "Generally, no. A notice period is required."}]}
    ]
    try:
        start = time.time()
        res = rag_orchestrator.trigger_pipeline(
            "What if they refuse to leave?",
            filters={"document_id": "rental_123"},
            history=history
        )
        latency = time.time() - start
        print(f"Follow-up Q: What if they refuse to leave? (Latency: {latency:.2f}s)")
        print(f"A: {res.get('answer')}")
    except Exception as e:
        print(f"Memory test failed: {e}")
        
    # 4. Hallucination Test
    print("\n[Phase 6] Hallucination Testing")
    try:
        start = time.time()
        res = rag_orchestrator.trigger_pipeline(
            "What is the punishment under Section 999 of the BNS?",
            filters={"tenant_id": "global"}
        )
        latency = time.time() - start
        print(f"Q: What is the punishment under Section 999 of the BNS? (Latency: {latency:.2f}s)")
        print(f"A: {res.get('answer')}")
        print(f"Citations: {[c['marker'] for c in res.get('citations', [])]}")
    except Exception as e:
        print(f"Hallucination test failed: {e}")

if __name__ == "__main__":
    run_tests()
