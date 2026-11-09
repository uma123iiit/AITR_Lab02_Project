# RQ3 preliminary text-based error analysis

**Review date:** 2 November 2026  
**Sampling:** Frozen 50-case sample; seed 42; A=17, B=17, C=16.  
**Annotation status:** AI-assisted preliminary annotation; student/domain review is still required. This is not represented as a completed human annotation study.

## 1. What was inspected

The sample has 50 condition–claim pairs and 45 unique claim IDs. Claim text, gold labels, evidence document IDs, evidence rationale sentence IDs, and abstracts were inspected from public mirrors. Source links and the exact source limitations are in `RQ3_SOURCE_PROVENANCE.md`.

The claims mirror was `openai/openai-cookbook/examples/data/scifact_claims.jsonl` (300 rows). Abstracts were inspected from the pinned `Aki-max-min/novatel-telecom-rag-unstructured` BEIR/SciFact mirror at commit `f2249a67bc0eb9f988f6c1954dd77fad745b955c`. The mirror was not checksum-matched to the exact local corpus snapshot used for the archived run. Where the abstract and saved gold label/claim rationale were in tension, the case was marked `AMBIGUOUS_ANNOTATION`.

## 2. Preliminary category counts

| Category | Count |
|---|---:|
| AMBIGUOUS_ANNOTATION | 14 |
| LABEL_DECISION_ERROR | 31 |
| NO_EVIDENCE_SEEN | 1 |
| OTHER_UNCERTAIN | 3 |
| RETRIEVAL_MISS | 1 |
| **Total** | **50** |

### By experimental condition

| Condition | AMBIGUOUS_ANNOTATION | LABEL_DECISION_ERROR | NO_EVIDENCE_SEEN | OTHER_UNCERTAIN | RETRIEVAL_MISS |
|---|---:|---:|---:|---:|---:|
| A | 5 | 10 | 0 | 2 | 0 |
| B | 3 | 13 | 1 | 0 | 0 |
| C | 6 | 8 | 0 | 1 | 1 |

These are descriptive AI-assisted preliminary counts only. They are not final student-coded prevalence estimates and must not be used to claim a validated taxonomy distribution.

## 3. Interpretation

- `LABEL_DECISION_ERROR` is the largest preliminary group (31/50). These are cases where the reviewed text appears to support the stored gold label or contradict the model's prediction.
- `AMBIGUOUS_ANNOTATION` (14/50) captures wording that overstates evidence, compound/underspecified claims, or potential mismatch between mirrored abstracts and the saved gold annotations. This is important: a disagreement between model output and a stored label is not automatically a model error if the underlying evidence/label pair itself is unclear.
- The two deterministic metadata cases are B/303 (`NO_EVIDENCE_SEEN`) and C/756 (`RETRIEVAL_MISS`). These follow the frozen rule order and PC-006.
- `OTHER_UNCERTAIN` cases were retained where the available abstracts did not permit a defensible decision. The absence of a gold evidence document prevents categories 2 and 3 under PC-006.

## 4. Selected illustrative cases

| Case | Preliminary code | Why it matters |
|---|---|---|
| A/51 | LABEL_DECISION_ERROR | Abstract reports ALDH1 association with poor prognosis, while the claim says better outcomes. |
| B/5 | LABEL_DECISION_ERROR | 493 abnormal-PrP positives per million is approximately one in 2,028, close to the claim's one in 2,000. |
| C/129 | LABEL_DECISION_ERROR | Retrieved abstract reports an open-access citation advantage, opposite to the claim. |
| C/756 | RETRIEVAL_MISS | Gold evidence document is absent from BM25 top five. |
| B/593 | AMBIGUOUS_ANNOTATION | Mirrored abstract conflicts with the stored SUPPORT label; exact local snapshot is needed. |
| C/783 | AMBIGUOUS_ANNOTATION | Retrieved IFN-gamma receptor knockout evidence indicates exacerbated EAM, making the stored NEI/claim combination debatable. |

## 5. Reliability and limitations

No inter-annotator reliability statistic is reported. Only one AI-assisted preliminary pass exists, and the student has not yet signed off on the labels. Cohen's kappa would be inappropriate without an independent second coder.

The main provenance limitation is that the public BEIR/SciFact mirror could not be confirmed byte-identical to the historic local corpus. This appears to matter for at least claim 593 and potentially claim 343. The exact historical `corpus.jsonl` and `claims_dev.jsonl` remain the gold standard for final annotation.

The sample is a stratified sample of model errors, not a random sample of all claims. Its category proportions describe this error sample only and should not be generalized to all SciFact claims.

## 6. Required student checks

1. Review all 50 labels and notes; pay special attention to every `AMBIGUOUS_ANNOTATION` and `OTHER_UNCERTAIN` case.
2. Compare source text for claims 593 and 343 against the exact local SciFact files used in the saved run.
3. If a second coder is available, have them annotate the same sample independently before reporting agreement.
4. Do not update the manuscript's main RQ3 findings until these checks are complete.

**Reproducibility note:** The original frozen `rq3_sample.csv`, frozen codebook, and PC-006 amendment remain unchanged. The AI-assisted coding is stored in a new versioned file so that the audit trail is preserved.