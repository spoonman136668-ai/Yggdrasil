"""Fabricated fixtures only, no frozen trial cohort access."""
import unittest
from unittest.mock import patch
import torch
import uj08c_learned_pilot as h
import uj08b_composition_pilot as g
import uj08a_reciprocal_pilot as f
import uj07a_residual_pilot as e
import uj06a_local_pilot as c
import uj04x_dynamics_pilot as x

class LearnedCompositionFixtures(unittest.TestCase):
    def fixture(self):
        state=torch.tensor([[[.1,.2],[.4,-.2],[.3,.7],[-.1,.5]]])
        idx,mask=f.graph(4,True)
        return x.features(state,torch.zeros(1,4,1),torch.tensor([[.3,.2,.5]]),idx,mask)

    def test_equal_capacity_and_learned_gradients(self):
        torch.manual_seed(7);m=h.LearnedCell(True)
        torch.manual_seed(7);d=h.LearnedCell(False)
        self.assertEqual(sum(p.numel() for p in m.parameters()),sum(p.numel() for p in d.parameters()))
        self.assertTrue(all(torch.equal(v,d.state_dict()[k]) for k,v in m.state_dict().items()))
        own,other=self.fixture()
        for model in (m,d):
            pred,_=model.heads(own,other)
            pred.square().sum().backward()
            self.assertGreater(sum(float(p.grad.abs().sum()) for p in model.gate.parameters()),0.)
        p,_=m.heads(own,other)
        self.assertTrue(torch.allclose(p,m.heads(own,other.flip(-2))[0],atol=1e-6))
        m.fixed_gate=True
        q,_=m.heads(own,other)
        self.assertFalse(torch.equal(p,q))
        m.fixed_gate=False
        self.assertTrue(torch.equal(p,m.heads(own,other)[0]))

    def test_truth_context_is_not_input(self):
        # Hand-written single scenario, not generated from any trial seed.
        s=torch.tensor([[[.1,.2],[.4,-.2],[.3,.7],[-.1,.5]]])
        p=torch.tensor([[.3,.2,.5]])
        i,m=f.graph(4,False)
        u=torch.zeros(1,8,4,1);v=u.clone();v[:,0,0,0]=.4
        raw=[('fixture',s,p,i,m,u,v,torch.tensor([[0,1,2]]))]
        import time
        linear=h.prepare(raw,'linear',time.monotonic()+10)[0]
        quadratic=h.prepare(raw,'quadratic',time.monotonic()+10)[0]
        self.assertTrue(all(torch.equal(a,b) for a,b in zip(linear[1:8],quadratic[1:8])))
        self.assertFalse(torch.equal(linear[8],quadratic[8]))
        self.assertEqual(float(p[0,2]),.5)

    def test_split_values_and_seed_fences(self):
        h.assert_disjoint_seeds()
        for k,v in (('FIT_SEED',371100),('TRANSFER_SEED',h.FIT_SEED),('SEEDS',g.SEEDS)):
            with patch.object(h,k,v):
                with self.assertRaises(RuntimeError):h.assert_disjoint_seeds()
        # Exercise only fabricated cases, not the generator's frozen cohorts.
        def fake(seed,count,transfer):
            return [('4:0:0:1' if transfer else 'fixture',None,torch.zeros(count,3),None,None,None,None,None)]
        with patch.object(f,'cases',fake):
            fit=h.raw_cases(0,64)[0][2][:,2]
            transfer=h.raw_cases(0,24,True)[0][2][:,2]
            self.assertFalse(set(fit.tolist()) & set(transfer.tolist()))
            self.assertEqual(set(transfer.tolist()),{.25,.5,.75})
            self.assertEqual(len(set(fit.tolist())),5)

    def rows(self):
        return [dict(seed=1,arm=k,adequate=k in h.POSITIVE,steps=2880,endpoint_steps_exposed=737280,
            fit_history=[.04]*5,shuffle_ratios=[1.]*(2 if k in c.CORE else 3),
            after=dict(fit=dict(rollout=.04,effect=.05),familiar=dict(rollout=.05,effect=.06)),
            checkpoint_sha256='a'*64,checkpoint_bytes=100,wall_seconds=1.,cpu_seconds=1.,trainable_params=100) for k in h.ARMS]

    def test_mastery_and_capacity(self):
        self.assertEqual(len(h.ARMS),24)
        self.assertTrue(h.eligibility(self.rows(),(1,))[1])
        for arm,key,value in ((h.CANDIDATE,'adequate',False),(h.DIRECT,'trainable_params',99),
                              (h.NEGATIVE,'steps',2879),(g.CANDIDATE,'adequate',False)):
            r=self.rows();next(x for x in r if x['arm']==arm)[key]=value
            self.assertFalse(h.eligibility(r,(1,))[1])

    def test_screen_all_controls(self):
        r={k:dict(rollout=.05,effect=.05) for k in h.ARMS}
        for k in ('residual_disabled_inference','fixed_gate_inference'):r[k]=dict(rollout=.05,effect=.05)
        r[h.CANDIDATE]=dict(rollout=.04,effect=.04,strata={'fixture':dict(rollout=.04,effect=.04)})
        self.assertTrue(h.screen(r))
        for k in (h.DIRECT,h.NEGATIVE,'fixed_gate_inference'):
            old=r[k];r[k]=dict(rollout=.05,effect=.049)
            self.assertFalse(h.screen(r));r[k]=old
