import sys
import unittest
from pathlib import Path

project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root / "src"))

from legal_rag.metrics import evaluate_query, mrr, recall_at_k


class TestMetrics(unittest.TestCase):
    def test_recall_at_k(self):
        preds = [("a", 1.0), ("b", 0.5), ("c", 0.1)]
        gt = ["a", "c"]
        self.assertEqual(recall_at_k(preds, gt, 1), 0.5)
        self.assertEqual(recall_at_k(preds, gt, 3), 1.0)

    def test_mrr(self):
        preds = [("x", 1.0), ("a", 0.9), ("b", 0.8)]
        self.assertEqual(mrr(preds, ["a"]), 0.5)

    def test_evaluate_query(self):
        preds = [("a", 1.0), ("b", 0.5)]
        gt = ["a"]
        metrics = evaluate_query(preds, gt, ks=(1, 3))
        self.assertEqual(metrics["recall@1"], 1.0)
        self.assertEqual(metrics["mrr"], 1.0)


if __name__ == "__main__":
    unittest.main()
