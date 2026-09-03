import sys
import unittest
from pathlib import Path

project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root / "src"))

from legal_rag.chunking import FixedTokenChunker, WholeDocumentChunker
from legal_rag.corpus import load_fixture
from legal_rag.retrievers import BM25Retriever, DenseRetriever, HybridRetriever


class TestRetrievers(unittest.TestCase):
    def setUp(self):
        self.fixture = project_root / "data" / "fixtures" / "tiny_fixture.json"
        self.docs, _ = load_fixture(self.fixture)

    def test_bm25_whole(self):
        chunker = WholeDocumentChunker()
        chunks = chunker.chunk(self.docs)
        retriever = BM25Retriever()
        retriever.index(chunks)
        results = retriever.search("cheats and thereby dishonestly induces the person deceived", top_k=3)
        self.assertEqual(results[0][0], "ipc_s420")

    def test_bm25_chunked(self):
        chunker = FixedTokenChunker(size=100, overlap=0)
        chunks = chunker.chunk(self.docs)
        retriever = BM25Retriever()
        retriever.index(chunks)
        results = retriever.search("cheats and thereby dishonestly induces the person deceived", top_k=3)
        self.assertEqual(results[0][0], "ipc_s420")

    def test_dense_retriever(self):
        chunker = WholeDocumentChunker()
        chunks = chunker.chunk(self.docs)
        retriever = DenseRetriever(cache_dir=None)
        retriever.index(chunks)
        results = retriever.search("dishonestly induces delivery of money", top_k=3)
        self.assertTrue(len(results) > 0)

    def test_hybrid_retriever(self):
        chunker = WholeDocumentChunker()
        chunks = chunker.chunk(self.docs)
        bm25 = BM25Retriever()
        dense = DenseRetriever(cache_dir=None)
        hybrid = HybridRetriever(bm25, dense)
        hybrid.index(chunks)
        results = hybrid.search("dishonestly induces delivery of money", top_k=3)
        self.assertTrue(len(results) > 0)


if __name__ == "__main__":
    unittest.main()
