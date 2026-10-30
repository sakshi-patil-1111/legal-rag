
import os, sys, re, json, glob
sys.path.insert(0, os.path.abspath('BACKEND'))
from app.knowledge.vector_store import vector_store

def get_case_name_from_json(json_path):
    try:
        with open(json_path, 'r', encoding='utf-8') as f:
            content = f.read().strip()
            if not content: return None
            data = json.loads(content)
        
        # Try metadata fields
        p = data.get('petitioner')
        r = data.get('respondent')
        if p and r and p != 'None' and r != 'None':
            return f'{p} v. {r}'.strip()
            
        # Fallback to full text regex
        text = data.get('text', '')
        if not text: return None
        
        match_pet = re.search(r'PETITIONER:\s*(.*?)\s*Vs\.', text, re.IGNORECASE | re.DOTALL)
        match_res = re.search(r'RESPONDENT:\s*(.*?)\s*DATE OF JUDGMENT:', text, re.IGNORECASE | re.DOTALL)
        if match_pet and match_res:
            p = match_pet.group(1).strip().replace('\n', ' ')
            r = match_res.group(1).strip().replace('\n', ' ')
            p = re.sub(r'\s+', ' ', p).strip()
            r = re.sub(r'\s+', ' ', r).strip()
            return f'{p} v. {r}'
            
        return None
    except Exception as e:
        return None

def fix_metadata():
    print('Fetching SC collection metadata...')
    data = vector_store.sc_collection.get(include=['metadatas'])
    ids = data['ids']
    metadatas = data['metadatas']
    
    # map case_id -> actual case name
    case_names = {}
    updates = []
    
    for i in range(len(ids)):
        meta = metadatas[i]
        case_id = meta.get('case_id')
        
        if not case_id: continue
        
        # Determine if it needs fix
        current_name = meta.get('case_name')
        if current_name == 'None v. None' or current_name == 'None v. Unknown Respondent' or current_name == 'Unknown v. Unknown':
            if case_id not in case_names:
                # Find the json
                json_basename = case_id.replace('SC_', '') + '.json'
                json_path = os.path.join('BACKEND', 'data', 'judgments', json_basename)
                if os.path.exists(json_path):
                    real_name = get_case_name_from_json(json_path)
                    if real_name:
                        case_names[case_id] = real_name
                    else:
                        case_names[case_id] = 'Unknown Case'
                else:
                    case_names[case_id] = 'Unknown Case'
            
            real_name = case_names[case_id]
            if real_name != 'Unknown Case':
                meta['case_name'] = real_name[:200]
                meta['source_name'] = real_name[:200]
                updates.append((ids[i], meta))
        elif meta.get('case_name') and not meta.get('source_name'):
            meta['source_name'] = meta['case_name']
            updates.append((ids[i], meta))
            
    print(f'Found {len(updates)} chunks to update.')
    
    if updates:
        batch_size = 500
        for i in range(0, len(updates), batch_size):
            batch = updates[i:i+batch_size]
            b_ids = [b[0] for b in batch]
            b_metas = [b[1] for b in batch]
            vector_store.sc_collection.update(ids=b_ids, metadatas=b_metas)
            print(f'Updated {i + len(batch)}/{len(updates)}')
            
    print('Done.')

if __name__ == '__main__':
    fix_metadata()

