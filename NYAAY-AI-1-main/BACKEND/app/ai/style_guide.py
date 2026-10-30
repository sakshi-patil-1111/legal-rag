from typing import Dict, Any

class StyleGuide:
    """
    Centralized Document Style Guide for the Drafting Engine.
    Enforces Legal Precision, Citations, and Document-Specific Authenticity Rules.
    """

    UNIVERSAL_RULES = """
UNIVERSAL LEGAL DRAFTING RULES:
1. Legal Citation Policy: Never cite a statute simply because it belongs to the same practice area. Every statute must satisfy: 
   - Direct factual connection.
   - Procedural applicability.
   - Relief being sought.
   If these are absent, do NOT cite the statute.
2. Qualified Language: Use legally qualified language appropriate to the procedural stage.
   Examples: 'appears to constitute', 'prima facie amounts to', 'is liable to be treated as', 'may amount to', 'is capable of attracting'. 
   Avoid absolute conclusions unless legally unavoidable.
3. Threat Mitigation: Do not explicitly threaten IPC sections unless mandated. Use 'which may give rise to civil and/or criminal remedies available in law'.
4. Terminology Consistency: Maintain consistent use of terms (e.g., 'Our Client', 'Noticee') throughout the draft.
5. Content Focus: You are responsible ONLY for generating the legal content and logical structure. Do NOT add formatting notes.
"""

    DOCUMENT_RULES = {
        "LEGAL_NOTICE": """
DOCUMENT SPECIFIC RULES (Legal Notice):
Must mimic authentic drafting conventions followed by senior Indian advocates.
1. The title MUST strictly be "LEGAL NOTICE" unless a specific statutory reference is required by the user facts. Do not write verbose titles like "LEGAL NOTICE UNDER THE PROVISIONS OF...".
2. The `body` array MUST ONLY contain the substantive numbered paragraphs of the notice. DO NOT include "To", "Date", "Subject", "Sir/Madam", "REGD. A.D.", or "PARTIES" in the `body` array. The system renders these automatically.
3. Write naturally and assertively. Avoid academic "1. 2. 3." disjointed styles. Use proper paragraph transitions.
4. Do not invent an Advocate's name if none is provided. Do not use the Client's name as the Advocate's name.
5. Do not invent a Date.
""",
        "CONSUMER_COMPLAINT": """
DOCUMENT SPECIFIC RULES (Consumer Complaint):
Must mimic authentic drafting conventions followed by Indian advocates.
Include mandatory sections in this order:
- Cause title
- Parties
- Territorial & Pecuniary Jurisdiction
- Facts in chronology
- Cause of action
- Deficiency in service / unfair trade practice
- Reliefs
- Prayer
- Verification
""",
        "PLAINT": """
DOCUMENT SPECIFIC RULES (Plaint):
Must mimic authentic drafting conventions followed by Indian advocates.
Include mandatory sections in this order:
- Cause title
- Jurisdiction
- Facts
- Cause of action
- Limitation
- Valuation
- Relief
- Verification
""",
        "AFFIDAVIT": """
DOCUMENT SPECIFIC RULES (Affidavit):
Must mimic authentic drafting conventions followed by Indian advocates.
Include mandatory sections in this order:
- Deponent details
- Numbered sworn statements
- Verification clause
- Attestation block
""",
        "BAIL_APPLICATION": """
DOCUMENT SPECIFIC RULES (Bail Application):
Must mimic authentic drafting conventions followed by Indian advocates.
Include mandatory sections in this order:
- Court heading
- FIR details
- Facts
- Grounds for bail
- Prayer
- Verification
"""
    }

    @classmethod
    def get_rules_for_document(cls, document_type: str) -> str:
        doc_rules = cls.DOCUMENT_RULES.get(document_type, "DOCUMENT SPECIFIC RULES: Follow standard Indian drafting conventions.")
        return f"{cls.UNIVERSAL_RULES}\n{doc_rules}"

style_guide = StyleGuide()
