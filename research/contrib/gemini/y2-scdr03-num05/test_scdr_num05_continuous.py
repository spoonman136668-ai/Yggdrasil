"""Unit tests for SCDRNumContinuous (null restraint, byte-exact Bank 0 preservation, permuted & partial transfer)."""

from __future__ import annotations

import random
import sys
import unittest
from pathlib import Path

NUM05_DIR = Path(__file__).resolve().parents[2] / "chatgpt" / "CAUSAL-AMALGAM" / "NUM05"
if NUM05_DIR.exists() and str(NUM05_DIR) not in sys.path:
    sys.path.insert(0, str(NUM05_DIR))

from num05 import SOURCE_TAG, digest, error, public_row, target
from scdr_num05_continuous import SCDRNumContinuous


def _rows(seed: int, mode: str) -> list[dict]:
    rng = random.Random(seed)
    perm = (2, 4, 0, 1, 3)
    out = []
    for i in range(416):
        a = i % 5
        q = (i // 5) % 4
        sx = 1 if q & 1 else -1
        sy = 1 if q & 2 else -1
        obs = (round(sx * (0.68 + 0.20 * rng.random()), 6), round(sy * (0.68 + 0.20 * rng.random()), 6))
        def la(ai):
            b = (ai - 2) * 0.13
            p = 1 if ai % 2 else -1
            dx = b + 0.34 * sx + 0.11 * sy * p
            dy = -b + 0.34 * sy - 0.12 * sx * (-p)
            r = 0.45 * dx - 0.30 * dy + 0.20 * sx * sy + 0.14 * (ai % 3 - 1)
            return dx, dy, r
        def lb(ai):
            b = (ai - 2) * 0.13
            p = 1 if ai % 2 else -1
            dx = -0.45 * sx - b + 0.25 * sy * (-p) + 0.20 * p
            dy = -0.43 * sy + b - 0.27 * sx * (-p) - 0.10 * (ai % 3 - 1)
            r = -0.50 * dx + 0.28 * dy - 0.30 * sx * sy + 0.20 * ((ai + 1) % 3 - 1)
            return dx, dy, r
        if 160 <= i < 320 and mode != "null":
            dx, dy, r = la(perm[a]) if (mode == "perm" or a < 3) else lb(a)
        else:
            dx, dy, r = la(a)
        dx, dy, r = round(dx + rng.gauss(0, 0.02), 6), round(dy + rng.gauss(0, 0.02), 6), round(r + rng.gauss(0, 0.02), 6)
        nobs = (round(obs[0] + dx, 6), round(obs[1] + dy, 6))
        out.append(public_row(digest(f"t:{mode}:{seed}:{i}".encode()), obs, a, nobs, r, False, False, source_tag=SOURCE_TAG))
    return out


class TestSCDRNumContinuous(unittest.TestCase):
    def test_null_never_archives(self) -> None:
        m = SCDRNumContinuous()
        for row in _rows(77001, "null"):
            m.observe(row)
        self.assertFalse(m.archived)

    def test_permuted_archives_preserves_bank0_and_transfers(self) -> None:
        m = SCDRNumContinuous()
        errs = []
        for row in _rows(77002, "perm"):
            errs.append(error(m.forecast(row["observation"], row["action"]), target(row)))
            m.observe(row)
        self.assertTrue(m.archived)
        self.assertEqual(m.bank0.signature(), m.bank0_frozen_signature)
        self.assertLess(sum(errs[160:240]) / 80.0, 0.025)
        self.assertLess(sum(errs[352:416]) / 64.0, 0.01)

    def test_partial_selectively_abstains_on_novel_actions(self) -> None:
        m = SCDRNumContinuous()
        abstain_b = None
        for idx, row in enumerate(_rows(77003, "partial")):
            m.observe(row)
            if idx == 319:
                abstain_b = [b[5] for b in m.beliefs]
        self.assertIsNotNone(abstain_b)
        assert abstain_b is not None
        self.assertLess(sum(abstain_b[:3]) / 3.0, 0.05)
        self.assertGreater(sum(abstain_b[3:]) / 2.0, 0.90)



    def test_checkpoint_restore_is_byte_exact(self) -> None:
        rows = _rows(77004, "partial")
        m1 = SCDRNumContinuous()
        for row in rows[:210]:
            m1.observe(row)
        ckpt = m1.checkpoint()
        d_before = m1.checkpoint_digest()
        m2 = SCDRNumContinuous.restore(ckpt)
        self.assertEqual(d_before, m2.checkpoint_digest())
        for row in rows[210:]:
            p1 = m1.forecast(row["observation"], row["action"])
            p2 = m2.forecast(row["observation"], row["action"])
            self.assertEqual(p1, p2)
            m1.observe(row)
            m2.observe(row)
        self.assertEqual(m1.checkpoint_digest(), m2.checkpoint_digest())

if __name__ == "__main__":
    unittest.main()
