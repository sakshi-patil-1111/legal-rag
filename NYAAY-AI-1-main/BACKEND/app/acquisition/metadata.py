import os
import json
import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DATA_DIR = os.path.join(BASE_DIR, "data")
DOWNLOADS_DIR = os.path.join(DATA_DIR, "downloads")
VALIDATED_DIR = os.path.join(DATA_DIR, "validated")
APPROVED_DIR = os.path.join(DATA_DIR, "approved")

class MetadataExtractor:
    """
    Combines parsed text with provenance and static/dynamic metadata to produce the final 
    corpus document for human review.
    """
    def __init__(self):
        os.makedirs(APPROVED_DIR, exist_ok=True)
        
    def generate_final_document(self, act_id: str) -> Dict[str, Any]:
        # Load validated output
        val_path = os.path.join(VALIDATED_DIR, f"{act_id}_validated.json")
        with open(val_path, "r", encoding="utf-8") as f:
            val_data = json.load(f)
            
        # Load provenance sidecar
        prov_path = os.path.join(DOWNLOADS_DIR, f"{act_id}_provenance.json")
        provenance = {}
        if os.path.exists(prov_path):
            with open(prov_path, "r", encoding="utf-8") as f:
                provenance = json.load(f).get("source", {})
                
        # Base metadata framework
        document = {
            "document_id": act_id,
            "static_metadata": {
                "act_name": act_id.replace("_", " ").title(),
                "act_year": act_id.split("_")[-1] if "_" in act_id else "Unknown",
                "jurisdiction": "Central",
                "applicable_states": ["All"],
                "document_type": "Act",
                "legal_domain": "General",
                "practice_areas": []
            },
            "dynamic_metadata": {
                "corpus_version": "v1.0",
                "amended_on": None,
                "repealed": False,
                "superseded_by": None,
                "effective_date": "2024-07-01" if "BNS" in act_id else None,
                "chunk_count": len(val_data.get("sections", []))
            },
            "provenance": provenance,
            # Reserved SC Fields
            "reserved_metadata": {
                "court": None,
                "bench_strength": None,
                "judges": [],
                "decision_date": None,
                "citation": None,
                "neutral_citation": None,
                "statutes_referenced": [],
                "overruled_cases": [],
                "relied_on_cases": [],
                "paragraph_number": None
            },
            "parser_report": val_data.get("parser_report", {}),
            "content": val_data.get("sections", [])
        }
        return document

    def process_file(self, act_id: str):
        logger.info(f"Extracting metadata for {act_id}...")
        final_doc = self.generate_final_document(act_id)
        
        save_path = os.path.join(APPROVED_DIR, f"{act_id}_final.json")
        with open(save_path, "w", encoding="utf-8") as f:
            json.dump(final_doc, f, indent=4)
            
        logger.info(f"Successfully generated final approved corpus document at {save_path}")
        return final_doc

if __name__ == "__main__":
    import argparse
    logging.basicConfig(level=logging.INFO)
    parser = argparse.ArgumentParser()
    parser.add_argument("--act_id", required=True, help="Act ID to finalize")
    args = parser.parse_args()
    
    m = MetadataExtractor()
    m.process_file(args.act_id)
