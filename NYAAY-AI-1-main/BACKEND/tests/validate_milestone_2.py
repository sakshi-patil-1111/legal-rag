import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.knowledge.vector_store import vector_store
from app.knowledge.hybrid_retriever import hybrid_retriever
from app.knowledge.embeddings import embedding_service
from app.ai.orchestrator import rag_orchestrator

def run_validation():
    print("\n--- MILESTONE 2: KNOWLEDGE BASE VALIDATION ---\n")
    
    # 1. Inspect ChromaDB
    try:
        db_docs = vector_store.collection.get(include=["metadatas", "documents"])
        ids = db_docs.get("ids", [])
        metadatas = db_docs.get("metadatas", [])
        
        doc_ids = set()
        for m in metadatas:
            if m and "document_id" in m:
                doc_ids.add(m["document_id"])
                
        print(f"Total Unique Documents Ingested: {len(doc_ids)}")
        for doc in doc_ids:
            print(f"  - {doc}")
            
        print(f"\nTotal Chunks (Embeddings): {len(ids)}")
        
        if metadatas:
            print(f"\nSample Metadata Completeness:")
            for key, val in metadatas[0].items():
                print(f"  {key}: {val}")
    except Exception as e:
        print(f"Failed to query ChromaDB: {e}")

    # 2. Test Retrieval Pipeline
    print("\n\n--- TESTING HYBRID RETRIEVAL ---")
    query = "Can Parliament amend the fundamental rights?"
    print(f"Query: '{query}'")
    
    try:
        emb = embedding_service.embed_query(query)
        results = hybrid_retriever.search(query, emb, n_results=3)
        print(f"Retrieved {len(results)} chunks.")
        for i, res in enumerate(results):
            source = res['metadata'].get('source_name', 'Unknown')
            print(f"\nResult {i+1} [Source: {source}]:")
            print(f"{res['document'][:200]}...")
    except Exception as e:
        print(f"Retrieval test failed: {e}")

    # 3. Test Full RAG Orchestrator
    print("\n\n--- TESTING RAG ORCHESTRATOR ---")
    try:
        response = rag_orchestrator.trigger_pipeline(query, task_type="QA")
        print(f"LLM Answer:\n{response['answer']}")
        print(f"\nCitations used: {[c['marker'] for c in response['citations']]}")
    except Exception as e:
        print(f"RAG Orchestrator test failed: {e}")
        
if __name__ == "__main__":
    run_validation()
