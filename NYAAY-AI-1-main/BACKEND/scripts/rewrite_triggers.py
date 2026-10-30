import sys
import re

with open('app/ai/orchestrator.py', 'r', encoding='utf-8') as f:
    code = f.read()

# We will replace trigger_pipeline and trigger_pipeline_stream.
# Let's locate them.
trigger_pipeline_pattern = r'def trigger_pipeline\(self.*?def trigger_pipeline_stream'
# It's better to just write the new methods entirely and replace them.

new_trigger_pipeline = '''
    def trigger_pipeline(self, question: str, filters: Dict[str, Any] = None, history: List[Dict[str, Any]] = None, task_type: str = "QA") -> Dict[str, Any]:
        import time
        overall_start = time.time()
        
        if not guardrails.validate_input(question):
            return self._fallback_response("Your question violates safety or length policies.")

        is_complex = self._estimate_complexity(question)
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
            retrieval_latency = round(time.time() - retrieval_start, 2)
            # Replaced the LLM filter with the structured pre-retrieval
            
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
            retrieval_latency = round(time.time() - retrieval_start, 2)
            # Filter relevant chunks removed for simple queries
        
        # Calculate Retrieval Confidence
        r_conf_score, r_conf_label, r_conf_reason, avg_score, max_score = calculate_retrieval_confidence(chunks, query_analysis if is_complex else None)

        pc_start = time.time()
        
        # We need to pass sub_issues to prompt_builder if complex
        sub_issues = query_analysis.get("sub_queries", []) if is_complex else []
        
        system_instruction, user_prompt = prompt_builder.construct_prompt(question, chunks, history, task_type=task_type, sub_issues=sub_issues)
        pc_latency = round(time.time() - pc_start, 2)
        
        gen_start = time.time()
        raw_answer, retry_sleep_time = self._generate_with_fallback(system_instruction, user_prompt)
        
        if raw_answer:
            is_valid, validated_answer = validate_response(raw_answer)
            if not is_valid:
                logger.warning(f"Validation failed: {validated_answer}. Regenerating once.")
                raw_answer, retry_sleep_time2 = self._generate_with_fallback(system_instruction, user_prompt)
                retry_sleep_time += retry_sleep_time2
                if raw_answer:
                    is_valid, validated_answer = validate_response(raw_answer)
                    raw_answer = validated_answer if is_valid else None
            else:
                raw_answer = validated_answer
                
        gen_total_latency = time.time() - gen_start
        model_processing_time = round(max(0, gen_total_latency - retry_sleep_time), 2)
        total_latency = round(time.time() - overall_start, 2)
        
        metrics = {
            "embedding_time": emb_latency,
            "retrieval_time": retrieval_latency,
            "prompt_construction_time": pc_latency,
            "model_processing_time": model_processing_time,
            "retry_delay_time": retry_sleep_time,
            "total_latency": total_latency,
            "is_complex": is_complex
        }
        
        if not raw_answer:
            global_metrics.record_failure("llm_failures")
            return self._fallback_response("Failed to generate an answer. The AI service may be overloaded.")

        rs_score, rs_label = extract_reasoning_confidence(raw_answer)
        
        used_citations = set(re.findall(r'\[(\d+)\]', raw_answer))
        auth_retrieved = len(chunks)
        auth_used = len(used_citations)
        
        statutes_used = 0
        sc_used = 0
        citations = []
        for i, chunk in enumerate(chunks):
            marker_num = str(i + 1)
            if marker_num in used_citations:
                meta = chunk.get("metadata", {})
                src_name = meta.get("source_name", "Unknown")
                domain = meta.get("legal_domain", "")
                
                if meta.get("document_type") == "statute" or "Act" in src_name or "Sanhita" in src_name:
                    statutes_used += 1
                elif meta.get("document_type") == "judgment" or meta.get("court") == "Supreme Court" or "Supreme Court" in src_name:
                    sc_used += 1
                    
                citations.append({
                    "marker": f"[{marker_num}]",
                    "text_snippet": chunk.get("document", "")[:150] + "...",
                    "source_name": src_name,
                    "article_or_section": meta.get("section", meta.get("article", "Unknown")),
                    "legal_domain": domain,
                    "retrieval_method": meta.get("retrieval_method", "unknown"),
                    "similarity_score": meta.get("rrf_score", 0.0),
                    "retrieval_rank": meta.get("retrieval_rank", i + 1),
                    "chunk_used_by_llm": True,
                    "metadata": meta,
                    "full_relevant_text": chunk.get("document", "")
                })

        advanced_metadata = {
            "authorities_retrieved": auth_retrieved,
            "authorities_used": auth_used,
            "statutes_used": statutes_used,
            "sc_judgments_used": sc_used,
            "average_retrieval_score": round(avg_score, 4),
            "highest_retrieval_score": round(max_score, 4),
            "retrieval_time": retrieval_latency,
            "generation_time": model_processing_time,
            "corpus_coverage": "High" if auth_retrieved > 5 else "Low",
            "reasoning_confidence_score": rs_score
        }

        confidence_payload = {
            "level": r_conf_label if r_conf_label else "🟡 Moderate",
            "reason": r_conf_reason if r_conf_reason else "Derived from retrieved authorities."
        }

        return {
            "answer": raw_answer,
            "citations": citations,
            "confidence": confidence_payload,
            "advanced_metadata": advanced_metadata,
            "metrics": metrics
        }
    def trigger_pipeline_stream
'''

# Find trigger_pipeline and replace up to trigger_pipeline_stream
import re
new_code = re.sub(r'    def trigger_pipeline\(self.*?    def trigger_pipeline_stream', new_trigger_pipeline, code, flags=re.DOTALL)

with open('app/ai/orchestrator.py', 'w', encoding='utf-8') as f:
    f.write(new_code)
    
print("Rewrote trigger_pipeline successfully.")
