"""Public DEV qualification only. No scientific first-use or acceptance."""
import hashlib
import math
import unittest

from weight_written import (
    SPEC, SPEC_SHA256, OBSERVATIONS, TRANSFER_CONTEXTS,
    WeightWrittenNetwork, SymbolicControl, TabularControl,
    ConventionalMLPControl, oracle_choice, public_rule,
)


class WSP02Tests(unittest.TestCase):
    def test_compiled_spec_capacity_and_frozen_weights(self):
        self.assertEqual(hashlib.sha256(SPEC.encode()).hexdigest(), SPEC_SHA256)
        a = WeightWrittenNetwork()
        self.assertEqual(a.STATIC_WEIGHT_COUNT, 3072)
        self.assertEqual(a.TRAINABLE_WEIGHTS, 0)
        self.assertEqual(a.STATE_BITS, 64)
        self.assertEqual(a.CHECKPOINT_BYTES, 44)
        self.assertEqual(len(a._compat), 64)
        self.assertEqual({len(row) for row in a._compat}, {32})
        self.assertEqual(len(a._votes), 8)
        self.assertEqual({len(arms) for arms in a._votes}, {2})
        self.assertEqual({len(row) for arms in a._votes for row in arms}, {64})
        self.assertEqual({x for row in a._compat for x in row}, {0, 1})
        self.assertEqual(a.static_weight_hash(), WeightWrittenNetwork().static_weight_hash())
        self.assertEqual(ConventionalMLPControl.TRAINABLE_WEIGHTS, 65)
        self.assertEqual(ConventionalMLPControl.STEPS, 512)

    def test_all_64_causal_worlds_and_all_four_transfer_contexts(self):
        counts = dict(weight=0, symbolic=0, tabular=0, erased=0)
        decisive = ties = 0
        static_hash = WeightWrittenNetwork().static_weight_hash()
        for h in range(64):
            net, sym, tab = WeightWrittenNetwork(), SymbolicControl(), TabularControl()
            for c, action in OBSERVATIONS:
                reward = public_rule(h, c, action)
                for model in (net, sym, tab):
                    model.observe(c, action, reward)
            self.assertEqual(net.remaining, 1)
            self.assertEqual(sym.remaining, 1)
            self.assertEqual(net.static_weight_hash(), static_hash)
            for c in TRANSFER_CONTEXTS:
                expected = oracle_choice(h, c)
                decisive += expected is not None
                ties += expected is None
                guesses = dict(weight=net.choose(c), symbolic=sym.choose(c),
                               tabular=tab.choose(c), erased=WeightWrittenNetwork().choose(c))
                for key, value in guesses.items():
                    counts[key] += value == expected
                self.assertEqual(net.choose(c), sym.choose(c))
                for action in (0, 1):
                    self.assertEqual(net.predict_outcome(c, action), public_rule(h, c, action))
            self.assertEqual(WeightWrittenNetwork.restore(net.snapshot()).snapshot(), net.snapshot())
        self.assertEqual((decisive, ties), (128, 128))
        self.assertEqual(counts, dict(weight=256, symbolic=256, tabular=128, erased=128))

    def test_ood_reward_failure_preserves_pre_witness_action_choice(self):
        # WSP-02 diagnostic correction after original CI failed: XOR both binary
        # rewards flips action preference for 64 decisive cases. The red first
        # qualification is preserved; this asserts the negative, not success.
        wrong_rewards = wrong_decisive = 0
        for h in range(64):
            net = WeightWrittenNetwork()
            sym = SymbolicControl()
            for c, action in OBSERVATIONS:
                reward = public_rule(h, c, action, ood=True)
                net.observe(c, action, reward)
                sym.observe(c, action, reward)
            self.assertEqual(net.remaining, 1)
            for c in TRANSFER_CONTEXTS:
                true_action = oracle_choice(h, c, ood=True)
                self.assertEqual(net.choose(c), sym.choose(c))
                if net.choose(c) is not None and net.choose(c) != true_action:
                    wrong_decisive += 1
                for action in (0, 1):
                    wrong_rewards += net.predict_outcome(c, action) != public_rule(h, c, action, ood=True)
            self.assertNotEqual(net.predict_outcome(3, 0), public_rule(h, 3, 0, ood=True))
            # One genuinely observed contradiction, not hidden evaluator labels.
            net.observe(3, 0, public_rule(h, 3, 0, ood=True))
            sym.observe(3, 0, public_rule(h, 3, 0, ood=True))
            self.assertEqual(net.remaining, 0)
            self.assertEqual(sym.remaining, 0)
            for c in TRANSFER_CONTEXTS:
                self.assertIsNone(net.choose(c))
                self.assertIsNone(net.predict_outcome(c, 0))
        self.assertEqual(wrong_rewards, 256)
        self.assertEqual(wrong_decisive, 64)

    def test_absent_evidence_and_sham_contradiction(self):
        net = WeightWrittenNetwork()
        self.assertEqual(net.remaining, 64)
        self.assertIsNone(net.choose(7))
        net.observe(0, 0, 0)
        self.assertEqual(net.remaining, 32)
        net.observe(0, 0, 1)
        self.assertEqual(net.remaining, 0)
        self.assertIsNone(net.choose(3))

    def test_cold_restore_identical_subsequent_updates(self):
        net = WeightWrittenNetwork()
        for c, a in OBSERVATIONS:
            net.observe(c, a, public_rule(37, c, a))
        raw = net.snapshot()
        twin = WeightWrittenNetwork.restore(raw)
        self.assertEqual(len(raw), 44)
        self.assertEqual(twin.snapshot(), raw)
        self.assertEqual(twin.static_weight_hash(), net.static_weight_hash())
        for model in (twin, net):
            model.observe(3, 0, public_rule(37, 3, 0))
        self.assertEqual(net.snapshot(), twin.snapshot())

    def test_corrupted_checkpoint_rejected_and_no_mutation(self):
        net = WeightWrittenNetwork()
        raw = net.snapshot()
        edited = bytearray(raw)
        edited[10] ^= 1
        for candidate in (raw[:-1], bytes(edited), bytearray(raw), b"NOPE" + raw[4:]):
            with self.subTest(candidate_type=type(candidate)), self.assertRaises(ValueError):
                WeightWrittenNetwork.restore(candidate)
        self.assertEqual(net.snapshot(), raw)

    def test_invalid_public_observation_fails_closed(self):
        net = WeightWrittenNetwork()
        initial = net.snapshot()
        cases = ((True, 0, 0), (-1, 0, 0), (8, 0, 0),
                 (0, True, 0), (0, 2, 0), (0, 0, True), (0, 0, 2))
        for args in cases:
            with self.subTest(args=args), self.assertRaises(ValueError):
                net.observe(*args)
            self.assertEqual(net.snapshot(), initial)
        with self.assertRaises(ValueError):
            net.choose(True)
        with self.assertRaises(ValueError):
            net.predict_outcome(0, True)

    def test_frozen_conventional_control_trains_on_only_six_public_experiences(self):
        correct = 0
        losses = []
        for h in range(64):
            experiences = tuple((c, action, public_rule(h, c, action))
                                for c, action in OBSERVATIONS)
            model = ConventionalMLPControl()
            model.fit(experiences)
            self.assertTrue(math.isfinite(model.fit_loss))
            self.assertEqual(model.STEPS, 512)
            losses.append(model.fit_loss)
            for c in TRANSFER_CONTEXTS:
                correct += model.choose(c) == oracle_choice(h, c)
        self.assertGreaterEqual(correct, 0)
        self.assertLessEqual(correct, 128)  # always chooses; ties count wrong
        self.assertEqual(len(losses), 64)
        same = tuple((c, a, public_rule(0, c, a)) for c, a in OBSERVATIONS)
        p = ConventionalMLPControl()
        q = ConventionalMLPControl()
        p.fit(same)
        q.fit(same)
        self.assertEqual(p.fit_loss, q.fit_loss)
        self.assertEqual(p.w, q.w)


if __name__ == "__main__":
    unittest.main()
