# RQ3 error codebook: FROZEN 2026-10-30

Status: FROZEN. Drafted by the assistant from the example categories in Prompt06; edited and approved by the researcher.
Changes require a new versioned file and a protocol-change entry; this file is never edited in place.
Freeze rule (Prompt05/07): frozen and hashed BEFORE anyone looks at the sampled errors (sha256 in configs/rq3_codebook.FROZEN.md.sha256).
No individual error cases had been inspected when this was frozen (aggregate metrics, confusion matrices and the RQ2 hit/miss table had been). Coding is single-annotator (descriptive) unless a second
annotator codes the same sample independently.

Unit: one claim-condition pair where predicted_label != gold_label (dev, matched set of 286 claims).
Sampling: up to 50 errors total, stratified across conditions A/B/C, seed 42, drawn before coding; code all if fewer.
One primary category per case (single label). Optional free-text note. Apply the FIRST rule that fits, in order.

| # | Code | Operational definition | Applies to |
|---|------|------------------------|-----------|
| 1 | NO_EVIDENCE_SEEN | B or C input has empty evidence (includes B on NEI claims). Not used for condition A | B/C with empty evidence |
| 2 | RETRIEVAL_MISS | Condition C and no gold evidence document is in the top 5 (hit status = miss) | C |
| 3 | EVIDENCE_IRRELEVANT | Evidence shown, and the gold-relevant document is absent or the shown text does not bear on the claim | B/C |
| 4 | LABEL_DECISION_ERROR | (condition A: any error with no coder-judged ambiguity) A gold-relevant document is shown (B, or C hit), or the claim is judged answerable, but the model chose the wrong class (merged former categories 4 and 5: misread evidence and wrong decision are not separated, since a bag-of-words verifier does not read) | any |
| 5 | INPUT_FORMAT_TRUNCATION | Input formatting problem or truncation flag set (expected rare: truncation_flag is 0 for every run) | any |
| 6 | AMBIGUOUS_ANNOTATION | The coder judges the gold label itself debatable given the shown evidence | any |
| 7 | OTHER_UNCERTAIN | None of the above fits, or the coder cannot decide | any |

Notes and decisions:
- DECIDED by researcher: former categories 4 (misread) and 5 (decision error) merged into 4.
- DECIDED by researcher: condition A errors are not coded as NO_EVIDENCE_SEEN (it would hold every A error). A errors are
  coded only with 4, 5, 6, 7. A stays in the stratified sample. Gold label and gold-evidence presence are reported from
  saved files, not coded.
- Cases 2 and 3 can be assigned from saved ranks without reading text. 4 to 7 need reading.
- If a second annotator codes the sample, report raw agreement and Cohen's kappa; kappa >= 0.60 is an exploratory target only.

Approval record: approved by the researcher in session, 2026-10-30. Hash: see configs/rq3_codebook.FROZEN.md.sha256 (a hash cannot sit inside the file it covers).