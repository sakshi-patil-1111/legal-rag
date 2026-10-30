import sys, os
import json
sys.path.insert(0, os.path.abspath('BACKEND'))
from app.knowledge.hybrid_retriever import hybrid_retriever
from app.knowledge.embeddings import embedding_service

QUERIES = {
    "Municipal": ("A municipal authority has repeatedly failed to collect garbage...", "Constitutional & Administrative"),
    "Employment": ("Employee dismissed without hearing or disclosing allegations...", "Labour & Employment"),
    "Homebuyer": ("Developer delayed possession by 4 years...", "Property & Real Estate"),
    "SC_Direct": ("Supreme Court judgments explaining natural justice...", "Labour & Employment")
}

MULTIPLIERS = [0.00, 0.02, 0.05, 0.10, 0.15] # Maps to 1.00, 1.02, 1.05, 1.10, 1.15

results_log = {}

for mult_weight in MULTIPLIERS:
    print(f"\n--- Testing Multiplier: {1.0 + mult_weight:.2f} ---")
    results_log[mult_weight] = {}
    
    for q_name, (query_text, target_domain) in QUERIES.items():
        predicted = {target_domain: 1.0} 
        
        q_emb = embedding_service.embed_query(query_text)
        
        chunks = hybrid_retriever.search(
            query=query_text,
            query_embedding=q_emb,
            n_results=10,
            predicted_domains=predicted,
            domain_multiplier_weight=mult_weight
        )
        
        results_log[mult_weight][q_name] = [
            f"[{c['metadata'].get('legal_domain', 'Unknown')}] {c['metadata'].get('source_name', '?')}" for c in chunks[:3]
        ]
        
        # We also want to see if the target_domain chunks floated to the top
        domain_hits = sum(1 for c in chunks[:5] if c['metadata'].get('legal_domain') == target_domain)
        print(f"  {q_name}: {domain_hits}/5 in top 5 are {target_domain}")

with open("BACKEND/benchmark_rrf_results.json", "w") as f:
    json.dump(results_log, f, indent=2)
