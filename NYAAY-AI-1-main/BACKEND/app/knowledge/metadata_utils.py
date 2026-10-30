import re
from typing import Dict, Any

def get_canonical_source_name(metadata: Dict[str, Any]) -> str:
    """
    Extracts a reliable canonical human-readable source title from document metadata,
    handling fallbacks across various document types (statutes, judgments, schemes).
    """
    if not metadata:
        return "Unknown"
        
    # Check hierarchy of potential identity fields
    for key in [
        "canonical_source_name",
        "source_name",
        "case_name",
        "case_title",
        "scheme_name",
        "act_name",
        "title",
        "document_name",
        "document_title"
    ]:
        val = metadata.get(key)
        if val and isinstance(val, str):
            val = val.strip()
            # Reject known bad placeholders
            if val and val != "None v. None" and val != "Case: None v. Unknown Respondent" and val != "Unknown v. Unknown" and val.lower() != "unknown":
                # Ensure it's not a generic placeholder
                if not re.match(r'^case:\s*none', val, re.IGNORECASE):
                    return val
                
    # Fallback for Supreme Court/High Court judgments if petitioner/respondent exist
    petitioner = metadata.get("petitioner")
    respondent = metadata.get("respondent")
    if petitioner and respondent:
        pet_str = str(petitioner).strip()
        res_str = str(respondent).strip()
        if pet_str and res_str and pet_str.lower() != "none" and res_str.lower() != "none" and pet_str.lower() != "unknown" and res_str.lower() != "unknown respondent":
            return f"{pet_str} v. {res_str}"
            
    # Fallback to original filename if nothing else exists
    filename = metadata.get("original_filename")
    if filename and isinstance(filename, str):
        # Don't use meaningless random hashes
        if len(filename) > 5 and not re.match(r'^[0-9a-fA-F\-]{10,}\.pdf$', filename):
            # Clean extension
            clean_name = re.sub(r'\.[a-zA-Z0-9]+$', '', filename)
            return clean_name.replace('_', ' ').replace('-', ' ').title()
            
    return "Unknown"
