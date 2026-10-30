import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.ai.orchestrator import rag_orchestrator

def test_bridge():
    question = "My builder promised possession in 2024 but it is now 2026 and I still haven't got the flat. What can I do under RERA?"
    print(f"User Query: {question}")
    
    # We pass empty history and REASONING task type
    result = rag_orchestrator.trigger_pipeline(
        question=question,
        filters={"tenant_id": "global"},
        history=[],
        task_type="REASONING"
    )
    
    print("\n--- AI RESPONSE ---")
    print(result["answer"])
    
    print("\n--- RETRIEVED CITATIONS ---")
    for cit in result["citations"]:
        print(f"{cit['marker']}: {cit['source_name']}")

if __name__ == "__main__":
    test_bridge()
