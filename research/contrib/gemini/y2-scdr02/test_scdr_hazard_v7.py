"""Unit tests for SCDR-RoleCell-v7 (Changepoint Hazard Sinkhorn & Bonferroni Latch H1)."""

from __future__ import annotations

import random
import unittest

from scdr_hazard_v7 import HazardSinkhornRoleCellV7, LatchAndBonferroniH1Sheet
from scdr_sinkhorn_v6 import GeneralSheetKBit


def _synth_7a(seed: int, steps: int, amap: tuple) -> list[dict]:
    rng = random.Random(seed)
    b0, b1, b2 = 0, 0, 0
    trace = []
    for _ in range(steps):
        pa = rng.randrange(7)
        op = amap[pa]
        nb0, nb1, nb2 = b0, b1, b2
        if op == 1:
            nb0 ^= 1
        elif op == 2:
            nb1 ^= 1
        elif op == 3:
            nb2 ^= 1
        elif op == 4:
            nb0, nb1, nb2 = b1, b2, b0
        elif op == 5:
            nb0, nb1 = nb1, nb0
        elif op == 6:
            nb0, nb1, nb2 = nb0 ^ 1, nb1 ^ 1, nb2 ^ 1
        trace.append({"obs_code": (b0 << 2) | (b1 << 1) | b2, "action": pa, "next_obs_code": (nb0 << 2) | (nb1 << 1) | nb2})
        b0, b1, b2 = nb0, nb1, nb2
    return trace


class TestSCDRHazardV7(unittest.TestCase):
    def test_mid_episode_silent_shift_recovers_fast(self) -> None:
        tr = _synth_7a(10, 1500, (0, 1, 2, 3, 4, 5, 6))
        ep = _synth_7a(11, 120, (4, 6, 0, 5, 2, 1, 3)) + _synth_7a(12, 120, (1, 3, 5, 0, 6, 4, 2))
        sheet = GeneralSheetKBit(3, 7)
        sheet.fit(tr)
        res = HazardSinkhornRoleCellV7([sheet], 3, 7, hazard=0.015).score_stream(ep)
        post_tail = sum(res["losses"][160:]) / len(res["losses"][160:])
        self.assertLess(post_tail, 0.08)

    def test_bonferroni_null_restraint_zero_splits_and_latches(self) -> None:
        rng = random.Random(42)
        obs = [0, 0]
        tr = []
        for _ in range(500):
            nxt = [rng.randrange(2), rng.randrange(2)]
            tr.append({"observation": list(obs), "action": rng.randrange(3), "next_observation": list(nxt)})
            obs = nxt
        m = LatchAndBonferroniH1Sheet(max_lag=3)
        info = m.fit(tr)
        self.assertEqual(info["lag_splits"], 0)
        self.assertEqual(info["latch_fired"], 0)


if __name__ == "__main__":
    unittest.main()
