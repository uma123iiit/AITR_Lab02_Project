# Phase II - Dataset, baselines and frozen experiment protocol

## Dataset and source

SciFact is the primary dataset. The archived audit records 809 train claims, 300 dev claims, a 5,183-document corpus and 300 unlabeled test claims. In the original run, the test split was not used for metric evaluation. The 286-claim primary development matched set excludes 14 near-duplicate train/dev pairs at token-set Jaccard >= 0.9. The gold-evidence slice comprises 182 claims (60 CONTRADICT, 122 SUPPORT); the remaining 104 matched claims have no annotated gold evidence and map to NOT_ENOUGH_INFO (NEI). The Jaccard >= 0.7 sensitivity set contains 209 matched claims, including a 127-claim gold-evidence slice.

**License caveat:** The official SciFact repository's LICENSE page distinguishes claim/evidence annotations (CC BY 4.0), corpus abstracts from S2ORC (ODC-By 1.0), and code (Apache 2.0). The Hugging Face dataset card separately displays CC BY-NC 2.0. This is a material metadata discrepancy; the archive itself marks license as unresolved. This package therefore excludes raw data and does not grant redistribution permission. Confirm applicable source-corpus terms and record the exact data revision before public release.

## Data split and leakage controls

- Fit the supervised verifier on `claims_train.jsonl`; evaluate only on the fixed eligible development claims.
- Do not call the development set a held-out test set. Official test labels are not public and the official repository directs test evaluation through its leaderboard.
- The corpus is the retrieval candidate pool. Gold evidence IDs/labels are used only for B/oracle construction and post-hoc retrieval scoring, never for BM25 or TF-IDF ranking.
- IDs and labels are checked; same matched IDs are used across A/B/C.
- 14 dev claims with train twins at Jaccard >= 0.9 are held out. A separately disclosed stricter Jaccard >= 0.7 sensitivity analysis is reported; it does not replace the primary evaluation.

## Conditions and model

A: claim text only. B: claim plus the first annotated rationale set per evidence document in file order; NEI examples have empty evidence and are therefore not an oracle comparison. C: claim plus BM25 top-5 title + abstract text. Each condition has a separately fitted TF-IDF + Logistic Regression verifier using the same train split, algorithm family and frozen config. Settings: unigram/bigram TF-IDF, min_df=1, max_features=100000, LogisticRegression C=1, lbfgs, max_iter=2000, random_state=42, no class weighting, argmax prediction. BM25 uses rank-bm25 0.2.2, k1=1.5, b=0.75, epsilon=0.25, lowercase `\w+` tokenization, top-5, doc-ID tie break. TF-IDF retrieval is a second retrieval comparator.

## Metrics and deep analysis

Classification: macro-F1 (primary), accuracy, per-class precision/recall/F1, confusion matrices. Paired bootstrap: 2,000 resamples of claim IDs, seed 42, percentile 95% interval. Retrieval: document-level Recall@5 over the 182 claims with annotated gold evidence. Deeper analysis: paired condition contrasts; near-duplicate sensitivity; BM25-vs-TF-IDF retrieval; hit/miss stratification; empty-evidence rule control; planned taxonomy-coded error analysis (not yet coded).

## Flow

`Train claims + condition-specific inputs -> TF-IDF vectorizer -> Logistic Regression -> saved per-claim probabilities/predictions -> matched-ID evaluation -> paired bootstrap and confusion matrices`. In parallel: `claim query -> frozen BM25 / TF-IDF corpus ranker -> top-5 documents -> Recall@5 against gold IDs (post-hoc only) -> C verifier input`.

## Protocol caveats

The A/B/C design compares separately fitted models under matched training data and a shared algorithm family; it is not the same as intervening on the input of one frozen single trained model. This is an important scope distinction. Gold evidence is oracle information. B on NEI is an empty-evidence condition and can exploit the NEI-equals-empty-evidence relationship. C inputs are long, the feature cap binds, and BM25's epsilon floor for frequent terms was not sensitivity-tested.