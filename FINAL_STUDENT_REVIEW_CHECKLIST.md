# Final student review checklist

This checklist records the current submission status. Historical audit logs are retained as provenance; a past limitation in a separate review environment should not be read as a current project failure.

## Manuscript and submission
- [x] Final manuscript prepared as a nine-page paper using the instructor-provided template.
- [x] Paper PDF, LaTeX source, bibliography and figure exports are included in the repository.
- [x] Manuscript figures and archived numerical results are cross-referenced.

## Code and reproducibility
- [x] Archived prediction files have a documented read-only integrity/metrics audit.
- [x] Python source compilation (compileall) passed in the recorded audit.
- [x] Student confirms that the complete test suite passes in the working project environment.
- [x] Test suite includes test_inputs.py and test_retrieval.py; the earlier missing-rank-bm25 report refers only to a separate review container.
- [ ] If a byte-identical historical data archive is required for a clean end-to-end reproduction, verify the downloaded archive against the recorded SHA-256 before running it.

## RQ3 student verification
- [x] Frozen 50-row sample and codebook artifacts are documented.
- [x] AI-assisted preliminary codes and source/provenance notes are documented.
- [ ] Review all 50 rows against the exact local claims_dev.jsonl and corpus.jsonl snapshot used in the experiment.
- [ ] Apply the frozen codebook and PC-006 amendment; record disagreements and reasons.
- [ ] Fill the student verification sheet with the actual final category, reviewer identity and review date.
- [ ] Update the RQ3 report only after the student review is complete.
- [ ] Do not report Cohen's kappa unless a second annotator independently codes the same cases.

## Human accountability and presentation
- [x] Instructor template and final paper page count confirmed by the student.
- [x] Demonstration script is available and aligned with the repository paths.
- [ ] Rehearse the demonstration using the actual repository files and commands.
- [ ] Be prepared to explain every method, result, research decision and limitation.
- [ ] Add a student sign-off only after personally completing the relevant checks.

## Current status note

The paper, code and test suite are reported as complete and working by the student. The RQ3 codes remain preliminary until the student verification sheet records the actual manual review. The historical review-container dependency issue is preserved in the audit trail for transparency, but it is not evidence that the student's working project or full test suite is failing.
