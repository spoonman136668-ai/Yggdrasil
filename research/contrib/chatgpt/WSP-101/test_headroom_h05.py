"""Frozen H05 DEV controls: source isolation, repair, cold retention, strong tie."""
from __future__ import annotations
import json
import sys
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from headroom_h05_world import (
    DEV_IDS, SOURCE_ACTIONS, REPAIR_ACTIONS, HELDOUT,
    observer, observed_basis, observed_repair, observed_passive,
    evaluator_truth_only, READOUT, NOOP
)
from headroom_h05_writer import (
    DirectRepairBank, _sparse_syndrome_decoder, _checked_repair,
    CUBIC_BYTES, QUAD_BYTES, WEIGHT_BYTES
)
from headroom_h05_symbolic import ExactSymbolicRepair
from headroom_h05_experiment import audit


class H05Tests(unittest.TestCase):
    def test_frozen_source_cardinality(self):
        self.assertEqual(DEV_IDS, tuple(range(32)))
        self.assertEqual(len(SOURCE_ACTIONS), 56)
        self.assertEqual(len(REPAIR_ACTIONS), 48)
        self.assertEqual(len(HELDOUT), 920)
        self.assertEqual(len(set(SOURCE_ACTIONS) & set(REPAIR_ACTIONS)), 0)
        self.assertEqual(len(set(HELDOUT) & (set(SOURCE_ACTIONS) | set(REPAIR_ACTIONS))), 0)

    def test_grammar_syndromes_are_unique(self):
        self.assertEqual(len(_sparse_syndrome_decoder()), 7261)

    def test_no_evaluator_imports_inside_solvers(self):
        for path in ("headroom_h05_writer.py", "headroom_h05_symbolic.py"):
            code = (HERE / path).read_text("utf-8")
            for forbidden in (
                "from headroom_h05_world", "import headroom_h05_world",
                "evaluator_truth_only", "_unknown_program", "_world_seed"
            ):
                self.assertNotIn(forbidden, code)
        source = (HERE / "headroom_h05_symbolic.py").read_text("utf-8")
        self.assertNotIn("import headroom_h05_writer", source)
        self.assertNotIn("from headroom_h05_writer", source)

    def test_public_latch_is_delayed(self):
        endpoint = observer(0)
        self.assertEqual(set(endpoint.__slots__), {"reset", "step"})
        self.assertEqual(endpoint.reset(), 0)
        self.assertEqual(endpoint.step(REPAIR_ACTIONS[0]),
                         {"observation": 0, "reward": 0})
        self.assertIn(endpoint.step(READOUT)["observation"], (0, 1))
        with self.assertRaises(ValueError):
            endpoint.step(READOUT)

    def test_no_passive_leak(self):
        a = observed_passive(0)
        self.assertEqual(a, observed_passive(1))
        self.assertTrue(all(observed_passive(w) == a for w in DEV_IDS))

    def test_protected_identifiers_denied(self):
        for val in (-1, 32, 101011, 101101, 101201, 101301, True, None):
            with self.subTest(id=val), self.assertRaises(PermissionError):
                observer(val)

    def test_wrong_public_actions_denied(self):
        endpoint = observer(1)
        for x in (-1, 1026, READOUT, True, None, 0.0):
            with self.subTest(action=x), self.assertRaises(ValueError):
                endpoint.step(x)
        endpoint.reset()
        endpoint.step(NOOP)
        with self.assertRaises(ValueError):
            endpoint.step(NOOP)

    def test_full_basis_reuses_previous_quadratic_writer(self):
        from headroom_h04_writer import program_weights, predict_weights
        for w in (0, 7, 13, 16, 22, 31):
            basis = observed_basis(w)
            q = program_weights(basis)
            self.assertEqual(len(basis), 56)
            self.assertTrue(all(predict_weights(q, x) == y for x, y in basis))

    def test_sparse_repair_updates_only_new_weights(self):
        for w in (0, 1, 2, 16, 17, 18, 31):
            bank = DirectRepairBank(1)
            bank.fit_quadratic(0, observed_basis(w))
            old = bank.base_bytes(0)
            repaired_count = bank.repair_cubic(0, observed_repair(w))
            self.assertEqual(repaired_count, w % 3)
            self.assertEqual(bank.base_bytes(0), old)
            self.assertTrue(all(bank.predict(0, x) == evaluator_truth_only(w, x)
                                for x in (0, 7, 31, 127, 511, 1023)))
            with self.assertRaises(ValueError):
                bank.repair_cubic(0, observed_repair(w))

    def test_independent_strong_symbolic_parity(self):
        for w in (0, 1, 2, 15, 16, 31):
            source, repair = observed_basis(w), observed_repair(w)
            symbolic = ExactSymbolicRepair(source, repair)
            bank = DirectRepairBank(1)
            bank.fit_quadratic(0, source)
            bank.repair_cubic(0, repair)
            for action in (7, 11, 127, 511, 1023):
                self.assertEqual(bank.predict(0, action), symbolic.predict(action))

    def test_cold_checksum_and_disjoint_slots(self):
        bank = DirectRepairBank(2)
        bank.fit_quadratic(0, observed_basis(0))
        bank.repair_cubic(0, observed_repair(0))
        first = bank.cold_image()
        bank.fit_quadratic(1, observed_basis(1))
        bank.repair_cubic(1, observed_repair(1))
        cold = DirectRepairBank.restore(first)
        for x in (7, 15, 511, 1023):
            self.assertEqual(bank.predict(0, x), cold.predict(0, x))
        self.assertEqual(bank.numeric_bytes, 2 * WEIGHT_BYTES)
        self.assertEqual(bank.checkpoint_bytes, 8 + 2 * (WEIGHT_BYTES + 1) + 32)
        damaged = bytearray(first)
        damaged[10] ^= 1
        with self.assertRaises(ValueError):
            DirectRepairBank.restore(bytes(damaged))
        with self.assertRaises(ValueError):
            DirectRepairBank.restore(first[:-1])

    def test_malformed_public_repair_fails(self):
        source = observed_repair(0)
        for bad in (source[:-1], source[1:2] + source[0:1] + source[2:],
                    tuple((action, True) for action, _ in source)):
            with self.subTest(length=len(bad)), self.assertRaises(ValueError):
                _checked_repair(bad)

    def test_unknown_tenway_effect_is_not_identifiable(self):
        self.assertIn(1023, HELDOUT)
        self.assertTrue(all(x.bit_count() <= 8 for x in REPAIR_ACTIONS))
        for w in (0, 1, 16, 31):
            self.assertTrue(all(evaluator_truth_only(w, a, unknown_tenway=True) == y
                                for a, y in observed_basis(w) + observed_repair(w)))
            self.assertNotEqual(evaluator_truth_only(w, 1023),
                                evaluator_truth_only(w, 1023, unknown_tenway=True))

    def test_replay_and_exact_synthetic_result(self):
        self.assertEqual(observed_basis(10), observed_basis(10))
        self.assertEqual(observed_repair(10), observed_repair(10))
        result = audit()
        self.assertEqual(result["classification"], "DEV_SPARSE_CUBIC_WEIGHT_REPAIR_PARITY")
        self.assertEqual(result["heldout_queries"], 29440)
        self.assertEqual(result["accuracy_counts"]["repaired"], 29440)
        self.assertEqual(result["accuracy_counts"]["symbolic"], 29440)
        self.assertTrue(result["quadratic_weights_unchanged_during_cubic_repair"])
        self.assertFalse(result["scientific_pass"])
        self.assertFalse(result["truly_unfamiliar_family_transfer_demonstrated"])
        print("WSP101_H05_DEV_RESULT=" +
              json.dumps(result, sort_keys=True, separators=(",", ":")), flush=True)


if __name__ == "__main__":
    unittest.main()
