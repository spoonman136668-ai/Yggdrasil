"""Unit tests for SCDR-RoleCell-v4 (public boundary, null restraint, speciation, gauge compression, on-policy guard)."""

from __future__ import annotations

import random
import unittest

from scdr_rolecell import ChargedProbeGaugePolicy, SCDRRoleCell


def _synthetic_trace(seed: int, steps: int, mode: str, perm: tuple[int, int, int] = (0, 1, 2)) -> list[dict]:
    rng = random.Random(seed)
    obs = [0, 0]
    trace = []
    for _ in range(steps):
        pa = rng.randrange(3)
        ta = perm[pa]
        if mode == "null":
            nxt = [rng.randrange(2), rng.randrange(2)]
        elif mode == "flip":
            nxt = [obs[0] ^ (1 if ta == 1 else 0), obs[1] ^ (1 if ta == 2 else 0)]
        else:
            raise ValueError(mode)
        trace.append({"observation": list(obs), "action": pa, "next_observation": list(nxt)})
        obs = nxt
    return trace


class TestSCDRRoleCell(unittest.TestCase):
    def test_rejects_hidden_or_oracle_fields(self) -> None:
        cell = SCDRRoleCell()
        bad = [{"observation": [0, 0], "action": 0, "next_observation": [0, 1], "hidden": [1, 0, 1]}]
        with self.assertRaises(ValueError):
            cell.train_regime(bad)

    def test_null_restraint_zero_splits(self) -> None:
        tr = _synthetic_trace(7, 400, "null")
        cell = SCDRRoleCell()
        info = cell.train_regime(tr)
        self.assertEqual(info["splits"], 0)

    def test_gauge_deduplication_reuses_sheet(self) -> None:
        tr1 = _synthetic_trace(11, 300, "flip", perm=(0, 1, 2))
        tr2 = _synthetic_trace(12, 300, "flip", perm=(2, 0, 1))
        cell = SCDRRoleCell(use_gauge_dedup=True)
        cell.train_regime(tr1)
        info = cell.train_regime(tr2)
        self.assertEqual(info["action"], "gauge_reuse")
        self.assertEqual(len(cell.sheets), 1)

    def test_speciation_on_conflicting_regime_without_dedup(self) -> None:
        tr1 = _synthetic_trace(11, 300, "flip", perm=(0, 1, 2))
        tr2 = _synthetic_trace(12, 300, "flip", perm=(2, 0, 1))
        cell = SCDRRoleCell(use_gauge_dedup=False, use_quine_guard=True)
        cell.train_regime(tr1)
        info = cell.train_regime(tr2)
        self.assertEqual(info["action"], "speciate")
        self.assertEqual(len(cell.sheets), 2)

    def test_on_policy_budget_respected(self) -> None:
        tr1 = _synthetic_trace(19, 300, "flip", perm=(0, 1, 2))
        cell = SCDRRoleCell()
        cell.train_regime(tr1)
        pol = ChargedProbeGaugePolicy(cell, probe_penalty=0.01)
        pol.start([0, 0], paid_budget=4)
        obs = [0, 0]
        for _ in range(15):
            a = pol.choose()
            nxt = [obs[0] ^ (1 if a == 2 else 0), obs[1] ^ (1 if a == 0 else 0)]
            pol.update({"observation": obs, "action": a, "next_observation": nxt})
            obs = nxt
        self.assertLessEqual(pol.spent, 4)


if __name__ == "__main__":
    unittest.main()
