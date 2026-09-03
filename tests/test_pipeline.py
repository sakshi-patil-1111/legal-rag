import sys
import unittest
from pathlib import Path

project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root / "src"))

from legal_rag.corpus import load_fixture
from legal_rag.metrics import evaluate_query
from legal_rag.retrievers import BM25Retriever


class TestPipeline(unittest.TestCase):
    def setUp(self):
        self.fixture = project_root / "data" / "fixtures" / "tiny_fixture.json"

    def test_load_fixture(self):
        docs, queries = load_fixture(self.fixture)
        self.assertEqual(len(docs), 4)
        self.assertEqual(len(queries), 3)

    def test_bm25_retrieves_relevant(self):
        docs, queries = load_fixture(self.fixture)
        retriever = BM25Retriever()
        retriever.index(docs)
        for query in queries:
            predictions = retriever.search(query.text, top_k=10)
            metrics = evaluate_query(predictions, query.ground_truth, ks=(1, 5))
            self.assertGreaterEqual(metrics["mrr"], 0.5)


if __name__ == "__main__":
    unittest.main()
