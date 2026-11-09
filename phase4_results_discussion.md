# Phase IV - Contribution, experimental results and interpretation

## Prompt 12 - Contribution pathway

**Selected pathway: B, controlled comparative study**, with descriptive failure analysis as a supporting component. The comparison is not claimed as the first of its kind: prior scientific claim-verification work already studies retrieval and oracle/open evidence settings. The project contribution is limited to an auditable matched-subset comparison, per-claim outputs, a near-duplicate sensitivity check, separate retrieval metrics, a shortcut control and a prespecified error-codebook workflow.

## Prompt 13 - Results from saved output files

All values below are read from timestamped result files and are development-set results from one frozen run. They are not official test results.

| Condition | n=286 Accuracy | n=286 Macro-F1 | n=182 accuracy | n=182 Macro-F1 |
|---|---:|---:|---:|---:|
| A - claim only | 0.4615 | 0.3757 | 0.3901 | 0.3140 |
| B - gold evidence | 0.6014 | 0.4988 | 0.4835 | 0.3492 |
| C - BM25 top-5 | 0.4371 | 0.3650 | 0.3736 | 0.3119 |

The 286-claim primary set includes three classes. The 182-claim evidence slice contains only SUPPORT and CONTRADICT; its macro-F1 is averaged over these two classes and is not directly interchangeable with the three-class metric.

On the primary set, CONTRADICT F1 is 0.0476 (A), 0.0444 (B) and 0.0659 (C); NOT_ENOUGH_INFO F1 is 0.5865, 0.8442 and 0.5616; SUPPORT F1 is 0.4929, 0.6078 and 0.4676. The verifier is especially weak at CONTRADICT classification.

The paired bootstrap estimates are B-A +0.1231 (95% CI [+0.0721, +0.1783]) on all 286 claims but this is confounded by empty evidence on NEI cases; B-A +0.0352 (95% CI [-0.0275, +0.0974]) on the 182 evidence-bearing claims, which is inconclusive. C-A is -0.0106 (95% CI [-0.0622, +0.0438]) on 286 claims and -0.0021 (95% CI [-0.0629, +0.0591]) on the evidence slice. No reliable improvement is established under the predeclared rule.

The rule `predict NEI iff B evidence is empty, otherwise predict SUPPORT` obtains accuracy 0.7902 and macro-F1 0.6009 on all 286 claims, exceeding B. This exposes an evidence-presence shortcut: the large full-set B-A difference cannot be interpreted as proof that gold evidence improves reasoning.

## Prompt 13 - RQ2 retrieval

| Retriever | Gold-document hits at 5 | Recall@5 |
|---|---:|---:|
| BM25 | 164/182 | 0.9011 |
| TF-IDF | 151/182 | 0.8297 |

High document Recall@5 does not guarantee correct evidence interpretation or verdict prediction. The hit/miss analysis is exploratory; the miss set is small.

## Prompt 14 - Discussion and negative results

Direct observations: B's full-set gain is confounded by empty-evidence NEI examples; the gain on the evidence-bearing slice is small and uncertain; C does not outperform A; BM25 retrieves a gold document for many claims but classification remains weak. Possible mechanisms such as bag-of-words difficulty with negation, directional relations or long-context dilution are hypotheses, not isolated causal findings.

## RQ3 status — AI-assisted preliminary, not human-final (02 November 2026)

The frozen sample remains 50 error rows (A=17, B=17, C=16; seed 42). A separate AI-assisted preliminary review assigns one provisional code to every row: `LABEL_DECISION_ERROR` 31, `AMBIGUOUS_ANNOTATION` 14, `OTHER_UNCERTAIN` 3, `NO_EVIDENCE_SEEN` 1 and `RETRIEVAL_MISS` 1. Only B/303 (`NO_EVIDENCE_SEEN`) and C/756 (`RETRIEVAL_MISS`) are deterministic metadata assignments; the remaining 48 are preliminary text-review judgments. The reviewed text came from public SciFact mirrors not checksum-matched to the exact historical experiment corpus. All 50 rows need student verification against the exact local corpus and condition-specific inputs. These counts are not final human-coded prevalence estimates; no second coder, Cohen's kappa or population-level taxonomy claim is reported.

## High-value follow-ups

1. Verify all 50 RQ3 preliminary labels against the exact dataset snapshot and condition inputs; obtain independent second-coder review if feasible.
2. Run shuffled-label controls for B/C and BM25 epsilon sensitivity checks.
3. Run all tests in the pinned Python 3.11.2 environment and record the full test output.
4. Pin the exact upstream dataset revision and confirm snapshot-level license provenance before considering raw-data redistribution.