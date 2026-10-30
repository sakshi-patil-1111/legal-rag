import os
import json
import re
from datasets import load_dataset

BASE_DIR = os.path.dirname(__file__)
DOCS_FILE = os.path.join(BASE_DIR, "DOCS", "target_corpus_structure.md")
BATCH_DIR = os.path.join(BASE_DIR, "BACKEND", "data", "batch_2")
MANIFEST_FILE = os.path.join(BATCH_DIR, "manifest.json")

def clean_filename(name):
    clean_name = re.sub(r'[^a-z0-9]', '_', name.lower())
    clean_name = re.sub(r'_+', '_', clean_name).strip('_')
    return clean_name

def normalize_text(text):
    return re.sub(r'[^a-z0-9]', '', str(text).lower())

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

def get_missing_acts():
    acts = parse_corpus_structure()
    with open(MANIFEST_FILE, "r") as f:
        manifest = json.load(f)
    found_names = [e["act_name"] for e in manifest]
    return [a for a in acts if a["act_name"] not in found_names]

def main():
    missing_acts = get_missing_acts()
    print(f"There are {len(missing_acts)} acts missing.")
    if not missing_acts:
        return
        
    print("Loading HuggingFace dataset...")
    try:
        ds = load_dataset('mratanusarkar/Indian-Laws', split='train')
    except Exception as e:
        print(f"Error loading dataset: {e}")
        return

    # Group all sections by act_title in the dataset
    print("Grouping dataset by act title...")
    dataset_acts = {}
    for row in ds:
        title = row.get('act_title')
        if not title:
            continue
        norm_title = normalize_text(title)
        if norm_title not in dataset_acts:
            dataset_acts[norm_title] = []
        dataset_acts[norm_title].append(row.get('law', ''))
        
    success_count = 0
    for act in missing_acts:
        act_norm = normalize_text(act["act_name"])
        best_match = None
        for ds_title in dataset_acts.keys():
            if act_norm in ds_title or ds_title in act_norm:
                if len(act_norm) > 10 and len(ds_title) > 10:
                    best_match = ds_title
                    break
        
        if best_match:
            print(f"Match found in HF dataset for '{act['act_name']}'")
            # Combine all sections
            full_text = "\n\n".join(dataset_acts[best_match])
            
            filename = f"{clean_filename(act['act_name'])}.txt"
            filepath = os.path.join(BATCH_DIR, filename)
            
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(full_text)
                
            append_to_manifest({
                "file": filename,
                "domain": act["domain"],
                "act_name": act["act_name"],
                "type": "statute",
                "source": "huggingface:mratanusarkar/Indian-Laws"
            })
            success_count += 1
        else:
            print(f"Still missing: {act['act_name']}")
            
    print(f"\nFinished! Found {success_count} more acts from HuggingFace.")

if __name__ == "__main__":
    main()
