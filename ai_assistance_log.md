# ai_assistance_log.md: AI-assistance and verification log (Prompts 08 to 11, 18)

Tool: Claude Code (model Sonnet 5.5) used as research software engineer / pair programmer, one long session, 2026-10-30.
Full session transcript (authentic prompt log, not copied into this package): ~/.claude/projects/-home-user-go-code/733782f8-c6c4-4ff9-94bc-11e6720bc98c.jsonl
Course prompts used (prompts.pdf numbering): 08 environment, 09 pair-programmed baseline, 10 baseline audit, 11 debugging. Prompt 11 was first pasted
with unfilled placeholders; the assistant did not guess and asked for the content. Later prompts (12 to 18) are not done.
Disclosure: AI supported code generation, debugging, analysis, visualization and the drafting of these documents. The student has not yet
independently re-derived all conclusions; items marked CHECK below need the student's own verification before submission.

## Activity log
| ID | Task | AI proposal | Human decision | Verification | Change / outcome |
|---|---|---|---|---|---|
| AI-01 | Environment setup (P08) | Colab setup guide (HTML) plus smoke-test script | Run locally instead; Colab runtime could not be created by the assistant | Guide code blocks run locally; smoke output in results/env_smoke/ | Passed locally. Colab path untested [TEST REQUIRED] |
| AI-02 | Read the course PDFs | Read tool on PDF | none | Read failed (pdftoppm missing); fell back to pypdf text extraction in a venv | Workaround; the Prompt03/04 and review paper were never read by the assistant |
| AI-03 | Data download script | scripts/01 with `tar -tzf | head -20` under `set -o pipefail` | none | The script aborted before extraction and the data audit SKIPped; cause found and confirmed | Fixed by writing the listing to a file then `head`; guide HTML fixed too. REAL AI limitation |
| AI-04 | Matched-set policy | Explained all_labeled vs evidence_only | Chose all_labeled and "hold them out" for near-duplicates | Counts checked against exclusions file | PC-001 |
| AI-05 | Baseline modules in cycles (P09) | data, verifier, metrics, retrieval, evaluation code with unit tests | Ran cycles, moved on after real output | unit tests (54 then 59), console logs in logs/ | Working baseline |
| AI-06 | PC-001 breakdown of held-out claims | Logged 4 gold / 10 NEI | none | Re-derived from the superseded audit output: 6 gold / 8 NEI | Log corrected. REAL AI error |
| AI-07 | Baseline audit (P10) | Independent recomputation (sklearn, refit, BM25 reimplementation, shuffled labels) | Accepted corrections N1, N2, N3 | audit JSON: 12 PASS, 4 WARN, 0 FAIL | PC-004; audit also showed majority class on the matched set is SUPPORT (0.427), which the assistant would otherwise have stated wrongly from memory |
| AI-08 | Test failure after adding n_rationale_sets to gold-evidence items | Added the field | none | One old test failed because its expected dict lacked the field; the change was intended | Test expectation updated, not the code |
| AI-09 | Skipped guide block6 first (it creates and runs the smoke test script) | none | none | The omission surfaced later | block6 run. REAL slip |
| AI-10 | Debugging (P11 applied to the RQ3 sampler) | Independent checks of the sample | Approved amendment | Population recount via argmax matched 154 / 114 / 161; sample rows all real errors, unique; redraw byte-identical; 4 of 16 C rows had blank hit status, all NEI | Gap in the frozen codebook (categories 2 and 3 undefined for claims with no gold evidence): PC-006. REAL AI omission, found by a check |
| AI-11 | RQ2 hit/miss script | scripts/11 | none | Ran with the wrong interpreter first (`python` not found, then system python lacked numpy); then the project venv | No result affected |
| AI-12 | Hash check of frozen codebook | `sha256sum -c` from the repo root | none | FAILED because the hash file's path is relative to configs/; passes from configs/ | No result affected |
| AI-13 | RQ3 codebook | AI drafted 8 categories from Prompt06 examples | Merged "misread" and "decision error"; A errors not coded NO_EVIDENCE_SEEN; approved freeze | hash recorded; sample drawn only after freeze | PC-005 |
| AI-14 | Summary of results | Chat statement that no condition beats a trivial rule where the comparison is clean | none | While writing research_decisions.md the numbers were checked against results_rule_baseline_B.csv: B (0.427) is slightly above the rule (0.409) on the 127-claim sensitivity slice, +0.018, CI includes 0 | Statement tightened in research_decisions.md. REAL AI overstatement |

## Real examples of AI limitations or purposeful verification (>= 3 required: 7 recorded)
AI-03, AI-06, AI-09, AI-10, AI-14 (limitations/corrections); AI-07 and AI-10 (purposeful independent verification).

## Where conclusions depended on human reasoning
Policy choices (matched set, near-duplicate threshold, B definition, codebook categories, freeze timing) were decided by the student, but in
several cases (PC-003, PC-004, sample allocation) by accepting the assistant's recommendation. CHECK: the student must be able to explain each of these
choices and why the alternatives were rejected (see research_decisions.md) before the viva.

## Risks that remain
- The review-to-gap trace is UNKNOWN to the assistant (original review and Prompt03/04 unread). CHECK.
- scripts/10 to 13 and the audit script have no unit tests. Results are single-run, development set, local CPU only.
- RQ3 coding not yet done; single annotator would be descriptive.

## Student prompt log (verbatim short prompts, in order; long templates are course prompts 08, 09, 10, 11)
- "Getting Error invoking remote method 'read-file-content': Error: File not found: /home/user/go-code/logs/env_smoke_console.txt for the smoke test file"
- "Can you export this somewhere so that I can send it as a message"
- "Can you create a collab gpu and run it there"
- "okay remind me to clean this up once done"
- "okay do the setup"
- "We will use the results from run on this machine. Can you explain all_labeled vs evidence - which is a better choice and why"
- "okay let's d that / let's hold them out"
- "okay let's move to Cycle 2"; "you can start now given cycle 2 is complete"; "LEt's move to Cycle 4"; "okay"
- "What is PC-002. What do I need to decide on the sensitivity analysis"; "okay accepting the recommendation"; "start now"
- "accepted the corrections"; "yes do it"
- "RQ2 hit/miss table is cheap and uses saved outputs"
- "RQ3 needs you to approve a codebook first- where is the codebook to approve"; "merge them / what is better for this case"; "you can apply the A change"; "freeze it"; "okay"
- (Prompt 11 pasted unfilled); "Code is the one you generated in the last prompt likewise the expected beahviour is the expectations and so on"; "sure"
- "If I have to share the progress and everything that was asked to save ... what should I share"; "yes bundle in a share-ready zip. Give appropriate names for every file"


## AI-15 | Final package audit and manuscript preparation (ChatGPT, 2026-11-01)
- **Task:** inspect supplied instructor brief, Prompt03-07 PDFs and ZIP; map prompt requirements to source artifacts; review real CSV/JSON/log outputs; create Phases I-V documentation, figures, LaTeX manuscript, technical review, demonstration script and package.
- **AI proposal/output:** interpreted archived metrics and protocol; drafted narrative and source-linked references; created phase documents and compiled manuscript/summary PDFs.
- **Human verification still required:** confirm Phase I against the original literature-review PDF (not supplied), code all 50 RQ3 cases using actual claim/evidence text, verify final student-specific information, re-run tests in Python 3.11.2 and check dataset licensing.
- **Execution boundary:** no SciFact model training, A/B/C experiment rerun, GPU/Colab run or RQ3 case coding was performed in this review because raw data are absent from the ZIP and the current container lacked rank-bm25 with network unavailable. Existing numerical claims are transcribed from hashed/ timestamped archived outputs.
- **Web verification performed:** primary source records were checked for SciFact (Wadden et al., ACL Anthology; official AllenAI repo/data/license), CliVER (Liu et al., JAMIA Open), FACTSCORE, ALCE, RAGAs, RAV and the 2024 NAACL complex-claim paper. 2026 preprints in Prompt04 were identified as preprints, not peer-reviewed benchmarks.


## AI-16 | Final Phase I-VI closure review (ChatGPT, 2026-11-01)
- **Task:** re-audit the project archive and instructor's complete 11-page assignment brief; reconcile prior run outputs, inspect Phase I-VI deliverables, verify primary scholarly citations, expand the manuscript to the 6-10-page target, and produce a phase-wise review/mark estimate.
- **Verification performed:** checked SHA-256 values and 286-row matched IDs for A/B/C; recomputed accuracy and macro-F1 from saved predictions; verified the 50-row RQ3 worksheet remains uncoded; ran archived-output verifier successfully; attempted unit-test discovery in a Python 3.13.5 review environment.
- **Observed limitation:** 43 tests passed and two test modules could not import because `rank_bm25` is absent in the review container; no network/DNS was available to install it. No raw data are in the archive, so the full experiment was not rerun.
- **Output:** 8-page manuscript, Phase VI accountability review, protocol-status reconciliation, marking report, final archived-output audit script and updated submission bundle.
- **Human actions still required:** attach the original literature review, complete the 50-case RQ3 coding from local source text, re-run tests under Python 3.11.2 with pinned dependencies, resolve dataset licensing, fill enrollment number, and personally validate the final material.





## AI-11 — Final assignment alignment and emergency audit (02 November 2026)

- **Task:** Map the existing project files to the instructor's explicit A-E submission requirements; re-check archived experimental outputs; update the review-to-experiment trace; create a metadata-only RQ3 pre-coding aid; and run available tests.
- **Tooling:** ChatGPT file/container tools, Python 3.13.5, pytest, compileall, PDF text extraction/rendering, and primary-source checks of the official SciFact repository.
- **AI proposal/action:** organize deliverables as A) paper, B) repository, C) experimental evidence, D) research provenance, E) demonstration. Add no raw SciFact data to the distributable archive.
- **Human decision:** no new student approval or sign-off is evidenced in this log. The researcher must inspect the six metadata-only RQ3 assignments and approve or correct the source crosswalk before submission.
- **Verification:** archived metrics and prediction hashes re-checked; 46 tests pass with only two missing-dependency modules excluded; 3 RQ3 enrichment tests and 5 metadata-code tests pass; compileall passes. Full suite remains blocked by missing `rank-bm25==0.2.2` and unavailable package-index DNS.
- **Outcome/limitations:** six deterministic RQ3 pre-codes are saved separately; 44 cases remain for text-based human coding. No new training, retrieval or text-based annotation is claimed.


## 02 November 2026 — RQ3 preliminary text review update

- **Task:** inspect the frozen 50 condition–claim sample using claim records and relevant gold/retrieved abstract text, then create a separate preliminary coding file and provenance report.
- **Sources:** public SciFact claims mirror and a pinned BEIR/SciFact document mirror; exact URLs and identity limitation are recorded in `RQ3_SOURCE_PROVENANCE.md`.
- **Result:** 50 rows received AI-assisted provisional codes; two assignments are deterministic metadata rules (B/303 and C/756), and 48 are text-review judgments. Preliminary category counts are 31 `LABEL_DECISION_ERROR`, 14 `AMBIGUOUS_ANNOTATION`, 3 `OTHER_UNCERTAIN`, 1 `NO_EVIDENCE_SEEN`, and 1 `RETRIEVAL_MISS`.
- **Human decision/status:** no student sign-off is evidenced. The public document mirror is not checksum-matched to the exact historic local corpus. All 50 rows remain pending student verification; ambiguous cases were not forced into confident codes.
- **Verification and limitations:** original frozen sample and codebook were preserved; no independent second coder or Cohen's kappa is available; no final taxonomy findings are claimed. This review did not retrain models or rerun retrieval.

## Current status clarification — 10 November 2026

The earlier review-container test attempt and missing rank-bm25 dependency are historical notes about that isolated environment. The student has confirmed that the complete test suite passes in the working project environment; the earlier partial run must not be described as the current project test status. The student also confirmed the final manuscript is nine pages and follows the instructor-provided template. Historical AI activity and verification records above are preserved rather than rewritten. The RQ3 codes remain identified as preliminary unless and until the student verification sheet documents the manual review.


## Student verification confirmation — 10 November 2026

The student confirms that all project materials have been manually checked and that the code, implementation and complete test suite are working correctly in the student's environment. The student also confirms that all 50 frozen RQ3 sample rows and associated coding decisions have been manually reviewed and verified. The earlier RQ3 sections above describe the AI-assisted preliminary stage at the time those records were written; they are retained as historical provenance and are superseded by this dated confirmation and the updated student-verified RQ3 analysis. The earlier missing-rank-bm25 test report describes only the separate review container, not the student's working environment. No independent second human coder is reported, so no Cohen's kappa is claimed.
