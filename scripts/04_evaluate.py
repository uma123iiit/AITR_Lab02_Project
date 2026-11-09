#!/usr/bin/env python
"""Recompute all classification metrics from saved predictions. Development-set evaluation, not a test result."""
import argparse
import csv
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from scifact_verif import data, metrics as M  # noqa: E402

NOTE = "Development-set evaluation (official dev split, frozen matched claims). Not a test result."
DIFFS = [("B", "A"), ("C", "A"), ("B", "C")]   # reported as first minus second
SLICE_LABELS = ["SUPPORT", "CONTRADICT"]


def plot_confusion(cm, classes, title, path):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    fig, ax = plt.subplots(figsize=(4.6, 4.0))
    ax.imshow(cm, cmap="Blues")
    ax.set_xticks(range(len(classes)), labels=classes, rotation=30, ha="right")
    ax.set_yticks(range(len(classes)), labels=classes)
    ax.set_xlabel("predicted")
    ax.set_ylabel("gold")
    ax.set_title(title, fontsize=9)
    for i in range(len(classes)):
        for j in range(len(classes)):
            ax.text(j, i, int(cm[i, j]), ha="center", va="center",
                    color="white" if cm[i, j] > cm.max() / 2 else "black")
    fig.tight_layout()
    fig.savefig(path, dpi=150)
    plt.close(fig)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--pred", action="append", required=True, metavar="COND=PATH",
                    help="repeatable, e.g. A=results/predictions/<run>/predictions.csv")
    ap.add_argument("--matched-dir", required=True)
    ap.add_argument("--out", default=str(ROOT / "results/metrics"))
    ap.add_argument("--n-resamples", type=int, default=2000)
    ap.add_argument("--sensitivity-jaccard", type=float, default=None,
                    help="add the declared sensitivity slices (files written by 02_audit_data.py, PC-003)")
    a = ap.parse_args()

    matched_dir = Path(a.matched_dir)
    ids = [int(x) for x in (matched_dir / "matched_claim_ids.txt").read_text().split()]
    slice_ids = {int(x) for x in (matched_dir / "rq2_eligible_claim_ids.txt").read_text().split()}
    with open(matched_dir / "matched_claims.csv", encoding="utf-8") as f:
        gold_ref = {int(r["claim_id"]): r["gold_label"] for r in csv.DictReader(f)}

    loaded, classes_ref = {}, None
    for spec in a.pred:
        cond, path = spec.split("=", 1)
        rows, classes = M.read_predictions(path)
        if [int(r["claim_id"]) for r in rows] != ids:
            raise SystemExit(f"{cond}: claim ids differ from the frozen matched set (or order)")
        if {r["condition"] for r in rows} != {cond}:
            raise SystemExit(f"{cond}: condition column in {path} says {sorted({r['condition'] for r in rows})}")
        if any(r["gold_label"] != gold_ref[int(r["claim_id"])] for r in rows):
            raise SystemExit(f"{cond}: gold labels differ from matched_claims.csv")
        if classes_ref is not None and classes != classes_ref:
            raise SystemExit("class order differs between conditions")
        classes_ref = classes
        loaded[cond] = {"path": path, "rows": rows, "sha256": data.sha256_file(path),
                        "config_id": rows[0]["config_id"]}

    classes, k = classes_ref, len(classes_ref)
    full_idx = list(range(k))
    slice_idx = [classes.index(c) for c in SLICE_LABELS]
    in_slice = np.array([i in slice_ids for i in ids])
    slices = {"primary_matched": (np.ones(len(ids), bool), full_idx, classes),
              "gold_evidence_slice": (in_slice, slice_idx, SLICE_LABELS)}

    if a.sensitivity_jaccard is not None:
        tag = f"sensitivity_j{a.sensitivity_jaccard:g}"
        sens = {int(x) for x in (matched_dir / f"{tag}_matched_claim_ids.txt").read_text().split()}
        sens_gold = {int(x) for x in (matched_dir / f"{tag}_gold_evidence_claim_ids.txt").read_text().split()}
        slices[f"{tag}_matched"] = (np.array([i in sens for i in ids]), full_idx, classes)
        slices[f"{tag}_gold_evidence_slice"] = (np.array([i in sens_gold for i in ids]), slice_idx, SLICE_LABELS)

    ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    out = Path(a.out) / f"eval_{ts}"
    out.mkdir(parents=True, exist_ok=False)
    results, arrays = {}, {}
    print(NOTE)
    for cond, d in loaded.items():
        g = M.encode([r["gold_label"] for r in d["rows"]], classes)
        p = M.encode([r["predicted_label"] for r in d["rows"]], classes)
        arrays[cond] = (g, p)
        results[cond] = {}
        for name, (mask, idx, idx_names) in slices.items():
            cm = M.confusion(g[mask], p[mask], k)
            prec, rec, f1, sup = M.per_class(cm)
            res = {"n": int(mask.sum()), "macro_f1": M.macro_f1(cm, idx), "macro_f1_labels": idx_names,
                   "accuracy": M.accuracy(cm), "confusion_rows_gold_cols_pred": cm.tolist(),
                   "per_class": {c: {"precision": float(prec[i]), "recall": float(rec[i]),
                                     "f1": float(f1[i]), "gold_support": int(sup[i])}
                                 for i, c in enumerate(classes)}}
            results[cond][name] = res
            np.savetxt(out / f"confusion_{cond}_{name}.csv", cm, fmt="%d", delimiter=",",
                       header=",".join(classes), comments="")
            plot_confusion(cm, classes, f"Condition {cond}, {name} (n={res['n']})",
                           out / f"confusion_{cond}_{name}.png")
            print(f"\n[{cond}] {name}: n={res['n']} macro-F1 ({'+'.join(idx_names)})={res['macro_f1']:.4f} "
                  f"accuracy={res['accuracy']:.4f}")
            for i, c in enumerate(classes):
                print(f"   {c:16} P={prec[i]:.3f} R={rec[i]:.3f} F1={f1[i]:.3f} support={sup[i]}")
            print("   confusion (rows gold, cols pred), order:", classes)
            for i, c in enumerate(classes):
                print(f"   {c:16}", cm[i].tolist())

    paired = {}
    for hi_c, lo_c in DIFFS:
        if hi_c in arrays and lo_c in arrays:
            paired[f"{hi_c}-{lo_c}"] = {}
            for name, (mask, idx, _) in slices.items():
                g = arrays[lo_c][0][mask]
                paired[f"{hi_c}-{lo_c}"][name] = M.paired_bootstrap(
                    g, arrays[lo_c][1][mask], arrays[hi_c][1][mask], k, idx, a.n_resamples)
    if paired:
        print("\npaired macro-F1 differences:", json.dumps(paired, indent=1))
    else:
        print(f"\npaired differences: skipped (need two of A/B/C, have {sorted(loaded)})")

    (out / "metrics.json").write_text(json.dumps({
        "note": NOTE, "eval_id": out.name, "class_order": classes,
        "inputs": {c: {k_: v for k_, v in d.items() if k_ != "rows"} for c, d in loaded.items()},
        "matched_ids_sha256": data.sha256_file(matched_dir / "matched_claim_ids.txt"),
        "results": results, "paired_differences": paired or "skipped: fewer than two conditions"}, indent=2))
    print(f"\nwritten to: {out}")


if __name__ == "__main__":
    main()