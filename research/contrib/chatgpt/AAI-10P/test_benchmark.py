"""AAI-10P benchmark-only tests. Scientific cohorts must remain unconsumed."""
import importlib.util
import json
from pathlib import Path
import unittest

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("aai10p_benchmark", HERE / "benchmark.py")
b = importlib.util.module_from_spec(spec)
spec.loader.exec_module(b)


class TestCausalInterventionBenchmark(unittest.TestCase):
    def test_frozen_protocol_still_precedes_implementation(self):
        p = json.loads((HERE / "prereg.json").read_text(encoding="utf8"))
        self.assertEqual(p["schema"], "yggdrasil.contrib.aai10p.frozen-benchmark-prereg.v1")
        self.assertEqual(p["id"], "AAI-10P")
        self.assertFalse(p["authority"]["scientific_first_use"])
        self.assertFalse(p["authority"]["candidate_integration"])
        self.assertEqual(p["public_observation"]["intervention_horizon"], 2)
        self.assertEqual(p["reserved_unconsumed_science_cohorts"]["transfer"],
                         {"start": 992000, "count": 64})
        self.assertEqual(tuple(p["regime_pairs"]["familiar"]), ("A", "B"))
        self.assertEqual(tuple(p["regime_pairs"]["unfamiliar"]), ("C", "D"))

    def test_distinct_nontrivial_equations(self):
        self.assertEqual(b.mediators("A", (1, 1, 0)), (0, 1))
        self.assertEqual(b.mediators("B", (1, 1, 0)), (0, 0))
        self.assertEqual(b.mediators("C", (1, 1, 0)), (1, 1))
        self.assertEqual(b.mediators("D", (1, 1, 0)), (1, 0))
        with self.assertRaises(ValueError):
            b.mediators("UNRECOGNIZED", (1, 1, 1))

    def test_public_information_fence(self):
        x, g = (0, 1, 1), (1, 0)
        for law in b.LAWS:
            s = b.public_initial(law, x, g)
            self.assertEqual(set(s), {"x", "mediators", "goal", "reward", "actions_taken"})
            self.assertEqual(s["x"], list(x))
            self.assertEqual(s["goal"], list(g))
            t = b.public_step(law, s, (0, 1))
            self.assertEqual(set(t), set(s))
            self.assertEqual(t["actions_taken"], 1)
            with self.assertRaises(ValueError):
                b.public_step(law, {**s, "hidden_law": law}, (0, 1))

    def test_interventions_are_persistent_not_reset(self):
        for law in b.LAWS:
            for x in b.INPUTS:
                for g in b.GOALS:
                    for first in b.ACTIONS:
                        for second in b.ACTIONS:
                            t = b.public_trace(law, x, g, (first, second))
                            final_x = list(x)
                            final_x[first[0]] = first[1]
                            final_x[second[0]] = second[1]
                            self.assertEqual(t[2]["x"], final_x)
                            self.assertEqual(t[2]["mediators"], list(b.mediators(law, final_x)))
                            self.assertEqual(t[2]["reward"],
                                             b.reward(t[2]["mediators"], g, 2))

    def test_stale_policy_regret_is_real_and_symmetric_admission(self):
        for familiar, unfamiliar in b.PAIRS:
            self.assertTrue(all(b.intervention_distinguishes(
                familiar, unfamiliar, x) for x in b.INPUTS))
            self.assertGreaterEqual(b.stale_policy_regret(familiar, unfamiliar), 0.50)
            self.assertGreaterEqual(b.stale_policy_regret(unfamiliar, familiar), 0.50)

    def test_cold_public_replay_bitwise_deterministic(self):
        for law in b.LAWS:
            p = b.public_trace(law, (1, 0, 1), (0, 1), ((2, 0), (1, 1)))
            q = b.public_trace(law, (1, 0, 1), (0, 1), ((2, 0), (1, 1)))
            self.assertEqual(json.dumps(p, sort_keys=True),
                             json.dumps(q, sort_keys=True))

    def test_invalid_actions_and_horizon_fail_closed(self):
        s = b.public_initial("A", (0, 0, 0), (1, 1))
        with self.assertRaises(ValueError):
            b.public_step("A", s, (4, 1))
        with self.assertRaises(ValueError):
            b.public_trace("A", (0, 0, 0), (1, 1), ((0, 1), (1, 1), (2, 1)))
        with self.assertRaises(ValueError):
            b.public_step("A", b.public_step("A", b.public_step("A", s, (1, 1)), (0, 1)), (2, 1))

    def test_complete_frozen_mechanics_with_no_science(self):
        r = b.mechanical()
        self.assertEqual(r["one_action_cases"], 768)
        self.assertEqual(r["two_action_cases"], 4608)
        self.assertEqual(r["scientific_cohorts_used"], 0)
        self.assertTrue(all(r["checks"].values()))
        self.assertEqual(r, b.mechanical())


if __name__ == "__main__":
    unittest.main()
