import requests
import json
import os
import time

BASE_URL = "http://127.0.0.1:8000/api/drafting"
ARTIFACTS_DIR = r"C:\Users\ANSH DARJI\.gemini\antigravity\brain\61ef92e6-f3be-4e13-8ae3-4b62111b02a1\scratch"
os.makedirs(ARTIFACTS_DIR, exist_ok=True)

def test_intent_classification():
    scenarios = [
        "My phone was stolen.",
        "My employer didn't pay salary.",
        "My landlord won't return my deposit.",
        "My college misspelled my name.",
        "I need to give authority to my brother."
    ]
    results = []
    for s in scenarios:
        start_time = time.time()
        resp = requests.post(f"{BASE_URL}/generate", json={"user_facts": s})
        duration = time.time() - start_time
        results.append({"scenario": s, "response": resp.json(), "duration": duration})
    
    with open(os.path.join(ARTIFACTS_DIR, "intent_results.json"), "w") as f:
        json.dump(results, f, indent=2)
    print("Intent tests complete.")

def test_missing_info_resubmission():
    # 1. Provide vague facts
    resp = requests.post(f"{BASE_URL}/generate", json={"user_facts": "My landlord Amit won't return my deposit for the house in Delhi."})
    data = resp.json()
    with open(os.path.join(ARTIFACTS_DIR, "missing_info_stage1.json"), "w") as f:
        json.dump(data, f, indent=2)
        
    if data.get("status") == "MISSING_INFO":
        # 2. Resubmit with provided fields
        provided = {field: f"Dummy {field}" for field in data["missing_fields"]}
        resp2 = requests.post(f"{BASE_URL}/generate", json={"user_facts": "My landlord Amit won't return my deposit for the house in Delhi.", "provided_fields": provided})
        data2 = resp2.json()
        with open(os.path.join(ARTIFACTS_DIR, "missing_info_stage2.json"), "w") as f:
            json.dump(data2, f, indent=2)
            
        return data2.get("document_object")
    return data.get("document_object")

def test_generators(doc_obj):
    if not doc_obj:
        print("No document object to generate files for.")
        return
        
    # PDF
    start_time = time.time()
    resp_pdf = requests.post(f"{BASE_URL}/download/pdf", json=doc_obj)
    pdf_duration = time.time() - start_time
    if resp_pdf.status_code == 200:
        with open(os.path.join(ARTIFACTS_DIR, "test_draft.pdf"), "wb") as f:
            f.write(resp_pdf.content)
            
    # DOCX
    start_time = time.time()
    resp_docx = requests.post(f"{BASE_URL}/download/docx", json=doc_obj)
    docx_duration = time.time() - start_time
    if resp_docx.status_code == 200:
        with open(os.path.join(ARTIFACTS_DIR, "test_draft.docx"), "wb") as f:
            f.write(resp_docx.content)
            
    with open(os.path.join(ARTIFACTS_DIR, "perf_results.json"), "w") as f:
        json.dump({"pdf_duration": pdf_duration, "docx_duration": docx_duration}, f, indent=2)
    print("Generator tests complete.")

if __name__ == "__main__":
    print("Running intent tests...")
    test_intent_classification()
    print("Running missing info tests...")
    doc_obj = test_missing_info_resubmission()
    print("Running generator tests...")
    test_generators(doc_obj)
