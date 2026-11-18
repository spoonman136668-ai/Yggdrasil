"""WSP-176: exhaust all five-node DAG masks under opaque downstream dynamics.

These are source-FREE, fabricated proof stress controls. No original reset/do/step.
"""
from __future__ import annotations

import ast
from pathlib import Path
import unittest

from public_boundary import PublicEvidence
from goal_veto import goal_action, plan

POSITIONS = ((0, 0), (0, 4), (4, 0), (4, 4), (2, 2))
EDGES = tuple((src, dst) for dst in range(1, 5) for src in range(dst))


def simulate_translated(colors: list[int], index: int, chosen: int,
                        mask: int, seed: int) -> None:
    """An adversarial source-free *surrogate*, not the original simulator.

    The only required source semantic is that an intervention can propagate
    through future graph indices but cannot change a previous index.
    """
    colors[index] = chosen
    reached = {index}
    for later in range(index + 1, 5):
        parents = [earlier for earlier in reached
                   if (earlier, later) in (EDGES[k] for k in range(len(EDGES))
                                           if (mask >> k) & 1)]
        if parents:
            reached.add(later)
            colors[later] = (seed + 3 * later + sum(
                (p + 1) * (colors[p] + 1) for p in parents)) % 5


class FifthStepVetoTests(unittest.TestCase):
    def test_all_dags_and_opaque_downstream_laws(self):
        # Enumerates EVERY directed i<j edge mask, 3 different hidden dynamics.
        # A five-step reward=1.0 is a theorem under original source's
        # lower-index immunity, not evidence from protected original worlds.
        for mask in range(1 << len(EDGES)):
            for seed in (0, 7, 29):
                goal_colors = [(seed + 3 * i + (mask >> (i % 10))) % 5
                               for i in range(5)]
                current = [(seed + i) % 5 for i in range(5)]
                public_goal = tuple((x, y, c) for (x, y), c
                                    in zip(POSITIONS, goal_colors))
                actions = plan(public_goal)
                self.assertEqual(len(actions), 5)
                for i, action in enumerate(actions):
                    self.assertEqual(action, goal_action(public_goal, i))
                    self.assertEqual(divmod(action, 5), (i, goal_colors[i]))
                    simulate_translated(current, i, action % 5, mask, seed)
                    self.assertEqual(current[:i + 1], goal_colors[:i + 1])
                self.assertEqual(sum(a == b for a, b in zip(current, goal_colors)) / 5, 1.0)

    def test_invalid_step_and_goal(self):
        goal = tuple((x, y, i) for i, (x, y) in enumerate(POSITIONS))
        for invalid in (-1, 5, 6, True, None, 3.0, "2"):
            with self.subTest(invalid=invalid), self.assertRaisesRegex(ValueError, "STEP_RANGE"):
                goal_action(goal, invalid)
        for malformed in (None, (), ((0, 0, 0),), tuple((0, 0, i) for i in range(5))):
            with self.subTest(malformed=malformed), self.assertRaises(ValueError):
                plan(malformed)

    def test_only_public_goal_no_source_import(self):
        root = Path(__file__).with_name("goal_veto.py")
        content = root.read_text(encoding="utf-8")
        ast.parse(content)
        for banned in ("import causal_gym", "import torch", "import numpy", "owner_lease",
                       "original_source_actor", "source_reset", "source_step",
                       "mlps", "adjacency_matrix", "actions_to_target"):
            self.assertNotIn(banned, content)
        goal = tuple((x, y, i) for i, (x, y) in enumerate(POSITIONS))
        self.assertEqual(plan(goal), (0, 6, 12, 18, 24))


if __name__ == "__main__":
    unittest.main()
