# Citation and manuscript source audit — 1 November 2026

## Scope and method

This audit checks all 12 keys cited in `research_paper.tex` against authoritative publication or repository records. For proceedings papers, the ACL Anthology record is the bibliographic source; for the JAMIA Open article, PubMed/OUP metadata and abstract are used; for scikit-learn, the JMLR record is used; for the two 2026 works, the arXiv first-version records are used. This is a metadata and cited-claim check, not a full replication of every cited paper's experiments. The manuscript cites 11 scholarly items plus the official dataset licence record. All `\citep{...}` keys in the LaTeX manuscript have one matching BibTeX entry and one matching manual bibliography entry.

## Reference-by-reference results

| BibTeX key | Bibliographic/source check | Context claim check and treatment |
|---|---|---|
| `wadden2020fact` | ACL Anthology record confirms authors, title, EMNLP 2020, pp. 7534–7550, DOI `10.18653/v1/2020.emnlp-main.609`. https://aclanthology.org/2020.emnlp-main.609/ | Supports SciFact as a scientific claim-verification task with evidence-containing abstracts and rationales; original paper reports 1,409 claims and a corpus of 5,183 abstracts. |
| `liu2024cliver` | PubMed record confirms all 11 authors, title, JAMIA Open 7(1):ooae021, 21 Feb 2024, DOI `10.1093/jamiaopen/ooae021`. https://pubmed.ncbi.nlm.nih.gov/38455840/ | Supports CliVER as retrieval-augmented scientific claim verification, label evaluation on SciFact and CoVERt, and Open/Oracle evaluation on clinician claims. Manuscript wording was corrected to keep these evaluation settings distinct. |
| `min2023factscore` | ACL Anthology confirms author list, EMNLP 2023, pp. 12076–12100, DOI `10.18653/v1/2023.emnlp-main.741`. https://aclanthology.org/2023.emnlp-main.741/ | Supports the claim that FActScore decomposes long-form generations into atomic facts and evaluates support against a knowledge source. |
| `gao2023alce` | ACL Anthology confirms authors, EMNLP 2023, pp. 6465–6488, DOI `10.18653/v1/2023.emnlp-main.398`. https://aclanthology.org/2023.emnlp-main.398/ | Supports ALCE as a benchmark for citation-enabled generation and evaluation along fluency, correctness and citation quality. |
| `es2024ragas` | ACL Anthology confirms authors, EACL 2024 System Demonstrations, pp. 150–158, DOI `10.18653/v1/2024.eacl-demo.16`. https://aclanthology.org/2024.eacl-demo.16/ | Supports RAGAs as a reference-free evaluation framework that distinguishes retrieval/context relevance, faithful use of context and generation quality. |
| `zheng2024rav` | ACL Anthology confirms authors, Findings of ACL 2024, pp. 9274–9281, DOI `10.18653/v1/2024.findings-acl.551`. https://aclanthology.org/2024.findings-acl.551/ | Supports the description of RAV as a retrieval-focused fact-verification framework. Its reported experiments use FEVER; it is adjacent work, not a result directly comparable to this SciFact study. |
| `chen2024complex` | ACL Anthology confirms authors, NAACL-HLT 2024, pp. 3569–3587, DOI `10.18653/v1/2024.naacl-long.196`. https://aclanthology.org/2024.naacl-long.196/ | Supports claim decomposition, raw web-evidence retrieval constrained to documents available before the claim, and veracity prediction on complex political claims. |
| `robertson2009bm25` | Bibliographic indexes DBLP and the Webis bibliographic index agree on Robertson & Zaragoza, 2009, *Foundations and Trends in Information Retrieval* 3(4):333–389, DOI `10.1561/1500000019`. https://dblp.org/rec/journals/ftir/RobertsonZ09.html | Supports BM25 as a probabilistic relevance-ranking framework. The manuscript does not attribute any experimental result to this reference. |
| `pedregosa2011sklearn` | JMLR confirms all 16 authors, title, 12(85):2825–2830, 2011. https://www.jmlr.org/papers/v12/pedregosa11a.html | Supports attribution of the scikit-learn software ecosystem used for TF–IDF/logistic-regression implementation. |
| `deka2026retrieval` | arXiv record confirms Pritam Deka and Prabhjot Singh, title, arXiv:2608.01409, first posted 2 Aug 2026. https://arxiv.org/abs/2608.01409 | Its abstract reports a CARE-XAI evaluation across five biomedical/health sources and source-dependent retrieval effects, including SciFact. Treated explicitly as a preprint, not peer-reviewed evidence or a baseline. |
| `huang2026taxonomy` | arXiv record confirms Heyuan Huang et al., title, arXiv:2609.30467, first posted 24 Sep 2026. https://arxiv.org/abs/2609.30467 | Supports the description of an automatically induced taxonomy for retrieval-stage and verifier-reasoning errors in long-form medical factuality evaluation. Treated explicitly as a preprint. |
| `allenai2026scifactlicense` | Official AllenAI repository `LICENSE.md`: https://github.com/allenai/scifact/blob/master/LICENSE.md | States CC BY 4.0 for claim/evidence annotations, ODC-By 1.0 for corpus abstracts (S2ORC), and Apache 2.0 for code. The `master` URL is mutable; this source check does not prove that the archived `release/latest` bytes correspond to a particular immutable commit. |

## Figure, table and cross-reference audit

- The manuscript contains two figures and two tables. Their files are present under `paper/figures/` and the paper references each with a LaTeX `\ref{...}` callout.
- Figure 1 (`macro_f1_by_condition.png`) depicts the six values in the Results table: macro-F1 0.3757/0.4988/0.3650 for the 286-claim three-class matched set and 0.3140/0.3492/0.3119 for the 182-claim two-class evidence slice. The caption says the slices use different class sets; the text explicitly warns not to compare their macro-F1 values directly.
- Figure 2 (`retrieval_recall_at5.png`) depicts 164/182 = 90.11% for BM25 and 151/182 = 82.97% for TF–IDF. These are retrieval Recall@5 values, not classifier accuracy.
- The classification tables are derived from the archived per-claim output CSVs and saved metric JSON. `scripts/14_verify_saved_outputs.py` and `scripts/15_audit_archived_results.py` independently recompute and check the archived metrics. Their audit does not retrain the models.
- LaTeX label/reference scan: every `\ref{...}` used in the paper has a corresponding `\label{...}` declaration. The RQ3 section makes clear that the 50 sampled cases are not yet coded and reports no taxonomy category counts or agreement statistic.

## Issues corrected during this audit

1. The related-work description of Liu et al. (2024) previously conflated the SciFact/CoVERt label-evaluation setting with the Open/Oracle clinician-claim setting. It has been rewritten to distinguish them based on the PubMed record and article figures.
2. The manual bibliography's final `\bibitem` had a literal `\n` token before `\end{thebibliography}`. This was corrected to a true line break.
3. FActScore's DOI and full author list, RAV's full author list, BM25's middle initial, and scikit-learn author accents were normalized in the bibliography.
4. References to licensing now distinguish component-level licence statements from the still-unpinned downloaded archive snapshot.

## Limits of this check

This is a citation metadata and claim-alignment review, not a systematic review of every full cited paper. It does not validate every source's underlying experimental methodology. The 2026 arXiv papers are preprints. The original SciFact source archive's exact immutable commit remains unidentified. The archived results were checked as outputs, but model training and retrieval were not rerun because the raw dataset is not included and the current audit runtime lacks `rank-bm25==0.2.2`.