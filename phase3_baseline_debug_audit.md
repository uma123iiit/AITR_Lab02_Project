# Phase III - AI-assisted coding, baseline validation and debugging audit

## Prompt 08 - Environment

The original local smoke log (2026-10-30) records Python 3.11.2, NumPy 2.4.6, SciPy 1.17.1, scikit-learn 1.9.1, rank-bm25 0.2.2, PyYAML 6.0.3, pandas 3.0.6, Matplotlib 3.11.2, Transformers 5.20.1, SentencePiece 0.2.2 and CPU-only PyTorch 2.15.0. The smoke test records data parsing, TF-IDF/logistic-regression plumbing, BM25 and TF-IDF retrieval, and an NLI model forward pass. CUDA was unavailable; this was a local CPU run, not a Colab GPU run.

## Prompt 09 - Baseline modules

Present in the archive: reusable modules for data/schema handling, input construction, classification, retrieval, metric computation, sampling and seed control; numbered scripts for audit, retrieval, A/B/C inference, evaluation, independent audit, shortcut baseline, RQ2 and RQ3 sampling; and unit-test source files. Model joblib files are not included and are intended to be rebuilt.

## Prompt 10 - Baseline validation (source-reported and audited)

The `baseline_validation.md` report states 18 checks: 12 PASS, 4 WARN, 2 INFO, 0 FAIL. It records independent metric recomputation from saved predictions (maximum absolute difference 1.1e-16), independent condition-A refit (probability difference 5e-09 due to stored precision), train-only vectorizer vocabulary check (9,018 terms vs 10,957 if dev had been used), independent BM25 top-5 replication on a 60-claim sample, Recall@5 recomputation and exact frozen A rerun. The archived run log confirms the later A/B/C runs under the frozen config.

**Audit chronology correction:** `results/validation/baseline_audit_20261030T132321Z.json` is the earlier audit snapshot and contains warnings that B/C had not yet run and A predated the freeze. Those warnings are timestamp-appropriate, not evidence that the later A/B/C run is absent. `logs/protocol_changes.md` RUN-001 records the post-freeze A rerun, B/C runs and evaluation. Keep the original audit intact; use the later RUN-001 record and `baseline_validation.md` for final status.

## Prompt 11 - Debugging examples recorded in the original AI log

The authentic project log records several real verification/correction examples: a shell pipefail/download-listing issue corrected after the download script aborted; a near-duplicate breakdown initially misreported by the assistant and manually re-derived; a missed smoke-test guide step later executed; a post-draw RQ3 codebook ambiguity for cases without gold evidence fixed through a versioned amendment before coding; and an overly broad claim about the empty-evidence rule corrected after inspecting the numeric table. It also records a relative-path hash-check failure that passed from the correct directory. These are source-reported events, not independently replayed here.

## Independent audit in this review environment

A fresh `python -m unittest discover -s tests -v` attempt was made with the available Python 3.13.5 container. The run could not complete: the container lacks `rank_bm25`, and network/DNS was unavailable when attempting to install rank-bm25==0.2.2. The discovery output showed 45 test cases, with 43 passing and 2 import errors for test modules that import the missing package. The original project baseline validation states 59 tests passed in its Python 3.11.2 environment, but a full stdout test transcript was not included in the ZIP. Do not merge these two different test environments or claim the present rerun passed.

## Corrections applied in this final package

1. Added a pinned `requirements.lock.txt` copied from the original smoke-test environment's captured `pip freeze` file, with a clear provenance header.
2. Added a phase-wise documentation set and final README mapping instructor prompts to actual evidence.
3. Preserved timestamped outputs and the old audit JSON without overwriting historical records; documented chronology.
4. Explicitly labelled the RQ3 sample as uncoded and removed any claim that taxonomy results exist.
5. Explicitly labelled missing original review, raw data, Colab rerun and clean-checkout reproduction as unresolved.