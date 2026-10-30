import chromadb
from chromadb.config import Settings
import os
from typing import List, Dict, Any, Optional

DB_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "chroma_db")
BACKUP_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "chroma_db_backup")

def stitch_db(db_path: str):
    import glob
    parts = sorted(glob.glob(f"{db_path}.part*"), key=lambda x: int(x.split('.part')[-1]))
    if not parts or os.path.exists(db_path):
        return
    import logging
    logging.getLogger(__name__).info(f"Reconstructing {db_path} from {len(parts)} parts...")
    with open(db_path, 'wb') as outfile:
        for part in parts:
            with open(part, 'rb') as infile:
                outfile.write(infile.read())

class VectorStore:
    def __init__(self, collection_name: str = "nyaay_knowledge"):
        import shutil
        os.makedirs(DB_DIR, exist_ok=True)
        # Check and stitch both potential locations for the DB
        stitch_db(os.path.join(DB_DIR, "chroma.sqlite3"))
        if os.path.exists(BACKUP_DIR):
            stitch_db(os.path.join(BACKUP_DIR, "chroma.sqlite3"))
            
        # Copy from backup if DB_DIR is essentially empty
        db_file = os.path.join(DB_DIR, "chroma.sqlite3")
        if os.path.exists(BACKUP_DIR) and (not os.path.exists(db_file) or os.path.getsize(db_file) < 1000000):
            import logging
            logging.getLogger(__name__).info(f"Copying ChromaDB from {BACKUP_DIR} to {DB_DIR}")
            shutil.copytree(BACKUP_DIR, DB_DIR, dirs_exist_ok=True)

        
        # Initialize ChromaDB client using PersistentClient for local storage
        self.client = chromadb.PersistentClient(path=DB_DIR, settings=Settings(anonymized_telemetry=False))
        self.collection = self.client.get_or_create_collection(
            name=collection_name,
            metadata={"hnsw:space": "cosine"}
        )
        self.sc_collection = self.client.get_or_create_collection(
            name="supreme_court_cases",
            metadata={"hnsw:space": "cosine"}
        )

    def add_chunks(self, ids: List[str], embeddings: List[List[float]], documents: List[str], metadatas: List[Dict[str, Any]], target_collection: str = "nyaay_knowledge"):
        """Add vectorized chunks to the collection."""
        if not ids:
            return
            
        coll = self.collection if target_collection == "nyaay_knowledge" else self.sc_collection
        
        # Chroma API limits batch size
        batch_size = 500
        for i in range(0, len(ids), batch_size):
            coll.upsert(
                ids=ids[i:i + batch_size],
                embeddings=embeddings[i:i + batch_size],
                documents=documents[i:i + batch_size],
                metadatas=metadatas[i:i + batch_size]
            )

    def search(self, query_embedding: List[float], n_results: int = 5, where: Optional[Dict[str, Any]] = None, search_sc: bool = False) -> List[Dict[str, Any]]:
        """Search for the most similar chunks. Optionally include supreme_court_cases."""
        
        def do_search(coll, n, where_clause):
            # ChromaDB expects None, not an empty dict
            if where_clause == {}:
                where_clause = None
                
            # Pass where_clause to ChromaDB if it's not None
            try:
                res = coll.query(
                    query_embeddings=[query_embedding],
                    n_results=n,
                    where=where_clause,
                    include=["documents", "metadatas", "distances"]
                )
                formatted = []
                if res and res["ids"] and len(res["ids"]) > 0:
                    for i in range(len(res["ids"][0])):
                        formatted.append({
                            "id": res["ids"][0][i],
                            "document": res["documents"][0][i],
                            "metadata": res["metadatas"][0][i],
                            "distance": res["distances"][0][i]
                        })
                return formatted
            except Exception as e:
                import logging
                logging.getLogger(__name__).error(f"Retrieval failed for collection {coll.name} with where={where_clause}. Error: {e}")
                return []

        results = do_search(self.collection, n_results, where)
        
        if search_sc:
            # Normalize where clause for SC collection (remove tenant_id, keep legal_domain)
            sc_where = None
            if where:
                sc_where = {}
                if "legal_domain" in where:
                    sc_where["legal_domain"] = where["legal_domain"]
                if "$and" in where:
                    valid_conds = [c for c in where["$and"] if "tenant_id" not in c]
                    if valid_conds:
                        sc_where["$and"] = valid_conds
                if not sc_where:
                    sc_where = None

            # Retrieve equal number of SC results to guarantee representation
            sc_results = do_search(self.sc_collection, n_results, sc_where)
            results.extend(sc_results)
            # Re-sort by distance (lower is better for cosine distance in Chroma)
            results.sort(key=lambda x: x["distance"])
            # Return all (up to 2 * n_results) so RRF has access to both sets fully
        
        return results
        
    def delete_by_metadata(self, where: Dict[str, Any]):
        """Delete documents matching specific metadata (e.g. document_id)."""
        self.collection.delete(where=where)

# Singleton instance for global access
vector_store = VectorStore()
