"""Run: python -m unittest discover -s tests -v"""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from scifact_verif import sampling as S  # noqa: E402


class Allocate(unittest.TestCase):
    def test_equal_split_with_remainder(self):
        self.assertEqual(S.allocate({"A": 99, "B": 99, "C": 99}, 50), {"A": 17, "B": 17, "C": 16})

    def test_small_stratum_redistributes(self):
        self.assertEqual(S.allocate({"A": 99, "B": 5, "C": 99}, 50), {"A": 23, "B": 5, "C": 22})

    def test_take_all_when_fewer_than_total(self):
        self.assertEqual(S.allocate({"A": 10, "B": 5, "C": 20}, 50), {"A": 10, "B": 5, "C": 20})

    def test_never_exceeds_total_or_stratum(self):
        c = {"A": 3, "B": 40, "C": 12}
        t = S.allocate(c, 50)
        self.assertEqual(sum(t.values()), 50)
        self.assertTrue(all(t[k] <= c[k] for k in c))


class Draw(unittest.TestCase):
    def test_seeded_and_order_independent(self):
        ids = {"A": list(range(100)), "B": list(range(100, 200))}
        a = S.draw(ids, {"A": 5, "B": 5}, 42)
        b = S.draw({"B": ids["B"][::-1], "A": ids["A"][::-1]}, {"A": 5, "B": 5}, 42)
        self.assertEqual(a, b)
        self.assertEqual(len(set(a["A"])), 5)
        self.assertNotEqual(a, S.draw(ids, {"A": 5, "B": 5}, 43))


if __name__ == "__main__":
    unittest.main()