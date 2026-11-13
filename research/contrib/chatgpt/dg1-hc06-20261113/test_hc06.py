"""HC06 reproducibility, independent comparator, physical budget and negative controls."""
import json
import unittest

from bayesian_control import (
    BayesianEntropyPlanner, action_ok, canonical, rule_output, state_ok,
    MAX_SNAPSHOT,
)
from eval_dev import FAMILIES, SourceWorld, hc05, one_world, one_policy


class IndependentBayesianResearchTests(unittest.TestCase):
    def test_independent_baseline_exact_prior_parity(self):
        for state in range(16):
            for action in range(4):
                for h in range(6):
                    self.assertEqual(rule_output(state,action,h),
                                     hc05.local_effect(state,action,h))

    def test_conventional_bayesian_abstains_when_prior_disagrees(self):
        m=BayesianEntropyPlanner()
        self.assertEqual(m.logical_bits,24)
        self.assertIsNone(m.predict(0,0))
        old=m.snapshot()
        for state in range(16):
            self.assertIn(m.choose(state),range(4))
        self.assertEqual(m.snapshot(),old)
        m.observe(0,0,0)
        self.assertEqual(m.predict(0,0),0)
        self.assertIsNone(m.predict(1,0))
        self.assertEqual(m.charged,1)

    def test_public_consequences_restrict_bayesian_posterior(self):
        m=BayesianEntropyPlanner()
        for state in (0,1,2,4):
            outcome=state ^ (rule_output(state,0,0)<<0)
            m.observe(state,0,outcome)
        for state in range(16):
            expected=state^(rule_output(state,0,0)<<0)
            self.assertEqual(m.predict(state,0),expected)

    def test_invalid_public_event_is_transactional(self):
        m=BayesianEntropyPlanner()
        checkpoint=m.snapshot()
        for bad in ((0,0,2),(-1,0,0),(16,0,0),
                    (0,4,0),(True,0,0),(0,True,0),(0,0,16)):
            with self.subTest(bad=bad):
                with self.assertRaises(ValueError):
                    m.observe(*bad)
                self.assertEqual(m.snapshot(),checkpoint)
        with self.assertRaises(TypeError):
            m.observe(0,0,0,hidden_physics="oracle")

    def test_cold_checkpoints_and_tamper_fail_closed(self):
        m=BayesianEntropyPlanner()
        m.observe(0,0,0)
        m.observe(1,0,1)
        data=m.snapshot()
        self.assertLessEqual(len(data),MAX_SNAPSHOT)
        restored=BayesianEntropyPlanner.restore(data)
        self.assertEqual(restored.snapshot(),data)
        forged=bytearray(data)
        forged[15]^=1
        for blob in (bytes(forged),data[:-2],data+b"!",bytearray(data),
                     b"z"*(MAX_SNAPSHOT+1)):
            with self.subTest(length=len(blob)):
                with self.assertRaises(ValueError):
                    BayesianEntropyPlanner.restore(blob)
        bad=json.loads(data)
        bad["payload"]["survivors"]=[66,63,63,63]
        with self.assertRaises(ValueError):
            BayesianEntropyPlanner.restore(json.dumps(bad).encode())

    def test_all_5_arms_charged_exact_actions_no_reset(self):
        row=one_world(41001,"iid")
        for name,report in row["arms"].items():
            self.assertEqual(report["source_actions"],12,name)
            self.assertEqual(report["logical_prior_mask_bits"],24,name)
            self.assertTrue(report["cold_restore"],name)
            self.assertLessEqual(report["checkpoint_bytes"],1024,name)
            self.assertEqual(sum(report["accuracy"][k] for k in
                ("correct","wrong_confident","abstained")),64)

    def test_physical_world_charges_only_real_actions(self):
        world=SourceWorld(41009,"rewired")
        before=41009%16
        q=world.source_next_for_evaluator(before,0,0)
        self.assertEqual(world.physical_actions,0)
        self.assertEqual(world.charge(before,0,0),q)
        self.assertEqual(world.physical_actions,1)

    def test_return_to_A_has_25_actual_physical_steps(self):
        row=one_world(41025,"return_A")
        for r in row["arms"].values():
            self.assertEqual(r["source_actions"],25)
            self.assertTrue(r["cold_restore"])

    def test_unseen_graph_and_majority_negatives_remain_reported(self):
        for seed,group in ((41009,"rewired"),(41017,"majority")):
            with self.subTest(group=group):
                r=one_world(seed,group)
                for policy,receipt in r["arms"].items():
                    scores=receipt["accuracy"]
                    self.assertEqual(sum(scores[k] for k in
                        ("correct","wrong_confident","abstained")),64)
                    self.assertEqual(scores["unseen_total"],
                        sum(scores["unseen_"+k] for k in
                            ("correct","wrong_confident","abstained")))

    def test_source_guardrails_and_frozen_seeds(self):
        for family,seeds in FAMILIES.items():
            self.assertEqual(len(seeds),8)
            for seed in seeds:
                world=SourceWorld(seed,family)
                self.assertEqual(world.physical_actions,0)
        for kind,seed in (("iid",0),("rewired",41001),
                          ("return_A",41009),("majority",41025)):
            with self.assertRaises(ValueError):
                SourceWorld(seed,kind)
        for bad in (-1,16,True,None):
            with self.assertRaises(ValueError):
                state_ok(bad)
        for bad in (-1,4,True,None):
            with self.assertRaises(ValueError):
                action_ok(bad)


if __name__=="__main__":
    unittest.main()
