# Final student review checklist

This checklist separates work already documented in the repository from checks that still require the student's own review. Do not mark an item complete until the corresponding action has actually been performed.

## Manuscript and submission
- [ ] Recompile the current `paper/research_paper.tex` and inspect the complete PDF.
- [ ] Confirm the final page count, figures, tables, references, page breaks and formatting.
- [ ] Verify that the final manuscript's numerical claims match the archived result files.
- [ ] Confirm the required student and course details before submission.

## Code and reproducibility
- [x] Archived prediction files have a documented read-only integrity/metrics audit.
- [x] Python source compilation (`compileall`) passed in the recorded audit.
- [ ] Install the pinned dependencies in the specified Python 3.11.2 environment.
- [ ] Run the complete test suite, including `test_inputs.py` and `test_retrieval.py`.
- [ ] Re-run the documented workflow from a clean checkout and record the actual outputs.
- [ ] Confirm whether a newly downloaded SciFact archive matches the historical SHA-256 before treating it as the same snapshot.

## RQ3 student verification
- [x] Frozen 50-row sample and codebook artifacts are documented.
- [x] AI-assisted preliminary codes and source/provenance notes are documented.
- [ ] Review all 50 rows against the exact local `claims_dev.jsonl` and `corpus.jsonl` snapshot used in the experiment.
- [ ] Apply the frozen codebook and PC-006 amendment; record disagreements and reasons.
- [ ] Fill the student verification sheet with the actual final category, reviewer identity and review date.
- [ ] Update the RQ3 report only after the student review is complete.
- [ ] Do not report Cohen's kappa unless a second annotator independently codes the same cases.

## Human accountability and presentation
- [ ] Read the complete manuscript and be prepared to explain every method, result and limitation.
- [ ] Check the AI-assistance log against the work actually performed and correct any inaccurate entries.
- [ ] Add a student sign-off only after personally completing the relevant checks.
- [ ] Rehearse the demonstration using the actual repository files and commands.

## Current status note

The repository contains documented automated checks and an AI-assisted preliminary RQ3 coding pass. It does **not** currently establish that the student has completed a full manual review of every file, independently verified all 50 RQ3 cases, or successfully run the complete test suite in the specified environment. Those activities should be recorded only after they are performed.
