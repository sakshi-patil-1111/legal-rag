import os
import sys
import time

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.knowledge.hybrid_retriever import HybridRetriever

def run_perf():
    from app.knowledge.embeddings import EmbeddingService
    
    retriever = HybridRetriever()
    embedder = EmbeddingService()
    
    query = "What is the penalty for theft?"
    
    start_embed = time.time()
    embedding = embedder.get_embedding(query)
    embed_latency = (time.time() - start_embed) * 1000
    
    start_ret = time.time()
    results = retriever.search(query, query_embedding=embedding, n_results=3, where={"tenant_id": "global"})
    ret_latency = (time.time() - start_ret) * 1000
    
    print(f"Embedding Latency: {embed_latency:.2f}ms")
    print(f"Retrieval Latency: {ret_latency:.2f}ms")
    print(f"Found {len(results)} chunks.")

if __name__ == "__main__":
    run_perf()
