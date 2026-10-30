import os
import json
import logging
from datetime import datetime
from typing import Dict, Any, List, Optional

logger = logging.getLogger(__name__)

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DATA_DIR = os.path.join(BASE_DIR, "data")
MANIFEST_PATH = os.path.join(DATA_DIR, "corpus_manifest.json")
REPORTS_DIR = os.path.join(DATA_DIR, "reports")

def ensure_directories():
    os.makedirs(DATA_DIR, exist_ok=True)
    os.makedirs(REPORTS_DIR, exist_ok=True)

class CorpusManifestManager:
    """
    Manages the corpus_manifest.json file, serving as the single source of truth for the corpus.
    """
    def __init__(self):
        ensure_directories()
        self.manifest = self._load_manifest()

    def _load_manifest(self) -> Dict[str, Any]:
        if os.path.exists(MANIFEST_PATH):
            with open(MANIFEST_PATH, "r", encoding="utf-8") as f:
                try:
                    return json.load(f)
                except json.JSONDecodeError:
                    logger.error("Failed to decode corpus_manifest.json. Creating a new one.")
                    
        return self._create_empty_manifest()

    def _create_empty_manifest(self) -> Dict[str, Any]:
        return {
            "manifest_version": "1.0",
            "last_updated": datetime.utcnow().isoformat() + "Z",
            "corpus_stats": {
                "total_acts": 0,
                "total_chunks": 0,
                "total_embeddings": 0,
                "domains_covered": [],
                "batches_completed": []
            },
            "acts": {}
        }

    def save_manifest(self):
        self.manifest["last_updated"] = datetime.utcnow().isoformat() + "Z"
        # Recompute global stats
        acts = self.manifest["acts"]
        self.manifest["corpus_stats"]["total_acts"] = len(acts)
        self.manifest["corpus_stats"]["total_chunks"] = sum(a.get("chunk_count", 0) for a in acts.values())
        self.manifest["corpus_stats"]["total_embeddings"] = sum(a.get("embedding_count", 0) for a in acts.values())
        
        domains = set(a.get("legal_domain") for a in acts.values() if a.get("legal_domain"))
        self.manifest["corpus_stats"]["domains_covered"] = list(domains)
        
        batches = set(a.get("ingestion_batch") for a in acts.values() if a.get("ingestion_batch"))
        self.manifest["corpus_stats"]["batches_completed"] = sorted(list(batches))

        with open(MANIFEST_PATH, "w", encoding="utf-8") as f:
            json.dump(self.manifest, f, indent=4)
            
        # Optional: Save a versioned manifest
        version = f"v{len(self.manifest['corpus_stats']['batches_completed'])}.0"
        version_path = os.path.join(DATA_DIR, f"corpus_manifest_{version}.json")
        with open(version_path, "w", encoding="utf-8") as f:
             json.dump(self.manifest, f, indent=4)


    def add_or_update_act(self, act_data: Dict[str, Any]):
        document_id = act_data.get("document_id")
        if not document_id:
            raise ValueError("document_id is required to update manifest")
        
        self.manifest["acts"][document_id] = act_data
        self.save_manifest()
        logger.info(f"Updated manifest for {document_id}")

    def get_act(self, document_id: str) -> Optional[Dict[str, Any]]:
        return self.manifest["acts"].get(document_id)

    def generate_batch_report(self, batch_id: str, results: Dict[str, Any]) -> str:
        report = {
            "batch_id": batch_id,
            "completed_at": datetime.utcnow().isoformat() + "Z",
            **results
        }
        
        report_path = os.path.join(REPORTS_DIR, f"{batch_id}_report.json")
        with open(report_path, "w", encoding="utf-8") as f:
            json.dump(report, f, indent=4)
            
        logger.info(f"Generated batch report at {report_path}")
        return report_path

    def check_duplicate(self, document_id: str, file_hash: str) -> Dict[str, Any]:
        """
        Returns info if duplicate is found.
        """
        if document_id in self.manifest["acts"]:
            return {"type": "act_duplicate", "document_id": document_id}
            
        for act_id, act_info in self.manifest["acts"].items():
            if act_info.get("sha256_hash") == file_hash:
                 return {"type": "hash_duplicate", "document_id": act_id, "hash": file_hash}
                 
        return {"type": "none"}
