# Research Notebooks

## 01_reproducibility_workflow.ipynb

This notebook provides an entry point to the existing SciFact research
workflow. It uses the implementation under `src/`, command-line scripts
under `scripts/`, tests under `tests/`, and archived outputs under
`results/`.

The notebook:
- Checks the repository structure and Python environment.
- Verifies archived prediction outputs.
- Audits archived metrics and the preliminary RQ3 sample structure.
- Displays archived A/B/C development-set metrics and paper figures.
- Documents optional commands for rerunning the original data-dependent
  workflow after the raw SciFact data have been acquired.

## Important interpretation notes

The notebook's archived-output checks do not constitute a new experiment
or an independent reproduction. The displayed results are archived
development-set results, not test-set performance.

Raw SciFact data are not distributed in this repository. Follow
`data/README.md` before running data-dependent commands.

The RQ3 preliminary codes still require student verification and must not
be described as final human annotations. The full test suite must also
be verified in the specified Python 3.11.2 environment before claiming
complete reproducibility.
