#!/usr/bin/env python
"""RQ2 second half: accuracy of condition C by BM25 top-5 hit/miss on the gold-evidence slice (dev, saved outputs only).

Descriptive. Hit status comes from 06_eval_retrieval.py (document-level hit). A and B accuracy on the same groups are
reported as references: their inputs do not depend on retrieval, so differences between groups reflect which claims miss.
"""
import argparse
import csv
import json
import sys
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from scifact_verif import metrics  # noqa: E402


def read_csv(p):
    with open(p, encoding="utf-8") as f:
        return list(csv.DictReader(f))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--hits", required=True, help="per_claim_hits.csv from 06_eval_retrieval.py")
    ap.add_argument("--pred", action="append", required=True, help="COND=predictions.csv (A, B, C)")
    ap.add_argument("--out", default=str(ROOT / "results/metrics"))
    a = ap.parse_args()
    hit = {int(r["claim_id"]): int(r["hit_at_5"]) for r in read_csv(a.hits) if r["method"] == "bm25"}
    preds = {}
    for item in a.pred:
        c, p = item.split("=", 1)
        preds[c] = {int(r["claim_id"]): r for r in read_csv(p)}
    for c in "ABC":
        missing = [i for i in hit if i not in preds[c]]
        if missing:
            raise SystemExit(f"condition {c}: {len(missing)} slice claims have no prediction")
    groups = {"hit": [i for i in hit if hit[i]], "miss": [i for i in hit if not hit[i]]}
    out = {"note": "Development set, gold-evidence slice, BM25 document-level hit@5. Descriptive; groups are unequal in size.",
           "n": len(hit), "groups": {}}
    for g, ids in groups.items():
        out["groups"][g] = {"n": len(ids), "gold_label_counts": {}, "accuracy": {}}
        lab = defaultdict(int)
        for i in ids:
            lab[preds["C"][i]["gold_label"]] += 1
        out["groups"][g]["gold_label_counts"] = dict(lab)
        for c in "ABC":
            k = sum(preds[c][i]["gold_label"] == preds[c][i]["predicted_label"] for i in ids)
            lo, hi = metrics.wilson_interval(k, len(ids))
            out["groups"][g]["accuracy"][c] = {"correct": k, "n": len(ids), "accuracy": k / len(ids), "wilson95": [lo, hi]}
        by = {}
        for L in sorted(lab):
            sub = [i for i in ids if preds["C"][i]["gold_label"] == L]
            by[L] = {"n": len(sub), **{c: sum(preds[c][i]["predicted_label"] == L for i in sub) for c in "ABC"}}
        out["groups"][g]["correct_by_gold_label"] = by
    try:
        from scipy.stats import fisher_exact
        h, m = out["groups"]["hit"]["accuracy"]["C"], out["groups"]["miss"]["accuracy"]["C"]
        _, pv = fisher_exact([[h["correct"], h["n"] - h["correct"]], [m["correct"], m["n"] - m["correct"]]])
        out["exploratory_fisher_exact_p_C_hit_vs_miss"] = float(pv)
    except Exception as e:  # scipy optional
        out["exploratory_fisher_exact_p_C_hit_vs_miss"] = f"unavailable: {e}"
    for g in ("hit", "miss"):
        d = out["groups"][g]
        print(f"[{g}] n={d['n']} gold labels={d['gold_label_counts']}")
        for c in "ABC":
            r = d["accuracy"][c]
            print(f"   {c}: {r['correct']}/{r['n']} = {r['accuracy']:.3f}  Wilson95 [{r['wilson95'][0]:.3f}, {r['wilson95'][1]:.3f}]")
        print(f"   correct by gold label: {d['correct_by_gold_label']}")
    print(f"exploratory Fisher exact p (C, hit vs miss): {out['exploratory_fisher_exact_p_C_hit_vs_miss']}")
    dest = Path(a.out) / f"rq2_hit_miss_{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')}.json"
    dest.write_text(json.dumps(out, indent=2))
    print(f"written to: {dest}")


if __name__ == "__main__":
    main()