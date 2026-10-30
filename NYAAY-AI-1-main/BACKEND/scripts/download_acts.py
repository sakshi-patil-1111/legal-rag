import os
import json
import re
from bs4 import BeautifulSoup
import shutil

BASE_DIR = os.path.dirname(__file__)
DOCS_FILE = os.path.join(BASE_DIR, "DOCS", "target_corpus_structure.md")
BATCH_DIR = os.path.join(BASE_DIR, "BACKEND", "data", "batch_2")
MANIFEST_FILE = os.path.join(BATCH_DIR, "manifest.json")
LAWS_DIR = os.path.join(BASE_DIR, "laws-of-india-2")

def clean_filename(name):
    clean_name = re.sub(r'[^a-z0-9]', '_', name.lower())
    clean_name = re.sub(r'_+', '_', clean_name).strip('_')
    return clean_name

def normalize_text(text):
    # Remove all non-alphanumeric and convert to lowercase for loose matching
    return re.sub(r'[^a-z0-9]', '', text.lower())

def setup_directory():
    if os.path.exists(BATCH_DIR):
        shutil.rmtree(BATCH_DIR)
    os.makedirs(BATCH_DIR, exist_ok=True)
    with open(MANIFEST_FILE, "w") as f:
        json.dump([], f)

def append_to_manifest(entry):
    with open(MANIFEST_FILE, "r") as f:
        manifest = json.load(f)
    manifest.append(entry)
    with open(MANIFEST_FILE, "w") as f:
        json.dump(manifest, f, indent=2)

def parse_corpus_structure():
    acts = []
    current_domain = None
    with open(DOCS_FILE, "r", encoding="utf-8") as f:
        lines = f.readlines()
        
    for line in lines:
        line = line.strip()
        domain_match = re.match(r'^##\s+\d+\.\s+(.+)$', line)
        if domain_match:
            current_domain = domain_match.group(1).strip()
            if "Secondary Sources" in current_domain:
                current_domain = None
            continue
            
        if current_domain and line.startswith("* "):
            act_name_raw = line[2:].strip().replace('**', '')
            act_name = re.sub(r'\(.*?\)', '', act_name_raw).strip()
            if "Mapping Document" in act_name:
                continue
            acts.append({"domain": current_domain, "act_name": act_name})
    return acts

def build_index():
    # Build an index of all XML files available
    xml_files = []
    for root, _, files in os.walk(LAWS_DIR):
        for f in files:
            if f.endswith(".xml"):
                xml_files.append({
                    "name": f,
                    "normalized": normalize_text(f.replace('.xml', '')),
                    "path": os.path.join(root, f)
                })
    return xml_files

def extract_text_from_xml(filepath):
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            soup = BeautifulSoup(f.read(), 'xml')
            return soup.get_text(separator='\n', strip=True)
    except Exception as e:
        print(f"Error parsing {filepath}: {e}")
        return None

def main():
    print("Parsing corpus structure...")
    acts = parse_corpus_structure()
    print(f"Found {len(acts)} acts in corpus structure.")
    
    setup_directory()
    
    print("Indexing local laws repository...")
    index = build_index()
    print(f"Found {len(index)} XML acts in repository.")
    
    success_count = 0
    for act in acts:
        act_norm = normalize_text(act["act_name"])
        
        # Some tweaks for better matching
        # "Bharatiya Nyaya Sanhita" doesn't exist in 2020 dumps, but we try anyway.
        # "Semiconductor Integrated Circuits Layout-Design Act" 
        
        best_match = None
        for item in index:
            if act_norm in item["normalized"] or item["normalized"] in act_norm:
                # To prevent very short generic names from matching everything
                if len(act_norm) > 10 and len(item["normalized"]) > 10:
                    best_match = item
                    break
        
        if best_match:
            print(f"Match found for '{act['act_name']}': {best_match['name']}")
            text = extract_text_from_xml(best_match["path"])
            if text and len(text) > 100:
                filename = f"{clean_filename(act['act_name'])}.txt"
                filepath = os.path.join(BATCH_DIR, filename)
                
                with open(filepath, "w", encoding="utf-8") as f:
                    f.write(text)
                    
                append_to_manifest({
                    "file": filename,
                    "domain": act["domain"],
                    "act_name": act["act_name"],
                    "type": "statute",
                    "source_xml": best_match["name"]
                })
                success_count += 1
        else:
            print(f"No match found in repository for '{act['act_name']}'. Skipping.")
            
    print(f"\nFinished! Successfully processed and extracted REAL text for {success_count} acts.")

if __name__ == "__main__":
    main()
