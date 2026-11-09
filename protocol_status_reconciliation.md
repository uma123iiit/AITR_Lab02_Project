# Protocol Status Reconciliation Note

The archived `configs/primary_frozen.yaml` is retained unchanged as the original timestamped protocol artifact. Its embedded `rq3.codebook: NOT FROZEN` field reflects the state at the time that YAML was written and is now stale relative to later activity.

Subsequent artifacts document that the RQ3 codebook was frozen separately:
- `configs/rq3_codebook.FROZEN.md` (with companion SHA-256 file)
- `configs/rq3_codebook.AMENDMENT-1.md` (PC-006 clarification for empty-gold-evidence cases, also hashed)
- `results/rq3/rq3_sample_meta.json` records the frozen codebook hash, sample seed 42, 50-case allocation (A=17, B=17, C=16) and prediction-file hashes.

This note reconciles the chronology; it does not retroactively rewrite the original frozen configuration. The amendment is a transparent post-freeze codebook clarification. All 50 sample coder fields remain blank, so codebook freeze and sampling are complete, but coding and empirical RQ3 findings are not.