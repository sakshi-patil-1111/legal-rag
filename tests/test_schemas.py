import sys
import unittest
from pathlib import Path

project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root / "src"))

from legal_rag.schemas import LegalDocument, LegalQuery


class TestSchemas(unittest.TestCase):
    def test_query_roundtrip(self):
        q = LegalQuery(
            qid="q1",
            text="test query",
            task_type="statute_retrieval",
            ground_truth=["doc_1"],
        )
        d = q.to_dict()
        q2 = LegalQuery.from_dict(d)
        self.assertEqual(q.qid, q2.qid)
        self.assertEqual(q.ground_truth, q2.ground_truth)

    def test_document_roundtrip(self):
        doc = LegalDocument(
            doc_id="doc_1",
            doc_type="statute",
            title="Title",
            raw_text="some text",
        )
        d = doc.to_dict()
        doc2 = LegalDocument.from_dict(d)
        self.assertEqual(doc.doc_id, doc2.doc_id)
        self.assertEqual(doc.raw_text, doc2.raw_text)


if __name__ == "__main__":
    unittest.main()
