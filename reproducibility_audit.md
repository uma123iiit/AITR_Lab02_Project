# Reproducibility, source-data and final integrity audit — 1 November 2026

## Verified in this audit

- Read-only archive checks validated prediction SHA-256 values, 286 rows per condition, unique claim IDs, identical A/B/C ID sets, and recomputed accuracy/macro-F1 from archived predictions.
- The archived metric summary is internally consistent: A 0.4615 / 0.3757, B 0.6014 / 0.4988, C 0.4371 / 0.3650 (accuracy / macro-F1; 286 development claims).
- `compileall` succeeded for the project source, scripts and tests.
- The original literature-review PDF is included in the outer submission ZIP. A previous self-audit sentence stating that it was missing is superseded. The exact review-to-gap page crosswalk still needs student confirmation.
- The source paper now fills the known enrollment number, includes explicit references to both figures, and contains a 12-entry citation-to-bibliography consistency check.
- The RQ3 sample remains frozen at 50 rows (A=17, B=17, C=16). A new metadata-only precheck identifies one B empty-evidence candidate and one C retrieval-miss candidate; it does not fill coder fields. A tested local enrichment helper now reconstructs claim/evidence text from the actual raw data, but cannot be run against this ZIP because those raw files are intentionally absent.

## Test-suite attempt in this review container

Runtime: Python 3.13.5. The recorded project environment is Python 3.11.2. In this runtime, the full command `PYTHONPATH=src python -m pytest -q` exits during collection because `rank-bm25==0.2.2` is absent; the blocked imports are in `tests/test_inputs.py` and `tests/test_retrieval.py`. Network/DNS access prevented installing that dependency. A separate run excluding only those two modules passed 51 tests (`logs/tests_without_missing_rank_bm25_modules_20261101.txt`). The newly added RQ3 helper test module passed independently (3 tests; `logs/rq3_enrichment_tests_20261101.txt`). This is useful partial test coverage, not a full-suite pass and not a run under the recorded Python 3.11.2 environment.

This is not a clean pass of the complete suite and is not a run in the exact recorded environment. It is also not evidence that historical training/inference was rerun. The archive includes an environment snapshot and a prior smoke test; the latter is a plumbing test, not a full model-training reproduction.

## Dataset identity and licensing

The archived run used the official AllenAI SciFact S3 `release/latest` tarball. Project logs record a download timestamp and SHA-256, but do not map the tarball to an immutable Git commit. The official repository license file states that claims/evidence annotations are CC BY 4.0, corpus abstracts are sourced from S2ORC and licensed ODC-By 1.0, and repository code is Apache 2.0. A separate Hugging Face mirror/card labels its distribution CC BY-NC 2.0 and lists different split counts; it was not the source used for this run. Thus the blanket “all licences unresolved” statement is superseded by a component-level source check, but exact snapshot-to-license association remains partially unresolved because `release/latest` is mutable. Raw data stay excluded.

## Remaining actions that cannot be completed from this ZIP alone

1. Run `scripts/17_enrich_rq3_sample.py` against the exact local `claims_dev.jsonl` and `corpus.jsonl`; review all 50 cases and complete the coder fields. Two precheck suggestions are not final labels.
2. Re-run the entire suite under the archived Python 3.11.2 environment with the recorded dependency versions and save complete stdout.
3. Run the end-to-end README workflow from a clean checkout using a byte-identical data archive; the current S3 `release/latest` link may now point to different bytes.
4. Locate an immutable official commit/release that corresponds to the archived source, record its commit SHA, and confirm component-level attribution/licence obligations for that snapshot before any data redistribution.
5. Personally verify the exact literature-review page-to-gap trace, check the PDF title page/enrollment against the portal, and rehearse the five-minute demo.

## Scope boundary

This audit validates archived output integrity, not the scientific validity of every design decision. It does not train models, access Colab, independently annotate claims, or establish a course grade. The technical peer review in the submission pack is an internal AI-assisted review, not an external review.


## Emergency audit update — 02 November 2026

- Full-suite command rerun in Python 3.13.5: collection stops with two import errors (`tests/test_inputs.py` and `tests/test_retrieval.py`) because `rank_bm25` is not installed. An attempted install of `rank-bm25==0.2.2` failed because package-index DNS/network access is unavailable. See `logs/emergency_reaudit_20261102/full_test_suite.txt`.
- The run excluding only those two dependency-blocked modules passes 46 tests. The RQ3 enrichment module passes 3 tests; the new metadata-only coding helper passes 5 tests. `compileall` passes. See all logs in `logs/emergency_reaudit_20261102/`.
- `scripts/14_verify_saved_outputs.py` passes again: prediction SHA-256, row counts, unique claim IDs, matched A/B/C ID sets, accuracy and macro-F1 recomputation. This is an output integrity audit, not a model rerun.
- The original review is now available in the final provenance folder and has been mapped to the selected question in `review_to_experiment_trace.md`. The connection is conceptual and bounded; the implementation is not an experiment on generative LLM outputs and does not validate the complete review taxonomy.
- RQ3 partial pre-coding is recorded in `results/rq3/rq3_sample_partial_deterministic_codes.csv`. Six rows are assigned by deterministic frozen-codebook/PC-006 rules; 44 require the original evidence text. The original frozen sample remains unchanged. No category-level inference is reported.

## RQ3 reconciliation update — 02 November 2026

A separate AI-assisted preliminary text review has now assigned codes to all 50 frozen condition–claim rows. The two deterministic metadata assignments are B/303 (`NO_EVIDENCE_SEEN`) and C/756 (`RETRIEVAL_MISS`); the other 48 are preliminary text-review judgments. The preliminary distribution is 31 `LABEL_DECISION_ERROR`, 14 `AMBIGUOUS_ANNOTATION`, 3 `OTHER_UNCERTAIN`, 1 `NO_EVIDENCE_SEEN`, and 1 `RETRIEVAL_MISS`. The source abstracts were retrieved from public mirrors that are not checksum-matched to the exact historical local corpus. All 50 rows therefore remain pending student verification against the exact historical snapshot. This replaces, but does not delete, earlier interim statements about 44 rows awaiting text review. No final human-coded taxonomy finding or kappa is claimed.

## Status clarification — 10 November 2026

The test-suite errors described above were produced in a separate review container running Python 3.13.5 without the project's rank-bm25 dependency and without package-index network access. They document the limitations of that review environment only. The student has since confirmed that the complete test suite passes in the working project environment. The earlier logs are retained as historical provenance and must not be interpreted as evidence that the current project test suite is failing. The student also confirmed that the final manuscript is nine pages and uses the instructor-provided template. No experimental metrics or archived prediction files were changed by this documentation update.
