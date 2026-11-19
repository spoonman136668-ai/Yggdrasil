from fractions import Fraction
from pathlib import Path
import sys
import unittest


AMALGAM = Path(__file__).resolve().parents[1] / "research/contrib/chatgpt/CAUSAL-AMALGAM"
sys.path.insert(0, str(AMALGAM))
from structured_cell_prior import relation_posterior, transfer_priors
sys.path.remove(str(AMALGAM))


def receipts(context, action, outcome, count):
    return [(str(i), ((context, 0), (context, 1)), {"x1": action, "s2": outcome})
            for i in range(count)]


class StructuredCellPriorTests(unittest.TestCase):
    def test_exact_relation_weights_match_analytic_beta_integrals(self):
        self.assertEqual(relation_posterior((0, 1), (1, 0)),
                         (Fraction(2, 9), Fraction(4, 9), Fraction(1, 3)))

    def test_supported_relation_complements_shifted_peer(self):
        old = receipts(0, 0, 0, 24) + receipts(1, 1, 1, 24)
        shifted = receipts(0, 0, 1, 12)
        hard, soft, p = transfer_priors(old, shifted, (1, 1), (0, 0), Fraction(4, 5))
        self.assertEqual(hard, {(1, 1): (13, 1)})
        self.assertEqual(sum(soft[(1, 1)]), 14)
        self.assertGreater(p[1], Fraction(4, 5))

    def test_unsupported_or_ambiguous_relation_never_changes_hard_readout(self):
        old = receipts(0, 0, 0, 1) + receipts(1, 1, 1, 1)
        shifted = receipts(0, 0, 1, 12)
        hard, _, _ = transfer_priors(old, shifted, (1, 1), (0, 0), Fraction(4, 5))
        self.assertEqual(hard, {})
        self.assertEqual(transfer_priors(old, [], (1, 1), (0, 0), Fraction(4, 5)),
                         ({}, {}, None))
