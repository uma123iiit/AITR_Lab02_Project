"""Data loading, validation and eligibility for the SciFact A/B/C study (Prompt07 sections 3 and 4A).

Standard library only. Gold evidence is exposed only through gold_evidence(); nothing here feeds
labels or evidence into retrieval.
"""
import csv
import hashlib
import json
import re
from collections import Counter
from pathlib import Path

SUPPORT, CONTRADICT, NEI = "SUPPORT", "CONTRADICT", "NOT_ENOUGH_INFO"
RAW_LABELS = {SUPPORT, CONTRADICT}
POLICIES = ("all_labeled", "evidence_only")

UNLABELED = "UNLABELED_NO_EVIDENCE_FIELD"
UNKNOWN_LABEL = "UNKNOWN_RAW_LABEL"
MIXED = "MIXED_EVIDENCE_LABELS"
DUPLICATE_ID = "DUPLICATE_CLAIM_ID"
DOC_MISSING = "EVIDENCE_DOC_NOT_IN_CORPUS"
BAD_INDEX = "EVIDENCE_SENTENCE_INDEX_OUT_OF_RANGE"
NEI_POLICY = "NEI_NO_GOLD_EVIDENCE_EXCLUDED_BY_POLICY"
NEAR_DUP = "NEAR_DUPLICATE_OF_TRAIN_CLAIM"

NEAR_DUP_JACCARD = 0.9


def read_jsonl(path):
    rows = []
    with open(path, encoding="utf-8") as f:
        for n, line in enumerate(f, 1):
            if not line.strip():
                continue
            try:
                rows.append(json.loads(line))
            except json.JSONDecodeError as e:
                raise ValueError(f"{path}:{n}: invalid JSON ({e})") from e
    return rows


def sha256_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def find_data_dir(root):
    corpus = next(Path(root).rglob("corpus.jsonl"), None)
    if corpus is None:
        raise FileNotFoundError(f"no corpus.jsonl under {root}; run scripts/01_download_data.sh")
    return corpus.parent


def load_corpus(path):
    """Returns {str(doc_id): doc}. Keys are strings because claim evidence keys are strings."""
    docs = {}
    for d in read_jsonl(path):
        key = str(d["doc_id"])
        if key in docs:
            raise ValueError(f"duplicate corpus doc_id {key}")
        docs[key] = d
    return docs


def load_claims(path):
    claims = read_jsonl(path)
    for c in claims:
        for k in ("id", "claim"):
            if k not in c:
                raise ValueError(f"{path}: claim record missing '{k}': {str(c)[:120]}")
    return claims


def derive_gold_label(claim):
    """Returns (label or None, reasons).

    Rule: no 'evidence' key -> unlabeled; empty evidence -> NOT_ENOUGH_INFO; exactly one distinct raw
    label -> that label; more than one -> excluded (MIXED); any value outside SUPPORT/CONTRADICT -> excluded.
    """
    if "evidence" not in claim:
        return None, [UNLABELED]
    labels = {e.get("label") for items in claim["evidence"].values() for e in items}
    if not labels:
        return NEI, []
    if labels - RAW_LABELS:
        return None, [UNKNOWN_LABEL]
    if len(labels) > 1:
        return None, [MIXED]
    return next(iter(labels)), []


def gold_evidence(claim, corpus, rationale="first"):
    """Returns (items, reasons). Each item: doc_id (str), sentence_indices (sorted), n_rationale_sets, text.

    rationale: "first" uses the first annotated rationale set of each document in file order (frozen choice,
    PC-004); "union" uses every set. Index validity is always checked over all sets.

    For evaluation, condition B and the audit only. Never pass this to retrieval.
    """
    if rationale not in ("first", "union"):
        raise ValueError(f"rationale must be 'first' or 'union', got {rationale!r}")
    items, reasons = [], set()
    for doc_id, annots in (claim.get("evidence") or {}).items():
        doc = corpus.get(str(doc_id))
        if doc is None:
            reasons.add(DOC_MISSING)
            continue
        if not annots:
            continue
        sents = doc["abstract"]
        every = sorted({i for a in annots for i in a["sentences"]})
        if any(not isinstance(i, int) or i < 0 or i >= len(sents) for i in every):
            reasons.add(BAD_INDEX)
            continue
        idx = sorted(set(annots[0]["sentences"])) if rationale == "first" else every
        items.append({"doc_id": str(doc_id), "sentence_indices": idx, "n_rationale_sets": len(annots),
                      "text": " ".join(sents[i] for i in idx)})
    return items, sorted(reasons)


def build_matched_set(claims, corpus, policy, holdout_ids=frozenset()):
    """Returns (matched rows, exclusion rows). len(matched) + len(excluded) == len(claims), always.

    holdout_ids: claim ids to hold out of evaluation (near-duplicates of train claims)."""
    if policy not in POLICIES:
        raise ValueError(f"policy must be one of {POLICIES}, got {policy!r}")
    id_counts = Counter(c["id"] for c in claims)
    matched, excluded = [], []
    for c in claims:
        label, reasons = derive_gold_label(c)
        reasons = list(reasons)
        if id_counts[c["id"]] > 1:
            reasons.append(DUPLICATE_ID)
        items, ev_reasons = gold_evidence(c, corpus)
        reasons += ev_reasons
        if label == NEI and policy == "evidence_only":
            reasons.append(NEI_POLICY)
        if c["id"] in holdout_ids:
            reasons.append(NEAR_DUP)
        if reasons:
            excluded.append({"claim_id": c["id"], "reason_codes": "|".join(reasons)})
            continue
        matched.append({"claim_id": c["id"], "gold_label": label, "n_gold_docs": len(items),
                        "b_evidence_empty": not items, "claim": c["claim"]})
    if len(matched) + len(excluded) != len(claims):
        raise AssertionError("claims were dropped without an exclusion row")
    return matched, excluded


def rq2_eligible_ids(matched):
    """RQ2 Recall@5 denominator: matched claims with at least one usable gold evidence document."""
    return [m["claim_id"] for m in matched if m["n_gold_docs"] >= 1]


def _tokens(text):
    return set(re.sub(r"[^a-z0-9 ]", " ", text.lower()).split())


def near_duplicates(train_claims, dev_claims, threshold=NEAR_DUP_JACCARD):
    """Dev claims whose normalised text equals, or has token-set Jaccard >= threshold with, a train claim."""
    train = [(c["id"], _tokens(c["claim"])) for c in train_claims]
    out = []
    for d in dev_claims:
        dt = _tokens(d["claim"])
        for tid, tt in train:
            union = dt | tt
            j = len(dt & tt) / len(union) if union else 0.0
            if j >= threshold:
                out.append({"dev_id": d["id"], "train_id": tid, "jaccard": round(j, 3)})
    return out


def twin_dev_ids(train_claims, dev_claims, threshold):
    """Ids of dev claims that have at least one train claim at token-set Jaccard >= threshold."""
    return {p["dev_id"] for p in near_duplicates(train_claims, dev_claims, threshold)}


def audit(data_dir):
    """Policy-independent audit of the raw files. Returns a JSON-serialisable dict."""
    d = Path(data_dir)
    corpus = load_corpus(d / "corpus.jsonl")
    report = {"data_dir": str(d), "corpus_n": len(corpus),
              "corpus_doc_id_types": sorted({type(x["doc_id"]).__name__ for x in corpus.values()}),
              "file_sha256": {}, "splits": {}}
    for name in ["corpus.jsonl", "claims_train.jsonl", "claims_dev.jsonl", "claims_test.jsonl"]:
        if (d / name).exists():
            report["file_sha256"][name] = sha256_file(d / name)
    splits = {}
    for s in ["train", "dev", "test"]:
        p = d / f"claims_{s}.jsonl"
        if not p.exists():
            continue
        cl = load_claims(p)
        splits[s] = cl
        ids = [c["id"] for c in cl]
        info = {"n": len(cl), "id_types": sorted({type(i).__name__ for i in ids}),
                "duplicate_ids": len(ids) - len(set(ids)),
                "keys": dict(Counter(k for c in cl for k in c))}
        if s != "test":
            labels = [derive_gold_label(c) for c in cl]
            info["gold_label_counts"] = dict(Counter(lab if lab else "|".join(r) for lab, r in labels))
            info["raw_label_values_seen"] = sorted({e.get("label") for c in cl
                                                    for items in c["evidence"].values() for e in items})
            info["with_nonempty_evidence"] = sum(1 for c in cl if c["evidence"])
            info["evidence_doc_ids_not_in_corpus"] = sum(1 for c in cl for k in c["evidence"] if k not in corpus)
            info["evidence_key_types"] = sorted({type(k).__name__ for c in cl for k in c["evidence"]})
            info["bad_sentence_index_claims"] = sum(
                1 for c in cl if BAD_INDEX in gold_evidence(c, corpus)[1])
        report["splits"][s] = info
    if "train" in splits and "dev" in splits:
        report["near_duplicates_train_dev"] = near_duplicates(splits["train"], splits["dev"])
    return report


def label_map(train_claims):
    labels = sorted({derive_gold_label(c)[0] for c in train_claims} - {None})
    return {"rule": "no 'evidence' key -> unlabeled; empty evidence dict -> NOT_ENOUGH_INFO; one distinct "
                    "raw label (SUPPORT|CONTRADICT) -> that label; mixed or unknown -> excluded",
            "labels_in_train": labels,
            "class_order_note": "alphabetical, equal to sklearn LogisticRegression.classes_; "
                                "verify against clf.classes_ at fit time and save in run metadata"}


def write_artifacts(out_dir, policy, split, matched, excluded, tag=""):
    out = Path(out_dir) / f"{split}_{policy}{tag}"
    out.mkdir(parents=True, exist_ok=True)
    (out / "matched_claim_ids.txt").write_text("".join(f"{m['claim_id']}\n" for m in matched))
    with open(out / "matched_claims.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["claim_id", "gold_label", "n_gold_docs", "b_evidence_empty", "claim"])
        w.writeheader()
        w.writerows(matched)
    with open(out / "exclusions.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["claim_id", "reason_codes"])
        w.writeheader()
        w.writerows(excluded)
    (out / "rq2_eligible_claim_ids.txt").write_text("".join(f"{i}\n" for i in rq2_eligible_ids(matched)))
    return out