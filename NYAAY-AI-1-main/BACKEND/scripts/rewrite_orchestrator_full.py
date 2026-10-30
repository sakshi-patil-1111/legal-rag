import re

with open('app/ai/orchestrator.py', 'r', encoding='utf-8') as f:
    code = f.read()

# Replace gemini-2.5-flash with gemini-3.6-flash
code = code.replace('gemini-2.5-flash', 'gemini-3.6-flash')

# 1. Insert new methods right before _filter_relevant_chunks
new_methods = '''
    def _estimate_complexity(self, question: str) -> bool:
        q = question.lower()
        has_multiple_issues = len(re.findall(r'\\b(and|also|additionally|further|moreover|what about|as well)\\b', q)) >= 2
        has_sc_request = bool(re.search(r'\\b(supreme court|sc judgment|precedent|case law|held)\\b', q))
        has_multi_domain = bool(re.search(r'\\b(rera|consumer|constitutional|fundamental right|natural justice)\\b', q)) and bool(re.search(r'\\b(compensation|refund|criminal|arrest|bail)\\b', q))
        word_count = len(question.split())
        is_long = word_count > 60
        signals = sum([has_multiple_issues, has_sc_request, has_multi_domain, is_long])
        return signals >= 1

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
                        model='gemini-3.6-flash',
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

    def _multi_query_retrieve(self, sub_queries: List[str], base_query_embedding: List[float], predicted_domains: Dict[str, float], doc_type_priority: str, filters: Dict[str, Any], explicit_sc_requested: bool) -> List[Dict[str, Any]]:
        if not sub_queries:
            return []
            
        import concurrent.futures
        
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
                    # Tag with sub_issue
                    for r in res:
                        if "sub_issue_ids" not in r["metadata"]:
                            r["metadata"]["sub_issue_ids"] = []
                        # Simplistic tagging
                    all_results.extend(res)
                except Exception as e:
                    logger.warning(f"Parallel retrieval failed: {e}")
                    
        dedup_map = {}
        for r in all_results:
            cid = r["id"]
            if cid not in dedup_map:
                dedup_map[cid] = r
            else:
                if r.get("metadata", {}).get("rrf_score", 0) > dedup_map[cid].get("metadata", {}).get("rrf_score", 0):
                    dedup_map[cid] = r
                    
        unique_results = list(dedup_map.values())
        unique_results.sort(key=lambda x: x.get("metadata", {}).get("rrf_score", 0), reverse=True)
        return unique_results[:20]
'''
# find _filter_relevant_chunks
idx = code.find('    def _filter_relevant_chunks')
code = code[:idx] + new_methods + '\n' + code[idx:]

# Now replace the body of trigger_pipeline and trigger_pipeline_stream to use the new logic
# We'll just replace specific parts of trigger_pipeline
# 1. replace _analyze_and_expand_query with complex logic

tp_start = code.find('    def trigger_pipeline(')
tp_end = code.find('    def trigger_pipeline_stream(')
tp_code = code[tp_start:tp_end]

# We modify tp_code:
# Find:
#         search_query = self._analyze_and_expand_query(question, history)
# ... up to ...
#         chunks = self._filter_relevant_chunks(question, chunks)
# Replace with adaptive logic

old_logic_start = tp_code.find('        # 1.5 Conversational Query Rewriting')
old_logic_end = tp_code.find('        retrieval_latency = round(time.time() - retrieval_start, 2)')

new_logic = '''        is_complex = self._estimate_complexity(question)
        query_analysis = {}
        
        if is_complex:
            query_analysis = self._analyze_query_structured(question, history)
            search_query = query_analysis.get("sub_queries", [question])[0]
            predicted_domains = query_analysis.get("domains", {})
            doc_type_priority = "any"
            explicit_sc = query_analysis.get("explicit_sc_requested", False)
            
            emb_start = time.time()
            try:
                query_embedding = embedding_service.embed_query(search_query)
            except Exception as e:
                logger.error(f"Failed to embed query: {e}")
                return self._fallback_response("Internal error while processing your question.")
            emb_latency = round(time.time() - emb_start, 2)
            
            retrieval_start = time.time()
            try:
                chunks = self._multi_query_retrieve(
                    query_analysis.get("sub_queries", [question]),
                    query_embedding,
                    predicted_domains,
                    doc_type_priority,
                    filters,
                    explicit_sc
                )
            except Exception as e:
                logger.error(f"Vector search failed: {e}")
                return self._fallback_response("Failed to retrieve context.")
                
        else:
            search_query = self._analyze_and_expand_query(question, history)
            
            emb_start = time.time()
            try:
                query_embedding = embedding_service.embed_query(search_query)
            except Exception as e:
                logger.error(f"Failed to embed query: {e}")
                return self._fallback_response("Internal error while processing your question.")
            emb_latency = round(time.time() - emb_start, 2)
            
            if not query_embedding:
                return self._fallback_response("Failed to process question text.")
                
            from app.ai.domain_classifier import domain_classifier
            domain_predictions = domain_classifier.predict_domain(search_query)
            predicted_domains = domain_predictions.get("domains", {})
            doc_type_priority = domain_predictions.get("document_type_priority", "any")

            retrieval_start = time.time()
            try:
                chunks = hybrid_retriever.search(
                    query=search_query, 
                    query_embedding=query_embedding, 
                    n_results=10, 
                    where=filters,
                    predicted_domains=predicted_domains,
                    document_type_priority=doc_type_priority
                )
            except Exception as e:
                logger.error(f"Vector search failed: {e}")
                return self._fallback_response("Failed to retrieve context.")
'''

tp_code = tp_code[:old_logic_start] + new_logic + tp_code[old_logic_end:]

# Fix Calculate Retrieval Confidence call
tp_code = tp_code.replace('calculate_retrieval_confidence(chunks)', 'calculate_retrieval_confidence(chunks, query_analysis if is_complex else None)')

# Fix construct_prompt call
tp_code = tp_code.replace('prompt_builder.construct_prompt(question, chunks, history, task_type=task_type)', 'prompt_builder.construct_prompt(question, chunks, history, task_type=task_type, sub_issues=query_analysis.get("sub_queries", []) if is_complex else [])')


# Now do stream method similarly
tps_start = code.find('    def trigger_pipeline_stream(')
tps_end = code.find('    def _generate_with_fallback(')
tps_code = code[tps_start:tps_end]

old_logic_start_s = tps_code.find('        search_query = self._analyze_and_expand_query(question, history)')
old_logic_end_s = tps_code.find('        retrieval_latency = round(time.time() - retrieval_start, 2)')

new_logic_s = '''        is_complex = self._estimate_complexity(question)
        query_analysis = {}
        
        if is_complex:
            query_analysis = self._analyze_query_structured(question, history)
            search_query = query_analysis.get("sub_queries", [question])[0]
            predicted_domains = query_analysis.get("domains", {})
            doc_type_priority = "any"
            explicit_sc = query_analysis.get("explicit_sc_requested", False)
            
            yield f"data: {json.dumps({'type': 'status', 'data': 'Searching legal corpus...'})}\\n\\n"
            emb_start = time.time()
            try:
                query_embedding = embedding_service.embed_query(search_query)
            except:
                yield f"data: {json.dumps({'type': 'error', 'data': 'Internal error while processing your question.'})}\\n\\n"
                return
            emb_latency = round(time.time() - emb_start, 2)
            
            retrieval_start = time.time()
            try:
                chunks = self._multi_query_retrieve(
                    query_analysis.get("sub_queries", [question]),
                    query_embedding,
                    predicted_domains,
                    doc_type_priority,
                    filters,
                    explicit_sc
                )
            except Exception as e:
                yield f"data: {json.dumps({'type': 'error', 'data': 'Failed to retrieve context.'})}\\n\\n"
                return
                
        else:
            search_query = self._analyze_and_expand_query(question, history)
            
            yield f"data: {json.dumps({'type': 'status', 'data': 'Searching legal corpus...'})}\\n\\n"
            emb_start = time.time()
            try:
                query_embedding = embedding_service.embed_query(search_query)
            except:
                yield f"data: {json.dumps({'type': 'error', 'data': 'Internal error while processing your question.'})}\\n\\n"
                return
            emb_latency = round(time.time() - emb_start, 2)
            
            if not query_embedding:
                yield f"data: {json.dumps({'type': 'error', 'data': 'Failed to process question text.'})}\\n\\n"
                return
                
            from app.ai.domain_classifier import domain_classifier
            domain_predictions = domain_classifier.predict_domain(search_query)
            predicted_domains = domain_predictions.get("domains", {})
            doc_type_priority = domain_predictions.get("document_type_priority", "any")

            retrieval_start = time.time()
            try:
                chunks = hybrid_retriever.search(
                    query=search_query, 
                    query_embedding=query_embedding, 
                    n_results=12, 
                    where=filters,
                    predicted_domains=predicted_domains,
                    document_type_priority=doc_type_priority
                )
            except Exception as e:
                yield f"data: {json.dumps({'type': 'error', 'data': 'Failed to retrieve context.'})}\\n\\n"
                return
'''

tps_code = tps_code[:old_logic_start_s] + new_logic_s + tps_code[old_logic_end_s:]
tps_code = tps_code.replace('prompt_builder.construct_prompt(question, chunks, history, task_type=task_type)', 'prompt_builder.construct_prompt(question, chunks, history, task_type=task_type, sub_issues=query_analysis.get("sub_queries", []) if is_complex else [])')

final_code = code[:tp_start] + tp_code + tps_code + code[tps_end:]
with open('app/ai/orchestrator.py', 'w', encoding='utf-8') as f:
    f.write(final_code)
    
print("Rewrote full orchestrator logic correctly.")
