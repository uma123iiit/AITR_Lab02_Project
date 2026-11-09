# RQ3 coding instructions — do not fill by guessing

Input worksheet: `results/rq3/rq3_sample.csv` (50 rows). Codebook: `configs/rq3_codebook.FROZEN.md`; apply `configs/rq3_codebook.AMENDMENT-1.md` as PC-006.

## Step 1 — metadata-only precheck (already generated)

`results/rq3/rq3_metadata_precheck.csv` was generated from the frozen sample metadata. It identifies two first-rule candidates: one B case with empty evidence (`NO_EVIDENCE_SEEN`) and one C case with non-empty gold evidence but no BM25 top-five hit (`RETRIEVAL_MISS`). These are **precheck suggestions only**, not completed coder labels. The other 48 rows require text review. The original `coder_category` and `coder_note` columns remain blank in both files.

## Step 2 — reconstruct the actual text packet locally

The raw SciFact data are not in this ZIP. After obtaining the exact local dataset used in the archived run, execute:

```bash
PYTHONPATH=src python scripts/17_enrich_rq3_sample.py \
  --data-dir data/raw/scifact \
  --output results/rq3/rq3_sample_enriched_FOR_LOCAL_CODING.csv
```

The script joins claim IDs to `claims_dev.jsonl`, joins document IDs to `corpus.jsonl`, checks the sample's gold/shown document IDs against raw claims and condition-specific saved predictions, and creates a local packet containing the claim text, exact condition-specific evidence text, gold rationale sets and full gold abstracts. It deliberately leaves coder fields blank. If ID checks fail, stop and investigate the dataset version; do not bypass the mismatch.

The enriched packet contains copied claim/abstract text and must remain local. Do not add it to the public project ZIP.

## Step 3 — manual annotation

For each row, read the claim, the evidence actually shown to that condition, and the gold rationale/context. Assign exactly one primary code using the frozen codebook's rule order and enter a concise rationale in `coder_note`. If the text is unavailable, do not infer a category from the numeric label alone; use `OTHER_UNCERTAIN` only if you have reviewed the case and genuinely cannot decide. For empty gold-evidence claims, categories `RETRIEVAL_MISS` and `EVIDENCE_IRRELEVANT` do not apply per PC-006.

If a second annotator participates, both annotators must independently code the same cases without seeing the other's labels; then report raw agreement and Cohen's kappa. With one annotator, report descriptive counts only and no inter-annotator reliability statistic.