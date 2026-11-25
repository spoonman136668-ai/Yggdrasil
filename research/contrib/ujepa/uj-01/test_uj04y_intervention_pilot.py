"""Source-free fabricated Y0 interface fixtures. No trial data or fitting."""
import unittest
import torch
import uj04y_intervention_pilot as y

class InterventionFixtures(unittest.TestCase):
    def test_factorized_local_effect(self):
        m=y.Factorized()
        a=torch.zeros(2,6);b=a.clone();b[:,2]=.5
        other=torch.zeros(2,3,3);changed=other.clone();changed[:,0,:]=torch.tensor([.2,.3,1.])
        p=m.heads(b,other)[0]-m.heads(a,other)[0]
        q=m.heads(b,changed)[0]-m.heads(a,changed)[0]
        self.assertTrue(torch.allclose(p,q,atol=1e-6))
        p.sum().backward()
        self.assertIsNotNone(m.action_effect[0].weight.grad)

    def test_matched_loss_and_target_isolation(self):
        a=torch.zeros(2,6);b=a.clone();b[:,2]=.5
        other=torch.zeros(2,3,3)
        ya=torch.tensor([[1.,0.],[-1.,0.]]);yb=torch.tensor([[2.,0.],[-2.,0.]])
        for arm in y.ARMS:
            m=y.make_model(arm)
            loss,metrics=y.loss_for(m,a,b,other,ya,yb,arm,torch.tensor([1,0]))
            self.assertGreater(metrics['contrast_mismatch'],0.)
            loss.backward()
            self.assertTrue(all(p.grad is None for p in m.target.parameters()))
            before=m.heads(a,other)[0].detach()
            with torch.no_grad():
                for p in m.target.parameters():p.fill_(float('nan'))
            self.assertTrue(torch.equal(before,m.heads(a,other)[0].detach()))

    def test_reject_unmatched_state(self):
        a=torch.zeros(2,6);b=a.clone();b[:,0]=.5
        other=torch.zeros(2,3,3);ya=torch.ones(2,2)
        with self.assertRaises(ValueError):
            y.loss_for(y.Factorized(),a,b,other,ya,ya,'factorized_pair',torch.tensor([1,0]))

    def test_independent_aux_gate(self):
        rows=[dict(seed=1,arm=a,adequate=a in y.CORE,after=dict(familiar=dict(endpoint=.01))) for a in y.ARMS]
        self.assertEqual(y.gate(rows,(1,))[1],dict(pair=True,structural=True,jepa=False))
        rows[0]['adequate']=False
        self.assertFalse(any(y.gate(rows,(1,))[1].values()))
        with self.assertRaises(RuntimeError):y.gate(rows[:-1],(1,))

    def test_screen_fail_closed(self):
        candidate=dict(rollout=.1,effect=.1,strata={'a':dict(rollout=.1,effect=.1)})
        control=dict(rollout=.1,effect=.2)
        negative=dict(rollout=1.,effect=1.)
        self.assertTrue(y.screen(candidate,(control,),negative))
        self.assertFalse(y.screen(candidate,(dict(rollout=.05,effect=.2),),negative))
        candidate['strata']['a']['effect']=.16
        self.assertFalse(y.screen(candidate,(control,),negative))
