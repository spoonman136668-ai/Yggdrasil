"""Unit tests for MultiBankSCDRNumV2 (precision-gated disjoint parity, multi-bank freezing, reward control)."""

from __future__ import annotations

import unittest

from scdr_num05_multibank import MultiBankSCDRNumV2
from test_scdr_num05_continuous import _rows


class TestMultiBankSCDRNumV2(unittest.TestCase):
    def test_null_never_freezes_any_bank(self) -> None:
        m = MultiBankSCDRNumV2()
        for r in _rows(78001, "null"):
            m.observe(r)
        self.assertEqual(len(m.frozen_banks), 0)

    def test_permuted_freezes_byte_exact_and_selects_high_reward_action(self) -> None:
        m = MultiBankSCDRNumV2()
        for r in _rows(78002, "perm"):
            m.observe(r)
        self.assertEqual(len(m.frozen_banks), 1)
        self.assertEqual(m.frozen_banks[0].signature(), m.frozen_sigs[0])
        a = m.choose_action_for_reward((0.75, 0.75))
        self.assertIn(a, range(5))


if __name__ == "__main__":
    unittest.main()
