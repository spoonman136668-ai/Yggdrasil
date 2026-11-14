"""AAI-10B exhaustive-ish synthetic semantic-equivalence, cold and disarm tests."""
import itertools
import json
from pathlib import Path
import subprocess
import sys
import unittest

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "AAI-10P"))
sys.path.insert(0, str(HERE.parent / "AAI-10A"))
sys.path.insert(0, str(HERE))

import benchmark as b
import models as frozen
import cached as fast


def synthetic_rows():
    for law in ("A", "B", "C", "D"):
        for rep in range(2):
            for i, x in enumerate(b.INPUTS):
                g = b.GOALS[(i + rep) % len(b.GOALS)]
                initial = b.public_initial(law, x, g)
                action = b.ACTIONS[(i * 3 + rep) % len(b.ACTIONS)]
                yield initial
                yield b.public_step(law, initial, action)


class FrozenCacheIdentity(unittest.TestCase):
    def test_registration_and_no_science(self):
        p = json.loads((HERE / "prereg.json").read_text(encoding="utf-8"))
        self.assertEqual(p["id"], "AAI-10B")
        self.assertEqual(p["parent_candidate_sha"],
                         "64a585010e13519c6290cc8c406154e1f23b9e78")
        self.assertFalse(p["authority"]["science_first_use"])
        self.assertTrue(p["no_post_result_tuning"])
        self.assertEqual(p["scientific_fresh_cohorts_used"], 0)
        self.assertEqual(len(b.INPUTS), 8)

    def test_all_public_prefixes_preserve_exact_model_and_predictions(self):
        old = frozen.ProtectedOperatorBank()
        new = fast.CachedOperatorBank()
        seen = 0
        for observed in synthetic_rows():
            old.learn(observed)
            new.learn(observed)
            seen += 1
            self.assertEqual(frozen.canonical(old.state()),
                             frozen.canonical(new.state()), seen)
            for x in b.INPUTS:
                self.assertEqual(old.predict(x), new.predict(x), (seen, x))
            if seen % 16 == 0:
                for x, goal in itertools.product(b.INPUTS, b.GOALS):
                    public = b.public_initial("A", x, goal)
                    self.assertEqual(old.choose(public), new.choose(public),
                                     (seen, x, goal))
                    # Same decision under repeat with no intervening update.
                    self.assertEqual(new.choose(public), new.choose(public))
        self.assertEqual(seen, 128)

    def test_exact_cold_checkpoint_forks_and_no_stale_predictions(self):
        original = frozen.ProtectedOperatorBank()
        accelerated = fast.CachedOperatorBank()
        rows = list(synthetic_rows())
        for event in rows[:64]:
            original.learn(event)
            accelerated.learn(event)
        snap = frozen.canonical(original.state())
        self.assertEqual(snap, frozen.canonical(accelerated.state()))
        clone = fast.cold_clone(snap)
        self.assertEqual(snap, frozen.canonical(clone.state()))
        for e in rows[64:]:
            original.learn(e)
            accelerated.learn(e)
            clone.learn(e)
            self.assertEqual(frozen.canonical(original.state()),
                             frozen.canonical(accelerated.state()))
            self.assertEqual(frozen.canonical(original.state()),
                             frozen.canonical(clone.state()))
            for x in b.INPUTS:
                self.assertEqual(original.predict(x), accelerated.predict(x))
                self.assertEqual(original.predict(x), clone.predict(x))
        self.assertEqual(frozen.canonical(fast.cold_clone(snap).state()), snap)

    def test_full_public_schema_protects_against_hidden_labels(self):
        old = frozen.ProtectedOperatorBank()
        new = fast.CachedOperatorBank()
        source = b.public_initial("A", (0, 1, 0), (1, 0))
        for bogus in ("law", "ground_truth_env_change", "secret", "regime"):
            invalid = {**source, bogus: "A"}
            for model in (old, new):
                snapshot = frozen.canonical(model.state())
                with self.assertRaises(ValueError):
                    model.learn(invalid)
                with self.assertRaises(ValueError):
                    model.choose(invalid)
                self.assertEqual(snapshot, frozen.canonical(model.state()))

    def test_ephemeral_cache_never_serializes_and_restarts_empty(self):
        m = fast.CachedOperatorBank()
        r = b.public_initial("A", (0, 0, 1), (1, 0))
        self.assertEqual(len(m._predictions), 0)
        m.predict((0, 0, 1))
        m.choose(r)
        self.assertGreater(len(m._predictions), 0)
        self.assertGreater(len(m._plans), 0)
        snap = frozen.canonical(m.state())
        self.assertNotIn("_predictions", snap)
        self.assertNotIn("_plans", snap)
        clone = fast.cold_clone(snap)
        self.assertEqual(clone._predictions, {})
        self.assertEqual(clone._plans, {})
        self.assertEqual(frozen.canonical(clone.state()), snap)
        first = b.public_initial("B", (0, 0, 1), (1, 0))
        second = b.public_step("B", first, b.ACTIONS[4])
        m.learn(first)
        m.learn(second)
        self.assertEqual(m._predictions, {})
        self.assertEqual(m._plans, {})

    def test_invalid_checkpoint_and_bad_input_rejected(self):
        s = frozen.canonical(fast.CachedOperatorBank().state())
        with self.assertRaises(ValueError):
            fast.cold_clone(s + " ")
        with self.assertRaises(ValueError):
            fast.CachedOperatorBank().predict((1, 2, 0))

    def test_primary_cli_fails_closed(self):
        p = subprocess.run([sys.executable, "-B", str(HERE/"profile_dev.py"),
                            "--primary"], capture_output=True, text=True, timeout=10)
        self.assertNotEqual(p.returncode, 0)
        self.assertIn("DISARMED", p.stderr)


if __name__ == "__main__":
    unittest.main()
