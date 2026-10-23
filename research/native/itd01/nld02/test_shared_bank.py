"""NLD-02 fails closed on original-source aliases and state/feedback corruption."""
import inspect
import json
import unittest
from shared_bank import (
    SharedLocalCells, SharedPerceptron, SharedEpisodic, ConstantZero,
    FIT, EVAL, SEED, PATTERNS, SCHEMA, alias_certificate, checkpoint,
    fit_public, score_public, run,
)


class SharedBankTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.report=run()

    def test_existing_source_only_not_h1h2_or_r9_first_use(self):
        x=self.report
        self.assertEqual(x["schema"], SCHEMA)
        self.assertEqual(x["only_reused_development_smoke_seed"],3)
        self.assertFalse(x["original_r9_101_211_307_reused"])
        self.assertFalse(x["scientific_first_use"])
        self.assertEqual(x["ckb_admission"],"NOT_OBSERVED")
        self.assertEqual(x["source_first_use"],"PREVIOUSLY_EXPOSED_PUBLIC_R9_SMOKE")
        with self.assertRaisesRegex(ValueError,"ONLY_PRIOR_PUBLIC_SEED"):
            run(101)

    def test_genuinely_one_shared_bank_and_no_public_family_input(self):
        native=SharedLocalCells()
        self.assertEqual(len(native.cells),10)
        self.assertFalse(hasattr(native,"family_banks"))
        for fn in (native.choose,native.observe_public_action,native.learn_delayed):
            self.assertNotIn("family",inspect.signature(fn).parameters)
        self.assertFalse(self.report["native_input_has_family_or_task_identity"])
        self.assertEqual(self.report["active_native_cell_banks"],1)

    def test_original_public_causal_alias_is_inherent(self):
        a=alias_certificate()
        self.assertEqual(a["public_four_bit_patterns"],16)
        self.assertEqual(a["different_A_B_action_targets_without_task_cue"],8)
        self.assertEqual(a["max_joint_correct_on_balanced_uniform_A_B"],.75)
        self.assertFalse(a["target_rule_visible_to_learner"])
        self.assertEqual(len(PATTERNS),16)

    def test_delayed_feedback_and_token_identity_refused(self):
        m=SharedLocalCells()
        sensors=(True,False,False,True)
        snap=m.save()
        with self.assertRaisesRegex(ValueError,"FEEDBACK_MISSING"):
            m.learn_delayed("unknown",True,2)
        m.observe_public_action("a",sensors,0,0)
        with self.assertRaisesRegex(ValueError,"DUPLICATE"):
            m.observe_public_action("a",sensors,0,0)
        with self.assertRaisesRegex(ValueError,"PENDING"):
            m.save()
        with self.assertRaisesRegex(ValueError,"EARLY_OR_LATE"):
            m.learn_delayed("a",False,1)
        self.assertEqual(m.feedback_updates,0)
        m.learn_delayed("a",False,2)
        self.assertNotEqual(snap,m.save())
        self.assertEqual(m.feedback_updates,1)
        with self.assertRaisesRegex(ValueError,"MISSING"):
            m.learn_delayed("a",True,2)

    def test_equal_public_fit_and_state_change_observable(self):
        x=self.report
        self.assertEqual([p["public_actions"] for p in x["public_fitting"]],[FIT,FIT])
        self.assertEqual([p["delayed_feedback"] for p in x["public_fitting"]],[FIT,FIT])
        self.assertEqual(set(x["feedback_updates_per_arm"].values()),{2*FIT})
        self.assertEqual(set(x["feedback_updates_per_arm"]),{
            "shared-native-ten-cell","trained-shared-pairwise-perceptron",
            "trained-shared-episodic-action-memory"})
        self.assertGreaterEqual(x["native_actual_weight_changes"],0)
        self.assertEqual(x["cold_after_a"]["matching_16_public_decisions"],16)
        self.assertEqual(x["cold_after_b"]["matching_16_public_decisions"],16)

    def test_read_only_public_scoring_and_equal_baseline_information(self):
        x=self.report
        self.assertEqual(set(x["views"]),{"a_pre","a_post","a_after_b","b_post"})
        for k,view in x["views"].items():
            self.assertEqual(view["n"],EVAL)
            self.assertFalse(view["family_label_given_to_learner"])
            self.assertTrue(view["no_model_updates_on_score"])
            self.assertEqual(set(view["accuracy"]),{
                "shared-native-ten-cell","trained-shared-pairwise-perceptron",
                "trained-shared-episodic-action-memory",
                "untrained-current-only-zero","erased-native-state"})
            self.assertTrue(all(0<=v<=1 for v in view["accuracy"].values()))
            self.assertGreaterEqual(view["native_vs_erased_action_disagreements"],0)

    def test_checkpoint_sha_and_tamper_refusal(self):
        m=SharedLocalCells()
        fit_public([m],"A")
        ck=checkpoint(m)
        self.assertTrue(ck["cold_restore_exact"])
        self.assertLess(ck["bytes"],32768)
        raw=m.save()
        obj=json.loads(raw)
        obj["payload"]["cells"][0]["fast"]+=1
        with self.assertRaisesRegex(ValueError,"CHECKPOINT_HASH"):
            SharedLocalCells.restore(json.dumps(obj).encode())
        with self.assertRaisesRegex(ValueError,"CHECKPOINT_SIZE"):
            SharedLocalCells.restore(b"")

    def test_reporting_does_not_conflate_interference_and_information_gap(self):
        x=self.report
        self.assertEqual(x["causal_composition"],"NOT_TESTED_HANDDESIGNED_PAIR_FEATURES")
        self.assertEqual(x["unfamiliar_transfer"],"NOT_TESTED_ORIGINAL_R9_ZERO_SHOT_NO_GO")
        self.assertFalse(x["matched_per_model_resource_costs"])
        self.assertEqual(x["disposition"],
            "NLD02_SHARED_BANK_EXISTING_SOURCE_DEV_DIAGNOSTIC_RETAIN_ALL_RESULTS")
        self.assertEqual(x["known_source_alias_certificate"][
            "causal_identifiability_without_task_cue"],"ALIASED_FOR_SIMULTANEOUS_A_B")
        self.assertIn("a_after_b_minus_a_after_fit",x["contrasts"])


if __name__=="__main__":
    unittest.main()
