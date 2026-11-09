"""Unit tests for scifact_verif.data using a tiny synthetic corpus. Run: python -m unittest discover -s tests -v"""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from scifact_verif import data as D  # noqa: E402

S0, S1, S2 = "Drug A lowers blood pressure.", "It was tested in 40 adults.", "Effects lasted six weeks."
CORPUS = {  # keys are str, as load_corpus produces; the raw files hold int doc_id
    "1": {"doc_id": 1, "title": "T1", "abstract": [S0, S1, S2]},
    "2": {"doc_id": 2, "title": "T2", "abstract": ["Drug B had no effect.", "Sample was small."]},
}


def ev(doc, sentences, label):
    return {doc: [{"sentences": sentences, "label": label}]}


CLAIMS = [
    {"id": 1, "claim": "Drug A lowers blood pressure.", "evidence": ev("1", [0, 2], "SUPPORT"), "cited_doc_ids": [1]},
    {"id": 2, "claim": "Drug B works.", "evidence": ev("2", [0], "CONTRADICT"), "cited_doc_ids": [2]},
    {"id": 3, "claim": "Drug C cures flu.", "evidence": {}, "cited_doc_ids": [1]},
    {"id": 4, "claim": "Mixed claim.", "evidence": {**ev("1", [0], "SUPPORT"), **ev("2", [0], "CONTRADICT")}},
    {"id": 5, "claim": "Missing doc.", "evidence": ev("99", [0], "SUPPORT")},
    {"id": 6, "claim": "Bad index.", "evidence": ev("1", [7], "SUPPORT")},
    {"id": 7, "claim": "No evidence field at all."},
    {"id": 8, "claim": "Dup one.", "evidence": ev("1", [0], "SUPPORT")},
    {"id": 8, "claim": "Dup two.", "evidence": ev("1", [1], "SUPPORT")},
]


class DeriveLabel(unittest.TestCase):
    def test_cases(self):
        lab = {c["id"]: D.derive_gold_label(c) for c in CLAIMS[:7]}
        self.assertEqual(lab[1], ("SUPPORT", []))
        self.assertEqual(lab[2], ("CONTRADICT", []))
        self.assertEqual(lab[3], ("NOT_ENOUGH_INFO", []))
        self.assertEqual(lab[4], (None, [D.MIXED]))
        self.assertEqual(lab[7], (None, [D.UNLABELED]))

    def test_unknown_label(self):
        self.assertEqual(D.derive_gold_label({"id": 0, "claim": "x", "evidence": ev("1", [0], "MAYBE")}),
                         (None, [D.UNKNOWN_LABEL]))


class GoldEvidence(unittest.TestCase):
    def test_text_and_str_ids(self):
        items, reasons = D.gold_evidence(CLAIMS[0], CORPUS)
        self.assertEqual(reasons, [])
        self.assertEqual(items, [{"doc_id": "1", "sentence_indices": [0, 2], "n_rationale_sets": 1,
                                  "text": f"{S0} {S2}"}])

    def test_missing_doc_and_bad_index(self):
        self.assertEqual(D.gold_evidence(CLAIMS[4], CORPUS), ([], [D.DOC_MISSING]))
        self.assertEqual(D.gold_evidence(CLAIMS[5], CORPUS), ([], [D.BAD_INDEX]))


class RationaleSets(unittest.TestCase):
    TWO = {"id": 20, "claim": "x", "evidence": {"1": [{"sentences": [2], "label": "SUPPORT"},
                                                      {"sentences": [0, 1], "label": "SUPPORT"}]}}

    def test_first_uses_only_the_first_set_in_file_order(self):
        items, reasons = D.gold_evidence(self.TWO, CORPUS)           # default is the frozen "first"
        self.assertEqual((reasons, items[0]["sentence_indices"], items[0]["n_rationale_sets"]), ([], [2], 2))
        self.assertEqual(items[0]["text"], S2)

    def test_union_uses_every_set(self):
        items, _ = D.gold_evidence(self.TWO, CORPUS, rationale="union")
        self.assertEqual(items[0]["sentence_indices"], [0, 1, 2])
        self.assertEqual(items[0]["text"], f"{S0} {S1} {S2}")

    def test_bad_index_in_a_later_set_is_still_flagged(self):
        c = {"id": 21, "claim": "x", "evidence": {"1": [{"sentences": [0], "label": "SUPPORT"},
                                                        {"sentences": [9], "label": "SUPPORT"}]}}
        for policy in ("first", "union"):
            self.assertEqual(D.gold_evidence(c, CORPUS, rationale=policy), ([], [D.BAD_INDEX]))

    def test_unknown_policy_rejected(self):
        with self.assertRaises(ValueError):
            D.gold_evidence(self.TWO, CORPUS, rationale="all")

    def test_gold_document_ids_do_not_depend_on_policy(self):
        ids = lambda p: [i["doc_id"] for i in D.gold_evidence(self.TWO, CORPUS, rationale=p)[0]]
        self.assertEqual(ids("first"), ids("union"))


class MatchedSet(unittest.TestCase):
    def reasons(self, excluded):
        return {e["claim_id"]: e["reason_codes"] for e in excluded}

    def test_all_labeled(self):
        matched, excluded = D.build_matched_set(CLAIMS, CORPUS, "all_labeled")
        self.assertEqual([m["claim_id"] for m in matched], [1, 2, 3])
        self.assertTrue(next(m for m in matched if m["claim_id"] == 3)["b_evidence_empty"])
        r = self.reasons(excluded)
        self.assertEqual(r[4], D.MIXED)
        self.assertEqual(r[5], D.DOC_MISSING)
        self.assertEqual(r[6], D.BAD_INDEX)
        self.assertEqual(r[7], D.UNLABELED)
        self.assertEqual(r[8], D.DUPLICATE_ID)   # both copies of id 8 excluded -> one row keyed by id

    def test_evidence_only_drops_nei(self):
        matched, excluded = D.build_matched_set(CLAIMS, CORPUS, "evidence_only")
        self.assertEqual([m["claim_id"] for m in matched], [1, 2])
        self.assertEqual(self.reasons(excluded)[3], D.NEI_POLICY)

    def test_no_silent_drops(self):
        for p in D.POLICIES:
            matched, excluded = D.build_matched_set(CLAIMS, CORPUS, p)
            self.assertEqual(len(matched) + len(excluded), len(CLAIMS))

    def test_holdout_near_duplicates(self):
        matched, excluded = D.build_matched_set(CLAIMS, CORPUS, "all_labeled", holdout_ids={1, 3})
        self.assertEqual([m["claim_id"] for m in matched], [2])
        r = self.reasons(excluded)
        self.assertEqual(r[1], D.NEAR_DUP)
        self.assertEqual(r[3], D.NEAR_DUP)
        self.assertEqual(len(matched) + len(excluded), len(CLAIMS))

    def test_holdout_combines_with_other_reasons(self):
        _, excluded = D.build_matched_set(CLAIMS, CORPUS, "evidence_only", holdout_ids={3})
        self.assertEqual(self.reasons(excluded)[3], f"{D.NEI_POLICY}|{D.NEAR_DUP}")

    def test_bad_policy(self):
        with self.assertRaises(ValueError):
            D.build_matched_set(CLAIMS, CORPUS, "whatever")

    def test_rq2_denominator_excludes_empty_gold(self):
        matched, _ = D.build_matched_set(CLAIMS, CORPUS, "all_labeled")
        self.assertEqual(D.rq2_eligible_ids(matched), [1, 2])


class TwinIds(unittest.TestCase):
    def test_threshold_controls_membership(self):
        train = [{"id": 10, "claim": "drug a lowers blood pressure in adults"}]
        dev = [{"id": 1, "claim": "drug a raises blood pressure in adults"},    # Jaccard 6/8 = 0.75
               {"id": 2, "claim": "chocolate improves memory"}]
        self.assertEqual(D.twin_dev_ids(train, dev, 0.7), {1})
        self.assertEqual(D.twin_dev_ids(train, dev, 0.9), set())


class NearDuplicates(unittest.TestCase):
    def test_exact_and_near(self):
        train = [{"id": 10, "claim": "Aspirin reduces the risk of heart attack in adults."}]
        dev = [{"id": 1, "claim": "aspirin reduces the risk of heart attack in adults!"},
               {"id": 2, "claim": "Chocolate improves memory."}]
        out = D.near_duplicates(train, dev)
        self.assertEqual([(o["dev_id"], o["train_id"]) for o in out], [(1, 10)])


if __name__ == "__main__":
    unittest.main()