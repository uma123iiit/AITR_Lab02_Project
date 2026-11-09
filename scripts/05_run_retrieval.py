#!/usr/bin/env python
"""Run BM25 and TF-IDF retrieval (top 5) for all train claims and the frozen matched dev claims.

Writes ranked results only. Gold evidence is not read or used here.
"""
import argparse
import csv
import hashlib
import json
import os
import platform
import sys
import time
from datetime import datetime, timezone
from importlib import metadata
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from scifact_verif import data, retrieval  # noqa: E402
from scifact_verif.seed import set_seed  # noqa: E402


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--matched-dir", required=True)
    ap.add_argument("--data-dir", default=None)
    ap.add_argument("--out", default=str(ROOT / "results/retrieval"))
    a = ap.parse_args()

    set_seed(42)
    d = Path(a.data_dir) if a.data_dir else data.find_data_dir(ROOT / "data/raw/scifact")
    corpus = data.load_corpus(d / "corpus.jsonl")
    corpus_sha = data.sha256_file(d / "corpus.jsonl")
    doc_ids = sorted(int(k) for k in corpus)
    texts = [retrieval.doc_text(corpus[str(i)]) for i in doc_ids]

    train = data.load_claims(d / "claims_train.jsonl")
    dev_text = {c["id"]: c["claim"] for c in data.load_claims(d / "claims_dev.jsonl")}
    dev_ids = [int(x) for x in (Path(a.matched_dir) / "matched_claim_ids.txt").read_text().split()]
    queries = [("train", c["id"], c["claim"]) for c in train] + [("dev", i, dev_text[i]) for i in dev_ids]

    retrievers = [retrieval.BM25Retriever(), retrieval.TfidfRetriever()]
    ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    out = Path(a.out) / f"retrieval_{ts}"
    out.mkdir(parents=True, exist_ok=False)

    meta = {"run_id": out.name, "timestamp_utc": ts, "top_k": retrieval.TOP_K, "corpus_sha256": corpus_sha,
            "n_docs": len(doc_ids), "doc_text": "title + ' ' + ' '.join(abstract sentences, original order)",
            "n_queries": {"train": len(train), "dev": len(dev_ids)},
            "query_ids_sha256": hashlib.sha256(json.dumps([[s, i] for s, i, _ in queries]).encode()).hexdigest(),
            "matched_dir": a.matched_dir, "methods": {},
            "hardware": {"platform": platform.platform(), "cpus": os.cpu_count(), "python": sys.version.split()[0]},
            "versions": {p: metadata.version(p) for p in ["rank-bm25", "scikit-learn", "numpy"]}}

    valid = set(doc_ids)
    for r in retrievers:
        index_s = r.fit(doc_ids, texts)
        index_version = f"{r.name}|{r.settings()['implementation']}|corpus={corpus_sha[:12]}"
        t0 = time.perf_counter()
        results = {(s, i): r.search(q) for s, i, q in queries}
        search_s = time.perf_counter() - t0
        # validity and determinism checks
        for key, hits in results.items():
            ids = [x for x, _ in hits]
            if len(ids) != retrieval.TOP_K or len(set(ids)) != len(ids) or not set(ids) <= valid:
                raise SystemExit(f"{r.name}: invalid top-k for {key}: {ids}")
        for s, i, q in queries[:20]:
            if r.search(q) != results[(s, i)]:
                raise SystemExit(f"{r.name}: nondeterministic ranking for {(s, i)}")
        with open(out / f"ranks_{r.name}.csv", "w", newline="", encoding="utf-8") as f:
            w = csv.writer(f)
            w.writerow(["claim_id", "split", "method", "rank", "doc_id", "score", "index_version"])
            for (s, i), hits in results.items():
                for rank, (doc, score) in enumerate(hits, 1):
                    w.writerow([i, s, r.name, rank, doc, f"{score:.8f}", index_version])
        meta["methods"][r.name] = {"settings": r.settings(), "index_version": index_version,
                                   "index_seconds": round(index_s, 3), "search_seconds": round(search_s, 3),
                                   "ms_per_query": round(1000 * search_s / len(queries), 3)}
        first = queries[len(train)]   # first dev claim
        print(f"[{r.name}] index {index_s:.1f}s, {len(queries)} queries in {search_s:.1f}s "
              f"({1000 * search_s / len(queries):.1f} ms/query); top-5 valid, deterministic on 20 repeats")
        print(f"   dev claim {first[1]} top-5 (doc_id, score): {[(x, round(sc, 3)) for x, sc in results[(first[0], first[1])]]}")

    (out / "retrieval_meta.json").write_text(json.dumps(meta, indent=2))
    print(f"corpus n={len(doc_ids)} sha256={corpus_sha[:16]}…  queries: train={len(train)} dev={len(dev_ids)}")
    print(f"written to: {out}")


if __name__ == "__main__":
    main()