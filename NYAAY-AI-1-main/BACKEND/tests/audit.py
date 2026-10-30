import os
import sys
import time
import chromadb

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.config import settings

def run_audit():
    print("=== NYAAY AI RED TEAM AUDIT ===")
    
    db_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "chroma_db")
    
    print("\n--- PHASE 4: CORPUS VERIFICATION (CHROMADB) ---")
    try:
        client = chromadb.PersistentClient(path=db_dir)
        collections = client.list_collections()
        print(f"Number of Collections: {len(collections)}")
        for col in collections:
            count = col.count()
            print(f"Collection: {col.name}")
            print(f"Document/Chunk Count: {count}")
            if count > 0:
                results = col.get(limit=10)
                sources = set(meta.get('source_name', 'Unknown') for meta in results['metadatas'] if meta)
                print(f"Sample Sources: {sources}")
    except Exception as e:
        print(f"ChromaDB Inspection Failed: {e}")

    print("\n--- PHASE 7: SECURITY VERIFICATION ---")
    env_keys = ['GEMINI_API_KEY', 'JWT_SECRET_KEY']
    for k in env_keys:
        val = os.getenv(k)
        if val:
            print(f"SECRET {k} is loaded.")
        else:
            print(f"SECRET {k} is MISSING.")
            
if __name__ == "__main__":
    run_audit()
