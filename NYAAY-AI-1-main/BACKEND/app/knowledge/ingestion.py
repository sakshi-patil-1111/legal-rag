from typing import Dict, Any, List
from app.knowledge.chunking import semantic_chunker
from app.knowledge.embeddings import embedding_service
from app.knowledge.vector_store import vector_store
import logging

logger = logging.getLogger(__name__)

class IngestionPipeline:
    def __init__(self):
        pass

    def process_document(self, text: str, base_metadata: Dict[str, Any]):
        """
        Processes a raw document string: chunks it, embeds it, and stores it in the Vector Database.
        """
        logger.info(f"Starting ingestion for document: {base_metadata.get('document_id', 'unknown')}")
        
        # 1. Chunking
        chunks = semantic_chunker.chunk_text(text, base_metadata)
        logger.info(f"Created {len(chunks)} chunks.")
        
        if not chunks:
            logger.warning("No chunks generated from document.")
            return

        # Prepare lists for vector store
        ids = []
        documents = []
        metadatas = []
        texts_to_embed = []
        
        for chunk in chunks:
            ids.append(chunk["id"])
            documents.append(chunk["text"])
            metadatas.append(chunk["metadata"])
            texts_to_embed.append(chunk["text"])
            
        # 2. Embedding
        logger.info("Generating embeddings...")
        try:
            embeddings = embedding_service.embed_texts(texts_to_embed)
        except Exception as e:
            logger.error(f"Embedding failed during ingestion: {e}")
            raise e
            
        # 3. Storage
        logger.info("Storing in vector database...")
        vector_store.add_chunks(
            ids=ids,
            embeddings=embeddings,
            documents=documents,
            metadatas=metadatas
        )
        
        # 4. Rebuild BM25 Index
        from app.knowledge.bm25_manager import bm25_manager
        tenant_id = base_metadata.get("tenant_id", "global")
        try:
            bm25_manager.rebuild_index(tenant_id)
        except Exception as e:
            logger.error(f"Failed to rebuild BM25 index after ingestion: {e}")

        logger.info(f"Successfully ingested {len(chunks)} chunks.")

ingestion_pipeline = IngestionPipeline()
