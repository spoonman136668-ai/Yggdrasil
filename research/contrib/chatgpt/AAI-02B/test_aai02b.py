"""AAI-02B source invariants; engineering, not independent scientific acceptance."""
import importlib.util
import json
import pathlib
import unittest

PATH = pathlib.Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location("aai02b", PATH / "run.py")
m = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(m)


class AAI02BTests(unittest.TestCase):
    def test_no_overlap_and_causal_identifiability(self):
        self.assertEqual(len(set(m.TRAIN) | set(m.DEV) | set(m.TRANSFER) | set(m.NEGATIVE)), 896)
        for seed in (62000, 62017, 63000, 64000, 65000):
            w = m.setting(seed, seed >= 64000)
            self.assertEqual(w["diagnostic"], (3 * (w["context"] % 4) + 1) % 4)
            self.assertIn(w["law"], (0, 1))
            self.assertEqual(len(m.events_for(w)), 96)
            self.assertEqual(len(m.events_for(w, True)), 104)

    def test_eight_slot_online_cap_and_no_hidden_truth(self):
        w = m.setting(63000)
        es = m.events_for(w)
        self.assertTrue(all("law" not in e and "diagnostic" not in e for e in es))
        for method in ("recent", "active_recent", "reservoir", "expert"):
            keep = m.retain(es, method, w["context"], w["seed"], oracle=w["diagnostic"])
            self.assertEqual(len(keep), 8)
        for method in ("direct", "logistic", "scrambled"):
            keep = m.retain(es, method, w["context"], w["seed"], [0.1] * 16)
            self.assertEqual(len(keep), 8)

    def test_supervised_fit_and_cold_restore(self):
        train = [m.setting(s) for s in list(m.TRAIN)[:16]]
        w = m.direct_fit(train)
        logistic, bce = m.logistic_fit(train)
        self.assertEqual((len(w), len(logistic)), (16, 16))
        self.assertGreaterEqual(bce, 0)
        self.assertEqual(json.loads(json.dumps(w)), w)

    def test_determinism_and_no_integration(self):
        a, b = m.evaluate(), m.evaluate()
        a.pop("elapsed_seconds")
        b.pop("elapsed_seconds")
        self.assertEqual(a, b)
        self.assertEqual(a["prereg_commit"], m.PREREG)
        self.assertEqual(a["integration"], "NONE")

    def test_nontrivial_negative_and_reversal_controls(self):
        result = m.evaluate()
        self.assertIn("negative", result["cohorts"])
        self.assertIn("dev_reversal", result["cohorts"])
        self.assertIn("transfer_reversal", result["cohorts"])
        self.assertIn("mcnemar_p", result["paired"])
        self.assertTrue(result["sanity"]["fixed_eight_memory_slots"])


if __name__ == "__main__":
    unittest.main()
