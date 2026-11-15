"""AAI-11G source-only oracle-relative benchmark qualification tests."""
from __future__ import annotations
import json
from pathlib import Path
import subprocess
import sys
import unittest

HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
sys.path.insert(0,str(HERE.parent/"AAI-11P"))
sys.path.insert(0,str(HERE.parent/"AAI-11A"))
sys.path.insert(0,str(HERE.parent/"AAI-11D"))
sys.path.insert(0,str(HERE.parent/"AAI-11F"))
import world,controls,admission
import learner as original_learner
import calibration
import audit as ceiling
import admit


class OracleRelativeProtocol(unittest.TestCase):
    def test_prereg_source_stacked_no_science_and_old_gate_immutable(self):
        p=json.loads((HERE/"prereg.json").read_text("utf8"))
        self.assertEqual(p["id"],"AAI-11G")
        self.assertEqual(p["lineage"]["parent_sha"],
                         "36cc12381a4153048e5971899fa388a0aafd7480")
        self.assertEqual(p["lineage"]["original_AAI11P_world_blob"],
                         "88d220e94ccf736e490f20922f1c7f5d3c1d3746")
        self.assertTrue(p["authority"]["original_models_immutable"])
        self.assertTrue(p["authority"]["no_science_first_use"])
        self.assertEqual(p["future_scientific_acceptance_contract"]["consumed"],0)
        self.assertTrue(p["no_post_result_tuning"])
        self.assertEqual(p["lineage"]["first_protocol_error"].split(":")[0],
                         "60% exact three-bit goal success impossible")

    def test_future_criteria_are_feasible_and_do_not_retroactively_modify(self):
        p=json.loads((HERE/"prereg.json").read_text("utf8"))
        g=p["future_candidate_dev_gates_frozen_now"]
        self.assertEqual(g["reward_margin_over_strongest_conventional"],.08)
        self.assertEqual(g["normalized_reachable_goal_recovery_margin_over_best_of_all_11_controls"],.05)
        self.assertEqual(g["unreachable_oracle_regret_noninferiority_max_excess_vs_strongest_reward_control"],.03)
        self.assertEqual(g["familiar_AB_reward_noninferiority_max_drop"],.03)
        self.assertEqual(g["whole_process_cost_ratio_to_fastest_matched_conventional_max"],2.)
        self.assertTrue(g["no_fixed_absolute_raw_goal_success_minimum"])
        self.assertTrue(g["all_criteria_required"])

    def test_all_eleven_strong_conventional_controls_preserved(self):
        self.assertEqual(len(admit.MATCHED),11)
        self.assertEqual(len(set(admit.MATCHED)),11)
        self.assertEqual(admit.MATCHED,(
            *controls.METHODS,"graph_recent8","graph_recent16","graph_all"))
        self.assertEqual(admit.POSTERIOR,"posterior_planner")
        self.assertNotIn(admit.POSTERIOR,admit.MATCHED)
        self.assertEqual(original_learner.CANDIDATE,"protected_graph")

    def test_reachability_oracle_ceiling_with_two_independent_methods(self):
        a=ceiling.mechanical_audit()
        self.assertEqual(a["exact_goal_attainable_episodes"],144)
        self.assertEqual(a["exact_goal_unattainable_episodes"],144)
        self.assertEqual(a["exact_goal_oracle_upper_bound"],.5)
        self.assertTrue(a["two_independent_reachability_algorithms_agree"])
        self.assertAlmostEqual(a["original_exact_two_action_oracle_mean_reward"],
                               2.448263889,places=7)

    def test_oracle_relative_denominator_and_impossible_goal_not_learner_failure(self):
        rows=[]
        for law in world.TRANSFER:
            rows.extend([
                {"law":law,"oracle_reachable":1,"oracle_reward":3.,
                 "reward":3.,"goal_correct":1,"actions":0},
                {"law":law,"oracle_reachable":0,"oracle_reward":2.,
                 "reward":1.95,"goal_correct":0,"actions":1}
            ])
        out=admit.finalize_method(rows,4,4)
        self.assertEqual(out["reachable_goals_total"],4)
        self.assertEqual(out["reachable_goals_hit"],4)
        self.assertEqual(out["oracle_normalized_reachable_goal_recovery"],1.)
        self.assertEqual(out["raw_exact_three_goal_fraction"],.5)
        self.assertAlmostEqual(out["unreachable_regret"],.05)
        self.assertAlmostEqual(out["reachable_regret"],0.)

    def test_impossible_hit_or_above_oracle_fails_closed(self):
        base=[]
        for law in world.TRANSFER:
            base.append({"law":law,"oracle_reachable":1,"oracle_reward":3.,
                         "reward":2.95,"goal_correct":1,"actions":1})
            base.append({"law":law,"oracle_reachable":0,"oracle_reward":2.,
                         "reward":2.,"goal_correct":0,"actions":0})
        with self.assertRaises(AssertionError):
            admit.finalize_method([{**row,"goal_correct":1} if i==1 else row
                                   for i,row in enumerate(base)],4,4)
        with self.assertRaises(AssertionError):
            admit.finalize_method([{**row,"reward":3.1} if i==0 else row
                                   for i,row in enumerate(base)],4,4)
        with self.assertRaises(AssertionError):
            admit.finalize_method(base,5,3)

    def test_selection_tie_is_stable_and_success_floor_is_separate(self):
        scores={"graph_all":2.,"graph_recent16":2.,"graph_recent8":2.}
        methods=("graph_recent8","graph_recent16","graph_all")
        self.assertEqual(admit.best_method(scores,methods),"graph_recent8")
        reward={"map":2.1,"recent":2.2}
        success={"map":.9,"recent":.6}
        self.assertEqual(admit.best_method(reward,("map","recent")),"recent")
        self.assertEqual(admit.best_method(success,("map","recent")),"map")

    def test_same_public_operator_evidence_for_original_map_and_posterior(self):
        recent=original_learner.GraphWindow("graph_recent8")
        posterior=calibration.PosteriorCausalModel("posterior_planner")
        for i in range(14):
            row=world.copy_public(world.start("A",world.INPUTS[i],
                                               world.GOALS[i%8]))
            recent.observe(row)
            posterior.observe(row)
        self.assertEqual(recent.rows,posterior.rows)
        self.assertEqual(recent.stats,posterior.stats)
        self.assertEqual(len(recent.rows),8)
        for x in world.INPUTS[:7]:
            probs=posterior.predict(x)
            self.assertEqual(len(probs),3)
            self.assertTrue(all(0<=p<=1 for p in probs))
        self.assertEqual(calibration.checkpoint(posterior),
                         calibration.checkpoint(calibration.restore(
                             "posterior_planner",calibration.checkpoint(posterior))))

    def test_original_contexts_and_private_fields_not_leaked(self):
        row=world.start("C",world.INPUTS[9],world.GOALS[2])
        for name,actor in (("graph_recent8",
                            original_learner.GraphWindow("graph_recent8")),
                           ("posterior_planner",
                            calibration.PosteriorCausalModel("posterior_planner"))):
            for private in ("law","oracle","counterfactual","world_id","seed"):
                with self.assertRaises(ValueError):
                    actor.observe({**row,private:"C"})
                with self.assertRaises(ValueError):
                    actor.choose({**row,private:"C"})
            self.assertEqual(len(actor.rows),0)
        for key in world.FIXTURES:
            for law in world.TRANSFER:
                orig=admission.contexts(key,law,12)
                self.assertEqual(len(orig),12)
                self.assertEqual(len(set(orig)),12)

    def test_first_use_cli_and_original_reserved_world_ids_disarmed(self):
        cmd=[sys.executable,"-B",str(HERE/"admit.py")]
        for args in (["--primary"],["--source-protocol-admission","--primary"],
                     ["--world","995000"],[]):
            result=subprocess.run(cmd+args,text=True,capture_output=True,
                                  timeout=8)
            self.assertNotEqual(result.returncode,0)
            self.assertTrue("DISARMED" in result.stderr or
                            "unrecognized arguments" in result.stderr or
                            "only three frozen" in result.stderr)
        for forbidden in (994000,995000,995063,996000,996031,"995000",
                          "mechanical:delta"):
            with self.assertRaises(PermissionError):
                world.fixture(forbidden)


if __name__=="__main__":
    unittest.main()
