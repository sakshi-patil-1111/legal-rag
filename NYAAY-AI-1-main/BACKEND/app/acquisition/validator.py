import os
import json
import logging
import re
from typing import Dict, Any

logger = logging.getLogger(__name__)

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DATA_DIR = os.path.join(BASE_DIR, "data")
PARSED_DIR = os.path.join(DATA_DIR, "parsed")
VALIDATED_DIR = os.path.join(DATA_DIR, "validated")

class StatutoryValidator:
    """
    Performs Citation Integrity Checks on parsed statutory documents.
    Identifies missing sections, omitted sections, and duplicate sections.
    """
    def __init__(self):
        os.makedirs(VALIDATED_DIR, exist_ok=True)
        
    def _extract_numeric_part(self, section_str: str) -> int:
        match = re.search(r"(\d+)", section_str)
        return int(match.group(1)) if match else 0
        
    def validate_document(self, parsed_data: Dict[str, Any]) -> Dict[str, Any]:
        sections = parsed_data.get("sections", [])
        report = parsed_data.get("parser_report", {})
        
        expected_next = 1
        missing = 0
        duplicates = 0
        
        seen_sections = set()
        
        for sec in sections:
            sec_num_str = sec.get("section_number", "")
            if not sec_num_str:
                continue
                
            if sec_num_str in seen_sections:
                duplicates += 1
                logger.warning(f"Duplicate section detected: {sec_num_str}")
            seen_sections.add(sec_num_str)
            
            numeric_val = self._extract_numeric_part(sec_num_str)
            
            # Simple missing check (ignores alphabet suffixes like 120A for this basic test)
            if numeric_val > expected_next:
                diff = numeric_val - expected_next
                # Check if it was explicitly omitted in the text
                # (Real logic would check if sec title says 'Omitted' or 'Repealed')
                is_omitted = "omitted" in sec.get("section_title", "").lower()
                if not is_omitted:
                    missing += diff
                    logger.warning(f"Missing section gap detected between {expected_next-1} and {numeric_val}")
            
            expected_next = numeric_val + 1
            
        report["missing_sections"] = missing
        report["duplicate_sections"] = duplicates
        
        if missing > 0 or duplicates > 0:
            report["confidence"] = "LOW"
            report["hierarchy_score"] -= (missing * 5) + (duplicates * 10)
        
        parsed_data["parser_report"] = report
        return parsed_data

    def process_file(self, filename: str):
        logger.info(f"Validating {filename}...")
        filepath = os.path.join(PARSED_DIR, filename)
        
        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)
            
        validated_data = self.validate_document(data)
        
        # Save to validated dir
        act_id = data["act_id"]
        save_path = os.path.join(VALIDATED_DIR, f"{act_id}_validated.json")
        with open(save_path, "w", encoding="utf-8") as f:
            json.dump(validated_data, f, indent=4)
            
        logger.info(f"Validation complete for {act_id}. Score: {validated_data['parser_report']['hierarchy_score']}")
        return validated_data

if __name__ == "__main__":
    import argparse
    logging.basicConfig(level=logging.INFO)
    parser = argparse.ArgumentParser()
    parser.add_argument("--filename", required=True, help="Filename in parsed/ to validate")
    args = parser.parse_args()
    
    v = StatutoryValidator()
    v.process_file(args.filename)
