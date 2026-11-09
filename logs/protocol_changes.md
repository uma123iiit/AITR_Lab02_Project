# Protocol-change log (Prompt07 section 14)

## PC-001, 2026-10-30: matched-set policy and near-duplicate hold-out
- **Old setting:** matched-set policy undecided (`all_labeled` vs `evidence_only`); near-duplicate handling undecided.
- **New setting (decided by researcher):**
  1. Primary matched set = `all_labeled` (dev claims with a gold class; NEI claims kept, condition B input = claim with empty evidence, flagged `b_evidence_empty`).
  2. Secondary analysis, declared BEFORE any model run: the same saved predictions sliced to matched claims with >=1 gold evidence document (`rq2_eligible_claim_ids.txt`). Macro-F1 on this slice is computed over SUPPORT and CONTRADICT only (NEI has no gold support there). Report paired B-A, C-A, B-C with the same bootstrap settings.
  3. Dev claims that near-duplicate a train claim (token-set Jaccard >= 0.9) are held out of evaluation (reason `NEAR_DUPLICATE_OF_TRAIN_CLAIM`). Train is unchanged.
- **Reason:** feasibility and leakage control (data issue). `all_labeled` keeps the official three-way task. B on NEI claims has no real gold evidence, and "empty evidence" predicts NEI in training, so the 188-style slice is the clean oracle comparison. Held-out dev claims could be memorised via their train twins.
- **Evaluation outputs inspected before this change?** Only the data audit (counts, near-duplicate list). No model predictions or metrics exist yet.
- **Claims/splits rerun:** dev audit re-run with `--near-dup holdout`; earlier outputs kept in `results/audit/superseded_pre_nd_holdout/`.
- **Counts after the change (dev):** total 300, matched 286 (NEI 104, SUPPORT 122, CONTRADICT 60), held out 14, matched with empty gold evidence 104, gold-evidence slice / RQ2 denominator 182.
- **Comparability:** primary run. Counts differ from the earlier 300 / 188 by exactly the 14 held-out claims (6 of them had gold evidence, 8 were NEI; verified against the superseded all_labeled output).
- **Approved by:** researcher.
- **Known limitation to report:** in B, the NEI/empty-evidence shortcut inflates B on the all-claims set; interpret B-A and B-C on the gold-evidence slice.

## PC-002, 2026-10-30: retrieval settings fixed before the first retrieval run
- **Old setting:** tokenizer and retrieved claim sets left open by Prompt07 (section 4A fixes method, k=5 and tie rule only).
- **New setting:** BM25 tokenizer = `\w+` on lowercased text (no stopwords, no stemming). TF-IDF uses the same token basis (`token_pattern=(?u)\b\w+\b`, unigrams+bigrams, L2). Ties break by ascending numeric doc_id. BM25 = rank-bm25 0.2.2 BM25Okapi defaults (k1=1.5, b=0.75, epsilon=0.25). Retrieval runs for all 809 train claims (needed to train condition C) and the 286 frozen matched dev claims. MRR@10 skipped: top-10 was not predeclared.
- **Reason:** feasibility; the protocol left these unspecified. Chosen before any dev retrieval metric was seen.
- **Evaluation outputs inspected before this change?** Condition A metrics only. No retrieval output existed.
- **Claims/splits rerun:** none, first retrieval run (results/retrieval/retrieval_20261030T131217Z).
- **Comparability:** primary run. Note BM25Okapi replaces negative IDF values (terms in over half of documents) with epsilon times the average IDF; this is the library's behaviour.
- **Approved by:** researcher (accepted in session after the choices were explained; recorded when PC-003 was approved).

## PC-003, 2026-10-30: declared sensitivity analysis for train-twin dev claims
- **Old setting:** only dev claims at token-set Jaccard >= 0.9 to a train claim were held out (14 claims, PC-001).
- **New setting:** the primary analysis is UNCHANGED (286 matched claims; 182 gold-evidence slice). Added a declared sensitivity analysis: the matched set minus dev claims with a train twin at Jaccard >= 0.7. Files: `results/audit/dev_all_labeled_nd-holdout/sensitivity_j0.7_matched_claim_ids.txt` (209 claims: SUPPORT 88, CONTRADICT 39, NEI 82) and `sensitivity_j0.7_gold_evidence_claim_ids.txt` (127 claims). Same predictions, scored on the smaller sets; same metrics and bootstrap settings. Macro-F1 on the gold-evidence slice is over SUPPORT+CONTRADICT as in PC-001.
- **Reason:** data issue found after Cycle 3: 91 of 300 dev claims have a train claim at Jaccard >= 0.7 (116 at >= 0.6), mostly paraphrase or negated minimal pairs, often with opposite labels. Changing the primary threshold after seeing condition A dev scores would be post hoc, so it is added as a sensitivity analysis instead.
- **Evaluation outputs inspected before this change?** Yes: condition A metrics on the primary sets and BM25/TF-IDF Recall@5 had been seen. Condition A scores on the sensitivity sets had NOT been computed when this was declared. Conditions B and C do not exist yet.
- **Claims/splits rerun:** none; ID files derived from the existing frozen matched set (primary files verified byte-identical).
- **Comparability:** sensitivity analysis only, never the headline. If primary and sensitivity conclusions disagree, report both.
- **Approved by:** researcher (accepted my recommendation, threshold 0.7).

## PC-004, 2026-10-30: condition B definition (baseline validation findings N1, N2) and freeze order (N3)
- **Old setting:** B took the union of all annotated rationale sets per document (not declared in the protocol); NEI handling in B and how to read B undefined.
- **New setting (researcher accepted the report's recommended options):**
  1. **N2:** B uses the FIRST annotated rationale set of each evidence document, in file order. `data.gold_evidence(..., rationale="first")` is the frozen default; `"union"` stays available for an exploratory variant. Index validity is checked over all sets either way; gold document ids do not depend on the policy.
  2. **N1:** NEI claims keep empty evidence in B. B is an oracle only on the gold-evidence slice (182 claims; 127 in the j0.7 sensitivity set). Interpret B-A and B-C on that slice. The paper-style pseudo-rationale variant (top-k TF-IDF sentences from the cited abstract for NOINFO claims) is NOT run unless declared separately. A rule baseline (predict NEI iff evidence is empty) must be reported next to B.
  3. **N3:** condition A ran before any frozen config. After `primary_frozen.yaml` is written, A is rerun through `07_run_condition.py` and must reproduce results/predictions/A_tfidf-lr-d35269ef_20261030T130731Z (identical input_text_hash, probabilities within 1e-7).
- **Reason:** baseline validation (results/validation/baseline_audit_20261030T132321Z.json): 75 of 182 matched dev claims with evidence have 2+ rationale sets in a document (mean evidence sentences 1.91 union vs 1.22 first); empty evidence equals the NEI set exactly (304 train, 104 dev).
- **Evaluation outputs inspected before this change?** Condition A metrics and retrieval Recall@5 only. No B or C predictions or metrics exist.
- **Claims/splits rerun:** none. Frozen matched, slice and sensitivity files verified byte-identical after the code change.
- **Comparability:** primary run definition. B text is shorter than in the dry run before this change (mean 270 vs 369 chars, train).
- **Approved by:** researcher.

## RUN-001, 2026-10-30: primary A/B/C run under configs/primary_frozen.yaml (frozen 13:27:56 UTC)
- Gates: baseline validation (12 pass, 4 warn, 0 fail); researcher confirmed the B/C inputs; frozen A rerun reproduced the pre-freeze A run exactly (286/286 identical labels and hashes, max |dp| = 0).
- Runs: A_tfidf-lr-d35269ef_20261030T132802Z, B_tfidf-lr-d35269ef_20261030T132814Z, C_tfidf-lr-d35269ef_20261030T132826Z (retrieval_20261030T131217Z, BM25 top-5). Evaluation: results/metrics/eval_20261030T132835Z; rule baseline: results/metrics/rule_baseline_B_20261030T132905Z.json; console: logs/eval_ABC_console.txt.
- Observed at run time: C vocabulary hit the 100,000-feature cap (uncertainty U6 confirmed as binding).
- No protocol values were changed after seeing these results. Development-set results, single frozen run.
- Not yet done: RQ2 accuracy by hit/miss, RQ3 codebook and error sample, shuffled-label controls for B and C, Colab rerun, epsilon=0 retrieval check.

## PC-005, 2026-10-30: RQ3 error codebook frozen
- **Old setting:** `primary_frozen.yaml` records `rq3.codebook: NOT FROZEN`. That file is not edited (it is frozen); this entry supersedes that one field.
- **New setting:** `configs/rq3_codebook.FROZEN.md`, seven single-label categories (NO_EVIDENCE_SEEN B/C only, RETRIEVAL_MISS, EVIDENCE_IRRELEVANT, LABEL_DECISION_ERROR, INPUT_FORMAT_TRUNCATION, AMBIGUOUS_ANNOTATION, OTHER_UNCERTAIN). Researcher decisions: merged "misread" and "decision error"; condition A errors are not coded NO_EVIDENCE_SEEN. Hash in `configs/rq3_codebook.FROZEN.md.sha256`.
- **Evaluation outputs inspected before this change?** Aggregate metrics, confusion matrices and the RQ2 hit/miss table (the A-handling decision was made after seeing it). No individual error case had been read. The error sample has NOT been drawn.
- **Claims/splits rerun:** none.
- **Comparability:** RQ3 is descriptive, single-annotator unless a second annotator codes the same sample independently.
- **Approved by:** researcher.
- RQ2 hit/miss also completed under RUN-001: `scripts/11_rq2_hit_miss.py`, `results/metrics/rq2_hit_miss_20261030T140935Z.json` (descriptive; confounded by label mix; no unit tests for the script).

## RUN-002, 2026-10-30: RQ3 error sample drawn (after PC-005 freeze)
- `scripts/12_draw_rq3_sample.py` (hash-checks the frozen codebook first; refuses to redraw). Population: 154 A, 114 B, 161 C errors on the 286 matched dev claims. Equal allocation across conditions (a choice not specified by the protocol, declared here): A 17, B 17, C 16 = 50, seed 42.
- Outputs: `results/rq3/rq3_sample.csv` (empty coder columns), `results/rq3/rq3_sample_meta.json` (seed, counts, codebook and prediction-file hashes). Console: `logs/rq3_sample_console.txt`. Unit tests for allocation and draw: `tests/test_sampling.py` (59 tests pass). The draw script itself has no test.
- No sampled case had been read when drawn. Coding not started. Single annotator unless a second independently codes the same sheet.

## PC-006, 2026-10-30: RQ3 codebook amendment 1 (scope of categories 2 and 3)
- **Old setting:** frozen codebook (PC-005) defines RETRIEVAL_MISS and EVIDENCE_IRRELEVANT relative to a gold document; undefined for claims with no gold evidence.
- **New setting:** `configs/rq3_codebook.AMENDMENT-1.md` (hash in `.sha256`): for claims with empty gold_evidence_doc_ids, categories 2 and 3 do not apply. The frozen file is not edited and still verifies.
- **Found by:** post-draw check of the sample sheet (4 of 16 C rows had blank hit status); see the verification output in the session.
- **Evaluation outputs inspected before this change?** Aggregate results; sheet columns only (conditions, labels, flags). No sampled case was read or coded.
- **Claims/splits rerun:** none; sample unchanged (sample_csv_sha256 in rq3_sample_meta.json).
- **Approved by:** researcher.