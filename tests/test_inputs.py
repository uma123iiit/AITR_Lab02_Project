"""Tests for scifact_verif.inputs. Run: python -m unittest discover -s tests -v"""
import inspect
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from scifact_verif import inputs as I  # noqa: E402

CORPUS = {"1": {"doc_id": 1, "title": "T1", "abstract": ["A1.", "A2."]},
          "2": {"doc_id": 2, "title": "T2", "abstract": ["B1."]}}


class GoldText(unittest.TestCase):
    def test_sorted_by_numeric_doc_id_and_separated(self):
        items = [{"doc_id": "10", "text": "ten"}, {"doc_id": "9", "text": "nine"}]
        self.assertEqual(I.gold_evidence_text(items), "nine | ten")   # numeric, not string, order

    def test_no_evidence_is_empty_string(self):
        self.assertEqual(I.gold_evidence_text([]), "")


class RetrievedText(unittest.TestCase):
    def test_rank_order_title_then_abstract(self):
        self.assertEqual(I.retrieved_evidence_text([2, 1], CORPUS), "T2 B1. | T1 A1. A2.")

    def test_builder_takes_no_gold_argument(self):
        self.assertEqual(list(inspect.signature(I.retrieved_evidence_text).parameters), ["doc_ids", "corpus"])

    def test_module_does_not_import_evidence_code(self):
        src = Path(I.__file__).read_text()
        self.assertNotIn("scifact_verif.data", src)
        self.assertNotIn("from scifact_verif import data", src)


if __name__ == "__main__":
    unittest.main()