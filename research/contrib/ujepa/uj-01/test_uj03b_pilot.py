"""UJ03B fabricated-only qualification; no real data acquisition."""
import json
import time
import unittest
import torch
from uj03b_pilot import fresh, model_for, labels_for, loss_for, scores, fit, measure, ARMS
from uj03a_pilot import digest
from learned_jepa import LearnedJEPA

class UJ03BTests(unittest.TestCase):
    def setUp(self):
        self.threads=torch.get_num_threads()
        torch.set_num_threads(1)
        self.rows=tuple((str(i),'math',('question '+chr(97+i)).encode(),
            (b'1',b'2',b'3',b'4',b'5'),i%5) for i in range(8))
    def tearDown(self):
        torch.set_num_threads(self.threads)
    def test_fresh_partition_and_bad_digest(self):
        raw=b'\n'.join(json.dumps(dict(question='problem '+chr(97+i),
            options=['A)1','B)2','C)3','D)4','E)5'],correct='ABCDE'[i%5])).encode() for i in range(20))
        parts,m=fresh(raw,digest(raw),4,4,2,4)
        self.assertEqual([len(p) for p in parts],[4,2,4,2])
        self.assertEqual(len({r[0] for p in parts for r in p}),12)
        self.assertEqual((parts,m),fresh(raw,digest(raw),4,4,2,4))
        with self.assertRaises(ValueError):
            fresh(raw,'0'*64,4,4,2,4)
    def test_matched_objective_and_shuffle(self):
        a=model_for('contrastive',1801)
        b=model_for('positive_only',1801)
        labels=labels_for(self.rows,'contrastive',1801)
        self.assertEqual(sorted(labels),sorted(labels_for(self.rows,'shuffled',1801)))
        self.assertNotEqual(labels,labels_for(self.rows,'shuffled',1801))
        self.assertGreater(float(loss_for(a,self.rows,labels,'contrastive')),
                           float(loss_for(b,self.rows,labels,'positive_only')))
        for arm in ARMS:
            with self.subTest(arm=arm):
                model=model_for(arm,1801)
                acc=fit(model,self.rows,arm,1801,1,time.monotonic()+30)
                self.assertEqual(acc['steps'],1)
                self.assertEqual(acc['exposure_bytes'],sum(len(r[2])+sum(map(len,r[3])) for r in self.rows))
                self.assertEqual(measure(model,self.rows,time.monotonic()+30)['n'],8)
                if isinstance(model,LearnedJEPA):
                    self.assertTrue(all(p.grad is None for p in model.target.parameters()))
    def test_budget_and_score_label_independence(self):
        model=model_for('contrastive',1801).eval()
        flipped=tuple(r[:4]+((r[4]+1)%5,) for r in self.rows)
        self.assertTrue(torch.equal(scores(model,self.rows)[0],scores(model,flipped)[0]))
        with self.assertRaises(RuntimeError):
            fit(model,self.rows,'contrastive',1801,1,time.monotonic()-1)
