# Repository contents and submission boundary

This index describes the contents of this GitHub repository only. It is **not** an inventory of the original A–E submission package, and references to external packaging folders are intentionally not used as repository paths.

## Research implementation
- `src/scifact_verif/` — reusable data, input formatting, retrieval, verifier, metrics and RQ3 helper modules.
- `scripts/` — dataset acquisition/audit, experiment execution, evaluation, archived-output checks and RQ3 utilities.
- `tests/` — focused unit and validation tests.
- `configs/` — experiment settings, frozen protocol, RQ3 codebook and amendment.
- `requirements.txt`, `requirements.lock.txt` — dependency declarations and recorded environment snapshot.

## Data and experimental evidence
- `data/README.md` — official SciFact source, schema, acquisition record and component-level licence notes. Raw data are not redistributed.
- `results/` — selected archived metrics, predictions, retrieval evaluation, audit records and preliminary RQ3 material.
- `logs/` — selected command output and audit records. These are historical records, not proof that every workflow has been rerun from a clean checkout.

## Manuscript and research provenance
- `paper/` — LaTeX manuscript source, bibliography, citation audit and reference notes. The compiled PDF and figure exports are not currently included.
- `research_decisions.md`, `review_to_experiment_trace.md`, `baseline_validation.md`, `ai_assistance_log.md` — research rationale, traceability and verification records.
- `phase1_gap_matrix.md` through `phase6_accountability_review.md`, `protocol_status_reconciliation.md`, `reproducibility_audit.md` — project planning, results, review and reproducibility history.
- `demo_5min.md`, `viva_questions_and_answers.md` — demonstration and viva preparation.
- `FINAL_STUDENT_REVIEW_CHECKLIST.md` — remaining student-owned submission and verification tasks.
- `LIMITATIONS_AND_REMEDIATION.md` — limitation-by-limitation status and remediation actions.

## Important omissions and limitations
- No Jupyter notebook is included. The workflow is implemented as Python modules, scripts and tests.
- The compiled paper PDF and paper figure exports are not included in the current GitHub tree.
- Raw SciFact files and model-weight artifacts are excluded.
- RQ3 codes are AI-assisted preliminary suggestions, not human-final annotations.
- The complete test suite and clean-checkout reproduction remain unverified.
- No screen recording or proof of a live demonstration is included.
