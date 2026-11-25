"""C0 fabricated data only."""
import time
import unittest
from unittest.mock import patch
import torch
import uj06a_local_pilot as c
import uj05a_stability_pilot as a
import uj04x_dynamics_pilot as x

class CFixtures(unittest.TestCase):
    def test_control_schedule_and_fresh_seeds(self):
        self.assertEqual(len(c.ARMS),10)
        self.assertEqual(len(c.CONTROLS),8)
        for arm in c.LOCAL:
            self.assertEqual([c.schedule(arm,e) for e in range(c.EPOCHS)],[a.schedule('relational_teacher',e) for e in range(c.EPOCHS)])
        c.assert_disjoint_seeds()
        with patch.object(c,'TRANSFER_SEED',321300):
            with self.assertRaises(RuntimeError):c.assert_disjoint_seeds()

    def test_all_local_losses(self):
        s=torch.zeros(2,4,2);s[1,:,0]=.3
        p=torch.tensor([[.3,.2,0.],[.4,.3,1.]])
        i,m=x.graph(4,'path');u=torch.zeros(2,8,4,1);v=u.clone()
        u[0,:,0,0]=.5;v[0,:,0,0]=-.5;u[1,:,2,0]=-.4;v[1,:,2,0]=.4
        o=torch.tensor([[0,1,2],[2,0,1]])
        ta=torch.arange(1,9,dtype=torch.float32)[None,:,None,None].expand(2,8,4,2).clone()*.02
        tb=-ta;ta[1]*=-1;tb[1]*=-1
        row=('fixture',s,p,i,m,u,v,o,ta,tb)
        torch.manual_seed(1);model=x.Cell(False)
        losses=[]
        for arm in c.LOCAL+(c.NEGATIVE,):
            loss,metrics=c.loss_for(model,arm,row,torch.tensor([1,0]),time.monotonic()+30,c.schedule(arm,0)[0])
            self.assertEqual(len(metrics),6)
            self.assertGreater(metrics[4],0)
            model.zero_grad();loss.backward()
            self.assertIsNotNone(model.result.weight.grad)
            self.assertTrue(all(q.grad is None for q in model.target.parameters()))
            losses.append(float(loss.detach()))
        self.assertGreater(losses[1],losses[0])
        self.assertNotEqual(losses[1],losses[2])
        with self.assertRaises(ValueError):c.loss_for(model,c.CANDIDATE,row,torch.tensor([1,0]),time.monotonic()+30,8)

    def test_mastery_fail_closed(self):
        rows=[dict(seed=1,arm=k,adequate=k!=c.NEGATIVE,after=dict(familiar=dict(rollout=.01))) for k in c.ARMS]
        self.assertTrue(c.eligibility(rows,(1,))[1])
        rows[0]['adequate']=False
        self.assertFalse(c.eligibility(rows,(1,))[1])
        with self.assertRaises(RuntimeError):c.eligibility(rows[:-1]+[rows[0]],(1,))
