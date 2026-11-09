# Deliverables content index

This index maps every required item in the assignment handbook to the exact materials supplied in the A–E package.

## A. Research paper

Folder: `A_Research_Paper/`

- `Research_Paper_Final.pdf` — final compiled eight-page manuscript.
- `research_paper.tex` — editable LaTeX manuscript.
- `references.bib` — bibliography database.
- `references_manual.tex` — manually managed references, retained for compilation/review.
- `figures/` — macro-F1 comparison, paired-difference confidence intervals and retrieval Recall@5, in PNG and PDF formats.
- `CITATION_AUDIT.md` — citation-key and source audit.
- `README.md` — paper build and source notes.

## B. GitHub repository

Folder: `B_GitHub_Repository/AITR_Lab02_MNS2026009_EvidenceConditioned/`

- `README.md` — research question, project map, experiment summary and reproduction commands.
- `requirements.txt`, `requirements.lock.txt` — dependency declarations.
- `src/` — reusable Python modules for loading data, formatting evidence, retrieval, classification, scoring and RQ3 helpers.
- `scripts/` — data checks, environment smoke checks, retrieval, training/evaluation, output audit and RQ3 scripts.
- `tests/` — unit and sanity tests.
- `configs/` — frozen experiment configuration and RQ3 codebook/amendment.
- `data/README.md` — dataset acquisition, format and license/provenance notes; raw data are not redistributed.
- `results/`, `logs/` — archived metrics, predictions, retrieval ranks, figures and run logs.
- `paper/` — LaTeX source, bibliography and compiled paper assets.
- `research_decisions.md`, `baseline_validation.md`, `ai_assistance_log.md`, `review_to_experiment_trace.md` — project decisions and verification.
- `MANIFEST.md`, `FINAL_SHA256SUMS.txt` — file inventory and integrity information.

## C. Experimental evidence

Folder: `C_Experimental_Evidence/`

- `results/results.csv` — primary A/B/C development-set metrics.
- `results/results_paired_differences.csv` — paired bootstrap comparisons and confidence intervals.
- `results/results_rule_baseline_B.csv` — empty-evidence shortcut baseline.
- `results/results_rq2_hit_miss.csv` — retrieval hit/miss analysis.
- `results/retrieval/` — per-claim BM25 and TF-IDF rankings, document IDs and retrieval metadata.
- `results/metrics/` — timestamped predictions and metrics.
- `results/rq3/rq3_sample.csv` — original frozen 50-case sample; do not overwrite.
- `results/rq3/rq3_sample_ai_assisted_preliminary_20261102.csv` — separate 50-row preliminary annotation file.
- `results/rq3/rq3_student_verification_sheet.csv` — student sign-off/correction sheet.
- `results/rq3/RQ3_PRELIMINARY_TEXT_BASED_ANALYSIS.md` — preliminary counts, examples and limits.
- `results/rq3/RQ3_SOURCE_PROVENANCE.md` — source URLs, identity caveat and annotation protocol.
- `configs/`, `scripts/`, `logs/` — frozen protocol/codebook, audit utilities and genuine archived console output.

## D. Research provenance

Folder: `D_Research_Provenance/`

- `Original_Review_and_Assignment/` — original literature review and instructor assignment brief.
- `Prompt_01_02/` — final gap matrix and research decisions in Markdown, DOCX and PDF.
- `Prompt_03_08/` — literature-to-experiment mapping, feasibility/novelty/access, research brief, dataset/baseline validation, frozen experiment blueprint and environment guide.
- `Decision_and_Validation/` — research decisions, review-to-experiment trace, baseline audit, protocol reconciliation, reproducibility audit, peer review, AI-assistance log, citation audit and frozen RQ3 codebook/amendment.
- Root RQ3 docs — preliminary analysis, source provenance, review guide and superseded-report correction.

## E. Demonstration

Folder: `E_Demonstration/`

- `demo_5min.md` — timed walkthrough script with actual project files and measured results.
- `viva_questions_and_answers.md` — technical viva preparation.

**Not included:** an actual screen recording or evidence of live demonstration. The student must deliver that part personally if required by the instructor/portal.

## Data and reproducibility boundaries

- Reported scores are from the matched development set, not the official hidden test split.
- Raw SciFact corpus/claims files are excluded.
- Model weights are not newly trained in this final packaging audit.
- RQ3 preliminary codes are not human-final and should not be presented as such.
- A clean environment rerun of the complete test suite remains open.