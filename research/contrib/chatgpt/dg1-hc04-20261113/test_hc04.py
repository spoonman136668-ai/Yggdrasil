"""HC04 finite-source developer tests; no protected scientific first use."""
import json
import unittest

from model import (
    CHECKPOINT_LIMIT, FULL_MASK, ConventionalConstraintControl,
    VersionedCausalCells, hypothesis_effect, require_state, require_action,
)
from eval_dev import PhysicalWorld, one_seed


class VersionSpaceTests(unittest.TestCase):
    def test_ambiguity_requires_abstention_until_discriminating_evidence(self):
        candidate = VersionedCausalCells()
        # Action 0 on state 0: two mechanisms fit with different own slopes.
        candidate.observe(0, 0, 0)
        self.assertEqual(candidate.predict(0, 0), 0)
        self.assertIsNone(candidate.predict(1, 0))
        self.assertIsNotNone(candidate.predict_ungated(1, 0))
        # A second public intervention at an own=1 state determines slope.
        candidate.observe(1, 0, 1)
        self.assertEqual(candidate.predict(1, 0), 1)
        self.assertEqual(candidate.predict(0, 0), 0)

    def test_two_banks_reactivate_after_observed_reversal(self):
        cells = VersionedCausalCells()
        cells.observe(0, 0, 0)  # A
        cells.observe(0, 0, 1)  # contradictory B, new bank
        self.assertEqual(cells.splits, 1)
        self.assertEqual(len(cells.banks), 2)
        cells.observe(0, 0, 0)  # A returns, no label provided
        self.assertEqual(cells.active, 0)
        self.assertEqual(cells.reactivations, 1)
        self.assertEqual(cells.predict(0, 0), 0)

    def test_same_charged_ledger_conventional_equivalence(self):
        for seed, family in [(22101, "parity"), (22105, "own_bit"),
                             (22109, "and")]:
            result = one_seed(seed, family)
            self.assertEqual(result["candidate"],
                             result["conventional_equivalent"])
            self.assertEqual(sum(result["candidate"][field] for field
                                 in ("correct", "wrong_confident", "abstained")), 64)
            self.assertTrue(result["cold_parity"])

    def test_own_bit_physics_can_be_learned_with_public_transition(self):
        world = PhysicalWorld(22105, "own_bit")
        model = VersionedCausalCells()
        action = 2
        for state in (0, 4):
            model.observe(state, action, world.step(state, action, 0))
        self.assertEqual(model.predict(9, action), world.step(9, action, 0))
        self.assertEqual(model.predict(13, action), world.step(13, action, 0))

    def test_invalid_public_delta_is_atomic(self):
        m = VersionedCausalCells()
        original = m.snapshot()
        for args in [(0, 0, 2), (-1, 0, 0), (0, 4, 0),
                     (True, 0, 0), (0, True, 0), (0, 0, 16)]:
            with self.subTest(args=args):
                with self.assertRaises(ValueError):
                    m.observe(*args)
                self.assertEqual(m.snapshot(), original)
        with self.assertRaises(TypeError):
            m.observe(0, 0, 0, hidden_regime="A")

    def test_capacity_and_full_bank_fail_closed(self):
        m = VersionedCausalCells()
        m.observe(0, 0, 0)
        m.observe(0, 0, 1)
        self.assertEqual(len(m.banks), 2)
        self.assertEqual(m.logical_hypothesis_bits, 32)
        self.assertLessEqual(len(m.snapshot()), CHECKPOINT_LIMIT)
        self.assertEqual(m.updates, 2)

    def test_checkpoint_restore_canonical_with_tamper_rejection(self):
        m = VersionedCausalCells()
        m.observe(0, 0, 0)
        m.observe(0, 0, 1)
        m.observe(0, 0, 0)
        raw = m.snapshot()
        self.assertEqual(VersionedCausalCells.restore(raw).snapshot(), raw)
        edited = bytearray(raw)
        edited[35] ^= 1
        for payload in (bytes(edited), raw[:-1], b"{}", bytearray(raw),
                        b"x" * (CHECKPOINT_LIMIT + 1)):
            with self.subTest(length=len(payload),typ=type(payload)):
                with self.assertRaises(ValueError):
                    VersionedCausalCells.restore(payload)
        forged = json.loads(raw)
        forged["payload"]["banks"][0][0] = 0
        with self.assertRaises(ValueError):
            VersionedCausalCells.restore(json.dumps(forged).encode())

    def test_strict_parameter_and_boolean_validation(self):
        for bad in (0, 3, True, 1.0, "2"):
            with self.subTest(limit=bad):
                with self.assertRaises(ValueError):
                    VersionedCausalCells(bank_limit=bad)
        for bad in (2, 0.0, 0, None):
            if type(bad) is bool or bad in (True, False):
                continue
            with self.subTest(reactivate=bad):
                with self.assertRaises(ValueError):
                    VersionedCausalCells(reactivate=bad)
        for bad in (-1, 16, True, None):
            with self.assertRaises(ValueError):
                require_state(bad)
        for bad in (-1, 4, True, None):
            with self.assertRaises(ValueError):
                require_action(bad)
        for bad in (-1, 4, True):
            with self.assertRaises(ValueError):
                hypothesis_effect(0, 0, bad)


if __name__ == "__main__":
    unittest.main()
