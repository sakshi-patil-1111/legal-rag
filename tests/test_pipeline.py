import sys
import unittest
from pathlib import Path

project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root / "src"))

from legal_rag.bm25 import SimpleBM25
from legal_rag.corpus import load_fixture
from legal_rag.experiment import run_bm25_experiment
from legal_rag.metrics import evaluate_query
from legal_rag.tokenization import tokenize


class TestPipeline(unittest.TestCase):
    def setUp(self):
        self.fixture = project_root / "data" / "fixtures" / "tiny_fixture.json"

    def test_load_fixture(self):
        docs, queries = load_fixture(self.fixture)
        self.assertEqual(len(docs), 4)
        self.assertEqual(len(queries), 3)

    def test_bm25_retrieves_relevant(self):
        docs, queries = load_fixture(self.fixture)
        index = SimpleBM25(docs, tokenize)
        for query in queries:
            predictions = index.retrieve(query.text, top_k=10)
            metrics = evaluate_query(predictions, query.ground_truth, ks=(1, 5))
            self.assertGreaterEqual(metrics["mrr"], 0.5)

    def test_experiment(self):
        results = run_bm25_experiment(self.fixture, top_k=10, ks=(1, 3, 5, 10))
        self.assertEqual(results["n_queries"], 3)
        self.assertIn("mrr", results["metrics"])
        self.assertGreaterEqual(results["metrics"]["mrr"], 0.5)


if __name__ == "__main__":
    unittest.main()
