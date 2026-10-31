import json
import unittest
from residual_belief import ResidualBelief, ACTIVE_SLOTS, RETAINED_SLOTS, TOTAL_SLOTS, TARGETS, FEATURES


def xvec(i):
    return tuple(1.0 if j == i % FEATURES else 0.0 for j in range(FEATURES))


def yvec(i):
    return tuple(1.0 if j == i % TARGETS else 0.0 for j in range(TARGETS))


class ResidualBeliefTests(unittest.TestCase):
    def test_fixed_partition_and_capacity_after_many_updates(self):
        m = ResidualBelief()
        for i in range(40):
            m.predict(xvec(i), i % 3)
            receipt = m.observe_selected_outcome(yvec(i))
            self.assertIn(receipt["disposition"], {"formed_active_state", "revised_active_state", "revised_retained_state", "revised_and_promoted_state"})
            self.assertEqual(m.stats()["total_slots"], TOTAL_SLOTS)
            self.assertEqual(m.stats()["active_slots"], ACTIVE_SLOTS)
            self.assertEqual(m.stats()["retained_slots"], RETAINED_SLOTS)

    def test_observation_is_strictly_post_prediction_and_single_use(self):
        m = ResidualBelief()
        with self.assertRaisesRegex(RuntimeError, "NO_PENDING_SELECTED_ACTION"):
            m.observe_selected_outcome(yvec(0))
        m.predict(xvec(0), 0)
        with self.assertRaisesRegex(RuntimeError, "PENDING_OUTCOME"):
            m.predict(xvec(1), 1)
        m.observe_selected_outcome(yvec(0))
        with self.assertRaisesRegex(RuntimeError, "NO_PENDING_SELECTED_ACTION"):
            m.observe_selected_outcome(yvec(0))

    def test_contradictory_outcome_is_counted_and_revises_prediction(self):
        m = ResidualBelief()
        x = xvec(0)
        m.predict(x, 0); m.observe_selected_outcome(yvec(0))
        before = m.predict(x, 0)
        receipt = m.observe_selected_outcome(tuple(-v for v in yvec(0)))
        after = m.predict(x, 0)
        self.assertTrue(receipt["contradiction"])
        self.assertIn("revised", receipt["disposition"])
        self.assertNotEqual(before.values, after.values)

    def test_cold_restart_preserves_predictions_and_state_counts(self):
        m = ResidualBelief()
        for i in range(12):
            m.predict(xvec(i), i % 3); m.observe_selected_outcome(yvec(i))
        blob = m.snapshot()
        control = ResidualBelief.restore(blob)
        restored = ResidualBelief.restore(blob)
        expected = control.predict(xvec(3), 0)
        actual = restored.predict(xvec(3), 0)
        self.assertEqual(expected, actual)
        self.assertEqual(control.stats(), restored.stats())

    def test_pending_outcome_cannot_be_checkpointed(self):
        m = ResidualBelief(); m.predict(xvec(0), 0)
        with self.assertRaisesRegex(RuntimeError, "PENDING_OUTCOME"):
            m.snapshot()

    def test_checkpoint_tampering_rejected(self):
        m = ResidualBelief(); m.predict(xvec(0), 0); m.observe_selected_outcome(yvec(0))
        data = json.loads(m.snapshot())
        data["payload"]["slots"][0]["target"][0] = 0.75
        with self.assertRaisesRegex(ValueError, "HASH_MISMATCH"):
            ResidualBelief.restore(json.dumps(data).encode())

    def test_invalid_dimensions_and_nonfinite_values_rejected(self):
        m = ResidualBelief()
        with self.assertRaisesRegex(ValueError, "DIMENSION"):
            m.predict((0.0,))
        m.predict(xvec(0), 0)
        with self.assertRaisesRegex(ValueError, "OUT_OF_RANGE"):
            m.observe_selected_outcome([float("nan")] * TARGETS)


    def test_same_public_features_are_separated_by_selected_action(self):
        m = ResidualBelief()
        m.predict(xvec(0), 0); m.observe_selected_outcome(yvec(0))
        unseen = m.predict(xvec(0), 1)
        self.assertFalse(unseen.covered)
        m.observe_selected_outcome(yvec(1))
        action_zero = m.predict(xvec(0), 0)
        m.pending = None
        action_one = m.predict(xvec(0), 1)
        m.pending = None
        self.assertNotEqual(action_zero.values, action_one.values)

    def test_invalid_selected_action_is_rejected(self):
        m = ResidualBelief()
        with self.assertRaisesRegex(ValueError, "SELECTED_ACTION_OUT_OF_RANGE"):
            m.predict(xvec(0), 3)

    def test_checkpoint_has_exactly_sixteen_slots_and_declared_partition(self):
        data = json.loads(ResidualBelief().snapshot())
        self.assertEqual(len(data["payload"]["slots"]), 16)
        self.assertEqual(data["payload"]["partition"], {"active": 7, "retained": 9})

    def test_retained_contradiction_is_promoted_without_capacity_growth(self):
        m = ResidualBelief()
        for i in range(16):
            m.predict(xvec(i), i % 3); m.observe_selected_outcome(yvec(i))
        self.assertEqual(m.stats()["active_valid"], 7)
        self.assertEqual(m.stats()["retained_valid"], 9)
        m.predict(xvec(0), 0)
        receipt = m.observe_selected_outcome(tuple(-v for v in yvec(0)))
        self.assertEqual(receipt["disposition"], "revised_and_promoted_state")
        self.assertEqual(m.stats()["active_valid"], 7)
        self.assertEqual(m.stats()["retained_valid"], 9)


if __name__ == "__main__":
    unittest.main()
