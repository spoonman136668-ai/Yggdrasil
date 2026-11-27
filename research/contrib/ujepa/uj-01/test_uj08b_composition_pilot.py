"""Source-free composition and frozen gate fixtures."""
import unittest
from unittest.mock import patch
import torch
import uj08b_composition_pilot as g
import uj08a_reciprocal_pilot as f
import uj07a_residual_pilot as e
import uj06a_local_pilot as c
import uj04x_dynamics_pilot as x

class CompositionFixtures(unittest.TestCase):
    def fixture(self):
        state=torch.tensor([[[.1,.2],[.4,-.2],[.3,.7],[-.1,.5]]])
        idx,mask=f.graph(4,True)
        return x.features(state,torch.zeros(1,4,1),torch.tensor([[.3,.2,.5]]),idx,mask)

    def test_endpoint_equivalence_and_capacity(self):
        torch.manual_seed(7)
        m=g.CompositionCell(True)
        torch.manual_seed(7)
        d=g.CompositionCell(False)
        self.assertEqual(sum(p.numel() for p in m.parameters()),sum(p.numel() for p in d.parameters()))
        self.assertTrue(all(torch.equal(v,d.state_dict()[k]) for k,v in m.state_dict().items()))
        own,other=self.fixture()
        for value in (0.,1.):
            own[...,5]=value
            p,z=m.heads(own,other)
            q,w=d.heads(own,other)
            self.assertTrue(torch.equal(p,q) and torch.equal(z,w))
            m.zero_grad();d.zero_grad()
            p.sum().backward();q.sum().backward()
            for a,b in zip(m.parameters(),d.parameters()):
                if a.grad is not None:self.assertTrue(torch.allclose(a.grad,b.grad,atol=1e-7))

    def test_composition_identity(self):
        m=g.CompositionCell(True)
        own,other=self.fixture()
        own[...,5]=0
        p0,_=m.heads(own,other)
        own[...,5]=1
        p1,_=m.heads(own,other)
        for v in (.25,.5,.75):
            own[...,5]=v
            p,_=m.heads(own,other)
            self.assertTrue(torch.allclose(p,(1-v)*p0+v*p1,atol=1e-7))
        own[...,5]=1.1
        with self.assertRaises(ValueError):m.heads(own,other)

    def test_schedule_factorial(self):
        for k in (g.CANDIDATE,g.DIRECT_FULL,g.NEGATIVE):
            self.assertEqual(g.schedule(k,0)[0],8)
        for k in (g.COMPOSED_TEACHER,g.DIRECT_TEACHER):
            self.assertEqual(g.schedule(k,119)[0],1)

    def rows(self):
        return [dict(seed=1,arm=k,adequate=k in g.POSITIVE,steps=2880,endpoint_steps_exposed=737280,
            fit_history=[.04]*5,shuffle_ratios=[1.]*(2 if k in c.CORE else 3),
            after=dict(fit=dict(rollout=.04,effect=.05),familiar=dict(rollout=.05,effect=.06)),
            checkpoint_sha256='a'*64,checkpoint_bytes=100,wall_seconds=1.,cpu_seconds=1.,trainable_params=100) for k in g.ARMS]

    def test_mastery_fences(self):
        self.assertEqual(len(g.ARMS),21)
        self.assertTrue(g.eligibility(self.rows(),(1,))[1])
        for arm,key,value in ((g.CANDIDATE,'adequate',False),(g.DIRECT_FULL,'trainable_params',99),
                              (g.NEGATIVE,'steps',2879),(e.SHUFFLED,'shuffle_ratios',[1.,1.,.49])):
            r=self.rows();next(x for x in r if x['arm']==arm)[key]=value
            self.assertFalse(g.eligibility(r,(1,))[1])
        with self.assertRaises(RuntimeError):g.eligibility(self.rows()[:-1],(1,))

    def test_seeds_and_screen(self):
        g.assert_disjoint_seeds()
        with patch.object(g,'TRANSFER_SEED',361300):
            with self.assertRaises(RuntimeError):g.assert_disjoint_seeds()
        r={k:dict(rollout=.05,effect=.05) for k in g.ARMS}
        r['residual_disabled_inference']=dict(rollout=.05,effect=.05)
        r[g.CANDIDATE]=dict(rollout=.04,effect=.04,strata={'fixture':dict(rollout=.04,effect=.04)})
        self.assertTrue(g.screen(r))
        r[g.COMPOSED_TEACHER]=dict(rollout=.05,effect=.049)
        self.assertFalse(g.screen(r))
