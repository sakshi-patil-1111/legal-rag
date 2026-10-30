import hashlib
import time
from typing import Dict, Any, List

def calculate_hash(content: str) -> str:
    hasher = hashlib.sha256()
    hasher.update(content.encode('utf-8'))
    return hasher.hexdigest()

def extract_metadata(structured_blocks: List[Dict[str, Any]], source_url: str, document_name: str, legal_domain: str, act_name: str, document_type: str = "statute") -> Dict[str, Any]:
    """
    Adds comprehensive metadata and versioning to the document and its structural chunks.
    Implements Phase 5 (Metadata) and Phase 6 (Versioning).
    """
    
    # Calculate full document hash based on extracted text to track true changes
    full_text = "\n".join(b["text"] for b in structured_blocks)
    doc_hash = calculate_hash(full_text)
    
    doc_metadata = {
        "document_id": document_name,
        "source_name": document_name.upper().replace(".PDF", "").replace(".TXT", "").replace(".MD", ""),
        "source_url": source_url,
        "source_type": "official",
        "legal_domain": legal_domain,
        "act_name": act_name,
        "document_type": document_type,
        "retrieval_date": int(time.time()),
        "processing_timestamp": int(time.time()),
        "version": "1.0",
        "sha256_hash": doc_hash
    }
    
    # Update blocks with chunk-level metadata
    for i, block in enumerate(structured_blocks):
        block_hash = calculate_hash(block["text"])
        chunk_meta = {
            "chunk_id": f"{document_name}_chunk_{i}",
            "document_id": document_name,
            "part": block.get("part", ""),
            "chapter": block.get("chapter", ""),
            "section": block.get("section", ""),
            "legal_domain": legal_domain,
            "source_name": doc_metadata["source_name"],
            "chunk_hash": block_hash
        }
        block["metadata"] = chunk_meta
        
    return {
        "document_metadata": doc_metadata,
        "blocks": structured_blocks
    }
