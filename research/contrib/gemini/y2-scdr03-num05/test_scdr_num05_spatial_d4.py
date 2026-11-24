"""Unit tests for SpatialSymSCDRNumV3 (D4 spatial-symmetry x Sinkhorn transfer, quarantine freezing, cold replay)."""

from __future__ import annotations

import random
import sys
import unittest
from pathlib import Path

NUM05_DIR = Path(__file__).resolve().parents[2] / "chatgpt" / "CAUSAL-AMALGAM" / "NUM05"
if NUM05_DIR.exists() and str(NUM05_DIR) not in sys.path:
    sys.path.insert(0, str(NUM05_DIR))

from num05 import NumericRegimeMemory, SOURCE_TAG, digest, error, public_row, target
from scdr_num05_spatial_d4 import D4_INV, SpatialSymSCDRNumV3, apply_d4


def _law_a(sx: int, sy: int, ai: int) -> tuple[float, float, float]:
    b = (ai - 2) * 0.13
    p = 1 if ai % 2 else -1
    dx = b + 0.34 * sx + 0.11 * sy * p
    dy = -b + 0.34 * sy - 0.12 * sx * (-p)
    r = 0.45 * dx - 0.30 * dy + 0.20 * sx * sy + 0.14 * (ai % 3 - 1)
    return dx, dy, r


def _law_b(sx: int, sy: int, ai: int) -> tuple[float, float, float]:
    b = (ai - 2) * 0.13
    p = 1 if ai % 2 else -1
    dx = -0.45 * sx - b + 0.25 * sy * (-p) + 0.20 * p
    dy = -0.43 * sy + b - 0.27 * sx * (-p) - 0.10 * (ai % 3 - 1)
    r = -0.50 * dx + 0.28 * dy - 0.30 * sx * sy + 0.20 * ((ai + 1) % 3 - 1)
    return dx, dy, r


def _d4_rows(seed: int, mode: str) -> list[dict]:
    rng = random.Random(seed)
    perm = (2, 4, 0, 1, 3)
    out = []
    for i in range(400):
        a = i % 5
        q = (i // 5) % 4
        sx = 1 if q & 1 else -1
        sy = 1 if q & 2 else -1
        obs = (round(sx * (0.68 + 0.20 * rng.random()), 6), round(sy * (0.68 + 0.20 * rng.random()), 6))
        in_p2 = 160 <= i < 280
        if not in_p2 or mode == "null":
            dx, dy, r = _law_a(sx, sy, a)
        elif mode == "rot90_perm":
            ix, iy = apply_d4(D4_INV[1], obs[0], obs[1])
            dx0, dy0, r = _law_a(1 if ix >= 0 else -1, 1 if iy >= 0 else -1, perm[a])
            dx, dy = apply_d4(1, dx0, dy0)
        elif mode == "reflect_partial":
            if a < 3:
                ix, iy = apply_d4(D4_INV[7], obs[0], obs[1])
                dx0, dy0, r = _law_a(1 if ix >= 0 else -1, 1 if iy >= 0 else -1, perm[a])
                dx, dy = apply_d4(7, dx0, dy0)
            else:
                dx, dy, r = _law_b(sx, sy, a)
        elif mode == "disjoint":
            dx, dy, r = _law_b(sx, sy, a)
        else:
            raise ValueError(mode)
        dx = round(dx + rng.gauss(0, 0.02), 6)
        dy = round(dy + rng.gauss(0, 0.02), 6)
        r = round(r + rng.gauss(0, 0.02), 6)
        nobs = (round(obs[0] + dx, 6), round(obs[1] + dy, 6))
        out.append(public_row(digest(f"td4:{mode}:{seed}:{i}".encode()), obs, a, nobs, r, False, False, source_tag=SOURCE_TAG))
    return out


class TestSpatialSymSCDRNumV3(unittest.TestCase):
    def test_d4_group_inverses(self) -> None:
        pt = (0.73, -0.41)
        for g in range(8):
            x1, y1 = apply_d4(g, *pt)
            x2, y2 = apply_d4(D4_INV[g], x1, y1)
            self.assertEqual((x2, y2), pt)

    def test_null_restraint_zero_archives(self) -> None:
        m = SpatialSymSCDRNumV3()
        for r in _d4_rows(79001, "null"):
            m.observe(r)
        self.assertEqual(len(m.frozen_banks), 0)

    def test_rot90_perm_recovers_gauge_and_preserves_bank0(self) -> None:
        m = SpatialSymSCDRNumV3()
        errs = []
        gauge_at_p2 = None
        for idx, r in enumerate(_d4_rows(79002, "rot90_perm")):
            errs.append(error(m.forecast(r["observation"], r["action"]), target(r)))
            m.observe(r)
            if idx == 279:
                gauge_at_p2 = m.map_gauge()
        self.assertEqual(len(m.frozen_banks), 1)
        self.assertEqual(m.frozen_banks[0].signature(), m.frozen_sigs[0])
        self.assertEqual(gauge_at_p2, (0, "rot90"))
        self.assertLess(sum(errs[160:280]) / 120.0, 0.02)

    def test_reflect_partial_isolates_novel_actions(self) -> None:
        m = SpatialSymSCDRNumV3()
        gauge_at_p2 = None
        fam_abs = nov_abs = None
        for idx, r in enumerate(_d4_rows(79003, "reflect_partial")):
            m.observe(r)
            if idx == 279:
                gauge_at_p2 = m.map_gauge()
                fam_abs = sum(m.action_abstain_prob(a) for a in range(3)) / 3.0
                nov_abs = sum(m.action_abstain_prob(a) for a in range(3, 5)) / 2.0
        self.assertEqual(gauge_at_p2, (0, "anti_diag"))
        assert fam_abs is not None and nov_abs is not None
        self.assertLess(fam_abs, 0.15)
        self.assertGreater(nov_abs, 0.85)

    def test_disjoint_quarantine_matches_num05_phase2(self) -> None:
        rows = _d4_rows(79004, "disjoint")
        v3 = SpatialSymSCDRNumV3()
        native = NumericRegimeMemory()
        e_v3, e_nat = [], []
        for r in rows:
            obs, act, y = r["observation"], r["action"], target(r)
            e_v3.append(error(v3.forecast(obs, act), y))
            e_nat.append(error(native.forecast(obs, act), y))
            v3.observe(r)
            native.observe(r)
        self.assertAlmostEqual(sum(e_v3[160:280]) / 120.0, sum(e_nat[160:280]) / 120.0, places=6)

    def test_cold_checkpoint_restore_is_byte_exact(self) -> None:
        rows = _d4_rows(79005, "reflect_partial")
        m1 = SpatialSymSCDRNumV3()
        for r in rows[:210]:
            m1.observe(r)
        ckpt = m1.checkpoint()
        d_mid = m1.checkpoint_digest()
        m2 = SpatialSymSCDRNumV3.restore(ckpt)
        self.assertEqual(d_mid, m2.checkpoint_digest())
        for r in rows[210:]:
            self.assertEqual(m1.forecast(r["observation"], r["action"]), m2.forecast(r["observation"], r["action"]))
            m1.observe(r)
            m2.observe(r)
        self.assertEqual(m1.checkpoint_digest(), m2.checkpoint_digest())


if __name__ == "__main__":
    unittest.main()
