import sys
import unittest
from pathlib import Path

project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root / "src"))

from legal_rag.reranker import NoOpReranker, TokenOverlapReranker


class TestReranker(unittest.TestCase):
    def test_noop(self):
        r = NoOpReranker()
        candidates = [("a", 1.0), ("b", 0.5), ("c", 0.2)]
        out = r.rerank("query", candidates, {"a": "query text", "b": "other"}, 2)
        self.assertEqual(len(out), 2)
        self.assertEqual(out[0][0], "a")

    def test_token_overlap(self):
        r = TokenOverlapReranker()
        candidates = [("a", 1.0), ("b", 0.5)]
        texts = {"a": "the quick brown fox", "b": "the quick brown query"}
        out = r.rerank("quick query", candidates, texts, 2)
        self.assertEqual(out[0][0], "b")


if __name__ == "__main__":
    unittest.main()
