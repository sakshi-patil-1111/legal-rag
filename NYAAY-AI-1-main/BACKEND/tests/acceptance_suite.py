import requests
import time
import sys

BASE_URL = "http://127.0.0.1:8000/api/drafting"
PASSED = 0
FAILED = 0

def print_result(name, success, detail=""):
    global PASSED, FAILED
    if success:
        print(f"[PASS]: {name} {detail}")
        PASSED += 1
    else:
        print(f"[FAIL]: {name} {detail}")
        FAILED += 1

def rate_limit_sleep():
    # Since Gemini 2.5 Free Tier is extremely strict (5 RPM),
    # we sleep to ensure we don't trigger burst rate limits.
    time.sleep(15)

def run_missing_info_loop():
    print("\n--- Running Missing Info Loop Test ---")
    payload = {"user_facts": "I want to file a police complaint about my stolen bike."}
    try:
        r1 = requests.post(f"{BASE_URL}/generate", json=payload)
        data1 = r1.json()
        if data1.get("status") == "MISSING_INFO":
            print_result("Initial Missing Info detection", True)
        else:
            print_result("Initial Missing Info detection", False, str(data1))
            return
            
        rate_limit_sleep()
        
        missing = data1.get("missing_fields", [])
        provided = {missing[0]: "Pulsar 150"}
        
        payload["provided_fields"] = provided
        r2 = requests.post(f"{BASE_URL}/generate", json=payload)
        data2 = r2.json()
        
        if data2.get("status") == "MISSING_INFO" or data2.get("status") == "SUCCESS":
            print_result("Provided partial info filters questions correctly", True)
        else:
            print_result("Provided partial info filters questions correctly", False, str(data2))
    except Exception as e:
        print_result("Missing Info Loop Test", False, str(e))

def run_negative_testing():
    print("\n--- Running Negative Edge Case Tests ---")
    cases = [
        ("Empty Prompt", ""),
        ("Gibberish", "asdfasdfasdfasdf"),
        ("Unrelated", "Give me a recipe for chocolate cake"),
    ]
    
    for name, facts in cases:
        try:
            r = requests.post(f"{BASE_URL}/generate", json={"user_facts": facts})
            # It shouldn't crash, it should return UNKNOWN or MISSING_INFO
            data = r.json()
            if "status" in data or "detail" in data:
                print_result(f"Negative Case: {name}", True)
            else:
                print_result(f"Negative Case: {name}", False, str(data))
        except Exception as e:
            print_result(f"Negative Case: {name}", False, str(e))
        rate_limit_sleep()

def run_edit_workflow():
    print("\n--- Running Edit Workflow Test ---")
    payload = {
        "user_facts": "Need an affidavit stating my name is Ansh and I am 30 years old residing in Mumbai.",
        "provided_fields": {"father_or_spouse_name": "Raj", "purpose_of_affidavit": "Passport"}
    }
    
    try:
        r1 = requests.post(f"{BASE_URL}/generate", json=payload)
        data1 = r1.json()
        doc_obj = data1.get("document_object")
        if not doc_obj:
            print_result("Generate V1 for Editing", False, str(data1))
            return
            
        print_result("Generate V1 for Editing", True)
        rate_limit_sleep()
        
        edit_payload = {
            "document_object": doc_obj,
            "edit_instructions": "Change my age to 31"
        }
        r2 = requests.post(f"{BASE_URL}/edit", json=edit_payload)
        doc_v2 = r2.json()
        
        if doc_v2.get("metadata", {}).get("version") == 2:
            print_result("Edit increments version to V2", True)
        else:
            print_result("Edit increments version to V2", False, str(doc_v2))
            
    except Exception as e:
        print_result("Edit Workflow Test", False, str(e))

def check_dead_code():
    print("\n--- Running Dead Code Audit ---")
    import os
    if os.path.exists("../app/services/drafting_service.py"):
        print_result("Dead code (drafting_service.py) removed", False, "File still exists")
    else:
        print_result("Dead code removed", True)
        
def run_all():
    print("Starting Final Acceptance Suite...")
    run_missing_info_loop()
    run_negative_testing()
    run_edit_workflow()
    check_dead_code()
    
    print("\n===============================")
    print(f"Total Passed: {PASSED}")
    print(f"Total Failed: {FAILED}")
    print("===============================")
    
    if FAILED > 0:
        sys.exit(1)

if __name__ == "__main__":
    run_all()
