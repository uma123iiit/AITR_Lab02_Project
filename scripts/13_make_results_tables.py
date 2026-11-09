#!/usr/bin/env python
"""Flatten saved metric JSON files into CSV tables. Copies numbers only; computes nothing new and invents nothing.
Every row carries the source file and its sha256."""
import argparse
import csv
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def write(path, rows):
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)
    print(f"wrote {path} ({len(rows)} rows)")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--eval", required=True)
    ap.add_argument("--rule", required=True)
    ap.add_argument("--rq2", required=True)
    ap.add_argument("--out", default=str(ROOT / "results"))
    a = ap.parse_args()
    out = Path(a.out)
    m = json.loads(Path(a.eval).read_text())
    src, h = a.eval, sha(a.eval)
    note = "dev set, frozen primary run, not test"

    main_rows = []
    for cond, sl in m["results"].items():
        for name, r in sl.items():
            pc = r["per_class"]
            main_rows.append({"condition": cond, "slice": name, "n": r["n"], "macro_f1": round(r["macro_f1"], 4),
                              "macro_f1_over": "+".join(r["macro_f1_labels"]), "accuracy": round(r["accuracy"], 4),
                              "f1_CONTRADICT": round(pc["CONTRADICT"]["f1"], 4),
                              "f1_NOT_ENOUGH_INFO": round(pc["NOT_ENOUGH_INFO"]["f1"], 4),
                              "f1_SUPPORT": round(pc["SUPPORT"]["f1"], 4), "note": note, "source": src, "source_sha256": h})
    write(out / "results.csv", main_rows)

    diff_rows = []
    for cmp_, sl in m["paired_differences"].items():
        for name, d in sl.items():
            diff_rows.append({"comparison": cmp_, "slice": name, "n_claims": d["n_claims"], "difference_macro_f1": round(d["difference"], 4),
                              "ci95_low": round(d["ci95_low"], 4), "ci95_high": round(d["ci95_high"], 4),
                              "ci_excludes_zero": d["ci_excludes_zero"], "resamples": d["n_resamples"], "seed": d["seed"],
                              "note": note, "source": src, "source_sha256": h})
    write(out / "results_paired_differences.csv", diff_rows)

    rb = json.loads(Path(a.rule).read_text())
    rule_rows = []
    for name, r in rb["results"].items():
        d = r["B_minus_rule_macro_f1"]
        rule_rows.append({"slice": name, "n": r["n"], "rule_macro_f1": round(r["rule"]["macro_f1"], 4), "rule_accuracy": round(r["rule"]["accuracy"], 4),
                          "B_macro_f1": round(r["B"]["macro_f1"], 4), "B_accuracy": round(r["B"]["accuracy"], 4),
                          "B_minus_rule": round(d["difference"], 4), "ci95_low": round(d["ci95_low"], 4), "ci95_high": round(d["ci95_high"], 4),
                          "rule": rb["rule"], "source": a.rule, "source_sha256": sha(a.rule)})
    write(out / "results_rule_baseline_B.csv", rule_rows)

    q = json.loads(Path(a.rq2).read_text())
    q_rows = []
    for g, d in q["groups"].items():
        for cond, r in d["accuracy"].items():
            q_rows.append({"bm25_hit_group": g, "group_n": d["n"], "condition": cond, "correct": r["correct"], "accuracy": round(r["accuracy"], 4),
                           "wilson95_low": round(r["wilson95"][0], 4), "wilson95_high": round(r["wilson95"][1], 4),
                           "gold_label_counts": json.dumps(d["gold_label_counts"], sort_keys=True), "source": a.rq2, "source_sha256": sha(a.rq2)})
    write(out / "results_rq2_hit_miss.csv", q_rows)


if __name__ == "__main__":
    main()