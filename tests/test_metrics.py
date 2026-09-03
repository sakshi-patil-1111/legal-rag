import sys
import unittest
from pathlib import Path

project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root / "src"))

from legal_rag.metrics import (
    average_precision, evaluate_query, macro_f1_at_k, mrr, recall_at_k,
)


class TestMetrics(unittest.TestCase):
    def test_recall_at_k(self):
        preds = [("a", 1.0), ("b", 0.5), ("c", 0.1)]
        self.assertEqual(recall_at_k(preds, ["a", "c"], 1), 0.5)
        self.assertEqual(recall_at_k(preds, ["a", "c"], 3), 1.0)

    def test_mrr(self):
        self.assertEqual(mrr([("x", 1.0), ("a", 0.9)], ["a"]), 0.5)

    def test_macro_f1_at_k(self):
        preds = [("a", 1.0), ("b", 0.5), ("c", 0.1)]
        gt = ["a", "c"]
        # k=3: tp=2, prec=2/3, rec=2/2=1, f1=2*(2/3)*1/((2/3)+1)=4/5
        self.assertAlmostEqual(macro_f1_at_k(preds, gt, 3), 0.8, places=4)

    def test_average_precision(self):
        preds = [("a", 1.0), ("b", 0.5), ("c", 0.1)]
        gt = ["a", "c"]
        # AP = (1/1 + 2/3) / 2 = (1 + 0.6667) / 2 = 0.8333
        self.assertAlmostEqual(average_precision(preds, gt), 5 / 6, places=4)

    def test_evaluate_query(self):
        preds = [("a", 1.0), ("b", 0.5)]
        metrics = evaluate_query(preds, ["a"], ks=(1, 3))
        self.assertEqual(metrics["recall@1"], 1.0)
        self.assertEqual(metrics["mrr"], 1.0)
        self.assertIn("f1@1", metrics)
        self.assertIn("map", metrics)


if __name__ == "__main__":
    unittest.main()
