import os
import sys
import time

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.services.drafting_service import drafting_service, DraftRequest

def run_tests():
    print("=== SPRINT 5.5: DRAFTING ENGINE VALIDATION ===")
    
    tests = [
        {
            "name": "Test 1: Consumer Complaint (Standard)",
            "request": DraftRequest(
                draft_type="Consumer Complaint",
                user_facts="I bought a defective washing machine from ElectroMart on June 1st for 15,000 INR. They are refusing to replace it despite a 1-year warranty.",
                tenant_id="global"
            )
        },
        {
            "name": "Test 2: Police Complaint (Criminal Context Retrieval)",
            "request": DraftRequest(
                draft_type="Police Complaint",
                user_facts="Rohan broke into my house at night and stole my laptop. I have CCTV footage.",
                tenant_id="global"
            )
        },
        {
            "name": "Test 3: Hallucination/Stress Test (Fake Law)",
            "request": DraftRequest(
                draft_type="Legal Notice",
                user_facts="My neighbor is violating the Intergalactic Space Property Act of 2025 by parking his UFO on my roof. I want to sue him for 1 million space credits.",
                tenant_id="global"
            )
        }
    ]

    for test in tests:
        print(f"\n[Running] {test['name']}")
        start_time = time.time()
        
        try:
            response = drafting_service.generate_draft(test['request'])
            latency = time.time() - start_time
            
            print(f"Latency: {latency:.2f} seconds")
            print(f"Draft Type Generated: {response.get('draft_type')}")
            
            citations = response.get('citations', [])
            print(f"Citations Retrieved: {len(citations)}")
            for c in citations:
                print(f"  - {c['marker']}: {c['metadata'].get('source_name')} - {c['metadata'].get('section')}")
            
            content_preview = response.get('content', '')[:300].replace('\n', ' ')
            print(f"Content Preview: {content_preview}...")
            
        except Exception as e:
            print(f"Error during {test['name']}: {e}")

if __name__ == "__main__":
    run_tests()
