"""Unit tests for SCDR-RoleCell-v6 (Sinkhorn soft-exclusion, obs symmetries, public boundary, 7-action scaling)."""

from __future__ import annotations

import random
import unittest

from scdr_sinkhorn_v6 import (
    OBS_SYMMETRIES,
    FreshOnlineKBit,
    GeneralSheetKBit,
    SinkhornRoleCellV6,
    apply_obs_sym,
    invert_obs_sym,
    multichannel_brier_nbits,
    sinkhorn_sub_stochastic,
)


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
        elif op == "reset":
            nb0, nb1, nb2 = 0, 0, 0
        elif op == "set":
            nb0, nb1, nb2 = 1, 1, 1
        trace.append({"obs_code": (b0 << 2) | (b1 << 1) | b2, "action": pa, "next_obs_code": (nb0 << 2) | (nb1 << 1) | nb2})
        b0, b1, b2 = nb0, nb1, nb2
    return trace


class TestSCDRSinkhornV6(unittest.TestCase):
    def test_obs_sym_roundtrip(self) -> None:
        for sym in OBS_SYMMETRIES:
            for o in range(4):
                self.assertEqual(invert_obs_sym(apply_obs_sym(o, sym), sym), o)

    def test_sinkhorn_suppresses_claimed_role_and_preserves_fresh(self) -> None:
        # Row 0 locked on role 0; Row 1 undecided; Row 2 is novel (fresh=0.95)
        raw = [
            [0.95, 0.02, 0.02, 0.01],
            [0.33, 0.33, 0.33, 0.01],
            [0.02, 0.02, 0.01, 0.95],
        ]
        out = sinkhorn_sub_stochastic(raw, 3, iters=3)
        # Row 1's weight on role 0 must drop below roles 1 and 2
        self.assertLess(out[1][0], out[1][1])
        # Novel action's fresh column must remain untouched
        self.assertAlmostEqual(out[2][3], 0.95, places=6)

    def test_rejects_hidden_fields(self) -> None:
        sheet = GeneralSheetKBit(2, 3)
        with self.assertRaises(ValueError):
            sheet.fit([{"observation": [0, 0], "action": 0, "next_observation": [0, 1], "oracle": 1}])

    def test_7action_partial_selective_abstention_beats_fresh(self) -> None:
        tr = _synth_7a(31, 1200, (0, 1, 2, 3, 4, 5, 6))
        ev = _synth_7a(32, 120, (5, 2, 6, 1, 4, "reset", "set"))
        sheet = GeneralSheetKBit(3, 7)
        sheet.fit(tr)
        res = SinkhornRoleCellV6([sheet], 3, 7, use_sinkhorn=True).score_stream(ev)

        fr = FreshOnlineKBit(3, 7)
        floss = []
        for e in ev:
            floss.append(multichannel_brier_nbits(fr.predict(e["obs_code"], e["action"]), e["next_obs_code"], 3))
            fr.update(e["obs_code"], e["action"], e["next_obs_code"])
        fresh_60 = sum(floss[:60]) / 60.0

        self.assertLess(res["brier_60"], fresh_60 - 0.05)
        self.assertLess(sum(res["abstain_per_action"][:5]) / 5.0, 0.05)
        self.assertGreater(sum(res["abstain_per_action"][5:]) / 2.0, 0.90)


if __name__ == "__main__":
    unittest.main()
