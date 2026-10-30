import sys

with open('app/ai/validator.py', 'r', encoding='utf-8') as f:
    code = f.read()

new_calc = '''def calculate_retrieval_confidence(chunks, query_analysis=None):
    if not chunks:
        return 0, "🔴 Insufficient", "No relevant authority was found in the indexed knowledge base.", 0.0, 0.0
    
    scores = [c['metadata'].get('rrf_score', 0) for c in chunks]
    avg_score = sum(scores) / len(scores) if scores else 0
    max_score = max(scores) if scores else 0
    
    has_statute = any("Act" in c['metadata'].get("source_name", "") or "Code" in c['metadata'].get("source_name", "") or "Sanhita" in c['metadata'].get("source_name", "") or c['metadata'].get('document_type') == 'statute' for c in chunks)
    has_judgment = any("Judgment" in c['metadata'].get("legal_domain", "") or "Supreme Court" in c['metadata'].get("source_name", "") or "SC" in c['metadata'].get("source_name", "") or c['metadata'].get('document_type') == 'judgment' or c['metadata'].get('court_level') == 'Supreme Court' for c in chunks)

    predicted_domains = (query_analysis or {}).get("domains", {})
    domain_matched = False
    if predicted_domains:
        domain_matched = any(c['metadata'].get('legal_domain', '') in predicted_domains for c in chunks)
    else:
        domain_matched = True # Not a complex query, default to True for this check
        
    sc_requested = (query_analysis or {}).get("explicit_sc_requested", False)
    
    if has_statute and has_judgment and domain_matched:
        score, label = 95, "🟢 High"
        reason = "Directly applicable statutory provisions and binding judgments retrieved."
    elif has_statute and domain_matched:
        score, label = 80, "🟢 High"
        reason = "Direct statutory provisions govern this issue."
    elif has_statute and not domain_matched:
        score, label = 55, "🟡 Moderate"
        reason = "Statutory provisions retrieved but may not be the primary governing authority."
    elif sc_requested and not has_judgment:
        score, label = 40, "🟠 Limited"
        reason = "Supreme Court precedent requested but not found in indexed corpus."
    elif has_judgment:
        score, label = 75, "🟡 Moderate"
        reason = "Case law supports this conclusion, but primary statutory texts were not retrieved."
    else:
        score, label = 60, "🟠 Limited"
        reason = "Only indirect or related authorities were retrieved. The conclusion relies on analogy."

    return score, label, reason, avg_score, max_score
'''

start_idx = code.find('def calculate_retrieval_confidence')
end_idx = code.find('def validate_response')

code = code[:start_idx] + new_calc + '\n' + code[end_idx:]

with open('app/ai/validator.py', 'w', encoding='utf-8') as f:
    f.write(code)

print("Rewrote validator.py successfully")
