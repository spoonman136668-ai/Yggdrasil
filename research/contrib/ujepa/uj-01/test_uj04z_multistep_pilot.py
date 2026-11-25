"""Fabricated source-free Z0 checks; no trial generation or fitting."""
import time
import unittest
import torch
import uj04z_multistep_pilot as z
import uj04x_dynamics_pilot as x

class ZFixtures(unittest.TestCase):
    def setUp(self):
        self.deadline=time.monotonic()+30
        s=torch.zeros(2,4,2);s[1,:,0]=.7
        p=torch.tensor([[.3,.2,0.],[.4,.3,1.]])
        i,m=x.graph(4,'path')
        a=torch.zeros(2,8,4,1);b=a.clone()
        a[0,:,0,0]=.5;b[0,:,0,0]=-.5
        a[1,:,2,0]=-.4;b[1,:,2,0]=.4
        o=torch.tensor([[0,1,2],[2,0,1]])
        ta=torch.ones(2,8,4,2)*.2;tb=-ta
        ta[1]*=-1;tb[1]*=-1
        self.row=('fixture',s,p,i,m,a,b,o,ta,tb)

    def test_self_fed_gradient_and_teacher_distinction(self):
        _,s,p,i,m,a,_,o,ta,_=self.row
        model=x.Cell(False)
        pred,_=z.trace(model,s,p,i,m,a,o,self.deadline)
        teacher,_=z.trace(model,s,p,i,m,a,o,self.deadline,ta)
        self.assertTrue(torch.equal(pred[:,0],teacher[:,0]))
        self.assertFalse(torch.allclose(pred[:,1:],teacher[:,1:]))
        pred[:,-1].sum().backward()
        self.assertIsNotNone(model.result.weight.grad)

    def test_all_arms_and_target_isolation(self):
        for arm in z.ARMS:
            model=x.Cell(arm.startswith('dense'))
            loss,metrics=z.loss_for(model,arm,self.row,torch.tensor([1,0]),self.deadline)
            self.assertGreater(metrics[2],0.)
            loss.backward()
            self.assertTrue(all(p.grad is None for p in model.target.parameters()))
            _,s,p,i,m,a,_,o,_,_=self.row
            with torch.no_grad():
                before=z.trace(model,s,p,i,m,a,o,self.deadline)[0]
                for q in model.target.parameters():q.fill_(float('nan'))
                after=z.trace(model,s,p,i,m,a,o,self.deadline)[0]
            self.assertTrue(torch.equal(before,after))

    def test_bad_permutation(self):
        with self.assertRaises(ValueError):
            z.loss_for(x.Cell(False),'relational_rollout',self.row,torch.tensor([0,0]),self.deadline)

    def test_gate_independence(self):
        rows=[dict(seed=1,arm=a,adequate=a in z.ARMS[:4],after=dict(familiar=dict(rollout=.01))) for a in z.ARMS]
        self.assertEqual(z.eligibility(rows,(1,))[1],dict(primary=True,jepa=False))
        rows[0]['adequate']=False
        self.assertFalse(any(z.eligibility(rows,(1,))[1].values()))
        with self.assertRaises(RuntimeError):z.eligibility(rows[:-1],(1,))
