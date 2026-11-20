"""NCI07 on-policy DEV guard tests: no full-world trial evaluation here."""
from __future__ import annotations

import unittest

from aba_recall import BoundedCausalRecall, ExactGridSwitchBayes
from onpolicy_dev_screen import (
    ARM_NAMES, CASES, COLD_STEP, PHASE_STEPS, TOTAL_STEPS,
    consequence, eligible_action, expected_brier, new_arms, probability,
)
from protocol_guard import AuditError, canonical_public_tape


class OnPolicyGuardTests(unittest.TestCase):
    def test_frozen_world_sizes(self):
        self.assertEqual(len(CASES), 5)
        self.assertEqual(TOTAL_STEPS, 3 * PHASE_STEPS)
        self.assertEqual(COLD_STEP, 200)
        self.assertEqual(len(ARM_NAMES) * TOTAL_STEPS * len(CASES), 9600)

    def test_reversal_94_law_evaluator_only(self):
        self.assertEqual(probability("REV94", 0, 0), .94)
        self.assertEqual(probability("REV94", 128, 0), .06)
        self.assertEqual(probability("REV94", 256, 0), .94)

    def test_observationally_indistinguishable_fixed_arm(self):
        self.assertEqual(set(probability("UNIDENTIFIABLE_ACTION0", t, 0)
                             for t in range(TOTAL_STEPS)), {.5})
        self.assertEqual(probability("UNIDENTIFIABLE_ACTION0", 0, 1), .9)
        self.assertEqual(probability("UNIDENTIFIABLE_ACTION0", 128, 1), .1)

    def test_stationary_baseline_does_not_change(self):
        self.assertEqual(len(set(CASES["STATIONARY"])), 1)

    def test_hashed_dev_outcome_reproducible(self):
        self.assertEqual(consequence("REV94", 37, 1), consequence("REV94", 37, 1))
        self.assertIn(consequence("NEUTRAL_THIRD", 130, 0), (0, 1))

    def test_forced_action0_prevents_unseen_counterfactual(self):
        m = BoundedCausalRecall()
        for t in (0, 1, 17, 127, 255, 383):
            action, reason = eligible_action(m, t, "UNIDENTIFIABLE_ACTION0")
            self.assertEqual((action, reason), (0, "forced-unidentifiable"))

    def test_common_probe_accounted_as_action(self):
        m = BoundedCausalRecall()
        self.assertEqual(eligible_action(m, 0, "REV80"), (0, "fixed-probe"))
        self.assertEqual(eligible_action(m, 1, "REV80"), (1, "fixed-probe"))

    def test_abstention_costs_real_action(self):
        self.assertEqual(eligible_action(BoundedCausalRecall(), 2, "REV94"),
                         (0, "abstention-fallback"))

    def test_invalid_synthetic_query_rejected(self):
        for world, step, action in (("missing", 0, 0), ("REV94", -1, 0),
                                    ("REV94", 384, 0), ("REV94", 0, True),
                                    ("REV94", 0, 2)):
            with self.subTest(world=world, step=step, action=action):
                with self.assertRaises(AuditError):
                    probability(world, step, action)

    def test_public_action_does_not_receive_evaluator_fields(self):
        row = {"observation": 7, "action": 0, "outcome": 1}
        canonical_public_tape([row])
        for key in ("phase", "source_id", "oracle", "counterfactual"):
            with self.subTest(key=key), self.assertRaises(AuditError):
                BoundedCausalRecall().observe(dict(row, **{key: "hidden"}))

    def test_expected_brier_is_proper(self):
        self.assertAlmostEqual(expected_brier(.94, .94), .94 * .06)
        self.assertAlmostEqual(expected_brier(.5, .5), .25)
        self.assertGreater(expected_brier(.94, .06), expected_brier(.94, .94))

    def test_arm_set_independent_state(self):
        arms = new_arms()
        self.assertEqual(tuple(arms), ARM_NAMES)
        self.assertIsInstance(arms["grid_hmm"], ExactGridSwitchBayes)
        arms["candidate"].observe({"observation": 7, "action": 0, "outcome": 1})
        self.assertEqual(arms["grid_hmm"].witnesses, 0)


if __name__ == "__main__":
    unittest.main()
