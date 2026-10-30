import json
import sys
import os
import time

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.ai.orchestrator import rag_orchestrator
from app.knowledge.bm25_manager import bm25_manager

QUERIES = [
    # 5 Hard Queries
    ("T1_rape_consent", "My client was convicted for rape. The complainant delayed filing the FIR by 3 months, and there were no physical injuries. We have evidence of subsequent friendly WhatsApp chats showing consent. Are there Supreme Court judgments on this?"),
    ("T2_illegal_detention", "Police arrested my brother yesterday evening and have not produced him before a magistrate. They have held him for more than 24 hours without a warrant. What are his rights? Are there Supreme Court precedent?"),
    ("T3_homebuyer_rera", "I paid 80 lakh to a builder for a flat in 2019. Possession was promised in 2022. The builder is claiming force majeure. I want a full refund with interest and want to stop paying EMIs. What does RERA say and are there Supreme Court judgments?"),
    ("T4_natural_justice", "A government regulatory authority cancelled my business licence without issuing any show cause notice or giving me a chance to be heard. They are offering a post-decisional hearing. Is this a violation of natural justice? I need Supreme Court precedent."),
    ("T5_adverse_possession", "My family has been living on a piece of land since 1985. The original owner never asked us to leave, but now they are filing a case. Can we claim adverse possession if our possession was permissive? Any Supreme Court judgment?"),
    
    # 5 Simple Queries
    ("S1_anticipatory_bail", "What are the conditions for granting anticipatory bail?"),
    ("S2_murder", "What is the difference between murder and culpable homicide under Indian law?"),
    ("S3_fir_refusal", "Police refused to register my FIR. What can I do?"),
    ("S4_consumer_defective", "I bought a defective product. Under the Consumer Protection Act, what rights do I have and which commission should I approach?"),
    ("S5_fundamental_rights", "What are the fundamental rights regarding freedom of speech and expression in India?")
]

def run_final():
    print("Capturing Final Metrics...")
    
    bm25_manager.get_index("global")
    
    metrics = []
    
    for query_id, query_text in QUERIES:
        print(f"Processing {query_id}...")
        try:
            start_time = time.time()
            result = rag_orchestrator.trigger_pipeline(query_text, task_type="CIVIC")
            total_time = time.time() - start_time
            
            citations = result.get("citations", [])
            sc_count = 0
            for cit in citations:
                if "Supreme Court" in cit.get("source_name", "") or cit.get("metadata", {}).get("court_level") == "Supreme Court":
                    sc_count += 1
            
            metrics.append({
                "query_id": query_id,
                "latency_total": total_time,
                "sc_citations_used": sc_count,
                "confidence_score": result.get("advanced_metadata", {}).get("reasoning_confidence_score"),
                "answer": result.get("answer", "")
            })
            
        except Exception as e:
            print(f"Error on {query_id}: {e}")
            
    with open("scripts/final_metrics.json", "w") as f:
        json.dump(metrics, f, indent=4)
    print("Final metrics saved to scripts/final_metrics.json")

if __name__ == '__main__':
    run_final()
