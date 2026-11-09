# Viva preparation — concise defensible answers

## 1. What is the problem?
Scientific claim verification requires both finding relevant research evidence and deciding whether it supports, contradicts, or does not resolve a claim. Retrieval and classification can fail separately.

## 2. What are A, B and C?
A receives only the claim. B receives the claim with annotated gold evidence (an oracle condition). C receives the claim with the top five abstracts retrieved by BM25.

## 3. Why SciFact?
It provides scientific claims, evidence-containing abstracts and rationale annotations for a focused verification task. The project uses 809 local training claims, 300 development claims and a 5,183-document corpus as recorded by its data audit.

## 4. Why 286 instead of all 300 development claims?
Fourteen claims with a near-duplicate training counterpart at token-set Jaccard similarity at least 0.9 were held out to reduce a possible train-development duplicate effect. A sensitivity analysis at threshold 0.7 was also recorded.

## 5. Why macro-F1?
The three labels are not evenly represented. Macro-F1 gives each class equal weight, so a strong score on a majority class cannot completely hide poor performance on a minority class. Accuracy is also reported.

## 6. What does Recall@5 = 90.11% mean?
For 164 of the 182 claims that have gold evidence, at least one gold evidence document appeared among the five BM25-ranked documents. It is a retrieval measure, not classification accuracy.

## 7. Why is condition B's full-set score misleading?
NOT ENOUGH INFO claims have no gold evidence. A classifier can exploit whether evidence is empty as a shortcut. The empty-evidence rule baseline outperforms B on the full matched set, so the full-set B advantage cannot be interpreted as evidence reasoning improvement.

## 8. What does the bootstrap interval tell us?
On the evidence-bearing subset, B-A macro-F1 is +0.0352, but the 95% paired-bootstrap interval is [-0.0275, +0.0974]. Because it includes zero, the evidence does not establish a reliable improvement under the predefined rule.

## 9. Why did high retrieval Recall@5 not improve C?
A hit only means a gold document is in the top five. The classifier may still fail to interpret the abstract, may be distracted by other retrieved documents, or may be limited by bag-of-words features. The experiment does not isolate which explanation is causal.

## 10. What is the contribution?
An auditable matched-subset comparison with per-claim outputs, near-duplicate sensitivity analysis, retrieval diagnostics, a shortcut baseline and transparent negative/inconclusive findings. The three-condition comparison itself is not claimed as novel; prior work already studies oracle/open scientific claim verification.

## 11. Is RQ3 complete?
No. The frozen 50-case sample is fixed, and a separate file now contains AI-assisted preliminary codes for all rows: 48 text-review judgments and two metadata-deterministic assignments (B/303 `NO_EVIDENCE_SEEN`, C/756 `RETRIEVAL_MISS`). The text came from public SciFact mirrors that are not checksum-matched to the exact historical local corpus. All 50 rows need student verification against that exact source. The preliminary distribution is not final human-coded prevalence; there is no independent second coder and no Cohen's kappa.

## 12. Why is the full test suite not complete?
The present audit container is Python 3.13.5 and lacks `rank-bm25==0.2.2`. Two test modules fail collection because that dependency cannot import, and package-index DNS prevented installation. Fifty-one tests pass when only those two modules are excluded. A complete run under the recorded Python 3.11.2 environment is still required.

## 13. Why not evaluate on the SciFact test split?
The official SciFact test labels are not public. This project reports only the labeled development-set evaluation and does not present development results as test performance.

## 14. What is the dataset licence status?
The official AllenAI licence page distinguishes CC BY 4.0 claim/evidence annotations, ODC-By 1.0 S2ORC abstracts and Apache 2.0 repository code. The experiment archive came from a moving `release/latest` URL, not a pinned commit, so the exact archive-to-revision association remains unresolved. Raw data are therefore excluded.

## 15. What would you do next?
Complete the 44 text-based RQ3 reviews and check the six pre-codes, run the full test suite in Python 3.11.2 with pinned dependencies, pin the exact dataset revision, then perform further controlled ablations such as shuffled-label controls or retrieval sensitivity.