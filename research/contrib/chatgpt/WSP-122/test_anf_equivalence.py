"""WSP-122 no-original-source structural equivalence across synthetic laws.

The evidence in this test is fabricated by the test, not returned by an
independently controlled source. It exhaustively checks each evidence PREFIX
for a bounded set of Boolean laws; the row-space proof in README is general.
No original, reserved, first-use, or protected world is opened.
"""
from __future__ import annotations

import random
from unittest import TestCase
from unittest.mock import patch

import rule_growth as R


def _synthetic_view():
    # A contrived public algebraic view, not a scientific source world.
    subjects = tuple(range(16))
    return R.PublicWorld(122900, subjects, subjects, subjects, ())


def _truth_table_from_monomial(mask):
    return sum(int(context & mask == mask) << context
               for context in range(16))


def _synthetic_laws():
    # Every individual monomial, its complement, and deterministic mixtures.
    laws = {0, 0xFFFF}
    for mask in range(16):
        bits = _truth_table_from_monomial(mask)
        laws.add(bits)
        laws.add(bits ^ 0xFFFF)
    rng = random.Random(122920)
    for _ in range(128):
        laws.add(rng.randrange(1 << 16))
    return tuple(sorted(laws))


class StructuralANFEquivalenceTests(TestCase):
    def test_every_evidence_prefix_under_varied_boolean_laws(self):
        view = _synthetic_view()
        comparisons = 0
        cases = _synthetic_laws()
        # Two orders exercise distinct elimination pivot and evidence histories.
        with patch.object(R, "original_world",
                          side_effect=AssertionError("sealed source opened")):
            for law in cases:
                for order_id in range(2):
                    order = list(range(16))
                    if order_id:
                        random.Random(122123 ^ law).shuffle(order)
                    numeric = R.NumericRuleMemory()
                    symbolic = R.SymbolicANF()
                    for prefix, context in enumerate(order, 1):
                        # These are SYNTHETIC algebraic constraints; the digest
                        # is not a trusted-source or observation receipt.
                        label = (law >> context) & 1
                        fake = R.VerifiedObservation(
                            view.seed, context, context, label,
                            R.digest(["synthetic", law, order_id, prefix]))
                        numeric.observe(view, fake)
                        symbolic.observe(view, fake)
                        self.assertFalse(numeric.inconsistent)
                        self.assertEqual(numeric.degree, symbolic.degree)
                        self.assertEqual(len(numeric.weights), 16)
                        for test_context in range(16):
                            self.assertEqual(
                                numeric.infer_context(test_context),
                                symbolic.infer(view, test_context),
                                (law, order_id, prefix, test_context))
                            comparisons += 1
                        if prefix in (1, 4, 8, 12, 16):
                            cold = R.NumericRuleMemory.restore(
                                numeric.snapshot())
                            self.assertEqual(
                                [cold.infer_context(k) for k in range(16)],
                                [symbolic.infer(view, k) for k in range(16)])
        self.assertGreaterEqual(len(cases), 32)
        self.assertEqual(comparisons, len(cases) * 2 * 16 * 16)

    def test_preallocated_slots_and_no_unknown_primitive(self):
        numeric = R.NumericRuleMemory()
        symbolic = R.SymbolicANF()
        view = _synthetic_view()
        self.assertEqual(len(numeric.weights), 16)
        self.assertEqual(numeric.degree, 1)
        self.assertEqual(symbolic.degree, 1)
        for context in range(16):
            self.assertIsNone(numeric.infer_context(context))
            self.assertIsNone(symbolic.infer(view, context))
        self.assertEqual(tuple(sorted(R._terms(4))), tuple(range(16)))
