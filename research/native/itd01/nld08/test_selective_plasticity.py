"""NLD08: selective prequential plasticity and exact source/accounting tests."""
import json
import unittest
from selective_plasticity import (
    CueNative,CuePerceptron,CueEpisodic,Detector,
    SelectivePlasticityGate,consume_public_feedback_without_plasticity,
    GATE_ERROR_THRESHOLD,DETECTOR_WARMUP,DIAGNOSTIC_GLOBAL_FEEDBACK_TICKS,
    SEED,FIT,TOTAL,DELAY,run
)

class SelectivePlasticityTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.x=run()

    def test_custody_source_and_original_negative_unchanged(self):
        x=self.x
        self.assertEqual(x["previously_exposed_public_dev_seed"],3)
        self.assertFalse(x["protected_first_use"])
        self.assertFalse(x["original_r9_science_seeds_101_211_307_used"])
        self.assertEqual(x["ckb_scientific_admission"],"NOT_OBSERVED")
        self.assertFalse(x["source_reset_visible_to_learners"])
        with self.assertRaisesRegex(ValueError,"ALREADY_EXPOSED_PUBLIC_SEED3"):
            run(101)

    def test_prespecified_gate_uses_only_prior_errors_and_existing_context(self):
        gate=SelectivePlasticityGate(True)
        router=Detector()
        router.errors=[1,1,1]
        router.feedback_count=63
        self.assertFalse(gate.decision(router))
        router.feedback_count=64
        self.assertTrue(gate.decision(router))
        router.errors=[1,0,1,0]
        self.assertFalse(gate.decision(router))
        router.errors=[1,1,1]
        router.codes=[-1,1]
        router.active=1
        self.assertFalse(gate.decision(router))
        self.assertFalse(SelectivePlasticityGate(False).decision(router))
        self.assertEqual((GATE_ERROR_THRESHOLD,DETECTOR_WARMUP),(3,64))
        with self.assertRaises(ValueError):
            SelectivePlasticityGate(1)

    def test_skipping_weights_consumes_true_feedback_and_exact_pending_event(self):
        sensors=(True,False,True,False)
        event={"token":"PUB-000","tick":0,"feedback_tick":2,
               "sensors":sensors,"action":0,"success":True}
        for model in (CueNative(True),CuePerceptron(True),CueEpisodic(True)):
            before=model.save()
            model.observe_public_action("PUB-000",sensors,-1,0,0)
            public_before=model.feedback_updates
            consume_public_feedback_without_plasticity(model,event,2)
            self.assertEqual(model.feedback_updates,public_before+1)
            self.assertNotIn("PUB-000",model.pending)
            self.assertNotEqual(before,model.save())  # receipt count changed
            with self.assertRaisesRegex(ValueError,"MISSING"):
                consume_public_feedback_without_plasticity(model,event,2)
            model.observe_public_action("PUB-001",sensors,-1,0,4)
            early=dict(event,token="PUB-001",tick=4,feedback_tick=5)
            with self.assertRaisesRegex(ValueError,"CAUSAL"):
                consume_public_feedback_without_plasticity(model,early,5)
            self.assertIn("PUB-001",model.pending)

    def test_all_fitted_models_receive_256_authentic_outcomes(self):
        x=self.x
        self.assertEqual(x["source_actions_received"],256)
        self.assertEqual(set(x["actual_public_feedback_events_received_each_arm"].values()),
                         {256})
        self.assertEqual(len(x["actual_public_feedback_events_received_each_arm"]),7)
        self.assertEqual([r["legal_public_actions"]
                          for r in x["original_private_source_receipts"]],[FIT,FIT])
        self.assertEqual([r["delayed_public_outcomes"]
                          for r in x["original_private_source_receipts"]],[FIT,FIT])
        for name,v in x["applied_public_feedback_updates_each_arm"].items():
            self.assertEqual(v+x["gates"][name]["suppressed_plastic_updates"],TOTAL)

    def test_original_nld06_unmodified_negative_reproduced(self):
        x=self.x
        a=x["a_retained_after_b"]["routed_correct_of_56"]
        b=x["b_post_learning"]["routed_correct_of_56"]
        self.assertEqual(a["native_baseline"],48)
        self.assertEqual(a["perceptron_baseline"],48)
        self.assertEqual(a["native_never_switch"],33)
        self.assertEqual(b["native_baseline"],56)
        self.assertEqual(x["alarms"]["native_baseline"][0]["feedback_tick"],140)

    def test_early_gate_cost_and_no_extra_snapshot_storage(self):
        x=self.x
        self.assertEqual(x["native_gate_extra_parameter_snapshot_buffer_bytes"],0)
        self.assertEqual(x["original_nld07_rollback_peak_extra_native_snapshot_bytes_reference"],
                         18702)
        for candidate in ("native_gate","perceptron_gate","episodic_gate"):
            gate=x["gates"][candidate]
            self.assertTrue(gate["enabled"])
            self.assertGreaterEqual(gate["suppressed_plastic_updates"],0)
            self.assertLessEqual(gate["suppressed_plastic_updates"],TOTAL)
            self.assertGreater(gate["serialized_gate_bytes"],0)
        for other in ("native_baseline","native_never_switch",
                      "perceptron_baseline","episodic_baseline"):
            self.assertFalse(x["gates"][other]["enabled"])
            self.assertEqual(x["gates"][other]["suppressed_plastic_updates"],0)

    def test_forensic_private_attribution_and_readonly_evaluation(self):
        x=self.x
        self.assertEqual(x["private_forensic_reference_feedback_ticks"],
                         list(DIAGNOSTIC_GLOBAL_FEEDBACK_TICKS))
        self.assertEqual(set(x["private_readonly_16_pattern_attribution"]),
                         {"129","140","257"})
        for phase in x["private_readonly_16_pattern_attribution"].values():
            self.assertEqual(set(phase),set(x["gates"]))
            for pattern_accuracy in phase.values():
                self.assertEqual(set(pattern_accuracy),
                                 {"A_-1","A_1","B_-1","B_1"})
                self.assertTrue(all(0<=v<=16 for v in pattern_accuracy.values()))
        for phase in (x["a_retained_after_b"],x["b_post_learning"]):
            self.assertTrue(phase["no_fitting_during_scoring"])
            self.assertEqual(phase["public_unscored_delayed_probes"],8)
            self.assertEqual(phase["scored_observations"],56)
            self.assertEqual(set(phase["public_probe_context_decisions"]),set(x["gates"]))
            self.assertEqual(set(phase["oracle_task_slot_correct_of_56_evaluator_only"]),
                             set(x["gates"]))
        self.assertEqual(x["native_gate_checkpoint"]["matching_cold_public_predictions"],32)

    def test_negative_retention_and_equality_not_premature_causal_transfer(self):
        x=self.x
        self.assertEqual(x["novel_causal_composition"],"NOT_TESTED")
        self.assertEqual(x["unfamiliar_source_transfer"],
                         "NOT_TESTED_R9_C_NEGATIVE_PRESERVED")
        self.assertFalse(x["isolated_model_cpu_rss_parity"])
        self.assertEqual(x["disposition"],
                         "NLD08_PUBLIC_DEV_EARLY_PLASTICITY_GATE_RETAIN_ALL_OUTCOMES")

if __name__=="__main__":
    unittest.main()
