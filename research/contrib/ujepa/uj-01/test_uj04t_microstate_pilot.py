"""Source-free fixture checks, no training or scored T0 execution."""
import time
import unittest
import torch
from uj04t_microstate_pilot import (teacher,digits,reference,value,local_data,cases_for,
                                    Cell,Memory,rollout,tensor,action)

class FixtureTests(unittest.TestCase):
    def test_arithmetic_and_stress(self):
        self.assertEqual(teacher(0,1,9,9),(9,1))
        self.assertEqual(teacher(1,1,0,0),(9,1))
        for case,expected in (((0,2,'fixture',99,1),100),((1,3,'fixture',100,1),99)):
            t,keys=reference(case)
            self.assertEqual(value(case[0],t),expected)
            self.assertEqual(keys[0][1],0)
            self.assertEqual(t[0][1],1)
        with self.assertRaises(ValueError): digits(100,2)
    def test_partition(self):
        a,b=local_data()
        self.assertEqual((len(a),len(b)),(320,80))
        self.assertFalse({r[:4] for r in a}&{r[:4] for r in b})
        self.assertEqual((a,b),local_data())
        for op in (0,1):
            for c in (0,1):
                self.assertEqual(sum(r[:2]==(op,c) for r in b),20)
        cases=cases_for(1,3,8,seed_base=17)
        self.assertEqual(len(set(cases)),12)
        self.assertTrue(all(a>=b for op,w,k,a,b in cases))
    def test_no_truth_carry(self):
        class Probe:
            def __init__(self): self.enc=[];self.states=[]
            def encode(self,c): self.enc.append(c.clone());return c
            def step(self,s,a):
                self.states.append(s.clone())
                return torch.tensor([[1.]+[0.]*9]),torch.tensor([[0.,1.]]),s+7
        cases=((0,2,'fixture',0,0),)
        for kind,expected in (('jepa',7.),('explicit',1.)):
            model=Probe()
            pred=rollout(model,cases,kind,time.monotonic()+5)
            self.assertEqual(pred,(((0,1),(0,1)),))
            self.assertEqual(float(model.states[1][0,0]),expected)
    def test_model_interface(self):
        torch.manual_seed(1)
        m=Cell()
        a=tensor([action(0,2,3)])
        d,c,s=m.step(m.encode(tensor([[0.]])),a)
        self.assertEqual((tuple(d.shape),tuple(c.shape),tuple(s.shape)),((1,10),(1,2),(1,16)))
        (d.sum()+c.sum()).backward()
        self.assertTrue(all(p.grad is None for p in m.target.parameters()))
        self.assertTrue(any(p.grad is not None for p in m.transition.parameters()))
        m.ema()
    def test_memory_no_heldout_labels(self):
        a,b=local_data()
        m=Memory(a)
        self.assertEqual(len(m.fit),320)
        self.assertTrue(all(m.predict(*r[:4])==r[4:] for r in a))
        self.assertTrue(all(r[:4] not in m.fit for r in b))
        with self.assertRaises(RuntimeError):
            rollout(m,((0,2,'fixture',0,0),),'memory',time.monotonic()-1)
