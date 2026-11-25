"""D0 fabricated receipt tests; never generate trial data."""
import copy
import unittest
from unittest.mock import patch
import uj06b_transfer_pilot as d
import uj06a_local_pilot as c

class DFixtures(unittest.TestCase):
    def rows(self):
        return [dict(seed=1,arm=k,adequate=k in d.POSITIVE,steps=2880,
            endpoint_steps_exposed=737280,fit_history=[.04]*5,
            shuffle_ratios=[1.]*(2 if k in c.CORE else 3),
            after=dict(fit=dict(rollout=.04,effect=.05),familiar=dict(rollout=.05,effect=.06)),
            checkpoint_sha256='a'*64,checkpoint_bytes=100,wall_seconds=1.,cpu_seconds=1.) for k in d.ARMS]

    def test_exact_reuse(self):
        self.assertIs(d.train,c.train)
        self.assertIs(d.evaluate,c.evaluate)
        self.assertEqual(d.CONTROLS,c.CONTROLS)
        self.assertEqual(len(d.POSITIVE),8)
        self.assertEqual(len(d.CORRUPTED),2)

    def test_negative_controls_do_not_require_true_target_plateau(self):
        r=self.rows()
        self.assertTrue(d.eligibility(r,(1,))[1])
        next(x for x in r if x['arm']==d.CORRUPTED[0])['after']['fit']['rollout']=.101
        self.assertFalse(d.eligibility(r,(1,))[1])

    def test_positive_mastery_and_bad_negative_fail_closed(self):
        for arm,key,value in ((d.CANDIDATE,'adequate',False),(d.NEGATIVE,'steps',2879),
                (d.CORRUPTED[0],'shuffle_ratios',[1.,1.,.49]),(d.NEGATIVE,'checkpoint_sha256','bad'),
                (d.CORRUPTED[0],'wall_seconds',float('nan'))):
            r=self.rows();next(x for x in r if x['arm']==arm)[key]=value
            self.assertFalse(d.eligibility(r,(1,))[1])
        r=self.rows()
        with self.assertRaises(RuntimeError):d.eligibility(r[:-1]+[r[0]],(1,))

    def test_seed_disjointness(self):
        d.assert_disjoint_seeds()
        for k,v in (('TRANSFER_SEED',331300),('SEEDS',c.SEEDS),('FAMILIAR_SEED',d.FIT_SEED+1)):
            with patch.object(d,k,v):
                with self.assertRaises(RuntimeError):d.assert_disjoint_seeds()

    def test_original_screen(self):
        candidate=dict(rollout=.04,effect=.04,strata={'fixture':dict(rollout=.04,effect=.04)})
        control=dict(rollout=.04,effect=.05)
        self.assertTrue(d.y.screen(candidate,(control,),dict(rollout=1.,effect=1.)))
        self.assertFalse(d.y.screen(candidate,(dict(rollout=.04,effect=.049),),dict(rollout=1.,effect=1.)))
