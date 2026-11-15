"""AAI-11F frozen exact-goal two-action oracle feasibility source tests."""
from __future__ import annotations

import json
import math
from pathlib import Path
import subprocess
import sys
import unittest

HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
sys.path.insert(0,str(HERE.parent/"AAI-11P"))
import world,admission
import audit


class OriginalGoalGateFeasibility(unittest.TestCase):
    def test_prereg_original_source_and_first_use_fence(self):
        p=json.loads((HERE/"prereg.json").read_text("utf8"))
        self.assertEqual(p["id"],"AAI-11F")
        self.assertEqual(p["lineage"]["parent_sha"],
                         "f9429b90e35c6b98b85a328e8b5c6186519ea27d")
        self.assertEqual(p["lineage"]["frozen_world_blob"],
                         "88d220e94ccf736e490f20922f1c7f5d3c1d3746")
        self.assertEqual(p["lineage"]["frozen_contexts_blob"],
                         "0f921dfeebda9ad3a0e217747e4b0365ba9c655e")
        self.assertEqual(p["prespecified_gate"]["original_threshold"],.60)
        self.assertEqual(p["science"]["used"],0)
        self.assertFalse(p["science"]["first_use_authorized"])
        self.assertTrue(p["no_post_result_tuning"])

    def test_same_input_action_goal_and_independent_frozen_laws(self):
        self.assertEqual(len(world.INPUTS),64)
        self.assertEqual(len(world.GOALS),8)
        self.assertEqual(len(world.ACTIONS),12)
        self.assertEqual(world.TRANSFER,("C","D","E","F"))
        self.assertEqual(world.FIXTURES,(
            "mechanical:alpha","mechanical:beta","mechanical:gamma"))
        self.assertEqual(len(set(world.ACTIONS)),12)

    def test_exhaustive_zero_one_two_action_solver_and_independent_BFS(self):
        for law in world.TRANSFER:
            for x in world.INPUTS[:8]:
                states,outputs=audit.closure(law,x)
                self.assertEqual(len(states),3)
                self.assertEqual(states[0],{x})
                for goal in world.GOALS:
                    exact=audit.sequences(law,x,goal)
                    self.assertEqual(exact["reachable_outcomes"],outputs)
                    self.assertEqual(exact["attainable"],int(goal in outputs))
                    self.assertEqual(exact["best_reward_has_goal"],exact["attainable"])
                    self.assertAlmostEqual(exact["reward_best"],
                                           world.exact_oracle(law,x,goal))

    def test_original_context_selection_no_dev_or_transfer_science(self):
        for key in world.FIXTURES:
            for law in world.TRANSFER:
                a=admission.contexts(key,law,12)
                b=admission.contexts(key,law,12)
                self.assertEqual(a,b)
                self.assertEqual(len(a),12)
                self.assertEqual(len(set(a)),12)
        for invalid in (994000,995000,995063,996000,996031,"995000",
                        "mechanical:delta",None):
            with self.assertRaises(PermissionError):
                world.fixture(invalid)

    def test_source_fixed_benchmark_ceiling_and_60_percent_arithmetic(self):
        result=audit.mechanical_audit()
        self.assertEqual(result["classification"],
                         "BENCHMARK_GOAL_GATE_IMPOSSIBLE")
        self.assertEqual(result["unique_original_contexts"],144)
        self.assertEqual(result["total_original_evaluation_episodes"],288)
        self.assertEqual(result["exact_goal_attainable_episodes"],144)
        self.assertEqual(result["exact_goal_unattainable_episodes"],144)
        self.assertEqual(result["exact_goal_oracle_upper_bound"],.5)
        self.assertEqual(result["frozen_60_percent_minimum_successes"],173)
        self.assertEqual(result["unattainable_required_additional_successes"],29)
        self.assertTrue(result["two_independent_reachability_algorithms_agree"])
        self.assertTrue(result["original_benchmark_oracle_reward_verified"])
        self.assertEqual(result["reserved_cohorts_consumed"],0)

    def test_cost_sensitive_exact_oracle_reproduction(self):
        outcome=audit.mechanical_audit()
        self.assertAlmostEqual(
            outcome["original_exact_two_action_oracle_mean_reward"],
            2.448263889,places=7)
        self.assertEqual(outcome["minimum_actions_to_exact_goal_for_unique_contexts"]["impossible"],72)
        self.assertEqual(sum(outcome["minimum_actions_to_exact_goal_for_unique_contexts"].values()),144)
        self.assertTrue(all(k in ("0","1","2","impossible")
                            for k in outcome["minimum_actions_to_exact_goal_for_unique_contexts"]))

    def test_per_law_and_fixture_oracle_limit_independent_of_candidate(self):
        result=audit.mechanical_audit()
        bylaw=result["per_law_unique_contexts"]
        for key,expected in (("C",15),("D",22),("E",18),("F",17)):
            self.assertEqual(bylaw[key]["n"],36)
            self.assertEqual(bylaw[key]["reachable"],expected)
        byfixture=result["per_fixture_unique_contexts"]
        for key,expected in (("mechanical:alpha",25),
                             ("mechanical:beta",22),
                             ("mechanical:gamma",25)):
            self.assertEqual(byfixture[key]["n"],48)
            self.assertEqual(byfixture[key]["reachable"],expected)

    def test_all_six_bit_eight_goal_combinations_have_structural_shortfall(self):
        result=audit.mechanical_audit()["full_64x8_goal_structural_ceiling"]
        for law,n in (("C",240),("D",240),("E",228),("F",240)):
            self.assertEqual(result[law]["total"],512)
            self.assertEqual(result[law]["reachable"],n)
            self.assertLess(result[law]["fraction"],.6)

    def test_full_gate_not_retroactively_reclassified_as_science_pass(self):
        result=audit.mechanical_audit()
        self.assertEqual(result["historical_goal_success"][
                             "AAI11D_posterior_only"],.40625)
        self.assertEqual(result["historical_goal_success"][
                             "AAI11D_risk_policy"],.388888889)
        self.assertLess(result["historical_goal_success"][
                            "original_graph_recent8"],.5)
        self.assertFalse(result["new_learners_trained"])
        self.assertTrue(result["source_only"])
        self.assertNotIn("SCIENTIFIC_PASS",result["status"])

    def test_primary_cli_first_use_and_invalid_execution_are_disarmed(self):
        cmd=[sys.executable,"-B",str(HERE/"audit.py")]
        for extra in (["--primary"],["--primary","--mechanical-oracle-audit"],
                      ["--world","995000"],[]):
            run=subprocess.run(cmd+extra,text=True,capture_output=True,timeout=8)
            self.assertNotEqual(run.returncode,0)
            self.assertTrue("DISARMED" in run.stderr or
                            "unrecognized arguments" in run.stderr or
                            "only original three frozen" in run.stderr)


if __name__=="__main__":
    unittest.main()
