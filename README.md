# Evidence Availability and Retrieval in Scientific Claim Verification

**Student:** Umakant Singh  
**Enrollment:** MNS2026009  
**Course:** AI Tools for Research | IIIT Allahabad  
**Dataset:** SciFact  
**Study type:** Controlled comparative development-set study

## Research question

On matched SciFact development claims, how do claim-only (A), claim + annotated gold evidence (B), and claim + BM25 top-five retrieved evidence (C) affect three-way scientific claim-verification performance? Supporting analyses examine retrieval Recall@5 and a prespecified error sample.

## Key archived results

| Condition | Accuracy (n=286) | Macro-F1 (n=286) |
|---|---:|---:|
| A — claim only | 0.4615 | 0.3757 |
| B — gold evidence | 0.6014 | 0.4988 |
| C — BM25 top-5 evidence | 0.4371 | 0.3650 |

On the 182-claim evidence-bearing subset, macro-F1 is A=0.3140, B=0.3492 and C=0.3119. The B-A difference is +0.0352 with 95% paired-bootstrap CI [-0.0275, +0.0974], so the predefined improvement rule is not met. BM25 Recall@5 is 164/182 = 90.11%. Retrieval success does not guarantee correct classification. These are development-set results, not test-set results.

## Repository structure

```text
AITR_Lab02_Project/
├── README.md
├── requirements.txt
├── requirements.lock.txt
├── .gitignore
├── configs/                 # experiment settings and frozen protocol/codebook
├── data/
│   └── README.md            # data access, format, provenance and licensing
├── notebooks/               # notebook status and any verified runnable notebooks
├── src/scifact_verif/       # reusable data, retrieval, verifier and metric modules
├── scripts/                 # download, audit, training, evaluation and analysis entrypoints
├── tests/                   # unit and focused validation tests
├── results/                 # archived metrics, predictions, audits and RQ3 materials
├── logs/                    # recorded command output and audit logs
├── paper/
│   ├── research_paper.tex
│   ├── references.bib
│   └── figures/              # final manuscript figures
├── research_decisions.md
├── baseline_validation.md
├── reproducibility_audit.md
├── ai_assistance_log.md
├── MANIFEST.md
└── FINAL_STUDENT_REVIEW_CHECKLIST.md
```

The repository contains executable Python modules, command-line scripts and tests. No Jupyter notebook is claimed unless a verified `.ipynb` file is added. Raw SciFact data, fitted private model objects and unverified notebook outputs are not included.

## Reproduction

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

The dataset download script uses the official AllenAI `release/latest` archive, a moving URL. Compare the downloaded archive's checksum with the historical SHA-256 in `data/README.md` before treating it as an exact reproduction.

## Verification and limitations

- The manuscript has been compiled and visually inspected; citation keys were checked against the bibliography.
- Archived prediction outputs were audited for hashes, row counts, claim IDs and metric consistency.
- Python compilation checks passed. The latest archived partial test run passed 51 tests with two dependency-blocked modules excluded. The complete test suite has **not** been verified successfully; `rank-bm25==0.2.2` was unavailable during the recorded audit.
- RQ3 contains AI-assisted preliminary codes for 50 frozen condition–claim rows (48 text-review judgments and two deterministic metadata assignments). These are not final human annotations; student verification remains required. No Cohen's kappa is claimed.
- The study reports development-set results only. It does not claim hidden test-set performance, a new neural architecture, or validation of the full nine-category literature-review taxonomy.
- Raw SciFact data are intentionally excluded. See `data/README.md` for provenance and licensing details.

## Dataset and citation

- [Official AllenAI SciFact repository](https://github.com/allenai/scifact)
- [Official SciFact dataset archive](https://scifact.s3-us-west-2.amazonaws.com/release/latest/data.tar.gz)
- Primary dataset paper: Wadden et al. (2020), *Fact or Fiction: Verifying Scientific Claims*, EMNLP.

## Submission status

This repository already contains the core implementation, scripts, tests, configurations, archived result tables, research documentation and LaTeX source. Before submission, verify that the selected final PDF and final figure exports are present under `paper/`, complete student verification of the RQ3 sample, and rerun the full test suite in the pinned environment. Do not represent any of these outstanding checks as complete until evidence is committed.
