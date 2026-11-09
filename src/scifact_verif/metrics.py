"""Evaluation metrics recomputed from saved predictions (Prompt07 section 5).

Zero-division policy: precision, recall and F1 are 0.0 when their denominator is 0. Macro-F1 is the
unweighted mean of per-class F1 over a stated label subset; the confusion matrix always uses the full
label set, so predictions outside the subset count as errors.
"""
import csv
from pathlib import Path

import numpy as np


def read_predictions(path):
    """Returns (rows, class order). Fails if a stored label disagrees with the stored probabilities."""
    path = Path(path)
    with open(path, newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    if not rows:
        raise ValueError(f"{path}: no rows")
    pcols = [c for c in rows[0] if c.startswith("p_")]
    classes = [c[2:] for c in pcols]
    for r in rows:
        p = [float(r[c]) for c in pcols]
        if abs(sum(p) - 1) > 1e-6:
            raise ValueError(f"{path}: probabilities for claim {r['claim_id']} do not sum to 1")
        recomputed = classes[int(np.argmax(p))]
        if recomputed != r["predicted_label"]:
            raise ValueError(f"{path}: claim {r['claim_id']} stored label {r['predicted_label']} "
                             f"!= argmax {recomputed}")
    return rows, classes


def encode(labels, classes):
    index = {c: i for i, c in enumerate(classes)}
    return np.array([index[x] for x in labels], dtype=int)


def confusion(gold, pred, k):
    """Rows are gold classes, columns are predicted classes."""
    return np.bincount(gold * k + pred, minlength=k * k).reshape(k, k)


def per_class(cm):
    """Returns precision, recall, F1 and gold support per class."""
    tp = np.diag(cm).astype(float)
    predicted = cm.sum(axis=0).astype(float)
    support = cm.sum(axis=1).astype(float)
    precision = np.divide(tp, predicted, out=np.zeros_like(tp), where=predicted > 0)
    recall = np.divide(tp, support, out=np.zeros_like(tp), where=support > 0)
    denom = precision + recall
    f1 = np.divide(2 * precision * recall, denom, out=np.zeros_like(tp), where=denom > 0)
    return precision, recall, f1, support.astype(int)


def macro_f1(cm, label_idx):
    return float(per_class(cm)[2][list(label_idx)].mean())


def accuracy(cm):
    return float(np.trace(cm) / cm.sum())


def wilson_interval(successes, n, z=1.96):
    """Wilson score interval for a proportion (95% by default)."""
    if n == 0:
        return (0.0, 0.0)
    p = successes / n
    denom = 1 + z * z / n
    center = (p + z * z / (2 * n)) / denom
    half = z * np.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / denom
    return (float(max(0.0, center - half)), float(min(1.0, center + half)))


def paired_bootstrap(gold, pred_a, pred_b, k, label_idx, n_resamples=2000, seed=42):
    """Macro-F1 difference (b minus a) with a percentile 95% CI.

    Claim indices are resampled once per replicate and applied to both conditions, so pairing is kept.
    """
    rng = np.random.default_rng(seed)
    n = len(gold)

    def score(g, p):
        return macro_f1(confusion(g, p, k), label_idx)

    point = score(gold, pred_b) - score(gold, pred_a)
    diffs = np.empty(n_resamples)
    for i in range(n_resamples):
        s = rng.integers(0, n, n)
        diffs[i] = score(gold[s], pred_b[s]) - score(gold[s], pred_a[s])
    lo, hi = np.percentile(diffs, [2.5, 97.5])
    return {"difference": float(point), "ci95_low": float(lo), "ci95_high": float(hi),
            "n_resamples": n_resamples, "seed": seed, "n_claims": n,
            "ci_excludes_zero": bool(lo > 0 or hi < 0)}