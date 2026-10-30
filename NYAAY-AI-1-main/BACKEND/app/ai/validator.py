import re

def calculate_retrieval_confidence(chunks, query_analysis=None):
    if not chunks:
        return 0, "🔴 Insufficient", "No relevant authority was found in the indexed knowledge base.", 0.0, 0.0
    
    scores = [c['metadata'].get('rrf_score', 0) for c in chunks]
    avg_score = sum(scores) / len(scores) if scores else 0
    max_score = max(scores) if scores else 0
    
    from app.knowledge.metadata_utils import get_canonical_source_name
    
    def get_src(c):
        return get_canonical_source_name(c.get('metadata', {}))

    has_statute = any("Act" in get_src(c) or "Code" in get_src(c) or "Sanhita" in get_src(c) or c['metadata'].get('document_type') == 'statute' for c in chunks)
    has_judgment = any("Judgment" in c['metadata'].get("legal_domain", "") or "Supreme Court" in get_src(c) or "SC" in get_src(c) or c['metadata'].get('document_type') == 'judgment' or c['metadata'].get('court_level') == 'Supreme Court' for c in chunks)

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

def validate_response(raw_answer):
    # Dynamic headings mean we can no longer strictly require a fixed set of headers.
    # However, we must still ensure the model doesn't output empty or severely malformed text.
    if len(raw_answer.strip()) < 50:
        return False, "Response is too short to be a valid legal answer."

    # Reject hallucinated numerical likelihoods
    if re.search(r'\b\d{2,3}%\s+likelihood\b', raw_answer, re.IGNORECASE):
        return False, "Response contains hallucinated probability percentages."
        
    return True, raw_answer

def extract_reasoning_confidence(raw_answer):
    # Heuristic: count assumptions and missing facts
    missing_count = len(re.findall(r'(?i)critical missing', raw_answer))
    assumed_count = len(re.findall(r'(?i)facts assumed', raw_answer))
    
    score = 100 - (missing_count * 15) - (assumed_count * 5)
    score = max(0, min(100, score))
    
    if score >= 90:
        return score, f"🟢 High - Facts are clear and well-established."
    elif score >= 70:
        return score, f"🟡 Moderate - Some assumptions required for complete analysis."
    else:
        return score, f"🟠 Limited - Critical facts are missing, impacting analysis."
