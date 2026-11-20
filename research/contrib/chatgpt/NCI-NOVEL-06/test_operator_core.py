"""Pure, non-scored engineering unit fixtures for NCI06; zero first-use worlds."""
import math
import json
import hashlib
import unittest

from operator_core import (
    CausalComposer, ExactCompositionBayes, OperatorBank,
    _context, _programs, _wire,
)


def toy_bank():
    bank = OperatorBank()
    for name, col in (("fixture_a", 0), ("fixture_b", 1), ("fixture_c", 2)):
        for _ in range(2):
            for code in range(64):
                bits = tuple((code >> i) & 1 for i in range(5))
                bank.observe(name, bits, (code >> 5) & 1, bits[col])
        bank.freeze(name)
    return bank


def toy_rows(law):
    rows = []
    for i in range(160):
        code = i % 64
        bits = tuple((code >> j) & 1 for j in range(5))
        action = (code >> 5) & 1
        rows.append((bits, action, law(bits, action)))
    return rows


def filled_composer(bank, law):
    c = CausalComposer(bank, ("fixture_a", "fixture_b", "fixture_c"))
    for bits, action, result in toy_rows(law)[:96]:
        c.observe(bits, action, result, phase="TRAIN")
    for bits, action, result in toy_rows(law)[96:]:
        c.observe(bits, action, result, phase="VALID")
    return c


class OperatorCoreTests(unittest.TestCase):
    def test_context_strict_binary_five_bits(self):
        for state, action in (([0] * 4, 0), ([0] * 5, 2),
                              ([0] * 4 + [True], 0), ([0] * 5, True)):
            with self.subTest(state=state, action=action):
                with self.assertRaises(ValueError):
                    _context(state, action)
        self.assertEqual(_context([1, 0, 1, 0, 1], 1)[2], 53)

    def test_program_enumeration_is_fixed(self):
        self.assertEqual(len(_programs()), 24)
        self.assertEqual(len(set(_programs())), 24)
        self.assertEqual(_wire("xor_and", 1, 0, 1), 1)
        with self.assertRaises(ValueError):
            _wire("secret-oracle", 1, 1, 1)

    def test_sparse_public_evidence_abstains(self):
        bank = OperatorBank()
        bank.observe("fixture_a", [0] * 5, 0, 1)
        with self.assertRaisesRegex(ValueError, "exactly 128"):
            bank.freeze("fixture_a")
        with self.assertRaisesRegex(ValueError, "not trained"):
            bank.read("fixture_a", [0] * 5, 0)

    def test_frozen_primitives_are_learned_from_public_witnesses(self):
        bank = toy_bank()
        for i in range(64):
            bits = tuple((i >> j) & 1 for j in range(5))
            action = (i >> 5) & 1
            for name, j in (("fixture_a", 0), ("fixture_b", 1), ("fixture_c", 2)):
                self.assertEqual(bank.read(name, bits, action), bits[j])
        with self.assertRaisesRegex(ValueError, "immutable"):
            bank.observe("fixture_a", [0] * 5, 0, 0)

    def test_frozen_operator_checkpoint_roundtrips_cold(self):
        old = toy_bank()
        raw = old.snapshot()
        self.assertEqual(OperatorBank.restore(raw).snapshot(), raw)
        self.assertEqual(OperatorBank.restore(raw).read("fixture_c", (1, 1, 0, 0, 1), 1), 0)

    def test_checkpoint_corruption_rejected(self):
        x = bytearray(toy_bank().snapshot())
        x[16] ^= 1
        with self.assertRaisesRegex(ValueError, "digest"):
            OperatorBank.restore(bytes(x))
        with self.assertRaises(ValueError):
            OperatorBank.restore(b"NC06not-a-checkpoint")

    def test_primitive_world_limit_and_public_keys(self):
        bank = OperatorBank()
        for i in range(12):
            bank.observe("toy" + str(i), [0] * 5, 0, 0)
        with self.assertRaisesRegex(ValueError, "world limit"):
            bank.observe("thirteenth", [0] * 5, 0, 1)
        with self.assertRaisesRegex(ValueError, "public world key"):
            bank.observe("bad/world", [0] * 5, 0, 0)

    def test_target_valid_requires_complete_train(self):
        bank = toy_bank()
        candidate = CausalComposer(bank, ("fixture_a", "fixture_b", "fixture_c"))
        with self.assertRaisesRegex(ValueError, "precede"):
            candidate.observe([0] * 5, 0, 0, phase="VALID")
        with self.assertRaisesRegex(ValueError, "incomplete"):
            candidate.compile()

    def test_adaptation_binds_three_learned_operators(self):
        bank = toy_bank()
        law = lambda bits, action: (bits[0] ^ bits[1]) & bits[2]
        candidate = filled_composer(bank, law)
        self.assertTrue(candidate.compile())
        self.assertIsNotNone(candidate.binding)
        self.assertAlmostEqual(candidate.predict((1, 0, 1, 0, 0), 0), .94)
        self.assertAlmostEqual(candidate.predict((1, 1, 1, 0, 0), 0), .06)

    def test_no_new_relationship_yields_no_birth(self):
        bank = toy_bank()
        candidate = filled_composer(bank, lambda bits, action: bits[0])
        self.assertFalse(candidate.compile())
        self.assertIsNone(candidate.binding)

    def test_no_more_observations_after_binding(self):
        candidate = filled_composer(toy_bank(), lambda bits, act: (bits[0] ^ bits[1]) & bits[2])
        self.assertTrue(candidate.compile())
        with self.assertRaisesRegex(ValueError, "finished"):
            candidate.observe([0] * 5, 0, 0, phase="TRAIN")

    def test_unchanged_primitive_memory_after_composition(self):
        bank = toy_bank()
        before = bank.snapshot()
        candidate = filled_composer(bank, lambda bits, act: (bits[0] ^ bits[1]) & bits[2])
        candidate.compile()
        self.assertEqual(bank.snapshot(), before)
        self.assertEqual(bank.read("fixture_a", (1, 0, 1, 0, 0), 0), 1)

    def test_composition_cold_restore_and_lineage(self):
        bank = toy_bank()
        candidate = filled_composer(bank, lambda bits, act: (bits[0] ^ bits[1]) & bits[2])
        self.assertTrue(candidate.compile())
        state = candidate.snapshot()
        resumed = CausalComposer.restore(OperatorBank.restore(bank.snapshot()), state)
        self.assertEqual(resumed.snapshot(), state)
        self.assertEqual(resumed.predict((1, 1, 1, 0, 0), 1), candidate.predict((1, 1, 1, 0, 0), 1))
        other = OperatorBank.restore(bank.snapshot())
        other.observe("fourth", [0] * 5, 0, 0)
        with self.assertRaisesRegex(ValueError, "lineage"):
            CausalComposer.restore(other, state)

    def test_unmatched_primitive_state_prevents_compilation(self):
        bank = toy_bank()
        candidate = filled_composer(bank, lambda bits, act: (bits[0] ^ bits[1]) & bits[2])
        bank.observe("fourth", [0] * 5, 0, 0)
        with self.assertRaisesRegex(ValueError, "changed"):
            candidate.compile()

    def test_equal_evidence_fully_fitted_exact_bayes_reference(self):
        bank = toy_bank()
        rows = toy_rows(lambda bits, act: (bits[0] ^ bits[1]) & bits[2])
        control = ExactCompositionBayes(bank, ("fixture_a", "fixture_b", "fixture_c"))
        with self.assertRaisesRegex(ValueError, "not fitted"):
            control.predict([0] * 5, 0)
        control.fit(rows[:96])
        self.assertEqual(len(control.posterior), 24)
        self.assertAlmostEqual(math.fsum(control.posterior), 1, places=13)
        self.assertGreater(control.predict((1, 0, 1, 0, 0), 0), 0.75)
        self.assertLess(control.predict((1, 1, 1, 0, 0), 0), 0.25)

    def test_rehashed_forged_binding_rejected_against_witnesses(self):
        bank = toy_bank()
        candidate = filled_composer(bank, lambda bits, act: (bits[0] ^ bits[1]) & bits[2])
        self.assertTrue(candidate.compile())
        raw = candidate.snapshot()
        record = json.loads(raw[8:-32])
        record["binding"] = ["xor3", [0, 1, 2]]
        fake = json.dumps(record, sort_keys=True, separators=(",", ":")).encode("ascii")
        rehashed = b"NC06" + len(fake).to_bytes(4, "big") + fake + hashlib.sha256(fake).digest()
        with self.assertRaisesRegex(ValueError, "contradicts public evidence"):
            CausalComposer.restore(bank, rehashed)

    def test_frozen_primitive_refuses_retraining_after_restore(self):
        bank = OperatorBank.restore(toy_bank().snapshot())
        with self.assertRaisesRegex(ValueError, "immutable"):
            bank.observe("fixture_b", [0] * 5, 0, 1)

    def test_train_and_valid_capacity_is_bounded(self):
        bank = toy_bank()
        c = filled_composer(bank, lambda bits, act: bits[0])
        with self.assertRaisesRegex(ValueError, "budget"):
            c.observe([0] * 5, 0, 0, phase="VALID")

    def test_identical_action_observations_do_not_claim_paired_interventions(self):
        bank = toy_bank()
        candidate = CausalComposer(bank, ("fixture_a", "fixture_b", "fixture_c"))
        for i in range(96):
            bits = tuple((i >> j) & 1 for j in range(5))
            candidate.observe(bits, 0, (bits[0] ^ bits[1]) & bits[2], phase="TRAIN")
        for i in range(64):
            bits = tuple((i >> j) & 1 for j in range(5))
            candidate.observe(bits, 0, (bits[0] ^ bits[1]) & bits[2], phase="VALID")
        self.assertFalse(candidate.compile())


if __name__ == "__main__":
    unittest.main()
