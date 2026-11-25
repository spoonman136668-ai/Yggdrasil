"""Fabricated U0 fixtures only; no trial scoring or training."""
import time
import unittest
import torch
import uj04u_stability_pilot as u
import uj04t_microstate_pilot as t

class StabilityFixtures(unittest.TestCase):
    def test_bounded_interface(self):
        torch.manual_seed(1)
        m=u.Cell()
        a=t.tensor([t.action(0,1,2)])
        z=m.encode(t.tensor([[0.]]))
        for _ in range(128):
            d,c,z=m.step(z,a)
            self.assertEqual(tuple(z.shape),(1,16))
            self.assertTrue(bool((z.abs()<=1).all()))
        (d.sum()+c.sum()).backward()
        self.assertTrue(any(p.grad is not None for p in m.transition.parameters()))
        self.assertTrue(all(p.grad is None for p in m.target.parameters()))
    def test_nonfinite_rejected(self):
        m=u.Cell()
        with self.assertRaises(RuntimeError):
            m.step(torch.full((1,16),float('inf')),torch.zeros(1,11))
        with self.assertRaises(RuntimeError): m.encode(torch.tensor([[float('nan')]]))
    def test_self_feedback(self):
        class Probe(u.Cell):
            def __init__(self): super().__init__(); self.inputs=[]; self.outputs=[]
            def step(self,state,a):
                self.inputs.append(state)
                d,c,n=super().step(state,a); self.outputs.append(n)
                return d,c,n
        paths=(((0,0,1,2,3,0),(0,0,4,5,9,0)),
               ((0,1,9,9,9,1),(0,1,0,1,2,0)))
        m=Probe()
        loss,cm,pm=u.sequence_loss(m,u.pack(paths),'jepa',torch.tensor([1,0]))
        self.assertIs(m.inputs[1],m.outputs[0])
        self.assertEqual((cm,pm),(2,4))
        loss.backward()
        self.assertTrue(all(p.grad is None for p in m.target.parameters()))
    def test_path_restriction(self):
        fit=((0,0,1,2,3,0),(0,1,1,2,4,0),(1,0,3,1,2,0),(1,1,3,1,1,0))
        a=u.make_batches(fit,11,set(),time.monotonic()+5,steps=4,batch_size=3)
        b=u.make_batches(fit,11,set(),time.monotonic()+5,steps=4,batch_size=3)
        self.assertEqual(a,b)
        self.assertEqual([len(x[0]) for x in a],[2,4,8,16])
        self.assertTrue(all(row in fit for batch in a for path in batch for row in path))
        for batch in a: u.pack(batch)
    def test_path_validation(self):
        with self.assertRaises(ValueError):
            u.pack((((0,0,1,2,3,0),(0,1,1,2,4,0)),))
