"""Zero official cohort use: independent physical physics and ambiguity gates."""
import importlib.util
from pathlib import Path
import unittest

spec = importlib.util.spec_from_file_location(
    "md30_preflight", Path(__file__).with_name("structural_rewire.py"))
module = importlib.util.module_from_spec(spec)
import sys
sys.modules[spec.name] = module
spec.loader.exec_module(module)


class MD30Preflight(unittest.TestCase):
    def test_reference_physics_all_fixture_motifs_and_clamps(self):
        for family in module.FAMILIES:
            for seed in (11, 22, 33, 44):
                graph = module.fixture_graph(seed, family)
                for root in ((0, 0), (0, 1), (1, 0), (1, 1)):
                    for clamp in (None, *((n, v) for n in range(6) for v in (0, 1))):
                        self.assertEqual(graph.respond(root, clamp),
                                         module.reference_enumerate(graph, root, clamp))
                self.assertEqual(graph.fingerprint(), module.fixture_graph(seed, family).fingerprint())

    def test_opposite_actions_with_identical_public_history_and_paid_diagnostic(self):
        fixture = module.preflight_headroom()
        self.assertEqual((fixture["left_best"], fixture["right_best"]), (1, 0))
        self.assertEqual(fixture["headroom"], 0.75)
        a, b = module.World(module.LEFT), module.World(module.RIGHT)
        self.assertEqual(a.observe(), b.observe())
        ra, rb = a.step({"kind": "diagnostic", "node": 0, "value": 1}), b.step(
            {"kind": "diagnostic", "node": 0, "value": 1})
        self.assertEqual(ra[1], -0.05)
        self.assertEqual(rb[1], -0.05)
        self.assertNotEqual(ra[0]["sensor_vector"], rb[0]["sensor_vector"])
        self.assertEqual(len(a.observe()["charged_history"]), 1)

    def test_unannounced_genuine_structural_rewire(self):
        world = module.World(module.LEFT, next_graph=module.RIGHT)
        start = world.observe()
        world.step({"kind": "diagnostic", "node": 0, "value": 1})
        after, score, done = world.step({"kind": "actuator", "node": 1, "value": 1})
        self.assertFalse(done)
        self.assertEqual(score, 0.98)
        self.assertEqual(after["phase"], 1)
        self.assertEqual(after["sensor_vector"], start["sensor_vector"])
        self.assertNotIn("graph", after)
        self.assertNotIn("rewire", after)
        observed, reward, _ = world.step({"kind": "diagnostic", "node": 0, "value": 1})
        self.assertEqual(reward, -0.05)
        self.assertEqual(observed["sensor_vector"][5], 0)
        _, score2, done2 = world.step({"kind": "actuator", "node": 0, "value": 1})
        self.assertTrue(done2)
        self.assertEqual(score2, 0.98)
        self.assertEqual(world.receipt()["paid_steps"], 4)

    def test_action_caps_both_stages_and_no_unpaid_target_reward(self):
        world = module.World(module.LEFT)
        for _ in range(3):
            result = world.step({"kind": "diagnostic", "node": 2, "value": 0})
            self.assertEqual(result[1], -0.05)
        with self.assertRaisesRegex(AssertionError, "CAP"):
            world.step({"kind": "diagnostic", "node": 2, "value": 0})
        world.step({"kind": "actuator", "node": 1, "value": 1})
        for _ in range(3):
            world.step({"kind": "diagnostic", "node": 2, "value": 0})
        world.step({"kind": "actuator", "node": 1, "value": 1})
        rec = world.receipt()
        self.assertEqual(rec["paid_steps"], 8)
        self.assertEqual(rec["net_utility"], 1.66)
        with self.assertRaises(AssertionError):
            world.step({"kind": "actuator", "node": 0, "value": 1})

    def test_reserved_and_all_other_official_seeds_fail_closed(self):
        for seed in (1080001, 1080768, 2080001, 3080064, 4080001, 4080256, 1070001):
            with self.assertRaisesRegex(AssertionError, "COHORT_ACCESS_DENIED"):
                module.fixture_graph(seed, "composed")
        for invalid in (True, "11", -1):
            with self.assertRaises(Exception):
                module.fixture_graph(invalid, "chain")

    def test_no_future_labels_or_hidden_structure_in_policy_observation(self):
        world = module.World(module.LEFT, next_graph=module.RIGHT)
        obs = world.observe()
        text = module.canonical(obs).lower()
        for forbidden in ("seed", "graph", "topology", "rewire", "latent", "future", "oracle"):
            self.assertNotIn(forbidden, text)
        self.assertEqual(len(obs["sensor_vector"]), 6)
        self.assertEqual(len(obs["actuator_availability"]), 2)

    def test_invalid_action_does_not_charge_or_advance(self):
        world = module.World(module.LEFT)
        before = world.observe()
        for invalid in ({"kind": "actuator", "node": 2, "value": 1},
                        {"kind": "diagnostic", "node": 5, "value": 0},
                        {"kind": "actuator", "node": 0, "value": True},
                        {"kind": "actuator", "node": 0, "value": 0, "peek": True}):
            with self.assertRaises(AssertionError):
                world.step(invalid)
            self.assertEqual(world.observe(), before)


if __name__ == "__main__":
    unittest.main()
