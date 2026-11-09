# RQ3 codebook amendment 1 (applies to configs/rq3_codebook.FROZEN.md), 2026-10-30

The frozen codebook is unchanged and its hash still verifies. This amendment adds one scope rule. It is recorded as PC-006.
It was written after the sample was drawn (RUN-002) but BEFORE any sampled case was coded or read.

Rule: if a claim has no gold evidence document (gold_evidence_doc_ids is empty in the sheet; these are NOT_ENOUGH_INFO claims),
categories 2 (RETRIEVAL_MISS) and 3 (EVIDENCE_IRRELEVANT) do not apply, because both are defined relative to a gold document.
Code such cases with 1 (B/C with empty evidence), 4, 5, 6 or 7. Condition A keeps its existing restriction (4 to 7 only).
For C, a blank bm25_hit_at_5 means exactly this situation; it is not a retrieval miss.

Reason: the frozen definitions of 2 and 3 are undefined for claims with no gold document (found in a post-draw check of the sheet).
Effect on comparability: none on the sample or on any metric; it only restricts which categories a coder may assign.