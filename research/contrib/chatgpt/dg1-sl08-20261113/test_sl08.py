"""SL08: prospective custody, failure gates, matched actions, no oracle."""
import unittest
from sl08 import (ARMS, COHORTS, FLIPS, FREEZE, Calibrated, World,
                  audit, one_world)


class Dummy:
    def __init__(self):
        self.next_prediction = 0

    def predict(self, before, action):
        return self.next_prediction

    def observe(self, before, action, after):
        pass

    def rest(self):
        pass


class SL08Tests(unittest.TestCase):
    def test_frozen_seeds_and_paying_physical_steps(self):
        self.assertEqual(FREEZE, "66a64101af5c926f43a91e991409034b3b18be35")
        self.assertEqual(len(ARMS), 6)
        self.assertEqual(sum(map(len, COHORTS.values())), 32)
        for group, seeds in COHORTS.items():
            w = World(seeds[0], group)
            s = seeds[0] % 16
            for step in range(80):
                kind, action, s = w.step(
                    s, step, step % 4 if step >= 60 and step not in FLIPS else None)
                self.assertIn(kind, ("flip", "causal"))
            self.assertEqual(w.paid, 80)
            with self.assertRaises(ValueError):
                w.step(s, 79, 0)
        with self.assertRaises(ValueError):
            World(100101, "ABCA")

    def test_two_paid_correct_observations_required_for_recovery(self):
        x = Calibrated("native_action2")
        d = Dummy()
        x.model = d
        d.next_prediction = 0
        x.observe(0, 0, 1)  # Paid physically valid wrong prediction.
        self.assertFalse(x.trusted[0])
        self.assertIsNone(x.predict(0, 0))
        d.next_prediction = 1
        x.observe(0, 0, 1)
        self.assertFalse(x.trusted[0])
        x.observe(0, 0, 1)
        self.assertTrue(x.trusted[0])
        self.assertEqual(x.predict(0, 0), 1)
        self.assertEqual(x.errors_observed, 1)
        self.assertEqual(x.quarantines, 1)
        self.assertEqual(x.causal_events, 3)

    def test_independent_conventional_has_same_two_hit_rule(self):
        x = Calibrated("conventional_action2")
        d = Dummy()
        x.model = d
        x.observe(0, 0, 1)
        self.assertFalse(x.trusted[0])
        d.next_prediction = 1
        x.observe(0, 0, 1)
        self.assertFalse(x.trusted[0])
        x.observe(0, 0, 1)
        self.assertTrue(x.trusted[0])

    def test_one_hit_and_global_ablations(self):
        x = Calibrated("native_action1")
        d = Dummy()
        x.model = d
        x.observe(0, 0, 1)
        self.assertFalse(x.trusted[0])
        d.next_prediction = 1
        x.observe(0, 0, 1)
        self.assertTrue(x.trusted[0])
        z = Calibrated("native_global2")
        z.model = Dummy()
        z.observe(0, 0, 1)
        self.assertEqual(z.trusted, [False] * 4)

    def test_custody_and_tamper_rejection(self):
        for arm in ARMS:
            x = Calibrated(arm)
            x.observe(0, 0, 0)
            x.observe(1, 1, 1)
            x.rest()
            raw = x.snapshot()
            y = Calibrated.restore(raw)
            self.assertEqual(y.snapshot(), raw)
            for state in range(16):
                for action in range(4):
                    self.assertEqual(x.predict(state, action),
                                     y.predict(state, action))
            self.assertLessEqual(len(raw), 8192)
            for bad in (raw[:-1], raw + b" ", raw[1:],
                        bytes([raw[0] ^ 1]) + raw[1:]):
                with self.assertRaises(ValueError):
                    Calibrated.restore(bad)

    def test_no_fictive_learning_and_audit_separation(self):
        a = Calibrated("native_action2")
        with self.assertRaises(TypeError):
            a.observe(0, 0, 1, phase_label="A")
        with self.assertRaises(ValueError):
            a.observe(0, 0, 2)
        self.assertEqual(a.causal_events, 0)
        world = World(101001, "ABCA")
        with self.assertRaises(ValueError):
            audit(a, world, set(), 79)

    def test_one_world_all_arms_share_full_physical_trace(self):
        w = one_world(101001, "ABCA")
        self.assertEqual(set(w["arms"]), set(ARMS))
        self.assertEqual(len(set(v["trace_sha256"] for v in
                                 w["arms"].values())), 1)
        for v in w["arms"].values():
            self.assertEqual(v["paid_steps"], 80)
            self.assertEqual(v["flips"], 10)
            self.assertEqual(v["causal_observations"], 70)
            self.assertLessEqual(v["cold_checkpoint_bytes"], 8192)
            for stage in ("60", "64", "72", "80"):
                sums = v["stage_audits"][stage]
                self.assertEqual(sum(sums[k] for k in
                                     ("correct", "wrong_confident", "abstained")), 64)


if __name__ == "__main__":
    unittest.main()
