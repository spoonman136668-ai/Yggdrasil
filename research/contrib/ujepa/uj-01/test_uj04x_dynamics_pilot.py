"""Fabricated X0 source-free interface tests, no trial generation or fitting."""
import unittest
import time
import torch
import uj04x_dynamics_pilot as x

class DynamicsFixtures(unittest.TestCase):
    def test_graph_and_shape(self):
        for n,kind in ((4,'path'),(4,'ring'),(4,'star'),(6,'tree'),(8,'chord')):
            idx,mask=x.graph(n,kind)
            self.assertEqual(tuple(idx.shape),(n,3))
            self.assertTrue(bool((mask.sum(-1)>0).all()))
            self.assertEqual(int(mask.sum()),int(mask.sum())//2*2)

    def test_neighbor_permutation(self):
        m=x.Cell()
        own=torch.zeros(2,6)
        other=torch.tensor([[[.3,.2,1.],[.5,.1,1.],[0.,0.,0.]]]*2)
        p=m.heads(own,other)[0]
        q=m.heads(own,other[:,[2,0,1],:])[0]
        self.assertTrue(torch.allclose(p,q,atol=1e-6))
        p.sum().backward()
        self.assertIsNotNone(m.edge[0].weight.grad)

    def test_target_isolation(self):
        own=torch.zeros(2,6);other=torch.zeros(2,3,3)
        y=torch.tensor([[1.,0.],[-1.,0.]])
        for arm in x.ARMS:
            m=x.Cell(arm=='dense')
            loss,_,_=x.loss_for(m,own,other,y,arm,torch.tensor([1,0]))
            loss.backward()
            self.assertTrue(all(p.grad is None for p in m.target.parameters()))
            if arm in ('no_latent','dense'):self.assertEqual(float(m.predict.weight.grad.abs().sum()),0.)
            before=m.heads(own,other)[0].detach()
            with torch.no_grad():
                for p in m.target.parameters():p.fill_(float('nan'))
            self.assertTrue(torch.equal(before,m.heads(own,other)[0].detach()))

    def test_gates_independent(self):
        rows=[dict(seed=1,arm=a,adequate=a in ('no_latent','dense'),after=dict(familiar=.01)) for a in x.ARMS]
        self.assertEqual(x.gate(rows,(1,))[1:],(True,False))
        rows[-1]['adequate']=False
        self.assertEqual(x.gate(rows,(1,))[1:],(False,False))
        self.assertTrue(x.adequate([.009]*5))
        self.assertFalse(x.adequate([.15]*5))

    def test_rollout_uses_predicted_state(self):
        class Probe:
            def __init__(self):self.inputs=[]
            def heads(self,own,other):
                self.inputs.append(own.detach().clone())
                return torch.ones_like(own[...,:2]),None
        model=Probe();idx,mask=x.graph(4,'path')
        initial=torch.zeros(1,4,2);params=torch.zeros(1,3)
        tr=x.rollout(model,initial,params,idx,mask,torch.zeros(2,1,4,1),time.monotonic()+10)
        self.assertTrue(torch.allclose(model.inputs[1][...,:2],tr[0]))
        self.assertTrue(torch.allclose(tr[1],torch.full_like(initial,2*x.DT)))
