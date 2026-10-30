import os
import sys

# Ensure backend directory is in path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.knowledge.embeddings import embedding_service
from app.knowledge.hybrid_retriever import hybrid_retriever
import json

queries = [
    "What are the conditions for granting anticipatory bail?",
    "What is the procedure to incorporate a new public company?",
    "What are the essential elements of a valid contract?",
    "What is the penalty for committing murder or culpable homicide?",
    "What is the limitation period for filing a civil suit for breach of contract?"
]

results_output = []

for q in queries:
    # 1. Embed query
    query_emb = embedding_service.embed_query(q)
    
    # 2. Search
    results = hybrid_retriever.search(query=q, query_embedding=query_emb, n_results=3)
    
    formatted_results = []
    for r in results:
        meta = r["metadata"]
        formatted_results.append({
            "act_name": meta.get("act_name", "Unknown"),
            "section": meta.get("section", "Unknown"),
            "retrieval_method": meta.get("retrieval_method", "Unknown"),
            "rrf_score": round(meta.get("rrf_score", 0), 4),
            "text": r["document"][:200] + "..." # Truncate for display
        })
    
    results_output.append({
        "query": q,
        "results": formatted_results
    })

with open("retrieval_test_results.json", "w", encoding="utf-8") as f:
    json.dump(results_output, f, indent=4)

print("Test complete. Results written to retrieval_test_results.json")
