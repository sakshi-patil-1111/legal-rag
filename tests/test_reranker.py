import sys
import unittest
from pathlib import Path

project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root / "src"))

from legal_rag.reranker import LLMReranker, NoOpReranker, TokenOverlapReranker


class _StubLLM:
    def __init__(self, text: str):
        self._text = text

    def generate(self, prompt, system="", temperature=0.0, max_tokens=256, **_):
        from legal_rag.llm import LLMResponse

        return LLMResponse(
            text=self._text, latency_seconds=0.0, tokens_in=10, tokens_out=5,
        )


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

    def test_llm_rerank_reorders(self):
        r = LLMReranker.__new__(LLMReranker)
        r.pool_size = 3
        r.query_chars = 4000
        r.doc_chars = 1000
        r.max_retries = 1
        r.reasoning_effort = None
        r.calls = r.tokens_in = r.tokens_out = r.failures = 0
        r._llm = _StubLLM("[3, 1, 2]")
        candidates = [("a", 1.0), ("b", 0.5), ("c", 0.2), ("d", 0.1)]
        texts = {k: f"text {k}" for k in "abcd"}
        out = r.rerank("q", candidates, texts, 3)
        self.assertEqual([d for d, _ in out], ["c", "a", "b"])

    def test_llm_rerank_fallback_on_bad_json(self):
        r = LLMReranker.__new__(LLMReranker)
        r.pool_size = 3
        r.query_chars = 4000
        r.doc_chars = 1000
        r.max_retries = 1
        r.reasoning_effort = None
        r.calls = r.tokens_in = r.tokens_out = r.failures = 0
        r._llm = _StubLLM("not json at all")
        candidates = [("a", 1.0), ("b", 0.5), ("c", 0.2)]
        texts = {k: f"text {k}" for k in "abc"}
        out = r.rerank("q", candidates, texts, 2)
        self.assertEqual([d for d, _ in out], ["a", "b"])
        self.assertEqual(r.failures, 1)


if __name__ == "__main__":
    unittest.main()
