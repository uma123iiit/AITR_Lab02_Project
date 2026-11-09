#!/usr/bin/env python
"""Condition A (claim only): fit TF-IDF + LR on train, predict the frozen matched dev claims, save outputs."""
import argparse
import csv
import json
import sys
from collections import Counter
from datetime import datetime, timezone
from importlib import metadata
from pathlib import Path

import joblib

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from scifact_verif import data, verifier  # noqa: E402
from scifact_verif.seed import set_seed  # noqa: E402

CONDITION = "A"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--matched-dir", required=True,
                    help="e.g. results/audit/dev_all_labeled_nd-holdout (holds matched_claims.csv)")
    ap.add_argument("--data-dir", default=None)
    ap.add_argument("--out", default=str(ROOT / "results/predictions"))
    a = ap.parse_args()

    seed_info = set_seed(42)
    cfg = verifier.LRConfig()
    d = Path(a.data_dir) if a.data_dir else data.find_data_dir(ROOT / "data/raw/scifact")
    matched_dir = Path(a.matched_dir)

    # training data: every labeled train claim
    train = data.load_claims(d / "claims_train.jsonl")
    labels = [data.derive_gold_label(c) for c in train]
    bad = [(c["id"], r) for c, (lab, r) in zip(train, labels) if lab is None]
    if bad:
        raise SystemExit(f"unlabeled/invalid train claims, stop and diagnose: {bad[:5]}")
    train_ids = [c["id"] for c in train]
    train_y = [lab for lab, _ in labels]
    train_x = [verifier.make_input(CONDITION, c["claim"]) for c in train]

    # evaluation data: frozen matched dev claims
    with open(matched_dir / "matched_claims.csv", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    ids_txt = [int(x) for x in (matched_dir / "matched_claim_ids.txt").read_text().split()]
    if [int(r["claim_id"]) for r in rows] != ids_txt:
        raise SystemExit("matched_claims.csv and matched_claim_ids.txt disagree")
    dev_text = {c["id"]: c["claim"] for c in data.load_claims(d / "claims_dev.jsonl")}
    for r in rows:
        if dev_text.get(int(r["claim_id"])) != r["claim"]:
            raise SystemExit(f"claim text mismatch for id {r['claim_id']}")
    if set(train_ids) & set(ids_txt):
        raise SystemExit("train and matched dev claim ids overlap")

    vec, clf, info = verifier.fit(train_x, train_y, cfg)
    dev_x = [verifier.make_input(CONDITION, r["claim"]) for r in rows]
    classes, proba, pred, seconds = verifier.predict(vec, clf, dev_x)
    unseen = {r["gold_label"] for r in rows} - set(classes)
    if unseen:
        raise SystemExit(f"gold labels never seen in training: {unseen}")

    ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    run_id = f"{CONDITION}_{cfg.config_id()}_{ts}"
    out = Path(a.out) / run_id
    out.mkdir(parents=True, exist_ok=False)          # never overwrite a previous run

    sk = metadata.version("scikit-learn")
    with open(out / "predictions.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["claim_id", "condition", "gold_label", "predicted_label"] + [f"p_{c}" for c in classes]
                   + ["input_text_hash", "truncation_flag", "evidence_doc_ids", "config_id", "model_revision",
                      "seed", "inference_ms_per_claim", "exclusion_reason"])
        for r, x, p, y in zip(rows, dev_x, proba, pred):
            w.writerow([r["claim_id"], CONDITION, r["gold_label"], y] + [f"{v:.8f}" for v in p]
                       + [verifier.input_hash(x), 0, "", cfg.config_id(), f"scikit-learn=={sk}", 42,
                          f"{1000 * seconds / len(rows):.4f}", ""])
    joblib.dump({"vectorizer": vec, "classifier": clf}, out / "model.joblib")
    (out / "train_claim_ids.txt").write_text("".join(f"{i}\n" for i in train_ids))
    (out / "run_meta.json").write_text(json.dumps({
        "run_id": run_id, "condition": CONDITION, "config_id": cfg.config_id(), "config": cfg.__dict__,
        "class_order": classes, "seed_info": seed_info, "fit_info": info,
        "train_class_counts": dict(Counter(train_y)), "n_eval": len(rows),
        "matched_dir": str(matched_dir),
        "matched_ids_sha256": data.sha256_file(matched_dir / "matched_claim_ids.txt"),
        "train_file_sha256": data.sha256_file(d / "claims_train.jsonl"),
        "dev_file_sha256": data.sha256_file(d / "claims_dev.jsonl"),
        "versions": {p: metadata.version(p) for p in ["scikit-learn", "numpy", "scipy"]},
        "python": sys.version.split()[0], "timestamp_utc": ts}, indent=2, default=str))

    print(f"run_id: {run_id}")
    print(f"train n={info['n_train']} class counts={dict(Counter(train_y))}")
    print(f"vocab size={info['vocab_size']} converged={info['converged']} n_iter={info['n_iter']} "
          f"fit={info['fit_seconds']}s")
    print(f"class order (clf.classes_): {classes}")
    print(f"eval n={len(rows)} proba.shape={proba.shape} max |row sum - 1|={abs(proba.sum(1) - 1).max():.2e}")
    print(f"predicted label counts (not a metric): {dict(Counter(pred))}")
    print(f"inference: {1000 * seconds / len(rows):.3f} ms/claim (batch of {len(rows)})")
    for r, p, y in list(zip(rows, proba, pred))[:3]:
        print(f"  claim {r['claim_id']}: gold={r['gold_label']} pred={y} p={[round(float(v), 3) for v in p]}")
    print(f"written to: {out}")


if __name__ == "__main__":
    main()