#!/usr/bin/env python3
"""Join the frozen RQ3 sample to local SciFact claim/corpus text for manual coding."""
from pathlib import Path
import argparse, json
from scifact_verif.rq3_enrichment import enrich_rq3_sample

ROOT = Path(__file__).resolve().parents[1]
p = argparse.ArgumentParser()
p.add_argument('--data-dir', default=str(ROOT/'data/raw/scifact'), help='Directory containing corpus.jsonl and claims_dev.jsonl')
p.add_argument('--sample', default=str(ROOT/'results/rq3/rq3_sample.csv'))
p.add_argument('--meta', default=str(ROOT/'results/rq3/rq3_sample_meta.json'))
p.add_argument('--output', default=str(ROOT/'results/rq3/rq3_sample_enriched_FOR_LOCAL_CODING.csv'))
a = p.parse_args()
data = Path(a.data_dir)
meta = json.loads(Path(a.meta).read_text(encoding='utf-8'))
preds = {k: str(ROOT / v['path']) for k, v in meta['prediction_files'].items()}
result = enrich_rq3_sample(a.sample, data/'claims_dev.jsonl', data/'corpus.jsonl', preds, a.output)
print(json.dumps(result, indent=2))
print('KEEP THE ENRICHED FILE LOCAL. It contains copied claim/abstract text and is not part of the public project archive.')