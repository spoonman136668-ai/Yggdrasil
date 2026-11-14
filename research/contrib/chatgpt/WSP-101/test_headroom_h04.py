"""H04 dev-only causal coefficient writing, genuine public consequence checks."""
from __future__ import annotations

import json
import sys
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from headroom_h04_world import (
    DEV_IDS, SOURCE_ACTIONS, HELDOUT_ACTIONS, observer, observed_source,
    observed_passive, evaluator_truth_only, READOUT, NOOP
)
from headroom_h04_writer import (
    program_weights, predict_weights, DirectWeightBank, WEIGHT_BYTES
)
from headroom_h04_symbolic import SymbolicPolynomial
from headroom_h04_experiment import audit

class H04Tests(unittest.TestCase):
    def test_frozen_basis_and_disjoint_targets(self):
        self.assertEqual(DEV_IDS, tuple(range(32)))
        self.assertEqual(len(SOURCE_ACTIONS), 56)
        self.assertEqual(len(HELDOUT_ACTIONS), 968)
        self.assertFalse(set(SOURCE_ACTIONS) & set(HELDOUT_ACTIONS))

    def test_public_delayed_consequence_and_source_size(self):
        endpoint = observer(0)
        self.assertEqual(set(endpoint.__slots__), {"reset", "step"})
        self.assertEqual(endpoint.reset(), 0)
        self.assertEqual(endpoint.step(SOURCE_ACTIONS[0]),
                         {"observation": 0, "reward": 0})
        self.assertIn(endpoint.step(READOUT)["observation"], (0, 1))
        with self.assertRaises(ValueError):
            endpoint.step(READOUT)
        self.assertEqual(len(observed_source(0)), 56)

    def test_passive_cannot_expose_causal_rule(self):
        expected = observed_passive(0)
        self.assertTrue(all(observed_passive(w) == expected for w in DEV_IDS))

    def test_no_original_world_ids(self):
        for bad in (-1, 32, 101011, 101101, 101201, 101301, True, None):
            with self.subTest(x=bad), self.assertRaises(PermissionError):
                observer(bad)

    def test_invalid_action_rejected(self):
        endpoint = observer(1)
        for a in (-1, 1026, True, None, "0", 1.0, READOUT):
            with self.subTest(a=a), self.assertRaises(ValueError):
                endpoint.step(a)
        endpoint.reset()
        endpoint.step(NOOP)
        with self.assertRaises(ValueError):
            endpoint.step(NOOP)

    def test_symbolic_independent_of_world_and_writer(self):
        code = (HERE / "headroom_h04_symbolic.py").read_text("utf-8")
        for name in ("from headroom_h04_world", "import headroom_h04_world",
                     "from headroom_h04_writer", "import headroom_h04_writer",
                     "_coefficients", "evaluator_truth_only"):
            self.assertNotIn(name, code)
        writer = (HERE / "headroom_h04_writer.py").read_text("utf-8")
        self.assertNotIn("from headroom_h04_world", writer)
        self.assertNotIn("import headroom_h04_world", writer)

    def test_numeric_and_symbolic_agree_with_public_events(self):
        for w in (0, 7, 15, 16, 31):
            src = observed_source(w)
            encoded = program_weights(src)
            symbolic = SymbolicPolynomial(src)
            for x in (0, 1, 3, 7, 15, 31, 127, 511, 1023):
                correct = evaluator_truth_only(w, x)
                self.assertEqual(predict_weights(encoded, x), correct)
                self.assertEqual(symbolic.predict(x), correct)

    def test_out_of_family_cubic_same_source_but_different_heldout(self):
        for w in (0, 16, 31):
            src = observed_source(w)
            self.assertTrue(all(
                evaluator_truth_only(w, x, cubic=True) == bit for x, bit in src))
            self.assertEqual(sum(
                evaluator_truth_only(w, x, cubic=True) != evaluator_truth_only(w, x)
                for x in HELDOUT_ACTIONS), 128)

    def test_strict_source_validity(self):
        src = observed_source(0)
        with self.assertRaises(ValueError):
            program_weights(src[:-1])
        with self.assertRaises(ValueError):
            program_weights(src[1:2] + src[0:1] + src[2:])
        with self.assertRaises(ValueError):
            program_weights(tuple((x, True) for x, _ in src))
        with self.assertRaises(ValueError):
            SymbolicPolynomial(src[:-1])

    def test_write_once_and_disjoint_memory(self):
        bank = DirectWeightBank(2)
        bank.write(0, observed_source(0))
        before = bank.cold_image()
        with self.assertRaises(ValueError):
            bank.write(0, observed_source(1))
        self.assertIsNone(bank.predict(1, 7))
        bank.write(1, observed_source(1))
        restored = DirectWeightBank.restore(before)
        for x in (7, 31, 1023):
            self.assertEqual(bank.predict(0, x), restored.predict(0, x))

    def test_cold_integrity_and_bytes(self):
        bank = DirectWeightBank()
        bank.write(0, observed_source(0))
        image = bank.cold_image()
        self.assertEqual(bank.numeric_bytes, 32 * WEIGHT_BYTES)
        self.assertEqual(len(image), 8 + 32 * 8 + 32)
        self.assertEqual(DirectWeightBank.restore(image).cold_image(), image)
        tampered = bytearray(image)
        tampered[11] ^= 1
        with self.assertRaises(ValueError):
            DirectWeightBank.restore(bytes(tampered))

    def test_frozen_dev_result_no_scientific_superiority(self):
        result = audit()
        self.assertEqual(result["classification"], "DEV_NATIVE_WEIGHT_PROGRAMMING_PARITY")
        self.assertFalse(result["scientific_superiority"])
        self.assertFalse(result["unfamiliar_family_transfer_demonstrated"])
        self.assertFalse(result["protected_original_worlds_used"])
        self.assertFalse(result["native_accepted_model_modified"])
        print("WSP101_H04_DEV_RESULT=" +
              json.dumps(result, sort_keys=True, separators=(",", ":")), flush=True)

if __name__ == "__main__":
    unittest.main()
