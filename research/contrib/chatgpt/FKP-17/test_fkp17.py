"""FKP17 source-safe fixtures. No native env reset, no original H128 source first-use."""
import hashlib
import math
import unittest

import headroom as h


class FrozenSourceFixture(unittest.TestCase):
    def test_study_source_fences_and_exact_cohort_custody(self):
        self.assertEqual(h.FIT,tuple(range(975100,975108)))
        self.assertEqual(h.AUDIT,tuple(range(975200,975208)))
        self.assertEqual(h.HORIZONS,(16,32,64,128))
        self.assertEqual(h.ANCHORS,(0,16,32,64))
        self.assertEqual(len(h.PLAN_NAMES),24)
        self.assertEqual(h.UPSTREAM_SHA,"a94f2b60d1769ea44df3226561488768e1dff9f4")
        for seed in (976500,976600,975500,974000,975108,975208,0,True):
            with self.assertRaises(PermissionError):
                h.fence(seed,0,0)
        with self.assertRaises(PermissionError):
            h.fence(h.FIT[0],128,0)
        with self.assertRaises(PermissionError):
            h.fence(h.FIT[0],0,24)
        with self.assertRaises(PermissionError):
            h.fence(h.FIT[0],0,-1)

    def test_24_real_legal_action_programs_and_deterministic_replay(self):
        for seed in (h.FIT[0],h.AUDIT[-1]):
            for anchor in h.ANCHORS:
                for plan in range(24):
                    for t in (0,1,7,8,9,16,31,64,127):
                        args=(plan,seed,anchor,t)
                        a=h.planned_action(*args,previous_action=3,
                                           previous_block_positive=False)
                        b=h.planned_action(*args,previous_action=3,
                                           previous_block_positive=False)
                        self.assertEqual(a,b)
                        self.assertIn(a,range(9))
        for k in range(9):
            self.assertEqual(h.planned_action(k,h.FIT[0],16,127),k)
            self.assertEqual(h.planned_action(9+k,h.FIT[0],16,0),k)
            self.assertEqual(h.planned_action(9+k,h.FIT[0],16,8),(k+4)%9)
        with self.assertRaises(ValueError):
            h.planned_action(21,h.FIT[0],16,8,previous_action=None)
        with self.assertRaises(ValueError):
            h.planned_action(0,h.FIT[0],0,128)

    def test_public_feedback_is_source_reward_conditioned_only(self):
        seed=h.FIT[0]
        for plan in (21,22,23):
            a=h.planned_action(plan,seed,0,8,previous_action=4,
                               previous_block_positive=True)
            b=h.planned_action(plan,seed,0,8,previous_action=4,
                               previous_block_positive=False)
            self.assertEqual(a,4)
            self.assertEqual(b,(4+1+plan-21)%9)
            self.assertNotEqual(a,b)

    def test_horizon_prefixes_reuse_one_actual_trajectory(self):
        rewards=[0.125]*20
        goals=[0]*19+[1]
        positive=[1]*20
        negative=[0]*20
        result=h.horizon_prefix_receipts(rewards,goals,positive,negative)
        self.assertAlmostEqual(result["16"]["earned_real_return"],2)
        self.assertAlmostEqual(result["128"]["earned_real_return"],2.5)
        self.assertEqual(result["16"]["goal_events"],0)
        self.assertEqual(result["32"]["goal_events"],1)
        self.assertEqual(result["64"]["goal_events"],1)
        self.assertTrue(result["128"]["terminated_early"])
        self.assertEqual(result["128"]["realized_source_steps"],20)
        with self.assertRaises(ValueError):
            h.horizon_prefix_receipts([],[],[],[])
        with self.assertRaises(ValueError):
            h.horizon_prefix_receipts([float("nan")],[0],[0],[0])

    def test_world_cluster_bootstrap_does_not_double_count_anchors(self):
        rows=[]
        for seed in h.AUDIT:
            for anchor in h.ANCHORS:
                for plan in range(24):
                    rows.append({"seed":seed,"anchor":anchor,"plan":plan,
                                 "valid":True,
                                 "by_horizon":{"128":{
                                   "earned_real_return":0.3 if plan==0 else 0.0,
                                   "goal_events":1 if seed in h.AUDIT[:2] and anchor in (0,16) and plan==0 else 0,
                                   "positive_reward_events":1 if plan==0 else 0,
                                   "negative_reward_events":0,
                                   "realized_source_steps":128
                                 }}})
        paired=h.paired_world_bootstrap(rows,lambda p:max(p.values()),
                    lambda p:p[18],128)
        self.assertAlmostEqual(paired["mean_paired_gain"],0.3)
        self.assertAlmostEqual(paired["world_cluster_ci95"][0],0.3)
        self.assertEqual(paired["audited_worlds"],8)
        # fixture classification is a source-only property, never SCIENTIFIC_PASS
        # Can add shorter horizon outputs to exercise all4 with no actual source.
        for r in rows:
            for n in ("16","32","64"):
                r["by_horizon"][n]=dict(r["by_horizon"]["128"])
        scores=h.describe(rows,18)
        self.assertEqual(scores["classification"],"DEV_SOURCE_HEADROOM_ONLY_NOT_SCIENCE")
        self.assertFalse(scores["scientific_pass"])
        self.assertEqual(scores["horizons"]["128"]["distinct_worlds_with_some_goal"],2)
        self.assertEqual(scores["horizons"]["128"]["goal_reachable_anchor_count"],4)

    def test_no_default_synthetic_policy_is_called_science(self):
        self.assertEqual(h.MAX_REAL_SOURCE_ACTIONS,315000)
        self.assertEqual(h.BOOTSTRAP_COUNT,10000)
        self.assertEqual(h.PLAN_NAMES[18],"BLIND_RANDOM8_0")
        self.assertTrue(all(p.isupper() or "_" in p for p in h.PLAN_NAMES))


if __name__=="__main__":
    unittest.main()
