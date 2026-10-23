"""NLD-05 fail-closed public context formation and scientific boundary tests."""
import inspect
import json
import unittest

from context_formation import (
    SEED, FIT, EVAL, PROBES, SCORED, FIT_DIAGNOSTIC, MAX_CONTEXTS,
    NEW_CONTEXT_ERROR_THRESHOLD, ErrorContextFormer, CueNative, PUBLIC_CODES,
    public_correct, source_fit_phase_private, verify_checkpoint, run,
)


def dummy_history(correct, n=FIT_DIAGNOSTIC):
    return [{"token":f"public-{i}","sensors":[False,False,False,False],
             "action":0,"success":correct==0,"tick":i,"feedback_tick":i+2}
            for i in range(n)]


class ConstantPolicy:
    def choose(self, sensors, code):
        return 0


class NLD05Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.report=run()

    def test_existing_public_smoke_no_original_first_use(self):
        x=self.report
        self.assertEqual(x["already_exposed_public_R9_seed"],SEED)
        self.assertFalse(x["protected_first_use"])
        self.assertFalse(x["original_frozen_r9_101_211_307_run"])
        self.assertEqual(x["authenticated_ckb_scientific_admission"],"NOT_OBSERVED")
        with self.assertRaisesRegex(ValueError,"DEV_SEED_3_ONLY"):
            run(101)

    def test_exact_original_unmodified_FIT_trace_and_feedback_budget(self):
        x=self.report
        self.assertEqual(len(x["source_fit_receipts"]),2)
        self.assertTrue(all(t["legal_public_actions"]==FIT and
                            t["delayed_public_outcomes"]==FIT
                            for t in x["source_fit_receipts"]))
        self.assertEqual(set(x["public_fit_feedback_per_model"].values()),{2*FIT})
        self.assertEqual(x["public_fit_feedback_privileged_oracle"],2*FIT)
        self.assertEqual(x["public_unlabeled_phase_resets"],2)
        self.assertEqual(x["formation_diagnostic_outcome_cost_each_phase"],16)
        self.assertTrue(x["formation_offline_buffered_phase"])

    def test_contexts_created_from_prediction_errors_not_list_of_task_names(self):
        x=self.report
        self.assertLessEqual(x["native_context_slot_count"],2)
        self.assertEqual(x["native_two_slot_cap_prospectively_frozen"],MAX_CONTEXTS)
        self.assertEqual(NEW_CONTEXT_ERROR_THRESHOLD,3)
        self.assertEqual(set(x["phase_formation"]),{
            "native_dynamic","perceptron_dynamic","episodic_dynamic",
            "native_no_new_slot"})
        for runs in x["phase_formation"].values():
            self.assertEqual(len(runs),2)
            self.assertTrue(runs[0]["created"])
            self.assertEqual(runs[0]["code"],-1)
        for method in (ErrorContextFormer.form,
                       ErrorContextFormer.choose_from_public_probes):
            names=list(inspect.signature(method).parameters)
            self.assertNotIn("family",names)
            self.assertNotIn("task_id",names)

    def test_false_spawning_vs_identifiable_change_and_overflow(self):
        router=ErrorContextFormer()
        policy=ConstantPolicy()
        a=router.form(policy,dummy_history(correct=0))
        self.assertTrue(a["created"])
        b=router.form(policy,dummy_history(correct=0))
        self.assertFalse(b["created"])
        c=router.form(policy,dummy_history(correct=1))
        self.assertTrue(c["created"])
        self.assertEqual(router.codes,[-1,1])
        with self.assertRaisesRegex(ValueError,"CAPACITY_EXCEEDED"):
            router.form(policy,dummy_history(correct=1))
        blind=ErrorContextFormer(disabled_spawning=True)
        blind.form(policy,dummy_history(correct=0))
        self.assertFalse(blind.form(policy,dummy_history(correct=1))["created"])
        self.assertEqual(blind.codes,[-1])

    def test_public_delayed_token_and_selection_ambiguity(self):
        with self.assertRaisesRegex(ValueError,"NEED_EXACT_SIXTEEN"):
            ErrorContextFormer().form(ConstantPolicy(),dummy_history(0,n=8))
        x=dummy_history(0)
        x[1]["token"]=x[0]["token"]
        with self.assertRaisesRegex(ValueError,"DUPLICATE_PUBLIC_PROBE"):
            ErrorContextFormer().form(ConstantPolicy(),x)
        broken=dummy_history(0)
        broken[0]["feedback_tick"]=broken[0]["tick"]+1
        with self.assertRaisesRegex(ValueError,"OUTCOME_OR_DELAY_INVALID"):
            ErrorContextFormer().form(ConstantPolicy(),broken)
        history=dummy_history(0,n=PROBES)
        selector=ErrorContextFormer()
        selector.form(ConstantPolicy(),dummy_history(0))
        selected=selector.choose_from_public_probes(ConstantPolicy(),history)
        self.assertEqual(selected["selected_slot"],-1)
        self.assertEqual(selected["public_delayed_probes"],PROBES)

    def test_cold_policy_and_router_restoration_and_tamper_refusal(self):
        r=self.report["native_checkpoint"]
        self.assertEqual(r["cold_predictions_checked"],32)
        self.assertLess(r["policy_bytes"],32768)
        self.assertLess(r["context_bytes"],16384)
        a=ErrorContextFormer()
        a.form(ConstantPolicy(),dummy_history(correct=0))
        raw=a.save()
        self.assertEqual(ErrorContextFormer.restore(raw).save(),raw)
        changed=json.loads(raw)
        changed["payload"]["codes"]=[-1,1]
        with self.assertRaisesRegex(ValueError,"CHECKPOINT_IDENTITY"):
            ErrorContextFormer.restore(json.dumps(changed).encode())
        with self.assertRaisesRegex(ValueError,"CHECKPOINT_SIZE"):
            ErrorContextFormer.restore(b"")

    def test_eval_respects_probe_cost_and_no_oracle_as_candidate(self):
        x=self.report
        self.assertEqual(x["eval_unscored_probe_cost_each_role"],PROBES)
        self.assertEqual(set(x["evaluation"]),{"stage_0","stage_1"})
        for row in x["evaluation"].values():
            self.assertEqual(row["public_unscored_probes"],PROBES)
            self.assertEqual(row["public_scored_steps"],SCORED)
            self.assertEqual(len(row["public_delayed_history_sha256"]),64)
            scores=row["correct_scored_of_56"]
            self.assertIn("native_dynamic",scores)
            self.assertIn("perceptron_dynamic",scores)
            self.assertIn("episodic_dynamic",scores)
            self.assertIn("native_no_new_slot",scores)
            self.assertIn("oracle_known_source_context",scores)
            self.assertTrue(all(type(n) is int and 0<=n<=SCORED
                                for n in scores.values()))
            for decision in row["context_decisions"].values():
                self.assertEqual(decision["public_delayed_probes"],PROBES)
                self.assertIn(decision["selected_slot"],PUBLIC_CODES)

    def test_no_premature_claims_of_automatic_causal_abstraction(self):
        x=self.report
        self.assertEqual(x["unfamiliar_transfer"],
                         "NOT_TESTED_R9_ZERO_SHOT_NO_GO_PRESERVED")
        self.assertEqual(x["causal_composition"],
                         "NOT_TESTED_PREDEFINED_FEATURE_MAP_TWO_SLOT_LIMIT")
        self.assertFalse(x["per_model_cpu_rss_parity"])
        self.assertEqual(x["native_better_than_trained_conventional"],"NOT_PRESUMED")
        self.assertEqual(x["disposition"],
            "NLD05_REUSED_PUBLIC_DEV_ERROR_FORMED_CONTEXT_RECORD_ALL_NEGATIVES")


if __name__=="__main__":
    unittest.main()
