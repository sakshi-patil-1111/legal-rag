from collections.abc import Sequence


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


def mrr(
    predictions: Sequence[tuple[str, float]],
    ground_truth: Sequence[str],
) -> float:
    relevant = set(ground_truth)
    for rank, (doc_id, _) in enumerate(predictions, start=1):
        if doc_id in relevant:
            return 1.0 / rank
    return 0.0


def evaluate_query(
    predictions: Sequence[tuple[str, float]],
    ground_truth: Sequence[str],
    ks: tuple[int, ...] = (1, 3, 5, 10),
) -> dict[str, float]:
    return {
        f"recall@{k}": recall_at_k(predictions, ground_truth, k) for k in ks
    } | {"mrr": mrr(predictions, ground_truth)}
