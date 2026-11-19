"""CAP04 pre-first-use shortcut-control evidence checks; no registered seeds."""
import importlib.util
from pathlib import Path
import unittest
from collections import defaultdict
from yggdrasil.native_context_basis import digest

ROOT = Path(__file__).resolve().parents[1] / "research/contrib/chatgpt/YGG-CAP04"
def load(name, filename):
    spec = importlib.util.spec_from_file_location(name, ROOT / filename)
    obj = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(obj)
    return obj

audit = load("cap04_shortcut_fixture_audit", "shortcut_controls.py")
source = load("cap04_shortcut_fixture_source", "prospective_source.py")


class ShortcutControlAuditTests(unittest.TestCase):
    def test_same_public_tapes_equal_budget_and_frozen_first_use(self):
        receipt = audit.audit_engineering_fixtures()
        self.assertEqual(receipt["evidence_class"],
                         "ENGINEERING_FIXTURE_DIAGNOSTIC_ONLY")
        self.assertEqual(set(receipt["invalid_oracle_arms"]),
                         set(audit.DIAGNOSTIC_ORACLES))
        self.assertEqual(receipt["fitted_events"], {f: 96 for f in audit.FIXTURES})
        self.assertEqual(set(receipt["arms"]), set(audit.ARMS))
        self.assertEqual(set(receipt["phase_mean_brier"]), set(audit.PHASE_WINDOWS))
        self.assertEqual(receipt, audit.audit_engineering_fixtures())
        for phase, metrics in receipt["phase_mean_brier"].items():
            self.assertEqual(set(metrics), set(audit.ARMS))
            self.assertTrue(all(0 <= value <= 1 for value in metrics.values()))
        for seed in source.REGISTERED:
            with self.subTest(seed=seed), self.assertRaisesRegex(
                    ValueError, "REGISTERED_FIRST_USE_FORBIDDEN"):
                source.generate_registered(seed)

    def test_prequential_fencing_and_atomic_rejections(self):
        m = audit.ShortcutControls()
        left = source.engineering_fixture(source.ENGINEERING_FIXTURES[0])
        start = m.checkpoint()
        with self.assertRaisesRegex(ValueError, "FUTURE_SENSOR"):
            m.forecast(audit.FIXTURES[0], 0, left[0]["views"],
                       left[0]["action"], "transition", left[0]["s2"])
        with self.assertRaisesRegex(ValueError, "WITNESSED_SENSOR"):
            m.forecast(audit.FIXTURES[0], 0, left[0]["views"],
                       left[0]["action"], "reward")
        with self.assertRaisesRegex(ValueError, "CLOCK"):
            m.forecast(audit.FIXTURES[0], 1, left[1]["views"],
                       left[1]["action"], "transition")
        self.assertEqual(m.checkpoint(), start)
        first = m.forecast(audit.FIXTURES[0], 0, left[0]["views"],
                           left[0]["action"], "transition")
        self.assertEqual(set(first), set(audit.ARMS))
        self.assertTrue(all(abs(x - .5) < 1e-12 for x in first.values()))
        self.assertEqual(start, m.checkpoint())
        m.observe(audit.FIXTURES[0], 0, left[0])
        before = m.checkpoint()
        with self.assertRaisesRegex(ValueError, "DUPLICATE"):
            m.observe(audit.FIXTURES[0], 1, left[0])
        self.assertEqual(before, m.checkpoint())
        with self.assertRaisesRegex(ValueError, "COLD_HASH"):
            audit.ShortcutControls.restore(before, "0" * 64)
        self.assertEqual(audit.ShortcutControls.restore(
            before, digest(before)).checkpoint(), before)

    def test_historical_action_clock_and_source_identity_confounds_exposed(self):
        left, right = [source.engineering_fixture(f) for f in audit.FIXTURES]
        # The original fixed cycle must fail predecessor identifiability.
        old = [source.ACTIONS[t % 4] for t in range(96)]
        old_support = defaultdict(set)
        for t in range(32, 72):
            old_support[old[t]].add(old[t - 1])
        self.assertEqual({a: len(old_support[a]) for a in source.ACTIONS},
                         {a: 1 for a in source.ACTIONS})
        # A clock/current-action lookup cannot recover the actual predecessor
        # across both independent fixture worlds; this is a SOURCE support
        # property, not a learned model result.
        ambiguous = [t for t in range(32, 72)
                     if left[t]["action"] == right[t]["action"] and
                     left[t - 1]["action"] != right[t - 1]["action"]]
        self.assertGreaterEqual(len(ambiguous), 1)
        # Conversely a permitted source+clock *oracle* reconstructs every
        # predecessor: warn against exposing source identity or seed keys.
        for fixture, rows in zip(audit.FIXTURES, (left, right)):
            self.assertEqual([source.exogenous_action(fixture, t)
                              for t in range(96)],
                             [r["action"] for r in rows])
            self.assertEqual([source.exogenous_action(fixture, t - 1)
                              for t in range(33, 72)],
                             [rows[t - 1]["action"] for t in range(33, 72)])
            same_public = defaultdict(set)
            for t in range(32, 72):
                same_public[(rows[t]["views"], rows[t]["action"])].add(
                    rows[t - 1]["action"])
            self.assertGreaterEqual(sum(len(v) >= 2 for v in same_public.values()), 4)

    def test_history_sham_is_past_only_and_independently_fit(self):
        fixture = audit.FIXTURES[0]
        rows = source.engineering_fixture(fixture)
        model = audit.ShortcutControls()
        for t, row in enumerate(rows[:48]):
            before = model.checkpoint()
            a = model.forecast(fixture, t, row["views"], row["action"],
                               "transition")
            b = model.forecast(fixture, t, row["views"], row["action"],
                               "reward", row["s2"])
            self.assertEqual(before, model.checkpoint())
            self.assertEqual(set(a), set(b))
            model.observe(fixture, t, row)
        self.assertEqual(model.checkpoint(),
                         audit.ShortcutControls.restore(
                             model.checkpoint(), digest(model.checkpoint())).checkpoint())
        # Verify actual and deliberately misaligned previous-action features
        # diverge while neither arm uses the current target or future action.
        self.assertTrue(any(rows[t - 1]["action"] != rows[t - 2]["action"]
                            for t in range(2, 48)))


if __name__ == "__main__":
    unittest.main()
