#!/usr/bin/env python
"""Independent audit of the baseline pipeline. Deliberately does NOT import scifact_verif: every check
recomputes from the raw files, the saved outputs, and plain scikit-learn/numpy.

Status per check: PASS / WARN / FAIL / INFO. A PASS means the check ran and agreed, not that the design is right.
"""
import csv
import json
import math
import re
import sys
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path

import joblib
import numpy as np
import yaml
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, f1_score

ROOT = Path(__file__).resolve().parents[1]
LOG = []
PAPER_2A = {"train": {"SUPPORT": 332, "NOT_ENOUGH_INFO": 304, "CONTRADICT": 173},
            "dev": {"SUPPORT": 124, "NOT_ENOUGH_INFO": 112, "CONTRADICT": 64}}   # Wadden et al. 2020, Table 2a
CLASSES = ["CONTRADICT", "NOT_ENOUGH_INFO", "SUPPORT"]
TOL = 1e-9


def rec(name, status, detail):
    LOG.append({"check": name, "status": status, "detail": detail})
    print(f"[{status:4}] {name} :: {detail}", flush=True)


def jl(p):
    return [json.loads(x) for x in open(p, encoding="utf-8") if x.strip()]


def label(c):
    labs = {e["label"] for v in c["evidence"].values() for e in v}
    return "NOT_ENOUGH_INFO" if not labs else ("MIXED" if len(labs) > 1 else next(iter(labs)))


def ids(p):
    return [int(x) for x in Path(p).read_text().split()]


dd = next((ROOT / "data/raw/scifact").rglob("corpus.jsonl")).parent
corpus = jl(dd / "corpus.jsonl")
train, dev, test = (jl(dd / f"claims_{s}.jsonl") for s in ("train", "dev", "test"))
M = ROOT / "results/audit/dev_all_labeled_nd-holdout"
matched = ids(M / "matched_claim_ids.txt")
gold_slice = ids(M / "rq2_eligible_claim_ids.txt")
dev_by = {c["id"]: c for c in dev}

# ---- D1 data vs the original paper and official docs
for s, cl in (("train", train), ("dev", dev)):
    got = dict(Counter(label(c) for c in cl))
    rec(f"D1 label counts {s} vs paper Table 2a", "PASS" if got == PAPER_2A[s] else "FAIL", f"repo={got} paper={PAPER_2A[s]}")
rec("D1 corpus size and test split", "PASS" if len(corpus) == 5183 and len(test) == 300 and all("evidence" not in c for c in test) else "FAIL",
    f"corpus={len(corpus)} (paper 5183); test n={len(test)} without evidence field (paper: 100/100/100, labels private)")
viol = sum(1 for c in train + dev for k in c["evidence"] if int(k) not in c["cited_doc_ids"])
rec("D2 evidence documents are cited documents", "PASS" if viol == 0 else "WARN", f"violations={viol} (docs.md does not state this as a rule; checked empirically)")
mixed = sum(1 for c in train + dev if label(c) == "MIXED")
rec("D3 claims with mixed SUPPORT/CONTRADICT across documents", "PASS" if mixed == 0 else "WARN", f"{mixed} (paper Table 2b: 63 claims have 2+ evidence abstracts)")
multi_doc = sum(1 for c in train + dev if len(c["evidence"]) > 1)
rec("D3 claims with 2+ evidence documents", "INFO", f"{multi_doc} of {len(train) + len(dev)} train+dev claims")

# ---- D4 how condition B turns annotations into text (union of all rationale sets)
mc = [dev_by[i] for i in matched if dev_by[i]["evidence"]]
multi_set = sum(1 for c in mc if any(len(v) > 1 for v in c["evidence"].values()))
union = [sum(len({i for e in v for i in e["sentences"]}) for v in c["evidence"].values()) for c in mc]
first = [sum(len(v[0]["sentences"]) for v in c["evidence"].values()) for c in mc]
rec("D4 B input = union of ALL rationale sets per document", "WARN",
    f"{multi_set}/{len(mc)} matched dev claims with evidence have 2+ rationale sets in a document; mean evidence sentences "
    f"union={np.mean(union):.2f} vs first-rationale-only={np.mean(first):.2f}. Original paper trains on gold rationales; "
    f"which alternative to use is a methodological choice not fixed in the protocol")

# ---- A1/A2 independent recomputation of metrics from saved predictions
pred_dir = sorted((ROOT / "results/predictions").glob("A_*"))[-1]
rows = list(csv.DictReader(open(pred_dir / "predictions.csv", encoding="utf-8")))
g = [r["gold_label"] for r in rows]
p = [r["predicted_label"] for r in rows]
ev_dir = [d for d in sorted((ROOT / "results/metrics").glob("eval_*")) if "sensitivity" in (d / "metrics.json").read_text()][-1]
res = json.loads((ev_dir / "metrics.json").read_text())["results"]["A"]
slices = {"primary_matched": (matched, CLASSES), "gold_evidence_slice": (gold_slice, ["SUPPORT", "CONTRADICT"]),
          "sensitivity_j0.7_matched": (ids(M / "sensitivity_j0.7_matched_claim_ids.txt"), CLASSES),
          "sensitivity_j0.7_gold_evidence_slice": (ids(M / "sensitivity_j0.7_gold_evidence_claim_ids.txt"), ["SUPPORT", "CONTRADICT"])}
worst = 0.0
for name, (sid, labs) in slices.items():
    keep = [i for i, r in enumerate(rows) if int(r["claim_id"]) in set(sid)]
    gg, pp = [g[i] for i in keep], [p[i] for i in keep]
    f1 = f1_score(gg, pp, labels=labs, average="macro", zero_division=0)
    acc = accuracy_score(gg, pp)
    worst = max(worst, abs(f1 - res[name]["macro_f1"]), abs(acc - res[name]["accuracy"]))
    assert len(keep) == res[name]["n"], (name, len(keep), res[name]["n"])
rec("A1 metrics recomputed with sklearn from predictions.csv", "PASS" if worst < TOL else "FAIL", f"max abs diff vs metrics.json over 4 slices = {worst:.2e} (run {ev_dir.name})")

# ---- A2 independent refit of condition A
lab = lambda c: label(c)
Xtr, ytr = [c["claim"] for c in train], [lab(c) for c in train]
vec = TfidfVectorizer(ngram_range=(1, 2), min_df=1, max_features=100000)
Atr = vec.fit_transform(Xtr)
clf = LogisticRegression(max_iter=2000, random_state=42, C=1.0, solver="lbfgs").fit(Atr, ytr)
Pi = clf.predict_proba(vec.transform([dev_by[int(r["claim_id"])]["claim"] for r in rows]))
Ps = np.array([[float(r[f"p_{c}"]) for c in CLASSES] for r in rows])
diff = float(np.abs(Pi - Ps).max())
rec("A2 independent refit reproduces saved condition-A probabilities", "PASS" if diff < 1e-7 and list(clf.classes_) == CLASSES else "FAIL",
    f"max abs diff={diff:.2e} (saved probabilities have 8 decimals); class order {list(clf.classes_)}")
saved = joblib.load(pred_dir / "model.joblib")["vectorizer"]
v_all = TfidfVectorizer(ngram_range=(1, 2), min_df=1, max_features=100000).fit([c["claim"] for c in train + dev])
same = set(saved.vocabulary_) == set(vec.vocabulary_)
rec("A3 saved vocabulary comes from train claims only", "PASS" if same and len(v_all.vocabulary_) > len(vec.vocabulary_) else "FAIL",
    f"saved vocab={len(saved.vocabulary_)} == train-only refit; train+dev fit would give {len(v_all.vocabulary_)} (so the check can detect dev leakage)")

# ---- S1 chance and trivial baselines on the matched dev set
dev_y = [lab(dev_by[i]) for i in matched]
maj = Counter(dev_y).most_common(1)[0][0]
maj_f1 = f1_score(dev_y, [maj] * len(dev_y), labels=CLASSES, average="macro", zero_division=0)
Xdev = vec.transform([dev_by[i]["claim"] for i in matched])
f1s, accs = [], []
for seed in range(20):
    ys = list(np.random.RandomState(seed).permutation(ytr))
    pr = LogisticRegression(max_iter=2000, random_state=42).fit(Atr, ys).predict(Xdev)
    f1s.append(f1_score(dev_y, pr, labels=CLASSES, average="macro", zero_division=0))
    accs.append(accuracy_score(dev_y, pr))
a_f1, a_acc = res["primary_matched"]["macro_f1"], res["primary_matched"]["accuracy"]
rec("S1 trivial baselines on the 286 matched dev claims", "INFO",
    f"majority class ({maj}): accuracy={Counter(dev_y)[maj] / len(dev_y):.3f} macro-F1={maj_f1:.3f} | shuffled train labels, 20 seeds: "
    f"macro-F1={np.mean(f1s):.3f}±{np.std(f1s):.3f} accuracy={np.mean(accs):.3f}±{np.std(accs):.3f} | condition A: macro-F1={a_f1:.3f} accuracy={a_acc:.3f}")
rec("S1 condition A vs shuffled-label control", "PASS" if a_f1 > np.mean(f1s) + 2 * np.std(f1s) else "WARN",
    f"A macro-F1 is {(a_f1 - np.mean(f1s)) / max(np.std(f1s), 1e-9):.1f} SDs above the shuffled-label mean (a pipeline that learns nothing should sit near it)")

# ---- R1 independent BM25 (rank_bm25 Okapi formula re-derived) vs saved rankings
tok = lambda t: re.findall(r"\w+", t.lower())
docs = sorted(corpus, key=lambda d: d["doc_id"])
dids = np.array([d["doc_id"] for d in docs])
dtoks = [tok(d["title"] + " " + " ".join(d["abstract"])) for d in docs]
dl = np.array([len(t) for t in dtoks], float)
avgdl = dl.mean()
post, df = defaultdict(dict), Counter()
for i, t in enumerate(dtoks):
    for w, c in Counter(t).items():
        post[w][i] = c
        df[w] += 1
N, k1, b, eps = len(docs), 1.5, 0.75, 0.25
idf = {w: math.log(N - n + 0.5) - math.log(n + 0.5) for w, n in df.items()}
avg_idf = sum(idf.values()) / len(idf)
neg = [w for w, v in idf.items() if v < 0]
for w in neg:
    idf[w] = eps * avg_idf
ranks = defaultdict(list)
for r in csv.DictReader(open(sorted((ROOT / "results/retrieval").glob("retrieval_*"))[-1] / "ranks_bm25.csv", encoding="utf-8")):
    if r["split"] == "dev":
        ranks[int(r["claim_id"])].append((int(r["rank"]), int(r["doc_id"]), float(r["score"])))
bad_ids = bad_score = 0
for cid in matched[:60]:
    s = np.zeros(N)
    for q in tok(dev_by[cid]["claim"]):
        for i, tf in post.get(q, {}).items():
            s[i] += idf[q] * tf * (k1 + 1) / (tf + k1 * (1 - b + b * dl[i] / avgdl))
    top = np.lexsort((dids, -s))[:5]
    saved_top = sorted(ranks[cid])
    bad_ids += [int(dids[i]) for i in top] != [d for _, d, _ in saved_top]
    bad_score += max(abs(float(s[i]) - sc) for i, (_, _, sc) in zip(top, saved_top)) > 1e-6
rec("R1 independent BM25 reproduces saved top-5 ids and scores (60 dev claims)", "PASS" if bad_ids == 0 and bad_score == 0 else "FAIL",
    f"mismatched id lists={bad_ids}, mismatched scores={bad_score}; terms with negative IDF (in >half of docs) replaced by "
    f"{eps}*average_idf={eps * avg_idf:.4f}: {len(neg)} terms (library behaviour, e.g. {sorted(neg)[:6]})")

# ---- R2 Recall@5 recomputed from saved rankings and raw gold ids
rm = json.loads((sorted((ROOT / "results/retrieval_eval").glob("retrieval_eval_*"))[-1] / "retrieval_metrics.json").read_text())
for m in ("bm25", "tfidf"):
    rk = defaultdict(list)
    for r in csv.DictReader(open(sorted((ROOT / "results/retrieval").glob("retrieval_*"))[-1] / f"ranks_{m}.csv", encoding="utf-8")):
        if r["split"] == "dev":
            rk[int(r["claim_id"])].append(int(r["doc_id"]))
    hits = sum(1 for i in gold_slice if {int(k) for k in dev_by[i]["evidence"]} & set(rk[i]))
    ok = hits == rm["results"][m]["hits"] and len(gold_slice) == rm["results"][m]["denominator"]
    rec(f"R2 Recall@5 {m} recomputed independently", "PASS" if ok else "FAIL", f"{hits}/{len(gold_slice)} vs saved {rm['results'][m]['hits']}/{rm['results'][m]['denominator']}")

# ---- P1 provenance consistency
meta = json.loads((pred_dir / "run_meta.json").read_text())
draft = yaml.safe_load((ROOT / "configs/primary_frozen.draft.yaml").read_text())
rmeta = json.loads((sorted((ROOT / "results/retrieval").glob("retrieval_*"))[-1] / "retrieval_meta.json").read_text())
import hashlib
sha = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()
ok = (meta["config_id"] == draft["verifier"]["config_id"] and meta["matched_ids_sha256"] == draft["matched_set"]["ids_sha256"]
      and rmeta["corpus_sha256"] == sha(dd / "corpus.jsonl") == draft["retrieval"]["corpus_sha256"])
rec("P1 config id, matched-ids hash and corpus hash agree across run, retrieval and freeze draft", "PASS" if ok else "FAIL", f"config {meta['config_id']}")
conds = sorted({d.name.split("_")[0] for d in (ROOT / "results/predictions").iterdir()})
rec("P2 conditions with saved predictions", "WARN" if conds != ["A", "B", "C"] else "PASS", f"{conds}; B and C not run yet, so B/C code paths are untested end to end")
rec("P3 condition A predates the freeze gate", "WARN", "A was run before configs/primary_frozen.yaml existed; the frozen rerun must reproduce it exactly (check below)")

out = ROOT / "results/validation"
out.mkdir(parents=True, exist_ok=True)
ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
(out / f"baseline_audit_{ts}.json").write_text(json.dumps({"timestamp_utc": ts, "checks": LOG}, indent=2))
print(f"\nsummary: {dict(Counter(x['status'] for x in LOG))}  log: {out / ('baseline_audit_' + ts + '.json')}")
sys.exit(1 if any(x["status"] == "FAIL" for x in LOG) else 0)