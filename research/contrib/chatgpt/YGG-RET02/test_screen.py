"""YGG-RET02 deterministic source-bound negative and chronology checks."""
import importlib.util
from pathlib import Path
import unittest

SCRIPT = Path(__file__).with_name("screen.py")
spec = importlib.util.spec_from_file_location("ygg_ret02_screen", SCRIPT)
s = importlib.util.module_from_spec(spec)
spec.loader.exec_module(s)

class ScreenTests(unittest.TestCase):
    def test_original_two_sealed_cohorts_are_unchanged(self):
        for seed in (14071, 14072):
            new, old = s.inputs(seed)
            self.assertEqual((len(new), len(old)), (64, 32))
            self.assertEqual(len({x["source_id"] for x in new + old}), 96)
            self.assertTrue(all(x["already_consumed_diagnostic"] for x in old))

    def test_one_fixed_public_key_never_uses_hidden_world_or_phase(self):
        new, _ = s.inputs(14071)
        sample = dict(new[0])
        original = s.public_key(sample)
        sample["phase"] = "redacted"
        sample["world"] = 73424
        sample["seed"] = 0
        sample["row"] = dict(sample["row"], s2=1 - sample["row"]["s2"],
                             y=1 - sample["row"]["y"])
        self.assertEqual(original, s.public_key(sample))

    def test_likelihood_and_evidence_posterior_bounded(self):
        row = {"s2": 1, "y": 0}
        self.assertAlmostEqual(s.advance(.125, [.9, .1], [.1, .9], row),
                               0.125 * .81 / (.125 * .81 + .875 * .01))
        for w in (s.LO, s.HI):
            self.assertLessEqual(s.advance(w, [.9, .9], [.1, .1], row), s.HI)
            self.assertGreaterEqual(s.advance(w, [.9, .9], [.1, .1], row), s.LO)

    def test_hindsight_upper_bound_only_for_audit(self):
        row = {"s2": 1, "y": 1}
        a, b = [1., 0.], [0., 1.]
        self.assertAlmostEqual(s.oracle_score(a, b, row), .25)
        self.assertAlmostEqual(s.oracle_score([1, 1], [0, 0], row), 0.)
        self.assertTrue(s.oracle_score(a, b, row) <= min(s.brier(a, row),
                                                          s.brier(b, row)))

    def test_corrupt_public_views_fail_closed(self):
        row = {"s1": 0, "x1": 1, "s2": 1, "x2": 0, "y": 0}
        with self.assertRaisesRegex(ValueError, "PUBLIC_VIEWS"):
            s.public_key({"public_views": [[0, 2], [0, 1]], "row": row})
        with self.assertRaisesRegex(ValueError, "PUBLIC_ROW"):
            s.public_key({"public_views": [[0, 1], [0, 1]],
                          "row": dict(row, s1=1)})

    def test_full_original_trace_replay_is_deterministic(self):
        first = s.run()
        second = s.run()
        self.assertEqual(first, second)
        self.assertEqual(len(first["replicas"]), 2)
        for sample in first["replicas"]:
            self.assertEqual(len(sample["scored_new"]), 64)
            self.assertEqual(len(sample["scored_old"]), 32)
            self.assertEqual(sum(x["late"] for x in sample["scored_new"]), 16)
            self.assertEqual(len(set(x["source_id"] for x in
                                     sample["scored_new"])), 64)
            self.assertLessEqual(sample["late"]["oracle"],
                                 sample["late"]["loss"] + 1e-13)

    def test_repeated_and_reordered_records_fail_closed(self):
        new, old = s.inputs(14071)
        with self.assertRaisesRegex(ValueError, "DUPLICATE_ID"):
            s.screen_seed(14071, new[:1] + [new[0]] + new[2:], old)
        with self.assertRaisesRegex(ValueError, "SOURCE_SEQUENCE"):
            s.screen_seed(14071, [new[1], new[0]] + new[2:], old)
        with self.assertRaisesRegex(ValueError, "HISTORIC_DIAGNOSTIC_CUSTODY"):
            s.screen_seed(14071, new, [old[1], old[0]] + old[2:])

if __name__ == "__main__":
    unittest.main()
