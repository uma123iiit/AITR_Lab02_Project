# RQ3 text review provenance — 2 November 2026

## Purpose and status

This log records the external source material used for an **AI-assisted preliminary annotation** of the 50 frozen RQ3 claim-condition pairs. It is not a claim that the user's original raw SciFact files were uploaded or that the public mirror is byte-identical to the archived run corpus.

## Claim records

- Public mirror: `openai/openai-cookbook`, file `examples/data/scifact_claims.jsonl`, default-branch URL: https://github.com/openai/openai-cookbook/blob/main/examples/data/scifact_claims.jsonl
- Retrieved file contained 300 JSONL claim records. The 50 sampled condition–claim rows correspond to 45 unique claim IDs because five claim IDs occur in more than one condition.
- The retrieved records supplied claim text, gold-evidence document IDs, evidence labels, and sentence indices. The sample's gold evidence IDs and gold labels were checked against these record fields during the review.
- This is a third-party public mirror, not an immutable official SciFact download. It is used for text inspection only.

## Corpus/abstract records

- Public mirror: `Aki-max-min/novatel-telecom-rag-unstructured`, pinned repository commit `f2249a67bc0eb9f988f6c1954dd77fad745b955c`.
- Individual documents were retrieved from `data/processed/real_world/scifact/documents/SCIFACT_<doc_id>.json`.
- Each record identifies its source as `BEIR/SciFact` and supplies a title and abstract-like `content` field.
- These abstracts were used to inspect gold evidence documents and selected retrieved top-five documents where NEI claims required context review.
- The document mirror is **not confirmed byte-identical** to `/content/.../corpus.jsonl` used in the historic experiment. Several record/annotation-text tensions (notably claim 593 and claim 343) were therefore labelled ambiguous rather than resolved by assumption.

## Exact source URLs

- Claims mirror: https://github.com/openai/openai-cookbook/blob/main/examples/data/scifact_claims.jsonl
- Corpus mirror directory: https://github.com/Aki-max-min/novatel-telecom-rag-unstructured/tree/f2249a67bc0eb9f988f6c1954dd77fad745b955c/data/processed/real_world/scifact/documents
- Official SciFact repository and release instructions: https://github.com/allenai/scifact

## Annotation protocol

- Original frozen sample `rq3_sample.csv` and codebook were not overwritten.
- One primary code was assigned to each row using the frozen seven-category codebook and PC-006 amendment.
- First-rule order was respected for the two metadata-deterministic cases: B/303 → `NO_EVIDENCE_SEEN`; C/756 → `RETRIEVAL_MISS`.
- The other 48 assignments are preliminary text-based judgments, marked as AI-assisted and requiring student/domain review. Ambiguous or source-mismatched cases were not forced into `LABEL_DECISION_ERROR`.
- No Cohen's kappa or inter-annotator agreement is reported because there is no independent second annotator.
- Raw abstracts are not redistributed in this package; only document identifiers, notes, and source links are recorded.

## What remains to close RQ3

1. Student verifies all 50 AI-assisted labels and notes against the exact local SciFact corpus snapshot and the actual evidence input saved for each condition.
2. Resolve the claim 593 and claim 343 source/annotation conflicts against the exact local `corpus.jsonl` and `claims_dev.jsonl` used in the original experiment.
3. If time permits, recruit a second independent coder to label the same 50 rows; only then calculate agreement and Cohen's kappa.
4. Update the paper's RQ3 results only after the student's review is complete. The counts in the interim report are exploratory and must not be presented as final human-coded findings.


## Frozen codebook integrity

The uploaded project copy did not contain a separate `.sha256` sidecar for `rq3_codebook.FROZEN.md`. A current SHA-256 checksum is recorded in `rq3_codebook_integrity_20261102.json`; this is a present-day integrity check and does not prove that the same hash was captured at the original freeze time.