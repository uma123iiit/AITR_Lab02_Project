"""Tests for scifact_verif.metrics, cross-checked against scikit-learn. Run: python -m unittest discover -s tests -v"""
import sys
import tempfile
import unittest
from pathlib import Path

import numpy as np
from sklearn.metrics import accuracy_score, confusion_matrix, f1_score, precision_recall_fscore_support

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from scifact_verif import metrics as M  # noqa: E402

K = 3


def synthetic(seed, n=200):
    rng = np.random.RandomState(seed)
    g = rng.randint(0, K, n)
    p = np.where(rng.rand(n) < 0.55, g, rng.randint(0, K, n))
    return g, p


class AgainstSklearn(unittest.TestCase):
    def test_confusion_orientation_and_values(self):
        g, p = synthetic(0)
        self.assertTrue(np.array_equal(M.confusion(g, p, K), confusion_matrix(g, p, labels=range(K))))

    def test_per_class_and_macro_all_labels(self):
        for seed in range(5):
            g, p = synthetic(seed)
            cm = M.confusion(g, p, K)
            pr, rc, f1, sup = M.per_class(cm)
            spr, src, sf1, ssup = precision_recall_fscore_support(g, p, labels=range(K), zero_division=0)
            for mine, theirs in [(pr, spr), (rc, src), (f1, sf1), (sup, ssup)]:
                self.assertTrue(np.allclose(mine, theirs))
            self.assertAlmostEqual(M.macro_f1(cm, range(K)),
                                   f1_score(g, p, labels=range(K), average="macro", zero_division=0))
            self.assertAlmostEqual(M.accuracy(cm), accuracy_score(g, p))

    def test_macro_over_label_subset_counts_other_predictions_as_errors(self):
        g, p = synthetic(3)
        mask = g != 1                       # slice with no gold class 1, predictions may still be 1
        cm = M.confusion(g[mask], p[mask], K)
        self.assertAlmostEqual(M.macro_f1(cm, [0, 2]),
                               f1_score(g[mask], p[mask], labels=[0, 2], average="macro", zero_division=0))

    def test_zero_division_policy(self):
        g, p = np.array([0, 0, 1]), np.array([0, 0, 0])      # class 2 absent everywhere, class 1 never predicted
        pr, rc, f1, sup = M.per_class(M.confusion(g, p, K))
        self.assertEqual((pr[1], rc[1], f1[1], pr[2], f1[2]), (0.0, 0.0, 0.0, 0.0, 0.0))


class Bootstrap(unittest.TestCase):
    def test_identical_conditions_give_zero_difference(self):
        g, p = synthetic(1)
        r = M.paired_bootstrap(g, p, p, K, range(K), n_resamples=200)
        self.assertEqual((r["difference"], r["ci95_low"], r["ci95_high"]), (0.0, 0.0, 0.0))
        self.assertFalse(r["ci_excludes_zero"])

    def test_better_condition_has_positive_interval(self):
        g, _ = synthetic(2, n=300)
        rng = np.random.RandomState(5)
        bad = rng.randint(0, K, len(g))
        r = M.paired_bootstrap(g, bad, g, K, range(K), n_resamples=300)       # b is perfect
        self.assertGreater(r["difference"], 0.3)
        self.assertTrue(r["ci_excludes_zero"])
        self.assertGreater(r["ci95_low"], 0)

    def test_seeded_and_resamples_claims_not_rows(self):
        g, a = synthetic(4)
        _, b = synthetic(9)
        r1 = M.paired_bootstrap(g, a, b, K, range(K), n_resamples=100, seed=42)
        r2 = M.paired_bootstrap(g, a, b, K, range(K), n_resamples=100, seed=42)
        self.assertEqual(r1, r2)
        self.assertEqual(r1["n_claims"], len(g))


class Loader(unittest.TestCase):
    HEADER = "claim_id,condition,gold_label,predicted_label,p_X,p_Y\n"

    def write(self, body):
        d = tempfile.mkdtemp()
        p = Path(d) / "predictions.csv"
        p.write_text(self.HEADER + body)
        return p

    def test_reads_consistent_file(self):
        rows, classes = M.read_predictions(self.write("1,A,X,X,0.7,0.3\n2,A,Y,Y,0.2,0.8\n"))
        self.assertEqual((len(rows), classes), (2, ["X", "Y"]))

    def test_rejects_label_that_disagrees_with_probabilities(self):
        with self.assertRaises(ValueError):
            M.read_predictions(self.write("1,A,X,Y,0.7,0.3\n"))

    def test_rejects_probabilities_not_summing_to_one(self):
        with self.assertRaises(ValueError):
            M.read_predictions(self.write("1,A,X,X,0.7,0.1\n"))


if __name__ == "__main__":
    unittest.main()