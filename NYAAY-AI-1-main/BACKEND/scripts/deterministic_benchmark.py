import json
import sys
import os
import time

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.knowledge.embeddings import embedding_service
from app.knowledge.hybrid_retriever import hybrid_retriever
from app.knowledge.bm25_manager import bm25_manager
import torch

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

def run_benchmark():
    # Pin threads for consistent measurement
    torch.set_num_threads(os.cpu_count() or 1)
    
    print("Capturing Deterministic Baseline Metrics...")
    bm25_manager.get_index("global")
    
    metrics = []
    total_sc_chunks = 0
    total_retrieval_time = 0.0
    
    for query_id, query_text in QUERIES:
        try:
            emb_start = time.time()
            query_emb = embedding_service.embed_query(query_text)
            emb_time = time.time() - emb_start
            
            # Predict domain is relatively cheap, but let's mock it for perfect determinism?
            # Or use it. It's deterministic.
            from app.ai.domain_classifier import domain_classifier
            domain_predictions = domain_classifier.predict_domain(query_text)
            predicted_domains = domain_predictions.get("domains", {})
            doc_type_priority = domain_predictions.get("document_type_priority", "any")

            ret_start = time.time()
            chunks = hybrid_retriever.search(
                query=query_text, 
                query_embedding=query_emb, 
                n_results=10, 
                where=None,
                predicted_domains=predicted_domains,
                document_type_priority=doc_type_priority
            )
            ret_time = time.time() - ret_start
            
            sc_count = 0
            for chunk in chunks:
                meta = chunk.get("metadata", {})
                source = meta.get("source_name", "Unknown")
                ctype = meta.get("document_type", "Unknown")
                court = meta.get("court_level", "Unknown")
                
                if court == "Supreme Court" or ctype == "judgment" or "Supreme Court" in source:
                    sc_count += 1
            
            total_sc_chunks += sc_count
            total_retrieval_time += (emb_time + ret_time)
            
            metrics.append({
                "query_id": query_id,
                "sc_count": sc_count,
                "latency": emb_time + ret_time
            })
            
        except Exception as e:
            print(f"Error on {query_id}: {e}")
            
    with open("scripts/deterministic_metrics.json", "w") as f:
        json.dump(metrics, f, indent=4)
        
    avg_latency = total_retrieval_time / len(QUERIES)
    avg_sc = total_sc_chunks / len(QUERIES)
    print(f"Deterministic Benchmark Complete! Avg Latency: {avg_latency:.2f}s, Avg SC Chunks: {avg_sc}")
    return avg_latency, avg_sc

if __name__ == '__main__':
    run_benchmark()
