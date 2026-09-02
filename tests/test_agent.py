import sys
import unittest
from pathlib import Path

project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root / "src"))

from legal_rag.agent import ConstrainedAgent
from legal_rag.chunking import WholeDocumentChunker
from legal_rag.corpus import load_fixture
from legal_rag.retrievers import BM25Retriever


class TestAgent(unittest.TestCase):
    def setUp(self):
        self.fixture = project_root / "data" / "fixtures" / "tiny_fixture.json"
        self.docs, _ = load_fixture(self.fixture)
        chunker = WholeDocumentChunker()
        chunks = chunker.chunk(self.docs)
        retriever = BM25Retriever()
        retriever.index(chunks)
        self.agent = ConstrainedAgent(retriever, max_rounds=2)

    def test_agent_runs_and_logs_rounds(self):
        evidence, trace = self.agent.run("dishonestly induces delivery of money", top_k=3)
        self.assertTrue(len(evidence) > 0)
        self.assertEqual(len(trace.rounds), 2)
        self.assertTrue(trace.stop_reason)


if __name__ == "__main__":
    unittest.main()
