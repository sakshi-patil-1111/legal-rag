import os
import sys
import json
import time
from collections import Counter
from google import genai

# Ensure backend directory is in path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.ai.orchestrator import rag_orchestrator
from app.ai.domain_classifier import domain_classifier

api_keys = [
    os.environ.get("GEMINI_API_KEY", "YOUR_API_KEY_HERE"),
    os.environ.get("GEMINI_API_KEY_2", "YOUR_API_KEY_2_HERE")
]

tricky_queries = [
    # Criminal & Corporate Cross-Domain
    "If a company's defective product kills someone, can the CEO be sentenced to death?",
    "Can a company claim self-defense if it uses armed guards to protect its factory?",
    "Is it legal to pay a hacker to test my own company's security if they break some systems?",
    
    # Family Law Edge Cases
    "If I marry an American in a Hindu ceremony in New York, can I divorce them under the Special Marriage Act in Delhi?",
    "Can a father refuse to pay maintenance to a daughter who earns more than him?",
    "Is a prenuptial agreement valid in India if it was signed in Dubai?",
    
    # Cyber & Tech
    "Can I be arrested for forwarding a WhatsApp message that turns out to be fake news about a politician?",
    "If someone steals my cryptocurrency, is it considered theft under the Indian Penal Code?",
    "Do I need to pay income tax on virtual goods sold in a video game?",
    
    # Consumer & Medical
    "Can I sue a government hospital for medical negligence under the Consumer Protection Act?",
    "If a restaurant charges a mandatory service charge, is it legally enforceable?",
    "Can a pharmacist refuse to sell me emergency contraceptives?",
    
    # Property & Real Estate
    "If I have been living on government land for 20 years, can I claim adverse possession?",
    "Can a housing society legally ban me from keeping a pet dog?",
    "If my landlord locks me out for not paying rent for a month, what legal recourse do I have?",
    
    # Labour & Employment
    "Can my employer legally fire me for a social media post I made on a Sunday?",
    "Am I legally entitled to leave if I suffer a miscarriage?",
    "Is a non-compete clause valid if it stops me from working anywhere in India for 5 years?",
    
    # Constitutional & Procedural
    "Can a police officer search my car without a warrant if I am pulled over for a broken taillight?",
    "If a state passes a law that contradicts a central law on education, which one prevails?",
    "Can I file a PIL (Public Interest Litigation) regarding a pothole on my street?",
    
    # Taxation & Finance
    "Is the money I win from an illegal betting app subject to income tax?",
    "Can a bank freeze my account just because I received a large international wire transfer?",
    "If I accidentally transfer money to the wrong UPI ID, is the recipient legally bound to return it?",
    
    # Environmental & Animal Rights
    "Is it a crime to cut down a 50-year-old tree in my own private backyard?",
    "Can I be punished for feeding stray dogs if the neighbors complain about a nuisance?",
    
    # Vague Layman Queries
    "My boss is making me work 14 hours a day without overtime, is this legal?",
    "I found a lost wallet with 1 lakh rupees, do I get to keep it if no one claims it?",
    "Can someone go to jail for a bounced cheque of 500 rupees?",
    "I bought a second-hand car but the seller lied about the mileage, can I go to consumer court?"
]

results_summary = []

print("Starting evaluation of 30 tricky queries with new API Keys.")

for i, q in enumerate(tricky_queries):
    # Rotate API Key
    current_key = api_keys[i % len(api_keys)]
    new_client = genai.Client(api_key=current_key)
    
    # Monkey-patch the clients to avoid exhaustion
    rag_orchestrator.client = new_client
    domain_classifier.client = new_client
    
    print(f"\n[{i+1}/30] Testing Query: {q} (Using Key {i % len(api_keys) + 1})")
    
    try:
        # Trigger full pipeline
        response = rag_orchestrator.trigger_pipeline(q)
        
        # Extract metadata
        retrieved_acts = []
        for citation in response.get("citations", []):
            act = citation.get("source_name", "Unknown Act")
            retrieved_acts.append(act)
            
        act_counts = dict(Counter(retrieved_acts))
        
        results_summary.append({
            "query": q,
            "answer": response.get("answer", ""),
            "confidence": response.get("confidence", {}).get("level", ""),
            "retrieved_acts": act_counts
        })
        print(f"  -> Generated answer of length {len(response.get('answer', ''))}")
        
        # Intermittent save
        with open("full_rag_test_results.json", "w", encoding="utf-8") as f:
            json.dump(results_summary, f, indent=4)
            
    except Exception as e:
        print(f"  -> Error evaluating query: {e}")
        results_summary.append({
            "query": q,
            "error": str(e)
        })
        
    # Sleep to be polite to the APIs
    print("  Sleeping 10s...")
    time.sleep(10)

with open("full_rag_test_results.json", "w", encoding="utf-8") as f:
    json.dump(results_summary, f, indent=4)

print("\nFinished evaluating 30 queries. Output saved to full_rag_test_results.json")
