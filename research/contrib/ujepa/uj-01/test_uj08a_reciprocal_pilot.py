"""Fabricated fixtures only; no trial cohort generation."""
import unittest
from unittest.mock import patch
import torch
import uj08a_reciprocal_pilot as f
import uj07a_residual_pilot as e
import uj06a_local_pilot as c
import uj04x_dynamics_pilot as x

class ReciprocalFixtures(unittest.TestCase):
    def test_reciprocity_and_capacity(self):
        torch.manual_seed(7)
        m=f.InteractionCell(True)
        torch.manual_seed(7)
        d=f.InteractionCell(False)
        self.assertEqual(sum(p.numel() for p in m.parameters()),sum(p.numel() for p in d.parameters()))
        self.assertTrue(all(torch.equal(v,d.state_dict()[k]) for k,v in m.state_dict().items()))
        state=torch.tensor([[[.1,.2],[.4,-.2],[.3,.7],[-.1,.5]]])
        action=torch.zeros(1,4,1)
        params=torch.tensor([[.3,.2,.5]])
        idx,mask=f.graph(4,True)
        own,other=x.features(state,action,params,idx,mask)
        msg=m.edge_messages(own,other)
        self.assertTrue(torch.allclose(msg.sum((1,2)),torch.zeros(1,2),atol=1e-6))
        self.assertTrue(torch.equal(msg[other[...,2]==0],torch.zeros_like(msg[other[...,2]==0])))
        self.assertFalse(torch.allclose(d.edge_messages(own,other).sum((1,2)),torch.zeros(1,2),atol=1e-6))
        swapped=other.flip(-2)
        self.assertTrue(torch.allclose(m.heads(own,other)[0],m.heads(own,swapped)[0],atol=1e-6))
        own2=own.clone();own2[...,2]=1
        self.assertTrue(torch.equal(msg,m.edge_messages(own2,other)))

    def test_graph_factor_independence(self):
        for n in (4,8):
            for novel in (False,True):
                idx,mask=f.graph(n,novel)
                edges={(i,int(j)) for i in range(n) for j in idx[i][mask[i].bool()]}
                self.assertTrue(all((j,i) in edges and i!=j for i,j in edges))
                self.assertEqual(len(edges),2*(n-1+2*novel))

    def rows(self):
        return [dict(seed=1,arm=k,adequate=k in f.POSITIVE,steps=2880,endpoint_steps_exposed=737280,
            fit_history=[.04]*5,shuffle_ratios=[1.]*(2 if k in c.CORE else 3),
            after=dict(fit=dict(rollout=.04,effect=.05),familiar=dict(rollout=.05,effect=.06)),
            checkpoint_sha256='a'*64,checkpoint_bytes=100,wall_seconds=1.,cpu_seconds=1.,trainable_params=100) for k in f.ARMS]

    def test_eligibility_fail_closed(self):
        self.assertEqual(len(f.ARMS),16)
        self.assertTrue(f.eligibility(self.rows(),(1,))[1])
        for arm,key,value in ((f.CANDIDATE,'adequate',False),(f.DIRECT,'trainable_params',99),
                              (f.NEGATIVE,'steps',2879),(e.SHUFFLED,'shuffle_ratios',[1.,1.,.49])):
            r=self.rows();next(x for x in r if x['arm']==arm)[key]=value
            self.assertFalse(f.eligibility(r,(1,))[1])
        r=self.rows()
        with self.assertRaises(RuntimeError):f.eligibility(r[:-1]+[r[0]],(1,))

    def test_seed_disjointness(self):
        f.assert_disjoint_seeds()
        for k,v in (('TRANSFER_SEED',351300),('SEEDS',e.SEEDS),('FAMILIAR_SEED',f.FIT_SEED+1)):
            with patch.object(f,k,v):
                with self.assertRaises(RuntimeError):f.assert_disjoint_seeds()

    def test_screen_includes_both_negatives_and_all_controls(self):
        good=dict(rollout=.04,effect=.04,strata={'fixture':dict(rollout=.04,effect=.04)})
        rows={k:dict(rollout=.05,effect=.05) for k in f.ARMS}
        rows['residual_disabled_inference']=dict(rollout=.05,effect=.05)
        rows[f.CANDIDATE]=good
        self.assertTrue(f.screen(rows))
        rows[f.NEGATIVE]=dict(rollout=.04,effect=.04)
        self.assertFalse(f.screen(rows))
        rows[f.NEGATIVE]=dict(rollout=.05,effect=.05)
        rows[f.DIRECT]=dict(rollout=.05,effect=.049)
        self.assertFalse(f.screen(rows))

    def test_prefix_same_trajectory(self):
        t=torch.arange(16).reshape(1,16,1,1)
        data=[('fixture',None,None,None,None,t,t,None,t,t)]
        short=f.prefix(data,8)[0]
        self.assertTrue(torch.equal(short[5],t[:,:8]))
        self.assertTrue(torch.equal(short[8],t[:,:8]))
