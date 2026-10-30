import os
import sys
import time
import json
import hashlib
import logging
import argparse

# Ensure Python path includes the backend directory
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.knowledge.chunking import semantic_chunker
from app.knowledge.embeddings import embedding_service
from app.knowledge.vector_store import vector_store
from app.knowledge.bm25_manager import bm25_manager

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

CORPUS_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "corpus")
REPORT_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "corpus_statistics_report.json")

def parse_frontmatter(text: str):
    frontmatter = {}
    body = text
    if text.startswith("---\n"):
        parts = text.split("---\n", 2)
        if len(parts) >= 3:
            fm_text = parts[1]
            body = parts[2]
            for line in fm_text.strip().split('\n'):
                if ':' in line:
                    k, v = line.split(':', 1)
                    frontmatter[k.strip()] = v.strip()
    return frontmatter, body

def calculate_file_hash(filepath: str) -> str:
    hasher = hashlib.sha256()
    with open(filepath, 'rb') as f:
        buf = f.read()
        hasher.update(buf)
    return hasher.hexdigest()

def get_existing_hashes():
    """Retrieve already ingested file hashes from ChromaDB to prevent duplication."""
    try:
        db_docs = vector_store.collection.get(include=["metadatas"])
        metadatas = db_docs.get("metadatas", [])
        hashes = set(m.get("file_hash") for m in metadatas if m and "file_hash" in m)
        return hashes
    except Exception as e:
        logger.error(f"Failed to fetch existing hashes: {e}")
        return set()

def build_pipeline():
    logger.info("Starting Offline Indexing Pipeline...")
    
    if not os.path.exists(CORPUS_DIR):
        logger.error(f"Corpus directory not found at {CORPUS_DIR}")
        return

    existing_hashes = get_existing_hashes()
    logger.info(f"Found {len(existing_hashes)} previously ingested document versions.")

    stats = {
        "start_time": int(time.time()),
        "documents_processed": 0,
        "documents_skipped": 0,
        "total_chunks_created": 0,
        "total_embeddings_created": 0,
        "corpus_coverage": {},
        "errors": []
    }

    # 1. Corpus Iteration
    files_to_process = [f for f in os.listdir(CORPUS_DIR) if f.endswith(".md") or f.endswith(".txt")]
    
    for filename in files_to_process:
        filepath = os.path.join(CORPUS_DIR, filename)
        
        # 2. Duplicate Detection & Versioning
        file_hash = calculate_file_hash(filepath)
        if file_hash in existing_hashes:
            logger.info(f"Skipping {filename} - Already ingested (Hash: {file_hash[:8]})")
            stats["documents_skipped"] += 1
            continue

        logger.info(f"Ingesting new document: {filename} (Hash: {file_hash[:8]})")
        
        with open(filepath, 'r', encoding='utf-8') as f:
            text = f.read()
            
        frontmatter, clean_text = parse_frontmatter(text)
        
        # 3. Parsing & Metadata Extraction
        source_name = frontmatter.get("source_name", os.path.splitext(filename)[0].upper())
        domain = frontmatter.get("legal_domain")
        doc_type = frontmatter.get("document_type", "statute")
        act_name = frontmatter.get("act_name", source_name)
        
        if not domain:
            logger.error(f"Validation Failed: Missing 'legal_domain' in frontmatter for {filename}")
            stats["errors"].append({"file": filename, "error": "Missing legal_domain in frontmatter"})
            continue

        base_metadata = {
            "source_name": source_name,
            "document_id": filename,
            "file_hash": file_hash,
            "legal_domain": domain,
            "type": doc_type,
            "act_name": act_name,
            "tenant_id": "global",
            "ingestion_timestamp": int(time.time())
        }

        # 4. Validation
        if len(text.strip()) < 50:
            logger.warning(f"File {filename} is too short. Skipping.")
            stats["errors"].append({"file": filename, "error": "Too short"})
            continue

        try:
            # 5. Structural Chunking
            chunks = semantic_chunker.chunk_text(clean_text, base_metadata)
            if not chunks:
                logger.warning(f"No chunks generated for {filename}")
                stats["errors"].append({"file": filename, "error": "No chunks generated"})
                continue
                
            # 5.5 Corpus Validation (Phase 4)
            validation_errors = []
            seen_chunk_ids = set()
            chunk_sizes = []
            for c in chunks:
                c_text = c.get("text", "")
                c_id = c.get("id")
                c_meta = c.get("metadata", {})
                
                if not c_text.strip():
                    validation_errors.append(f"Empty chunk found: {c_id}")
                if c_id in seen_chunk_ids:
                    validation_errors.append(f"Duplicate chunk ID: {c_id}")
                seen_chunk_ids.add(c_id)
                chunk_sizes.append(len(c_text))
                
                # Check metadata
                required_meta = ["source_name", "document_id", "file_hash", "legal_domain"]
                for req in required_meta:
                    if req not in c_meta:
                        validation_errors.append(f"Broken metadata: Missing {req} in {c_id}")
            
            if validation_errors:
                logger.error(f"Validation failed for {filename}. Errors: {validation_errors}")
                stats["errors"].append({"file": filename, "error": "Validation failed", "details": validation_errors})
                continue # Stop indexing if validation fails
                
            texts_to_embed = [c["text"] for c in chunks]
            
            # 6. Embedding Generation
            embeddings = embedding_service.embed_texts(texts_to_embed)
            
            # 7. Vector Store Update
            vector_store.add_chunks(
                ids=[c["id"] for c in chunks],
                embeddings=embeddings,
                documents=texts_to_embed,
                metadatas=[c["metadata"] for c in chunks]
            )
            
            stats["documents_processed"] += 1
            stats["total_chunks_created"] += len(chunks)
            stats["total_embeddings_created"] += len(embeddings)
            stats["corpus_coverage"][source_name] = len(chunks)
            
            logger.info(f"Successfully processed {filename}: {len(chunks)} chunks.")
            
        except Exception as e:
            logger.error(f"Failed to ingest {filename}: {e}")
            stats["errors"].append({"file": filename, "error": str(e)})

    # 8. BM25 Index Construction
    if stats["documents_processed"] > 0:
        logger.info(f"Rebuilding Global BM25 Index...")
        start_bm25 = time.time()
        bm25_manager.rebuild_index("global")
        logger.info(f"BM25 Index rebuilt in {time.time() - start_bm25:.2f} seconds.")
    else:
        logger.info("No new documents to ingest. BM25 index remains unchanged.")

    # 9. Corpus Statistics Generation
    stats["end_time"] = int(time.time())
    stats["total_processing_time_seconds"] = stats["end_time"] - stats["start_time"]
    
    with open(REPORT_PATH, 'w', encoding='utf-8') as f:
        json.dump(stats, f, indent=4)
        
    logger.info(f"Pipeline finished. Statistics written to {REPORT_PATH}")
    logger.info(f"Summary: {stats['documents_processed']} docs processed, {stats['total_chunks_created']} chunks created.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="NYAAY AI 2.0 Offline Indexing Pipeline")
    parser.add_argument("command", choices=["build"], help="Command to execute")
    args = parser.parse_args()
    
    if args.command == "build":
        build_pipeline()
