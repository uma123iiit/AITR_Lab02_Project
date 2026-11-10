# Five-minute code-and-results demonstration

**Goal:** demonstrate the actual project flow and explain the research question, methods, results and scope accurately.

## Before the demo
Open the project repository in VS Code. Keep these files ready: `README.md`, `configs/primary_frozen.yaml`, `src/scifact_verif/verifier.py`, `src/scifact_verif/retrieval.py`, `scripts/07_run_condition.py`, `scripts/05_run_retrieval.py`, `results/results.csv`, `results/results_paired_differences.csv`, and the figures directly under `paper/`.

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

**4:15-5:00 — Error analysis and integrity**  
Show `reproducibility_audit.md` and `results/rq3/RQ3_PRELIMINARY_TEXT_BASED_ANALYSIS.md`. Explain that the 50 frozen sample rows were manually reviewed and verified by the student. Their category counts are descriptive of the selected sample only, not population-level estimates. No independent second coder or Cohen's kappa is claimed.

## Optional command to demonstrate archived-output validation
Run from repository root:

```bash
PYTHONPATH=src python scripts/14_verify_saved_outputs.py
```

This checks saved prediction hashes, IDs and metrics. It does not retrain the models.

The student confirms that the complete test suite passes in the working project environment. Earlier logs describe a separate review container that lacked `rank-bm25`; that environment-specific issue should not be presented as a failure of the project.
