# Phase VI - Human-AI Accountability (Prompt 18)

## Evidence reviewed
The project ZIP contains `ai_assistance_log.md`, `research_decisions.md`, `logs/protocol_changes.md`, test modules, run metadata, saved predictions, metrics, codebook versions and amendment hashes. The AI-assistance log has activity entries AI-01 through AI-15, including concrete corrections and verification events. It explicitly reports missing access to the complete Claude transcript and marks some student understanding checks.

## Authentic examples recorded in the project log

| Example | AI limitation or decision risk | Human/verification response recorded |
|---|---|---|
| AI-03 | A shell pipeline under `pipefail` caused the download script to abort before extraction. | The script was changed to write the listing to a file before previewing it; the actual console output was checked. |
| AI-06 | A summary misreported the breakdown of near-duplicate exclusions. | The counts were re-derived from the superseded audit output and the project log was corrected. |
| AI-09 | An environment setup guide block was skipped even though it created and ran the smoke test. | The missing block was later executed and the omission was recorded. |
| AI-10 | The original error codebook did not define how to code some empty-gold-evidence cases. | A post-draw amendment (PC-006) was added; sampling and blank-hit cases were inspected. |
| AI-14 | An assistant summary overstated that a trivial rule beat B on every clean slice. | The claim was checked against the saved rule-baseline table and narrowed; the 0.7-threshold evidence slice is not a supported difference. |

These examples are taken from the supplied AI log; they are not independently verifiable from a full chat transcript because the transcript itself was not supplied. They are therefore **project-recorded evidence**, not a substitute for the underlying conversation export.

## Human decisions that must be defensible in a viva
The log assigns the student decisions about the matched-set policy, near-duplicate threshold, gold-evidence construction, freeze timing, codebook categories and amendments. The student should be prepared to explain: (1) why the primary cutoff is Jaccard >=0.90 and why 0.70 is sensitivity only; (2) why condition B is oracle-only and confounded for NEI; (3) why BM25 Recall@5 is not classification accuracy; (4) why no Cohen's kappa is reported; and (5) why the study is not a novel first oracle/open comparison.

## Current review activity
This review used the instructor assignment PDF, Prompt 03-07 PDFs and the uploaded ZIP. It independently checked the saved prediction hashes, matched IDs and reported metric values from archived prediction files. It updated the paper to an eight-page manuscript and created a technical review and marking report. It did **not** rerun model training, access Colab/GPU, annotate the 50 RQ3 cases, or independently reproduce the historical Claude session.

## Remaining accountability actions
- Student: verify and explain all modeling/protocol choices before the demonstration.
- Student: attach the complete AI interaction log/export if required by the instructor; do not fabricate missing transcript content.
- Student: review the final LaTeX source, figures, tables, citations and numerical interpretations before submission.
- Student: add only authentic corrections or reflections after personally checking the work.

**Status:** Substantially documented; full transcript, student sign-off and RQ3 annotation remain outstanding.