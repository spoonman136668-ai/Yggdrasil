"""B0 source-free fixtures: matched arms, gate completeness, fresh seed separation."""
import unittest
from unittest.mock import patch
import uj05b_transfer_pilot as b
import uj05a_stability_pilot as a

class BFixtures(unittest.TestCase):
    def rows(self):
        return [dict(seed=1,arm=k,adequate=k!='relational_shuffled_result',after=dict(familiar=dict(rollout=.01))) for k in b.ARMS]

    def test_exact_matched_positive_controls(self):
        self.assertEqual(len(b.CORE),6)
        self.assertEqual(len(b.ARMS),9)
        self.assertEqual(set(b.ARMS),{k for k in a.ARMS if '_fixed_' not in k})
        self.assertEqual(set(b.CONTROLS),set(b.CORE)-{b.CANDIDATE})
        for k in b.ARMS:
            self.assertAlmostEqual(b.schedule(k,119)[1],.0001)
        self.assertIs(b.train,a.train)
        self.assertIs(b.evaluate,a.evaluate)
        for k in b.ARMS[-3:]:
            self.assertEqual([b.schedule(k,e) for e in range(b.EPOCHS)],[b.schedule(b.CANDIDATE,e) for e in range(b.EPOCHS)])

    def test_independent_gates_and_negative(self):
        rows=self.rows()
        self.assertEqual(b.eligibility(rows,(1,))[1],dict(primary=True,jepa=True))
        next(r for r in rows if r['arm']=='relational_shuffled_aux')['adequate']=False
        self.assertEqual(b.eligibility(rows,(1,))[1],dict(primary=True,jepa=False))
        next(r for r in rows if r['arm']=='dense_teacher')['adequate']=False
        self.assertEqual(b.eligibility(rows,(1,))[1],dict(primary=False,jepa=False))

    def test_reject_incomplete_duplicate_or_unknown(self):
        rows=self.rows()
        for bad in (rows[:-1],rows[:-1]+[rows[0]],rows[:-1]+[dict(rows[-1],arm='unknown')]):
            with self.assertRaises(RuntimeError):b.eligibility(bad,(1,))

    def test_fresh_split_and_prior_lineage(self):
        b.assert_disjoint_seeds()
        for name,value in (('FAMILIAR_SEED',b.FIT_SEED+1),('TRANSFER_SEED',311300),('SEEDS',a.SEEDS)):
            with patch.object(b,name,value):
                with self.assertRaises(RuntimeError):b.assert_disjoint_seeds()

    def test_frozen_transfer_screen(self):
        c=dict(rollout=.04,effect=.04,strata={'fixture':dict(rollout=.04,effect=.04)})
        strong=dict(rollout=.04,effect=.05)
        neg=dict(rollout=1.,effect=1.)
        self.assertTrue(b.y.screen(c,(strong,),neg))
        self.assertFalse(b.y.screen(c,(dict(rollout=.04,effect=.049),),neg))
        self.assertFalse(b.y.screen(c,(dict(rollout=.03,effect=.05),),neg))
