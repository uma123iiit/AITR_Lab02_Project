# Research Paper

This directory contains the research manuscript, bibliography, citation
audit, compiled manuscript PDF, and figure assets used by the paper.

## Main files

- `Revised_SciFact_Research_Paper.pdf` — revised compiled manuscript.
- `research_paper.tex` — editable LaTeX manuscript source.
- `references.bib` — bibliography database.
- `CITATION_AUDIT.md` — citation-key and reference consistency audit.
- `REFERENCES_NOTE.md` — supporting reference notes.
- `references_manual.tex` — manually managed reference material retained
  for review.

## Figures

The manuscript figure exports are stored directly in this directory:

- `macro_f1_by_condition.png` and `macro_f1_by_condition.pdf`
- `paired_differences_gold_slice.png` and
  `paired_differences_gold_slice.pdf`
- `retrieval_recall_at5.png` and `retrieval_recall_at5.pdf`

Keep both PNG and PDF versions. PNG files are convenient for previewing in
GitHub; PDF files preserve vector-quality output for publication and printing.
Do not regenerate or alter the figures without checking that they remain
consistent with the archived results and manuscript.

## Scope and reporting

The manuscript reports results from the matched SciFact development set.
It does not report performance on the hidden official test labels. The study
compares claim-only, gold-evidence, and BM25-retrieved-evidence conditions
using the archived experimental outputs.

The 50-row RQ3 sample was manually reviewed and verified by the student.
Its category counts are descriptive of this frozen sample and should not be
interpreted as population prevalence estimates. No inter-annotator agreement
statistic is reported because no independent second human annotator is
reported.

## Build instructions

The LaTeX source has been updated to reflect the student's completed manual review of the 50-case RQ3 sample and to use the figure filenames present directly in this directory. The committed `Revised_SciFact_Research_Paper.pdf` is still the previous compiled build and must be regenerated from the current `research_paper.tex` before submission. If rebuilding,
compile `research_paper.tex` with a LaTeX distribution and BibTeX installed.
Run the usual LaTeX–BibTeX–LaTeX–LaTeX sequence from this directory, or use the equivalent build command supported by your TeX distribution. The source references figure files in this same directory. Inspect the regenerated PDF for references, figure placement, page breaks, and layout.

## Reproducibility and data

Raw SciFact data are not included. Follow the download and provenance
instructions in the repository's `data/README.md`. The official
`release/latest` URL is a moving target; compare the downloaded archive
checksum with the historical value recorded in the project documentation
before treating it as the same dataset snapshot.

The notebook-based entry point is
`notebooks/01_reproducibility_workflow.ipynb`. It verifies archived outputs
and documents optional rerun commands; archived-output verification alone
does not constitute a new experiment or independent reproduction.
