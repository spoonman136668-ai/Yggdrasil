"""Unit tests for Cycles 20-21 (bit-exact cold-save/restore and 2-mode PO planner)."""

from __future__ import annotations

import random
import unittest

from scdr_planner_v8 import SCDRMultiStepPlannerV8
from scdr_po_planner_v9 import (
    FactorizedStallTwoModeSheet,
    POHiddenModePlannerV10,
    POHiddenModePlannerV9,
    TwoModeLatentSheet,
    cold_state_sha256,
    deserialize_planner_v8,
    deserialize_po_v10,
    serialize_po_v10,
    serialize_planner_v8,
    deserialize_po_v10,
    serialize_po_v10,
)
from scdr_sinkhorn_v6 import GeneralSheetKBit


def _step_7a(state: int, op: int) -> int:
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


class TestSCDRPOV9(unittest.TestCase):
    def test_cold_save_restore_is_bit_exact(self) -> None:
        rng = random.Random(77)
        st = 0
        tr = []
        for _ in range(400):
            a = rng.randrange(7)
            nst = _step_7a(st, a)
            tr.append({"obs_code": st, "action": a, "next_obs_code": nst})
            st = nst
        sheet = GeneralSheetKBit(3, 7)
        sheet.fit(tr)
        p1 = SCDRMultiStepPlannerV8(sheet, horizon=3, hazard=0.015)

        perm = (4, 6, 0, 5, 2, 1, 3)
        st = 0
        for _ in range(20):
            a = p1.choose_action(st, 5)
            nst = _step_7a(st, perm[a])
            p1.update(st, a, nst)
            st = nst

        raw = serialize_planner_v8(p1)
        self.assertLess(len(raw), 10000)
        p2 = deserialize_planner_v8(raw)
        self.assertEqual(cold_state_sha256(raw), cold_state_sha256(serialize_planner_v8(p2)))

        # Assert bit-exact action & belief equivalence over 30 more steps
        st1 = st2 = st
        for _ in range(30):
            a1 = p1.choose_action(st1, 5)
            a2 = p2.choose_action(st2, 5)
            self.assertEqual(a1, a2)
            nst1 = _step_7a(st1, perm[a1])
            nst2 = _step_7a(st2, perm[a2])
            p1.update(st1, a1, nst1)
            p2.update(st2, a2, nst2)
            st1, st2 = nst1, nst2
        self.assertEqual(serialize_planner_v8(p1), serialize_planner_v8(p2))

    def test_two_mode_em_fits_without_oracle_labels(self) -> None:
        rng = random.Random(88)
        st, lock = 0, 0
        tr = []
        for _ in range(600):
            a = rng.randrange(7)
            if a == 5:
                lock = 1 - lock
                nst = _step_7a(st, a)
            elif lock == 0 and a in (1, 3):
                nst = st
            else:
                nst = _step_7a(st, a)
            tr.append({"obs_code": st, "action": a, "next_obs_code": nst})
            st = nst
        po = TwoModeLatentSheet(3, 7, seed=9)
        po.fit_em(tr, iters=6)
        planner = POHiddenModePlannerV9(po, horizon=4)
        a = planner.choose_action(0, 5)
        self.assertIn(a, range(7))



    def test_po_v10_retroactive_credit_runs(self) -> None:
        rng = random.Random(91)
        st, lock = 0, 0
        tr = []
        for _ in range(600):
            a = rng.randrange(7)
            if a == 5:
                lock = 1
                nst = _step_7a(st, a)
            elif lock == 0 and a in (1, 2, 3, 6):
                nst = st
            else:
                nst = _step_7a(st, a)
            if nst == 5:
                lock = 0
            tr.append({"obs_code": st, "action": a, "next_obs_code": nst})
            st = nst
        fs = FactorizedStallTwoModeSheet(3, 7, seed=11)
        fs.fit_em(tr, iters=8)
        pl = POHiddenModePlannerV10(fs, horizon=4, hazard=0.015)
        a0 = pl.choose_action(0, 5)
        pl.update(0, a0, 0)
        a1 = pl.choose_action(0, 5)
        pl.update(0, a1, 4)
        self.assertIn(a1, range(7))


    def test_po_v10_cold_save_restore_is_bit_exact(self) -> None:
        rng = random.Random(99)
        st, lock = 0, 0
        tr = []
        for _ in range(500):
            a = rng.randrange(7)
            if a == 5:
                lock = 1
                nst = _step_7a(st, a)
            elif lock == 0 and a in (1, 2, 3, 6):
                nst = st
            else:
                nst = _step_7a(st, a)
            if nst == 5:
                lock = 0
            tr.append({"obs_code": st, "action": a, "next_obs_code": nst})
            st = nst
        fs = FactorizedStallTwoModeSheet(3, 7, seed=13)
        fs.fit_em(tr, iters=6)
        p1 = POHiddenModePlannerV10(fs, horizon=4, hazard=0.015)
        perm = (4, 6, 0, 5, 2, 1, 3)
        st = 0
        for _ in range(15):
            a = p1.choose_action(st, 5)
            nst = _step_7a(st, perm[a])
            p1.update(st, a, nst)
            st = nst
        raw = serialize_po_v10(p1)
        p2 = deserialize_po_v10(raw)
        self.assertEqual(cold_state_sha256(raw), cold_state_sha256(serialize_po_v10(p2)))
        s1 = s2 = st
        for _ in range(20):
            a1 = p1.choose_action(s1, 5)
            a2 = p2.choose_action(s2, 5)
            self.assertEqual(a1, a2)
            ns1 = _step_7a(s1, perm[a1])
            ns2 = _step_7a(s2, perm[a2])
            p1.update(s1, a1, ns1)
            p2.update(s2, a2, ns2)
            s1, s2 = ns1, ns2
        self.assertEqual(serialize_po_v10(p1), serialize_po_v10(p2))

if __name__ == "__main__":
    unittest.main()
