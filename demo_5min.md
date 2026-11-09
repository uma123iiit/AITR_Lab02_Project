# Five-minute code-and-results demonstration

**Goal:** demonstrate the actual project flow and explain the real result, including its limitations. Do not claim a clean full-suite pass or a completed RQ3 taxonomy analysis.

## Before the demo
Open the project repository in VS Code. Keep these files ready: `README.md`, `configs/primary_frozen.yaml`, `src/scifact_verif/verifier.py`, `src/scifact_verif/retrieval.py`, `scripts/07_run_condition.py`, `scripts/05_run_retrieval.py`, `results/results.csv`, `results/results_paired_differences.csv`, and the two figures under `paper/figures/`.

## Timed walkthrough

**0:00-0:45 — Problem and question**  
“Scientific claims need evidence. We asked whether a lightweight verifier behaves differently when it sees only the claim, gold evidence, or automatically retrieved evidence. This is a controlled comparative study, not a new model architecture.”

**0:45-1:30 — Dataset and protocol**  
Show `data/README.md` and `configs/primary_frozen.yaml`. Explain 809 train claims, 300 development claims, 5,183 corpus abstracts; 14 near-duplicate development claims were held out, leaving 286 matched claims, of which 182 have gold evidence. Say clearly that the official test labels were not used.

**1:30-2:20 — Code path**  
Show `scripts/05_run_retrieval.py`, `src/scifact_verif/retrieval.py`, `src/scifact_verif/verifier.py`, and the frozen config. Explain that BM25 ranks documents; a separate TF-IDF + Logistic Regression classifier predicts SUPPORT, CONTRADICT or NOT ENOUGH INFO. Gold labels/doc IDs are used for post-hoc scoring, not retrieval ranking.

**2:20-3:20 — Results**  
Show `results/results.csv` and the paper's macro-F1 figure. On 286 claims, A/B/C macro-F1 is 0.3757/0.4988/0.3650. Then switch to the evidence-bearing 182-claim slice: 0.3140/0.3492/0.3119. Explain that the B-A estimate is +0.0352 but its 95% CI [-0.0275, +0.0974] includes zero.

**3:20-4:15 — Deeper analysis**  
Show `results/results_rule_baseline_B.csv` and the retrieval Recall@5 figure. The full-set B score is confounded by empty evidence for NOT ENOUGH INFO cases; a simple evidence-presence rule can exploit that structure. BM25 Recall@5 is 90.11%, but C does not improve classification. Finding the right document is not the same as understanding it.

**4:15-5:00 — Integrity and limits**  
Show `reproducibility_audit.md` and `results/rq3/RQ3_PRELIMINARY_TEXT_BASED_ANALYSIS.md`. State: all 50 frozen sample rows have AI-assisted preliminary codes, but none of the 48 text-reviewed judgments is a student-final annotation; the two deterministic metadata assignments are B/303 and C/756. The public mirror was not checksum-matched to the exact historical corpus, so all 50 require student verification against the local snapshot. The partial test run passed 51 tests after excluding two modules blocked by missing `rank-bm25==0.2.2`; a full Python 3.11.2 run remains required. No raw data are redistributed because the exact historical release revision is not pinned.

## Optional command to demonstrate archived-output validation
Run from repository root:

```bash
PYTHONPATH=src python scripts/14_verify_saved_outputs.py
```

This checks saved prediction hashes, IDs and metrics. It does not retrain the models.