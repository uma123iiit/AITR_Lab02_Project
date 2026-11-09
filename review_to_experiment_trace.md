# Review-to-experiment trace (source crosswalk)

**Prior review:** *A Taxonomy of Hallucination Types in Large Language Models for Research Applications* (15 pages).
**Implementation study:** *Evidence Availability and Retrieval in Scientific Claim Verification: A Matched SciFact Development-Set Study*.
**Status:** source-to-question continuity is now documented. The link is conceptual and bounded; it is not a novelty proof.

## What the prior review actually says

| Original review location | Review-supported point | Connection to the implementation study | Boundary
|---|---|---|
| Section 4.3, pp. 5-6 | Source-faithfulness errors occur when generated content is unsupported by or improperly derived from a source. | Motivates checking claims against identified scientific evidence. | The implementation does not test free-form LLM generation.
| Section 4.8, p. 6 | Retrieval/tool-mediated errors include irrelevant/outdated documents, misreading, ignored contradictions and unsupported claims despite retrieval. | Motivates separating document retrieval from final claim classification. | The study uses a lexical classifier and BM25; it does not evaluate a full RAG generator.
| Section 6.6, p. 8 | RAG evaluation should distinguish retrieval quality, context use/faithfulness and generation quality; retrieval can fail or evidence can be misinterpreted. | Supports measuring Recall@5 separately from classification macro-F1. | The study measures retrieval and classifier outcomes, not generation quality.
| Section 8.6, p. 12 | RAG can create a false sense of security: retrieval may be poor/incomplete/stale or retrieved evidence may be misinterpreted. | Directly motivates comparing gold evidence with automatically retrieved evidence and examining the gap between retrieval success and verdict correctness. | The experiment tests one dataset/model family and cannot generalize to all RAG systems.
| Section 9.1, p. 12 | Future benchmarks should include evidence provenance and multiple dimensions of correctness. | Motivates claim-level matched records and explicit evidence-condition tracking. | This project is not a new benchmark.
| Section 9.2, p. 13 | A provenance-native system should connect a claim to an evidence passage, document identifier and verification state. | Motivates recording per-claim gold/retrieved document IDs and condition-specific predictions. | The archive records document IDs and predictions; it does not build a full provenance graph.
| Section 9.6, p. 13 | Independent components for evidence discovery and factuality/verification may reduce shared failure modes. | Motivates treating retrieval as a separate stage and comparing A/B/C inputs. | No independent verifier-agent architecture is implemented.

## How the research question follows

The review identifies a research-workflow risk: adding retrieved sources does not guarantee faithful use of those sources. The implementation narrows that broad concern to a tractable SciFact claim-verification experiment:

1. **RQ1:** compare claim-only (A), claim + annotated gold evidence (B), and claim + BM25 top-5 evidence (C) on matched development claims.
2. **RQ2:** test whether Recall@5 (retrieval coverage) is associated with downstream label correctness, while keeping retrieval and classification metrics distinct.
3. **RQ3:** classify a prespecified sample of model errors with a project-specific seven-category codebook. The codebook is not the same as the review's nine-category taxonomy; it is a task-specific operational coding scheme.

## What is and is not claimed

**Verified source continuity:** Sections 4.3, 4.8, 6.6, 8.6, 9.1, 9.2 and 9.6 of the prior review provide the conceptual motivation above.

**Researcher interpretation:** applying this motivation to a matched SciFact evidence-condition experiment is a bounded operationalization of the review's concerns.

**Not claimed:** the original review did not itself report this exact A/B/C experiment; this study is not the first oracle/open evidence comparison; the experiment does not evaluate a generative LLM or validate the full nine-category taxonomy. CliVER already studies retrieval-augmented scientific claim verification and uses SciFact. The defensible contribution is the auditable matched-split experiment, retrieval/classification separation, shortcut analysis, near-duplicate sensitivity check and transparent negative/inconclusive findings.

**Source used for page references:** the original 15-page literature-review PDF included in `D_Research_Provenance/Original_Literature_Review.pdf`.