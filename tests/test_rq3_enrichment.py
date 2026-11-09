import csv
import json
import tempfile
import unittest
from pathlib import Path

from scifact_verif.rq3_enrichment import enrich_rq3_sample, metadata_precheck


class TestRQ3Enrichment(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.claims = self.root/'claims_dev.jsonl'
        self.corpus = self.root/'corpus.jsonl'
        self.sample = self.root/'sample.csv'
        self.pred_a = self.root/'A.csv'
        self.pred_b = self.root/'B.csv'
        self.pred_c = self.root/'C.csv'
        self.claims.write_text('\n'.join([
            json.dumps({'id': 10, 'claim': 'Claim alpha', 'evidence': {'101': [{'label':'SUPPORT','sentences':[0]}]}}),
            json.dumps({'id': 11, 'claim': 'Claim beta', 'evidence': {}}),
        ])+'\n', encoding='utf-8')
        self.corpus.write_text('\n'.join([
            json.dumps({'doc_id': 101, 'title':'Gold title', 'abstract':['Gold sentence one.','Gold sentence two.']}),
            json.dumps({'doc_id': 102, 'title':'Retrieved title', 'abstract':['Retrieved abstract.']}),
        ])+'\n', encoding='utf-8')
        fields = ['condition','claim_id','gold_label','predicted_label','evidence_doc_ids_shown','gold_evidence_doc_ids','evidence_empty','bm25_hit_at_5','truncation_flag','coder_category','coder_note']
        samples = [
            ['A',10,'SUPPORT','CONTRADICT','','101','0','','0','',''],
            ['B',11,'NOT_ENOUGH_INFO','SUPPORT','','','1','','0','',''],
            ['C',10,'SUPPORT','CONTRADICT','102','101','0','0','0','',''],
        ]
        with self.sample.open('w', newline='', encoding='utf-8') as f:
            w=csv.writer(f); w.writerow(fields); w.writerows(samples)
        for path, rows in [(self.pred_a,[('10','')]),(self.pred_b,[('11','')]),(self.pred_c,[('10','102')])]:
            with path.open('w', newline='', encoding='utf-8') as f:
                w=csv.writer(f); w.writerow(['claim_id','evidence_doc_ids']); w.writerows(rows)

    def tearDown(self):
        self.tmp.cleanup()

    def test_enriches_actual_claim_and_condition_evidence(self):
        out = self.root/'enriched.csv'
        res = enrich_rq3_sample(self.sample, self.claims, self.corpus,
                                {'A':self.pred_a,'B':self.pred_b,'C':self.pred_c}, out, expected_rows=3)
        self.assertEqual(res['rows'], 3)
        with out.open(encoding='utf-8', newline='') as f:
            rows = list(csv.DictReader(f))
        self.assertEqual(rows[0]['claim_text'], 'Claim alpha')
        self.assertIn('CLAIM-ONLY', rows[0]['model_evidence_text_exact_condition'])
        self.assertEqual(rows[1]['model_evidence_text_exact_condition'], '[NO GOLD EVIDENCE TEXT: empty B input]')
        self.assertIn('Retrieved abstract.', rows[2]['model_evidence_text_exact_condition'])
        self.assertIn('Gold sentence one.', rows[0]['gold_rationale_context_all_sets'])
        self.assertTrue(all(r['coder_category']=='' and r['coder_note']=='' for r in rows))

    def test_metadata_precheck_is_not_final_annotation(self):
        out = self.root/'precheck.csv'
        result = metadata_precheck(self.sample, out, expected_rows=3)
        self.assertEqual(result['precheck_counts']['NO_EVIDENCE_SEEN'], 1)
        self.assertEqual(result['precheck_counts']['RETRIEVAL_MISS'], 1)
        self.assertEqual(result['precheck_counts']['MANUAL_TEXT_REVIEW_REQUIRED'], 1)
        with out.open(encoding='utf-8', newline='') as f:
            rows = list(csv.DictReader(f))
        self.assertTrue(all(r['coder_category']=='' and r['coder_note']=='' for r in rows))

    def test_mismatched_gold_ids_are_rejected(self):
        broken = self.root/'broken.csv'
        text = self.sample.read_text(encoding='utf-8').replace(',101,0,,0', ',999,0,,0', 1)
        broken.write_text(text, encoding='utf-8')
        with self.assertRaises(ValueError):
            enrich_rq3_sample(broken, self.claims, self.corpus,
                              {'A':self.pred_a,'B':self.pred_b,'C':self.pred_c}, self.root/'bad.csv', expected_rows=3)


if __name__ == '__main__':
    unittest.main()