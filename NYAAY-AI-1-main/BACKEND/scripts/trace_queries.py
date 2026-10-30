import os
import sys
import json

sys.stdout.reconfigure(encoding='utf-8')
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.ai.orchestrator import rag_orchestrator
from app.knowledge.hybrid_retriever import hybrid_retriever
from app.knowledge.embeddings import embedding_service
from app.knowledge.vector_store import vector_store
from app.knowledge.bm25_manager import bm25_manager
from app.ai.domain_classifier import domain_classifier

def trace_query(question: str, name: str):
    print(f"\n=============================================")
    print(f"TRACE: {name}")
    print(f"QUERY: {question}")
    print(f"=============================================")
    
    is_complex = rag_orchestrator._estimate_complexity(question)
    print(f"Complexity: {'COMPLEX' if is_complex else 'SIMPLE'}")
    
    if is_complex:
        query_analysis = rag_orchestrator._analyze_query_structured(question, [])
        print(f"Structured Analysis: {json.dumps(query_analysis, indent=2)}")
        
        search_query = query_analysis.get("sub_queries", [question])[0]
        predicted_domains = query_analysis.get("domains", {})
        doc_type_priority = "any"
        explicit_sc = query_analysis.get("explicit_sc_requested", False)
        
        print("Sub queries:")
        for sq in query_analysis.get("sub_queries", []):
            print(f"- {sq}")
            
        print("\nTracing first sub-query inside multi_query_retrieve...")
        sq0 = query_analysis.get("sub_queries", [question])[0]
        emb = embedding_service.embed_query(sq0)
        
        res = hybrid_retriever.search(
            query=sq0,
            query_embedding=emb,
            n_results=10,
            where={},
            predicted_domains=predicted_domains,
            document_type_priority=doc_type_priority
        )
        print(f"Top 3 results for first subquery:")
        for i, r in enumerate(res[:3]):
            print(f"  [{i}] {r['metadata'].get('source_name', 'Unknown')} (Score: {r['metadata'].get('rrf_score')})")
            
    else:
        expanded = rag_orchestrator._analyze_and_expand_query(question, [])
        print(f"Expanded Query: {expanded}")
        
        domain_preds = domain_classifier.predict_domain(expanded)
        print(f"Domain Prediction: {json.dumps(domain_preds, indent=2)}")
        predicted_domains = domain_preds.get("domains", {})
        doc_type_priority = domain_preds.get("document_type_priority", "any")
        
        emb = embedding_service.embed_query(expanded)
        
        res = hybrid_retriever.search(
            query=expanded,
            query_embedding=emb,
            n_results=10,
            where={},
            predicted_domains=predicted_domains,
            document_type_priority=doc_type_priority
        )
        print(f"Top 3 results:")
        for i, r in enumerate(res[:3]):
            print(f"  [{i}] {r['metadata'].get('source_name', 'Unknown')} (Score: {r['metadata'].get('rrf_score')})")
            
    print("\n--- FINAL PIPELINE RUN ---")
    final_res = rag_orchestrator.trigger_pipeline(question, filters={})
    print("\nANSWER:")
    print(final_res.get("answer"))
    print("\nCITATIONS:")
    for c in final_res.get("citations", []):
        print(f"- {c['source_name']}")

if __name__ == "__main__":
    q_a = "My landlord has refused to return my ₹60,000 security deposit after I moved out, claiming that the entire amount was used for repairs. He has not provided any bills or proof of the alleged damage. I have the rental agreement, photographs of the flat from the day I moved out, and proof that I paid the deposit. What are my legal rights, and what steps can I take to recover the deposit?"
    q_b = "Can my landlord evict me without notice?"
    
    trace_query(q_a, "QUERY A (Security Deposit)")
    trace_query(q_b, "QUERY B (Eviction Notice)")
