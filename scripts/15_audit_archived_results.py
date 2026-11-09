#!/usr/bin/env python3
"""Read-only integrity and metric audit of archived SciFact outputs."""
from pathlib import Path
import hashlib, json, sys
import pandas as pd
from sklearn.metrics import accuracy_score, f1_score
ROOT=Path(__file__).resolve().parents[1]
M=ROOT/'results/metrics/eval_20261030T132835Z/metrics.json'
meta=json.loads(M.read_text())
labels=['CONTRADICT','NOT_ENOUGH_INFO','SUPPORT']
frames={}
for cond, item in meta['inputs'].items():
    path=ROOT/item['path']
    digest=hashlib.sha256(path.read_bytes()).hexdigest()
    assert digest==item['sha256'], f'{cond}: hash mismatch'
    df=pd.read_csv(path)
    assert len(df)==286 and df.claim_id.is_unique, f'{cond}: row/ID issue'
    assert set(df.condition)=={cond}, f'{cond}: condition column issue'
    assert set(df.gold_label)==set(labels), f'{cond}: unexpected gold labels'
    assert df[['gold_label','predicted_label']].notna().all().all(), f'{cond}: missing labels'
    frames[cond]=df.set_index('claim_id').sort_index()
assert frames['A'].index.equals(frames['B'].index) and frames['A'].index.equals(frames['C'].index)
for cond, df in frames.items():
    got_acc=accuracy_score(df.gold_label,df.predicted_label)
    got_f1=f1_score(df.gold_label,df.predicted_label,labels=labels,average='macro',zero_division=0)
    saved=meta['results'][cond]['primary_matched']
    assert abs(got_acc-saved['accuracy'])<1e-10, f'{cond}: accuracy mismatch'
    assert abs(got_f1-saved['macro_f1'])<1e-10, f'{cond}: macro-F1 mismatch'
    print(f'PASS {cond}: SHA256, n=286, unique/matched IDs, labels, accuracy={got_acc:.4f}, macro-F1={got_f1:.4f}')
rq3=pd.read_csv(ROOT/'results/rq3/rq3_sample.csv')
assert len(rq3)==50 and rq3[['condition','claim_id']].duplicated().sum()==0
blank_cat=int(rq3.coder_category.isna().sum())
blank_note=int(rq3.coder_note.isna().sum())
print(f'PASS RQ3 sample structure: n=50, coder_category blank={blank_cat}, coder_note blank={blank_note}')
assert blank_cat==50 and blank_note==50, 'Unexpected coder completion; review before updating status.'
retr=json.loads((ROOT/'results/retrieval_eval/retrieval_eval_20261030T131304Z/retrieval_metrics.json').read_text())
print('PASS retrieval metrics JSON readable; see results/retrieval_eval/.../retrieval_metrics.json')
print('LIMIT: this script validates archived files and metric calculations; it does not retrain models or verify source-data licensing.')