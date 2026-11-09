"""Deterministic, metadata-only pre-coding for the frozen RQ3 sample.

Only categories explicitly permitted by the frozen codebook and PC-006 amendment
are assigned here. All text-dependent cases remain uncoded for human review.
"""
from __future__ import annotations

import math
from typing import Any


def _is_blank(value: Any) -> bool:
    if value is None:
        return True
    try:
        if isinstance(value, float) and math.isnan(value):
            return True
    except TypeError:
        pass
    text = str(value).strip()
    return text == "" or text.lower() in {"nan", "none", "null"}


def _as_flag(value: Any) -> int | None:
    if _is_blank(value):
        return None
    try:
        return int(float(value))
    except (TypeError, ValueError):
        return None


def deterministic_rq3_code(row: dict[str, Any]) -> tuple[str, str, str]:
    """Return (category, note, status); do not code text-dependent cases."""
    condition = str(row.get("condition", "")).strip().upper()
    has_gold_document = not _is_blank(row.get("gold_evidence_doc_ids"))
    evidence_empty = _as_flag(row.get("evidence_empty"))
    bm25_hit = _as_flag(row.get("bm25_hit_at_5"))

    # PC-006: claims without any gold evidence document cannot be called
    # retrieval misses or evidence-irrelevant. The amendment directs B/C cases
    # to category 1. For C, non-gold retrieved documents may still be present;
    # the note explicitly records that distinction.
    if condition in {"B", "C"} and not has_gold_document:
        note = (
            "Deterministic PC-006 assignment: this claim has no annotated gold "
            "evidence document, so categories 2 and 3 do not apply and the "
            "amendment directs B/C cases to category 1. For C, retrieved "
            "non-gold documents may still have been supplied; this label means "
            "no gold reference document exists, not necessarily zero input text."
        )
        return "NO_EVIDENCE_SEEN", note, "DETERMINISTIC_METADATA_RULE"

    if condition in {"B", "C"} and evidence_empty == 1:
        note = (
            "Deterministic codebook rule 1: the supplied B/C evidence input is "
            "empty. Assigned from the saved evidence_empty field; no text "
            "judgment was made."
        )
        return "NO_EVIDENCE_SEEN", note, "DETERMINISTIC_METADATA_RULE"

    if condition == "C" and has_gold_document and bm25_hit == 0:
        note = (
            "Deterministic codebook rule 2: at least one gold evidence document "
            "exists but none appears in BM25 top-5 (bm25_hit_at_5=0). Assigned "
            "from saved IDs/rank metadata; no text judgment was made."
        )
        return "RETRIEVAL_MISS", note, "DETERMINISTIC_METADATA_RULE"

    return "", "", "PENDING_TEXT_REVIEW"