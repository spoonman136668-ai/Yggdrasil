"""Empirical source-memory evidence, matched controls and unfamiliar negatives."""
import unittest
from empirical_probe_audit import run,trial
from empirical_local_probe import EmpiricalLocalProbe
from conventional_empirical_probe import ConventionalEmpiricalProbe
from unrestricted_operation_cells import INPUTS

class EmpiricalProbeTests(unittest.TestCase):
    def test_complete_source_evidence_required(self):
        native=EmpiricalLocalProbe()
        control=ConventionalEmpiricalProbe()
        for learner in (native,control):
            with self.assertRaises(ValueError):
                learner.close_source()
            with self.assertRaises(ValueError):
                learner.begin_target()
            learner.observe_source(INPUTS[0],False)
            with self.assertRaises(ValueError):
                learner.close_source()

    def test_exhaustive_evidence_parity_and_budget(self):
        cases=run()["cases"]
        self.assertEqual(len(cases),16)
        self.assertEqual(sum(r["source_member_diagnostic"] for r in cases),4)
        for row in cases:
            self.assertEqual(row["source_public_observations_per_arm"],32)
            for stage in row["stages"]:
                n=stage["round"]
                for arm,result in stage["scores"].items():
                    self.assertEqual(sum(result[k] for k in ("correct","wrong","abstentions")),4-len(stage["public_probe_paths"][arm]))
                    self.assertEqual(result["unseen"],4-len(stage["public_probe_paths"][arm]))
                    self.assertEqual(stage["target_actions"][arm],len(stage["public_probe_paths"][arm]))
                    self.assertLessEqual(stage["target_actions"][arm],n)
                    self.assertGreaterEqual(row["cpu_ns"][arm],0)
                self.assertEqual(stage["scores"]["local_active"],stage["scores"]["control_active"])
                self.assertEqual(stage["scores"]["local_fixed"],stage["scores"]["control_fixed"])
                self.assertEqual(stage["candidate_counts"]["local_active"],stage["candidate_counts"]["control_active"])
                self.assertEqual(stage["public_probe_paths"]["local_active"],stage["public_probe_paths"]["control_active"])

    def test_target_identity_not_passed_as_candidate_set(self):
        for target in range(16):
            row=trial(target)
            self.assertEqual(row["source_public_observations_per_arm"],32)
            self.assertEqual(row["stages"][0]["public_probe_paths"]["local_active"],
                             [[False,True]])
        with self.assertRaises(ValueError):
            trial(16)

    def test_unfamiliar_source_memory_is_not_a_safe_transfer_claim(self):
        rows=run()["cases"]
        familiar=[r for r in rows if r["source_member_diagnostic"]]
        unfamiliar=[r for r in rows if not r["source_member_diagnostic"]]
        def aggregate(group,arm,key):
            return sum(r["stages"][1]["scores"][arm][key] for r in group)
        self.assertEqual((aggregate(familiar,"local_active","correct"),
                          aggregate(familiar,"local_active","wrong")),(8,0))
        self.assertEqual((aggregate(unfamiliar,"local_active","correct"),
                          aggregate(unfamiliar,"local_active","wrong")),(8,16))
        self.assertEqual((aggregate(unfamiliar,"local_fixed","correct"),
                          aggregate(unfamiliar,"local_fixed","wrong")),(4,10))
        self.assertGreater(aggregate(unfamiliar,"local_active","wrong"),
                           aggregate(unfamiliar,"local_fixed","wrong"))
