from fractions import Fraction
from pathlib import Path
import sys
import unittest


AMALGAM = Path(__file__).resolve().parents[1] / "research/contrib/chatgpt/CAUSAL-AMALGAM"
sys.path.insert(0, str(AMALGAM))
from local_evidence_readout import EvidenceReadout
sys.path.remove(str(AMALGAM))


def old(_view, _first, *terminal):
    return Fraction(1, 2) if terminal else Fraction(1, 4)


def updated(_view, _first, *terminal):
    return Fraction(1, 2) if terminal else Fraction(3, 4)


class LocalEvidenceReadoutTests(unittest.TestCase):
    def test_only_local_weights_keep_the_unchanged_cell_at_its_anchor(self):
        local = EvidenceReadout(old, updated, local=True)
        shared = EvidenceReadout(old, updated, local=False)
        for readout in (local, shared):
            self.assertEqual(readout.forecast((1, 0), 1), Fraction(1, 4))
            readout.observe((1, 0), 1, 1, 0, 1)
            self.assertEqual(readout.forecast((1, 1), 1), Fraction(5, 8))
        self.assertEqual(local.forecast((1, 0), 0), Fraction(1, 4))
        self.assertEqual(shared.forecast((1, 0), 0), Fraction(5, 8))

    def test_invalid_terminal_readout_cannot_partially_update_transition(self):
        def invalid_terminal(view, first, *terminal):
            return 2 if terminal else updated(view, first)
        local = EvidenceReadout(old, invalid_terminal, local=True)
        with self.assertRaises(ValueError):
            local.observe((1, 0), 1, 1, 0, 1)
        self.assertEqual(local.forecast((1, 0), 1), Fraction(1, 4))

    def test_jointly_unsupported_outcome_falls_back_to_old_forecast(self):
        def impossible(_view, _first, *_terminal):
            return 0
        local = EvidenceReadout(impossible, impossible, local=True)
        local.observe((1, 0), 1, 1, 0, 1)
        self.assertEqual(local.forecast((1, 0), 1), 0)

    def test_new_public_evidence_can_restore_the_original_regime(self):
        local = EvidenceReadout(old, updated, local=True)
        for _ in range(8):
            local.observe((1, 0), 1, 1, 0, 0)
        self.assertGreater(local.forecast((1, 0), 1), Fraction(7, 10))
        for _ in range(8):
            local.observe((1, 0), 1, 0, 0, 0)
        self.assertLess(local.forecast((1, 0), 1), Fraction(3, 10))

    def test_replaying_public_receipts_recovers_forecasts(self):
        prefix = [((1, 0), 1, 1, 0, 0), ((0, 1), 0, 0, 1, 1)]
        a = EvidenceReadout(old, updated, local=True)
        b = EvidenceReadout(old, updated, local=True)
        for receipt in prefix:
            a.observe(*receipt)
        for receipt in prefix:
            b.observe(*receipt)
        self.assertEqual(a.forecast((0, 0), 0), b.forecast((0, 0), 0))
        self.assertEqual(a.forecast((1, 1), 1), b.forecast((1, 1), 1))
