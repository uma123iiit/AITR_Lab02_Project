# research_decisions.md: decisions, reasons, evidence, next actions

Project: Evidence-conditioned SciFact claim verification (claim only vs gold evidence vs BM25-retrieved evidence), with
taxonomy-guided error analysis. All results are DEVELOPMENT-set results from one frozen local run (CPU), never test.
Source protocol: Prompt05 brief, Prompt06 sheet, Prompt07 blueprint (provenance/). Full change history: logs/protocol_changes.md.

## Evidence ledger
| Label | Statement | Evidence |
|---|---|---|
| VERIFIED | Data counts match the SciFact paper's Table 2a (train 809, dev 300, corpus 5183) | results/validation/baseline_audit_20261030T132321Z.json (D1 checks) |
| VERIFIED | Metrics, condition-A refit, BM25 top-5 and Recall@5 recomputed independently of the repo code | same audit (A1, A2, R1, R2) |
| VERIFIED | Frozen rerun of A reproduces the pre-freeze A run exactly (286/286 labels and hashes) | logs/protocol_changes.md RUN-001 |
| VERIFIED | Sample for RQ3 redraws byte-identically with seed 42 | session check, logged in ai_assistance_log.md AI-10 |
| INFERRED | CONTRADICT is nearly undetected because a bag-of-words verifier cannot see negation or direction | CONTRADICT F1 0.04 to 0.12 across all rows of results/results.csv; mechanism NOT tested |
| INFERRED | B's primary-set gain over A comes from the empty-evidence = NEI shortcut | B below the empty-evidence rule baseline (results/results_rule_baseline_B.csv); not proven causally |
| UNKNOWN | Link from the original literature review to this question | the assistant never read paper_mns2026009.pdf, Prompt03 or Prompt04; the student must verify the review-to-gap trace |
| PARTIALLY RESOLVED | Official SciFact component licence statements are documented in data/README.md; the exact release/latest archive is not tied to an immutable upstream revision, so snapshot-to-licence association remains open | data/README.md; preserve the original frozen config unchanged and read protocol_status_reconciliation.md for chronology |
| UNKNOWN | Whether results hold on Colab/GPU, and effect of BM25 epsilon floor | Colab rerun and epsilon=0 check not done |

## Decisions
| ID | Date | Decision | Reason / evidence | Decided by |
|---|---|---|---|---|
| D-01 | 2026-10-30 | Run everything locally on CPU; Colab untested | The assistant cannot create a Colab runtime; local smoke test passed (results/env_smoke/) | student ("use the results from run on this machine") |
| D-02 | 2026-10-30 | Data: SciFact release tarball, sha256 recorded | Counts verified; revision/licence open (see ledger) | student |
| D-03 | 2026-10-30 | Verifier: TF-IDF + LogisticRegression, one model per condition, config tfidf-lr-d35269ef, seed 42 | Prompt07 fixed family; same train claims for A/B/C | protocol |
| D-04 | 2026-10-30 | Primary matched set = all_labeled (286 dev claims); secondary gold-evidence slice (182) | PC-001: keeps the 3-way task; the slice is the clean oracle comparison | student |
| D-05 | 2026-10-30 | Hold out 14 near-duplicate dev claims (Jaccard >= 0.9); declare sensitivity at >= 0.7 (209 / 127 claims) | PC-001, PC-003: 91 of 300 dev claims have a train twin at >= 0.7 | student (accepted assistant's recommendation) |
| D-06 | 2026-10-30 | Retrieval: BM25Okapi (rank-bm25 0.2.2), tokenizer \w+, top-5, ties by doc_id | PC-002; chosen before any retrieval metric was seen | student |
| D-07 | 2026-10-30 | Condition B = first rationale set per document; NEI claims keep empty evidence; rule baseline reported beside B | PC-004 from baseline-audit findings N1, N2 | student (accepted the corrections) |
| D-08 | 2026-10-30T13:27:56Z | Freeze configs/primary_frozen.yaml, then run A (rerun), B, C | RUN-001 | student |
| D-09 | 2026-10-30 | RQ3 codebook: 7 categories; "misread" merged with "decision error"; A errors not coded NO_EVIDENCE_SEEN; amendment 1 (categories 2, 3 do not apply to claims with no gold evidence) | PC-005, PC-006 | student; the gap behind PC-006 was missed by the assistant |
| D-10 | 2026-10-30 | RQ3 sample: 50 errors, equal allocation A 17 / B 17 / C 16, seed 42 | RUN-002; equal allocation was the assistant's choice, not in the protocol | student ("okay") |

## Headline findings (details: results/*.csv)
- Decision rule (Prompt05): a gain counts only if the estimate is >= 0.03 and the 95% paired-bootstrap CI excludes 0.
- B - A on the gold-evidence slice: +0.035, CI [-0.028, +0.097]: not supported. C - A: about 0 on every slice.
- B - A on all 286 claims is +0.123 with CI excluding 0, but B (0.499) is below the empty-evidence rule (0.601), so this is not evidence that evidence helps.
- On the 182-claim gold-evidence slice the empty-evidence rule predicts SUPPORT for every claim (macro-F1 0.401); A 0.314, B 0.349 and C 0.312 are all below it, and B - rule = -0.052 (CI [-0.093, -0.006]). On the 127-claim sensitivity slice B (0.427) is slightly above the rule (0.409), +0.018, CI [-0.040, +0.089], so that result is inconclusive.
- RQ2: BM25 Recall@5 = 164/182 = 0.901. Accuracy by hit/miss is confounded by label mix and n(miss) = 18.

## Next actions (status reconciled 10 November 2026)

The student has manually reviewed and verified all 50 RQ3 sample rows. The category counts are descriptive of this frozen, deliberately selected error sample; no population-prevalence claim or inter-annotator agreement statistic is made. The student also confirms that the complete test suite passes in the working project environment. Earlier entries below remain as historical decision records and are superseded where they conflict with this status.

Remaining optional research extensions are: (1) shuffled-label controls for B and C; (2) a Colab/GPU rerun; (3) an exploratory BM25 epsilon=0 check; and (4) identification of the immutable upstream SciFact revision to close the archive-to-licence provenance gap. These are extensions or provenance improvements, not prerequisites for describing the completed frozen development-set experiment.


## Post-review resolution (02 November 2026)

The earlier `UNKNOWN` entry about the review-to-gap link is superseded by the completed source crosswalk in `review_to_experiment_trace.md`. The original review's Sections 4.3, 4.8, 6.6, 8.6, 9.1, 9.2 and 9.6 motivate the bounded study of evidence availability, retrieval coverage and verifier outcomes. This is a conceptual bridge and a researcher's operational interpretation; it does not establish novelty. The paper explicitly acknowledges prior Oracle/Open scientific-claim verification work and does not claim a first-of-kind comparison.

The original RQ3 sample is preserved unchanged. A separate script and output apply only metadata-deterministic categories under the frozen codebook and PC-006 amendment. Six cases receive provisional metadata-only codes; 44 remain pending text review. The PC-006 assignment of `NO_EVIDENCE_SEEN` to C/NEI cases with retrieved non-gold documents is recorded with an explicit note so that the category's scope is not hidden.