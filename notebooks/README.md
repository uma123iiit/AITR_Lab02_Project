# Research Notebooks

## 01_reproducibility_workflow.ipynb

This notebook provides an entry point to the existing SciFact research
workflow. It uses the implementation under `src/`, command-line scripts
under `scripts/`, tests under `tests/`, and archived outputs under
`results/`.

The notebook:
- Checks the repository structure and Python environment.
- Verifies archived prediction outputs.
- Audits archived metrics and the frozen, manually reviewed RQ3 sample structure.
- Displays archived A/B/C development-set metrics and paper figures.
- Documents optional commands for rerunning the original data-dependent
  workflow after the raw SciFact data have been acquired.

## Important interpretation notes

The notebook's archived-output checks do not constitute a new experiment
or an independent reproduction. The displayed results are archived
development-set results, not test-set performance.

Raw SciFact data are not distributed in this repository. Follow
`data/README.md` before running data-dependent commands.

The student has manually reviewed and verified all 50 rows in the frozen RQ3 sample. The recorded category counts describe this selected error sample only; they are not population prevalence estimates. No inter-annotator agreement statistic is reported because no independent second annotator was used.

The student confirms that the complete test suite passes in the working project environment. An earlier independent review-container run used a different Python environment and could not collect two retrieval-dependent test modules because `rank-bm25` was unavailable there. That historical environment-specific limitation should not be presented as a failure of the student's working project environment. Archived-output verification in this notebook remains distinct from a fresh end-to-end reproduction.
