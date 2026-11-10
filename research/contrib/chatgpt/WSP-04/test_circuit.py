"""WSP-04 public DEV qualification. No independent scientific first-use."""
import hashlib
import math
import pathlib
import unittest
from circuit import (
    N_INPUTS, BASE, FOURTH, PAIRS, SEEDS, MODES, HELDOUT, REPLAY,
    WeightCell, WeightWrittenCircuit, ExactSymbolicANF, TrainedMLPControl,
    baseline_observations, public_reward, true_choice,
)
ROOT = pathlib.Path(__file__).resolve().parent
PROTOCOL_GIT_BLOB = "3ce5d3598179b33f61183704405c64df2e9c90e3"


class WSP04Tests(unittest.TestCase):
    def test_precommitted_frozen_protocol_and_budgets(self):
        blob = (ROOT / "protocol.json").read_bytes().replace(b"\r\n", b"\n")
        git_blob = b"blob " + str(len(blob)).encode() + b"\0" + blob
        self.assertEqual(hashlib.sha1(git_blob).hexdigest(), PROTOCOL_GIT_BLOB)
        self.assertEqual((N_INPUTS, len(BASE), len(FOURTH), len(PAIRS)), (5, 26, 5, 5))
        self.assertEqual((SEEDS, MODES, HELDOUT), (tuple(range(8)), (0, 1, 2), 31))
        self.assertEqual(WeightWrittenCircuit.GRADIENT_STEPS, 0)
        self.assertEqual(TrainedMLPControl.PARAMETERS, 97)
        self.assertEqual(TrainedMLPControl.STEPS, 256)

    def test_gates_are_explicit_five_input_binary_threshold_weights(self):
        for mask in range(32):
            cell = WeightCell(mask)
            self.assertEqual(cell.weights, tuple((mask >> bit) & 1 for bit in range(5)))
            self.assertEqual(cell.threshold, mask.bit_count())
            for context in range(32):
                self.assertEqual(cell.fires(context), (context & mask) == mask)

    def test_120_worlds_independent_symbolic_parity_and_two_stage_errors(self):
        observations = new_fourth_gates = restored = replayed = 0
        prewrong = middlewrong = 0
        for seed in SEEDS:
            for pair in PAIRS:
                for mode in MODES:
                    model, symbolic = WeightWrittenCircuit(), ExactSymbolicANF()
                    for c, a, y in baseline_observations(seed, pair, mode):
                        model.observe(c, a, y)
                        symbolic.observe(c, a, y)
                    correct = true_choice(seed, pair, mode, HELDOUT)
                    before = model.choose(HELDOUT)
                    self.assertEqual(before, symbolic.choose(HELDOUT))
                    self.assertEqual(before != correct, mode == 1)
                    prewrong += before != correct

                    witness1 = public_reward(seed, pair, mode, pair[0], 1)
                    model.observe(pair[0], 1, witness1)
                    symbolic.observe(pair[0], 1, witness1)
                    interim = model.choose(HELDOUT)
                    self.assertEqual(interim, symbolic.choose(HELDOUT))
                    self.assertEqual(interim != correct, mode == 2)
                    middlewrong += interim != correct

                    witness2 = public_reward(seed, pair, mode, pair[1], 1)
                    model.observe(pair[1], 1, witness2)
                    symbolic.observe(pair[1], 1, witness2)
                    self.assertEqual(model.choose(HELDOUT), correct)
                    self.assertEqual(symbolic.choose(HELDOUT), correct)
                    for a in (0, 1):
                        expected = public_reward(seed, pair, mode, HELDOUT, a)
                        self.assertEqual(model.predict_reward(HELDOUT, a), expected)
                        self.assertEqual(symbolic.predict_reward(HELDOUT, a), expected)
                    self.assertEqual(model.degree_four_gates, mode)
                    self.assertEqual(model.gate_count <= 64, True)
                    new_fourth_gates += model.degree_four_gates
                    save = model.snapshot()
                    clone = WeightWrittenCircuit.restore(save)
                    self.assertEqual(clone.compiled_weights_sha256(),
                                     model.compiled_weights_sha256())
                    self.assertEqual(clone.snapshot(), save)
                    restored += 1
                    for c, a in REPLAY:
                        clone.observe(c, a, public_reward(seed, pair, mode, c, a))
                    self.assertEqual(clone.snapshot(), save)
                    replayed += 1
                    observations += 1
        self.assertEqual((observations, prewrong, middlewrong, new_fourth_gates,
                          restored, replayed), (120, 40, 40, 120, 120, 120))

    def test_fifth_order_negative_is_unidentifiable_and_fails_closed(self):
        false_policy = incorrect_confident = denied_fifth = 0
        for seed in SEEDS:
            for pair in PAIRS:
                for mode in MODES:
                    model = WeightWrittenCircuit()
                    for event in baseline_observations(seed, pair, mode):
                        model.observe(*event)
                    for mask in pair:
                        model.observe(mask, 1, public_reward(seed, pair, mode, mask, 1))
                    wrong_true = true_choice(seed, pair, mode, HELDOUT,
                                             fifth_negative=True)
                    guess = model.choose(HELDOUT)
                    self.assertNotEqual(guess, wrong_true)
                    false_policy += 1
                    incorrect_confident += guess is not None
                    self.assertNotIn(HELDOUT, model.gates[1])
                    model.observe(HELDOUT, 1,
                                  public_reward(seed, pair, mode, HELDOUT, 1,
                                                fifth_negative=True))
                    self.assertTrue(model.unsafe)
                    self.assertIsNone(model.choose(HELDOUT))
                    self.assertIsNone(model.predict_reward(HELDOUT, 1))
                    self.assertNotIn(HELDOUT, model.gates[1])
                    self.assertTrue(WeightWrittenCircuit.restore(model.snapshot()).unsafe)
                    denied_fifth += 1
        self.assertEqual((false_policy, denied_fifth), (120, 120))
        self.assertGreater(incorrect_confident, 0)
        self.assertLess(incorrect_confident, 120)  # some pre-witness ties

    def test_no_growth_does_not_learn_fourth_order_gate(self):
        for mode in MODES:
            seed, pair = 7, (15, 23)
            model = WeightWrittenCircuit(max_degree=3)
            for event in baseline_observations(seed, pair, mode):
                model.observe(*event)
            for mask in pair:
                model.observe(mask, 1, public_reward(seed, pair, mode, mask, 1))
            self.assertEqual(model.degree_four_gates, 0)
            if mode:
                self.assertTrue(model.unsafe)
                self.assertIsNone(model.choose(HELDOUT))
            else:
                self.assertFalse(model.unsafe)
                self.assertEqual(model.choose(HELDOUT),
                                 true_choice(seed, pair, mode, HELDOUT))

    def test_public_evidence_dependency_prevents_unsupported_gate_invention(self):
        model = WeightWrittenCircuit()
        self.assertIsNone(model.choose(31))
        with self.assertRaises(ValueError):
            model.observe(15, 1, 0)
        self.assertEqual(model.gate_count, 0)
        self.assertEqual(len(model.events), 0)
        model.observe(0, 0, 1)
        self.assertIsNone(model.choose(31))

    def test_checkpoint_tamper_and_noncanonical_rejection(self):
        model = WeightWrittenCircuit()
        for event in baseline_observations(0, (15, 23), 1):
            model.observe(*event)
        raw = model.snapshot()
        tamper = bytearray(raw)
        tamper[8] ^= 1
        for candidate in (bytes(tamper), raw[:-1], bytearray(raw),
                          b"NOPE" + raw[4:]):
            with self.subTest(type=type(candidate)), self.assertRaises(ValueError):
                WeightWrittenCircuit.restore(candidate)

    def test_observed_repeated_conflict_fails_closed(self):
        m = WeightWrittenCircuit()
        m.observe(0, 0, 1)
        m.observe(0, 0, 0)
        self.assertTrue(m.unsafe)
        self.assertIsNone(m.choose(0))
        self.assertTrue(WeightWrittenCircuit.restore(m.snapshot()).unsafe)

    def test_invalid_inputs_are_noops(self):
        m = WeightWrittenCircuit()
        old = m.snapshot()
        for args in ((True, 0, 0), (-1, 0, 0), (32, 0, 0),
                     (0, True, 0), (0, 2, 0), (0, 0, True), (0, 0, -1)):
            with self.subTest(args=args), self.assertRaises(ValueError):
                m.observe(*args)
            self.assertEqual(m.snapshot(), old)
        with self.assertRaises(ValueError):
            WeightWrittenCircuit(max_degree=6)
        with self.assertRaises(ValueError):
            m.predict_reward(31, True)

    def test_frozen_trained_control_only_receives_public_observations(self):
        seed, pair, mode = 5, (27, 30), 2
        examples = baseline_observations(seed, pair, mode) + tuple(
            (mask, 1, public_reward(seed, pair, mode, mask, 1)) for mask in pair)
        a, b = TrainedMLPControl(), TrainedMLPControl()
        a.fit(examples, pair)
        b.fit(examples, pair)
        self.assertTrue(math.isfinite(a.loss))
        self.assertEqual(a.loss, b.loss)
        self.assertEqual(a.w, b.w)
        self.assertEqual(a.choose(HELDOUT), b.choose(HELDOUT))
        with self.assertRaises(ValueError):
            TrainedMLPControl().fit(examples[:-1], pair)


if __name__ == "__main__":
    unittest.main()
