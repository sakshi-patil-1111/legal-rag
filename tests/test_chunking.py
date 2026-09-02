import sys
import unittest
from pathlib import Path

project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root / "src"))

from legal_rag.chunking import (
    FixedCharChunker,
    FixedTokenChunker,
    RecursiveChunker,
    WholeDocumentChunker,
)
from legal_rag.corpus import load_fixture


class TestChunking(unittest.TestCase):
    def setUp(self):
        self.fixture = project_root / "data" / "fixtures" / "tiny_fixture.json"
        self.docs, _ = load_fixture(self.fixture)

    def test_whole_returns_one_per_doc(self):
        chunker = WholeDocumentChunker()
        chunks = chunker.chunk(self.docs)
        self.assertEqual(len(chunks), len(self.docs))
        self.assertEqual(chunks[0].chunk_id, self.docs[0].doc_id)
        self.assertEqual(chunks[0].parent_doc_id, self.docs[0].doc_id)

    def test_fixed_token_chunker(self):
        chunker = FixedTokenChunker(size=50, overlap=0)
        chunks = chunker.chunk(self.docs)
        self.assertGreaterEqual(len(chunks), len(self.docs))
        for c in chunks:
            self.assertTrue(c.chunk_id.startswith(c.parent_doc_id))

    def test_fixed_char_chunker(self):
        chunker = FixedCharChunker(size=200, overlap=0)
        chunks = chunker.chunk(self.docs)
        self.assertGreaterEqual(len(chunks), len(self.docs))
        self.assertLessEqual(len(chunks[0].text), 200 + 10)

    def test_recursive_chunker(self):
        chunker = RecursiveChunker(size=50, overlap=0)
        chunks = chunker.chunk(self.docs)
        self.assertGreaterEqual(len(chunks), len(self.docs))


if __name__ == "__main__":
    unittest.main()
