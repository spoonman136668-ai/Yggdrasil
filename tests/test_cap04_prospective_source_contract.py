"""CAP04 frozen source-shape checks; no registered cohort generated or scored."""
import importlib.util
from collections import defaultdict
from pathlib import Path
import unittest

SOURCE = Path(__file__).resolve().parents[1] / "research/contrib/chatgpt/YGG-CAP04/prospective_source.py"
spec = importlib.util.spec_from_file_location("cap04_source_staging", SOURCE)
source = importlib.util.module_from_spec(spec)
spec.loader.exec_module(source)


class ProspectiveSourceContractTests(unittest.TestCase):
    def test_registered_first_use_fails_closed_without_exceptions(self):
        self.assertEqual(set(source.REGISTERED_DEV), {99917, 99931})
        self.assertEqual(source.BOUNDARIES, (0, 32, 72, 96))
        for seed in source.REGISTERED:
            with self.subTest(seed=seed), self.assertRaisesRegex(
                    ValueError, "REGISTERED_FIRST_USE_FORBIDDEN"):
                source.generate_registered(seed)
        for seed in (False, "99917", 99811, 99829, 0):
            with self.subTest(seed=seed), self.assertRaises(ValueError):
                source.generate_registered(seed)

    def test_engineering_only_deterministic_public_history(self):
        for identity in source.ENGINEERING_FIXTURES:
            with self.subTest(identity=identity):
                rows = source.engineering_fixture(identity)
                self.assertEqual(rows, source.engineering_fixture(identity))
                self.assertEqual(len(rows), source.EPISODES)
                self.assertEqual(len({r["id"] for r in rows}), source.EPISODES)
                self.assertTrue(all(set(r) == {"id", "views", "action", "s2", "y", "post"}
                                    for r in rows))
                self.assertTrue(all(r["post"][1] == r["s2"] for r in rows))
                for before, after in zip(rows, rows[1:]):
                    self.assertEqual(after["views"], ((before["post"][0], before["post"][1]),
                                                      (before["post"][1], before["post"][2])))
                for start, end in ((0, 32), (32, 72), (72, 96)):
                    actual = [r["action"] for r in rows[start:end]]
                    self.assertEqual(set(actual), set(source.ACTIONS))
                    self.assertEqual({a: actual.count(a) for a in source.ACTIONS},
                                     {a: (end - start) // 4 for a in source.ACTIONS})

    def test_source_identity_separation_and_budget(self):
        left = source.engineering_fixture(source.ENGINEERING_FIXTURES[0])
        right = source.engineering_fixture(source.ENGINEERING_FIXTURES[1])
        self.assertTrue(set(x["id"] for x in left).isdisjoint(x["id"] for x in right))
        for invalid in ("99917", 99917, "100117", "engineering-history-01", None, False):
            with self.subTest(invalid=invalid), self.assertRaisesRegex(
                    ValueError, "REGISTERED_FIRST_USE_FORBIDDEN"):
                source.engineering_fixture(invalid)

    def test_novel_action_history_not_aliased_to_current_action(self):
        # Negative control: the original four-step cycle has only ONE
        # possible predecessor per current intervention; reject it.
        old = [source.ACTIONS[t % 4] for t in range(source.EPISODES)]
        old_pairs = defaultdict(set)
        for t in range(32, 72):
            old_pairs[old[t]].add(old[t - 1])
        self.assertEqual({a: len(old_pairs[a]) for a in source.ACTIONS},
                         {a: 1 for a in source.ACTIONS})
        for identity in source.ENGINEERING_FIXTURES:
            rows = source.engineering_fixture(identity)
            predecessor = defaultdict(set)
            for t in range(32, 72):
                predecessor[rows[t]["action"]].add(rows[t - 1]["action"])
            self.assertTrue(all(len(predecessor[a]) >= 2 for a in source.ACTIONS),
                            {a: len(predecessor[a]) for a in source.ACTIONS})

    def test_matched_public_state_action_exposes_distinct_predecessors(self):
        # Necessary, NOT sufficient for causal identification: history
        # varies even when current PUBLIC state and intervention are fixed.
        for identity in source.ENGINEERING_FIXTURES:
            rows = source.engineering_fixture(identity)
            matched = defaultdict(set)
            for t in range(32, 72):
                matched[(rows[t]["views"], rows[t]["action"])].add(
                    rows[t - 1]["action"])
            distinct = {k: v for k, v in matched.items() if len(v) >= 2}
            self.assertGreaterEqual(len(distinct), 4)
            self.assertGreaterEqual(len({k[1] for k in distinct}), 2)

    def test_clock_and_current_action_do_not_fix_prior_across_fixture_worlds(self):
        # Two independent exogenous schedules defeat the trivial
        # public (clock, current-action) -> previous-action shortcut.
        left, right = [source.engineering_fixture(identity)
                       for identity in source.ENGINEERING_FIXTURES]
        ambiguous = [t for t in range(32, 72)
                     if left[t]["action"] == right[t]["action"] and
                     left[t - 1]["action"] != right[t - 1]["action"]]
        self.assertGreaterEqual(len(ambiguous), 1)
        for identity, rows in zip(source.ENGINEERING_FIXTURES, (left, right)):
            for t, row in enumerate(rows):
                self.assertEqual(row["action"], source.exogenous_action(identity, t))
            for start, end in ((0, 32), (32, 72), (72, 96)):
                self.assertEqual({a: sum(r["action"] == a for r in rows[start:end])
                                  for a in source.ACTIONS},
                                 {a: (end - start) // 4 for a in source.ACTIONS})
            for bad in (-1, 96, True, 1.0):
                with self.assertRaises(ValueError):
                    source.exogenous_action(identity, bad)


if __name__ == "__main__":
    unittest.main()
