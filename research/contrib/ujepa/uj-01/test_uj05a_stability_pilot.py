"""Fabricated A0 checks; no trial data generation or training."""
import unittest
import time
import torch
import uj05a_stability_pilot as a
import uj04x_dynamics_pilot as x

class AFixtures(unittest.TestCase):
    def test_factorial_schedule(self):
        for arch in ('dense','relational'):
            for s in a.SCHEDULES:
                arm=f'{arch}_{s}'
                chunks=[a.schedule(arm,e)[0] for e in (0,15,30,45,119)]
                self.assertEqual(chunks,[1,2,4,8,8] if s.endswith('curriculum') else [8]*5)
                self.assertAlmostEqual(a.schedule(arm,0)[1],.003)
                self.assertAlmostEqual(a.schedule(arm,119)[1],.003 if s.startswith('fixed') else .0001)
        for arm in a.ARMS[-3:]:
            self.assertEqual([a.schedule(arm,e) for e in range(a.EPOCHS)],[a.schedule(a.CANDIDATE,e) for e in range(a.EPOCHS)])
        with self.assertRaises(ValueError):a.schedule('unknown',0)

    def test_chunk_reset_and_inference(self):
        s=torch.zeros(2,4,2);p=torch.ones(2,3)*.3;i,m=x.graph(4,'path')
        act=torch.zeros(2,8,4,1);o=torch.tensor([[0,1,2],[2,0,1]])
        teacher=torch.ones(2,8,4,2)*.8
        model=x.Cell(False);d=time.monotonic()+30
        full,_=a.trace(model,s,p,i,m,act,o,d)
        chunk,_=a.trace(model,s,p,i,m,act,o,d,teacher,2)
        self.assertTrue(torch.equal(full[:,:2],chunk[:,:2]))
        self.assertFalse(torch.allclose(full[:,2:],chunk[:,2:]))
        independent,_=a.trace(model,s,p,i,m,act,o,d,None,8)
        self.assertTrue(torch.equal(full,independent))
        full[:,-1].sum().backward()
        self.assertIsNotNone(model.result.weight.grad)

    def test_gate_and_split(self):
        a.assert_disjoint_seeds()
        from unittest.mock import patch
        with patch.object(a,'FAMILIAR_SEED',a.FIT_SEED+1):
            with self.assertRaises(RuntimeError):a.assert_disjoint_seeds()
        rows=[dict(seed=1,arm=k,adequate=k in a.ARMS[:10],after=dict(familiar=dict(rollout=.01))) for k in a.ARMS]
        self.assertEqual(a.eligibility(rows,(1,))[1],dict(primary=True,jepa=False))
        rows[0]['adequate']=False
        self.assertFalse(any(a.eligibility(rows,(1,))[1].values()))
        with self.assertRaises(RuntimeError):a.eligibility(rows[:-1],(1,))

    def test_all_arms_loss(self):
        s=torch.zeros(2,4,2);s[1,:,0]=.7
        p=torch.tensor([[.3,.2,0.],[.4,.3,1.]])
        i,m=x.graph(4,'path');u=torch.zeros(2,8,4,1);v=u.clone()
        u[0,:,0,0]=.5;v[0,:,0,0]=-.5
        u[1,:,2,0]=-.4;v[1,:,2,0]=.4
        o=torch.tensor([[0,1,2],[2,0,1]])
        ta=torch.ones(2,8,4,2)*.2;tb=-ta;ta[1]*=-1;tb[1]*=-1
        row=('fixture',s,p,i,m,u,v,o,ta,tb)
        for arm in a.ARMS:
            model=x.Cell(arm.startswith('dense'))
            loss,metrics=a.loss_for(model,arm,row,torch.tensor([1,0]),time.monotonic()+30,a.schedule(arm,0)[0])
            self.assertGreater(metrics[2],0)
            loss.backward()
            self.assertTrue(all(q.grad is None for q in model.target.parameters()))
