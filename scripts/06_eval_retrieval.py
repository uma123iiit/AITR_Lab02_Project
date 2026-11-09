#!/usr/bin/env python
"""Join saved top-5 rankings with gold evidence document ids and compute Recall@5 (dev, RQ2 denominator).

Gold ids are read here only, after retrieval has been saved. Hit = at least one gold evidence document in the top 5.
"""
import argparse
import csv
import json
import sys
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from scifact_verif import data, metrics  # noqa: E402

METHODS = ["bm25", "tfidf"]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--ranks-dir", required=True, help="results/retrieval/retrieval_<ts>")
    ap.add_argument("--matched-dir", required=True)
    ap.add_argument("--data-dir", default=None)
    ap.add_argument("--out", default=str(ROOT / "results/retrieval_eval"))
    a = ap.parse_args()

    d = Path(a.data_dir) if a.data_dir else data.find_data_dir(ROOT / "data/raw/scifact")
    matched = Path(a.matched_dir)
    denom_ids = [int(x) for x in (matched / "rq2_eligible_claim_ids.txt").read_text().split()]
    with open(matched / "matched_claims.csv", encoding="utf-8") as f:
        label = {int(r["claim_id"]): r["gold_label"] for r in csv.DictReader(f)}
    dev = {c["id"]: c for c in data.load_claims(d / "claims_dev.jsonl")}
    corpus = data.load_corpus(d / "corpus.jsonl")
    gold = {i: {int(k) for k in dev[i]["evidence"]} for i in denom_ids}
    if any(not g for g in gold.values()):
        raise SystemExit("an RQ2-eligible claim has no gold evidence document")
    if any(str(x) not in corpus for g in gold.values() for x in g):
        raise SystemExit("a gold document id is missing from the corpus")

    ranks_dir = Path(a.ranks_dir)
    meta = json.loads((ranks_dir / "retrieval_meta.json").read_text())
    ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    out = Path(a.out) / f"retrieval_eval_{ts}"
    out.mkdir(parents=True, exist_ok=False)

    per_claim, summary, hit_sets = [], {}, {}
    for m in METHODS:
        top = defaultdict(list)
        with open(ranks_dir / f"ranks_{m}.csv", encoding="utf-8") as f:
            for r in csv.DictReader(f):
                if r["split"] == "dev":
                    top[int(r["claim_id"])].append((int(r["rank"]), int(r["doc_id"])))
        missing = [i for i in denom_ids if i not in top]
        if missing:
            raise SystemExit(f"{m}: no ranking for {len(missing)} eligible claims")
        hits, by_label = set(), defaultdict(lambda: [0, 0])
        first_ranks = []
        for i in denom_ids:
            ranked = sorted(top[i])
            hit_ranks = [rk for rk, doc in ranked if doc in gold[i]]
            hit = bool(hit_ranks)
            if hit:
                hits.add(i)
                first_ranks.append(hit_ranks[0])
            by_label[label[i]][0] += hit
            by_label[label[i]][1] += 1
            per_claim.append({"claim_id": i, "method": m, "gold_label": label[i], "n_gold_docs": len(gold[i]),
                              "hit_at_5": int(hit), "first_gold_rank": hit_ranks[0] if hit else ""})
        n, h = len(denom_ids), len(hits)
        lo, hi = metrics.wilson_interval(h, n)
        hit_sets[m] = hits
        summary[m] = {"recall_at_5": h / n, "hits": h, "denominator": n, "wilson95": [lo, hi],
                      "by_gold_label": {k: {"hits": v[0], "n": v[1], "recall_at_5": v[0] / v[1]} for k, v in by_label.items()},
                      "first_gold_rank_counts_among_hits": dict(sorted(Counter(first_ranks).items()))}
        print(f"[{m}] Recall@5 = {h}/{n} = {h / n:.4f}  (Wilson 95%: {lo:.3f}-{hi:.3f})")
        for k, v in sorted(by_label.items()):
            print(f"   gold {k}: {v[0]}/{v[1]} = {v[0] / v[1]:.3f}")
        print(f"   rank of first gold doc among hits: {dict(sorted(Counter(first_ranks).items()))}")

    both = hit_sets["bm25"] & hit_sets["tfidf"]
    only_b, only_t = hit_sets["bm25"] - hit_sets["tfidf"], hit_sets["tfidf"] - hit_sets["bm25"]
    neither = set(denom_ids) - hit_sets["bm25"] - hit_sets["tfidf"]
    overlap = {"both": len(both), "bm25_only": len(only_b), "tfidf_only": len(only_t), "neither": len(neither)}
    print(f"overlap of hits: {overlap}")

    with open(out / "per_claim_hits.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(per_claim[0]))
        w.writeheader()
        w.writerows(per_claim)
    (out / "retrieval_metrics.json").write_text(json.dumps({
        "note": "Development-set retrieval evaluation; claims with >=1 gold evidence doc among the frozen matched set. "
                "Document-level hit, not sentence-level sufficiency.",
        "ranks_dir": str(ranks_dir), "retrieval_run_id": meta["run_id"], "corpus_sha256": meta["corpus_sha256"],
        "denominator": len(denom_ids), "results": summary, "hit_overlap": overlap,
        "runtime": {m: {k: v for k, v in meta["methods"][m].items() if k.endswith("seconds") or k == "ms_per_query"}
                    for m in METHODS}}, indent=2))

    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    fig, ax = plt.subplots(figsize=(3.8, 3.4))
    vals = [summary[m]["recall_at_5"] for m in METHODS]
    errs = [[summary[m]["recall_at_5"] - summary[m]["wilson95"][0] for m in METHODS],
            [summary[m]["wilson95"][1] - summary[m]["recall_at_5"] for m in METHODS]]
    ax.bar(["BM25", "TF-IDF"], vals, yerr=errs, capsize=4, color=["#3b7ea1", "#8a8a8a"])
    ax.set_ylim(0, 1)
    ax.set_ylabel("Recall@5")
    ax.set_title(f"Dev, n={len(denom_ids)} claims with gold evidence", fontsize=9)
    fig.tight_layout()
    fig.savefig(out / "recall_at_5.png", dpi=150)
    plt.close(fig)
    print(f"written to: {out}")


if __name__ == "__main__":
    main()