import os
import sys
import logging

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.corpus.manifest import CorpusManifestManager
from app.knowledge.vector_store import vector_store
from app.knowledge.bm25_manager import bm25_manager

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

def check_integrity():
    logger.info("Starting Corpus Integrity Check...")
    manager = CorpusManifestManager()
    manifest = manager.manifest
    acts = manifest.get("acts", {})
    
    errors = 0
    warnings = 0
    
    logger.info("Checking ChromaDB synchronization...")
    try:
        db_docs = vector_store.collection.get(include=["metadatas"])
        metadatas = db_docs.get("metadatas", [])
        
        # Count chunks per document in ChromaDB
        chroma_counts = {}
        for m in metadatas:
            if m:
                doc_id = m.get("document_id") or m.get("source_name") # accommodate older schemas
                if doc_id:
                    chroma_counts[doc_id] = chroma_counts.get(doc_id, 0) + 1
                    
        for act_id, act_info in acts.items():
            expected = act_info.get("chunk_count", 0)
            actual = chroma_counts.get(act_id, 0)
            # Try matching without extension or case just in case
            if actual == 0:
                 for key in chroma_counts:
                     if key.upper().startswith(act_id.upper()) or act_id.upper().startswith(key.upper()):
                         actual = chroma_counts[key]
                         break
                         
            if expected != actual:
                logger.error(f"Mismatch for {act_id}: Manifest expects {expected} chunks, ChromaDB has {actual}.")
                errors += 1
                
    except Exception as e:
        logger.error(f"Failed to query ChromaDB: {e}")
        errors += 1

    logger.info(f"Integrity check complete. Errors: {errors}, Warnings: {warnings}")
    if errors > 0:
        sys.exit(1)
        
if __name__ == "__main__":
    check_integrity()
