#!/usr/bin/env python
"""Assemble the Prompt07 freeze-gate config from files that already exist.

Default writes configs/primary_frozen.draft.yaml. --final writes configs/primary_frozen.yaml (refuses to
overwrite) and requires --inspection-confirmed. Anything that cannot be verified is marked BLOCKED or UNRESOLVED.
"""
import argparse
import json
import sys
from dataclasses import asdict
from datetime import datetime, timezone
from importlib import metadata
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from scifact_verif import data, inputs, verifier  # noqa: E402


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--matched-dir", required=True)
    ap.add_argument("--ranks-dir", required=True)
    ap.add_argument("--final", action="store_true")
    ap.add_argument("--inspection-confirmed", action="store_true")
    a = ap.parse_args()
    if a.final and not a.inspection_confirmed:
        raise SystemExit("--final needs --inspection-confirmed (researcher has inspected the condition inputs)")

    audit_dir = ROOT / "results/audit"
    audit = json.loads((audit_dir / "audit.json").read_text())
    matched = Path(a.matched_dir)
    ranks_meta = json.loads((Path(a.ranks_dir) / "retrieval_meta.json").read_text())
    cfg = verifier.LRConfig()
    dl = ROOT / "data/raw/scifact"
    sens = sorted(p.name for p in matched.glob("sensitivity_*.txt"))
    out = {
        "status": "FROZEN" if a.final else "DRAFT (not frozen)",
        "created_utc": datetime.now(timezone.utc).isoformat(),
        "data": {
            "source": (dl / "source_url.txt").read_text().strip() if (dl / "source_url.txt").exists() else "BLOCKED",
            "download_date_utc": (dl / "download_date_utc.txt").read_text().strip(),
            "archive_sha256": (dl / "data.tar.gz.sha256").read_text().split()[0],
            "file_sha256": audit["file_sha256"],
            "upstream_revision": "UNVERIFIED: 'release/latest' tarball; upstream commit not recorded, sha256 recorded",
            "license": "UNRESOLVED: Hugging Face card shows cc-by-nc-2.0; per-abstract terms not cleared",
        },
        "label_mapping": json.loads((audit_dir / "label_map.json").read_text()),
        "matched_set": {"split": "dev", "policy": "all_labeled", "near_duplicates": "holdout (Jaccard >= 0.9, PC-001)",
                        "dir": str(matched), "ids_sha256": data.sha256_file(matched / "matched_claim_ids.txt"),
                        "gold_evidence_slice_sha256": data.sha256_file(matched / "rq2_eligible_claim_ids.txt"),
                        "sensitivity_files": {n: data.sha256_file(matched / n) for n in sens},
                        "counts": {"matched": len((matched / "matched_claim_ids.txt").read_text().split()),
                                   "gold_evidence_slice": len((matched / "rq2_eligible_claim_ids.txt").read_text().split())}},
        "condition_inputs": {"A": "claim text only",
                             "B": verifier.TEMPLATE + " with the first annotated rationale set per document in file order "
                                  "(PC-004); empty for NEI claims, so B is an oracle only on the gold-evidence slice",
                             "C": verifier.TEMPLATE + " with BM25 top-5 title+abstract in rank order",
                             "separator": inputs.SEPARATOR},
        "retrieval": {"run_id": ranks_meta["run_id"], "top_k": ranks_meta["top_k"],
                      "corpus_sha256": ranks_meta["corpus_sha256"], "methods": ranks_meta["methods"]},
        "verifier": {"family": "TF-IDF + LogisticRegression, one model per condition, same train claims",
                     "config_id": cfg.config_id(), "config": json.loads(json.dumps(asdict(cfg))),
                     "prediction_rule": "argmax class probability, no threshold tuning"},
        "metrics": {"primary": "macro-F1", "secondary": ["accuracy", "per-class P/R/F1", "confusion matrix"],
                    "paired_differences": ["B-A", "C-A", "B-C"],
                    "bootstrap": {"resamples": 2000, "seed": 42, "unit": "claim id", "ci": "percentile 95%"},
                    "zero_division": "0.0", "retrieval": "Recall@5 (document-level hit), Wilson 95%"},
        "seed": 42,
        "software": {p: metadata.version(p) for p in ["scikit-learn", "numpy", "scipy", "rank-bm25", "matplotlib"]}
                    | {"python": sys.version.split()[0]},
        "rq3": {"codebook": "NOT FROZEN (must be frozen before sampled errors are inspected)",
                "sampling": "up to 50 errors, stratified by condition, seed 42"},
        "researcher_inspection_of_inputs": "CONFIRMED" if a.inspection_confirmed else "PENDING",
        "protocol_changes": "logs/protocol_changes.md (PC-001..PC-003)",
    }
    dest = ROOT / "configs" / ("primary_frozen.yaml" if a.final else "primary_frozen.draft.yaml")
    if a.final and dest.exists():
        raise SystemExit(f"{dest} already exists; create a new protocol version instead of overwriting")
    dest.write_text(yaml.safe_dump(out, sort_keys=False, width=110))
    print(f"written: {dest}")


if __name__ == "__main__":
    main()