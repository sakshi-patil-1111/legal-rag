import sys
import unittest
from pathlib import Path

project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root / "src"))

from legal_rag.datasets import load_il_pcsr, load_legalbench_rag


class TestDatasets(unittest.TestCase):
    def test_il_pcsr_statute(self):
        root = project_root / "data" / "fixtures" / "il_pcsr"
        queries, docs = load_il_pcsr(root, split="test", task="statute")
        self.assertEqual(len(queries), 1)
        self.assertEqual(queries[0].qid, "ilpcsr_test_1")
        self.assertEqual(queries[0].ground_truth, ["ipc_s302"])
        self.assertEqual(len(docs), 3)

    def test_il_pcsr_precedent(self):
        root = project_root / "data" / "fixtures" / "il_pcsr"
        queries, docs = load_il_pcsr(root, split="dev", task="precedent")
        self.assertEqual(len(queries), 1)
        self.assertEqual(queries[0].ground_truth, ["case_ramesh"])

    def test_legalbench_rag(self):
        root = project_root / "data" / "fixtures" / "legalbench_rag"
        queries, docs = load_legalbench_rag(root, split="test")
        self.assertEqual(len(queries), 2)
        self.assertEqual(len(docs), 2)


if __name__ == "__main__":
    unittest.main()
