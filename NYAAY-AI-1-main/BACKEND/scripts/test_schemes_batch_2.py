import os
import sys

sys.stdout.reconfigure(encoding='utf-8')
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
        "Who is eligible for MGNREGA?",
        "What are the eligibility requirements under NFSA?",
        "Who can receive PMMVY benefits?",
        "Who is eligible for NSAP?",
        "What are the eligibility criteria for IGNOAPS?",
        "Who can apply for PMAY Urban?",
        "Who is eligible for PMKVY?",
        "Who can claim benefits under PMFBY?",
        "Who can open an account under PMJDY?",
        "Who is eligible for PMJJBY?",
        "Who is eligible for PMSBY?",
        "Who can apply for PMEGP?",
        "Who is eligible under Jal Jeevan Mission?",
        "What are the beneficiaries covered under Swachh Bharat Mission?",
        "What disability-related benefits and eligibility information are available through UDID and the relevant official schemes?"
    ]
    
    print("Running Batch 2 Scheme Eligibility Queries...")
    for q in queries:
        run_test_query(q)
