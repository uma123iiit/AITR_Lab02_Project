"""BM25 and TF-IDF retrieval over the SciFact corpus (Prompt07 section 4A).

search() takes the claim text and nothing else. This module does not import the data/evidence code, so
gold annotations cannot influence ranking.
"""
import re
import time
from importlib import metadata

import numpy as np
from rank_bm25 import BM25Okapi
from sklearn.feature_extraction.text import TfidfVectorizer

TOP_K = 5
TOKEN_PATTERN = r"\w+"          # applied to lowercased text; no stopword removal, no stemming
_TOKEN_RE = re.compile(TOKEN_PATTERN)
TIE_RULE = "descending score; ties broken by ascending numeric doc_id"


def tokenize(text):
    return _TOKEN_RE.findall(text.lower())


def doc_text(doc):
    """Title followed by abstract sentences in original order."""
    return doc["title"] + " " + " ".join(doc["abstract"])


def rank_top_k(scores, doc_ids, k=TOP_K):
    """Top-k (doc_id, score) pairs. doc_ids is an integer array aligned with scores."""
    order = np.lexsort((doc_ids, -scores))[:k]
    return [(int(doc_ids[i]), float(scores[i])) for i in order]


class BM25Retriever:
    name = "bm25"

    def __init__(self, k1=1.5, b=0.75, epsilon=0.25):
        self.k1, self.b, self.epsilon = k1, b, epsilon

    def fit(self, doc_ids, texts):
        self.doc_ids = np.asarray(doc_ids, dtype=np.int64)
        t0 = time.perf_counter()
        self._bm25 = BM25Okapi([tokenize(t) for t in texts], k1=self.k1, b=self.b, epsilon=self.epsilon)
        return time.perf_counter() - t0

    def search(self, query, k=TOP_K):
        return rank_top_k(np.asarray(self._bm25.get_scores(tokenize(query))), self.doc_ids, k)

    def settings(self):
        return {"method": self.name, "implementation": f"rank-bm25=={metadata.version('rank-bm25')} BM25Okapi",
                "k1": self.k1, "b": self.b, "epsilon": self.epsilon, "tokenizer": TOKEN_PATTERN,
                "lowercase": True, "stopwords": None, "stemming": None, "tie_rule": TIE_RULE}


class TfidfRetriever:
    name = "tfidf"

    def __init__(self):
        self._vec = TfidfVectorizer(ngram_range=(1, 2), norm="l2", lowercase=True, min_df=1,
                                    token_pattern=r"(?u)\b\w+\b")

    def fit(self, doc_ids, texts):
        self.doc_ids = np.asarray(doc_ids, dtype=np.int64)
        t0 = time.perf_counter()
        self._matrix = self._vec.fit_transform(texts)          # corpus text only
        return time.perf_counter() - t0

    def search(self, query, k=TOP_K):
        q = self._vec.transform([query])
        return rank_top_k((self._matrix @ q.T).toarray().ravel(), self.doc_ids, k)   # cosine: both L2-normalised

    def settings(self):
        return {"method": self.name, "implementation": f"scikit-learn=={metadata.version('scikit-learn')} TfidfVectorizer",
                "ngram_range": [1, 2], "norm": "l2", "lowercase": True, "min_df": 1,
                "token_pattern": r"(?u)\b\w+\b", "vocabulary_size": len(self._vec.vocabulary_),
                "tie_rule": TIE_RULE}