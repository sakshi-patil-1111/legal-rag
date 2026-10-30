import sys

with open('app/knowledge/hybrid_retriever.py', 'r', encoding='utf-8') as f:
    code = f.read()

search_sc_code = '''
    def search_sc_only(self, query: str, query_embedding: List[float], n_results: int = 10) -> List[Dict[str, Any]]:
        # Dense search against sc_collection only
        dense_results = vector_store.search(query_embedding, n_results=n_results, search_sc=True)
        # Filter to only SC collection (distances < 1.0 or IDs starting with SC)
        # VectorStore's search already merges. We can manually filter:
        sc_candidates = [r for r in dense_results if 'SC_' in r['id'] or r['metadata'].get('court_level') == 'Supreme Court']
        
        # We can also do BM25 filtering, but to keep latency low, we just return the dense SC matches
        # and rerank them.
        if sc_candidates:
            from app.knowledge.reranker import reranker_service
            return reranker_service.rerank(query, sc_candidates, top_k=n_results)
        return []
'''

# insert before hybrid_retriever = HybridRetriever()
code = code.replace('hybrid_retriever = HybridRetriever()', search_sc_code + '\nhybrid_retriever = HybridRetriever()\n')

with open('app/knowledge/hybrid_retriever.py', 'w', encoding='utf-8') as f:
    f.write(code)

print("Patched hybrid_retriever.py")
