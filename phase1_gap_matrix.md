# Phase I - From review to research question

**Project:** Evidence-Conditioned Scientific Claim Verification with Taxonomy-Guided Error Analysis (SciFact)

**Evidence status (updated 02 November 2026):** The original 15-page literature review is included in the final provenance folder. A page-level source crosswalk is now available in `review_to_experiment_trace.md`. It links Sections 4.3, 4.8, 6.6, 8.6, 9.1, 9.2 and 9.6 to the implementation question, while distinguishing review-supported statements from the researcher's operational interpretation. This establishes conceptual continuity, not a novelty claim.

## Prompt 01 - Accountable workspace

The ZIP contains a structured Python project, source modules, scripts, configs, tests, metric outputs, run logs, `research_decisions.md`, `baseline_validation.md` and `ai_assistance_log.md`. The repository is portable except that raw SciFact files and rebuildable model objects were intentionally excluded. This submission adds phase-wise documentation, a LaTeX manuscript, verified bibliography, technical review, and demonstration outline.

## Prompt 02 - Candidate gap matrix

| Candidate gap | Evidence basis available now | Status | Testable question / evidence |
|---|---|---|---|
| G1. Evidence availability and retrieval condition | Prompt 03-05 identify claim-only, gold/oracle and retrieved-evidence settings; SciFact and CliVER establish that open/oracle evaluations already exist | VERIFIED as a project question; not novel by itself | On matched SciFact claims, how do three input evidence conditions change macro-F1? Save per-claim predictions and paired uncertainty. |
| G2. Error taxonomy across evidence conditions | Prompt 05-07 define taxonomy-guided error coding; actual sample of 50 errors exists but is not coded | Planned; empirical finding UNKNOWN | Which error categories appear by condition? Apply frozen codebook to a prespecified sample and report counts/denominators. |
| G3. Retrieval metric vs verifier outcome | RQ2 results contain BM25/TF-IDF retrieval ranks, Recall@5 and downstream hit/miss outcomes | VERIFIED as executed design | Does retrieving a gold document necessarily correspond to correct classification? Report retrieval and label metrics separately. |
| G4. Evidence-selection granularity | SciFact annotates rationale sentences; the experiment selects first rationale set per document for B | INFERRED as a methodological sensitivity point | Compare first-rationale vs union-of-rationales only as a new, declared ablation; current primary setting is first rationale. |
| G5. Claim/evidence context length and lexical model capacity | Baseline audit reports long C inputs (~8,000 characters) and a binding 100,000-feature cap | VERIFIED from the archived audit; causal effect UNKNOWN | Test truncation/length or feature-cap sensitivity in a separately frozen future run. |

The strongest executable choice within the recorded two-week/CPU constraint was a **controlled comparative study (Pathway B)** with a bounded error-analysis extension. The central A/B/C comparison overlaps prior published oracle/open work and is not represented as a new algorithm.

## Literature-to-experiment bridge (Prompt 03)

| Work | Verified original task | Relevance here | Role in this project |
|---|---|---|---|
| Min et al. (2023), FACTSCORE | Atomic factual support for long-form generations | Motivates fine-grained support checking; not a SciFact three-way classifier | Conceptual support only; not reproduced |
| Gao et al. (2023), ALCE | Citation-enabled LLM generation, evaluated for fluency, correctness and citation quality | Separates citation quality from whether a supplied evidence item supports a claim | Conceptual support only; not reproduced |
| Es et al. (2024), RAGAs | Multi-dimensional evaluation of RAG pipelines, including retrieval/context faithfulness aspects | Supports separating retrieval quality from verifier outcome | Conceptual support only; not run |
| Wadden et al. (2020), SciFact | Scientific claim verification benchmark with evidence and rationales | Primary task and dataset | Dataset/protocol source |
| Liu et al. (2024), CliVER | Retrieval-augmented scientific claim verification; reports Oracle and Open settings and uses SciFact dev | Closest overlap; disproves first-of-kind claim for broad oracle/open comparison | Novelty boundary / related work |

## Prompt 04 - Feasibility and novelty decision

**Decision: Conditional GO for a small, auditable empirical study. NO-GO for an absolute novelty claim or a promised >90% score.** The published CliVER paper already reports Open and Oracle settings and includes SciFact development-set evaluation. The defensible course-level contribution is a transparent matched-condition comparison with separate retrieval diagnostics, a leakage/near-duplicate audit and a prespecified error taxonomy. Its distinctiveness is provisional, and the taxonomy result is not complete until cases are coded.

Resource profile: CPU-friendly TF-IDF + Logistic Regression and BM25/TF-IDF retrieval; local CPU execution was recorded. Colab/GPU execution is unverified. Full MultiVerS or neural retraining was not attempted. A DeBERTa NLI forward-pass smoke test is recorded, but no full A/B/C DeBERTa experiment is present.

## Prompt 05 - Research questions and success criteria

**Primary RQ1:** On the same eligible SciFact development claims, how do (A) claim-only, (B) claim + gold evidence and (C) claim + BM25-retrieved evidence affect three-way verification performance?

Primary metric: macro-F1. Secondary metrics: accuracy, per-class precision/recall/F1 and confusion matrix. Report paired B-A, C-A and B-C differences with 95% paired-bootstrap intervals. The predeclared practical-effect reference is +0.03 macro-F1; a supported improvement requires the estimate to be at least +0.03 and its CI to exclude zero.

**RQ2:** How frequently does top-5 retrieval include at least one annotated gold evidence document, and how does hit/miss status relate to downstream correctness? Primary retrieval measure: Recall@5; report denominators and label composition.

**RQ3:** Which prespecified error categories appear in each condition? Draw up to 50 incorrect claim-condition cases with a fixed seed; codebook is frozen and amended for NEI/no-gold scope. Agreement statistics are allowed only when two annotators independently code the same items.

**Hypotheses (not findings):** gold evidence may outperform claim-only; retrieved evidence may underperform oracle evidence; error profiles may vary by evidence condition. Each may be contradicted or inconclusive.


## Post-review source trace update (02 November 2026)

The original review has now been read for the selected gap. Its warnings about retrieval/tool-mediated errors and false confidence in RAG (Sections 4.8 and 8.6), plus the recommendations on evidence provenance and independent verification (Sections 9.1, 9.2 and 9.6), support the motivation for comparing claim-only, gold-evidence and retrieved-evidence conditions. The implementation is deliberately narrower than the review: it studies a lexical SciFact verifier, not generative LLM hallucination or all nine review taxonomy categories. See `review_to_experiment_trace.md` for the complete crosswalk.