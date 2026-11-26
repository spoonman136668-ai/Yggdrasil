"""Source-free UJ07A fixtures: fabricated tensors and receipts only."""
import time
import unittest
from unittest.mock import patch
import torch
import uj07a_residual_pilot as e
import uj06a_local_pilot as c

class ResidualFixtures(unittest.TestCase):
    def rows(self):
        return [dict(seed=1,arm=k,adequate=k in e.POSITIVE,steps=2880,
            endpoint_steps_exposed=737280,fit_history=[.04]*5,
            shuffle_ratios=[1.]*(2 if k in c.CORE else 3),
            after=dict(fit=dict(rollout=.04,effect=.05),familiar=dict(rollout=.05,effect=.06)),
            checkpoint_sha256='a'*64,checkpoint_bytes=100,wall_seconds=1.,cpu_seconds=1.) for k in e.ARMS]

    def test_initial_identity_and_bound(self):
        m=e.ResidualCell()
        own=torch.zeros(2,4,6);other=torch.zeros(2,4,3,3)
        base,z,corr=m.parts(own,other)
        self.assertTrue(torch.equal(corr,torch.zeros_like(corr)))
        self.assertTrue(torch.equal(m.heads(own,other)[0],base))
        with torch.no_grad():m.correct[-1].bias.fill_(100)
        self.assertTrue((m.parts(own,other)[2].abs()<=e.BOUND).all())
        m.enabled=False
        self.assertTrue(torch.equal(m.heads(own,other)[0],base))

    def test_inference_independent_of_truth_and_gradient_detach(self):
        m=e.ResidualCell()
        own=torch.zeros(2,4,6);other=torch.zeros(2,4,3,3)
        _,_,corr=m.parts(own,other)
        corr.sum().backward()
        self.assertIsNone(m.result.weight.grad)
        self.assertIsNone(m.predict.weight.grad)
        self.assertIsNotNone(m.correct[-1].bias.grad)
        self.assertEqual(len(e.NEW),3)
        self.assertEqual(len(e.ARMS),13)

    def test_mastery_and_corruption(self):
        r=self.rows()
        self.assertTrue(e.eligibility(r,(1,))[1])
        for arm,key,value in ((e.CANDIDATE,'adequate',False),(e.SHUFFLED,'shuffle_ratios',[1.,1.,.49]),
                              (e.DIRECT,'steps',2879),(e.NEGATIVE,'checkpoint_sha256','bad')):
            r=self.rows();next(x for x in r if x['arm']==arm)[key]=value
            self.assertFalse(e.eligibility(r,(1,))[1])
        r=self.rows();next(x for x in r if x['arm']==e.SHUFFLED)['after']['fit']['rollout']=.101
        self.assertFalse(e.eligibility(r,(1,))[1])
        with self.assertRaises(RuntimeError):e.eligibility(r[:-1]+[r[0]],(1,))

    def test_seed_disjointness(self):
        e.assert_disjoint_seeds()
        for k,v in (('TRANSFER_SEED',341300),('SEEDS',(3401,3402,3403)),('FAMILIAR_SEED',e.FIT_SEED+1)):
            with patch.object(e,k,v):
                with self.assertRaises(RuntimeError):e.assert_disjoint_seeds()

    def test_disable_restores_on_error(self):
        m=e.ResidualCell()
        with patch.object(e,'evaluate',side_effect=RuntimeError('fixture')):
            with self.assertRaises(RuntimeError):e.disabled_score(m,[],time.monotonic()+1)
        self.assertTrue(m.enabled)
