import logging
from typing import List, Dict, Any, Optional
import numpy as np

from app.knowledge.vector_store import vector_store
from app.knowledge.bm25_manager import bm25_manager

logger = logging.getLogger(__name__)

from app.core.config import settings

class HybridRetriever:
    def __init__(self):
        pass # removed unused _bm25_cache and _corpus_cache per out-of-scope cleanup

    def _fuse_candidates(self, query: str, query_embedding: List[float], candidate_pool: int, where: Optional[Dict[str, Any]] = None, predicted_domains: Dict[str, float] = None, document_type_priority: str = "any", domain_multiplier_weight: float = 0.10) -> List[Dict[str, Any]]:
        """Dense + BM25 + RRF fusion WITHOUT the cross-encoder rerank.

        Returns up to `candidate_pool` candidates ordered by RRF, each with
        `retrieval_method`, `rrf_rank`, and `rrf_score` populated. This is the
        cheap part of retrieval (~0.08s); the expensive cross-encoder rerank
        (~0.1s/pair on CPU) is applied separately so a multi-query fan-out can
        gather candidates from every sub-query and rerank the union ONCE.
        """
        # 1. Dense Retrieval (ChromaDB)
        initial_k = 20
        dense_results = vector_store.search(query_embedding, n_results=initial_k, where=where, search_sc=True)
        
        # 2. Fetch corpus and BM25 index from Manager
        tenant_id = "global"
        if where:
            if "tenant_id" in where:
                tenant_id = where["tenant_id"]
            elif "$and" in where:
                for cond in where["$and"]:
                    if "tenant_id" in cond:
                        tenant_id = cond["tenant_id"]
                        break

        bm25, corpus_ids, corpus_docs, corpus_metadatas, id_to_index = bm25_manager.get_index(tenant_id)

        if not bm25 or not corpus_docs:
            return dense_results[:candidate_pool]

        tokenized_query = bm25_manager.tokenize_text(query)
        
        # Get BM25 scores
        bm25_scores = bm25.get_scores(tokenized_query)
        
        # 3. Reciprocal Rank Fusion (RRF) with Metadata Bonus
        rrf_scores = {}
        predicted_domains = predicted_domains or {}
        
        # Helper to calculate metadata multiplier
        def calculate_metadata_multiplier(metadata: Dict[str, Any]) -> float:
            multiplier = 1.0
            
            # Domain Match Bonus (Proportional to LLM confidence)
            chunk_domain = metadata.get("legal_domain", "")
            if chunk_domain in predicted_domains:
                multiplier += domain_multiplier_weight * predicted_domains[chunk_domain]
                
            # Document Type Bonus
            chunk_type = metadata.get("document_type", "")
            if document_type_priority != "any" and chunk_type == document_type_priority:
                multiplier += 0.05
                    
            return multiplier
        
        # Rank Dense
        for rank, res in enumerate(dense_results):
            chunk_id = res["id"]
            base_rrf = (1.0 / (60 + rank))
            multiplier = calculate_metadata_multiplier(res["metadata"])
            rrf_scores[chunk_id] = rrf_scores.get(chunk_id, 0.0) + (base_rrf * multiplier)
            
        # Rank Sparse (Top 30 from BM25) - using partial sort (B3) and correct multiplier (A2)
        k_sparse = 30
        if len(bm25_scores) > k_sparse:
            top_idx = np.argpartition(bm25_scores, -k_sparse)[-k_sparse:]
            sparse_ranking = top_idx[np.argsort(bm25_scores[top_idx])[::-1]]
        else:
            sparse_ranking = np.argsort(bm25_scores)[::-1]

        for rank, idx in enumerate(sparse_ranking):
            idx = int(idx)
            chunk_id = corpus_ids[idx]
            base_rrf = 1.0 / (60 + rank)
            multiplier = calculate_metadata_multiplier(corpus_metadatas[idx])
            rrf_scores[chunk_id] = rrf_scores.get(chunk_id, 0.0) + (base_rrf * multiplier)
            
        # 4. Sort and apply Candidate Pool limit (A1)
        sorted_rrf = sorted(rrf_scores.items(), key=lambda item: item[1], reverse=True)
        top_ids = [cid for cid, _ in sorted_rrf[:candidate_pool]]
        
        # 5. Reconstruct the candidate list of dicts (O(K) lookups) (B7)
        dense_by_id = {r["id"]: r for r in dense_results}
        sparse_id_set = {corpus_ids[int(i)] for i in sparse_ranking}
        
        candidate_results = []
        for rank, cid in enumerate(top_ids):
            found_dense = dense_by_id.get(cid)
            is_sparse = cid in sparse_id_set
            
            retrieval_method = "hybrid" if (found_dense and is_sparse) else "dense" if found_dense else "sparse"
            
            if found_dense:
                found_dense["metadata"]["retrieval_method"] = retrieval_method
                found_dense["metadata"]["rrf_rank"] = rank + 1
                found_dense["metadata"]["rrf_score"] = rrf_scores[cid]
                candidate_results.append(found_dense)
            else:
                idx = id_to_index.get(cid)
                if idx is not None:
                    candidate_results.append({
                        "id": cid,
                        "document": corpus_docs[idx],
                        "metadata": {
                            **corpus_metadatas[idx],
                            "retrieval_method": retrieval_method,
                            "rrf_rank": rank + 1,
                            "rrf_score": rrf_scores[cid]
                        },
                        "distance": 0.0
                    })

        return candidate_results

    def search(self, query: str, query_embedding: List[float], n_results: int = 10, where: Optional[Dict[str, Any]] = None, predicted_domains: Dict[str, float] = None, document_type_priority: str = "any", domain_multiplier_weight: float = 0.10, candidate_pool: Optional[int] = None) -> List[Dict[str, Any]]:
        """Full single-query retrieval: fuse candidates then cross-encoder rerank.

        Kept for the sync pipeline and the streaming provisional search. The
        multi-query path calls `_fuse_candidates` directly and reranks the
        merged union once (see orchestrator._multi_query_retrieve).

        `candidate_pool` overrides RERANK_CANDIDATE_POOL. Callers that only need
        a cheap seed (the streaming provisional search) pass a smaller pool so
        the rerank cost stays hidden behind the concurrent analysis LLM call.
        """
        if candidate_pool is None:
            candidate_pool = getattr(settings, "RERANK_CANDIDATE_POOL", 30)
        candidate_results = self._fuse_candidates(
            query, query_embedding, candidate_pool, where=where,
            predicted_domains=predicted_domains,
            document_type_priority=document_type_priority,
            domain_multiplier_weight=domain_multiplier_weight,
        )

        # Cross-Encoder Reranking
        if candidate_results:
            from app.knowledge.reranker import reranker_service
            final_results = reranker_service.rerank(query, candidate_results, top_k=n_results)
            # A3/A4: Mirror final_score to rrf_score for downstream compat
            for r in final_results:
                r["metadata"]["rrf_score"] = r["metadata"].get("final_score", r["metadata"].get("rrf_score", 0.0))
        else:
            final_results = []

        return final_results


    def _fuse_sc_candidates(self, query: str, query_embedding: List[float], candidate_pool: int = 30, predicted_domains: Dict[str, float] = None) -> List[Dict[str, Any]]:
        """Supreme-Court-only dense + BM25 + RRF fusion WITHOUT rerank.

        Returns up to `candidate_pool` SC candidates ordered by RRF, each with
        `rrf_score` and `retrieval_method` populated.
        """
        initial_k = 30
        
        # 1. Build where clause for domain filtering
        where = None
        if predicted_domains:
            top_domain = max(predicted_domains.items(), key=lambda x: x[1])
            if top_domain[1] > 0.4:
                where = {"legal_domain": top_domain[0]}

        # 2. Dense search (search_sc=True pulls from SC collection via vector_store.py)
        dense_results = vector_store.search(query_embedding, n_results=initial_k, where=where, search_sc=True)
        dense_sc = [r for r in dense_results if 'SC_' in r['id'] or r['metadata'].get('court_level') == 'Supreme Court']
        
        # 3. BM25 Search
        bm25, corpus_ids, corpus_docs, corpus_metadatas, id_to_index = bm25_manager.get_index("global")
        bm25_sc = []
        if bm25 and corpus_docs:
            query_tokens = bm25_manager.tokenize_text(query)
            # Remove stopwords from query tokens so BM25 isn't dominated by generic terms
            stop_words = {"supreme", "court", "precedent", "judgment", "case", "law", "the", "a", "an", "is", "of", "and", "in", "to", "for", "with", "on", "by"}
            filtered_tokens = [t for t in query_tokens if t not in stop_words]
            if not filtered_tokens:
                filtered_tokens = query_tokens
                
            doc_scores = bm25.get_scores(filtered_tokens)
            # B3: use argpartition for SC as well
            k_sc = initial_k * 2
            if len(doc_scores) > k_sc:
                top_idx = np.argpartition(doc_scores, -k_sc)[-k_sc:]
                top_bm25_indices = top_idx[np.argsort(doc_scores[top_idx])[::-1]]
            else:
                top_bm25_indices = np.argsort(doc_scores)[::-1]
            
            for idx in top_bm25_indices:
                idx = int(idx)
                score = doc_scores[idx]
                if score <= 0: continue
                c_id = corpus_ids[idx]
                meta = corpus_metadatas[idx]
                # Filter by SC and Domain
                is_sc = 'SC_' in c_id or meta.get('court_level') == 'Supreme Court'
                if not is_sc: continue
                
                if where and "legal_domain" in where:
                    if meta.get("legal_domain") != where["legal_domain"]:
                        continue
                        
                bm25_sc.append({
                    "id": c_id,
                    "document": corpus_docs[idx],
                    "metadata": meta,
                    "bm25_score": score
                })
        
        # 4. RRF Merging
        merged = {}
        def add_to_rrf(results, score_field, method_name):
            for rank, res in enumerate(results):
                doc_id = res['id']
                if doc_id not in merged:
                    merged[doc_id] = {
                        "id": doc_id,
                        "document": res['document'],
                        "metadata": res['metadata'].copy(),
                        "rrf_score": 0.0,
                        "sources": []
                    }
                merged[doc_id]["rrf_score"] += 1.0 / (60 + rank + 1)
                merged[doc_id]["sources"].append(method_name)
                merged[doc_id]["metadata"]["retrieval_method"] = "+".join(merged[doc_id]["sources"])

        add_to_rrf(dense_sc, "distance", "dense")
        add_to_rrf(bm25_sc, "bm25_score", "bm25")

        candidate_results = sorted(list(merged.values()), key=lambda x: x["rrf_score"], reverse=True)
        # Mirror rrf_score/rrf_rank into metadata so SC candidates share the same
        # contract as _fuse_candidates: the multi-query merge sorts on
        # metadata["rrf_score"], and downstream consumers expect every chunk to
        # carry an rrf_rank.
        for rank, c in enumerate(candidate_results):
            c["metadata"]["rrf_score"] = c["rrf_score"]
            c["metadata"]["rrf_rank"] = rank + 1
        return candidate_results[:candidate_pool]

    def search_sc_only(self, query: str, query_embedding: List[float], n_results: int = 10, predicted_domains: Dict[str, float] = None) -> List[Dict[str, Any]]:
        """Full SC-only retrieval: fuse SC candidates then rerank."""
        candidate_pool = getattr(settings, "RERANK_CANDIDATE_POOL", 30)
        candidate_results = self._fuse_sc_candidates(query, query_embedding, candidate_pool, predicted_domains)

        # Rerank
        if candidate_results:
            from app.knowledge.reranker import reranker_service
            ranked_sc = reranker_service.rerank(query, candidate_results, top_k=n_results)
            for chunk in ranked_sc:
                # A3/A4: Mirror final_score to rrf_score to prevent truncation against real RRF scores
                chunk["metadata"]["rrf_score"] = chunk["metadata"].get("final_score", 0.0)
            return ranked_sc
        return []

hybrid_retriever = HybridRetriever()
