"""WSP-11 frozen deterministic public DEV controls."""
import unittest
from partial_affine import (BASIS, HOLDOUT, GRADIENT_STEPS,
                            PartialAffineCircuit, affine_truth, bits,
                            observed_only_crossbar, symbolic_gf2)


def witness_set(code):
    return tuple((bits(i), affine_truth(code, i)) for i in BASIS)


class PartialAffineTests(unittest.TestCase):
    def test_all_affine_functions_and_symbolic_baseline(self):
        numeric = symbolic = 0
        for code in range(16):
            obs = witness_set(code)
            circuit = PartialAffineCircuit(obs)
            for index in HOLDOUT:
                numeric += circuit.predict(bits(index)) == affine_truth(code, index)
                symbolic += symbolic_gf2(obs, bits(index)) == affine_truth(code, index)
        self.assertEqual((numeric, symbolic), (64, 64))

    def test_information_matched_observed_only_control(self):
        total = 0
        for code in range(16):
            c = observed_only_crossbar(witness_set(code))
            for i in HOLDOUT:
                total += c.evaluate(bits(i)) == affine_truth(code, i)
        self.assertEqual(total, 32)

    def test_hidden_interaction_is_undetectable_before_witness(self):
        errors = 0
        for code in range(16):
            c = PartialAffineCircuit(witness_set(code))
            for i in HOLDOUT:
                perturbed = affine_truth(code, i) ^ (((i & 1) != 0) and ((i & 2) != 0))
                errors += c.predict(bits(i)) != int(perturbed)
        self.assertEqual(errors, 32)

    def test_outside_family_witness_faults_and_abstains(self):
        for code in range(16):
            c = PartialAffineCircuit(witness_set(code))
            i = 3
            self.assertFalse(c.observe_verification(bits(i), 1 ^ affine_truth(code, i)))
            self.assertIsNone(c.predict(bits(5)))
            with self.assertRaisesRegex(ValueError, "WSP11_FAULTED_SNAPSHOT"):
                c.snapshot()

    def test_weight_restore_all_worlds_and_zero_gradients(self):
        for code in range(16):
            c = PartialAffineCircuit(witness_set(code))
            old = c.circuit.programmed_sha256()
            raw = c.snapshot()
            r = PartialAffineCircuit.restore(raw)
            self.assertEqual(r.snapshot(), raw)
            self.assertEqual(old, r.circuit.programmed_sha256())
            self.assertEqual(len(r.circuit.weights), 56)
            for i in HOLDOUT:
                self.assertEqual(r.predict(bits(i)), c.predict(bits(i)))
            self.assertEqual(old, c.circuit.programmed_sha256())
        self.assertEqual(GRADIENT_STEPS, 0)

    def test_invalid_input_rejected_without_side_effect(self):
        for obs in ([], (), ((bits(0), 0),)*4,
                    tuple((bits(i), True) for i in BASIS),
                    tuple((bits(i), 0) for i in (0, 1, 2, 3))):
            with self.assertRaises(ValueError):
                PartialAffineCircuit(obs)
        c = PartialAffineCircuit(witness_set(3))
        start = c.circuit.programmed_sha256()
        for x in ((1, 0), (True, 0, 0), [1, 0, 0]):
            with self.assertRaises(ValueError):
                c.predict(x)
        with self.assertRaises(ValueError):
            c.observe_verification(bits(0), True)
        self.assertEqual(c.circuit.programmed_sha256(), start)

    def test_checkpoint_integrity_and_dimension(self):
        c = PartialAffineCircuit(witness_set(15))
        raw = c.snapshot()
        with self.assertRaises(ValueError):
            PartialAffineCircuit.restore(raw[:-1] + bytes([raw[-1] ^ 1]))
        from crossbar import DirectCrossbar
        with self.assertRaisesRegex(ValueError, "WSP11_INVALID_CHECKPOINT_DIMENSION"):
            PartialAffineCircuit.restore(DirectCrossbar.from_spec(2, 3).snapshot())


if __name__ == "__main__":
    unittest.main()
