"""ST11 source-only public-shaped mechanics, NOT new world/held science."""
from hashlib import sha256
import json
import unittest

from research.nci04_st9.native_repair import NativeRepair8, roll
from research.nci04_st11.public_probe_preference import (
    NativeProbePreference, canonical,
)


X = 0x35


def bits(value):
    return [(value >> index) & 1 for index in range(8)]


def public_shape_cycle(native, bank, effect=0, *, source_index=0):
    """A hand-constructed public-shaped mechanics fixture, not a real actor."""
    native.reset_episode()
    neutral = roll(X, 1)
    native.observe(bits(X), 0, bits(X ^ neutral), bits(neutral), train=False)
    before = native.snapshot()
    action = bank.propose(native)
    if action is None:
        raise ValueError("ST11_MECHANICAL_EXHAUSTED")
    public_before = bits(neutral)
    new_byte = roll(neutral, 1) ^ effect
    public_after = bits(new_byte)
    native.observe(public_before, action,
                   bits(neutral ^ new_byte), public_after, train=True)
    after = native.snapshot()
    ref = sha256(("ST11-UNSCORED-PUBLIC-SHAPE-" + str(source_index))
                 .encode("ascii")).hexdigest()
    return (bank.observe_revealed(before, after, public_before,
                                 action, public_after, ref),
            (before, after, public_before, action, public_after, ref))


class ObservedPreferenceContract(unittest.TestCase):
    def test_fits_realized_native_information_gain_from_valid_public_shape(self):
        native = NativeRepair8()
        bank = NativeProbePreference(native)
        initial_native = native.snapshot()
        for episode in range(5):
            bank, receipt = public_shape_cycle(native, bank, 0,
                                               source_index=episode)
            self.assertEqual(bank.origin_count + len(bank.events),
                             native.updates)
            self.assertIs(
                NativeProbePreference.restore(bank.snapshot(), native).__class__,
                NativeProbePreference,
            )
        self.assertEqual(native.updates, 5)
        self.assertEqual(native.degree, 1)
        self.assertEqual(len(bank.events), 5)
        self.assertEqual(bank.events[0][-1], 1)
        self.assertEqual(bank.events[-1][-1], 0)
        self.assertNotEqual(initial_native, native.snapshot())
        self.assertGreater(sum(bank.trials), 5)
        self.assertGreater(sum(bank.positive), 0)
        self.assertLess(sum(bank.positive), sum(bank.trials))
        native.reset_episode()
        neutral = roll(X, 1)
        native.observe(bits(X), 0, bits(X ^ neutral), bits(neutral), train=False)
        snap = native.snapshot()
        proposal = bank.propose(native)
        self.assertIsNotNone(proposal)
        self.assertEqual(proposal,
                         NativeProbePreference.restore(bank.snapshot(),
                                                       native).propose(native))
        self.assertEqual(native.snapshot(), snap)

    def test_duplicate_is_idempotent_and_conflicting_ref_fails_closed(self):
        native = NativeRepair8()
        original = NativeProbePreference(native)
        changed, evidence = public_shape_cycle(native, original, 0, source_index=5)
        self.assertIs(changed.observe_revealed(*evidence), changed)
        before = changed.snapshot()
        bad = list(evidence)
        bad[-1] = "0" * 64
        bad[3] = 16 if bad[3] != 16 else 15
        with self.assertRaises(ValueError):
            changed.observe_revealed(*bad)
        self.assertEqual(changed.snapshot(), before)
        bad = list(evidence)
        bad[-1] = "1" * 64
        bad[4] = bits(0)
        with self.assertRaises(ValueError):
            changed.observe_revealed(*bad)
        self.assertEqual(changed.snapshot(), before)
        with self.assertRaisesRegex(ValueError, "STALE"):
            changed.observe_revealed(
                evidence[0], evidence[1], evidence[2], evidence[3],
                evidence[4], "2" * 64
            )
        self.assertEqual(changed.snapshot(), before)

    def test_cold_counter_tampering_and_wrong_native_denied(self):
        native = NativeRepair8()
        bank = NativeProbePreference(native)
        bank, _ = public_shape_cycle(native, bank, source_index=0)
        original = bank.snapshot()
        for patch in ({"positive": [100] * 16},
                      {"scientific_pass": True},
                      {"origin_count": 8},
                      {"events": []},
                      {"current_identity": "x" * 64},
                      {"trials": [0] * 16}):
            x = json.loads(original)
            x.update(patch)
            with self.assertRaises(ValueError):
                NativeProbePreference.restore(canonical(x), native)
        with self.assertRaisesRegex(ValueError, "CUSTODY"):
            NativeProbePreference.restore(original, NativeRepair8())
        self.assertEqual(bank.snapshot(), original)

    def test_native_prior_retained_and_no_unannounced_action(self):
        native = NativeRepair8()
        original = NativeProbePreference(native)
        updated, evidence = public_shape_cycle(native, original, 0)
        # Opt-in may begin on already trained ST9 state, without discarding it.
        newer = NativeProbePreference(native)
        self.assertEqual(newer.origin_count, 1)
        self.assertEqual(newer.events, [])
        cold = native.snapshot()
        self.assertEqual(newer.snapshot(),
                         NativeProbePreference.restore(
                             newer.snapshot(), NativeRepair8.restore(cold)
                         ).snapshot())
        native.reset_episode()
        with self.assertRaisesRegex(ValueError, "CALIBRATION"):
            newer.propose(native)
        self.assertEqual(native.core if hasattr(native, "core") else
                         native.updates, 1)
        self.assertEqual(updated.events[0][3], evidence[3])

    def test_eight_intervention_limit_and_zero_original_first_use(self):
        native = NativeRepair8()
        bank = NativeProbePreference(native)
        for episode in range(8):
            bank, _ = public_shape_cycle(native, bank, 0,
                                         source_index=episode)
        self.assertEqual(native.updates, 8)
        self.assertEqual(len(bank.events), 8)
        self.assertEqual(len(set(e[0] for e in bank.events)), 8)
        native.reset_episode()
        neutral = roll(X, 1)
        native.observe(bits(X), 0, bits(X ^ neutral), bits(neutral), train=False)
        self.assertIsNone(bank.propose(native))
        self.assertFalse(json.loads(bank.snapshot())["scientific_pass"])
        self.assertFalse(json.loads(bank.snapshot())["accepted_native"])


if __name__ == "__main__":
    unittest.main()
