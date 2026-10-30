import asyncio
import sys
import os

# Add BACKEND to sys.path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from app.knowledge.embeddings import embedding_service
from app.knowledge.hybrid_retriever import hybrid_retriever
from app.knowledge.bm25_manager import bm25_manager
from app.knowledge.vector_store import vector_store
from app.ai.orchestrator import rag_orchestrator
import nltk

async def main():
    query = "A police officer refuses to register my FIR even though my laptop was stolen. What legal remedies are available?"
    print(f"Original Query: {query}")
    
    rewritten = rag_orchestrator._rewrite_query(query, [])
    print(f"Rewritten Query: {rewritten}")
    
    # Extract dense and sparse separately
    query_emb = embedding_service.embed_query(rewritten)
    
    # Fetch BM25 index
    bm25, corpus_ids, corpus_docs, corpus_metadatas = bm25_manager.get_index("global")
    if not bm25:
        print("BM25 index not loaded.")
        return
        
    tokenized_query = nltk.word_tokenize(rewritten.lower())
    sparse_scores = bm25.get_scores(tokenized_query)
    sparse_ranking = sorted(range(len(sparse_scores)), key=lambda i: sparse_scores[i], reverse=True)
    
    print("\n--- BM25 Top 20 ---")
    for i in range(min(20, len(sparse_ranking))):
        idx = sparse_ranking[i]
        score = sparse_scores[idx]
        if score > 0:
            doc_id = corpus_ids[idx]
            meta = corpus_metadatas[idx]
            print(f"Rank {i+1} | Score: {score:.4f} | ID: {doc_id} | Source: {meta.get('source_name', 'Unknown')} | Section: {meta.get('section_name', 'Unknown')}")
            
    print("\n--- Dense Top 20 ---")
    dense_results = vector_store.search(query_emb, n_results=20, where={"tenant_id": "global"})
    for i, res in enumerate(dense_results):
        meta = res["metadata"]
        print(f"Rank {i+1} | Distance: {res.get('distance', 0):.4f} | ID: {res['id']} | Source: {meta.get('source_name', 'Unknown')} | Section: {meta.get('section_name', 'Unknown')}")
        
    print("\n--- RRF Fusion ---")
    chunks = hybrid_retriever.search(rewritten, query_emb, n_results=10, where={"tenant_id": "global"})
    for i, chunk in enumerate(chunks):
        meta = chunk["metadata"]
        print(f"Final Rank {i+1} | RRF Score: {meta.get('rrf_score', 0):.4f} | Method: {meta.get('retrieval_method')} | Source: {meta.get('source_name')} | Section: {meta.get('section_name')}")

if __name__ == "__main__":
    asyncio.run(main())
