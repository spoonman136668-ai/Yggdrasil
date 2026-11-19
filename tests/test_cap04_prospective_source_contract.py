"""CAP04 frozen source-shape checks; no registered cohort generated or scored."""
import importlib.util
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


    def test_predecessor_is_not_aliased_to_current_action(self):
        self.assertEqual(source.SCHEMA, "yggdrasil.cap04.prospective-source.v2")
        expected = tuple(source.action_at(t) for t in range(source.EPISODES))
        self.assertEqual(len(expected), 96)
        # The schedule is independent of both fixture source identities,
        # unknown outcomes, hidden phase and private latent state.
        for identity in source.ENGINEERING_FIXTURES:
            rows = source.engineering_fixture(identity)
            self.assertEqual(tuple(r["action"] for r in rows), expected)
            self.assertEqual(tuple(expected[t] for t in range(32, 72)),
                             tuple(r["action"] for r in rows[32:72]))
            for start, end in ((0, 32), (32, 72), (72, 96)):
                actions = expected[start:end]
                self.assertEqual({action: actions.count(action)
                                  for action in source.ACTIONS},
                                 {action: (end-start)//4 for action in source.ACTIONS})
            # Prior-action variation conditional on the *same current action*
            # is necessary (old fixed-cycle source had exactly 1 per action).
            previous = {action: set() for action in source.ACTIONS}
            previous_in_same_public_context = {}
            for t in range(32, 72):
                event = rows[t]
                prior = rows[t-1]["action"]
                now = event["action"]
                previous[now].add(prior)
                key = (event["views"], now)
                previous_in_same_public_context.setdefault(key, set()).add(prior)
            self.assertGreaterEqual(min(map(len, previous.values())), 2)
            # Observed public-context/action duplicates with differing
            # predecessor occur; this is an engineering support check, not
            # an efficacy or intervention-effect claim.
            discriminating = sum(1 for v in previous_in_same_public_context.values()
                                 if len(v) > 1)
            self.assertGreaterEqual(discriminating, 4)
            self.assertTrue(any(len(v) > 1 for v in previous.values()))
        for invalid in (-1, 96, False, "0", None, 0.0):
            with self.subTest(invalid=invalid), self.assertRaisesRegex(
                    ValueError, "ACTION_CLOCK"):
                source.action_at(invalid)

    def test_source_identity_separation_and_budget(self):
        left = source.engineering_fixture(source.ENGINEERING_FIXTURES[0])
        right = source.engineering_fixture(source.ENGINEERING_FIXTURES[1])
        self.assertTrue(set(x["id"] for x in left).isdisjoint(x["id"] for x in right))
        for invalid in ("99917", 99917, "100117", "engineering-history-01", None, False):
            with self.subTest(invalid=invalid), self.assertRaisesRegex(
                    ValueError, "REGISTERED_FIRST_USE_FORBIDDEN"):
                source.engineering_fixture(invalid)


if __name__ == "__main__":
    unittest.main()
