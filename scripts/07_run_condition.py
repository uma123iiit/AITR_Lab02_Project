#!/usr/bin/env python
"""Run one evidence condition (A, B or C): build inputs, fit TF-IDF + LR on train, predict the matched dev claims.

--dry-run builds and prints the inputs and statistics, then exits before fitting anything.
"""
import argparse
import csv
import json
import sys
from collections import Counter, defaultdict
from datetime import datetime, timezone
from importlib import metadata
from pathlib import Path

import joblib

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from scifact_verif import data, inputs, verifier  # noqa: E402
from scifact_verif.seed import set_seed  # noqa: E402

RATIONALE_POLICY = "first"   # condition B: first annotated rationale set per document (PC-004)


def load_ranks(ranks_dir):
    meta = json.loads((ranks_dir / "retrieval_meta.json").read_text())
    ranks = defaultdict(list)
    with open(ranks_dir / "ranks_bm25.csv", encoding="utf-8") as f:       # BM25 is the primary retriever
        for r in csv.DictReader(f):
            ranks[(r["split"], int(r["claim_id"]))].append((int(r["rank"]), int(r["doc_id"]), float(r["score"])))
    return meta, {k: sorted(v) for k, v in ranks.items()}


def build_evidence(condition, split, raw, corpus, ranks):
    """Returns (evidence text or None, doc ids used, retrieval scores). Gold annotations are read only for B."""
    if condition == "A":
        return None, [], []
    if condition == "B":
        items, reasons = data.gold_evidence(raw, corpus, rationale=RATIONALE_POLICY)
        if reasons:
            raise SystemExit(f"claim {raw['id']}: gold evidence problem {reasons}")
        items = sorted(items, key=lambda x: int(x["doc_id"]))
        return inputs.gold_evidence_text(items), [int(i["doc_id"]) for i in items], []
    top = ranks.get((split, raw["id"]), [])
    if [r for r, _, _ in top] != [1, 2, 3, 4, 5]:
        raise SystemExit(f"claim {raw['id']} ({split}): ranking missing or incomplete")
    ids = [d for _, d, _ in top]
    return inputs.retrieved_evidence_text(ids, corpus), ids, [s for _, _, s in top]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--condition", required=True, choices=["A", "B", "C"])
    ap.add_argument("--matched-dir", required=True)
    ap.add_argument("--ranks-dir", default=None, help="required for C")
    ap.add_argument("--data-dir", default=None)
    ap.add_argument("--out", default=str(ROOT / "results/predictions"))
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args()
    cond = a.condition
    if cond == "C" and not a.ranks_dir:
        raise SystemExit("--ranks-dir is required for condition C")

    seed_info = set_seed(42)
    cfg = verifier.LRConfig()
    d = Path(a.data_dir) if a.data_dir else data.find_data_dir(ROOT / "data/raw/scifact")
    corpus = data.load_corpus(d / "corpus.jsonl")
    matched_dir = Path(a.matched_dir)
    ranks, ranks_meta = {}, None
    if cond == "C":
        ranks_meta, ranks = load_ranks(Path(a.ranks_dir))
        if ranks_meta["corpus_sha256"] != data.sha256_file(d / "corpus.jsonl"):
            raise SystemExit("ranking was produced from a different corpus file")

    train = data.load_claims(d / "claims_train.jsonl")
    labels = [data.derive_gold_label(c) for c in train]
    bad = [(c["id"], r) for c, (lab, r) in zip(train, labels) if lab is None]
    if bad:
        raise SystemExit(f"unlabeled/invalid train claims: {bad[:5]}")
    train_rows = []
    for c, (lab, _) in zip(train, labels):
        ev, ids, scores = build_evidence(cond, "train", c, corpus, ranks)
        train_rows.append({"id": c["id"], "label": lab, "ev_ids": ids, "text": verifier.make_input(cond, c["claim"], ev)})

    dev_raw = {c["id"]: c for c in data.load_claims(d / "claims_dev.jsonl")}
    with open(matched_dir / "matched_claims.csv", encoding="utf-8") as f:
        matched = list(csv.DictReader(f))
    ids_txt = [int(x) for x in (matched_dir / "matched_claim_ids.txt").read_text().split()]
    if [int(r["claim_id"]) for r in matched] != ids_txt:
        raise SystemExit("matched_claims.csv and matched_claim_ids.txt disagree")
    dev_rows = []
    for r in matched:
        raw = dev_raw[int(r["claim_id"])]
        if raw["claim"] != r["claim"]:
            raise SystemExit(f"claim text mismatch for id {r['claim_id']}")
        ev, ids, scores = build_evidence(cond, "dev", raw, corpus, ranks)
        if cond == "B" and (not ids) != (r["b_evidence_empty"] == "True"):
            raise SystemExit(f"claim {r['claim_id']}: empty-evidence flag disagrees with the audit")
        dev_rows.append({"id": raw["id"], "gold": r["gold_label"], "ev_ids": ids, "scores": scores,
                         "text": verifier.make_input(cond, raw["claim"], ev),
                         "gold_ids": sorted(int(k) for k in raw["evidence"])})   # audit column only, after inputs are built
    if {x["id"] for x in train_rows} & {x["id"] for x in dev_rows}:
        raise SystemExit("train and matched dev claim ids overlap")

    def stats(rows):
        lens = [len(x["text"]) for x in rows]
        return {"n": len(rows), "mean_chars": round(sum(lens) / len(lens), 1), "max_chars": max(lens),
                "empty_evidence": sum(1 for x in rows if cond != "A" and not x["ev_ids"])}
    print(f"condition {cond}: template={'claim only' if cond == 'A' else verifier.TEMPLATE!r} separator={inputs.SEPARATOR!r}")
    print(f"input stats train={stats(train_rows)} dev={stats(dev_rows)}")
    if cond != "A":
        for title, x in [("first dev claim with evidence", next(r for r in dev_rows if r["ev_ids"])),
                         ("first dev claim without evidence", next((r for r in dev_rows if not r["ev_ids"]), None))]:
            if x is not None:
                print(f"preview ({title}) id={x['id']} evidence docs={x['ev_ids']}:\n   {x['text'][:380]!r}")
    if a.dry_run:
        print("dry run: nothing fitted, nothing written")
        return

    vec, clf, info = verifier.fit([x["text"] for x in train_rows], [x["label"] for x in train_rows], cfg)
    classes, proba, pred, seconds = verifier.predict(vec, clf, [x["text"] for x in dev_rows])
    unseen = {x["gold"] for x in dev_rows} - set(classes)
    if unseen:
        raise SystemExit(f"gold labels never seen in training: {unseen}")

    ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    run_id = f"{cond}_{cfg.config_id()}_{ts}"
    out = Path(a.out) / run_id
    out.mkdir(parents=True, exist_ok=False)
    sk = metadata.version("scikit-learn")
    with open(out / "predictions.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["claim_id", "condition", "gold_label", "predicted_label"] + [f"p_{c}" for c in classes]
                   + ["input_text_hash", "truncation_flag", "evidence_doc_ids", "retrieval_scores",
                      "gold_evidence_doc_ids", "config_id", "model_revision", "seed", "inference_ms_per_claim",
                      "exclusion_reason"])
        for x, p, y in zip(dev_rows, proba, pred):
            w.writerow([x["id"], cond, x["gold"], y] + [f"{v:.8f}" for v in p]
                       + [verifier.input_hash(x["text"]), 0, ";".join(map(str, x["ev_ids"])),
                          ";".join(f"{s:.6f}" for s in x["scores"]), ";".join(map(str, x["gold_ids"])),
                          cfg.config_id(), f"scikit-learn=={sk}", 42, f"{1000 * seconds / len(dev_rows):.4f}", ""])
    joblib.dump({"vectorizer": vec, "classifier": clf}, out / "model.joblib")
    (out / "train_claim_ids.txt").write_text("".join(f"{x['id']}\n" for x in train_rows))
    (out / "run_meta.json").write_text(json.dumps({
        "run_id": run_id, "condition": cond, "config_id": cfg.config_id(), "config": cfg.__dict__,
        "template": None if cond == "A" else verifier.TEMPLATE, "separator": inputs.SEPARATOR,
        "rationale_policy": RATIONALE_POLICY if cond == "B" else None,
        "class_order": classes, "seed_info": seed_info, "fit_info": info,
        "train_class_counts": dict(Counter(x["label"] for x in train_rows)), "n_eval": len(dev_rows),
        "input_stats": {"train": stats(train_rows), "dev": stats(dev_rows)},
        "matched_dir": str(matched_dir), "matched_ids_sha256": data.sha256_file(matched_dir / "matched_claim_ids.txt"),
        "retrieval_run_id": ranks_meta["run_id"] if ranks_meta else None,
        "file_sha256": {n: data.sha256_file(d / n) for n in ["claims_train.jsonl", "claims_dev.jsonl", "corpus.jsonl"]},
        "versions": {p: metadata.version(p) for p in ["scikit-learn", "numpy", "scipy"]},
        "python": sys.version.split()[0], "timestamp_utc": ts}, indent=2, default=str))
    print(f"run_id: {run_id}")
    print(f"vocab size={info['vocab_size']} converged={info['converged']} n_iter={info['n_iter']} fit={info['fit_seconds']}s")
    print(f"class order: {classes}; proba.shape={proba.shape} max |row sum - 1|={abs(proba.sum(1) - 1).max():.2e}")
    print(f"predicted label counts (not a metric): {dict(Counter(pred))}")
    print(f"written to: {out}")


if __name__ == "__main__":
    main()