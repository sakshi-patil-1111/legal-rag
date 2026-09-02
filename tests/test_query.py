import sys
import unittest
from pathlib import Path

project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root / "src"))

from legal_rag.query import (
    DirectQueryStrategy,
    HyDEQueryStrategy,
    KeywordExpansionQueryStrategy,
)


class TestQueryStrategies(unittest.TestCase):
    def test_direct(self):
        s = DirectQueryStrategy()
        t = s.transform("test query")
        self.assertEqual(t.original, t.transformed)
        self.assertEqual(t.strategy, "direct")

    def test_keyword_expansion(self):
        s = KeywordExpansionQueryStrategy()
        t = s.transform("dishonestly induces delivery")
        self.assertIn("fraudulently", t.transformed)
        self.assertEqual(t.strategy, "keyword_expansion")

    def test_hyde(self):
        s = HyDEQueryStrategy()
        t = s.transform("test query")
        self.assertIn("test query", t.hypothetical_document)
        self.assertIn(t.hypothetical_document, t.transformed)
        self.assertEqual(t.strategy, "hyde")


if __name__ == "__main__":
    unittest.main()
