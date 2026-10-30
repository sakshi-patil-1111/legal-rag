import os
import sys

sys.stdout.reconfigure(encoding='utf-8')
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.ai.orchestrator import rag_orchestrator
import json

def run_test(query: str):
    print(f"Testing Query: {query}")
    result = rag_orchestrator.trigger_pipeline(query)
    
    citations = result.get("citations", [])
    if not citations:
        print("No citations found!")
        return
        
    print(f"Total citations: {len(citations)}")
    for cit in citations[:3]:
        print(f"  {cit['marker']} {cit['source_name']}")
        
    print("-" * 50)

if __name__ == "__main__":
    queries = [
        "What is the eligibility for Post Matric Scholarship for SC Students?",
        "Can a landlord unilaterally forfeit security deposit?"
    ]
    for q in queries:
        run_test(q)
