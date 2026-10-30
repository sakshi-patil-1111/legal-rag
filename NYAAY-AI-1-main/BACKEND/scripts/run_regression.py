import asyncio
import sys
import os

# Add BACKEND to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.ai.orchestrator import rag_orchestrator
from app.knowledge.bm25_manager import bm25_manager

QUERIES = [
    ("FIR refusal", "A police officer refuses to register my FIR even though my laptop was stolen. What legal remedies are available?"),
    ("Bail", "What is the procedure to get anticipatory bail if I am falsely accused of a non-bailable offence?"),
    ("Murder vs Culpable Homicide", "What is the difference between murder and culpable homicide?"),
    ("Theft", "Someone took my bicycle without my permission. Is this considered theft?"),
    ("Robbery", "When does theft amount to robbery?"),
    ("Cybercrime", "Someone hacked my computer and copied my data. What are the penalties under the IT Act?"),
    ("Contract Breach", "If a contract is broken, what compensation can the aggrieved party claim?"),
    ("Consumer Protection", "I bought a defective product. Under the Consumer Protection Act, what rights do I have and which commission should I approach?"),
    ("Constitutional Rights", "What are the fundamental rights regarding freedom of speech and expression in India?"),
    ("Basic Structure", "Can Parliament amend the basic structure of the Constitution?"),
]

async def run_regression():
    print("# Retrieval Regression Test Report\n")
    
    # Pre-flight check: Load BM25 explicitly to ensure it's loaded in this process
    bm25_manager.get_index("global")
    
    passed = 0
    
    for category, query in QUERIES:
        print(f"## Category: {category}")
        print(f"**Query:** {query}")
        
        try:
            # We call the orchestrator's generate_response to get the end-to-end result
            # But the orchestrator returns an async generator, we just want to collect the full text and context.
            # We can use the hybrid_retriever directly for checking retrieval accuracy.
            from app.knowledge.embeddings import embedding_service
            from app.knowledge.hybrid_retriever import hybrid_retriever
            
            rewritten = rag_orchestrator._rewrite_query(query, [])
            query_emb = embedding_service.embed_query(rewritten)
            chunks = hybrid_retriever.search(rewritten, query_emb, n_results=5, where={"tenant_id": "global"})
            
            print("**Retrieved Sources (Top 3):**")
            for i, chunk in enumerate(chunks[:3]):
                meta = chunk.get("metadata", {})
                source = meta.get("source_name", "Unknown")
                section = meta.get("section_name", "Unknown")
                print(f"{i+1}. Source: {source} | Section: {section} | Method: {meta.get('retrieval_method')}")
            
            if chunks:
                passed += 1
                print("**Status:** SUCCESS")
            else:
                print("**Status:** FAILED (No chunks retrieved)")
                
        except Exception as e:
            print(f"**Status:** ERROR - {e}")
            
        print("\n---\n")
        
    print(f"**Total Passed:** {passed}/{len(QUERIES)}")

if __name__ == "__main__":
    asyncio.run(run_regression())
