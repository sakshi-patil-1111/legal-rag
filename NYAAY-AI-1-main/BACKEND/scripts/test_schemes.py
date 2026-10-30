import os
import sys
import json

sys.stdout.reconfigure(encoding='utf-8')
# Ensure backend directory is in path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.ai.orchestrator import rag_orchestrator

def run_test_query(query_text: str):
    print(f"\n=============================================")
    print(f"QUERY: {query_text}")
    print(f"=============================================")
    try:
        response = rag_orchestrator.trigger_pipeline(
            question=query_text,
            filters={}
        )
        print("\n[ANSWER]")
        print(response.get("answer", "No answer found."))
        
        print("\n[CITATIONS]")
        citations = response.get("citations", [])
        if citations:
            for c in citations:
                meta = c.get('metadata', {})
                print(f"- {c['marker']} {meta.get('scheme_name', meta.get('source_name', 'Unknown'))} (Method: {meta.get('retrieval_method', 'unknown')}, RRF: {meta.get('rrf_score', 'N/A')})")
        else:
            print("No citations.")
    except Exception as e:
        print(f"[ERROR] {e}")

if __name__ == "__main__":
    queries = [
        "Am I eligible for PMAY?",
        "What are the eligibility criteria for PM-KISAN?",
        "What government scholarships are available for college students?",
        "What documents are required for this government scheme?", # Needs context or might trigger negative case or general answer
        "What benefits does this scheme provide?", # Same
        "I am a 24-year-old student from Uttar Pradesh with a family income of ₹2 lakh. What government schemes might I be eligible for?",
        "I am a farmer with 2 acres of land. Which government schemes could I qualify for?",
        "My annual family income is ₹1.5 lakh. Are there any government education schemes I can apply for?",
        
        # Negative testing
        "I am a 30-year old government employee earning ₹50,000 per month. Am I eligible for PMAY-G?",
        "What are the eligibility criteria for the Mars Colonization Scheme?",
        "Is PM-KISAN applicable to doctors?",
    ]
    
    # Regression tests
    regression_queries = [
        "What is the punishment for murder under the BNS?",
        "Can a police officer refuse to register an FIR?"
    ]
    
    print("Running Scheme Eligibility Queries...")
    for q in queries:
        run_test_query(q)
        
    print("\nRunning Regression Queries...")
    for q in regression_queries:
        run_test_query(q)
