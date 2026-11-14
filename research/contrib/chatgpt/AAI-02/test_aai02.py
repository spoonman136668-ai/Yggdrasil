"""Engineering-only checks for frozen AAI-02A, not a scientific acceptance test."""
import importlib.util
import json
import pathlib
import unittest

HERE = pathlib.Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location("aai02_run", HERE / "run.py")
aai = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(aai)


class AAI02Tests(unittest.TestCase):
    def test_seeds_and_laws(self):
        self.assertFalse(set(aai.TRAIN) & set(aai.DEV))
        self.assertFalse(set(aai.DEV) & set(aai.TRANSFER))
        self.assertFalse(set(aai.TRAIN) & set(aai.NEGATIVE))
        for s in (41000, 42000, 43000, 44000):
            w = aai.world(s)
            self.assertEqual(len(set(w["roles"].values())), 3)
            self.assertIn(w["law"], (0, 1))
            self.assertEqual(w, aai.world(s))

    def test_identifiable_only_by_diagnostic_intervention(self):
        for s in (41000, 42000, 43000, 44000):
            w = aai.world(s)
            other = dict(w, law=1-w["law"])
            self.assertEqual(aai.passive(w), aai.passive(other))
            for i in range(3):
                self.assertEqual(aai.intervention(w, "A", i),
                                 aai.intervention(other, "A", i))
                self.assertNotEqual(aai.intervention(w, "C", i)["b"],
                                    aai.intervention(other, "C", i)["b"])

    def test_bounded_same_memory_pool(self):
        for volume in aai.DISTRACTORS:
            w = aai.world(42000)
            events = [{"type": "passive", "abc": obs, "t": -4+i}
                      for i, obs in enumerate(aai.passive(w))]
            events.extend(aai.intervention(w, "C", i) for i in range(3))
            events.extend(aai.make_distractors(w, volume))
            for method in ("relevance", "recent", "reservoir"):
                memory = aai.retain(events, method, w["seed"])
                self.assertLessEqual(len(memory), 8)
                self.assertTrue(all("law" not in event for event in memory))
                if method == "relevance":
                    self.assertEqual(aai.feature(memory),
                                     aai.feature(events))
        self.assertEqual(aai.feature(aai.retain(events, "recent", w["seed"])), 0)

    def test_no_oracle_when_probe_removed(self):
        self.assertEqual(aai.bayes([]), 0)
        for s in (42000, 43000):
            w = aai.world(s)
            changed = [dict(aai.intervention(w, "C", i), action="A")
                       for i in range(3)]
            self.assertEqual(aai.feature(changed), 0)

    def test_determinism_excluding_timing(self):
        first = aai.evaluate()
        second = aai.evaluate()
        first.pop("local_elapsed_seconds")
        second.pop("local_elapsed_seconds")
        self.assertEqual(json.dumps(first, sort_keys=True),
                         json.dumps(second, sort_keys=True))
        self.assertEqual(first["prereg_commit"], aai.PREREG)
        self.assertEqual(first["integration"], "NONE")


if __name__ == "__main__":
    unittest.main()
