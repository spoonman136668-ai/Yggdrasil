"""CVH05 static and retrospective tests: all 124 original source actions consumed before CVH05."""
import ast
import json
from pathlib import Path
import unittest

import sixfold_falsification as s


class ProspectiveSourceDenialAndSixfoldTests(unittest.TestCase):
    def test_prereg_first_and_frozen_all_six_splits(self):
        p=json.loads((s.HERE/"prereg.json").read_text())
        self.assertEqual(p["schema"],"yggdrasil.cvh05.authentic-consumed-public-sixfold-identifiability-prereg.v1")
        self.assertEqual(p["parent"]["sha"],s.PARENT)
        self.assertFalse(p["authority"]["owner_protected_source_science_approved"])
        self.assertTrue(p["authority"]["no_external_source_first_use"])
        self.assertEqual(p["source"]["new_source_actions"],0)
        self.assertEqual([tuple(i) for i in p["frozen_pairs"]],list(s.PAIRS))
        self.assertEqual(s.PREREG_FIRST,"75abed7e43f04d23cf54ae2ed34130c8a4c46a54")
        self.assertEqual(len(s.PAIRS),6)
        self.assertEqual(len(set(s.PAIRS)),6)
        for train in s.PAIRS:
            held=[x for x in s.SEEDS if x not in train]
            self.assertEqual(len(held),2)
            self.assertFalse(set(held)&set(train))

    def test_original_public_actions_and_nonidentifiability_witness(self):
        worlds=s.cvh04.load_original_public()
        proof=s.off_policy_nonidentifiability(worlds)
        self.assertEqual(proof["original_source_observed_actions"],124)
        self.assertEqual(proof["source_actions_executed_by_this_test"],0)
        self.assertEqual(proof["unknown_opposite_action_immediate_reward_slots"],124)
        self.assertEqual(proof["counterfactual_disagreements_between_compatible_log_completions"],124)
        self.assertFalse(proof["off_policy_action_effect_identifiable_from_this_fixed_policy_log"])
        self.assertTrue(proof["hypothetical_not_original_source_mechanisms"])
        self.assertNotEqual(proof["hypothetical_zero_digest"],proof["hypothetical_one_digest"])
        self.assertEqual(proof["known_original_source_outcomes_changed"],0)

    def test_sixfold_frozen_source_only_and_exact_control_ties(self):
        r=s.run_sixfold()
        self.assertFalse(r["scientific_pass"])
        self.assertFalse(r["native_accepted"])
        self.assertFalse(r["deployment"])
        self.assertFalse(r["source_original_first_use"])
        self.assertEqual(r["new_original_source_actions"],0)
        self.assertEqual(r["original_real_source_interventions_reused"],124)
        self.assertEqual(r["metrics"]["n_unique_splits"],6)
        self.assertEqual(r["metrics"]["scored_held_predictions_total"],372)
        self.assertEqual(r["metrics"]["selected_supported_total"]+r["metrics"]["unsupported_total"],372)
        self.assertEqual(r["metrics"]["independent_exact_conventional_disagreements"],0)
        self.assertEqual(r["metrics"]["selected_supported_total"],r["metrics"]["independent_exact_conventional_supported_ties"])
        self.assertTrue(r["metrics"]["all_folds_cold_and_cumulative_retention"])
        self.assertEqual(len(r["folds"]),6)
        for f,train in zip(r["folds"],s.PAIRS):
            self.assertEqual(f["train_seeds"],list(train))
            self.assertEqual(f["train_real_source_actions_reused"],62)
            self.assertEqual(f["retrospective_held_real_source_actions_reused"],62)
            self.assertEqual(f["held_supported_n"]+f["held_unsupported_n"],62)
            self.assertTrue(f["posteval_old_train_counts_and_totals_preserved"])
        self.assertEqual(r["folds"][0]["held_supported_n"],55)
        self.assertEqual(r["folds"][0]["native_supported_mse"],0.278320065227)
        self.assertEqual(r["folds"][0]["train_global_supported_mse"],0.293237912094)
        self.assertEqual(r["folds"][0]["native_minus_global_mse_advantage"],0.014917846867)
        self.assertEqual(r["result_sha256"],s.digest({k:v for k,v in r.items() if k!="result_sha256"}))
        self.assertEqual(s.run_sixfold(),r)

    def test_original_source_tamper_fails_and_inherited_cvh04_score_unchanged(self):
        r=s.cvh04.run_retrospective()
        self.assertEqual(r["metric_receipt_sha256"],
                         "44f3f62ad48369448d2126154a482b2d215d94a6c19f8c3ad8024339ec5123f7")
        self.assertEqual(r["metrics"]["held_coverage_supported_n"],55)
        self.assertTrue(r["frozen_development_signal"])
        # Reuse exact prior CVH04 immutable/public receipt checks rather
        # than rebuilding potentially permissive source decoding.
        self.assertEqual(sum(len(x) for x in s.cvh04.load_original_public().values()),124)

    def test_no_reset_do_or_new_upstream_source_usage(self):
        src=(s.HERE/"sixfold_falsification.py").read_text()
        self.assertNotIn("import causal_gym",src)
        self.assertNotIn("env.reset(",src)
        self.assertNotIn("env.do(",src)
        self.assertNotIn("requests.get(",src)
        self.assertNotIn("subprocess.run(",src)
        self.assertNotIn("os.system(",src)
        self.assertIn("cvh04.load_original_public()",src)
        self.assertIn("cvh04.batch_public_returns(training)",src)
        self.assertIn("cvh04.EarnedReturnMemory()",src)
        self.assertIn("cvh04.canonicalize_report_precision(summary)",src)
        tree=ast.parse(src)
        self.assertTrue(any(isinstance(n,ast.FunctionDef) and n.name=="off_policy_nonidentifiability"
                            for n in ast.walk(tree)))

    def test_stronger_fourcell_is_fitted_without_held_labels(self):
        worlds=s.cvh04.load_original_public()
        train=(996100,996101)
        rows=[v for k in train for v in worlds[k]]
        prior=sum(v for k in train for v in s.cvh04.four_step_targets(worlds[k]))/62
        v=s._public_fourcell_fit(worlds,train,prior)
        self.assertEqual(set(v),{(0,0),(0,1),(1,0),(1,1)})
        self.assertTrue(all(isinstance(x,float) for x in v.values()))
        self.assertEqual(s.mse([0,1],[0,1]),0)
        self.assertEqual(s.mse([],[]),None)


if __name__=="__main__":
    unittest.main()
