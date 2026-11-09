#!/usr/bin/env python3
"""Create a separate partial RQ3 file using only frozen metadata rules."""
from pathlib import Path
import argparse
import pandas as pd
from scifact_verif.rq3_metadata import deterministic_rq3_code

ROOT = Path(__file__).resolve().parents[1]
p = argparse.ArgumentParser()
p.add_argument('--sample', default=str(ROOT/'results/rq3/rq3_sample.csv'))
p.add_argument('--claims', default=str(ROOT/'results/audit/dev_all_labeled_nd-holdout/matched_claims.csv'))
p.add_argument('--output', default=str(ROOT/'results/rq3/rq3_sample_partial_deterministic_codes.csv'))
p.add_argument('--packet', default=str(ROOT/'results/rq3/rq3_claim_text_review_packet.csv'))
a = p.parse_args()

sample = pd.read_csv(a.sample, dtype={'claim_id': 'int64'})
if len(sample) != 50:
    raise SystemExit(f'Expected frozen 50-row sample; found {len(sample)}')

claims = pd.read_csv(a.claims, dtype={'claim_id': 'int64'})
if 'claim' not in claims.columns:
    raise SystemExit('matched_claims.csv has no claim text column')
text_by_id = claims.drop_duplicates('claim_id').set_index('claim_id')['claim']
missing = sorted(set(sample.claim_id) - set(text_by_id.index))
if missing:
    raise SystemExit(f'Claim text missing for IDs: {missing}')

out = sample.copy()
if 'coder_category' not in out:
    out['coder_category'] = ''
else:
    out['coder_category'] = out['coder_category'].fillna('').astype(str)
if 'coder_note' not in out:
    out['coder_note'] = ''
else:
    out['coder_note'] = out['coder_note'].fillna('').astype(str)
statuses, bases = [], []
for idx, row in out.iterrows():
    # Preserve any previous coder entry; this script never overwrites one.
    if pd.notna(row.get('coder_category')) and str(row.get('coder_category')).strip():
        statuses.append('EXISTING_CODER_ENTRY_PRESERVED')
        bases.append('PRE_EXISTING')
        continue
    category, note, status = deterministic_rq3_code(row.to_dict())
    out.at[idx, 'coder_category'] = category
    out.at[idx, 'coder_note'] = note
    statuses.append(status)
    bases.append('FROZEN_METADATA_RULE' if category else 'TEXT_REVIEW_REQUIRED')
out['coding_status'] = statuses
out['coding_basis'] = bases
out.to_csv(a.output, index=False)

packet = out.copy()
packet['claim_text'] = packet.claim_id.map(text_by_id)
packet['abstract_text_status'] = 'NOT_IN_ARCHIVE - retrieve from exact local corpus.jsonl before text coding'
packet['human_review_required'] = packet.coding_status.eq('PENDING_TEXT_REVIEW')
packet['coding_reminder'] = packet.apply(
    lambda r: 'Do not infer category from label/prediction alone; inspect claim, shown abstracts and gold rationale.'
    if r['human_review_required'] else 'Preliminary deterministic metadata assignment only; check codebook note.', axis=1)
packet.to_csv(a.packet, index=False)

print(f'Frozen rows: {len(out)}')
print('Condition allocation:', out.condition.value_counts().sort_index().to_dict())
print('Preliminary deterministic categories:', out.loc[out.coder_category.ne(''), 'coder_category'].value_counts().to_dict())
print('Pending full-text reviews:', int(out.coding_status.eq('PENDING_TEXT_REVIEW').sum()))
print(f'Wrote: {a.output}')
print(f'Wrote: {a.packet}')
print('No abstracts were present or inferred; this is not a completed RQ3 analysis.')