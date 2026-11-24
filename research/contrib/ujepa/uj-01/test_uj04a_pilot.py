"""UJ04A fabricated fixtures; no real source or protected evaluation."""
import json
import time
import unittest
import torch
from uj04a_pilot import fresh,model_for,MultiPrefix,fit,measure,scores,rank_stats,penalty,ARMS
from uj03a_pilot import digest

class UJ04ATests(unittest.TestCase):
    def setUp(self):
        self.threads=torch.get_num_threads()
        torch.set_num_threads(1)
        self.rows=tuple((str(i),'math',('question '+chr(97+i)).encode(),
            (b'1',b'2',b'3',b'4',b'5'),i%5) for i in range(8))
    def tearDown(self):
        torch.set_num_threads(self.threads)
    def test_fresh_groups(self):
        raw=b'\n'.join(json.dumps(dict(question='problem '+chr(97+i),
            options=['A)1','B)2','C)3','D)4','E)5'],correct='ABCDE'[i%5])).encode() for i in range(20))
        tr,di,m=fresh(raw,digest(raw),4,8,4)
        self.assertEqual([x['count'] for x in m],[4,8,4])
        self.assertEqual(len({r[0] for r in tr+di}),12)
        self.assertEqual((tr,di,m),fresh(raw,digest(raw),4,8,4))
        with self.assertRaises(ValueError):
            fresh(raw,'0'*64,4,8,4)
    def test_causal_prefix_and_parameter_match(self):
        m=model_for('slots_cov',1901)
        z,idx=m.prefixes((b'abcd1111',b'abcd9999'))
        self.assertTrue(torch.equal(z[0,:2],z[1,:2]))
        self.assertFalse(torch.equal(z[0,-1],z[1,-1]))
        for arm in ('pooled','slots','shuffled'):
            q=model_for(arm,1901)
            self.assertTrue(all(torch.equal(v,q.state_dict()[k]) for k,v in m.state_dict().items()))
        a=model_for('prior',1901)
        self.assertEqual(sum(p.numel() for p in a.parameters()),sum(p.numel() for p in m.parameters()))
    def test_rank_and_decorrelation(self):
        x=torch.eye(8).repeat(2,1)
        y=torch.arange(16,dtype=torch.float32)[:,None].repeat(1,8)
        self.assertGreater(rank_stats(x)['rank'],rank_stats(y)['rank'])
        self.assertGreater(float(penalty(y,True)-penalty(y,False)),float(penalty(x,True)-penalty(x,False)))
    def test_all_arms_and_label_independence(self):
        flipped=tuple(r[:4]+((r[4]+1)%5,) for r in self.rows)
        for arm in ARMS:
            with self.subTest(arm=arm):
                m=model_for(arm,1901).eval()
                self.assertTrue(torch.equal(scores(m,self.rows),scores(m,flipped)))
                a=fit(m,self.rows,arm,1901,time.monotonic()+30,epochs=1)
                self.assertEqual(a['steps'],1)
                self.assertEqual(a['exposure_bytes'],sum(len(r[2])+sum(map(len,r[3])) for r in self.rows))
                self.assertEqual(measure(m,self.rows,time.monotonic()+30)['n'],8)
                if isinstance(m,MultiPrefix):
                    self.assertTrue(all(p.grad is None for p in m.target.parameters()))
                if arm=='shuffled':
                    self.assertGreater(a['changed_labels'],0)
        with self.assertRaises(RuntimeError):
            fit(model_for('slots',1901),self.rows,'slots',1901,time.monotonic()-1,epochs=1)
