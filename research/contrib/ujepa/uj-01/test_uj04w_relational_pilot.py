"""Source-free fabricated W0 interface/control fixtures; no trial data or training."""
import unittest
import torch
import uj04w_relational_pilot as w

class RelationalFixtures(unittest.TestCase):
    def test_role_gradient_and_state(self):
        m=w.Cell()
        op=torch.tensor([0,1]);x=torch.tensor([[.2,.5,0.],[.4,.1,1.]])
        d,n,z=m.heads(op,x)
        self.assertEqual(tuple(d.shape),(2,11))
        self.assertEqual(tuple(n.shape),(2,2))
        (d.sum()+n.sum()+z.sum()).backward()
        self.assertIsNotNone(m.roles.grad)
        with self.assertRaises(ValueError):m.heads(op,torch.ones(2,3)*.5)

    def test_target_gradient_and_controls(self):
        rows=((0,0,1,2,3,0),(1,1,3,2,0,1))
        op,x,d,n=w.pack(rows)
        for arm in w.ARMS:
            m=w.Cell(arm=='dense')
            loss,cm,pm=w.loss_for(m,op,x,d,n,arm,torch.tensor([1,0]))
            self.assertEqual((cm,pm),(2,2))
            loss.backward()
            self.assertIsNone(m.target.weight.grad)
            if arm in ('dense','no_latent'):
                self.assertEqual(float(m.predict.weight.grad.abs().sum()),0.)

    def test_gate_no_cross_seed_selection(self):
        def row(seed,arm,good):
            return dict(seed=seed,arm=arm,after=dict(fit=dict(exact=1.),excluded=dict(exact=1. if good else .5,worst=1. if good else .5)),plateau=True)
        rows=[row(seed,arm,arm==('jepa' if seed==1 else 'no_latent')) for seed in (1,2) for arm in w.ARMS]
        self.assertFalse(w.gate(rows,(1,2))[1])
        rows=[row(seed,arm,arm=='no_latent') for seed in (1,2) for arm in w.ARMS]
        self.assertTrue(w.gate(rows,(1,2))[1])
        with self.assertRaises(RuntimeError):w.gate(rows[:-1],(1,2))

    def test_inference_independent_of_targets(self):
        m=w.Cell()
        args=([0,1],[0,1],[1,3],[2,4])
        before=w.predict(m,*args)
        with torch.no_grad():
            m.outcome.weight.fill_(float('nan'));m.target.weight.fill_(float('nan'))
        self.assertEqual(before,w.predict(m,*args))

    def test_fabricated_reference(self):
        self.assertEqual(w.value(0,((0,1),(1,0))),11)
        self.assertEqual(w.value(1,((1,0),(0,0))),1)
        self.assertIsNone(w.value(1,((0,1),)))
