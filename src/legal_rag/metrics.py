import math
from collections.abc import Sequence
from typing import Any


def recall_at_k(
    predictions: Sequence[tuple[str, float]],
    ground_truth: Sequence[str],
    k: int,
) -> float:
    relevant = set(ground_truth)
    if not relevant:
        return 0.0
    retrieved = {p[0] for p in predictions[:k]}
    return len(retrieved & relevant) / len(relevant)


def precision_at_k(
    predictions: Sequence[tuple[str, float]],
    ground_truth: Sequence[str],
    k: int,
) -> float:
    relevant = set(ground_truth)
    if not relevant:
        return 0.0
    retrieved = [p[0] for p in predictions[:k]]
    if not retrieved:
        return 0.0
    return sum(1 for doc_id in retrieved if doc_id in relevant) / len(retrieved)


def mrr(
    predictions: Sequence[tuple[str, float]],
    ground_truth: Sequence[str],
) -> float:
    relevant = set(ground_truth)
    for rank, (doc_id, _) in enumerate(predictions, start=1):
        if doc_id in relevant:
            return 1.0 / rank
    return 0.0


def ndcg_at_k(
    predictions: Sequence[tuple[str, float]],
    ground_truth: Sequence[str],
    k: int,
) -> float:
    """Normalized Discounted Cumulative Gain at k (binary relevance)."""
    relevant = set(ground_truth)
    if not relevant:
        return 0.0
    dcg = 0.0
    for i, (doc_id, _) in enumerate(predictions[:k], start=1):
        if doc_id in relevant:
            dcg += 1.0 / math.log2(i + 1)
    ideal_hits = min(len(relevant), k)
    idcg = sum(1.0 / math.log2(i + 1) for i in range(1, ideal_hits + 1))
    return dcg / idcg if idcg > 0 else 0.0


def evaluate_query(
    predictions: Sequence[tuple[str, float]],
    ground_truth: Sequence[str],
    ks: tuple[int, ...] = (1, 3, 5, 10),
) -> dict[str, float]:
    metrics: dict[str, float] = {}
    for k in ks:
        metrics[f"recall@{k}"] = recall_at_k(predictions, ground_truth, k)
        metrics[f"precision@{k}"] = precision_at_k(predictions, ground_truth, k)
        metrics[f"ndcg@{k}"] = ndcg_at_k(predictions, ground_truth, k)
    metrics["mrr"] = mrr(predictions, ground_truth)
    return metrics


# ---------------------------------------------------------------------------
# Snippet-level metrics (for LegalBench-RAG)
# ---------------------------------------------------------------------------

def _spans_overlap(a_start: int, a_end: int, b_start: int, b_end: int) -> bool:
    return a_start < b_end and b_start < a_end


def _chunk_span(chunk: Any) -> tuple[int, int]:
    """Extract (char_start, char_end) from a LegalChunk's chunking_metadata."""
    meta = getattr(chunk, "chunking_metadata", {})
    start = meta.get("char_start", 0)
    end = meta.get("char_end", len(getattr(chunk, "text", "")))
    return start, end


def snippet_recall_at_k(
    predictions: Sequence[tuple[str, float]],
    snippets: Sequence[dict],
    chunk_map: dict[str, Any],
    k: int,
) -> float:
    """Fraction of ground-truth snippets covered by top-k retrieved chunks.

    A snippet is covered if some retrieved chunk belongs to the same file
    and its character span overlaps the snippet's span.
    """
    if not snippets:
        return 0.0
    retrieved = [chunk_map.get(cid) for cid, _ in predictions[:k] if cid in chunk_map]
    covered = 0
    for snip in snippets:
        fp = snip["file_path"]
        s_start, s_end = snip["span"]
        for chunk in retrieved:
            if chunk.parent_doc_id == fp:
                c_start, c_end = _chunk_span(chunk)
                if _spans_overlap(c_start, c_end, s_start, s_end):
                    covered += 1
                    break
    return covered / len(snippets)


def snippet_precision_at_k(
    predictions: Sequence[tuple[str, float]],
    snippets: Sequence[dict],
    chunk_map: dict[str, Any],
    k: int,
) -> float:
    """Fraction of top-k retrieved chunks that overlap a ground-truth snippet."""
    retrieved = [chunk_map.get(cid) for cid, _ in predictions[:k] if cid in chunk_map]
    if not retrieved:
        return 0.0
    relevant = 0
    for chunk in retrieved:
        c_start, c_end = _chunk_span(chunk)
        for snip in snippets:
            if chunk.parent_doc_id == snip["file_path"]:
                s_start, s_end = snip["span"]
                if _spans_overlap(c_start, c_end, s_start, s_end):
                    relevant += 1
                    break
    return relevant / len(retrieved)


def evaluate_query_snippet(
    predictions: Sequence[tuple[str, float]],
    snippets: Sequence[dict],
    chunk_map: dict[str, Any],
    ks: tuple[int, ...] = (1, 3, 5, 10),
) -> dict[str, float]:
    """Compute snippet-level recall@k and precision@k."""
    metrics: dict[str, float] = {}
    for k in ks:
        metrics[f"snippet_recall@{k}"] = snippet_recall_at_k(predictions, snippets, chunk_map, k)
        metrics[f"snippet_precision@{k}"] = snippet_precision_at_k(predictions, snippets, chunk_map, k)
    return metrics
