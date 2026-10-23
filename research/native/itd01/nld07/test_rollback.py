"""NLD07: verify exact NLD06 baseline, controlled state rollback and costs."""
import unittest
from rollback import (
    SEED,ROLLBACK_WINDOW,DIAGNOSTIC_GLOBAL_FEEDBACK_TICKS,learned_snapshot,
    restore_learned_only,CueNative,CuePerceptron,CueEpisodic,run
)

class NLD07Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.x=run()

    def test_dev_only_and_original_nld06_immutable(self):
        x=self.x
        self.assertEqual(x["source_free_old_dev_seed"],3)
        self.assertFalse(x["protected_first_use"])
        self.assertFalse(x["original_scientific_r9_101_211_307_replayed"])
        self.assertEqual(x["authenticated_ckb_scientific_admission"],"NOT_OBSERVED")
        self.assertEqual(x["original_nld06_head"],
                         "95ccf52bfe4207d22dbe0cd22369ec3c1447740e")
        with self.assertRaisesRegex(ValueError,"PRIOR_PUBLIC_SMOKE_SEED3"):
            run(101)

    def test_original_native_and_perceptron_negative_reproduced(self):
        x=self.x
        a=x["score_A_retained_after_B"]["routed_correct_of_56"]
        b=x["score_B"]["routed_correct_of_56"]
        self.assertEqual(a["native_baseline"],48)
        self.assertEqual(a["native_never_switch"],33)
        self.assertEqual(a["perceptron_baseline"],48)
        self.assertEqual(b["native_baseline"],56)
        self.assertEqual(x["detector_alarms"]["native_baseline"][0]["feedback_tick"],140)

    def test_equal_public_interventions_and_causal_clock(self):
        x=self.x
        self.assertEqual(x["uninterrupted_public_actions"],256)
        self.assertEqual(x["all_models_feedback_events_delivered"],256)
        self.assertEqual(set(x["learned_public_feedback_counts"].values()),{256})
        self.assertTrue(x["no_phase_reset_received_by_models"])
        self.assertEqual([d["legal_public_actions"] for d in x["original_source_receipts"]],
                         [128,128])
        self.assertEqual([d["delayed_public_outcomes"] for d in x["original_source_receipts"]],
                         [128,128])

    def test_fixed_private_attribution_without_new_source_draws(self):
        x=self.x
        self.assertEqual(x["forensic_private_feedback_ticks"],
                         list(DIAGNOSTIC_GLOBAL_FEEDBACK_TICKS))
        self.assertEqual(set(x["private_full_16_pattern_forensic_accuracy"]),
                         {"129","140","257"})
        for role in x["private_full_16_pattern_forensic_accuracy"].values():
            self.assertEqual(set(role),
               set(x["learned_public_feedback_counts"]))
            for item in role.values():
                self.assertEqual(set(item),{"A_-1","A_1","B_-1","B_1"})
                self.assertTrue(all(type(n) is int and 0<=n<=16
                                    for n in item.values()))

    def test_explicit_parameter_only_rollback_does_not_refund_feedback(self):
        m=CueNative(True)
        state=learned_snapshot(m)
        m.bias=1.0
        m.feedback_updates=17
        m.pending["held"]=(tuple([False]*4),-1,0,3)
        restore_learned_only(m,state)
        self.assertEqual(m.bias,0.0)
        self.assertEqual(m.feedback_updates,17)
        self.assertIn("held",m.pending)
        for model in (CuePerceptron(True),CueEpisodic(True)):
            state=learned_snapshot(model)
            model.feedback_updates=11
            model.pending["p"]=(tuple([False]*4),-1,0,0)
            restore_learned_only(model,state)
            self.assertEqual(model.feedback_updates,11)
            self.assertIn("p",model.pending)

    def test_sixteen_feedback_snapshots_and_per_model_cost(self):
        x=self.x
        self.assertEqual(ROLLBACK_WINDOW,16)
        rolls=x["retrospective_parameter_rollbacks"]
        for name in ("native_rollback","perceptron_rollback"):
            self.assertEqual(len(rolls[name]),1)
            self.assertEqual(rolls[name][0]["rolled_back_parameter_updates"],16)
            self.assertEqual(rolls[name][0]["trigger_feedback_tick"],140)
            self.assertEqual(rolls[name][0]["feedback_events_still_received"],139)
            self.assertGreater(x["extra_16_snapshot_ring_peak_bytes"][name],0)
        self.assertIn("episodic_rollback",rolls)
        self.assertEqual(x["extra_16_snapshot_ring_peak_bytes"]["episodic_rollback"]>0,True)

    def test_read_only_evaluator_separates_route_from_memory(self):
        x=self.x
        for role in (x["score_A_retained_after_B"],x["score_B"]):
            self.assertEqual(role["public_unscored_delayed_probes"],8)
            self.assertEqual(role["scored_observations"],56)
            self.assertTrue(role["no_fitting_during_scoring"])
            self.assertEqual(set(role["public_probe_context_decisions"]),
                             set(x["learned_public_feedback_counts"]))
            self.assertEqual(set(role["oracle_task_slot_correct_of_56_evaluator_only"]),
                             set(x["learned_public_feedback_counts"]))
            self.assertTrue(all(0<=v<=56 for v in role["routed_correct_of_56"].values()))
        self.assertEqual(x["native_cold_predictions_verified"],32)

    def test_preserve_negative_and_no_efficiency_or_transfer_claim(self):
        x=self.x
        self.assertEqual(x["unfamiliar_transfer"],
                         "NOT_TESTED_OLD_R9_C_ZERO_SHOT_NO_GO")
        self.assertFalse(x["per_model_cpu_rss_efficiency_claim"])
        self.assertEqual(x["causal_composition"],"NOT_TESTED")
        self.assertEqual(x["disposition"],
            "NLD07_EXISTING_PUBLIC_SOURCE_ROLLBACK_ABLATION_RETAIN_ALL_POSITIVES_AND_NEGATIVES")

if __name__=="__main__":
    unittest.main()
