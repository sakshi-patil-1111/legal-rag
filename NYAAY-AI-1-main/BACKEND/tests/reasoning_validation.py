import os
import sys
import time

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.services.reasoning_service import reasoning_service, ReasoningRequest

def run_tests():
    print("=== SPRINT 6: LEGAL REASONING ENGINE VALIDATION ===")
    
    tests = [
        {
            "name": "Criminal Law Scenario (Theft)",
            "request": ReasoningRequest(
                user_facts="Rohan broke into Amit's house at night, stole jewelry worth 5 lakhs, and ran away. He was caught on CCTV.",
                tenant_id="global"
            )
        },
        {
            "name": "Civil Law Scenario (Breach of Contract)",
            "request": ReasoningRequest(
                user_facts="I signed a contract with a builder to construct my house by June 2024. I paid 50% advance. The builder abandoned the project in March and is not returning my calls.",
                tenant_id="global"
            )
        },
        {
            "name": "Hallucination Test (Alien Invasion Law)",
            "request": ReasoningRequest(
                user_facts="Aliens landed in my backyard and destroyed my garden. I want to sue them under the Intergalactic Defense Treaty of 2026.",
                tenant_id="global"
            )
        }
    ]

    for test in tests:
        print(f"\n[Running] {test['name']}")
        start_time = time.time()
        
        try:
            response = reasoning_service.generate_analysis(test['request'])
            latency = time.time() - start_time
            
            print(f"Latency: {latency:.2f} seconds")
            
            citations = response.get('citations', [])
            print(f"Citations Retrieved: {len(citations)}")
            for c in citations:
                print(f"  - {c['marker']}: {c['metadata'].get('source_name')} - {c['metadata'].get('section')}")
            
            content_preview = response.get('content', '')[:500].replace('\n', ' ')
            print(f"Content Preview: {content_preview}...")
            
        except Exception as e:
            print(f"Error during {test['name']}: {e}")

if __name__ == "__main__":
    run_tests()
