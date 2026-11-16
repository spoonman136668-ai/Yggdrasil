"""Negative-only F50 numeric-envelope tests with FABRICATED reports.

No real evaluator, source model, development or protected cohort is opened.
Fake high scores are a parsing-test fixture, never F50 scientific evidence.
"""
import copy
import unittest

import f50_development_numeric_audit as audit
import f50_comparison_harness as harness


def fabricated_report():
    arms=[]
    for size,seed in harness.frozen_plan():
        for kind in harness.KINDS:
            if kind=="native":
                base=.82
            elif kind in harness.TRAINED_SOURCE_KINDS:
                base=.69
            elif kind in ("exact_source_bank_bayes","compositional_grammar_bayes"):
                base=.70
            elif kind in ("random","uniform"):
                base=.64
            else:
                base=.58
            arms.append({
                "schema":harness.SCHEMA,"size":size,"seed":seed,"arm":kind,
                "checkpoints":[{"budget":budget,
                                "clean_heldout_accuracy":base,
                                "cold_sha256":"a"*64}
                               for budget in harness.CHECKPOINTS],
                "observed_public_bits":192,"public_events":64,
                "proposals":(64*2048 if kind=="native"
                              or kind=="compositional_grammar_bayes"
                              or kind in harness.KINDS[8:] else 0),
                "prediction_accesses":1536,"target_cpu_seconds":100.0,
                "cold_restores":3,"fixture_only":False,
                "scientific_pass":False,
                "classification":"DEV_F50_UNCLASSIFIED"
            })
    return {"schema":harness.SCHEMA,
            "classification":"DEV_F50_UNCLASSIFIED",
            "world_count":9,"arms_per_world":12,
            "worlds":[list(x) for x in harness.frozen_plan()],
            "arm_runs":arms,
            "development_outcomes_consumed":9*12*64*3,
            "protected_cohorts_consumed":0,
            "scientific_pass":False,
            "independent_classification_required":True}


class NumericEnvelopeTests(unittest.TestCase):
    def test_all_fake_thresholds_never_become_scientific_pass(self):
        r=audit.audit_numeric_envelope(fabricated_report())
        self.assertEqual(r["world_arm_rows"],108)
        self.assertEqual(r["numeric_diagnostic"],
                         "NUMERIC_THRESHOLDS_MET_CUSTODY_AND_COST_UNVERIFIED")
        self.assertEqual(r["native_b32_mean"],"0.82")
        self.assertEqual(r["best_control_kind"],"exact_source_bank_bayes")
        self.assertFalse(r["scientific_pass"])
        self.assertFalse(r["total_process_cpu_cost_verified"])

    def test_incomplete_duplicate_fixture_and_wrong_proposal_fail_closed(self):
        raw=fabricated_report()
        for field,bad in (("arm_runs",raw["arm_runs"][:-1]),
                          ("development_outcomes_consumed",0),
                          ("classification","DEV_F50_GO"),
                          ("protected_cohorts_consumed",1)):
            r=copy.deepcopy(raw)
            r[field]=bad
            with self.assertRaises(audit.NumericAuditRejected):
                audit.audit_numeric_envelope(r)
        r=copy.deepcopy(raw)
        r["arm_runs"][1]["arm"]="native"
        with self.assertRaisesRegex(audit.NumericAuditRejected,
                                    "NONDEVELOPMENT_OR_INCOMPLETE_RUN"):
            audit.audit_numeric_envelope(r)
        r=copy.deepcopy(raw)
        r["arm_runs"][0]["fixture_only"]=True
        with self.assertRaises(audit.NumericAuditRejected):
            audit.audit_numeric_envelope(r)
        r=copy.deepcopy(raw)
        r["arm_runs"][0]["proposals"]=0
        with self.assertRaisesRegex(audit.NumericAuditRejected,"PROPOSAL_BUDGET"):
            audit.audit_numeric_envelope(r)
        r=copy.deepcopy(raw)
        r["arm_runs"][0]["checkpoints"][1]["clean_heldout_accuracy"]=float("nan")
        with self.assertRaises(audit.NumericAuditRejected):
            audit.audit_numeric_envelope(r)

    def test_margins_negatives_and_resource_stop_never_imply_go(self):
        r=fabricated_report()
        r["arm_runs"][0]["checkpoints"][1]["clean_heldout_accuracy"]=0.70
        x=audit.audit_numeric_envelope(r)
        self.assertEqual(x["numeric_diagnostic"],
                         "NUMERIC_THRESHOLDS_MET_CUSTODY_AND_COST_UNVERIFIED")
        self.assertEqual(x["world_b32_gaps"]["4096_4013"],"0.0")
        self.assertEqual(x["family_b32_gaps"]["4013"],"0.08")
        self.assertFalse(x["scientific_pass"])
        r=fabricated_report()
        r["arm_runs"][0]["target_cpu_seconds"]=1200.001
        self.assertEqual(audit.audit_numeric_envelope(r)["numeric_diagnostic"],
                         "RESOURCE_STOP")
        r=fabricated_report()
        for row in r["arm_runs"]:
            if row["arm"] in harness.TRAINED_SOURCE_KINDS:
                row["checkpoints"][1]["clean_heldout_accuracy"]=0.54
        self.assertEqual(audit.audit_numeric_envelope(r)["numeric_diagnostic"],
                         "TASK_HEADROOM_INVALID")

    def test_aggregate_each_family_over_all_three_source_bank_sizes(self):
        report=fabricated_report()
        # One world at 0 gap, two at +0.12. Family mean +0.08
        # must pass the frozen +0.02 aggregate threshold.
        report["arm_runs"][0]["checkpoints"][1]["clean_heldout_accuracy"]=0.70
        x=audit.audit_numeric_envelope(report)
        self.assertNotIn("FAMILY_B32_GAP_4013",x["numeric_reasons"])
        self.assertEqual(x["family_b32_gaps"]["4013"],"0.08")
        self.assertFalse(x["scientific_pass"])
        # All three bank sizes miss in one unseen family -> numeric NO_GO.
        for row in report["arm_runs"]:
            if row["seed"]==4013 and row["arm"]=="native":
                row["checkpoints"][1]["clean_heldout_accuracy"]=0.70
        fail=audit.audit_numeric_envelope(report)
        self.assertEqual(fail["numeric_diagnostic"],"NUMERIC_THRESHOLDS_NO_GO")
        self.assertIn("FAMILY_B32_GAP_4013",fail["numeric_reasons"])
        self.assertFalse(fail["scientific_pass"])

    def test_no_hidden_target_or_authority_imports(self):
        self.assertNotIn("PrivateTargetEvaluator",audit.__dict__)
        self.assertNotIn("DevelopmentEvaluatorClient",audit.__dict__)
        self.assertNotIn("open_development",audit.__dict__)


if __name__=="__main__":
    unittest.main()
