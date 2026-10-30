import sys
import os
import time
import json

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.knowledge.reranker import reranker_service
from app.knowledge.embeddings import embedding_service
from app.knowledge.hybrid_retriever import hybrid_retriever

QUERIES = [
    ("T1_rape_consent", "My client was convicted for rape. The complainant delayed filing the FIR by 3 months, and there were no physical injuries. We have evidence of subsequent friendly WhatsApp chats showing consent."),
    ("T3_homebuyer_rera", "I paid 80 lakh to a builder for a flat in 2019. Possession was promised in 2022. The builder is claiming force majeure. I want a full refund with interest and want to stop paying EMIs."),
]

def run_benchmark():
    print("Running reranker benchmark...")
    
    # We will just test ms-marco latency and see if it's acceptable.
    # BAAI/bge-reranker-base is not downloaded. 
    # The requirement is to benchmark ms-marco and see if it's fine.
    for q_id, q_text in QUERIES:
        print(f"Query: {q_id}")
        q_emb = embedding_service.embed_query(q_text)
        
        # Get candidates (hybrid retrieve but without reranking)
        # We can just use the DB directly for testing
        from app.knowledge.vector_store import vector_store
        res = vector_store.search(q_emb, n_results=15, search_sc=True)
        candidates = res[:15]
        
        t0 = time.time()
        reranked = reranker_service.rerank(q_text, candidates, top_k=5)
        latency = time.time() - t0
        
        print(f"Latency: {latency:.4f}s")
        print("Top 3 after reranking:")
        for r in reranked[:3]:
            print(f"- {r['metadata'].get('source_name', 'Unknown')}")
        print("---")

if __name__ == '__main__':
    run_benchmark()
