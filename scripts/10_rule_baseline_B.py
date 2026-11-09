#!/usr/bin/env python
"""Rule baseline for condition B (PC-004): predict NEI iff the gold evidence is empty, otherwise SUPPORT.

Uses only the b_evidence_empty flag from the frozen audit. Scored with the same metric code and slices as 04_evaluate.py,
including a paired bootstrap of B minus the rule.
"""
import argparse
import csv
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from scifact_verif import metrics as M  # noqa: E402

CLASSES = ["CONTRADICT", "NOT_ENOUGH_INFO", "SUPPORT"]
SLICE_LABELS = ["SUPPORT", "CONTRADICT"]


def ids(p):
    return [int(x) for x in Path(p).read_text().split()]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--matched-dir", required=True)
    ap.add_argument("--b-pred", required=True)
    ap.add_argument("--out", default=str(ROOT / "results/metrics"))
    a = ap.parse_args()
    md = Path(a.matched_dir)
    with open(md / "matched_claims.csv", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    order = [int(r["claim_id"]) for r in rows]
    brows, classes = M.read_predictions(a.b_pred)
    if [int(r["claim_id"]) for r in brows] != order or classes != CLASSES:
        raise SystemExit("B predictions do not match the frozen matched set or class order")
    k = len(CLASSES)
    g = M.encode([r["gold_label"] for r in rows], CLASSES)
    rule = M.encode(["NOT_ENOUGH_INFO" if r["b_evidence_empty"] == "True" else "SUPPORT" for r in rows], CLASSES)
    b = M.encode([r["predicted_label"] for r in brows], CLASSES)
    full, sl = list(range(k)), [CLASSES.index(c) for c in SLICE_LABELS]
    sets = {"primary_matched": (set(order), full), "gold_evidence_slice": (set(ids(md / "rq2_eligible_claim_ids.txt")), sl),
            "sensitivity_j0.7_matched": (set(ids(md / "sensitivity_j0.7_matched_claim_ids.txt")), full),
            "sensitivity_j0.7_gold_evidence_slice": (set(ids(md / "sensitivity_j0.7_gold_evidence_claim_ids.txt")), sl)}
    out, nei = {}, CLASSES.index("NOT_ENOUGH_INFO")
    for name, (keep, idx) in sets.items():
        mask = np.array([i in keep for i in order])
        cm_r, cm_b = M.confusion(g[mask], rule[mask], k), M.confusion(g[mask], b[mask], k)
        pr, rc, f1r, _ = M.per_class(cm_r)
        pb, rb, f1b, _ = M.per_class(cm_b)
        diff = M.paired_bootstrap(g[mask], rule[mask], b[mask], k, idx)
        out[name] = {"n": int(mask.sum()), "rule": {"macro_f1": M.macro_f1(cm_r, idx), "accuracy": M.accuracy(cm_r),
                                                    "nei_precision": float(pr[nei]), "nei_recall": float(rc[nei])},
                     "B": {"macro_f1": M.macro_f1(cm_b, idx), "accuracy": M.accuracy(cm_b),
                           "nei_precision": float(pb[nei]), "nei_recall": float(rb[nei])},
                     "B_minus_rule_macro_f1": diff}
        r_, b_ = out[name]["rule"], out[name]["B"]
        print(f"[{name}] n={out[name]['n']}")
        print(f"   rule: macro-F1={r_['macro_f1']:.4f} acc={r_['accuracy']:.4f} NEI P={r_['nei_precision']:.3f} R={r_['nei_recall']:.3f}")
        print(f"   B   : macro-F1={b_['macro_f1']:.4f} acc={b_['accuracy']:.4f} NEI P={b_['nei_precision']:.3f} R={b_['nei_recall']:.3f}")
        print(f"   B - rule macro-F1 = {diff['difference']:+.4f}  95% CI [{diff['ci95_low']:+.4f}, {diff['ci95_high']:+.4f}]")
    dest = Path(a.out) / f"rule_baseline_B_{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')}.json"
    dest.write_text(json.dumps({"rule": "NEI iff b_evidence_empty else SUPPORT", "b_pred": a.b_pred, "results": out}, indent=2))
    print(f"written to: {dest}")


if __name__ == "__main__":
    main()