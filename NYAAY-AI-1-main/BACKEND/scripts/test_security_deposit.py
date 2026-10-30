import os
import sys

sys.stdout.reconfigure(encoding='utf-8')
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.knowledge.hybrid_retriever import hybrid_retriever
from app.knowledge.embeddings import embedding_service
from app.ai.domain_classifier import domain_classifier
from app.ai.orchestrator import rag_orchestrator

query = "security deposit refund deductions repairs rental agreement"

print("--- Testing direct retrieval for security deposits ---")
expanded = rag_orchestrator._analyze_and_expand_query(query, [])
print(f"Expanded: {expanded}")

domain_preds = domain_classifier.predict_domain(expanded)
print(f"Domains: {domain_preds}")

emb = embedding_service.embed_query(expanded)

res = hybrid_retriever.search(
    query=expanded,
    query_embedding=emb,
    n_results=10,
    where={},
    predicted_domains=domain_preds.get("domains", {}),
    document_type_priority=domain_preds.get("document_type_priority", "any")
)

print(f"Found {len(res)} results.")
for i, r in enumerate(res[:5]):
    print(f"[{i}] {r['metadata'].get('source_name')} - Score: {r['metadata'].get('rrf_score')}")
    print(r['document'][:200])
    print("-" * 50)
