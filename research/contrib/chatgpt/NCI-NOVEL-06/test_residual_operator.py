"""Source-free NCI06 residual truth-function falsifiers; no protected worlds."""
import hashlib
import json
import math
import unittest
from itertools import product

from operator_core import OperatorBank, _programs, _predict
from residual_operator import (ExactTruthTableBayes, FIXED_MASKS,
                               ResidualComposer, _mask)


KEYS = ("public_a", "public_b", "public_c")


def bank_fixture(*, action_conditional=True):
    bank = OperatorBank()
    for name, col in ((KEYS[0], 0), (KEYS[1], 1), (KEYS[2], 2)):
        for _ in range(2):
            for code in range(64):
                bits = tuple((code >> i) & 1 for i in range(5))
                action = (code >> 5) & 1
                result = bits[col] ^ (action if col == 1 and action_conditional else 0)
                bank.observe(name, bits, action, result)
        bank.freeze(name)
    return bank


def mux(bits, action, *, action_conditional=True):
    a, b, c = bits[:3]
    if action_conditional:
        b ^= action
    return b if a else c


def target_rows(law):
    rows = []
    for i in range(160):
        code = i % 64
        bits = tuple((code >> j) & 1 for j in range(5))
        action = (code >> 5) & 1
        rows.append((bits, action, law(bits, action)))
    return rows


def fitted(bank, law):
    model = ResidualComposer(bank, KEYS)
    data = target_rows(law)
    for bits, action, outcome in data[:96]:
        model.observe(bits, action, outcome, phase="TRAIN")
    for bits, action, outcome in data[96:]:
        model.observe(bits, action, outcome, phase="VALID")
    return model


class ResidualEngineeringTests(unittest.TestCase):
    def test_fixed_programs_collapse_to_eight_distinct_functions(self):
        self.assertEqual(len(_programs()), 24)
        self.assertEqual(len({_mask(p) for p in _programs()}), 8)
        self.assertEqual(len(FIXED_MASKS), 8)
        self.assertEqual(256 - len(FIXED_MASKS), 248)

    def test_mux_is_outside_fixed_grammar_with_exact_two_mismatches(self):
        target = sum(mux((i & 1, (i >> 1) & 1, (i >> 2) & 1, 0, 0), 0,
                         action_conditional=False) << i for i in range(8))
        self.assertEqual(target, 0xd8)
        self.assertNotIn(target, FIXED_MASKS)
        self.assertEqual(min((target ^ current).bit_count() for current in FIXED_MASKS), 2)

    def test_new_unlisted_truth_operator_is_learned_from_public_outcomes(self):
        model = fitted(bank_fixture(), mux)
        self.assertTrue(model.compile())
        self.assertNotIn(model.mask, FIXED_MASKS)
        self.assertEqual(model.mask, 0xd8)
        self.assertAlmostEqual(model.predict((1, 0, 1, 0, 0), 0), .06)
        self.assertAlmostEqual(model.predict((1, 0, 1, 0, 0), 1), .94)

    def test_new_mask_cannot_be_compiled_twice(self):
        model = fitted(bank_fixture(), mux)
        self.assertTrue(model.compile())
        with self.assertRaisesRegex(ValueError, "already compiled"):
            model.compile()
        with self.assertRaisesRegex(ValueError, "frozen"):
            model.observe([0] * 5, 0, 0, phase="TRAIN")

    def test_existing_grammar_is_not_reborn_as_novel(self):
        law = lambda bits, action: (bits[0] ^ bits[1] ^ action) & bits[2]
        model = fitted(bank_fixture(), law)
        self.assertFalse(model.compile())
        self.assertIsNone(model.mask)

    def test_no_paired_action_effect_abstains(self):
        bank = bank_fixture(action_conditional=False)
        law = lambda bits, action: mux(bits, action, action_conditional=False)
        model = fitted(bank, law)
        self.assertFalse(model.compile())
        self.assertIsNone(model.predict((1, 0, 1, 0, 0), 0))

    def test_requires_full_fixed_training_and_validation(self):
        model = ResidualComposer(bank_fixture(), KEYS)
        with self.assertRaisesRegex(ValueError, "incomplete"):
            model.compile()

    def test_immutable_primitive_state_and_cold_restore(self):
        bank = bank_fixture()
        original = bank.snapshot()
        model = fitted(bank, mux)
        self.assertTrue(model.compile())
        blob = model.snapshot()
        restored = ResidualComposer.restore(OperatorBank.restore(original), blob)
        self.assertEqual(restored.snapshot(), blob)
        self.assertEqual(restored.mask, model.mask)
        self.assertEqual(bank.snapshot(), original)
        self.assertEqual(bank.read(KEYS[1], (1, 0, 0, 0, 0), 1), 1)

    def test_foreign_primitive_bank_rejected_on_cold_restore(self):
        bank = bank_fixture()
        model = fitted(bank, mux)
        self.assertTrue(model.compile())
        altered = bank_fixture(action_conditional=False)
        with self.assertRaisesRegex(ValueError, "lineage"):
            ResidualComposer.restore(altered, model.snapshot())

    def test_rehashed_false_novel_mask_rejected(self):
        bank = bank_fixture()
        model = fitted(bank, mux)
        self.assertTrue(model.compile())
        payload = json.loads(model.snapshot()[8:-32])
        payload["mask"] = 0x16
        body = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("ascii")
        fake = b"NC06" + len(body).to_bytes(4, "big") + body + hashlib.sha256(body).digest()
        with self.assertRaisesRegex(ValueError, "contradicts witnessed outcomes"):
            ResidualComposer.restore(bank, fake)

    def test_digest_corruption_rejected(self):
        model = fitted(bank_fixture(), mux)
        self.assertTrue(model.compile())
        broken = bytearray(model.snapshot())
        broken[-2] ^= 1
        with self.assertRaisesRegex(ValueError, "digest"):
            ResidualComposer.restore(model.base.bank, bytes(broken))

    def test_independent_exact_256_function_bayes_same_witnesses(self):
        bank = bank_fixture()
        model = fitted(bank, mux)
        self.assertTrue(model.compile())
        reference = ExactTruthTableBayes(bank, KEYS)
        with self.assertRaisesRegex(ValueError, "not fitted"):
            reference.predict((1, 0, 1, 0, 0), 0)
        reference.fit(model.base.train)
        self.assertEqual(len(reference.posterior), 256)
        self.assertAlmostEqual(math.fsum(reference.posterior), 1, places=13)
        for a, b, c in product((0, 1), repeat=3):
            for action in (0, 1):
                bits = (a, b, c, 0, 0)
                self.assertLess(abs(reference.predict(bits, action)
                                    - model.predict(bits, action)), 0.02)

    def test_full_exact_control_requires_all_96_observations(self):
        with self.assertRaisesRegex(ValueError, "96"):
            ExactTruthTableBayes(bank_fixture(), KEYS).fit([])

    def test_primitive_mutation_after_invention_fails_closed(self):
        bank = bank_fixture()
        model = fitted(bank, mux)
        self.assertTrue(model.compile())
        bank.observe("nonprimary", (0, 0, 0, 0, 0), 0, 0)
        with self.assertRaisesRegex(ValueError, "primitive changed"):
            model.predict((1, 0, 1, 0, 0), 0)


if __name__ == "__main__":
    unittest.main()
