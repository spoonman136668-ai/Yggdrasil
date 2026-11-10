"""WSP-05 public synthetic DEV; frozen first-use and negatives."""
import hashlib
import math
import pathlib
import unittest
from causal_signature import (
    SEEDS, STATE_IDS, PublicWorld, BinarySignatureGate,
    DirectSignatureCircuit, ExactSymbolicSignature, OneStepControl,
    IdentityControl, TrainedMLPControl,
)

ROOT = pathlib.Path(__file__).resolve().parent
PROTOCOL_BLOB = "03041e58ed19782e06dd949037c83fcd07425840"


class WSP05Tests(unittest.TestCase):
    def test_frozen_protocol_and_trainable_control_capacity(self):
        payload = (ROOT / "protocol.json").read_bytes().replace(b"\r\n", b"\n")
        git_blob = b"blob " + str(len(payload)).encode() + b"\0" + payload
        self.assertEqual(hashlib.sha1(git_blob).hexdigest(), PROTOCOL_BLOB)
        self.assertEqual(SEEDS, tuple(range(32)))
        self.assertEqual(DirectSignatureCircuit.GRADIENT_STEPS, 0)
        self.assertEqual(DirectSignatureCircuit.MAX_DETECTORS, 4)
        self.assertEqual(TrainedMLPControl.PARAMS, 33)
        self.assertEqual(TrainedMLPControl.MAX_STEPS, 2048)
        self.assertEqual(TrainedMLPControl.STOP_LOSS, 0.02)

    def test_four_binary_detector_input_weights_are_compiled_not_pretrained(self):
        for b0 in (0, 1):
            for b1 in (0, 1):
                for label in (0, 1):
                    gate = BinarySignatureGate.from_observation((b0, b1), label)
                    self.assertEqual(gate.weights, (1-b0, b0, 1-b1, b1))
                    self.assertEqual(gate.threshold, 2)
                    for x in (0, 1):
                        for y in (0, 1):
                            self.assertEqual(gate.fires((x, y)), (x, y) == (b0, b1))

    def test_worlds_are_opaque_with_complete_public_causal_data_budget(self):
        all_ids = set(STATE_IDS)
        first = []
        for seed in SEEDS:
            env = PublicWorld(seed)
            obs = env.public_experiences()
            self.assertEqual(len(obs), 20)
            self.assertEqual(set(x[0] for x in obs[:12]), all_ids)
            self.assertEqual(set(x[0] for x in obs[12:]), set(env.train))
            self.assertTrue(set(env.train).isdisjoint(env.test))
            self.assertEqual(len(env.test), 4)
            self.assertEqual({x[1] for x in obs[:12]}, {0})
            self.assertEqual({x[1] for x in obs[12:]}, {1})
            self.assertEqual({v for x in obs for v in (x[0],x[3])}, all_ids)
            first.append(env.public_experiences())
        self.assertNotEqual(first[0], first[1])

    def test_32_worlds_128_unseen_reward_transfers_and_control_parity(self):
        total = confidence = controls_id = symbolic = learned_gates = 0
        for seed in SEEDS:
            env = PublicWorld(seed)
            model = DirectSignatureCircuit()
            exact = ExactSymbolicSignature()
            identity = IdentityControl()
            one = OneStepControl()
            for e in env.public_experiences():
                for control in (model, exact, identity, one):
                    control.observe(*e)
            self.assertEqual(len(model.gates), 4)
            self.assertEqual(model.learned_connections, 16)
            learned_gates += len(model.gates)
            self.assertFalse(model.unsafe)
            for s in env.test:
                correct = env.outcome(s, 1)[2]
                self.assertEqual(model.predict_a1(s), correct)
                self.assertEqual(exact.predict_a1(s), correct)
                self.assertIsNone(identity.predict_a1(s))
                total += model.predict_a1(s) == correct
                symbolic += exact.predict_a1(s) == correct
                controls_id += identity.predict_a1(s) == correct
                confidence += model.predict_a1(s) is not None
        self.assertEqual((total, symbolic, controls_id, learned_gates, confidence),
                         (128, 128, 0, 128, 128))

    def test_one_step_signature_ablation_is_strictly_worse(self):
        n_correct = n_abstained = 0
        for seed in SEEDS:
            w = PublicWorld(seed)
            control = OneStepControl()
            for e in w.public_experiences():
                control.observe(*e)
            for s in w.test:
                pred = control.predict_a1(s)
                n_abstained += pred is None
                n_correct += pred == w.outcome(s, 1)[2]
        self.assertEqual((n_correct, n_abstained), (64, 64))

    def test_cold_restore_interference_isolation_and_replay(self):
        for seed in SEEDS:
            w = PublicWorld(seed)
            model = DirectSignatureCircuit()
            events = w.public_experiences()
            for e in events:
                model.observe(*e)
            checkpoint = model.snapshot()
            restored = DirectSignatureCircuit.restore(checkpoint)
            self.assertEqual(restored.snapshot(), checkpoint)
            self.assertEqual(restored.programmed_sha256(), model.programmed_sha256())
            before = tuple(restored.predict_a1(s) for s in w.test)
            for e in (events[0], events[11], events[12], events[-1]):
                restored.observe(*e)
            self.assertEqual(restored.snapshot(), checkpoint)
            self.assertEqual(tuple(restored.predict_a1(s) for s in w.test), before)
            # Independent world reuses opaque identifiers but not model state.
            other = PublicWorld((seed + 1) % len(SEEDS))
            separate = DirectSignatureCircuit()
            for e in other.public_experiences():
                separate.observe(*e)
            self.assertEqual(model.snapshot(), checkpoint)
            self.assertEqual(restored.snapshot(), checkpoint)
            self.assertEqual(len(separate.gates), 4)

    def test_unobservable_shift_causes_confident_errors_until_public_witness(self):
        misses = abstentions = 0
        for seed in SEEDS:
            w = PublicWorld(seed)
            model = DirectSignatureCircuit()
            for e in w.public_experiences():
                model.observe(*e)
            for s in w.test:
                p = model.predict_a1(s)
                actual = w.outcome(s, 1, heldout_shift=True)[2]
                self.assertIsNotNone(p)
                self.assertNotEqual(p, actual)
                misses += 1
            # First genuine OOD action1 observation. It contradicts one
            # existing two-bit causal equivalence class; do not generalize
            # the shift to all unseen classes without evidence.
            witness = w.outcome(w.test[0], 1, heldout_shift=True)
            model.observe(*witness)
            self.assertTrue(model.unsafe)
            self.assertEqual(len(model.gates), 4)
            for s in w.test:
                self.assertIsNone(model.predict_a1(s))
                abstentions += 1
            self.assertTrue(DirectSignatureCircuit.restore(model.snapshot()).unsafe)
        self.assertEqual((misses, abstentions), (128, 128))

    def test_missing_causal_consequence_and_invalid_inputs_fail_without_mutation(self):
        model = DirectSignatureCircuit()
        before = model.snapshot()
        with self.assertRaises(ValueError):
            model.observe(1000, 1, 1, 1001)
        self.assertEqual(model.snapshot(), before)
        for event in ((True, 0, 0, 1000), (999, 0, 0, 1000),
                      (1000, 2, 0, 1000), (1000, 0, True, 1000),
                      (1000, 0, 0, 2000)):
            with self.assertRaises(ValueError):
                model.observe(*event)
            self.assertEqual(model.snapshot(), before)
        self.assertIsNone(model.predict_a1(1000))

    def test_checkpoint_corruption_and_repeated_contradictory_source(self):
        w = PublicWorld(0)
        m = DirectSignatureCircuit()
        for e in w.public_experiences():
            m.observe(*e)
        raw = m.snapshot()
        edited = bytearray(raw)
        edited[16] ^= 1
        for blob in (raw[:-1], bytes(edited), bytearray(raw),
                     b"XXXX" + raw[4:]):
            with self.subTest(type=type(blob)), self.assertRaises(ValueError):
                DirectSignatureCircuit.restore(blob)
        e = w.public_experiences()[0]
        m.observe(e[0], e[1], e[2] ^ 1, e[3])
        self.assertTrue(m.unsafe)
        self.assertEqual(DirectSignatureCircuit.restore(m.snapshot()).snapshot(),
                         m.snapshot())

    def test_trained_control_data_budget_and_determinism(self):
        env = PublicWorld(5)
        exact = ExactSymbolicSignature()
        samples = []
        for e in env.public_experiences():
            exact.observe(*e)
            if e[1] == 1:
                samples.append((exact.signature(e[0]), e[2]))
        pairs = tuple(samples)
        a, b = TrainedMLPControl(), TrainedMLPControl()
        a.fit(pairs)
        b.fit(pairs)
        self.assertTrue(math.isfinite(a.loss))
        self.assertEqual(a.steps, b.steps)
        self.assertEqual(a.loss, b.loss)
        self.assertEqual(a.w, b.w)
        self.assertLessEqual(a.steps, a.MAX_STEPS)
        self.assertEqual(a.converged, a.loss <= a.STOP_LOSS)
        with self.assertRaises(ValueError):
            TrainedMLPControl().fit(pairs[:-1])


if __name__ == "__main__":
    unittest.main()
