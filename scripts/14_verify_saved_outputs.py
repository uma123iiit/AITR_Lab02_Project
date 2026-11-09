#!/usr/bin/env python3
"""Read-only checks over archived prediction and metric outputs; does not rerun training."""
from pathlib import Path
import hashlib, json, pandas as pd
ROOT=Path(__file__).resolve().parents[1]
M=ROOT/'results/metrics/eval_20261030T132835Z/metrics.json'
d=json.loads(M.read_text())
expected_n=286
sets={}
for cond, meta in d['inputs'].items():
    p=ROOT/meta['path']
    actual=hashlib.sha256(p.read_bytes()).hexdigest()
    assert actual==meta['sha256'], f'{cond} prediction hash mismatch'
    df=pd.read_csv(p)
    assert len(df)==expected_n, (cond,len(df))
    assert df['claim_id'].is_unique, cond
    sets[cond]=set(df['claim_id'].astype(int))
assert sets['A']==sets['B']==sets['C'], 'matched IDs differ'
print('PASS: prediction SHA-256, row counts, unique IDs and A/B/C matched IDs')
for c in ['A','B','C']:
    x=d['results'][c]['primary_matched']
    print(f"{c}: n={x['n']} accuracy={x['accuracy']:.4f} macro_f1={x['macro_f1']:.4f}")
print('Note: this read-only check verifies archived outputs, not model correctness or a new experiment run.')