import sys
from pathlib import Path
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from scifact_verif.rq3_metadata import deterministic_rq3_code


class TestRQ3MetadataCodes(unittest.TestCase):
    def test_b_empty_evidence(self):
        category, note, status = deterministic_rq3_code({"condition":"B", "gold_evidence_doc_ids":"", "evidence_empty":1})
        self.assertEqual(category, "NO_EVIDENCE_SEEN")
        self.assertEqual(status, "DETERMINISTIC_METADATA_RULE")

    def test_c_nei_no_gold_document_uses_pc006(self):
        category, note, status = deterministic_rq3_code({"condition":"C", "gold_evidence_doc_ids":"", "evidence_empty":0, "bm25_hit_at_5":""})
        self.assertEqual(category, "NO_EVIDENCE_SEEN")
        self.assertIn("non-gold documents", note)

    def test_c_gold_document_missed_is_retrieval_miss(self):
        category, _, _ = deterministic_rq3_code({"condition":"C", "gold_evidence_doc_ids":"123", "evidence_empty":0, "bm25_hit_at_5":0})
        self.assertEqual(category, "RETRIEVAL_MISS")

    def test_c_hit_requires_text_review(self):
        category, _, status = deterministic_rq3_code({"condition":"C", "gold_evidence_doc_ids":"123", "evidence_empty":0, "bm25_hit_at_5":1})
        self.assertEqual(category, "")
        self.assertEqual(status, "PENDING_TEXT_REVIEW")

    def test_a_not_evidence_seen(self):
        category, _, status = deterministic_rq3_code({"condition":"A", "gold_evidence_doc_ids":"123", "evidence_empty":0})
        self.assertEqual(category, "")
        self.assertEqual(status, "PENDING_TEXT_REVIEW")


if __name__ == "__main__":
    unittest.main()