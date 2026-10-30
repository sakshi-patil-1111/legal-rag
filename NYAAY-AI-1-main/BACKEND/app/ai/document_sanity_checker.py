import re
from typing import Dict, Any, List

def validate_document_authenticity(doc_obj_dict: Dict[str, Any]) -> Dict[str, Any]:
    """
    Performs deterministic sanity checks on a drafted document.
    Returns a Document Confidence Report and a list of specific issues to be fixed.
    """
    issues = []
    
    # --- 1. Structural Validation (Document-Specific) ---
    structural_score = 100
    doc_type = doc_obj_dict.get('document_type', '')
    
    if not doc_obj_dict.get('title'):
        structural_score -= 10
        issues.append("Missing Document Title.")
    
    if not doc_obj_dict.get('parties') and doc_type != 'AFFIDAVIT':
        structural_score -= 15
        issues.append("Missing Parties block.")
        
    if not doc_obj_dict.get('body') or len(doc_obj_dict.get('body', [])) < 2:
        structural_score -= 20
        issues.append("Body is missing or too short. Needs comprehensive factual and legal grounds.")

    if doc_type in ['AFFIDAVIT', 'PLAINT', 'CONSUMER_COMPLAINT']:
        if not doc_obj_dict.get('verification'):
            structural_score -= 20
            issues.append(f"Missing Verification clause which is mandatory for {doc_type}.")
            
    if doc_type == 'LEGAL_NOTICE':
        body_text = " ".join(doc_obj_dict.get('body', [])).lower()
        if "subject" not in body_text and not doc_obj_dict.get('title'):
            structural_score -= 15
            issues.append("Legal Notice is missing a Subject.")
        if "demand" not in body_text and "comply" not in body_text and "days" not in body_text:
            structural_score -= 15
            issues.append("Legal Notice is missing a clear demand section or compliance period.")
        if "rights" not in body_text and "prejudice" not in body_text:
            structural_score -= 15
            issues.append("Legal Notice is missing a reservation of rights clause.")

    if doc_type == 'PLAINT':
        body_text = " ".join(doc_obj_dict.get('body', [])).lower()
        if "jurisdiction" not in body_text:
            issues.append("Plaint is missing the Jurisdiction clause.")
        if "cause of action" not in body_text:
            issues.append("Plaint is missing the Cause of Action clause.")
        if "valuation" not in body_text and "court fee" not in body_text:
            issues.append("Plaint is missing the Valuation and Court Fee clause.")
        if "prayer" not in body_text and not doc_obj_dict.get('prayer'):
            issues.append("Plaint is missing the Prayer clause.")

    if doc_type == 'CONSUMER_COMPLAINT':
        body_text = " ".join(doc_obj_dict.get('body', [])).lower()
        if "jurisdiction" not in body_text:
            issues.append("Consumer Complaint is missing the Jurisdiction clause.")
        if "deficiency" not in body_text and "service" not in body_text:
            issues.append("Consumer Complaint is missing explicit allegations of Deficiency in Service.")
        if "relief" not in body_text and not doc_obj_dict.get('prayer'):
            issues.append("Consumer Complaint is missing Reliefs.")

    # --- 2. Formatting & Authenticity Validation ---
    formatting_score = 100
    authenticity_score = 100
    body = doc_obj_dict.get('body', [])
    for idx, para in enumerate(body):
        words = len(para.split())
        if words > 150:
            formatting_score -= 10
            issues.append(f"Paragraph {idx + 1} is too long ({words} words). Split it into smaller, focused paragraphs.")
    
    # Check duplicate signature blocks
    sig_blocks = doc_obj_dict.get('signature_blocks', [])
    if len(sig_blocks) > len(set(sig_blocks)):
        formatting_score -= 20
        issues.append("Duplicate signature blocks detected. Remove duplicates.")
        
    # Check AI-style phrasing for authenticity
    doc_text = " ".join(body) + " " + " ".join(doc_obj_dict.get('parties', {}).values())
    ai_phrases = ["it is important to note", "in conclusion", "furthermore", "moreover", "delve into", "testament to"]
    for phrase in ai_phrases:
        if phrase in doc_text.lower():
            authenticity_score -= 10
            issues.append(f"Unnatural phrasing detected: '{phrase}'. Remove AI-style conversational transitions.")

    # --- 3. Legal Precision & Citation Accuracy ---
    legal_precision = 100
    citation_accuracy = 100
    hallucination_risk = 0
    
    # Look for absolute legal conclusions
    absolute_phrases = ["constitutes a clear case", "is undeniably", "without a doubt", "clearly proves"]
    for phrase in absolute_phrases:
        if phrase in doc_text.lower():
            legal_precision -= 15
            issues.append(f"Absolute conclusion used: '{phrase}'. Soften to 'prima facie amounts to' or 'appears to constitute'.")

    generic_phrases = ["applicable labour laws", "applicable laws", "statutory provisions", "relevant sections"]
    for phrase in generic_phrases:
        if phrase in doc_text.lower():
            legal_precision -= 10
            issues.append(f"Used generic phrase '{phrase}'. Provide specific statutory provisions or remove.")

    # Citation checking heuristic: If an Act is cited, verify it doesn't sound completely irrelevant
    # (A simple heuristic for demonstration - in production, this could map against facts)
    if "employees' provident funds act" in doc_text.lower() and "pf" not in doc_text.lower() and "provident fund" not in doc_text.lower():
        citation_accuracy -= 20
        hallucination_risk = 50
        issues.append("Cited Employees' Provident Funds Act without factual basis regarding PF dues.")

    # Ensure annexures referenced in body exist in the list
    annexures = doc_obj_dict.get('annexures', [])
    if "annexure" in doc_text.lower() and not annexures:
        legal_precision -= 10
        issues.append("Annexures are referenced in the text but the Annexures list is empty.")

    # Placeholders check (Placeholder Leakage)
    missing_mandatory_fields = []
    # Identify leaked placeholders [Like This]
    generic_placeholders = re.findall(r'\[(.*?)\]', doc_text)
    
    # We consider certain placeholders mandatory and stop generation.
    mandatory_keywords = ['name', 'address', 'date', 'amount', 'court', 'jurisdiction', 'party']
    for p in generic_placeholders:
        p_lower = p.lower()
        if any(k in p_lower for k in mandatory_keywords):
            missing_mandatory_fields.append(p)
        else:
            authenticity_score -= 5
            issues.append(f"Optional placeholder [{p}] was left in the text. Ensure it is omitted or filled.")

    # Calculate final readiness
    final_score = (structural_score + formatting_score + legal_precision + citation_accuracy + authenticity_score) / 5
    
    # Deduplicate
    issues = list(set(issues))
    missing_mandatory_fields = list(set(missing_mandatory_fields))
    
    needs_refinement = (legal_precision < 90 or len(issues) > 0) and not missing_mandatory_fields
    
    return {
        "confidence_report": {
            "Structure": structural_score,
            "Formatting": formatting_score,
            "Legal Precision": legal_precision,
            "Citation Accuracy": citation_accuracy,
            "Hallucination Risk": f"{hallucination_risk}%",
            "Authenticity": authenticity_score,
            "Export Ready": "YES" if not needs_refinement else "NO"
        },
        "needs_refinement": needs_refinement,
        "issues": issues,
        "missing_mandatory_fields": missing_mandatory_fields
    }
