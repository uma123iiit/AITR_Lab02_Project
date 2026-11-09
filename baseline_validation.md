# baseline_validation.md: baseline reproduction and validation report (Prompt 10)

Baseline: TF-IDF (ngram 1-2, min_df 1, max_features 100000) + LogisticRegression (C 1.0, lbfgs, max_iter 2000, seed 42),
config tfidf-lr-d35269ef, on SciFact claims; condition A (claim only) is the baseline, B and C are the evidence conditions.
This is the protocol's own baseline, not a reproduction of a published number. No comparison to paper or leaderboard
values is made, by design: the task framing, matched set and model family differ.
Audit file: results/validation/baseline_audit_20261030T132321Z.json (independent recomputation without repo modules).
Status 2026-10-30: 18 checks, 12 PASS, 4 WARN, 2 INFO, 0 FAIL.

## VERIFIED
| Check | Result |
|---|---|
| D1 label counts vs paper Table 2a (train, dev), corpus size 5183 | match; test labels private, test never used |
| D2 evidence documents are cited documents | 0 violations |
| D3 mixed SUPPORT/CONTRADICT across documents | 0 claims |
| A1 metrics recomputed with sklearn | max abs diff 1.1e-16 |
| A2 independent refit reproduces saved A probabilities | max abs diff 5e-09 (8-decimal storage) |
| A3 vocabulary built from train claims only (9018 terms; train+dev would give 10957) | no dev leakage into the vectorizer |
| R1 independent BM25 reimplementation (60 dev claims) | 0 mismatched ids, 0 mismatched scores |
| R2 Recall@5 recomputed (BM25 164/182, TF-IDF 151/182) | match |
| P1 config id, matched-id hash and corpus hash agree across run, retrieval and freeze | agree |
| Frozen rerun of A (after freeze) | 286/286 identical labels and input hashes, max abs probability difference 0 (RUN-001) |

## UNCERTAIN (open)
- S1: condition A macro-F1 is 2.0 SD above the shuffled-train-label mean (0.319 +/- 0.028 over 20 seeds): the baseline is only modestly above a pipeline that learns nothing. Shuffled-label controls for B and C have not been run.
- Upstream data revision remains unverified because release/latest is mutable. Component-level licence statements for the official SciFact repository are documented in data/README.md; the exact archived tarball is not mapped to an immutable upstream revision, so snapshot-specific licence association remains partially unresolved. Environment verified locally only; Colab untested.
- BM25 (rank-bm25 0.2.2, epsilon 0.25) gives negative-IDF terms a floor weight (15 terms, e.g. 'a', 'and', 'are', 'as', 'by', 'for'); effect on retrieval untested.
- C inputs average about 8,000 characters and the 100,000-feature cap binds for C; the evidence swamps the claim.

## NEEDS CORRECTION (found, corrected, logged)
| Finding | Action | Where |
|---|---|---|
| N2: B used the union of all rationale sets per document (75/182 dev claims have 2+ sets); undeclared | B changed to the first rationale set | PC-004 |
| N1: B on NEI claims has empty evidence, which equals NEI; B is an oracle only on the gold-evidence slice | rule baseline (NEI iff empty evidence) reported beside B; interpret on the slice | PC-004, results/results_rule_baseline_B.csv |
| N3: A ran before any frozen config existed | A rerun after freeze and compared exactly | RUN-001 |
| Near-duplicate and train-twin dev claims (14 at >= 0.9; 91 at >= 0.7) | hold-out plus declared sensitivity analysis | PC-001, PC-003 |

## Acceptable adaptations vs comparison-invalidating changes
- Acceptable and declared: all_labeled matched set, near-duplicate hold-out, first-rationale B, BM25 settings, local CPU run.
- Would invalidate comparison: changing the matched set, metric, bootstrap settings or model config after seeing B/C results; using test labels. None done.

## Test status reconciliation (final review, 2026-11-01)
The project record states that 59 unit tests passed in the original Python 3.11.2 environment. The supplied archive does not include the complete historical unittest stdout, so this is project-reported. A new run in the review container (Python 3.13.5) executed 45 tests: 43 passed and two test modules failed to import because `rank_bm25` was not installed. Network/DNS access was unavailable, so the dependency could not be installed during this review. This is a review-environment import blocker; it is not a rerun of training or a disproof of the archived run. Full rerun under the recorded environment remains required.

Not unit-tested in the archived record: scripts/10, 11, 12, 13 and the audit script itself (checked by hand and by the independent recomputation above).


## Emergency verification update (02 November 2026)

The codebase was recompiled successfully with Python 3.13.5. The available partial test run passes 46 tests when excluding only `test_inputs.py` and `test_retrieval.py`, both of which fail collection due to the missing `rank-bm25` dependency. The three RQ3 text-enrichment tests and five new deterministic metadata-code tests pass independently. The full suite remains blocked; Python 3.11.2 environment-matched execution is still required. Archived predictions/metrics were rechecked by `scripts/14_verify_saved_outputs.py`; this validates saved files, not model training or inference. Raw logs are under `logs/emergency_reaudit_20261102/`.