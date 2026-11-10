"""WSP-03 public DEV controls; synthetic tests are not scientific first-use."""
import hashlib
import math
import pathlib
import unittest
from weight_circuit import (
    PROTOCOL_SHA256, BASIS, TRIPLES, SEEDS, TRANSFER,
    DirectWeightCircuit, ExactSymbolicANF, TrainedMLPControl, AndCell,
    world_reward, true_choice, samples,
)

ROOT = pathlib.Path(__file__).resolve().parent


class WSP03Tests(unittest.TestCase):
    def test_frozen_protocol_and_preregistered_capacity(self):
        self.assertEqual(hashlib.sha256((ROOT / "protocol.txt").read_bytes()).hexdigest(),
                         PROTOCOL_SHA256)
        self.assertEqual(BASIS, (0, 1, 2, 4, 8, 3, 5, 6, 9, 10, 12))
        self.assertEqual((SEEDS, TRIPLES, TRANSFER), (tuple(range(16)), (7, 11, 13, 14), 15))
        self.assertEqual(DirectWeightCircuit.GRADIENT_STEPS, 0)
        self.assertEqual(DirectWeightCircuit.MAX_GATES_PER_ACTION, 15)
        self.assertEqual(TrainedMLPControl.PARAMS, 71)
        self.assertEqual(TrainedMLPControl.STEPS, 512)

    def test_gate_is_actual_binary_connection_program(self):
        for mask in BASIS + TRIPLES:
            gate = AndCell.compile(mask)
            self.assertEqual(gate.weights, tuple((mask >> bit) & 1 for bit in range(4)))
            self.assertEqual(gate.threshold, mask.bit_count())
            for context in range(16):
                self.assertEqual(gate.fires(context), (context & mask) == mask)
        with self.assertRaises(ValueError):
            AndCell.compile(15)

    def test_all_public_worlds_before_and_after_one_novel_witness(self):
        total = pre_novel_wrong = new_gates = cold = 0
        for seed in SEEDS:
            for triple in TRIPLES:
                for novelty in (0, 1):
                    net = DirectWeightCircuit()
                    symbolic = ExactSymbolicANF()
                    no_growth = DirectWeightCircuit(max_degree=2)
                    for c, a, reward in samples(seed, triple, novelty):
                        for control in (net, symbolic, no_growth):
                            control.observe(c, a, reward)
                    expected = true_choice(seed, triple, novelty, TRANSFER)
                    pre = net.choose(TRANSFER)
                    if novelty:
                        self.assertNotEqual(pre, expected)
                        pre_novel_wrong += 1
                    else:
                        self.assertEqual(pre, expected)
                    self.assertEqual(net.choose(TRANSFER), symbolic.choose(TRANSFER))
                    witnessed = world_reward(seed, triple, novelty, triple, 1)
                    for control in (net, symbolic, no_growth):
                        control.observe(triple, 1, witnessed)
                    self.assertEqual(net.new_triple_gates, novelty)
                    self.assertEqual(net.choose(TRANSFER), expected)
                    self.assertEqual(symbolic.choose(TRANSFER), expected)
                    for a in (0, 1):
                        self.assertEqual(net.predict_reward(TRANSFER, a),
                                         world_reward(seed, triple, novelty, TRANSFER, a))
                        self.assertEqual(net.predict_reward(TRANSFER, a),
                                         symbolic.predict_reward(TRANSFER, a))
                    if novelty:
                        self.assertTrue(no_growth.unsafe)
                        self.assertIsNone(no_growth.choose(TRANSFER))
                    else:
                        self.assertEqual(no_growth.choose(TRANSFER), expected)
                    snap = net.snapshot()
                    restored = DirectWeightCircuit.restore(snap)
                    self.assertEqual(restored.snapshot(), snap)
                    self.assertEqual(restored.weights_sha256(), net.weights_sha256())
                    total += 1
                    new_gates += net.new_triple_gates
                    cold += int(restored.choose(TRANSFER) == expected)
        self.assertEqual((total, pre_novel_wrong, new_gates, cold),
                         (128, 64, 64, 128))

    def test_no_evidence_cannot_make_confident_predictions(self):
        model = DirectWeightCircuit()
        self.assertIsNone(model.predict_reward(15, 0))
        self.assertIsNone(model.choose(15))
        model.observe(0, 0, 0)
        self.assertIsNone(model.choose(15))
        with self.assertRaises(ValueError):
            DirectWeightCircuit().observe(15, 0, 0)

    def test_exact_cold_retention_with_interleaved_observation_replay(self):
        for seed in (0, 7, 15):
            net = DirectWeightCircuit()
            for c, a, reward in samples(seed, 7, 1):
                net.observe(c, a, reward)
            net.observe(7, 1, world_reward(seed, 7, 1, 7, 1))
            old = net.snapshot()
            restored = DirectWeightCircuit.restore(old)
            for c, a in ((0, 0), (1, 0), (4, 1), (12, 1)):
                restored.observe(c, a, world_reward(seed, 7, 1, c, a))
            self.assertEqual(restored.snapshot(), old)
            self.assertEqual(restored.choose(15), true_choice(seed, 7, 1, 15))

    def test_fourth_order_negative_remains_unlearned_and_abstains_after_witness(self):
        failures = abstentions = 0
        for seed in SEEDS:
            for triple in TRIPLES:
                model = DirectWeightCircuit()
                for c, a, r in samples(seed, triple, 1):
                    model.observe(c, a, r)
                model.observe(triple, 1, world_reward(seed, triple, 1, triple, 1))
                self.assertNotEqual(model.choose(15),
                                    true_choice(seed, triple, 1, 15, fourth_order=True))
                failures += 1
                model.observe(15, 1, world_reward(seed, triple, 1, 15, 1,
                                                 fourth_order=True))
                self.assertTrue(model.unsafe)
                self.assertIsNone(model.choose(15))
                self.assertIsNone(model.predict_reward(15, 1))
                self.assertEqual(DirectWeightCircuit.restore(model.snapshot()).snapshot(),
                                 model.snapshot())
                abstentions += 1
        self.assertEqual((failures, abstentions), (64, 64))

    def test_contradiction_and_corrupted_checkpoint_fail_closed(self):
        m = DirectWeightCircuit()
        before = m.snapshot()
        m.observe(0, 0, 1)
        m.observe(0, 0, 0)
        self.assertTrue(m.unsafe)
        self.assertIsNone(m.choose(0))
        self.assertTrue(DirectWeightCircuit.restore(m.snapshot()).unsafe)
        self.assertNotEqual(before, m.snapshot())
        raw = m.snapshot()
        corrupted = bytearray(raw)
        corrupted[15] ^= 1
        for item in (raw[:-1], bytes(corrupted), bytearray(raw), b"MISS" + raw[4:]):
            with self.subTest(item_type=type(item)), self.assertRaises(ValueError):
                DirectWeightCircuit.restore(item)

    def test_invalid_inputs_do_not_modify_state(self):
        m = DirectWeightCircuit()
        original = m.snapshot()
        for args in ((True, 0, 0), (-1, 0, 0), (16, 0, 0),
                     (0, True, 0), (0, 2, 0), (0, 0, True), (0, 0, 2)):
            with self.subTest(args=args), self.assertRaises(ValueError):
                m.observe(*args)
            self.assertEqual(m.snapshot(), original)
        with self.assertRaises(ValueError):
            m.predict_reward(15, True)
        with self.assertRaises(ValueError):
            DirectWeightCircuit(max_degree=4)

    def test_fixed_budget_trained_control_is_reproducible(self):
        for seed, triple, novelty in ((0, 7, 1), (15, 14, 0)):
            obs = samples(seed, triple, novelty) + (
                (triple, 1, world_reward(seed, triple, novelty, triple, 1)),)
            a, b = TrainedMLPControl(), TrainedMLPControl()
            a.fit(obs, triple)
            b.fit(obs, triple)
            self.assertTrue(math.isfinite(a.fit_loss))
            self.assertEqual(a.fit_loss, b.fit_loss)
            self.assertEqual(a.w, b.w)
            self.assertEqual(a.choose(TRANSFER), b.choose(TRANSFER))
            with self.assertRaises(ValueError):
                TrainedMLPControl().fit(obs[:-1], triple)


if __name__ == "__main__":
    unittest.main()
