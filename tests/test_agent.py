import sys
import unittest
from pathlib import Path

project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root / "src"))

from legal_rag.agent import ConstrainedAgent
from legal_rag.chunking import WholeDocumentChunker
from legal_rag.corpus import load_fixture
from legal_rag.legal_agent import LegalAgent
from legal_rag.llm import LLMResponse
from legal_rag.retrievers import BM25Retriever


class StubLLM:
    """Deterministic LLM stand-in keyed by system prompt."""

    ROUTES = {
        "routing component": '{"statute": "cheats and thereby dishonestly induces the person deceived", "precedent": null}',
        "reflection component": '{"sufficient": true}',
        "synthesis component": (
            '{"issue": "cheating", "applicable_statutes": '
            '[{"id": "ipc_s420", "relevance": "defines cheating"}], '
            '"supporting_precedents": [{"id": "ghost_doc", "relevance": "x"}], '
            '"analysis": "s420 applies", "suggested_action": "file complaint"}'
        ),
    }

    def generate(self, prompt, system="", temperature=0.3, max_tokens=512):
        for key, text in self.ROUTES.items():
            if key in system:
                return LLMResponse(text=text, latency_seconds=0.0)
        return LLMResponse(text="{}", latency_seconds=0.0)


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

    def test_legal_agent_dossier(self):
        chunker = WholeDocumentChunker()
        chunks = chunker.chunk(self.docs)
        retriever = BM25Retriever()
        retriever.index(chunks)
        doc_texts = {"statute": {d.doc_id: d.raw_text for d in self.docs}}
        doc_titles = {"statute": {d.doc_id: d.title for d in self.docs}}
        agent = LegalAgent(
            retrievers={"statute": retriever},
            doc_texts=doc_texts,
            doc_titles=doc_titles,
            llm=StubLLM(),
        )
        result = agent.run("person cheats and dishonestly induces delivery of money")
        self.assertEqual(result.dossier["issue"], "cheating")
        self.assertTrue(any(s.step == "route" for s in result.trace))
        self.assertTrue(any(s.step == "synthesize" for s in result.trace))
        # ghost_doc was never retrieved -> citation must be dropped
        self.assertTrue(result.warnings)
        self.assertEqual(len(result.dossier["supporting_precedents"]), 0)
        # real citation survives validation
        self.assertEqual(result.dossier["applicable_statutes"][0]["id"], "ipc_s420")


if __name__ == "__main__":
    unittest.main()
