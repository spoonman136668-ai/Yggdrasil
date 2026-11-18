"""CKAD32 non-B source-only tests of causal intervention policy and stop rules."""
import importlib.util
import itertools
import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parent
S=importlib.util.spec_from_file_location("ckad32_frozen_campaign",ROOT/"campaign.py")
c=importlib.util.module_from_spec(S)
S.loader.exec_module(c)


class CKAD32Tests(unittest.TestCase):
    def test_pinned_program_and_seed_isolation(self):
        self.assertEqual(c.PILOT,(9451,9452))
        self.assertEqual(c.PRIMARY,(1451,1452,1453))
        self.assertFalse(set(c.PILOT)&set(c.PRIMARY))
        self.assertEqual(c.COMMITTEE,24)
        self.assertEqual(c.PROBES,10)
        self.assertEqual(len(c.POLICIES),4)
        for g in c.GRAPHS:
            for t in itertools.product((0,1),repeat=3):
                self.assertIn(c.C30.composition(g,t),(0,1))

    def test_public_held_separation(self):
        for seed in (88001,88002):  # non-pilot, never used for scoring
            held,initial,pool=c.input_partition(seed)
            self.assertEqual((len(held),len(initial),len(pool)),(12,6,14))
            self.assertEqual(len(set(held+initial+pool)),32)
            self.assertFalse(set(held)&set(pool))
            self.assertFalse(set(held)&set(initial))

    def test_real_source_only_intervention_selection_and_survivor_filter(self):
        law=(1,19,2,7)
        init=(0,1,2,3,4,5)
        witnesses=[c.row(x,c.C30.effect(law,x)) for x in init]
        survivors=c.survivor_posterior(witnesses)
        self.assertIn(law,survivors)
        for policy in c.POLICIES:
            pool=(6,7,8,9,10,11,12,13,14,15,16,17,18,19)
            choose,details=c.select_probe(policy,88001,0,0,pool,survivors)
            self.assertIn(choose,pool)
            self.assertNotIn(choose,init)
            self.assertIn("committee_size",details)
            filtered=[x for x in survivors if c.C30.effect(x,choose)==c.C30.effect(law,choose)]
            self.assertIn(law,filtered)
            self.assertLessEqual(len(filtered),len(survivors))
            self.assertGreater(len(filtered),0)

    def test_committee_and_full_exact_bound(self):
        src=[c.row(x,(x&3).bit_count()&1) for x in range(6)]
        survivors=c.survivor_posterior(src)
        self.assertTrue(survivors)
        pool=tuple(range(6,20))
        a,meta=c.select_probe("bounded_committee24",88011,1,0,pool,survivors)
        b,control=c.select_probe("full_exact_information_gain",88011,1,0,pool,survivors)
        self.assertIn(a,pool)
        self.assertIn(b,pool)
        self.assertLessEqual(meta["committee_size"],24)
        self.assertEqual(control["committee_size"],len(survivors))

    def test_pilot_frozen_joint_threshold_and_fail_closed(self):
        def fake(seed,tournament=.19,random=.24,fixed=.24,post=3,rpost=7):
            def policy(name,brier,survivors):
                return {"model":{"cold_restore_exact":True,"retention_exact":True,
                                 "quarantine_exact":True},
                        "metrics":{"native_sparse":{"brier":brier}},
                        "posterior_survivors":[survivors]*3}
            return {"seed":seed,"policy_results":{
                "bounded_committee24":policy("candidate",tournament,post),
                "uniform_random":policy("random",random,rpost),
                "fixed_public_order":policy("fixed",fixed,8),
                "full_exact_information_gain":policy("exact",.20,3),
            }}
        self.assertEqual(c.screen([fake(9451),fake(9452)])["decision"],"PILOT_GO")
        self.assertEqual(c.screen([
            fake(9451,tournament=.24),fake(9452,tournament=.24)
        ])["decision"],"SCREEN_NO_GO")
        b=fake(9452);b["policy_results"]["fixed_public_order"]["model"]["quarantine_exact"]=False
        self.assertEqual(c.screen([fake(9451),b])["decision"],"INVALID")
        with self.assertRaises(AssertionError):
            c.screen([fake(9452),fake(9451)])

    def test_no_primary_seed_execution_and_bad_policy_rejected(self):
        self.assertNotIn(1451,c.PILOT)
        with self.assertRaises(ValueError):
            c.score_seed(999999)
        with self.assertRaises(ValueError):
            c.select_probe("unknown",88011,0,0,(1,2),[(0,0,0,1)])


if __name__=="__main__":
    unittest.main()
