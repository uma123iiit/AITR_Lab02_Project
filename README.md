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

## Instructor's required A–E submission checklist

The following checklist uses the five submission groups and wording specified in the assignment. It distinguishes repository evidence already present from actions or files that still need verification.

| Required item | Evidence currently in this repository | Status / remaining action |
|---|---|---|
| **A. Research paper** — final PDF, LaTeX source, `.bib`, figures; recommended 6–10 pages excluding references; use instructor-selected template if specified | `paper/Revised_SciFact_Research_Paper.pdf`, `paper/research_paper.tex`, `paper/references.bib`, `paper/CITATION_AUDIT.md`; figure exports are described in `paper/README.md` | PDF/source/bibliography are present. **Figure exports are not yet confirmed in `paper/figures/`**. Confirm final page count excluding references and verify whether the instructor specified a template. |
| **B. GitHub repository** — source code/notebooks, README, dependency versions, configs, reproducible commands, dataset acquisition instructions and evaluation scripts | `src/`, `scripts/`, `tests/`, `notebooks/01_reproducibility_workflow.ipynb`, `requirements.txt`, `requirements.lock.txt`, `configs/`, `data/README.md`, this README | Core repository components and instructions are present. Run the notebook and perform a clean-checkout reproduction; do not claim a successful full rerun until it has been completed. |
| **C. Experimental evidence** — actual CSV/log files, evaluation outputs, comparison tables, figures, random seeds and documented test conditions | `results/` contains metrics, predictions, retrieval outputs and comparison CSVs; `logs/` contains console/audit records; `configs/primary_frozen.yaml` records the frozen protocol and seed | Archived evidence is present. Results are from the matched development set. Figure files need uploading/verification; full test-suite and clean rerun evidence remain open. |
| **D. Research provenance** — one-page gap/decision brief, baseline validation report and concise AI prompt/code/verification log | `phase1_gap_matrix.md`, `research_decisions.md`, `baseline_validation.md`, `ai_assistance_log.md`, `review_to_experiment_trace.md` | The gap/decision trail, baseline report and AI-use log are present. Confirm that the gap/decision brief is formatted as a one-page submission artifact and that the AI log accurately reflects the student's work. |
| **E. Demonstration** — five-minute code-and-results walkthrough plus readiness for a short technical viva or rerun of one component | `demo_5min.md`, `viva_questions_and_answers.md` | Written preparation is present. The student must personally rehearse and deliver the walkthrough and be ready to explain or rerun one component. |

### Final actions before submission

- [ ] Add the six original PNG/PDF figure exports to `paper/figures/` and confirm they render on GitHub.
- [ ] Check the final paper is within the recommended 6–10 pages excluding references, and apply the instructor-selected template if one was specified.
- [ ] Run `notebooks/01_reproducibility_workflow.ipynb` from a clean Colab/local session and record actual outcomes.
- [ ] Install the pinned dependencies in Python 3.11.2 and run the **complete** test suite, including `test_inputs.py` and `test_retrieval.py`.
- [ ] Re-run the documented workflow from a clean checkout and preserve the resulting logs; distinguish this from archived-output verification.
- [ ] Verify all 50 preliminary RQ3 codes against the exact local SciFact snapshot and frozen codebook; record the student's decisions and review date. No independent second coder or Cohen's kappa is currently claimed.
- [ ] Confirm the one-page gap/decision brief and the AI prompt/code/verification log are ready as submission artifacts.
- [ ] Rehearse the five-minute demo and prepare to explain or rerun one component during the viva.
- [ ] Confirm the final paper, figures, and supporting evidence are the exact versions being submitted.

**Current completion statement:** The repository contains the main code, configurations, dependency records, dataset instructions, evaluation scripts, archived experimental evidence, provenance documents and written demonstration/viva preparation. This does not mean every A–E requirement is fully closed: figure exports, complete environment-matched testing, clean reproduction, student verification of RQ3, final manuscript/template checks, and the live demonstration remain student actions or need final verification.

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
