# Research paper

## Manuscript files

- `research_paper.tex` — editable LaTeX manuscript.
- `references.bib` — bibliography database.
- `CITATION_AUDIT.md` — citation-key and reference consistency audit.
- `references_manual.tex` — manually managed reference material retained for review.

The compiled PDF and figure exports are not currently included in this GitHub repository. The manuscript was previously compiled as an eight-page A4 document and its rendered pages were inspected in the review environment. Recompile the current source before submission if any manuscript or bibliography files have changed.

## Scope and reporting

The manuscript reports results from the matched SciFact development set. It does not report results on the hidden official test labels. The study compares claim-only, gold-evidence and BM25-retrieved-evidence conditions using the archived experimental outputs.

The RQ3 sample has a preliminary AI-assisted coding pass. Those codes are not final human annotations. The student review sheet must be completed against the exact dataset snapshot used in the experiment before presenting RQ3 as human-verified findings. No inter-annotator agreement statistic is reported.

## Build instructions

From this directory, compile with a LaTeX distribution and BibTeX installed. Use the usual LaTeX–BibTeX–LaTeX–LaTeX sequence, or the equivalent build command supported by your TeX distribution. Inspect the resulting PDF for references, figure placement, page breaks and layout.

## Reproducibility and data

Raw SciFact data are not included. Follow the download and provenance instructions in the repository's `data/README.md`. The official `release/latest` URL is a moving target; compare the downloaded archive checksum with the historical value recorded in the project documentation before treating it as the same dataset snapshot.
