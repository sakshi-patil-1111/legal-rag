import sys
import os
import time

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.knowledge.vector_store import vector_store

SECTION_TO_DOMAIN = {
    # Criminal Law
    "IPC": "Criminal Law", "BNS": "Criminal Law", "S. 302": "Criminal Law",
    "CrPC": "Criminal Law", "BNSS": "Criminal Law",
    # Constitutional
    "Art. 14": "Constitutional & Administrative", "Art. 21": "Constitutional & Administrative",
    "Art. 32": "Constitutional & Administrative", "Art. 226": "Constitutional & Administrative",
    # Property
    "T.P. Act": "Property & Real Estate", "Transfer of Property": "Property & Real Estate",
    "RERA": "Property & Real Estate",
    # Civil & Procedural
    "Limitation": "Civil & Procedural Law", "CPC": "Civil & Procedural Law",
    # Evidence
    "Evidence Act": "Evidence Law", "BSA": "Evidence Law",
    # Consumer
    "Consumer Protection": "Consumer & Product Liability",
    # Labour
    "Gratuity": "Labour & Employment", "Industrial Disputes": "Labour & Employment"
}

def backfill():
    print("Fetching SC cases from vector store...")
    sc_data = vector_store.sc_collection.get(include=["metadatas"])
    
    ids = sc_data.get("ids", [])
    metadatas = sc_data.get("metadatas", [])
    
    if not ids:
        print("No SC cases found.")
        return
        
    print(f"Found {len(ids)} SC chunks.")
    
    updated_count = 0
    batch_ids = []
    batch_metas = []
    
    for i, meta in enumerate(metadatas):
        updated = False
        
        # 1. Backfill Domain
        if not meta.get("legal_domain"):
            sections_cited = meta.get("sections_cited", "")
            case_name = meta.get("case_name", "").lower()
            domain = "Constitutional & Administrative" # Default for SC if unknown
            
            # Simple keyword matching for domain
            if "rape" in case_name or "murder" in case_name or "criminal" in case_name:
                domain = "Criminal Law"
            elif "tax" in case_name:
                domain = "Tax Law"
            elif "property" in case_name or "land" in case_name:
                domain = "Property & Real Estate"
                
            for kw, d in SECTION_TO_DOMAIN.items():
                if kw in sections_cited:
                    domain = d
                    break
                    
            meta["legal_domain"] = domain
            updated = True
            
        # 2. Backfill source_name for Citation
        if not meta.get("source_name"):
            meta["source_name"] = meta.get("case_name", "Supreme Court Judgment")
            updated = True
            
        if updated:
            batch_ids.append(ids[i])
            batch_metas.append(meta)
            updated_count += 1
            
        if len(batch_ids) >= 100:
            vector_store.sc_collection.update(ids=batch_ids, metadatas=batch_metas)
            batch_ids = []
            batch_metas = []
            
    if batch_ids:
        vector_store.sc_collection.update(ids=batch_ids, metadatas=batch_metas)
        
    print(f"Successfully updated metadata for {updated_count} SC chunks.")

if __name__ == '__main__':
    backfill()
