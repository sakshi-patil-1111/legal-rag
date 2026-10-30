import os
import sys
import json
import chromadb
from chromadb.config import Settings
from collections import defaultdict
import hashlib

def main():
    try:
        db_dir = os.path.join(os.path.dirname(__file__), "chroma_db")
        client = chromadb.PersistentClient(path=db_dir, settings=Settings(anonymized_telemetry=False))
        collection = client.get_collection(name="nyaay_knowledge")
        
        # Get everything
        data = collection.get(include=["documents", "metadatas", "embeddings"])
        
        ids = data.get("ids", [])
        documents = data.get("documents", [])
        metadatas = data.get("metadatas", [])
        embeddings = data.get("embeddings", [])
        
        print(f"Total chunks found: {len(ids)}")
        
        # Output everything as JSON so the agent can analyze it
        output = []
        for i in range(len(ids)):
            emb = None
            emb_len = 0
            emb_hash = None
            try:
                if embeddings is not None and len(embeddings) > i:
                    emb = embeddings[i]
                    if emb is not None:
                        emb_len = len(emb)
                        # ensure it's a list for hashing
                        if hasattr(emb, "tolist"):
                            emb = emb.tolist()
                        emb_hash = hashlib.sha256(str(list(emb)).encode()).hexdigest()
            except Exception as e:
                pass
                
            output.append({
                "id": ids[i],
                "document": documents[i],
                "metadata": metadatas[i],
                "embedding_length": emb_len,
                "embedding_hash": emb_hash
            })
            
        with open("audit_results.json", "w", encoding="utf-8") as f:
            json.dump(output, f, indent=2)
            
        print("Done. Saved to audit_results.json")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
