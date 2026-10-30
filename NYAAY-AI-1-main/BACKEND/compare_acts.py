import re
import json

def get_existing_docs():
    with open('audit_results.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    docs = set()
    for item in data:
        meta = item.get("metadata", {})
        doc_id = meta.get("document_id") or meta.get("source_name") or ""
        docs.add(doc_id.upper())
    return docs

def normalize(name):
    # simple normalization to match things like "BNS 2023" to "BHARATIYA_NYAYA_SANHITA"
    name = name.lower()
    if 'bns' in name and 'ipc' in name: return ['BHARATIYA_NYAYA_SANHITA', 'BNS']
    if 'bnss' in name and 'crpc' in name: return ['BHARATIYA_NAGARIK_SURAKSHA_SANHITA', 'BNSS']
    if 'bsa' in name and 'evidence' in name: return ['BSA_2023', 'BSA']
    if 'constitution' in name: return ['CONSTITUTION_OF_INDIA']
    if 'cpc' in name: return ['CPC_1908']
    if 'contract act' in name: return ['INDIAN_CONTRACT_ACT']
    if 'hindu marriage' in name: return ['HINDU_MARRIAGE_ACT_1955']
    if 'consumer protection' in name: return ['CONSUMER_PROTECTION_ACT']
    if 'it act' in name or 'information technology' in name: return ['INFORMATION_TECHNOLOGY_ACT']
    
    return [name]

def main():
    existing_docs = get_existing_docs()
    
    with open('target_acts.txt', 'r', encoding='utf-8') as f:
        lines = f.readlines()
        
    current_category = None
    output = []
    
    for line in lines:
        line = line.strip()
        if not line: continue
        
        # Check if category header (e.g. "1. Constitutional & Administrative")
        if re.match(r'^\d+\.\s+', line):
            current_category = line
            output.append(f"\n### {current_category}")
            continue
            
        # It's an act
        act_name = line
        search_terms = normalize(act_name)
        
        found = False
        for term in search_terms:
            for edoc in existing_docs:
                if term in edoc or edoc in term:
                    found = True
                    break
            if found: break
            
        if not found:
            output.append(f"- [ ] {act_name}")
        else:
            # We don't print it if it's found, or we could mark it as found
            output.append(f"- [x] ~~{act_name}~~ (Present)")
            
    with open('missing_acts_report.md', 'w', encoding='utf-8') as f:
        f.write("\n".join(output))
        
    print("Comparison complete. Check missing_acts_report.md")

if __name__ == '__main__':
    main()
