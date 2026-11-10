"""All checks are public deterministic development fixtures, not science."""

import hashlib
import unittest

from weight_written import (
    OBSERVATIONS, SPEC, SPEC_SHA256, SymbolicVersionSpace, TabularControl,
    WeightWrittenNetwork, correct_decision, public_rule,
)


class WeightProgrammingTests(unittest.TestCase):
    def test_frozen_protocol_hash_and_nontrainable_weights(self):
        self.assertEqual(hashlib.sha256(SPEC.encode()).hexdigest(), SPEC_SHA256)
        model = WeightWrittenNetwork()
        self.assertEqual(model.LEARNED_WEIGHT_COUNT, 0)
        self.assertEqual(model.STATE_BITS, 16)
        self.assertEqual(model.STATIC_WEIGHT_COUNT, 384)
        self.assertEqual(len(model._compat), 16)
        self.assertEqual({len(row) for row in model._compat}, {16})
        self.assertEqual(model.fixed_weights_sha256(), WeightWrittenNetwork().fixed_weights_sha256())
        self.assertEqual({w for row in model._compat for w in row}, {0, 1})

    def test_all_16_worlds_and_symbolic_strong_control(self):
        scores = {"weight": 0, "symbolic": 0, "tabular": 0, "erased": 0}
        decisive = ties = 0
        for h in range(16):
            written, symbolic, tabular = WeightWrittenNetwork(), SymbolicVersionSpace(), TabularControl()
            self.assertIsNone(written.choose(3))
            for context, action in OBSERVATIONS:
                reward = public_rule(h, context, action)
                for control in (written, symbolic, tabular):
                    control.observe(context, action, reward)
            self.assertEqual(written.remaining, 1)
            target = correct_decision(h, 3)
            decisive += target is not None
            ties += target is None
            for name, guess in (
                ("weight", written.choose(3)),
                ("symbolic", symbolic.choose(3)),
                ("tabular", tabular.choose(3)),
                ("erased", WeightWrittenNetwork().choose(3)),
            ):
                scores[name] += guess == target
            self.assertEqual(written.choose(3), symbolic.choose(3))
            self.assertEqual(WeightWrittenNetwork.restore(written.snapshot()).choose(3), target)
        self.assertEqual((decisive, ties), (8, 8))
        self.assertEqual(scores, {"weight": 16, "symbolic": 16, "tabular": 8, "erased": 8})

    def test_unknown_effect_abstains_until_public_intervention(self):
        for h in range(16):
            model = WeightWrittenNetwork()
            for context, action in OBSERVATIONS[:3]:
                model.observe(context, action, public_rule(h, context, action))
            self.assertEqual(model.remaining, 2)
            self.assertIsNone(model.choose(3))

    def test_conflicting_observations_abstain_not_guess(self):
        model = WeightWrittenNetwork()
        model.observe(0, 0, 0)
        model.observe(0, 0, 1)
        self.assertEqual(model.remaining, 0)
        self.assertIsNone(model.choose(3))
        self.assertIsNone(WeightWrittenNetwork.restore(model.snapshot()).choose(3))

    def test_checkpoint_exact_cold_restore_and_replay(self):
        a = WeightWrittenNetwork()
        for c, act in OBSERVATIONS:
            a.observe(c, act, public_rule(7, c, act))
        snap = a.snapshot()
        b = WeightWrittenNetwork.restore(snap)
        self.assertEqual(len(snap), 38)
        self.assertEqual(b.snapshot(), snap)
        self.assertEqual(a.fixed_weights_sha256(), b.fixed_weights_sha256())
        for m in (a, b):
            m.observe(3, 1, public_rule(7, 3, 1))
        self.assertEqual(a.snapshot(), b.snapshot())

    def test_invalid_inputs_are_noops(self):
        model = WeightWrittenNetwork()
        original = model.snapshot()
        for args in ((True, 0, 0), (-1, 0, 0), (4, 0, 0),
                     (0, True, 0), (0, 2, 0), (0, 0, True), (0, 0, -1)):
            with self.subTest(args=args), self.assertRaises(ValueError):
                model.observe(*args)
            self.assertEqual(model.snapshot(), original)
        with self.assertRaises(ValueError):
            model.choose(True)

    def test_corruption_and_wrong_types_rejected(self):
        blob = WeightWrittenNetwork().snapshot()
        damaged = bytearray(blob)
        damaged[4] ^= 0x01
        for candidate in (bytes(damaged), blob[:-1], bytearray(blob), b"XXXX" + blob[4:]):
            with self.subTest(candidate=candidate), self.assertRaises(ValueError):
                WeightWrittenNetwork.restore(candidate)


if __name__ == "__main__":
    unittest.main()
