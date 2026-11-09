"""TF-IDF + Logistic Regression verifier (Prompt07 section 4A). Condition A only in this cycle.

The vectorizer is fit on training inputs only. Prediction is the argmax class probability, with no
threshold tuning.
"""
import hashlib
import json
import time
import warnings
from dataclasses import asdict, dataclass

from sklearn.exceptions import ConvergenceWarning
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression


@dataclass(frozen=True)
class LRConfig:
    ngram_range: tuple = (1, 2)
    min_df: int = 1
    max_features: int = 100000
    max_iter: int = 2000
    random_state: int = 42
    class_weight: object = None
    C: float = 1.0            # sklearn default, recorded explicitly
    solver: str = "lbfgs"     # sklearn default, recorded explicitly

    def config_id(self):
        blob = json.dumps(asdict(self), sort_keys=True).encode()
        return "tfidf-lr-" + hashlib.sha256(blob).hexdigest()[:8]


TEMPLATE = "CLAIM: {claim}\nEVIDENCE: {evidence}"


def make_input(condition, claim_text, evidence_text=None):
    """A: claim text only. B and C: the same fixed template; empty evidence is allowed, None is not."""
    if condition == "A":
        return claim_text
    if condition in ("B", "C"):
        if evidence_text is None:
            raise ValueError(f"condition {condition} needs evidence text (use '' for none)")
        return TEMPLATE.format(claim=claim_text, evidence=evidence_text)
    raise ValueError(f"unknown condition {condition!r}")


def input_hash(text):
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def fit(train_texts, train_labels, cfg):
    """Returns (vectorizer, classifier, info). Vocabulary comes from train_texts only."""
    vec = TfidfVectorizer(ngram_range=cfg.ngram_range, min_df=cfg.min_df, max_features=cfg.max_features)
    X = vec.fit_transform(train_texts)
    clf = LogisticRegression(max_iter=cfg.max_iter, random_state=cfg.random_state,
                             class_weight=cfg.class_weight, C=cfg.C, solver=cfg.solver)
    t0 = time.perf_counter()
    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("always")
        clf.fit(X, train_labels)
    info = {"n_train": len(train_labels), "vocab_size": len(vec.vocabulary_),
            "converged": not any(issubclass(w.category, ConvergenceWarning) for w in caught),
            "n_iter": int(clf.n_iter_.max()), "fit_seconds": round(time.perf_counter() - t0, 3)}
    return vec, clf, info


def predict(vec, clf, texts):
    """Returns (class order, probabilities [n, n_classes], predicted labels, batch seconds)."""
    t0 = time.perf_counter()
    proba = clf.predict_proba(vec.transform(texts))
    seconds = time.perf_counter() - t0
    classes = [str(c) for c in clf.classes_]
    return classes, proba, [classes[i] for i in proba.argmax(axis=1)], seconds