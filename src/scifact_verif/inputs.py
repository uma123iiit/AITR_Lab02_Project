"""Evidence text for conditions B and C (Prompt07 section 4A).

Both builders take plain arguments only. The C builder receives retrieved document ids and the corpus, so it
cannot see gold annotations. This module does not import the data/evidence code.
"""
from scifact_verif import retrieval

SEPARATOR = " | "


def gold_evidence_text(items):
    """Condition B. items: dicts with doc_id and text (the annotated evidence sentences), as from
    data.gold_evidence. Ordered by numeric doc_id. No items gives an empty string."""
    return SEPARATOR.join(i["text"] for i in sorted(items, key=lambda x: int(x["doc_id"])))


def retrieved_evidence_text(doc_ids, corpus):
    """Condition C. doc_ids in rank order; each document is title followed by its abstract sentences."""
    return SEPARATOR.join(retrieval.doc_text(corpus[str(d)]) for d in doc_ids)