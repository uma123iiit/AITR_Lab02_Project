# Marking estimate and submission audit

**Student:** Umakant Singh  
**Course:** AI Tools for Research | Lab Assignment 02  
**Assessment date:** 2 November 2026  
**Estimated score:** **7.4/10** (self-assessment; not an instructor-issued mark)

> The assignment handbook defines deliverables A–E and minimum research standards, but does not give numerical weights. The weights below are an explicit working rubric to make this estimate transparent. The instructor may use different weights or additional criteria.

## Category-by-category estimate

| Component | Working weight | Estimated points | Evidence supporting the score | Main deductions / open items |
|---|---:|---:|---|---|
| A. Research paper | 2.0 | **1.6** | 8-page compiled PDF; LaTeX source, BibTeX, figures and citation audit included. Results and limitations are qualified. | Low classifier performance, one development run, no hidden test-set result, modest methodological contribution, RQ3 not final in the manuscript. |
| B. GitHub repository | 2.0 | **1.7** | Source modules, scripts, tests, README, dependency files, configs, dataset instructions, frozen protocol and result assets included. | Repository not pushed to GitHub; clean installation and full test suite not verified in the specified environment; raw data intentionally excluded. |
| C. Experimental evidence | 3.0 | **2.0** | Archived predictions, CSV metrics, retrieval rankings, paired bootstrap intervals, rule baseline, sensitivity/hit-miss analyses, logs, seeds and plots included. | Full-set B comparison has an identified shortcut confound; no new final training run; evidence is development-only; RQ3 labels remain AI-assisted preliminary and require source-matched student sign-off; full tests blocked. |
| D. Research provenance | 1.5 | **1.3** | Gap/decision brief, review-to-experiment trace, dataset protocol, baseline validation, peer review, AI-use log, codebook and source-provenance notes included. | Dataset revision not pinned to an immutable snapshot; exact source-mirror identity not established; AI-assistance log and source attribution still need student confirmation for authenticity. |
| E. Demonstration and viva | 1.5 | **0.8** | Five-minute timed walkthrough script and technical viva Q&A included. | No actual video/recording or evidence of live delivery; student must personally demonstrate code and explain the decisions. |
| **Total** | **10.0** | **7.4** | | |

## Research evidence that is strong

1. **Protocol discipline:** the study distinguishes claim-only, gold-evidence and BM25-retrieved-evidence conditions; uses a matched development set; documents near-duplicate filtering and a frozen configuration.
2. **Independent checks:** archived outputs have been audited for IDs, hashes, prediction/metric consistency and independent recomputation; the baseline audit records vectorizer leakage checks and a frozen rerun.
3. **Interpretation is candid:** the B condition's empty-evidence shortcut is explicitly measured; the evidence-bearing paired-bootstrap interval includes zero; C does not outperform A; high Recall@5 is not conflated with correct classification.
4. **Failure analysis and provenance:** error sampling, a frozen codebook, a codebook amendment, source provenance and a verification sheet are preserved without presenting preliminary labels as final human annotation.

## Main issues likely to cost marks

- **RQ3 is not final.** The 50-row file contains AI-assisted preliminary codes: 48 text-review judgments and two metadata-deterministic assignments. It needs student/domain verification against the exact historical local SciFact claims and corpus files. The public mirrors used for the text review are not cryptographically matched to the original local snapshot. Do not report the category distribution as final or generalize it beyond the selected error sample.
- **No second annotator.** Cohen's kappa is correctly not reported. If a second independent coder is available, both coders should annotate the same fixed sample before calculating agreement.
- **Full test suite is unresolved.** 51 tests passed when two dependency-blocked modules were excluded. This is not a full pass. Install the pinned requirements in Python 3.11.2 and run all tests.
- **Dataset provenance needs closure.** Preserve the exact upstream archive version/commit and checksum for the experiment; do not distribute raw files until rights and terms are settled.
- **Demonstration still needs delivery.** The script is not the demonstration itself. The student must run the project, show outputs, and answer viva questions.
- **No official test score.** The paper reports SciFact development-set results only; the hidden official test labels were not used.

## Score sensitivity

A reasonable evaluator could place this between **7.0 and 7.8/10**, depending on whether the instructor gives greater weight to the breadth of documentation and honest negative findings, or to complete experiment reruns, final human coding and the live demonstration. A mark above 9/10 is not supported by the evidence currently available.

## Highest-impact actions before final upload

1. Verify all 50 RQ3 rows against the exact dataset snapshot used in the experiments; manually approve or correct every preliminary category.
2. Run the full test suite in the pinned Python 3.11.2 environment and preserve the complete console output.
3. Pin the raw dataset revision/checksum in the data provenance record and rerun only if the retrieved version differs materially from the historical run.
4. Perform and record the five-minute demo; be ready to execute the archived-results verification command live.
5. Push the cleaned repository to GitHub only after a secret scan and a final check that no raw restricted dataset files are included.

## Important grading boundary

This estimate grades the **current artifacts**, not the student's oral explanation or a future successful rerun. The actual grade is determined by the instructor and may differ.