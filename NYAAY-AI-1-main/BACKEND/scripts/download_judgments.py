import os
import json
from datasets import load_dataset
from tqdm import tqdm

BASE_DIR = os.path.dirname(__file__)
JUDGMENTS_DIR = os.path.join(BASE_DIR, "BACKEND", "data", "judgments")
MANIFEST_FILE = os.path.join(JUDGMENTS_DIR, "manifest.json")

def setup_directory():
    os.makedirs(JUDGMENTS_DIR, exist_ok=True)
    if not os.path.exists(MANIFEST_FILE):
        with open(MANIFEST_FILE, "w") as f:
            json.dump([], f)

def append_to_manifest(entries):
    if os.path.exists(MANIFEST_FILE):
        with open(MANIFEST_FILE, "r") as f:
            manifest = json.load(f)
    else:
        manifest = []
        
    manifest.extend(entries)
    
    with open(MANIFEST_FILE, "w") as f:
        json.dump(manifest, f, indent=2)

def main():
    print("Setting up directory...")
    setup_directory()
    
    # We will fetch 5000 Supreme Court judgments to provide a substantial but manageable high-quality corpus.
    TARGET_COUNT = 5000
    
    print(f"Loading HuggingFace dataset (Target: {TARGET_COUNT} cases)...")
    try:
        # Use streaming to avoid downloading the entire massive dataset to memory/disk cache at once if we only want 5000
        ds = load_dataset('sinhal/Indian_Supreme_Court_Judgments', split='train', streaming=True)
    except Exception as e:
        print(f"Error loading dataset: {e}")
        return

    success_count = 0
    manifest_entries = []
    
    for row in ds:
        if success_count >= TARGET_COUNT:
            break
            
        case_no = row.get('case_no', '')
        if not case_no:
            case_no = f"case_{success_count}"
            
        # Clean the case number to be a valid filename
        filename_base = "".join(c if c.isalnum() else "_" for c in case_no).strip("_")
        if not filename_base:
            filename_base = f"case_{success_count}"
            
        filename = f"{filename_base}.json"
        filepath = os.path.join(JUDGMENTS_DIR, filename)
        
        # Structure the judgement data nicely
        judgement_data = {
            "case_no": row.get("case_no"),
            "petitioner": row.get("pet"),
            "respondent": row.get("res"),
            "petitioner_advocate": row.get("pet_adv"),
            "respondent_advocate": row.get("res_adv"),
            "bench": row.get("bench"),
            "judgement_by": row.get("judgement_by"),
            "judgment_dates": row.get("judgment_dates"),
            "sections_cited": row.get("sections_cited"),
            "articles_cited": row.get("articles_cited"),
            "text": row.get("full_text")
        }
        
        # Only save if there is actual text
        if judgement_data["text"] and len(judgement_data["text"]) > 100:
            with open(filepath, "w", encoding="utf-8") as f:
                json.dump(judgement_data, f, indent=2)
                
            manifest_entries.append({
                "file": filename,
                "domain": "Supreme Court Judgments",
                "case_no": judgement_data["case_no"],
                "type": "judgment",
                "source": "huggingface:sinhal/Indian_Supreme_Court_Judgments"
            })
            success_count += 1
            
            if success_count % 500 == 0:
                print(f"Downloaded {success_count} judgments...")
                # Write to manifest in chunks so we don't lose progress if it crashes
                append_to_manifest(manifest_entries)
                manifest_entries = []
                
    if manifest_entries:
        append_to_manifest(manifest_entries)
        
    print(f"\nFinished! Successfully downloaded {success_count} Supreme Court judgments.")

if __name__ == "__main__":
    main()
