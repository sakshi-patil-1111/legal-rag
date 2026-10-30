import json
import sys
import os
import time

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.ai.orchestrator import rag_orchestrator
from app.knowledge.embeddings import embedding_service
from app.knowledge.hybrid_retriever import hybrid_retriever
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

def capture_baseline():
    print("Capturing Baseline Metrics...")
    
    # Load BM25 explicitly
    bm25_manager.get_index("global")
    
    metrics = []
    
    for query_id, query_text in QUERIES:
        print(f"Processing {query_id}...")
        try:
            start_time = time.time()
            expanded_query = rag_orchestrator._analyze_and_expand_query(query_text, [])
            analysis_time = time.time() - start_time
            
            emb_start = time.time()
            query_emb = embedding_service.embed_query(expanded_query)
            emb_time = time.time() - emb_start
            
            # Predict domain
            from app.ai.domain_classifier import domain_classifier
            domain_predictions = domain_classifier.predict_domain(expanded_query)
            predicted_domains = domain_predictions.get("domains", {})
            doc_type_priority = domain_predictions.get("document_type_priority", "any")

            ret_start = time.time()
            chunks = hybrid_retriever.search(
                query=expanded_query, 
                query_embedding=query_emb, 
                n_results=10, 
                where=None,
                predicted_domains=predicted_domains,
                document_type_priority=doc_type_priority
            )
            ret_time = time.time() - ret_start
            
            # Record Top 10 stats
            top_10 = []
            sc_count = 0
            domains_found = []
            
            for rank, chunk in enumerate(chunks):
                meta = chunk.get("metadata", {})
                source = meta.get("source_name", "Unknown")
                domain = meta.get("legal_domain", "Unknown")
                ctype = meta.get("document_type", "Unknown")
                court = meta.get("court_level", "Unknown")
                
                domains_found.append(domain)
                if court == "Supreme Court" or ctype == "judgment" or "Supreme Court" in source:
                    sc_count += 1
                
                top_10.append({
                    "rank": rank + 1,
                    "source": source,
                    "domain": domain,
                    "type": ctype,
                    "court": court,
                    "rrf_score": meta.get("rrf_score", 0.0),
                    "method": meta.get("retrieval_method", "unknown")
                })
            
            metrics.append({
                "query_id": query_id,
                "query_text": query_text,
                "latency_analysis": analysis_time,
                "latency_embedding": emb_time,
                "latency_retrieval": ret_time,
                "total_time": analysis_time + emb_time + ret_time,
                "sc_chunks_in_top10": sc_count,
                "top_10": top_10
            })
            
        except Exception as e:
            print(f"Error on {query_id}: {e}")
            
    with open("scripts/baseline_metrics.json", "w") as f:
        json.dump(metrics, f, indent=4)
    print("Baseline metrics saved to scripts/baseline_metrics.json")

if __name__ == '__main__':
    capture_baseline()
