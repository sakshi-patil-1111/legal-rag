import os, sys, re
sys.path.insert(0, os.path.abspath('BACKEND'))
from app.knowledge.vector_store import vector_store

def fix_metadata():
    print("Fetching SC collection metadata...")
    data = vector_store.sc_collection.get(include=['metadatas', 'documents'])
    ids = data['ids']
    metadatas = data['metadatas']
    documents = data['documents']
    
    updates = []
    
    for i in range(len(ids)):
        meta = metadatas[i]
        doc = documents[i]
        
        if meta.get('case_name') == 'None v. None':
            # Extract from document
            match_pet = re.search(r'PETITIONER:\s*(.*?)\s*Vs\.', doc, re.IGNORECASE | re.DOTALL)
            match_res = re.search(r'RESPONDENT:\s*(.*?)\s*DATE OF JUDGMENT:', doc, re.IGNORECASE | re.DOTALL)
            
            # fallback
            if not match_pet:
                match_pet = re.search(r'(.*?)\s+v\.\s+', doc[:200], re.IGNORECASE)
            
            p = match_pet.group(1).strip().replace('\n', ' ') if match_pet else "Unknown Petitioner"
            r = match_res.group(1).strip().replace('\n', ' ') if match_res else "Unknown Respondent"
            
            # special cleanups
            p = re.sub(r'\s+', ' ', p).strip()
            r = re.sub(r'\s+', ' ', r).strip()
            
            new_case_name = f"{p} v. {r}"
            
            if new_case_name != 'Unknown Petitioner v. Unknown Respondent':
                meta['case_name'] = new_case_name[:200]
                meta['petitioner'] = p[:100]
                meta['respondent'] = r[:100]
                
                # set source_name as well so LLM relevance gate can read it
                meta['source_name'] = new_case_name[:200]
                updates.append((ids[i], meta))
        elif meta.get('case_name'):
            # It has a case name but might miss source_name
            if 'source_name' not in meta or not meta['source_name']:
                meta['source_name'] = meta['case_name']
                updates.append((ids[i], meta))
                
    print(f"Found {len(updates)} chunks to update.")
    
    if updates:
        batch_size = 500
        for i in range(0, len(updates), batch_size):
            batch = updates[i:i+batch_size]
            b_ids = [b[0] for b in batch]
            b_metas = [b[1] for b in batch]
            vector_store.sc_collection.update(ids=b_ids, metadatas=b_metas)
            print(f"Updated {i + len(batch)}/{len(updates)}")
            
    print("Done.")

if __name__ == "__main__":
    fix_metadata()
