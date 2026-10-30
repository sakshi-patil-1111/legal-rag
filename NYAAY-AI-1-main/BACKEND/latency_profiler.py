import time
import json
import asyncio
from typing import Dict, Any
import firebase_admin
from firebase_admin import credentials, auth
from google import genai
from google.genai import types
from app.core.config import settings

def print_latency(name: str, start: float, end: float, total_duration: float):
    duration = (end - start) * 1000
    percentage = (duration / (total_duration * 1000)) * 100 if total_duration > 0 else 0
    print(f"{name}: {duration:.2f}ms ({percentage:.2f}%)")

async def profile_kanoon_query():
    print("--- STARTING KANOON LATENCY PROFILE ---")
    results = {}
    
    total_start = time.perf_counter()
    
    # 1. Firebase Auth Simulation (Skipping actual network call if using dummy, but we can measure raw logic)
    auth_start = time.perf_counter()
    # Simulated auth overhead
    await asyncio.sleep(0.05) 
    auth_end = time.perf_counter()
    results['Firebase Auth (Simulated)'] = (auth_start, auth_end)

    # 2. Validation & Prompt Construction
    prompt_start = time.perf_counter()
    question = "Can my landlord evict me without notice?"
    system_instruction = """You are NYAAY AI, a legal assistant for the Indian Judiciary Ecosystem.
Your goal is to answer legal questions clearly and simply.

Instructions:
1. Explain legal concepts clearly.
2. Use simple language when possible.
3. Distinguish facts from interpretation.
4. Never claim to be a lawyer.
5. Always include a legal disclaimer.
6. Avoid hallucinating court judgments.
7. State uncertainty when unsure.
8. Focus on Indian law generally. Use Constitution, BNS, BNSS, BSA and other relevant Indian legal principles when applicable.
9. You MUST provide real-life examples of cases with judgments passed mainly by the Supreme Court or High Courts to prove a point or support the query. Provide the base of the judgment (i.e. it was because of these specific reasons).
10. Format your output using Markdown (bolding, bullet points).

You MUST respond strictly in the following JSON format:
{
    "answer": "Detailed explanation of the legal concept using Markdown",
    "summary": "A short one-to-two sentence summary",
    "similar_cases": "Markdown formatted section titled 'Similar Cases Verdicts' containing verdicts with reasoning in a simplified and short manner",
    "disclaimer": "This information is for educational purposes only and does not constitute legal advice. Please consult a qualified lawyer for legal matters.",
    "category": "e.g., Property Law, Constitutional Law, Criminal Law, etc."
}"""
    prompt_end = time.perf_counter()
    results['Prompt Construction'] = (prompt_start, prompt_end)

    # 3. Gemini API Call
    gemini_start = time.perf_counter()
    api_key = settings.GEMINI_API_KEY
    client = genai.Client(api_key=api_key)
    
    response = client.models.generate_content(
        model='gemini-2.5-flash',
        contents=question,
        config=types.GenerateContentConfig(
            system_instruction=system_instruction,
            response_mime_type="application/json",
        ),
    )
    gemini_end = time.perf_counter()
    results['Gemini API Request'] = (gemini_start, gemini_end)
    
    # 4. Response Parsing and Serialization
    parse_start = time.perf_counter()
    try:
        response_json = json.loads(response.text)
    except Exception as e:
        response_json = {}
    parse_end = time.perf_counter()
    results['Response Parsing & Serialization'] = (parse_start, parse_end)
    
    total_end = time.perf_counter()
    total_duration = total_end - total_start
    
    print(f"\nTOTAL REQUEST DURATION: {total_duration * 1000:.2f}ms\n")
    for name, (start, end) in results.items():
        print_latency(name, start, end, total_duration)
        
    print("\n--- GEMINI AUDIT ---")
    print(f"Model Used: gemini-2.5-flash")
    print(f"System Prompt Size (chars): {len(system_instruction)}")
    print(f"Output Token Size (chars approx): {len(response.text)}")
    print("---------------------------------------")

if __name__ == "__main__":
    asyncio.run(profile_kanoon_query())
