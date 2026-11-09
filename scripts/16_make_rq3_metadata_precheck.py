#!/usr/bin/env python3
"""Create transparent metadata-only RQ3 precheck hints; does not code any case."""
from pathlib import Path
import argparse, json
from scifact_verif.rq3_enrichment import metadata_precheck

ROOT = Path(__file__).resolve().parents[1]
p = argparse.ArgumentParser()
p.add_argument('--sample', default=str(ROOT/'results/rq3/rq3_sample.csv'))
p.add_argument('--output', default=str(ROOT/'results/rq3/rq3_metadata_precheck.csv'))
a = p.parse_args()
print(json.dumps(metadata_precheck(a.sample, a.output), indent=2))