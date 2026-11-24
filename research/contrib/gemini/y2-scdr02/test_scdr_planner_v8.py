"""Unit tests for SCDRMultiStepPlannerV8 (multi-step goal reaching in permuted 7-action world)."""

from __future__ import annotations

import random
import unittest

from scdr_planner_v8 import SCDRMultiStepPlannerV8
from scdr_sinkhorn_v6 import GeneralSheetKBit


def _step_7a(state: int, op: int | str) -> int:
    b0, b1, b2 = (state >> 2) & 1, (state >> 1) & 1, state & 1
    if op == 1:
        b0 ^= 1
    elif op == 2:
        b1 ^= 1
    elif op == 3:
        b2 ^= 1
    elif op == 4:
        b0, b1, b2 = b1, b2, b0
    elif op == 5:
        b0, b1 = b1, b0
    elif op == 6:
        b0, b1, b2 = b0 ^ 1, b1 ^ 1, b2 ^ 1
    return (b0 << 2) | (b1 << 1) | b2


class TestSCDRPlannerV8(unittest.TestCase):
    def test_multistep_vi3_solves_2step_goal_in_permuted_7action_world(self) -> None:
        rng = random.Random(55)
        st = 0
        tr = []
        for _ in range(1500):
            a = rng.randrange(7)
            nst = _step_7a(st, a)
            tr.append({"obs_code": st, "action": a, "next_obs_code": nst})
            st = nst
        sheet = GeneralSheetKBit(3, 7)
        sheet.fit(tr)

        planner = SCDRMultiStepPlannerV8(sheet, horizon=3, hazard=0.015)
        perm = (4, 6, 0, 5, 2, 1, 3)
        st = 0  # 000 -> goal 101 (5) requires >=2 steps!
        hits = 0
        for _ in range(60):
            a = planner.choose_action(st, goal_code=5)
            nst = _step_7a(st, perm[a])
            planner.update(st, a, nst)
            if nst == 5:
                hits += 1
                st = 0
            else:
                st = nst
        self.assertGreaterEqual(hits, 15)


if __name__ == "__main__":
    unittest.main()
