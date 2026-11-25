"""Source-free fabricated V0 interface and gate fixtures; no training or trial scoring."""
import unittest
import torch
import uj04v_factorized_pilot as v
import uj04t_microstate_pilot as t

class FactorizedFixtures(unittest.TestCase):
    def test_explicit_state(self):
        m=v.Cell()
        c=t.tensor([[0.],[1.]])
        a=t.tensor([t.action(0,1,2),t.action(1,5,3)])
        d,n,p=m.step(c,a)
        self.assertEqual(tuple(d.shape),(2,10))
        self.assertEqual(tuple(n.shape),(2,2))
        self.assertTrue(torch.equal(p,n.argmax(-1,keepdim=True).float()))
        with self.assertRaises(ValueError): m.encode(t.tensor([[.5]]))
        with self.assertRaises(RuntimeError): m.encode(t.tensor([[float('nan')]]))

    def test_aux_grad_and_negative(self):
        rows=((0,0,1,2,3,0),(0,1,9,9,9,1))
        c,a,d,n=t.batch(rows)
        for arm in v.ARMS:
            m=v.Cell()
            loss,cm,pm=v.loss_for(m,c,a,d,n,arm,torch.tensor([1,0]))
            self.assertEqual((cm,pm),(2,2))
            loss.backward()
            self.assertIsNone(m.target.weight.grad)
            self.assertIsNotNone(m.outcome.weight.grad)
            self.assertIsNotNone(m.predict.weight.grad)
            if arm=='no_latent': self.assertEqual(float(m.predict.weight.grad.abs().sum()),0.)
        with self.assertRaises(ValueError):
            v.loss_for(v.Cell(),c,a,d,n,'jepa',torch.tensor([0,0]))

    def test_target_ema(self):
        m=v.Cell()
        old=m.target.weight.detach().clone()
        with torch.no_grad(): m.outcome.weight.add_(1)
        m.ema()
        self.assertTrue(torch.allclose(m.target.weight,old+.01,atol=1e-6))

    def test_mastery_fail_closed(self):
        def row(arm,fit,known,plateau=True):
            return dict(seed=1,arm=arm,after=dict(fit=dict(exact=fit),known=dict(exact=known)),plateau=plateau)
        rows=[row(a,1.,1.) for a in v.ARMS]
        self.assertTrue(v.mastery(rows,(1,))[1])
        rows[1]=row('no_latent',.97,1.)
        self.assertFalse(v.mastery(rows,(1,))[1])
        rows[1]=row('no_latent',1.,1.,False)
        self.assertFalse(v.mastery(rows,(1,))[1])
        with self.assertRaises(RuntimeError): v.mastery(rows[:-1],(1,))
