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

## Project progress and remaining work

I have organized the project around the research paper, implementation, experimental results, research decisions and the planned demonstration. The main paper files, source code, notebook, configuration, dataset instructions, evaluation scripts and archived results are available in this repository.

The experiments reported in the paper use the matched SciFact development set. They should not be described as test-set results. The archived outputs have been checked, but I have not yet completed a clean-checkout reproduction or verified the full test suite in the pinned environment. The latest recorded partial test run passed 51 tests; two modules were excluded because of dependency issues.

I still need to complete the final clean reproduction, check the manuscript against any template specified by the instructor, verify the preliminary RQ3 codes against the dataset, and rehearse the five-minute demonstration. The RQ3 codes are preliminary AI-assisted suggestions, not final human annotations. I have not calculated Cohen's kappa.

## Quick links — open the required files directly

Use these links instead of searching through folders:

### A. Research paper
- [Final research paper PDF](paper/Revised_SciFact_Research_Paper.pdf)
- [LaTeX source](paper/research_paper.tex)
- [Bibliography (.bib)](paper/references.bib)
- [Paper folder and build notes](paper/README.md)
- [Citation audit](paper/CITATION_AUDIT.md)

### B. GitHub repository and reproducibility
- [Reproducibility notebook](notebooks/01_reproducibility_workflow.ipynb)
- [Notebook instructions](notebooks/README.md)
- [Dependencies](requirements.txt) and [pinned dependency lock](requirements.lock.txt)
- [Experiment configuration](configs/primary_frozen.yaml)
- [Dataset acquisition instructions](data/README.md)
- [Source code](src/)
- [Scripts](scripts/)
- [Tests](tests/)

### C. Experimental evidence
- [Main comparison table](results/results.csv)
- [Paired comparison and confidence intervals](results/results_paired_differences.csv)
- [Retrieval hit/miss results](results/results_rq2_hit_miss.csv)
- [Rule-baseline comparison](results/results_rule_baseline_B.csv)
- [Evaluation console log](logs/eval_ABC_console.txt)
- [Archived-output audit log](logs/final_archived_output_audit.txt)
- [Frozen experiment configuration and seed](configs/primary_frozen.yaml)

### D. Research provenance
- [Gap matrix / Phase I brief](phase1_gap_matrix.md)
- [Review-to-experiment trace](review_to_experiment_trace.md)
- [Research decisions](research_decisions.md)
- [Baseline validation report](baseline_validation.md)
- [Reproducibility audit](reproducibility_audit.md)
- [AI assistance and verification log](ai_assistance_log.md)
- [Final student review checklist](FINAL_STUDENT_REVIEW_CHECKLIST.md)

### E. Demonstration and viva
- [Five-minute demonstration script](demo_5min.md)

**Viva preparation:** A separate viva Q&A file was listed in an earlier inventory, but its current GitHub path could not be verified. It is therefore not linked as an available file here.

### Figures

The paper uses three figures: the macro-F1 comparison across conditions, the paired differences on the gold-evidence subset, and BM25 Recall@5. I have uploaded the figure exports to the repository.

## Repository structure

```text
AITR_Lab02_Project/
├── README.md
├── requirements.txt
├── requirements.lock.txt
├── configs/                 # experiment settings and frozen protocol/codebook
├── data/
│   └── README.md            # data access, format, provenance and licensing
├── notebooks/               # reproducibility workflow notebook
├── src/scifact_verif/       # reusable data, retrieval, verifier and metric modules
├── scripts/                 # download, audit, training, evaluation and analysis entrypoints
├── tests/                   # unit and focused validation tests
├── results/                 # archived metrics, predictions, audits and RQ3 materials
├── logs/                    # recorded command output and audit logs
├── paper/
│   ├── Revised_SciFact_Research_Paper.pdf
│   ├── research_paper.tex
│   ├── references.bib
│   └── figures/              # add/verify final manuscript figures here
├── research_decisions.md
├── baseline_validation.md
├── reproducibility_audit.md
├── ai_assistance_log.md
├── phase1_gap_matrix.md
├── demo_5min.md
└── viva_questions_and_answers.md
```

Raw SciFact data and fitted private model objects are not included. See `data/README.md` for acquisition instructions.

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
