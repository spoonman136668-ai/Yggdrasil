"""RD01 frozen source-free engineering test: opt-in direct terminal reward.

Frozen separately in RD01-FROZEN-ENGINEERING.md before implementation. The
original CAP04 preregistered DEV and accepted native learner are not invoked.
"""
import hashlib
import json
import unittest

from yggdrasil.native_context_basis import canonical, digest
from yggdrasil.native_predictive_state_split import (
    PredictiveStateSplit, SCHEMA, SCHEMA_DIRECT,
)
from yggdrasil.native_predictive_state_controls import MatchedHistoryControls

VIEWS = ((0, 0), (0, 0))
ACTION = (0, 0)


def source_id(reward, index):
    return hashlib.sha256(
        f"cap04-rd01-only/reward={reward}/step={index}".encode("ascii")
    ).hexdigest()


class DirectRewardShadowEngineeringTests(unittest.TestCase):
    def test_fixed_source_free_structural_reward_falsifier(self):
        for reward in (0, 1):
            with self.subTest(reward=reward):
                original = PredictiveStateSplit()
                direct = PredictiveStateSplit(reward_mode="direct")
                fitted = MatchedHistoryControls()
                for i in range(128):
                    s2 = i % 2
                    args = (source_id(reward, i), VIEWS, ACTION,
                            s2, reward, (0, s2, 0))
                    # Same actually observed episode; no simulated held labels.
                    for learner in (original, direct, fitted):
                        learner.observe(*args)
                self.assertEqual((original.count, direct.count, fitted.count),
                                 (128, 128, 128))
                previous = (original.checkpoint(), direct.checkpoint(),
                            fitted.checkpoint())
                xor = [original.forecast(VIEWS, ACTION, "residual", s2)
                       for s2 in (0, 1)]
                candidate = [direct.forecast(VIEWS, ACTION, "residual", s2)
                             for s2 in (0, 1)]
                conventional = [fitted.forecast(
                    VIEWS, ACTION, "residual", s2)[
                        "full_history_exact_state_action_Beta"]
                    for s2 in (0, 1)]
                xor_brier = sum((p - reward) ** 2 for p in xor) / 2
                candidate_brier = sum((p - reward) ** 2
                                      for p in candidate) / 2
                control_brier = sum((p - reward) ** 2
                                    for p in conventional) / 2
                self.assertAlmostEqual(sum(xor), 1.0, places=12)
                self.assertGreaterEqual(xor_brier, 0.25 - 1e-12)
                self.assertLess(candidate_brier, 0.05)
                self.assertLess(candidate_brier, xor_brier)
                reference = (1.0 / 66) if reward == 0 else (65.0 / 66)
                for p in conventional:
                    self.assertAlmostEqual(p, reference, places=12)
                self.assertLess(control_brier, 0.001)
                self.assertEqual(previous, (
                    original.checkpoint(), direct.checkpoint(),
                    fitted.checkpoint()))
                self.assertEqual(
                    PredictiveStateSplit.restore(
                        previous[0], digest(previous[0])).checkpoint(),
                    previous[0])
                restored = PredictiveStateSplit.restore(
                    previous[1], digest(previous[1]))
                self.assertEqual(restored.reward_mode, "direct")
                self.assertEqual(restored.checkpoint(), previous[1])
                for s2 in (0, 1):
                    self.assertEqual(
                        restored.forecast(VIEWS, ACTION, "residual", s2),
                        candidate[s2])

    def test_frozen_xor_v1_and_shadow_direct_checkpoint_are_disjoint(self):
        original = PredictiveStateSplit()
        direct = PredictiveStateSplit(reward_mode="direct")
        self.assertEqual(original.checkpoint(),
                         canonical({"schema": SCHEMA, "sham": False,
                                    "events": []}))
        self.assertNotIn(b"reward_mode", original.checkpoint())
        self.assertEqual(direct.checkpoint(),
                         canonical({"schema": SCHEMA_DIRECT, "sham": False,
                                    "reward_mode": "direct", "events": []}))
        self.assertNotEqual(original.checkpoint(), direct.checkpoint())
        for learner in (original, direct):
            learner.observe(source_id(0, 300), VIEWS, ACTION, 1, 0, (0, 1, 0))
            raw = learner.checkpoint()
            cold = PredictiveStateSplit.restore(raw, digest(raw))
            self.assertEqual(raw, cold.checkpoint())
            self.assertEqual(learner.reward_mode, cold.reward_mode)
            for first in (0, 1):
                self.assertEqual(
                    learner.forecast(VIEWS, ACTION, "residual", first),
                    cold.forecast(VIEWS, ACTION, "residual", first))
            with self.assertRaisesRegex(ValueError, "DUPLICATE_OR_CONFLICT"):
                learner.observe(source_id(0, 300), VIEWS, ACTION,
                                0, 1, (0, 0, 0))
            self.assertEqual(learner.checkpoint(), raw)
        for mode in ("other", "", 1, None):
            with self.assertRaisesRegex(ValueError, "REWARD_MODE"):
                PredictiveStateSplit(reward_mode=mode)
        before = direct.checkpoint()
        # A valid forged hash cannot turn new-format learned evidence into
        # original CAP04 mode or re-interpret the old schema as direct.
        doc = json.loads(before)
        doc["reward_mode"] = "xor"
        with self.assertRaisesRegex(ValueError, "COLD_REJECTED"):
            b = canonical(doc)
            PredictiveStateSplit.restore(b, digest(b))
        doc = json.loads(before)
        doc["schema"] = SCHEMA
        with self.assertRaisesRegex(ValueError, "COLD_REJECTED"):
            b = canonical(doc)
            PredictiveStateSplit.restore(b, digest(b))
        doc = json.loads(original.checkpoint())
        doc["reward_mode"] = "direct"
        with self.assertRaisesRegex(ValueError, "COLD_REJECTED"):
            b = canonical(doc)
            PredictiveStateSplit.restore(b, digest(b))
        self.assertEqual(direct.checkpoint(), before)

    def test_no_future_stage_one_sensor_and_read_purity(self):
        for mode in ("xor", "direct"):
            learner = PredictiveStateSplit(reward_mode=mode)
            before = learner.checkpoint()
            self.assertEqual(
                learner.forecast(VIEWS, ACTION, "transition"), 0.5)
            with self.assertRaisesRegex(ValueError, "FUTURE_SENSOR"):
                learner.forecast(VIEWS, ACTION, "transition", 1)
            with self.assertRaisesRegex(ValueError, "BIT"):
                learner.forecast(VIEWS, ACTION, "residual")
            self.assertEqual(learner.checkpoint(), before)


if __name__ == "__main__":
    unittest.main()
