import os
import sys
import json
from collections import Counter

# Ensure backend directory is in path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.knowledge.embeddings import embedding_service
from app.knowledge.hybrid_retriever import hybrid_retriever

hard_queries = [
    "How do I claim a deduction for money lost to a scammer?",
    "What happens if a minor signs a contract to buy a gun?",
    "Can a company be arrested for murder?",
    "What is the penalty for unauthorized access to a computer system?",
    "Is a marriage between two cousins valid?",
    "How to file for bankruptcy if a tenant refuses to pay rent?",
    "What is the maximum interest rate a bank can charge on a home loan?",
    "If a wild animal damages my crops, can I shoot it?",
    "Can I be fired for being pregnant?",
    "What to do if a doctor prescribes the wrong medicine?",
    "Can the government take away my land without compensation?",
    "Are cryptocurrencies considered legal tender or taxable assets?",
    "Can I divorce my spouse if they refuse to live with my parents?",
    "What is the punishment for cheating in an academic exam?",
    "Can a foreigner buy agricultural land in India?",
    "Is betting on cricket matches legally enforceable?",
    "What happens if a check bounces due to signature mismatch?",
    "Can a Hindu daughter claim a share in ancestral agricultural land?",
    "Is it illegal to record a phone call without the other person's permission?",
    "How long do I have to file a case against a builder for delayed possession?"
]

from app.ai.domain_classifier import domain_classifier

results_summary = []

for q in hard_queries:
    query_emb = embedding_service.embed_query(q)
    
    # 2.5 Pre-Search Domain Classification
    domain_predictions = domain_classifier.predict_domain(q)
    predicted_domains = domain_predictions.get("domains", {})
    doc_type_priority = domain_predictions.get("document_type_priority", "any")

    results = hybrid_retriever.search(
        query=q, 
        query_embedding=query_emb, 
        n_results=10,
        predicted_domains=predicted_domains,
        document_type_priority=doc_type_priority
    )
    
    retrieved_acts = []
    for r in results:
        act = r["metadata"].get("act_name", "Unknown Act")
        retrieved_acts.append(act)
        
    # Count occurrences of each act
    act_counts = dict(Counter(retrieved_acts))
    
    results_summary.append({
        "query": q,
        "retrieved_acts": act_counts
    })

with open("hard_queries_test.json", "w", encoding="utf-8") as f:
    json.dump(results_summary, f, indent=4)

print("Finished evaluating 20 hard queries. Output saved to hard_queries_test.json")
