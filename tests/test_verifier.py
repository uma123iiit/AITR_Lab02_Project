"""Sanity tests for scifact_verif.verifier. Run: python -m unittest discover -s tests -v"""
import sys
import unittest
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from scifact_verif import verifier as V  # noqa: E402

TRAIN_X = ["aspirin lowers risk", "aspirin raises risk", "drug unrelated outcome",
           "statin lowers cholesterol", "statin raises liver enzymes", "vitamin unrelated study"] * 5
TRAIN_Y = ["SUPPORT", "CONTRADICT", "NOT_ENOUGH_INFO"] * 10
EVAL_X = ["aspirin lowers risk zzdevonly", "statin raises risk"]


class Inputs(unittest.TestCase):
    def test_condition_a_is_claim_only(self):
        self.assertEqual(V.make_input("A", "claim text", "evidence ignored"), "claim text")

    def test_b_and_c_use_the_same_fixed_template(self):
        for cond in ("B", "C"):
            self.assertEqual(V.make_input(cond, "c", "e"), "CLAIM: c\nEVIDENCE: e")

    def test_empty_evidence_allowed_none_rejected(self):
        self.assertEqual(V.make_input("B", "c", ""), "CLAIM: c\nEVIDENCE: ")
        with self.assertRaises(ValueError):
            V.make_input("B", "c", None)

    def test_unknown_condition(self):
        with self.assertRaises(ValueError):
            V.make_input("D", "c", "e")

    def test_hash_deterministic(self):
        self.assertEqual(V.input_hash("abc"), V.input_hash("abc"))
        self.assertNotEqual(V.input_hash("abc"), V.input_hash("abd"))

    def test_config_id_stable_and_sensitive(self):
        self.assertEqual(V.LRConfig().config_id(), V.LRConfig().config_id())
        self.assertNotEqual(V.LRConfig().config_id(), V.LRConfig(class_weight="balanced").config_id())


class FitPredict(unittest.TestCase):
    def setUp(self):
        self.vec, self.clf, self.info = V.fit(TRAIN_X, TRAIN_Y, V.LRConfig())

    def test_shapes_and_probabilities(self):
        classes, proba, pred, seconds = V.predict(self.vec, self.clf, EVAL_X)
        self.assertEqual(classes, ["CONTRADICT", "NOT_ENOUGH_INFO", "SUPPORT"])   # sorted, as in sklearn
        self.assertEqual(proba.shape, (2, 3))
        self.assertLess(abs(proba.sum(axis=1) - 1).max(), 1e-9)
        self.assertEqual(pred, [classes[i] for i in proba.argmax(axis=1)])
        self.assertGreaterEqual(seconds, 0)

    def test_no_eval_text_in_vocabulary(self):
        self.assertNotIn("zzdevonly", self.vec.vocabulary_)

    def test_deterministic_refit(self):
        _, clf2, _ = V.fit(TRAIN_X, TRAIN_Y, V.LRConfig())
        self.assertTrue(np.array_equal(self.clf.coef_, clf2.coef_))

    def test_convergence_flag_reports_failure(self):
        rng = np.random.RandomState(0)
        words = [f"w{i}" for i in range(300)]
        x = [" ".join(rng.choice(words, 12)) for _ in range(200)]
        y = [["SUPPORT", "CONTRADICT", "NOT_ENOUGH_INFO"][i % 3] for i in range(200)]
        _, _, info = V.fit(x, y, V.LRConfig(max_iter=1))
        self.assertFalse(info["converged"])
        self.assertTrue(self.info["converged"])


if __name__ == "__main__":
    unittest.main()