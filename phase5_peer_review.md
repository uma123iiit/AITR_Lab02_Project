# Phase V - Manuscript, technical review and reproducibility

## Prompt 15 - Manuscript deliverables

The repository includes `paper/research_paper.tex` and `paper/references.bib`. The manuscript was compiled as an **8-page** A4 document and its rendered pages were inspected in the review environment. The compiled PDF and figure exports are not currently present in the GitHub tree. Recompile the current source before submission and confirm the final page count. The manuscript labels the study as a development-set evaluation and does not present RQ3 as completed human annotation.

## Prompt 16 - Internal technical peer review

This is an AI-assisted internal technical review of the included draft, not an external human peer review or a journal decision. Major concerns:

1. **RQ3 is not yet an empirical result.** The error sample is drawn, but all coder fields are blank. Remedy: code the cases against the frozen codebook using actual claim/evidence content; log uncertain cases and the annotator count. Do not report kappa with one annotator.
2. **The oracle/NEI comparison is confounded.** B has empty evidence for NEI, so the model can learn a label shortcut. Remedy: foreground the 182-claim gold-evidence slice and the empty-evidence-rule control; do not interpret all-286 B gain as a causal benefit of evidence.
3. **No independent model-family comparator was run end-to-end.** DeBERTa was smoke-tested only. Remedy: state the two-week/CPU scope and use a second learned verifier only in a separately planned experiment; do not compare to published CliVER scores as if same protocol.
4. **Development-set tuning risk.** Results are only dev results and no untouched public test labels are available. Remedy: use exact terminology and avoid claims of generalization.
5. **Single-seed and lexical-model weakness.** Contradict F1 is extremely low. Remedy: report per-class metrics, class imbalance and limited model capacity; add seeded robustness runs if time permits.
6. **Licensing and source revision unresolved.** The archive contains no raw data, uses a `release/latest` URL, and records conflicting license metadata. Remedy: pin and checksum the exact download, inspect terms for the full source corpus, and do not redistribute raw abstracts until cleared.
7. **Reproduction is not clean-checkout verified.** Models and raw data are excluded. Remedy: reproduce from the README in a clean environment; preserve exact outputs, logs and dependency lock.

Minor issues:
- The initial audit JSON is earlier than RUN-001 and contains stale-in-time warnings; retain and label it as an initial audit, with the chronology explanation in Phase III.
- `primary_frozen.yaml` retains an older `rq3.codebook: NOT FROZEN` field; later hashed codebook and PC-006 amendment are documented in `protocol_status_reconciliation.md`. The original frozen artifact is preserved unchanged.
- No `.ipynb` notebook is present; scripts plus unit tests are the executable project interface. This should be disclosed, not silently represented as a notebook submission.
- The original review PDF and full Claude transcript are not included in the provided ZIP. The former limits Phase I provenance; the latter limits independent audit of the complete AI interaction history.
- Enrollment number and any institution-specific identity fields must be completed before submission.

## Author-response / revision log

| Review concern | Action in this final package | Still required |
|---|---|---|
| Unsupported novelty | Manuscript states controlled comparison and cites CliVER overlap | Student checks closest-paper protocol/supplement |
| B shortcut | Added explicit empty-evidence rule comparison and cautious interpretation | Keep this prominent in viva |
| RQ3 preliminary | Added an AI-assisted preliminary pass and a student verification guide; explicitly distinguished preliminary codes from final annotations | Student must review all 50 rows against the exact dataset snapshot and record decisions |
| Audit chronology | Added Phase III audit chronology clarification | None unless newer audit generated |
| Missing lock file | Added lock snapshot from archived `pip freeze` | Clean install/rerun |
| License uncertainty | Preserved source conflict and excludes raw dataset | Check full terms before public release |
| Missing original review | Marked Phase I mapping provisional | Attach review and verify gap trace |
| Missing demonstration | Added 5-minute walk-through script | Student rehearses and demonstrates code |

## Prompt 17 - Repository readiness

A cleaned README is included. It describes problem, data acquisition, dependencies, commands, output locations, figures, limitations and reproduction steps. The raw data are not included, and the model joblib files are rebuildable. The lock snapshot is provided as an environment record. Commands that were not re-executed in the clean final package are tagged TEST REQUIRED.

## Five-minute demonstration script

1. **0:00-0:40 - Question:** State A/B/C conditions, RQ1-RQ3 and why this is a controlled comparison rather than a novelty claim.
2. **0:40-1:30 - Data/protocol:** Show SciFact splits, 286 matched dev claims, 14 near-duplicate exclusions, 182 gold-evidence claims and the no-test-label rule.
3. **1:30-2:30 - Code:** Open `scripts/07_run_condition.py`, `src/scifact_verif/verifier.py`, `scripts/05_run_retrieval.py` and the frozen config. Explain one input-output path.
4. **2:30-3:40 - Results:** Show `results/results.csv`, paired bootstrap CSV and the saved retrieval metrics. Explain B's empty-evidence shortcut and C's lack of improvement.
5. **3:40-4:30 - Audit:** Show `baseline_validation.md`, protocol changes and the RQ3 preliminary/student verification files; explain that AI-assisted coding is preliminary, student verification remains outstanding, and a clean-checkout rerun is still required.
6. **4:30-5:00 - Limitations/next steps:** Explain license, dev-only evaluation, CPU-only runtime and how to rerun one component.