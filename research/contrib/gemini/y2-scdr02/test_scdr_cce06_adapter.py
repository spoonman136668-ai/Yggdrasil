"""Unit tests for SCDRCCE06PolicyAdapter (y2-cce06 _episode, multi-sheet switching, goal-directed control)."""

from __future__ import annotations

import random
import sys
import unittest
from pathlib import Path

CCE06_DIR = Path(__file__).resolve().parents[2] / "chatgpt" / "y2-cce06"
sys.path.insert(0, str(CCE06_DIR))

import calibration_policy_frontier as cpf
from scdr_cce06_adapter import SCDRCCE06PolicyAdapter


class _ToyEnv:
    def __init__(self, seed: int, perm: tuple[int, int, int] = (2, 0, 1)):
        self.rng = random.Random(seed)
        self.perm = perm
        self.obs = [0, 0]

    def reset(self) -> list[int]:
        return list(self.obs)

    def step(self, action: int) -> list[int]:
        ta = self.perm[action]
        nxt = [self.obs[0] ^ (1 if ta == 1 else 0), self.obs[1] ^ (1 if ta == 2 else 0)]
        self.obs = nxt
        return list(nxt)


def _make_trace(seed: int, steps: int, perm: tuple[int, int, int]) -> list[dict]:
    env = _ToyEnv(seed, perm)
    rng = random.Random(seed + 100)
    out = []
    obs = env.reset()
    for _ in range(steps):
        a = rng.randrange(3)
        nxt = env.step(a)
        out.append({"observation": obs[:], "action": a, "next_observation": nxt[:]})
        obs = nxt
    return out


class TestSCDRCCE06Adapter(unittest.TestCase):
    def test_runs_directly_inside_y2_cce06_episode_evaluator(self) -> None:
        train = [_make_trace(1, 200, (0, 1, 2))]
        terminal = [_make_trace(2, 80, (2, 0, 1))]
        pol = SCDRCCE06PolicyAdapter(hazard=0.015, probe_penalty=0.012).fit(train)
        env = _ToyEnv(3, (2, 0, 1))
        rec = cpf._episode(pol, env, steps=30, budget=8, terminal=terminal)
        self.assertLessEqual(rec["paid_actions"], 8)
        self.assertEqual(len(rec["actions"]), 30)
        self.assertLess(rec["terminal_brier"], 0.05)

    def test_pending_action_cannot_be_replayed(self) -> None:
        train = [_make_trace(4, 100, (0, 1, 2))]
        pol = SCDRCCE06PolicyAdapter().fit(train)
        pol.start([0, 0], paid_budget=4)
        _ = pol.choose()
        with self.assertRaises(ValueError):
            pol.choose()

    def test_goal_directed_control_reaches_target_in_permuted_world(self) -> None:
        train = [_make_trace(10, 200, (0, 1, 2))]
        pol = SCDRCCE06PolicyAdapter(hazard=0.015).fit(train)
        env = _ToyEnv(11, (2, 0, 1))
        obs = env.reset()
        pol.start(obs[:], paid_budget=40)
        hits = 0
        for _ in range(30):
            a = pol.choose_for_goal([1, 1])
            nxt = env.step(a)
            pol.update({"observation": obs[:], "action": a, "next_observation": nxt[:]})
            if nxt == [1, 1]:
                hits += 1
            obs = nxt
        self.assertGreaterEqual(hits, 20)


if __name__ == "__main__":
    unittest.main()
