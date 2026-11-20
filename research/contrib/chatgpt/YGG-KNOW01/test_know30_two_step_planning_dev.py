"""KNOW30 mechanical and privacy checks — never consume prospective HELD."""
import random
import unittest
from know30_two_step_planning_dev import (
    PROTO,PREREG,PREREG_BLOB,MODE,MATCH,SHIFT,COHORTS,ARMS,
    protocol,structured_bit,high_uncertainty,horizon2_values,
    planner_action,independent_bellman_certificate,make_model,
    public_action,frozen_source_ids,witness,N,
)
from unknown_action_affordance_dev import JointHypothesis,digest

class KNOW30Unheld(unittest.TestCase):
    def test_prereg_exact_frozen(self):
        p=protocol()
        self.assertEqual(p["schema"],PROTO)
        self.assertEqual(PREREG,"effc0078a561fcc7c5a2584c95f75a97388a1ae5")
        self.assertEqual(PREREG_BLOB,"bd804e6a94debb4b314d9d6a86af179bb44de1a2")
        self.assertEqual(MODE,"engineering_fixture_only")
        self.assertEqual((len(MATCH),len(SHIFT),len(COHORTS),len(ARMS),N),
                         (6,6,2,8,32))
        self.assertTrue(set(MATCH).isdisjoint(SHIFT))
        self.assertEqual(p["held"]["actions_per_arm_per_cohort"],576)
        self.assertFalse(p["provenance"]["original_first_use_426"])
    def test_independent_two_branch_bellman_identity(self):
        certificate=independent_bellman_certificate()
        self.assertEqual(certificate["first_actions"],4)
        self.assertEqual(certificate["second_actions"],4)
        self.assertLessEqual(certificate["max_abs_error"],1e-10)
    def test_hypothetical_updates_never_mutate_original(self):
        m=JointHypothesis([1/6.]*6)
        saved=m.checkpoint()
        values=horizon2_values(m,0)
        self.assertEqual(len(values),4)
        self.assertEqual(m.checkpoint(),saved)
        self.assertIn(planner_action(m,0),range(4))
        self.assertEqual(m.checkpoint(),saved)
        with self.assertRaises(ValueError):
            horizon2_values(m,31)
        self.assertGreater(high_uncertainty(m),0.)
    def test_compute_matched_control_same_deliberations(self):
        x=JointHypothesis([1/6.]*6)
        rng=random.Random(7)
        for arm in ("fit_lookahead2","fit_entropy_compute_matched"):
            a,calls=public_action(arm,x,0,rng)
            self.assertIn(a,range(4))
            self.assertEqual(calls,1)
        fast=public_action("fit_entropy_fast",x,0,rng)
        self.assertEqual(fast[1],0)
        self.assertEqual(len(x.events),0)
    def test_privacy_and_source_denials_without_witness_execution(self):
        for arm in ARMS:
            if arm=="privileged_correct_map_entropy":continue
            with self.assertRaises(ValueError):
                make_model(arm,[1/6.]*6,(0,0))
        with self.assertRaises(ValueError):
            make_model("privileged_correct_map_entropy",[1/6.]*6)
        with self.assertRaises(ValueError):
            frozen_source_ids("original",0,MATCH[0])
        # This invalid mode is rejected before any private outcome exists.
        with self.assertRaises(ValueError):
            witness("prior_matched",0,MATCH[0],0,0,(0,0),
                    source_mode="original_owner")
        with self.assertRaises(ValueError):
            witness("prior_matched",0,MATCH[0],N,0,(0,0))
    def test_structured_rule_and_checkpoint_controls(self):
        for rule in range(4):
            for c in range(8):
                self.assertIn(structured_bit(rule,c),(0,1))
        for k in (True,4,-1):
            with self.assertRaises(ValueError):
                structured_bit(k,0)
        m=JointHypothesis([1/6.]*6)
        m.observe(0,0,0,1)
        raw=m.checkpoint()
        self.assertEqual(JointHypothesis.restore(raw,digest(raw)).checkpoint(),raw)
        with self.assertRaises(ValueError):
            JointHypothesis.restore(raw,"0"*64)
        with self.assertRaises(ValueError):
            m.observe(0,0,0,1)

if __name__=="__main__":
    unittest.main()
