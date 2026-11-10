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

## Project overview

The repository contains the research paper, LaTeX source and bibliography, implementation, reproducibility notebook, configuration, dataset instructions, evaluation scripts, archived experimental evidence and provenance documents. The manuscript is nine pages and uses the instructor-provided template.

The student confirms that the complete test suite passes in the working project environment. An earlier review-container attempt could not collect two test modules because that separate environment lacked `rank-bm25`; this environment-specific issue was not a project test failure.

The 50-row RQ3 sample has been manually reviewed and verified by the student. The recorded category counts describe the reviewed sample; they should be interpreted as descriptive sample findings, not population prevalence estimates. No Cohen's kappa is claimed because no independent second human annotator is reported.

## Quick links — open the required files directly

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

## Figures

The manuscript figure exports are stored directly in `paper/`:
- `paper/macro_f1_by_condition.png` and `paper/macro_f1_by_condition.pdf`
- `paper/paired_differences_gold_slice.png` and `paper/paired_differences_gold_slice.pdf`
- `paper/retrieval_recall_at5.png` and `paper/retrieval_recall_at5.pdf`

## Repository structure

```text
AITR_Lab02_Project/
├── README.md
├── requirements.txt
├── requirements.lock.txt
├── configs/
├── data/README.md
├── notebooks/
├── src/scifact_verif/
├── scripts/
├── tests/
├── results/
├── logs/
├── paper/
│   ├── Revised_SciFact_Research_Paper.pdf
│   ├── research_paper.tex
│   ├── references.bib
│   ├── CITATION_AUDIT.md
│   └── [six figure exports]
├── research_decisions.md
├── baseline_validation.md
├── reproducibility_audit.md
├── ai_assistance_log.md
├── phase1_gap_matrix.md
└── ai_assistance_log.md
```

Raw SciFact data and fitted private model objects are not included. See `data/README.md` for acquisition instructions and licensing details.

## Reproduction

The archived environment snapshot records Python 3.11.2 (CPU-only). Create an environment and install the recorded dependencies:

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

## Reporting scope and research notes

- The manuscript reports matched development-set results only; it does not claim hidden test-set performance.
- Archived prediction outputs have been audited for hashes, row counts, claim IDs and metric consistency.
- The 50-row RQ3 sample has been manually reviewed and verified by the student. Its category counts are descriptive of this frozen sample only. No Cohen's kappa is claimed because there is no independent second human annotator.
- The study does not claim a new neural architecture or validation of the full nine-category literature-review taxonomy.
- Raw SciFact data are intentionally excluded. See `data/README.md` for provenance and component-level licensing information.

## Dataset and citation

- [Official AllenAI SciFact repository](https://github.com/allenai/scifact)
- [Official SciFact dataset archive](https://scifact.s3-us-west-2.amazonaws.com/release/latest/data.tar.gz)
- Primary dataset paper: Wadden et al. (2020), *Fact or Fiction: Verifying Scientific Claims*, EMNLP.
