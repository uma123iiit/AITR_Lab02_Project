#!/usr/bin/env python
"""Audit raw SciFact files and freeze the matched claim set for one split and one eligibility policy."""
import argparse
import json
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from scifact_verif import data  # noqa: E402


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--data-dir", default=None, help="folder holding corpus.jsonl (default: search data/raw/scifact)")
    ap.add_argument("--split", default="dev", choices=["train", "dev"])
    ap.add_argument("--policy", required=True, choices=data.POLICIES,
                    help="how NEI claims (no gold evidence) enter the matched set; no default on purpose")
    ap.add_argument("--near-dup", required=True, choices=["holdout", "disclose"],
                    help="holdout: exclude dev claims that near-duplicate a train claim; disclose: keep and report only")
    ap.add_argument("--sensitivity-jaccard", type=float, default=None,
                    help="also write a declared sensitivity set: matched dev claims minus those with a train "
                         "twin at Jaccard >= this value (PC-003)")
    ap.add_argument("--out", default=str(ROOT / "results/audit"))
    a = ap.parse_args()

    d = Path(a.data_dir) if a.data_dir else data.find_data_dir(ROOT / "data/raw/scifact")
    corpus = data.load_corpus(d / "corpus.jsonl")
    claims = data.load_claims(d / f"claims_{a.split}.jsonl")
    train = data.load_claims(d / "claims_train.jsonl")

    report = data.audit(d)
    out_root = Path(a.out)
    out_root.mkdir(parents=True, exist_ok=True)
    (out_root / "audit.json").write_text(json.dumps(report, indent=2))
    (out_root / "label_map.json").write_text(json.dumps(data.label_map(train), indent=2))

    holdout = set()
    if a.near_dup == "holdout" and a.split == "dev":
        holdout = {p["dev_id"] for p in report.get("near_duplicates_train_dev", [])}
    matched, excluded = data.build_matched_set(claims, corpus, a.policy, holdout)
    out = data.write_artifacts(out_root, a.policy, a.split, matched, excluded, f"_nd-{a.near_dup}")

    print(f"data dir: {d}")
    print(f"corpus n={report['corpus_n']}  doc_id types={report['corpus_doc_id_types']}")
    for s, info in report["splits"].items():
        print(f"{s}: n={info['n']} id_types={info['id_types']} dup_ids={info['duplicate_ids']}"
              + (f" labels={info['gold_label_counts']} with_evidence={info['with_nonempty_evidence']}"
                 f" orphan_evidence_docs={info['evidence_doc_ids_not_in_corpus']}"
                 f" bad_sentence_idx_claims={info['bad_sentence_index_claims']}" if s != "test" else ""))
    nd = report.get("near_duplicates_train_dev", [])
    print(f"near-duplicate train/dev claim pairs (Jaccard>={data.NEAR_DUP_JACCARD}): {len(nd)} {nd[:5]}")
    print(f"--- split={a.split} policy={a.policy} near-dup={a.near_dup} ---")
    print(f"near-duplicate dev claims held out: {len(holdout)} ids={sorted(holdout)}")
    print(f"total={len(claims)} matched={len(matched)} excluded={len(excluded)}")
    print(f"matched label counts: {dict(Counter(m['gold_label'] for m in matched))}")
    print(f"matched with empty gold evidence (B input has no evidence): {sum(m['b_evidence_empty'] for m in matched)}")
    print(f"excluded by reason: {dict(Counter(e['reason_codes'] for e in excluded))}")
    print(f"RQ2 Recall@5 denominator (>=1 gold doc): {len(data.rq2_eligible_ids(matched))}")
    if a.sensitivity_jaccard is not None:
        if a.split != "dev":
            raise SystemExit("--sensitivity-jaccard applies to the dev split only")
        twins = data.twin_dev_ids(train, claims, a.sensitivity_jaccard)
        keep = [m for m in matched if m["claim_id"] not in twins]
        tag = f"sensitivity_j{a.sensitivity_jaccard:g}"
        (out / f"{tag}_matched_claim_ids.txt").write_text("".join(f"{m['claim_id']}\n" for m in keep))
        gold_keep = data.rq2_eligible_ids(keep)
        (out / f"{tag}_gold_evidence_claim_ids.txt").write_text("".join(f"{i}\n" for i in gold_keep))
        print(f"--- sensitivity set {tag} ---")
        print(f"dev claims with a train twin at Jaccard>={a.sensitivity_jaccard:g}: {len(twins)}")
        print(f"matched minus twins: {len(keep)} labels={dict(Counter(m['gold_label'] for m in keep))}")
        print(f"gold-evidence slice of that set: {len(gold_keep)}")
    print(f"written to: {out}")


if __name__ == "__main__":
    main()