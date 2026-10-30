import os
import hashlib
import sys
import logging
import time

# Ensure Python path includes the backend directory
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.knowledge.ingestion import ingestion_pipeline
from app.knowledge.vector_store import vector_store

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

CORPUS_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "corpus")

def calculate_file_hash(filepath: str) -> str:
    hasher = hashlib.sha256()
    with open(filepath, 'rb') as f:
        buf = f.read()
        hasher.update(buf)
    return hasher.hexdigest()

def get_ingested_hashes():
    """Retrieve already ingested file hashes from ChromaDB to prevent duplication."""
    try:
        # We query the DB for unique file_hash metadata
        db_docs = vector_store.collection.get(include=["metadatas"])
        metadatas = db_docs.get("metadatas", [])
        hashes = set(m.get("file_hash") for m in metadatas if m and "file_hash" in m)
        return hashes
    except Exception as e:
        logger.error(f"Failed to fetch existing hashes: {e}")
        return set()

def ingest_corpus():
    logger.info("Starting production corpus ingestion pipeline...")
    
    if not os.path.exists(CORPUS_DIR):
        logger.error(f"Corpus directory not found at {CORPUS_DIR}")
        return

    existing_hashes = get_ingested_hashes()
    logger.info(f"Found {len(existing_hashes)} previously ingested document versions.")

    files_processed = 0
    chunks_created = 0

    for filename in os.listdir(CORPUS_DIR):
        if not (filename.endswith(".md") or filename.endswith(".txt")):
            continue

        filepath = os.path.join(CORPUS_DIR, filename)
        file_hash = calculate_file_hash(filepath)

        if file_hash in existing_hashes:
            logger.info(f"Skipping {filename} - Already ingested (Version Hash: {file_hash[:8]})")
            continue

        logger.info(f"Ingesting new document/version: {filename} (Version Hash: {file_hash[:8]})")
        
        # Extract basic metadata from filename (e.g., "bns_2023.md" -> source_name: "bns_2023")
        source_name = os.path.splitext(filename)[0].upper()
        
        base_metadata = {
            "source_name": source_name,
            "document_id": filename,
            "file_hash": file_hash,
            "ingestion_timestamp": int(time.time()),
            "tenant_id": "global",
            "type": "statute" if "BNS" in source_name or "CONSTITUTION" in source_name or "BSA" in source_name else "judgment"
        }

        with open(filepath, 'r', encoding='utf-8') as f:
            text = f.read()

        try:
            # We bypass the standard pipeline's BM25 rebuild per document, 
            # and only rebuild it at the very end to save time.
            from app.knowledge.chunking import semantic_chunker
            from app.knowledge.embeddings import embedding_service
            
            chunks = semantic_chunker.chunk_text(text, base_metadata)
            if not chunks:
                logger.warning(f"No chunks generated for {filename}")
                continue
                
            texts_to_embed = [c["text"] for c in chunks]
            embeddings = embedding_service.embed_texts(texts_to_embed)
            
            vector_store.add_chunks(
                ids=[c["id"] for c in chunks],
                embeddings=embeddings,
                documents=texts_to_embed,
                metadatas=[c["metadata"] for c in chunks]
            )
            
            files_processed += 1
            chunks_created += len(chunks)
            logger.info(f"Successfully processed {filename}: {len(chunks)} chunks.")
            
        except Exception as e:
            logger.error(f"Failed to ingest {filename}: {e}")

    if files_processed > 0:
        logger.info(f"Ingestion complete. Rebuilding Global BM25 Index...")
        from app.knowledge.bm25_manager import bm25_manager
        bm25_manager.rebuild_index("global")
        logger.info(f"Pipeline finished: Processed {files_processed} files, created {chunks_created} chunks.")
    else:
        logger.info("No new documents to ingest.")

if __name__ == "__main__":
    ingest_corpus()
