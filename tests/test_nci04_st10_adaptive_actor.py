"""Unscored source-only ST10 mechanics: no private worlds, no held episodes."""
import unittest

from research.nci04_st9.native_repair import NativeRepair8, roll
from research.nci04_st10.adaptive_actor import choose_intervention

X = 0x35


def bits(x):
    return [(x >> i) & 1 for i in range(8)]


def feed_one_public_effect(model, effect):
    """Public-shaped fixture only; not an independent causal world."""
    model.reset_episode()
    neutral = roll(X, 1)
    model.observe(bits(X), 0, bits(X ^ neutral), bits(neutral), train=False)
    action = choose_intervention(model)
    if action is None:
        raise AssertionError("bounded actor exhausted unexpectedly")
    after = roll(neutral, 1) ^ effect
    model.observe(bits(neutral), action, bits(neutral ^ after), bits(after))
    return action - 1


class EvidenceGatedActorContract(unittest.TestCase):
    def test_action_consequence_changes_future_probe_without_source_oracle(self):
        same = NativeRepair8()
        changed = NativeRepair8()
        for _ in range(4):
            self.assertEqual(feed_one_public_effect(same, 0),
                             feed_one_public_effect(changed, 0))
        self.assertEqual(same.rank, 4)
        self.assertEqual(changed.rank, 4)
        # Both policies must ask a source action capable of disconfirming
        # the already-saturated linear hypothesis.
        self.assertEqual(feed_one_public_effect(same, 0), 3)
        self.assertEqual(feed_one_public_effect(changed, 1), 3)
        self.assertEqual(same.degree, 1)
        self.assertEqual(changed.degree, 2)
        same.reset_episode()
        changed.reset_episode()
        for model in (same, changed):
            neutral = roll(X, 1)
            model.observe(bits(X), 0, bits(X ^ neutral), bits(neutral),
                          train=False)
        self.assertNotEqual(choose_intervention(same),
                            choose_intervention(changed))
        self.assertEqual(choose_intervention(same), 7)  # B=6
        self.assertEqual(choose_intervention(changed), 16)  # B=15
        for model in (same, changed):
            snap = model.snapshot()
            self.assertEqual(choose_intervention(model),
                             choose_intervention(NativeRepair8.restore(snap)))
            self.assertEqual(model.snapshot(), snap)

    def test_calibration_not_optional_and_selector_has_no_side_effect(self):
        model = NativeRepair8()
        with self.assertRaisesRegex(ValueError, "CALIBRATION"):
            choose_intervention(model)
        model.reset_episode()
        neutral = roll(X, 1)
        model.observe(bits(X), 0, bits(X ^ neutral), bits(neutral), train=False)
        before = model.snapshot()
        self.assertEqual(choose_intervention(model), 2)  # B=1
        self.assertEqual(model.snapshot(), before)

    def test_eight_action_budget_and_conflict_abstention(self):
        model = NativeRepair8()
        for i in range(8):
            feed_one_public_effect(model, 0 if i < 4 else 1)
        model.reset_episode()
        neutral = roll(X, 1)
        model.observe(bits(X), 0, bits(X ^ neutral), bits(neutral), train=False)
        self.assertIsNone(choose_intervention(model))
        other = NativeRepair8()
        other.post_growth_conflicts = 1
        other.reset_episode()
        other.observe(bits(X), 0, bits(X ^ neutral), bits(neutral), train=False)
        self.assertIsNone(choose_intervention(other))

    def test_wrong_variant_rejected(self):
        for variant in ("no_replay", "no_growth", "erase"):
            with self.assertRaisesRegex(ValueError, "EXACT_REPAIR"):
                choose_intervention(NativeRepair8(variant))


if __name__ == "__main__":
    unittest.main()
