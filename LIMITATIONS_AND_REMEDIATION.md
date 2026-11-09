# Limitations and remediation plan

This document distinguishes repository-maintenance work from checks requiring original data, a suitable runtime, or student review. It is a status record, not a claim that unfinished work has been completed.

## Completed repository-maintenance actions

- The repository manifest and contents index have been reconciled with the current GitHub tree.
- Stale references to the old A–E packaging folders and notebook-status file have been removed.
- The README distinguishes the GitHub source-and-evidence repository from the larger submission ZIP.
- Official SciFact component licence statements are recorded in data/README.md. The original frozen configuration is retained unchanged; its historical unresolved fields are explained by the protocol reconciliation note.

## Remaining technical limitations

| Limitation | Current evidence | Required action | Can be completed from this repository alone? |
|---|---|---|---|
| Full test suite | In the available Python 3.13.5 runtime, collection fails for test_inputs.py and test_retrieval.py because rank-bm25==0.2.2 is absent. Installation was blocked by package-index DNS/network failure. | In Python 3.11.2, install requirements.txt (or the recorded lock in a compatible environment), run PYTHONPATH=src python -m pytest -q and save the unedited output. | No; dependency installation/runtime access is required. |
| Clean-checkout reproduction | Archived predictions and metrics have been integrity-audited; this is not a fresh training/inference run. | Clone the repository, acquire the exact data snapshot, run the README commands and preserve outputs/logs. | No; exact source data and a working environment are required. |
| Dataset identity | Historical archive SHA-256 is recorded, but the original tarball and immutable upstream revision are not included. The download URL is a moving release/latest pointer. | Locate the original archive or an authoritative immutable release matching the recorded checksum; do not silently substitute another snapshot. | No; original archive/upstream provenance is required. |
| RQ3 annotation | Fifty AI-assisted preliminary codes exist; 48 text judgments require human verification against the exact local experiment snapshot. | Review all 50 cases against the original claims_dev.jsonl, corpus.jsonl, actual model inputs and frozen codebook; record decisions, reviewer and date. | No; original data and student judgement are required. |
| Inter-annotator reliability | No independent second coder is documented. | If required, have a second coder independently label the same sample before calculating agreement. | No; a second human annotator is required. |
| Paper build and figures | LaTeX source and bibliography are in the repository; compiled PDF and figure exports are not in the current GitHub tree. A local build attempt stopped because BibTeX is not installed. | Build in a TeX environment with LaTeX, BibTeX and required packages; inspect all pages and figures; then add the PDF and figure exports. | No, not in the current runtime. |
| Notebook deliverable | No .ipynb is included; scripts and modules are the executable workflow. | Only if the assignment explicitly requires it, create a notebook wrapper that calls the real scripts and rerun every cell. | Possible, but data/runtime are needed. |
| Live demonstration | No recording or proof of live demonstration is included. | Student performs or records the demonstration if required. | No; student action is required. |

## Interpretation limits that must remain visible

- Results are from a matched SciFact development subset, not the hidden official test split.
- Gold-evidence condition B is confounded on the full set because NEI examples have empty evidence. The 182-claim evidence-bearing slice is the more defensible oracle comparison; its B–A macro-F1 difference is small and its 95% paired-bootstrap interval includes zero.
- BM25 Recall@5 is a retrieval metric, not a measure of whether the classifier interpreted evidence correctly.
- The verifier is a TF–IDF/logistic-regression baseline; the study does not establish performance for generative LLMs or modern RAG systems.
- RQ3 counts remain exploratory until the student verifies the preliminary codes. Do not report them as final human-coded prevalence or calculate Cohen's kappa without an independent second coder.
- The release/latest dataset URL is mutable. The historical hash identifies the archived byte artifact only if the original hash record is trusted; it does not identify an upstream release by itself.

## Submission decision

Do not describe the repository as fully reproduced, fully human-verified, or notebook-complete unless the corresponding checks have actually been performed. Use FINAL_STUDENT_REVIEW_CHECKLIST.md to record completion.
