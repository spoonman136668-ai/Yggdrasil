"""F48 immutable prereg, consequential intervention and Bayesian control tests."""
import json
from pathlib import Path
import tempfile
import unittest

from f48_counterfactual_witness_dev import (
    PREREG, HYPOTHESES, SEEDS, BUDGETS, POLICIES, N_ACTIONS,
    F48Rejected, freeze, consequence, candidate_table, HiddenWorld,
    MismatchWeights, ActiveArm, run_one, run,
)


class TestF48CausalMechanisms(unittest.TestCase):
    def test_frozen_protocol_precedes_code_worlds_and_deployment(self):
        p=freeze()
        self.assertEqual(p["status"],"FROZEN_PRE_CODE_PRE_WORLD_OUTCOMES")
        self.assertEqual(p["source_parent"],
                         "5d9f930317905e61751ebff62e1b650dcb234011")
        self.assertEqual(p["worlds"]["hypothesis_counts_high_first"],[256,128,64])
        self.assertEqual(p["worlds"]["fixed_development_seeds"],[149,151,157])
        self.assertEqual(p["worlds"]["budgets_high_first"],[32,16,8])
        self.assertTrue(all(p["safety"].values()))

    def test_threshold_tamper_rejected_without_source_write(self):
        original=PREREG.read_bytes()
        p=json.loads(original)
        p["frozen_metrics"]["positive_criteria"][
            "b16_native_unseen_accuracy_gain_vs_bayes_min"]=0
        with tempfile.TemporaryDirectory() as td:
            path=Path(td)/"tampered.json"
            path.write_text(json.dumps(p),encoding="utf-8")
            with self.assertRaisesRegex(F48Rejected,"FROZEN_PREREG_BLOB_CHANGED"):
                freeze(path)
        self.assertEqual(PREREG.read_bytes(),original)

    def test_all_candidate_two_stage_laws_identifiable_and_onehot_code(self):
        for count in HYPOTHESES:
            table=candidate_table(count)
            self.assertEqual(len(table),count)
            self.assertEqual(len(set(table)),count)
            for h in range(count):
                self.assertEqual(len(table[h]),256)
                self.assertTrue(all(x in (0,1) for x in table[h]))
                for b in range(8):
                    # Hash-gate nonlinear terms vanish for single-bit actions.
                    self.assertEqual(table[h][1<<b],(h>>b)&1)
                self.assertEqual(table[h][255],consequence(h,255))

    def test_world_public_interventions_and_negative_dimensions(self):
        for count in HYPOTHESES:
            for seed in SEEDS:
                a,b=HiddenWorld(count,seed),HiddenWorld(count,seed)
                self.assertEqual(a.evaluator_truth_only(),b.evaluator_truth_only())
                self.assertEqual(a.intervene(16,0),b.intervene(16,0))
                self.assertIn(a.intervene(255,0),(0,1))
        for count,seed in ((512,149),(32,149),(256,139),(256,True)):
            with self.subTest(count=count,seed=seed),self.assertRaises(
                    F48Rejected):
                HiddenWorld(count,seed)
        w=HiddenWorld(64,149)
        for action,rep in ((256,0),(-1,0),(0,33),(0,-1),(True,0)):
            with self.subTest(action=action,rep=rep),self.assertRaisesRegex(
                    F48Rejected,"PUBLIC_INTERVENTION_OUT_OF_SCOPE"):
                w.intervene(action,rep)

    def test_local_weight_programming_and_fully_fitted_posterior(self):
        w=HiddenWorld(64,149)
        model=MismatchWeights(64)
        for action in (1,2,4,8,16,32,64,128):
            model.observe(action,w.intervene(action,0))
        self.assertEqual(model.total,8)
        self.assertEqual(sum(model.action_seen),8)
        self.assertEqual(model.mismatch[model.map_id()],min(model.mismatch))
        self.assertAlmostEqual(sum(model.weights()),1)
        saved=model.checkpoint()
        self.assertEqual(saved,MismatchWeights.restore(saved).checkpoint())
        self.assertEqual(model.map_id(),MismatchWeights.restore(saved).map_id())

    def test_bad_observation_checkpoint_corruption_and_budget_enforcement(self):
        w=HiddenWorld(64,151)
        m=MismatchWeights(64)
        for a,y in ((-1,0),(256,0),(0,2),(0,True),(0,-1)):
            with self.subTest(a=a,y=y),self.assertRaisesRegex(
                    F48Rejected,"UNTRUSTED_OR_EXCESS_OBSERVATION"):
                m.observe(a,y)
        self.assertEqual(m.total,0)
        m.observe(0,w.intervene(0,0))
        snapshot=m.checkpoint()
        for corrupt in (snapshot[:-1],snapshot+b"\x00",
                        snapshot[:-1]+bytes((snapshot[-1]^1,)),
                        bytes((snapshot[0]^1,))+snapshot[1:]):
            with self.assertRaises(F48Rejected):
                MismatchWeights.restore(corrupt)
        self.assertEqual(m.checkpoint(),snapshot)

    def test_bayesian_ig_choice_is_exact_posterior_balance(self):
        a=ActiveArm("bayes_information_gain",64,149)
        choices=a.model.table
        # Under uniform prior select action with the most balanced predicted bit
        # counts; reproducible deterministic tie resolution.
        counts=[sum(row[action] for row in choices) for action in range(256)]
        best=min(range(256),key=lambda act:abs(2*counts[act]-64))
        self.assertEqual(a.select(),best)
        self.assertEqual(a.prediction_accesses,64*256)

    def test_witness_selection_differs_from_exact_information_gain(self):
        witness=ActiveArm("native_witness",256,151)
        bayes=ActiveArm("bayes_information_gain",256,151)
        self.assertEqual(witness.prediction_accesses,0)
        first_w=witness.select()
        first_b=bayes.select()
        self.assertIn(first_w,range(256))
        self.assertIn(first_b,range(256))
        self.assertEqual(witness.prediction_accesses,4*256)
        self.assertEqual(bayes.prediction_accesses,256*256)
        self.assertLess(witness.prediction_accesses,bayes.prediction_accesses)

    def test_actual_action_budget_and_cold_control_at_every_prefix(self):
        worlds=run_one(64,149)
        self.assertEqual([row["action_budget"] for row in worlds],[32,16,8])
        for row in worlds:
            self.assertEqual(set(row["arms"]),set(POLICIES))
            for v in row["arms"].values():
                self.assertEqual(v["total_real_action_observations"],row["action_budget"])
                self.assertEqual(v["public_observed_outcome_bits"],row["action_budget"])
                self.assertGreaterEqual(v["unqueried_action_count"],224)
                self.assertTrue(v["cold_restore_prediction_exact"])
                self.assertTrue(v["tamper_rejected"])
                self.assertTrue(v["isolated_clone_public_update_unchanged_original"])
                self.assertEqual(v["isolated_control_extra_public_actions"],1)
                self.assertEqual(v["isolated_control_extra_public_outcome_bits"],1)
                self.assertTrue(0<=v["heldout_counterfactual_MAP_accuracy"]<=1)
            self.assertEqual(row["observed_public_outcomes_per_arm"],row["action_budget"])

    def test_full_frozen_study_and_science_fences(self):
        d=run()
        self.assertEqual(d["hypothesis_counts_high_first"],[256,128,64])
        self.assertEqual(d["seeds"],[149,151,157])
        self.assertEqual(d["budgets_high_first"],[32,16,8])
        self.assertEqual(len(d["world_results"]),27)
        self.assertTrue(d["cold_and_tamper_all"])
        self.assertTrue(d["action_budgets_equal"])
        self.assertLessEqual(
            d["native_b16_prediction_accesses"]/d["bayes_b16_prediction_accesses"],0.50)
        self.assertIn(d["classification"],
                      ("DEV_COUNTERFACTUAL_WITNESS_GO","DEV_COUNTERFACTUAL_WITNESS_NO_GO"))
        for key in ("protected_first_use","accepted_native_Yggdrasil_model_edited",
                    "scientific_pass","deployed"):
            self.assertIs(d[key],False)


if __name__=="__main__":
    unittest.main()
