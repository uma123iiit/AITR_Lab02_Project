#!/usr/bin/env python
"""Draw the RQ3 error sample (PC-005 codebook must be frozen and its hash must verify).

Population: every claim-condition pair in the 286-claim matched dev set with predicted_label != gold_label.
Up to 50 errors, equal allocation across A/B/C (capped, remainder redistributed), seed 42. Writes the coding sheet with
empty coder columns. Prints counts only; it does not print case contents. Refuses to overwrite an existing sample.
"""
import argparse
import csv
import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from scifact_verif import sampling  # noqa: E402

TOTAL, SEED = 50, 42


def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--pred", action="append", required=True, help="COND=predictions.csv (A, B, C)")
    ap.add_argument("--hits", required=True, help="per_claim_hits.csv (BM25 hit status, gold-evidence slice only)")
    ap.add_argument("--out", default=str(ROOT / "results/rq3"))
    a = ap.parse_args()

    cb = ROOT / "configs/rq3_codebook.FROZEN.md"
    want = (ROOT / "configs/rq3_codebook.FROZEN.md.sha256").read_text().split()[0]
    if sha(cb) != want:
        raise SystemExit("frozen codebook hash does not verify; refusing to draw a sample")
    out = Path(a.out)
    if (out / "rq3_sample.csv").exists():
        raise SystemExit(f"{out / 'rq3_sample.csv'} exists; the sample is drawn once")

    preds, paths = {}, {}
    for item in a.pred:
        c, p = item.split("=", 1)
        paths[c] = p
        with open(p, encoding="utf-8") as f:
            preds[c] = {int(r["claim_id"]): r for r in csv.DictReader(f)}
    if sorted(preds) != ["A", "B", "C"]:
        raise SystemExit("need conditions A, B and C")
    with open(a.hits, encoding="utf-8") as f:
        hit = {int(r["claim_id"]): r["hit_at_5"] for r in csv.DictReader(f) if r["method"] == "bm25"}

    errors = {c: [i for i, r in preds[c].items() if r["predicted_label"] != r["gold_label"]] for c in "ABC"}
    counts = {c: len(v) for c, v in errors.items()}
    take = sampling.allocate(counts, TOTAL)
    chosen = sampling.draw(errors, take, SEED)

    rows = []
    for c in "ABC":
        for i in chosen[c]:
            r = preds[c][i]
            rows.append({"condition": c, "claim_id": i, "gold_label": r["gold_label"], "predicted_label": r["predicted_label"],
                         "evidence_doc_ids_shown": r["evidence_doc_ids"], "gold_evidence_doc_ids": r["gold_evidence_doc_ids"],
                         "evidence_empty": int(c != "A" and not r["evidence_doc_ids"]),
                         "bm25_hit_at_5": hit.get(i, "") if c == "C" else "", "truncation_flag": r["truncation_flag"],
                         "coder_category": "", "coder_note": ""})
    out.mkdir(parents=True, exist_ok=True)
    with open(out / "rq3_sample.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)
    (out / "rq3_sample_meta.json").write_text(json.dumps({
        "drawn_utc": datetime.now(timezone.utc).isoformat(), "seed": SEED, "total_cap": TOTAL,
        "allocation_rule": "equal across A/B/C, capped at stratum size, remainder redistributed (sampling.allocate)",
        "error_counts_population": counts, "sampled": take, "codebook": "configs/rq3_codebook.FROZEN.md",
        "codebook_sha256": want, "prediction_files": {c: {"path": paths[c], "sha256": sha(paths[c])} for c in "ABC"},
        "sample_csv_sha256": sha(out / "rq3_sample.csv"),
        "note": "claim text and shown evidence are not in the sheet; read them from the corpus/claims files and predictions."},
        indent=2))
    print(f"population errors: {counts}")
    print(f"sampled: {take} (total {sum(take.values())}), seed {SEED}")
    print(f"written to: {out}")


if __name__ == "__main__":
    main()