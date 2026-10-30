import sys
import re

with open('app/ai/orchestrator.py', 'r', encoding='utf-8') as f:
    code = f.read()

# Add _estimate_complexity
estimate_code = '''
    def _estimate_complexity(self, question: str) -> bool:
        q = question.lower()
        has_multiple_issues = len(re.findall(r'\\b(and|also|additionally|further|moreover|what about|as well)\\b', q)) >= 2
        has_sc_request = bool(re.search(r'\\b(supreme court|sc judgment|precedent|case law|held)\\b', q))
        has_multi_domain = bool(re.search(r'\\b(rera|consumer|constitutional|fundamental right|natural justice)\\b', q)) and bool(re.search(r'\\b(compensation|refund|criminal|arrest|bail)\\b', q))
        word_count = len(question.split())
        is_long = word_count > 60
        signals = sum([has_multiple_issues, has_sc_request, has_multi_domain, is_long])
        return signals >= 1
'''

# Add _analyze_query_structured
structured_code = '''
    def _analyze_query_structured(self, question: str, history: List[Dict[str, Any]]) -> Dict[str, Any]:
        sys_prompt = \"\"\"You are a legal query analyzer for Indian law. Analyze the query and return ONLY this JSON:
{
  "sub_queries": ["string", ...],
  "domains": {"Domain Name": 0.9},
  "explicit_sc_requested": true|false
}
Rules:
- sub_queries: 1-5 concise retrieval strings for each legal sub-issue.
- domains: only Indian legal domains; confidence float (e.g. 0.9).
- explicit_sc_requested: true only if user explicitly mentions SC/precedent/case law.
Output ONLY the JSON. No explanation.\"\"\"
        user_prompt = f"User Query: {question}\\nJSON Output:"
        try:
            temp_client = genai.Client(api_key=key_rotator.get())
            import time
            import json
            for attempt in range(3):
                try:
                    res = temp_client.models.generate_content(
                        model='gemini-2.5-flash',
                        contents=user_prompt,
                        config=types.GenerateContentConfig(
                            system_instruction=sys_prompt,
                            response_mime_type="application/json"
                        )
                    )
                    break
                except Exception as e:
                    if "503" in str(e) and attempt < 2:
                        time.sleep(2)
                        continue
                    raise e
            return json.loads(res.text)
        except Exception as e:
            logger.warning(f"Structured analysis failed: {e}")
            return {"sub_queries": [question], "domains": {}, "explicit_sc_requested": False}
'''

# Add _multi_query_retrieve
multi_query_code = '''
    def _multi_query_retrieve(self, sub_queries: List[str], base_query_embedding: List[float], predicted_domains: Dict[str, float], doc_type_priority: str, filters: Dict[str, Any], explicit_sc_requested: bool) -> List[Dict[str, Any]]:
        if not sub_queries:
            return []
            
        import concurrent.futures
        
        # We can just embed them sequentially, it's fast enough. Or use batch if embedding_service supports it.
        # Currently embed_query embeds one. Let's do sequential for simplicity and safety, ~100ms each.
        embeddings = []
        for sq in sub_queries:
            try:
                emb = embedding_service.embed_query(sq)
                embeddings.append(emb)
            except:
                embeddings.append(base_query_embedding)
                
        all_results = []
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=4) as ex:
            futures = []
            for i, sq in enumerate(sub_queries):
                futures.append(ex.submit(
                    hybrid_retriever.search,
                    query=sq,
                    query_embedding=embeddings[i],
                    n_results=10,
                    where=filters,
                    predicted_domains=predicted_domains,
                    document_type_priority=doc_type_priority
                ))
                
            if explicit_sc_requested:
                # Add SC-only search for the first sub_query (usually the most encompassing) or a specifically crafted one
                if hasattr(hybrid_retriever, 'search_sc_only'):
                    futures.append(ex.submit(
                        hybrid_retriever.search_sc_only,
                        query="Supreme Court precedent " + sub_queries[0],
                        query_embedding=base_query_embedding,
                        n_results=10
                    ))
                    
            for f in futures:
                try:
                    res = f.result()
                    all_results.extend(res)
                except Exception as e:
                    logger.warning(f"Parallel retrieval failed: {e}")
                    
        # Deduplicate and keep highest score
        dedup_map = {}
        for r in all_results:
            cid = r["id"]
            if cid not in dedup_map:
                dedup_map[cid] = r
            else:
                # Merge logic - if RRF is higher, keep it
                if r.get("metadata", {}).get("rrf_score", 0) > dedup_map[cid].get("metadata", {}).get("rrf_score", 0):
                    dedup_map[cid] = r
                    
        unique_results = list(dedup_map.values())
        unique_results.sort(key=lambda x: x.get("metadata", {}).get("rrf_score", 0), reverse=True)
        return unique_results[:20]
'''

# Find class RAGOrchestrator:
# Insert new methods after def __init__(self):
new_code = code.replace('        self.client = genai.Client(api_key=key_rotator.get())', '        self.client = genai.Client(api_key=key_rotator.get())' + '\\n' + estimate_code + '\\n' + structured_code + '\\n' + multi_query_code)

with open('app/ai/orchestrator.py', 'w', encoding='utf-8') as f:
    f.write(new_code)

print("Patched orchestrator.py successfully.")
