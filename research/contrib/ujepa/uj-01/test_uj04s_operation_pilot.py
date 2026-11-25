"""Source-free arithmetic DEV controls; no real source or learning trial."""
from fractions import Fraction as Q
import time
import unittest
import torch
from uj04s_operation_pilot import bits,features,decode,key,prepare,plan,roll,Latent,Direct,tensor,action,Memory,oriented

def row(name,steps):
    def r(v): return [Q(v).numerator,Q(v).denominator]
    return dict(row_id=name,group=name,steps=[dict(left=r(x),op=o,right=r(y),result=r(z)) for x,o,y,z in steps])

class OperationTests(unittest.TestCase):
    def test_exact_numeric_encoding(self):
        for v in (Q(0),Q(-3,7),Q(2**64-1,2**63),Q(1,2**64-1)):
            self.assertEqual(len(features(v)),132)
            self.assertEqual(decode(tensor(bits(v))*2-1),v)
        self.assertIsNone(decode(torch.zeros(129)))
        self.assertEqual(key(Q(2),'+',Q(3)),key(Q(3),'+',Q(2)))
        self.assertNotEqual(key(Q(2),'-',Q(3)),key(Q(3),'-',Q(2)))
    def test_unseen_atoms_and_chains(self):
        fit=[row('fit',[(2,'+',3,5),(5,'*',2,10)])]
        diag=[row('seen',[(3,'+',2,5),(5,'-',1,4)]),
              row('new',[(4,'+',7,11),(22,'/',11,2)])]
        tr,un,ch,m=prepare(dict(fit=fit,diagnostic=diag))
        self.assertEqual(len(tr),2)
        self.assertEqual(len(un),3)
        self.assertEqual(len(ch),1)
        self.assertEqual(m['excluded_chains_with_seen_atoms'],1)
        self.assertFalse(m['eligible'])
        self.assertEqual(roll(None,ch[0][0],ch[0][1]),ch[0][2])
        self.assertEqual(ch[0][1][-1],('/',Q(22),1))
    def test_no_true_intermediates_and_model_shapes(self):
        start,actions,truth=plan(((Q(1),'+',Q(2),Q(3)),(Q(3),'*',Q(4),Q(12))))
        self.assertEqual(roll(None,start,actions),truth)
        torch.manual_seed(17)
        x=tensor([features(Q(1))]); y=tensor([features(Q(2))]); a=tensor([action('+',0)])
        for model in (Latent(),Direct()):
            pred,state=model(x,y,a)
            self.assertEqual(tuple(pred.shape),(1,129))
            self.assertEqual(len(roll(model,start,actions)),2)
            pred.sum().backward()
            if isinstance(model,Latent):
                self.assertTrue(all(p.grad is None for p in model.target.parameters()))
                self.assertTrue(any(p.grad is not None for p in model.encoder.parameters()))
    def test_memory_control_and_orientation(self):
        rows=[(Q(2),'+',Q(3),Q(5))]
        mem=Memory(rows)
        self.assertEqual(mem.predict(Q(3),'+',Q(2),0),Q(5))
        self.assertEqual(mem.predict(Q(3),'+',Q(2),1),Q(5))
        self.assertEqual(len(oriented(rows)),2)
        self.assertIsNone(mem.predict(Q(1),'-',Q(2),0))
    def test_fail_closed(self):
        with self.assertRaises(ValueError):
            prepare(dict(fit=[row('same',[(1,'+',2,3),(3,'*',2,6)])],diagnostic=[row('same',[(1,'+',3,4),(4,'*',2,8)])]))
        with self.assertRaises(ValueError):
            prepare(dict(fit=[row('bad',[(1,'+',2,4),(4,'*',2,8)])],diagnostic=[]))
        with self.assertRaises(ValueError):
            features(Q(2**64))
