# Evidence Availability and Retrieval in Scientific Claim Verification

**Student:** Umakant Singh  
**Enrollment:** MNS2026009  
**Course:** AI Tools for Research | IIIT Allahabad  
**Dataset:** SciFact  
**Study type:** Controlled comparative development-set study

## Dataset download

This project uses the **SciFact** scientific claim-verification dataset released by AllenAI.

- **[Download the official SciFact dataset archive (data.tar.gz)](https://scifact.s3-us-west-2.amazonaws.com/release/latest/data.tar.gz)**
- [Official AllenAI SciFact repository and dataset documentation](https://github.com/allenai/scifact)
- [Dataset schema documentation](https://github.com/allenai/scifact/blob/master/doc/data.md)
- [Official component licence statements](https://github.com/allenai/scifact/blob/master/LICENSE.md)

To download and extract the current official archive from the repository root:

```bash
bash scripts/01_download_data.sh
```

The script downloads the current `release/latest` archive. This is a moving URL and may not be byte-identical to the historical snapshot used for the archived experiments. The project records the historical SHA-256 in `data/README.md`; compare hashes before treating a newly downloaded archive as an exact reproduction. Raw dataset files are intentionally not committed to this repository. See `data/README.md` for source, split, provenance and licence details.

## Research question
On matched SciFact development claims, how do claim-only (A), claim + annotated gold evidence (B), and claim + BM25 top-five retrieved evidence (C) affect three-way scientific claim-verification performance? Supporting analyses examine retrieval Recall@5 and a prespecified error sample.

## Key results (archived development run)

| Condition | Accuracy (n=286) | Macro-F1 (n=286) |
|---|---:|---:|
| A - claim only | 0.4615 | 0.3757 |
| B - gold evidence | 0.6014 | 0.4988 |
| C - BM25 top-5 evidence | 0.4371 | 0.3650 |

On the 182-claim evidence-bearing subset, macro-F1 is A=0.3140, B=0.3492 and C=0.3119. The B-A difference is +0.0352 with 95% paired-bootstrap CI [-0.0275, +0.0974], so the predefined improvement rule is not met. BM25 Recall@5 is 164/182 = 90.11%; retrieval success does not guarantee correct classification. All values are development-set results, not test-set results.

## Repository map
- `src/scifact_verif/` - data, input formatting, retrieval, classifier, metrics and RQ3 helpers.
- `scripts/` - download/audit, retrieval, training, evaluation, saved-output audit and RQ3 enrichment/pre-coding.
- `tests/` - unit/sanity tests.
- `configs/` - experiment and frozen protocol/codebook.
- `results/` - timestamped actual metrics, predictions, retrieval ranks, tables and figures.
- `logs/` - actual console outputs, protocol changes, environment and audit logs.
- `paper/` - LaTeX manuscript source, bibliography, citation audit and reference notes. The compiled PDF and figure image assets are not part of the current GitHub upload yet.
- `data/README.md` - dataset download link, acquisition, split and component-license provenance; raw data are excluded.
- `research_decisions.md`, `review_to_experiment_trace.md`, `baseline_validation.md`, `ai_assistance_log.md` - research provenance and verification.
- `FINAL_STUDENT_REVIEW_CHECKLIST.md` - submission, reproducibility and RQ3 student-review checklist.

## Reproduction (test required on a clean machine)
Use the recorded Python 3.11.2 CPU environment. Raw dataset files are not distributed.

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.lock.txt
bash scripts/00_check_compat.sh
bash scripts/01_download_data.sh
python scripts/env_smoke_test.py
python scripts/02_audit_data.py
PYTHONPATH=src python -m pytest -q
```

For archived-result verification without raw data:

```bash
PYTHONPATH=src python scripts/14_verify_saved_outputs.py
```

For the separate metadata-only RQ3 pre-code and claim text worklist (the latter needs local raw `claims_dev.jsonl`; abstracts are not in this archive):

```bash
PYTHONPATH=src python scripts/18_partial_rq3_metadata_codes.py
python scripts/17_enrich_rq3_sample.py --data-dir data/raw/scifact
```

The second command must be run only where the exact matching SciFact `claims_dev.jsonl` and `corpus.jsonl` are available. The generated text packet contains dataset text and must remain local.

## Implementation and verification status (02 November 2026)

- **Manuscript preparation:** The LaTeX manuscript was successfully compiled into an eight-page A4 document. The rendered pages were inspected for formatting and layout issues.
- **Citation verification:** The citation keys used in the manuscript were checked against the bibliography entries. The results are documented in `paper/CITATION_AUDIT.md`.
- **Archived results verification:** The saved prediction files were checked for consistency, including file hashes, row counts, claim identifiers, accuracy, and macro-F1 scores. The archived outputs passed these checks.
- **Code and test verification:** Python compilation checks (`compileall`) completed successfully. A partial test run passed 51 tests. Two test modules, `test_inputs.py` and `test_retrieval.py`, could not be collected because the required `rank-bm25==0.2.2` dependency was unavailable. Three additional RQ3 enrichment tests and five metadata-coding tests passed independently. Therefore, the complete test suite has not yet been verified successfully.
- **Environment limitation:** The project specifies Python 3.11.2. During a later audit using Python 3.13.5, a package-index DNS failure prevented installation of the missing dependency. The complete test suite should be rerun in the specified environment after resolving this dependency issue. Relevant logs are available in `logs/emergency_reaudit_20261102/`.
- **RQ3 preliminary analysis:** Preliminary AI-assisted codes were generated for all 50 frozen condition–claim combinations. These include 48 text-based review judgments and two deterministic metadata assignments: B/303 (`NO_EVIDENCE_SEEN`) and C/756 (`RETRIEVAL_MISS`). These codes are intended to support the subsequent review process and should not be treated as final human annotations. All 50 cases still require student verification. No inter-annotator agreement statistic, such as Cohen's kappa, is claimed.
- **Dataset provenance:** The experiments used the official AllenAI SciFact dataset archive. The original acquisition record contains a SHA-256 checksum, but the download URL (`release/latest`) does not identify an immutable upstream version. The raw dataset is therefore excluded from the public repository. The download source, checksum, and licensing information are documented in `data/README.md`.

## Data licensing and handling
The official AllenAI repository license describes claims/evidence annotations as CC BY 4.0, S2ORC-derived corpus abstracts as ODC-By 1.0, and repository code as Apache 2.0. The exact `release/latest` archive is not mapped to an immutable commit, so raw files are not redistributed. The separate Hugging Face mirror reports different licence metadata and split structure; it was not used for the archived run. See `data/README.md`.

## Contribution boundary
This is a controlled comparison with a simple lexical verifier, not a new neural architecture or a first-of-kind oracle/open study. The prior literature review motivates evidence provenance and retrieval risk, but the implementation does not test free-form LLM generation or validate the full nine-category literature-review taxonomy. See `review_to_experiment_trace.md`.

## Citation
The primary dataset paper is Wadden et al. (2020), *Fact or Fiction: Verifying Scientific Claims*, EMNLP. The full bibliography is in `paper/references.bib`.

## GitHub upload status
The repository includes the core Python source modules, scripts, tests, frozen configurations, research/provenance documents, LaTeX manuscript source, bibliography, selected archived result tables and selected audit logs. Some binary PDF/PNG assets and additional result/log files are not yet uploaded. Raw SciFact data remain intentionally excluded; use the official dataset link above to obtain the data locally. Do not interpret this as a complete mirror of the prepared ZIP until the remaining assets are added.
