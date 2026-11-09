# RQ3 — what has now been done and what you should verify

## Current status

An AI-assisted preliminary review has filled all 50 frozen sample rows using claim text, gold evidence identifiers/rationales, gold abstracts, and selected retrieved abstracts from public SciFact mirrors. It is not a final human annotation. The exact corpus snapshot used in the historic experiment is not checksum-matched to the public BEIR/SciFact document mirror.

The initial metadata-only precheck has exactly two deterministic assignments under the frozen codebook + PC-006:
- B / claim 303 — `NO_EVIDENCE_SEEN` (B input empty).
- C / claim 756 — `RETRIEVAL_MISS` (gold document absent from BM25 top-five).

The other 48 entries are AI-assisted text judgments and require student review. Four earlier interim `NO_EVIDENCE_SEEN` labels for C/198, C/350, C/577, and C/783 were incorrect because those C inputs contain retrieved documents. The correction is documented; old files are preserved as superseded artifacts.

## Files to use

1. `rq3_sample_ai_assisted_preliminary_20261102.csv` — full preliminary coding with notes.
2. `rq3_student_verification_sheet.csv` — same rows plus blank columns for your own approved category, revision note, reviewer and date.
3. `RQ3_PRELIMINARY_TEXT_BASED_ANALYSIS.md` — interim analysis and category counts.
4. `RQ3_SOURCE_PROVENANCE.md` — source links and provenance limitations.
5. `RQ3_PRIOR_INTERIM_CORRECTION.md` — correction of the earlier 6-case metadata-only mistake.
6. `rq3_sample.csv` — original frozen sample; unchanged.

## Student review procedure

For each of the 50 rows:
1. Open the exact local `claims_dev.jsonl` and `corpus.jsonl` from the same snapshot used in the archived experiment.
2. Check claim text, gold evidence document IDs, sentence IDs, and the text actually supplied to A/B/C.
3. Compare the preliminary category and rationale with the frozen seven-category codebook and PC-006. Use the codebook's first-fit order.
4. Enter your final decision in `student_verified_category`. Enter any disagreement or reason in `student_revision_note`, plus your reviewer identity/date.
5. Do not report Cohen's kappa unless a second person independently labels the same 50 rows without seeing these preliminary labels.

## Main cases to check carefully

- 593 in A/B: the public abstract mirror appears inconsistent with the saved gold SUPPORT label/sentence index.
- 343 in C: the public abstract mirror does not clearly show the specific bleeding-risk evidence implied by the stored gold label.
- 502 in A: claim wording is unclear and the cited document appears unrelated.
- 208 in A, 431 in B, 513 in A/C, 1221 in A/B, 759 in C, and 783 in C: the claim is broader or more specific than the available abstract, so the gold label is debatable or source-snapshot dependent.

## How to report the present interim results

You may state that an AI-assisted preliminary coding pass was conducted and that its provisional distribution is in the interim report. Do not describe it as human-coded or as final RQ3 findings until you personally verify the sheet against the exact local corpus. There is no second-coder reliability result yet.