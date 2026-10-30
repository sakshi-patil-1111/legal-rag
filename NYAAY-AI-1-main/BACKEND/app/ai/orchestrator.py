from app.knowledge.hybrid_retriever import hybrid_retriever
from app.knowledge.embeddings import embedding_service
from app.core.config import settings
from app.core.key_rotator import key_rotator
import re
import time
from typing import Dict, Any, List
from app.knowledge.metadata_utils import get_canonical_source_name
from app.core.logger import logger
import concurrent.futures
from google import genai
from google.genai import types

from app.ai.guardrails import guardrails
from app.ai.prompt_builder import prompt_builder
from app.core.metrics import global_metrics
from app.ai.validator import calculate_retrieval_confidence, validate_response, extract_reasoning_confidence


def thinking_config(level: str = "minimal"):
    """Low-latency ThinkingConfig for the Gemini 3 flash models we use.

    Thinking is on by default and dominated end-to-end latency (~7s on the
    analysis call) while also eating the max_output_tokens budget, which
    truncated the structured-analysis JSON.

    Only `thinking_level` works here: `thinking_budget=0` and
    `thinking_level="none"` are both rejected with HTTP 400 by
    gemini-3.6-flash and gemini-flash-lite-latest. Supported low settings are
    "minimal" and "low". Returns None if the installed SDK predates
    `thinking_level`, so callers fall back to the model default rather than
    raising.
    """
    try:
        return types.ThinkingConfig(thinking_level=level)
    except Exception:
        return None


# Analysis prompt, shared by the cached (no-history) and uncached paths.
ANALYSIS_SYS_PROMPT = """You are a legal case strategist. Analyze the user's query and decompose it into a structured CASE_OBJECT.
Return ONLY this JSON:
{
  "case_summary": "A clear, plain-language summary of the dispute.",
  "legal_issues": ["Specific legal question 1", "Specific legal question 2"],
  "material_facts": ["Fact 1", "Fact 2"],
  "missing_facts": ["What critical information is missing? (e.g., State, Date of notice)"],
  "sub_queries": ["Search query for issue 1", "Search query for issue 2"],
  "domains": {"Domain Name": 0.9},
  "explicit_sc_requested": true|false
}
Rules:
- sub_queries: 1-5 concise retrieval strings optimized for a vector database.
- domains: only Indian legal domains; confidence float (e.g. 0.9).
- explicit_sc_requested: true only if user explicitly mentions SC/precedent/case law.
Output ONLY the JSON. No explanation."""

# Free-tier quota is enforced per-project-per-model. gemini-3.6-flash allows
# only ~20 requests/day, so it is the FALLBACK here, not the primary: analysis
# is a short structured extraction that flash-lite handles just as well and
# measurably faster, and this keeps one exhausted model from adding seconds of
# 429 round-trips to every request. Flash models only — never a pro model.
ANALYSIS_MODELS = ("gemini-flash-lite-latest", "gemini-3.6-flash")

# A model whose daily quota is exhausted stays exhausted for hours, so remember
# it instead of paying for the 429 on every subsequent request.
_MODEL_COOLDOWN: Dict[str, float] = {}
_MODEL_COOLDOWN_SECONDS = 900


def _available_models(models) -> List[str]:
    """Models not currently known to be quota-exhausted (all of them if every
    candidate is cooling down, so we still attempt rather than hard-fail)."""
    now = time.time()
    live = [m for m in models if _MODEL_COOLDOWN.get(m, 0) <= now]
    return live or list(models)


class RAGOrchestrator:
    def __init__(self):
        # Base client for quick tasks, but we'll use rotator for heavy gen
        self.client = genai.Client(api_key=key_rotator.get())
        
    def _analyze_and_expand_query(self, question: str, history: List[Dict[str, Any]]) -> str:
        sys_prompt = """You are a legal query analyzer. Extract the core legal issue from the user's query and expand it into a comprehensive search query for a legal vector database.
Include relevant legal concepts, synonyms, and possible statutory frameworks (e.g., if it's about garbage collection, include solid waste management, municipal sanitation duties, public health, administrative inaction, nuisance, etc.).
DO NOT just repeat the user's text. Extract the true legal problem.
Output ONLY the expanded search query, nothing else."""
        
        history_text = "Conversation History:\\n"
        if history:
            for msg in history[-4:]:
                text_content = msg.get('content') or (msg.get('parts', [{}])[0].get('text', ''))
                history_text += f"{msg['role']}: {text_content}\\n"
        else:
            history_text = "No history."
            
        user_prompt = f"{history_text}\\nUser Query: {question}\\nExpanded Legal Search Query:"
        
        try:
            temp_client = genai.Client(api_key=key_rotator.get())
            import time
            for attempt in range(3):
                try:
                    res = temp_client.models.generate_content(
                        model='gemini-3.6-flash',
                        contents=user_prompt,
                        config=types.GenerateContentConfig(
                            system_instruction=sys_prompt,
                            thinking_config=thinking_config(getattr(settings, "ANALYSIS_THINKING_LEVEL", "minimal"))
                        )
                    )
                    break
                except Exception as e:
                    if "503" in str(e) and attempt < 2:
                        time.sleep(2)
                        continue
                    raise e
            expanded = res.text.strip()
            logger.info(f"Query expanded: '{question}' -> '{expanded}'")
            return expanded
        except Exception as e:
            logger.warning(f"Query expansion failed: {e}")
            return question


    def _estimate_complexity(self, question: str) -> bool:
        q = question.lower()
        has_sc_request = bool(re.search(r'\b(supreme court|sc judgment|precedent|case law|held)\b', q))
        has_multi_domain = bool(re.search(r'\b(rera|consumer|constitutional|fundamental right|natural justice)\b', q)) and bool(re.search(r'\b(compensation|refund|criminal|arrest|bail)\b', q))
        word_count = len(question.split())
        is_very_long = word_count > 100
        signals = sum([has_sc_request, has_multi_domain, is_very_long])
        return signals >= 1

    import functools

    @functools.lru_cache(maxsize=128)
    def _analyze_query_cached(self, question: str) -> str:
        """Cached wrapper. Deliberately lets failures propagate: lru_cache does
        not memoize exceptions, so a transient quota error won't poison the
        cache with an empty analysis for the rest of the process lifetime."""
        return self._run_analysis_llm(question)

    def _run_analysis_llm(self, question: str) -> str:
        """Structured-analysis call with key rotation and model fallback.

        Free-tier quota is enforced per-project-per-MODEL (gemini-3.6-flash
        allows only 20 requests/day), so a 429 means "try another key, then the
        next model" — not "give up". Previously any 429 returned "{}", which
        silently collapsed the multi-query fan-out to a single query and tripped
        the answer quality gate. Raises if every model/key is exhausted.
        """
        import time
        user_prompt = f"User Query: {question}\nJSON Output:"
        analysis_config = types.GenerateContentConfig(
            system_instruction=ANALYSIS_SYS_PROMPT,
            response_mime_type="application/json",
            max_output_tokens=800,
        )
        _tc = thinking_config(getattr(settings, "ANALYSIS_THINKING_LEVEL", "minimal"))
        if _tc is not None:
            analysis_config.thinking_config = _tc

        last_err = None
        for model in _available_models(ANALYSIS_MODELS):
            quota_exhausted = False
            # Try a few distinct keys per model before falling back to the next.
            for _ in range(max(1, min(3, key_rotator.count))):
                key = key_rotator.get()
                try:
                    # Keep a strong reference to the client: if it is only
                    # reachable through `.models`, CPython can collect it
                    # mid-call and close the underlying transport
                    # ("Cannot send a request, as the client has been closed").
                    client = genai.Client(api_key=key)
                    res = client.models.generate_content(
                        model=model,
                        contents=user_prompt,
                        config=analysis_config,
                    )
                    return (res.text or "").strip()
                except Exception as e:
                    last_err = e
                    err = str(e)
                    # Per-model daily cap: rotate to the next key, then the next
                    # model. Do NOT retire the key — it may still have quota on
                    # the other model (and for generation).
                    if "429" in err or "RESOURCE_EXHAUSTED" in err:
                        quota_exhausted = True
                        continue
                    if "503" in err:
                        time.sleep(1)
                        continue
                    break  # non-retryable for this model; try the next model
            if quota_exhausted:
                _MODEL_COOLDOWN[model] = time.time() + _MODEL_COOLDOWN_SECONDS
                logger.warning(f"Analysis model {model} quota-exhausted across keys; cooling down.")
        raise last_err if last_err else RuntimeError("Structured analysis failed")

    def _analyze_query_structured(self, question: str, history: List[Dict[str, Any]]) -> Dict[str, Any]:
        import json
        text = "{}"
        try:
            # History bypasses the cache (the analysis is per-question); the
            # prompt itself is identical in both cases.
            if not history:
                text = self._analyze_query_cached(question.strip().lower())
            else:
                text = self._run_analysis_llm(question)
        except Exception as e:
            logger.warning(f"Structured analysis failed: {e}")

        try:
            # Clean up markdown JSON block if present
            text = text.replace("```json", "").replace("```", "").strip()
            parsed = json.loads(text)
            if not isinstance(parsed, dict) or not parsed:
                raise ValueError("empty analysis object")
            return parsed
        except Exception as e:
            logger.warning(f"Structured analysis unusable, falling back to raw question: {e}")
            return {"case_summary": question, "legal_issues": [], "material_facts": [], "missing_facts": [], "sub_queries": [question], "domains": {}, "explicit_sc_requested": False}

    def _multi_query_retrieve(self, sub_queries: List[str], base_query_embedding: List[float], predicted_domains: Dict[str, float], doc_type_priority: str, filters: Dict[str, Any], explicit_sc_requested: bool, seed_chunks: List[Dict[str, Any]] = None, primary_query: str = None) -> List[Dict[str, Any]]:
        """Fan out over sub-queries but rerank the deduplicated union ONCE.

        Candidate generation (dense + BM25 + RRF) is cheap (~0.08s); the
        cross-encoder rerank is ~0.1s/pair on CPU and dominates latency. The
        old design reranked each sub-query's pool (and each SC pool) separately
        — 3-6 reranks of ~30 candidates = 90-180 pairs = 9-19s. Here we gather
        cheap fused candidates from every sub-query (+SC), dedupe, then rerank
        at most RERANK_MERGED_POOL of them a single time against the user's
        question. `seed_chunks` are already-reranked chunks (e.g. the streaming
        provisional search) that are merged in without re-reranking.
        """
        from app.core.config import settings
        sub_queries = sub_queries[:getattr(settings, 'MAX_SUB_QUERIES', 3)]
        seed_chunks = seed_chunks or []
        if not sub_queries:
            return seed_chunks
        primary_query = primary_query or sub_queries[0]
        n_sub = len(sub_queries)

        # Batch-embed sub-queries (BGE query prefix, matches embed_query).
        prefix = "Represent this sentence for searching relevant passages: "
        try:
            embeddings = embedding_service.embed_texts([prefix + sq for sq in sub_queries])
        except Exception:
            embeddings = [base_query_embedding] * n_sub

        per_pool = getattr(settings, "RERANK_CANDIDATE_POOL", 30)

        # 1. Gather CHEAP fused candidates (no rerank) from every sub-query.
        fused_lists = []  # list of (sub_idx, [candidates ordered by rrf])
        for i, sq in enumerate(sub_queries):
            try:
                cands = hybrid_retriever._fuse_candidates(
                    sq, embeddings[i], per_pool, where=filters,
                    predicted_domains=predicted_domains,
                    document_type_priority=doc_type_priority,
                )
                fused_lists.append((i, cands))
            except Exception as e:
                logger.warning(f"Candidate fusion failed for sub-query {i}: {e}")

        if explicit_sc_requested and hasattr(hybrid_retriever, "_fuse_sc_candidates"):
            for i, sq in enumerate(sub_queries):
                try:
                    sc_cands = hybrid_retriever._fuse_sc_candidates(
                        sq, embeddings[i], per_pool, predicted_domains)
                    fused_lists.append((i, sc_cands))
                except Exception as e:
                    logger.warning(f"SC candidate fusion failed for sub-query {i}: {e}")

        # 2. Dedupe by id; union the sub-issue tags; keep the highest RRF entry.
        seed_ids = {s["id"] for s in seed_chunks}
        cand_map = {}
        for sub_idx, cands in fused_lists:
            for c in cands:
                cid = c["id"]
                if cid in seed_ids:
                    continue  # already reranked in seed_chunks
                if cid not in cand_map:
                    c["metadata"]["sub_issue_ids"] = {sub_idx}
                    cand_map[cid] = c
                else:
                    cand_map[cid]["metadata"]["sub_issue_ids"].add(sub_idx)
                    if c["metadata"].get("rrf_score", 0) > cand_map[cid]["metadata"].get("rrf_score", 0):
                        merged_issues = cand_map[cid]["metadata"]["sub_issue_ids"]
                        c["metadata"]["sub_issue_ids"] = merged_issues
                        cand_map[cid] = c

        unique_candidates = sorted(
            cand_map.values(),
            key=lambda x: x["metadata"].get("rrf_score", 0), reverse=True)

        # 3. Round-robin select the rerank pool so every sub-issue is represented
        #    even if one sub-query's RRF scores dominate. The working set target is
        #    RERANK_MERGED_POOL; seed_chunks are ALREADY reranked, so we only need
        #    to rerank enough NEW candidates to top the set up — this is what makes
        #    reusing the streaming provisional rerank an actual latency saving.
        by_issue = {i: [] for i in range(n_sub)}
        for c in unique_candidates:
            for si in c["metadata"]["sub_issue_ids"]:
                if si in by_issue:
                    by_issue[si].append(c)

        merged_cap = max(0, getattr(settings, "RERANK_MERGED_POOL", 32) - len(seed_chunks))
        pool, pool_ids = [], set()
        cursors = {i: 0 for i in range(n_sub)}
        progressed = True
        while len(pool) < merged_cap and progressed:
            progressed = False
            for i in range(n_sub):
                lst = by_issue[i]
                while cursors[i] < len(lst):
                    c = lst[cursors[i]]
                    cursors[i] += 1
                    if c["id"] not in pool_ids:
                        pool.append(c)
                        pool_ids.add(c["id"])
                        progressed = True
                        break
                if len(pool) >= merged_cap:
                    break

        # 4. Rerank the whole pool ONCE against the user's question.
        if pool:
            from app.knowledge.reranker import reranker_service
            pool = reranker_service.rerank(primary_query, pool, top_k=len(pool))
            for r in pool:
                r["metadata"]["rrf_score"] = r["metadata"].get("final_score", r["metadata"].get("rrf_score", 0.0))

        # 5. Merge with already-reranked seed chunks (all now carry final_score).
        for s in seed_chunks:
            s["metadata"].setdefault("sub_issue_ids", {0})
        unique_results = pool + list(seed_chunks)

        # Normalize sub_issue_ids to lists for downstream/JSON safety.
        for r in unique_results:
            ids = r["metadata"].get("sub_issue_ids", {0})
            r["metadata"]["sub_issue_ids"] = list(ids) if isinstance(ids, (set, list)) else [0]

        unique_results.sort(key=lambda x: x.get("metadata", {}).get("final_score", 0), reverse=True)

        # 6. Fair allocation: guarantee minimum coverage per sub-issue, then fill
        #    remaining slots with the highest overall final_score.
        final_selected = []
        selected_ids = set()
        target_total = 20
        per_issue_target = max(1, target_total // n_sub)
        issue_counts = {i: 0 for i in range(n_sub)}

        for i in range(n_sub):
            for r in unique_results:
                if r["id"] not in selected_ids and i in r["metadata"]["sub_issue_ids"]:
                    if issue_counts[i] < per_issue_target:
                        final_selected.append(r)
                        selected_ids.add(r["id"])
                        issue_counts[i] += 1

        for r in unique_results:
            if len(final_selected) >= target_total:
                break
            if r["id"] not in selected_ids:
                final_selected.append(r)
                selected_ids.add(r["id"])

        return final_selected

    def _filter_relevant_chunks(self, question: str, chunks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        if not chunks:
            return chunks
            
        sys_prompt = """You are a Legal Relevance Evaluator for a RAG system.
Evaluate each retrieved legal document chunk against the user's query.

A chunk is PRIMARY_GOVERNING if it directly governs the core legal issue.
A chunk is SUPPORTING if it provides useful background law or establishes procedural rules that are actually applicable to the specific domain.
A chunk is IRRELEVANT if it is disconnected from the legal principles at hand OR if it is a procedural rule from an entirely unrelated domain (e.g., retrieving the Arms Act for a general "natural justice" query).

CRITICAL INSTRUCTION: Do NOT retain a chunk as SUPPORTING merely because it shares a procedural term (like 'opportunity of being heard') if the statute itself (e.g. THOT Act, Arms Act) has nothing to do with the user's facts. Err on the side of IRRELEVANT for unrelated statutes.

Respond with a valid JSON array of objects, where each object has 'id' (the chunk index provided), 'classification' (one of the 3 labels), and 'reasoning' (a brief explanation)."""

        from app.knowledge.metadata_utils import get_canonical_source_name
        user_prompt = f"User's Legal Query: {question}\\n\\n"
        for i, chunk in enumerate(chunks):
            meta = chunk.get("metadata", {})
            src = get_canonical_source_name(meta)
            user_prompt += f"--- Chunk ID: {i} | Source: {src} ---\\n{chunk['document'][:800]}\\n\\n"
            
        try:
            temp_client = genai.Client(api_key=key_rotator.get())
            import time
            for attempt in range(3):
                try:
                    res = temp_client.models.generate_content(
                        model='gemini-3.6-flash',
                        contents=user_prompt,
                        config=types.GenerateContentConfig(
                            system_instruction=sys_prompt,
                            response_mime_type="application/json",
                            thinking_config=thinking_config(getattr(settings, "ANALYSIS_THINKING_LEVEL", "minimal"))
                        )
                    )
                    break
                except Exception as e:
                    if "503" in str(e) and attempt < 2:
                        time.sleep(2)
                        continue
                    raise e
            import json
            classifications = json.loads(res.text)
            
            valid_indices = set()
            for item in classifications:
                if item.get("classification") in ["PRIMARY_GOVERNING", "SUPPORTING"]:
                    valid_indices.add(item.get("id"))
                    
            filtered_chunks = [chunks[i] for i in range(len(chunks)) if i in valid_indices]
            logger.info(f"Filtered chunks from {len(chunks)} down to {len(filtered_chunks)}")
            return filtered_chunks
        except Exception as e:
            logger.warning(f"Relevance filtering failed: {e}")
            return chunks
    def trigger_pipeline(self, question: str, filters: Dict[str, Any] = None, history: List[Dict[str, Any]] = None, task_type: str = "QA", language: str = "en") -> Dict[str, Any]:
        """
        Executes the full RAG pipeline for a given question.
        Returns a dict matching the KanoonResponse schema.
        """
        import time
        overall_start = time.time()
        
        # 1. Input Guardrails
        if not guardrails.validate_input(question):
            return self._fallback_response("Your question violates safety or length policies.")

        is_complex = True if task_type == "CIVIC" else self._estimate_complexity(question)
        query_analysis = {}
        
        if is_complex:
            query_analysis = self._analyze_query_structured(question, history)
            search_query = query_analysis.get("sub_queries", [question])[0]
            predicted_domains = query_analysis.get("domains", {})
            
            # Failsafe Domain Prediction
            if not predicted_domains:
                from app.ai.domain_classifier import domain_classifier
                logger.info("Structured domains empty. Falling back to domain_classifier.")
                domain_preds = domain_classifier.predict_domain(search_query)
                predicted_domains = domain_preds.get("domains", {})
                
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
                    (query_analysis.get("sub_queries") or [question]),
                    query_embedding,
                    predicted_domains,
                    doc_type_priority,
                    filters,
                    explicit_sc,
                    primary_query=question,
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
        retrieval_latency = round(time.time() - retrieval_start, 2)
        
        # Calculate Retrieval Confidence (Python Scoring)
        r_conf_score, r_conf_label, r_conf_reason, avg_score, max_score = calculate_retrieval_confidence(chunks, query_analysis if is_complex else None)

        # 4. Prompt Construction
        pc_start = time.time()
        system_instruction, user_prompt = prompt_builder.construct_prompt(question, chunks, history, task_type=task_type, query_analysis=query_analysis if is_complex else None, language=language)
        pc_latency = round(time.time() - pc_start, 2)
        
        gen_start = time.time()

        # 5. Generation (Single LLM Call)
        response_mime_type = "application/json" if task_type == "REASONING" else None
        raw_answer, retry_sleep_time = self._generate_with_fallback(system_instruction, user_prompt, response_mime_type)
        
        # 6. Deterministic Validation & Repair
        if raw_answer:
            is_valid, validated_answer = validate_response(raw_answer)
            if not is_valid:
                logger.warning(f"Validation failed: {validated_answer}. Regenerating once.")
                # Single Regeneration
                raw_answer, retry_sleep_time2 = self._generate_with_fallback(system_instruction, user_prompt, response_mime_type)
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
            "total_latency": total_latency
        }
        
        if not raw_answer:
            global_metrics.record_failure("llm_failures")
            return self._fallback_response("Failed to generate an answer. The AI service may be overloaded.")

        # 7. Extract Reasoning Confidence & Append Metadata
        rs_score, rs_label = extract_reasoning_confidence(raw_answer)
        
        # Extract all numbers from inside brackets (e.g. [4], [4, 7])
        used_citations = set()
        for bracket_content in re.findall(r'\[([^\]]+)\]', raw_answer):
            used_citations.update(re.findall(r'\d+', bracket_content))
            
        auth_retrieved = len(chunks)
        auth_used = len(used_citations)
        
        statutes_used = 0
        sc_used = 0
        
        citations = []
        for i, chunk in enumerate(chunks):
            marker_num = str(i + 1)
            if marker_num in used_citations:
                from app.knowledge.metadata_utils import get_canonical_source_name
                meta = chunk.get("metadata", {})
                src_name = get_canonical_source_name(meta)
                domain = meta.get("legal_domain", "")
                
                if meta.get("document_type") == "statute" or "Act" in src_name or "Sanhita" in src_name:
                    statutes_used += 1
                elif meta.get("document_type") == "judgment" or meta.get("court") == "Supreme Court" or "Supreme Court" in src_name:
                    sc_used += 1
                    
                citations.append({
                    "marker": f"[{marker_num}]",
                    "text_snippet": chunk["document"][:150] + "...",
                    "source_name": src_name,
                    "article_or_section": meta.get("section", meta.get("article", "Unknown")),
                    "legal_domain": domain,
                    "retrieval_method": meta.get("retrieval_method", "unknown"),
                    "similarity_score": meta.get("rrf_score", 0.0),
                    "retrieval_rank": meta.get("retrieval_rank", i + 1),
                    "chunk_used_by_llm": True,
                    "metadata": meta,
                    "full_relevant_text": chunk["document"]
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

    def trigger_pipeline_stream(self, question: str, filters: Dict[str, Any] = None, history: List[Dict[str, Any]] = None, task_type: str = "QA", language: str = "en"):
        import time
        import re
        import random
        from app.knowledge.metadata_utils import get_canonical_source_name
        import asyncio
        import json
        from app.core.config import settings
        
        overall_start = time.time()
        
        yield f"data: {json.dumps({'type': 'status', 'data': 'Analyzing intent...'})}\n\n"
        
        if not guardrails.validate_input(question):
            yield f"data: {json.dumps({'type': 'error', 'data': 'Your question violates safety or length policies.'})}\n\n"
            return

        is_complex = True if task_type == "CIVIC" else self._estimate_complexity(question)
        query_analysis = {}
        
        if is_complex:
            import concurrent.futures
            
            def provisional_search_task():
                q_emb = embedding_service.embed_query(question)
                # Cheap seed only: a small rerank pool keeps this fully hidden
                # behind the concurrent analysis LLM call. The multi-query pass
                # reranks the merged union afterwards.
                return q_emb, hybrid_retriever.search(
                    question, q_emb,
                    n_results=getattr(settings, "PROVISIONAL_N_RESULTS", 10),
                    where=filters,
                    predicted_domains={},
                    candidate_pool=getattr(settings, "PROVISIONAL_CANDIDATE_POOL", 14),
                )
                
            yield f"data: {json.dumps({'type': 'status', 'data': 'Analyzing intent and searching corpus...'})}\n\n"
            emb_start = time.time()
            
            with concurrent.futures.ThreadPoolExecutor(max_workers=2) as ex:
                llm_future = ex.submit(self._analyze_query_structured, question, history)
                search_future = ex.submit(provisional_search_task)
                
                query_analysis = llm_future.result()
                try:
                    query_embedding, prov_chunks = search_future.result()
                except Exception:
                    yield f"data: {json.dumps({'type': 'error', 'data': 'Internal error while processing your question.'})}\n\n"
                    return
                    
            emb_latency = round(time.time() - emb_start, 2)
            predicted_domains = query_analysis.get("domains", {})
            doc_type_priority = "any"
            explicit_sc = query_analysis.get("explicit_sc_requested", False)
            
            try:
                # Use provisional chunks if no subqueries, otherwise run multi-query
                sub_queries = query_analysis.get("sub_queries") or [question]
                # The provisional search already reranked the raw question under
                # the SAME `filters` used below, so its chunks are safe to reuse
                # as seeds and to return directly on the fast path — no chunk can
                # cross a tenant/where boundary. (Previously it ran with
                # where=None and the fast path returned those unfiltered chunks.)
                seed = prov_chunks
                retrieval_start = time.time()
                if len(sub_queries) <= 1 and not explicit_sc and not predicted_domains:
                    chunks = prov_chunks
                else:
                    chunks = self._multi_query_retrieve(
                        sub_queries,
                        query_embedding,
                        predicted_domains,
                        doc_type_priority,
                        filters,
                        explicit_sc,
                        seed_chunks=seed,
                        primary_query=question,
                    )
            except Exception as e:
                yield f"data: {json.dumps({'type': 'error', 'data': 'Failed to retrieve context.'})}\n\n"
                return
                
        else:
            search_query = self._analyze_and_expand_query(question, history)
            
            yield f"data: {json.dumps({'type': 'status', 'data': 'Searching legal corpus...'})}\n\n"
            emb_start = time.time()
            try:
                query_embedding = embedding_service.embed_query(search_query)
            except:
                yield f"data: {json.dumps({'type': 'error', 'data': 'Internal error while processing your question.'})}\n\n"
                return
            emb_latency = round(time.time() - emb_start, 2)
            
            if not query_embedding:
                yield f"data: {json.dumps({'type': 'error', 'data': 'Failed to process question text.'})}\n\n"
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
                yield f"data: {json.dumps({'type': 'error', 'data': 'Failed to retrieve context.'})}\n\n"
                return
        retrieval_latency = round(time.time() - retrieval_start, 2)
        
        # EXTRACT DETERMINISTIC METADATA EARLY
        extracted_authorities = set()
        extracted_docs = set()
        for c in chunks[:3]:
            m = c.get("metadata", {})
            if "authority" in m:
                extracted_authorities.add(m["authority"])
            if "document_type" in m:
                extracted_docs.add(m["document_type"])
                
        # Emit metadata early
        metadata_payload = {
            "authorities": list(extracted_authorities) if extracted_authorities else ["Refer to cited procedure"],
            "documents": list(extracted_docs)
        }
        yield f"data: {json.dumps({'type': 'metadata', 'data': metadata_payload})}\n\n"

        pc_start = time.time()
        system_instruction, user_prompt = prompt_builder.construct_prompt(question, chunks, history, task_type=task_type, query_analysis=query_analysis if is_complex else None, language=language)
        pc_latency = round(time.time() - pc_start, 2)
        
        yield f"data: {json.dumps({'type': 'status', 'data': 'Generating response...'})}\n\n"

        gen_start = time.time()
        full_text = ""
        ttft = None
        
        try:
            model_name = getattr(settings, "CIVIC_MODEL", "gemini-flash-lite-latest")
            current_key = key_rotator.get()
            config = types.GenerateContentConfig(
                system_instruction=system_instruction,
                max_output_tokens=8192,
            )
            _tc = thinking_config(getattr(settings, "GEN_THINKING_LEVEL", "low"))
            if _tc is not None:
                config.thinking_config = _tc

            import threading
            import queue
            
            q = queue.Queue()
            
            def run_gen():
                try:
                    temp_client = genai.Client(api_key=current_key)
                    response_stream = temp_client.models.generate_content_stream(
                        model=model_name,
                        contents=user_prompt,
                        config=config,
                    )
                    for chunk in response_stream:
                        q.put(("chunk", chunk.text))
                    q.put(("done", None))
                except Exception as e:
                    q.put(("error", e))
                    
            t = threading.Thread(target=run_gen)
            t.start()
            
            deadline = time.time() + 25
            while True:
                time_left = deadline - time.time()
                if time_left <= 0:
                    err_json = json.dumps({'type': 'error', 'data': '\n\n[Generation timed out to meet 25s SLA]'})
                    yield f"data: {err_json}\n\n"
                    break
                    
                try:
                    msg_type, data = q.get(timeout=min(0.5, time_left))
                    if msg_type == "chunk":
                        if ttft is None:
                            ttft = time.time() - gen_start
                        if data:
                            full_text += data
                            if task_type != "CIVIC":
                                yield f"data: {json.dumps({'type': 'chunk', 'data': data})}\n\n"
                    elif msg_type == "done":
                        break
                    elif msg_type == "error":
                        error_str = str(data)
                        logger.warning(f"Streaming error: {error_str}")
                        if "GenerateRequestsPerDayPerProject" in error_str:
                            key_rotator.remove_key(current_key)
                        yield f"data: {json.dumps({'type': 'error', 'data': 'Generation interrupted due to quota limit.'})}\n\n"
                        break
                except queue.Empty:
                    continue
                    
        except Exception as e:
            logger.error(f"Streaming failed: {e}")
            yield f"data: {json.dumps({'type': 'error', 'data': 'Generation failed.'})}\n\n"

        gen_total_latency = time.time() - gen_start
        total_latency = round(time.time() - overall_start, 2)
        
        metrics = {
            "embedding_time": emb_latency,
            "retrieval_time": retrieval_latency,
            "prompt_construction_time": pc_latency,
            "ttft": round(ttft, 2) if ttft else 0,
            "model_processing_time": round(gen_total_latency, 2),
            "output_tokens": len(full_text) // 4,
            "total_latency": total_latency
        }
        
        # Extract all numbers from inside brackets (e.g. [4], [4, 7])
        used_citations = set()
        for bracket_content in re.findall(r'\[([^\]]+)\]', full_text):
            used_citations.update(re.findall(r'\d+', bracket_content))
        
        citations = []
        for i, chunk in enumerate(chunks):
            marker_num = str(i + 1)
            if marker_num in used_citations or not used_citations:
                meta = chunk.get("metadata", {})
                citations.append({
                    "marker": f"[{marker_num}]",
                    "text_snippet": chunk["document"][:150] + "...",
                    "source_name": get_canonical_source_name(meta),
                    "article_or_section": meta.get("section", meta.get("article", "Unknown")),
                    "legal_domain": meta.get("legal_domain", ""),
                    "metadata": meta,
                    "full_relevant_text": chunk["document"]
                })

        if task_type == "CIVIC":
            clean = full_text.strip()
            if clean.startswith('```json'): clean = clean[7:]
            elif clean.startswith('```'): clean = clean[3:]
            if clean.endswith('```'): clean = clean[:-3]
            clean = clean.strip()
            
            try:
                j = json.loads(clean)
                # False Success Detection
                empty_count = 0
                total_fields = 0
                
                # Check problemAndRights
                pr = j.get('problemAndRights', {})
                for k, v in pr.items():
                    total_fields += 1
                    if not v or "Not established" in str(v):
                        empty_count += 1
                        
                # Check authority
                ra = j.get('relevantAuthority', {})
                for k, v in ra.items():
                    total_fields += 1
                    if not v or "Not established" in str(v):
                        empty_count += 1
                        
                # If more than 60% of fields are "Not established" despite having user facts, reject it.
                if total_fields > 0 and (empty_count / total_fields) > 0.6:
                    logger.warning("Quality Gate Failed: High number of Not Established fields.")
                    yield f"data: {json.dumps({'type': 'error', 'data': 'SYNTHESIS_FAILURE: The system could not confidently establish the legal facts from the retrieved authority.'})}\n\n"
                    return
                else:
                    # Emit the whole validated JSON
                    yield f"data: {json.dumps({'type': 'chunk', 'data': clean})}\n\n"
            except Exception as e:
                logger.error(f"Failed to parse CIVIC JSON: {e}")
                yield f"data: {json.dumps({'type': 'error', 'data': 'SYNTHESIS_FAILURE: Failed to generate a structured case dossier.'})}\n\n"
                return

        yield f"data: {json.dumps({'type': 'complete', 'citations': citations, 'metrics': metrics})}\n\n"

    def _generate_with_fallback(self, system_instruction: str, user_prompt: str, response_mime_type: str = None) -> tuple[str, float]:
        import time
        from app.core.config import settings
        max_retries = 2
        total_sleep_time = 0.0
        
        model_name = getattr(settings, "CIVIC_MODEL", "gemini-flash-lite-latest")
        
        for attempt in range(max_retries):
            try:
                current_key = key_rotator.get()
                temp_client = genai.Client(api_key=current_key)
                config = types.GenerateContentConfig(
                    system_instruction=system_instruction,
                    max_output_tokens=8192,
                )
                if response_mime_type:
                    config.response_mime_type = response_mime_type
                _tc = thinking_config(getattr(settings, "GEN_THINKING_LEVEL", "low"))
                if _tc is not None:
                    config.thinking_config = _tc

                response = temp_client.models.generate_content(
                    model=model_name,
                    contents=user_prompt,
                    config=config,
                )
                return response.text.strip(), total_sleep_time
            except Exception as e:
                error_str = str(e)
                logger.warning(f"RAG Generation failed on attempt {attempt+1}: {error_str}")
                
                if "GenerateRequestsPerDayPerProject" in error_str:
                    logger.warning("Daily quota exhausted, dropping key.")
                    key_rotator.remove_key(current_key)
                    continue
                elif "429" in error_str or "RESOURCE_EXHAUSTED" in error_str:
                    sleep_time = 0.5
                    time.sleep(sleep_time)
                    total_sleep_time += sleep_time
                continue
                
        return None, total_sleep_time

    def _fallback_response(self, message: str) -> Dict[str, Any]:
        return {
            "answer": message,
            "citations": [],
            "confidence": {
                "level": "Insufficient",
                "reason": message,
            },
            "metrics": {}
        }

rag_orchestrator = RAGOrchestrator()

