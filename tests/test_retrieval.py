"""Tests for scifact_verif.retrieval and metrics.wilson_interval. Run: python -m unittest discover -s tests -v"""
import inspect
import sys
import unittest
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from scifact_verif import metrics, retrieval as R  # noqa: E402

DOC_IDS = [1, 2, 3, 4, 5]
TEXTS = ["alpha beta gamma", "delta epsilon", "zeta eta theta", "iota kappa", "lambda mu"]


class Text(unittest.TestCase):
    def test_tokenize_keeps_negation_and_numbers(self):
        self.assertEqual(R.tokenize("No effect of IL-6 on 40 patients"),
                         ["no", "effect", "of", "il", "6", "on", "40", "patients"])

    def test_doc_text_order(self):
        self.assertEqual(R.doc_text({"title": "T", "abstract": ["S1.", "S2."]}), "T S1. S2.")


class Ranking(unittest.TestCase):
    def test_ties_break_by_ascending_doc_id(self):
        top = R.rank_top_k(np.array([1.0, 1.0, 0.5, 1.0]), np.array([30, 10, 20, 5]), k=3)
        self.assertEqual([d for d, _ in top], [5, 10, 30])

    def test_score_beats_doc_id(self):
        top = R.rank_top_k(np.array([0.1, 0.9]), np.array([1, 99]), k=2)
        self.assertEqual([d for d, _ in top], [99, 1])


class Retrievers(unittest.TestCase):
    def check(self, retriever):
        retriever.fit(DOC_IDS, TEXTS)
        top = retriever.search("gamma", k=4)
        self.assertEqual([d for d, _ in top], [1, 2, 3, 4])       # match first, zero-score ties by id
        self.assertGreater(top[0][1], 0)
        self.assertEqual([s for _, s in top[1:]], [0.0, 0.0, 0.0])
        self.assertEqual(top, retriever.search("gamma", k=4))      # deterministic
        self.assertTrue(all(isinstance(d, int) for d, _ in top))

    def test_bm25(self):
        self.check(R.BM25Retriever())

    def test_tfidf(self):
        self.check(R.TfidfRetriever())

    def test_tfidf_identical_text_is_cosine_one(self):
        r = R.TfidfRetriever()
        r.fit(DOC_IDS, TEXTS)
        doc, score = r.search("alpha beta gamma", k=1)[0]
        self.assertEqual(doc, 1)
        self.assertAlmostEqual(score, 1.0, places=6)

    def test_search_takes_only_the_query(self):
        for cls in (R.BM25Retriever, R.TfidfRetriever):
            self.assertEqual(list(inspect.signature(cls.search).parameters), ["self", "query", "k"])

    def test_module_does_not_import_gold_evidence_code(self):
        src = Path(R.__file__).read_text()
        self.assertNotIn("scifact_verif.data", src)
        self.assertNotIn("from . import data", src)


class Wilson(unittest.TestCase):
    def test_known_values(self):
        lo, hi = metrics.wilson_interval(5, 10)
        self.assertAlmostEqual(lo, 0.2366, places=3)
        self.assertAlmostEqual(hi, 0.7634, places=3)
        lo, hi = metrics.wilson_interval(0, 10)
        self.assertEqual(lo, 0.0)
        self.assertAlmostEqual(hi, 0.2775, places=3)

    def test_empty(self):
        self.assertEqual(metrics.wilson_interval(0, 0), (0.0, 0.0))


if __name__ == "__main__":
    unittest.main()