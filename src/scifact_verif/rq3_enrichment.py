"""Prepare a local, text-backed RQ3 annotation packet from official SciFact files.

This module deliberately leaves coder_category and coder_note blank. It reconstructs the
claim, gold rationale context, and exact condition-specific evidence input so a researcher
can read the source material and apply the frozen codebook manually.
"""
from __future__ import annotations

import csv
from pathlib import Path
from typing import Dict, Iterable, List

from scifact_verif.data import load_claims, load_corpus


def parse_ids(value: object) -> List[str]:
    if value is None:
        return []
    raw = str(value).strip()
    if not raw or raw.lower() in {"nan", "none", "null"}:
        return []
    return [part.strip() for part in raw.split(";") if part.strip()]


def _doc_full_text(doc: dict) -> str:
    title = str(doc.get("title", "")).strip()
    abstract = " ".join(str(s).strip() for s in (doc.get("abstract") or []) if str(s).strip())
    return (title + "\n" + abstract).strip()


def _gold_context(claim: dict, corpus: dict) -> str:
    blocks = []
    evidence = claim.get("evidence") or {}
    for doc_id in sorted(evidence, key=lambda x: int(x)):
        annots = evidence[doc_id] or []
        if not annots:
            continue
        doc = corpus.get(str(doc_id))
        if doc is None:
            blocks.append(f"[MISSING GOLD DOCUMENT {doc_id}]")
            continue
        title = str(doc.get("title", "")).strip()
        sents = doc.get("abstract") or []
        rationale_sets = []
        for j, annot in enumerate(annots, 1):
            indices = annot.get("sentences") or []
            selected = []
            for idx in indices:
                if not isinstance(idx, int) or idx < 0 or idx >= len(sents):
                    raise ValueError(f"Invalid rationale sentence index for claim {claim['id']}, doc {doc_id}: {idx}")
                selected.append(str(sents[idx]))
            rationale_sets.append(f"Rationale set {j} ({annot.get('label', 'UNKNOWN')}): " + " ".join(selected))
        blocks.append(f"GOLD DOC {doc_id}: {title}\n" + "\n".join(rationale_sets))
    return "\n\n".join(blocks)


def _gold_abstracts(claim: dict, corpus: dict) -> str:
    blocks = []
    evidence = claim.get("evidence") or {}
    for doc_id in sorted(evidence, key=lambda x: int(x)):
        if not evidence[doc_id]:
            continue
        doc = corpus.get(str(doc_id))
        if doc is None:
            blocks.append(f"[MISSING GOLD DOCUMENT {doc_id}]")
        else:
            blocks.append(f"GOLD DOC {doc_id}\n{_doc_full_text(doc)}")
    return "\n\n".join(blocks)


def _condition_evidence(condition: str, claim: dict, corpus: dict, shown_ids: List[str]) -> str:
    if condition == "A":
        return "[CLAIM-ONLY CONDITION: no evidence text was supplied to the model]"
    if condition == "B":
        pieces = []
        evidence = claim.get("evidence") or {}
        for doc_id in sorted(evidence, key=lambda x: int(x)):
            annots = evidence[doc_id] or []
            if not annots:
                continue
            doc = corpus.get(str(doc_id))
            if doc is None:
                raise ValueError(f"Missing gold evidence document {doc_id} for claim {claim['id']}")
            sents = doc.get("abstract") or []
            # The frozen B implementation supplies the first annotated rationale set only.
            indices = sorted(set(annots[0].get("sentences") or []))
            for idx in indices:
                if not isinstance(idx, int) or idx < 0 or idx >= len(sents):
                    raise ValueError(f"Invalid B rationale sentence index for claim {claim['id']}, doc {doc_id}: {idx}")
            pieces.append(" ".join(str(sents[idx]) for idx in indices))
        return " | ".join(pieces) if pieces else "[NO GOLD EVIDENCE TEXT: empty B input]"
    if condition == "C":
        pieces = []
        for doc_id in shown_ids:
            doc = corpus.get(str(doc_id))
            if doc is None:
                raise ValueError(f"Missing retrieved document {doc_id} for claim {claim['id']}")
            pieces.append(_doc_full_text(doc).replace("\n", " "))
        return " | ".join(pieces) if pieces else "[NO RETRIEVED DOCUMENTS]"
    raise ValueError(f"Unknown condition {condition!r}")


def enrich_rq3_sample(sample_csv: str | Path, claims_dev_jsonl: str | Path,
                      corpus_jsonl: str | Path, prediction_paths: Dict[str, str | Path],
                      output_csv: str | Path, expected_rows: int | None = 50) -> dict:
    """Join RQ3 rows to the actual SciFact text and write a local annotation packet."""
    sample_csv = Path(sample_csv)
    claims_by_id = {int(c["id"]): c for c in load_claims(claims_dev_jsonl)}
    corpus = load_corpus(corpus_jsonl)

    predictions = {}
    for cond, path in prediction_paths.items():
        with open(path, encoding="utf-8", newline="") as f:
            pred_by_id = {int(r["claim_id"]): r for r in csv.DictReader(f)}
        predictions[cond] = pred_by_id

    with open(sample_csv, encoding="utf-8-sig", newline="") as f:
        rows = list(csv.DictReader(f))
    if expected_rows is not None and len(rows) != expected_rows:
        raise ValueError(f"Expected {expected_rows} RQ3 rows, found {len(rows)}")

    output_rows = []
    for row in rows:
        cond = row["condition"]
        claim_id = int(row["claim_id"])
        claim = claims_by_id.get(claim_id)
        if claim is None:
            raise ValueError(f"Claim id {claim_id} not found in supplied claims_dev.jsonl")
        pred = predictions.get(cond, {}).get(claim_id)
        if pred is None:
            raise ValueError(f"Claim id {claim_id} not found in condition {cond} prediction file")

        raw_gold_ids = sorted(str(k) for k, v in (claim.get("evidence") or {}).items() if v)
        sheet_gold_ids = sorted(parse_ids(row.get("gold_evidence_doc_ids")))
        if raw_gold_ids != sheet_gold_ids:
            raise ValueError(f"Gold evidence ID mismatch for {cond}/{claim_id}: sample={sheet_gold_ids}, raw={raw_gold_ids}")

        raw_shown_ids = parse_ids(pred.get("evidence_doc_ids"))
        sheet_shown_ids = parse_ids(row.get("evidence_doc_ids_shown"))
        # B may have an empty string when gold evidence is absent; A is always claim-only.
        if raw_shown_ids != sheet_shown_ids:
            raise ValueError(f"Shown evidence ID mismatch for {cond}/{claim_id}: sample={sheet_shown_ids}, prediction={raw_shown_ids}")

        evidence_text = _condition_evidence(cond, claim, corpus, raw_shown_ids)
        gold_context = _gold_context(claim, corpus)
        gold_abstracts = _gold_abstracts(claim, corpus)
        out = dict(row)
        out.update({
            "claim_text": claim["claim"],
            "model_evidence_text_exact_condition": evidence_text,
            "gold_rationale_context_all_sets": gold_context or "[NO GOLD EVIDENCE ANNOTATED]",
            "gold_evidence_full_abstracts": gold_abstracts or "[NO GOLD EVIDENCE ABSTRACTS]",
            "shown_document_ids_verified": ";".join(raw_shown_ids),
            "gold_document_ids_verified": ";".join(raw_gold_ids),
            "coder_category": "",
            "coder_note": "",
            "annotation_status": "AWAITING_RESEARCHER_TEXT_REVIEW",
        })
        output_rows.append(out)

    extra = ["claim_text", "model_evidence_text_exact_condition", "gold_rationale_context_all_sets",
             "gold_evidence_full_abstracts", "shown_document_ids_verified", "gold_document_ids_verified",
             "annotation_status"]
    fieldnames = list(rows[0].keys()) + extra
    # Coder columns already exist in frozen sample; retain them empty in the packet.
    fieldnames = list(dict.fromkeys(fieldnames))
    output_csv = Path(output_csv)
    output_csv.parent.mkdir(parents=True, exist_ok=True)
    with open(output_csv, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(output_rows)
    return {"rows": len(output_rows), "output": str(output_csv), "claim_text_joined": len(output_rows),
            "coder_category_filled": 0, "coder_note_filled": 0}


def metadata_precheck(sample_csv: str | Path, output_csv: str | Path, expected_rows: int | None = 50) -> dict:
    """Create non-final, deterministic hints for rules derivable from frozen sample metadata.

    It never populates coder_category/coder_note and does not replace reading source text.
    """
    with open(sample_csv, encoding="utf-8-sig", newline="") as f:
        rows = list(csv.DictReader(f))
    if expected_rows is not None and len(rows) != expected_rows:
        raise ValueError(f"Expected {expected_rows} RQ3 rows, found {len(rows)}")
    for row in rows:
        cond = row["condition"]
        empty = str(row.get("evidence_empty", "")).strip() == "1"
        hit = str(row.get("bm25_hit_at_5", "")).strip()
        gold = parse_ids(row.get("gold_evidence_doc_ids"))
        if cond in {"B", "C"} and empty:
            code = "NO_EVIDENCE_SEEN"
            reason = "Frozen rule 1: B/C input evidence is empty. Verify the reconstructed input text before final coding."
        elif cond == "C" and gold and hit == "0":
            code = "RETRIEVAL_MISS"
            reason = "Frozen rule 2: condition C has gold evidence and BM25 hit@5 is zero. Verify source IDs and text."
        else:
            code = "MANUAL_TEXT_REVIEW_REQUIRED"
            reason = "Read the actual claim, shown document text and gold rationale; apply the frozen rule order."
        row["metadata_precheck_suggestion"] = code
        row["metadata_precheck_reason"] = reason
        row["coder_category"] = ""
        row["coder_note"] = ""
        row["final_annotation_status"] = "NOT_CODED"
    fieldnames = list(rows[0].keys())
    output_csv = Path(output_csv)
    output_csv.parent.mkdir(parents=True, exist_ok=True)
    with open(output_csv, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        w.writerows(rows)
    from collections import Counter
    counts = dict(Counter(r["metadata_precheck_suggestion"] for r in rows))
    return {"rows": len(rows), "precheck_counts": counts, "coder_fields_filled": 0, "output": str(output_csv)}