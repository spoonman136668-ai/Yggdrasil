"""Matched risk-aware active probing has no privilege over conventional controls."""
import unittest
from risk_aware_drift_audit import run,trial
from risk_aware_drift_probe import RiskAwareLocalProbe
from conventional_active_mutation import ConventionalActiveMutation
from unrestricted_operation_cells import INPUTS

class RiskAwareDriftTests(unittest.TestCase):
    def test_all_worlds_matched_custody_and_conventional_equivalence(self):
        rows=run()["runs"]
        self.assertEqual(len(rows),256)
        for row in rows:
            self.assertEqual(row["source_observations_per_arm"],8)
            self.assertEqual(row["target_observations_per_arm"],3)
            for stage in row["stages"]:
                n=stage["new_public_observations"]
                self.assertEqual(stage["scores"]["native_active"],
                                 stage["scores"]["conventional_active"])
                self.assertEqual(stage["scores"]["native_fixed"],
                                 stage["scores"]["conventional_fixed"])
                self.assertEqual(stage["probe_paths"]["native_active"],
                                 stage["probe_paths"]["conventional_active"])
                self.assertEqual(stage["probe_paths"]["native_fixed"],
                                 stage["probe_paths"]["conventional_fixed"])
                self.assertEqual(stage["remaining_hypotheses"]["native_active"],
                                 stage["remaining_hypotheses"]["conventional_active"])
                for name,result in stage["scores"].items():
                    self.assertEqual(sum(result[k] for k in ("correct","wrong","abstentions")),4-n)
                    self.assertEqual(result["unseen"],4-n)
                    self.assertEqual(len(stage["probe_paths"][name]),n)
                    self.assertGreaterEqual(row["cpu_ns"][name],0)

    def test_unknown_values_abstain_and_probe_costs_count(self):
        native=RiskAwareLocalProbe(3)
        classic=ConventionalActiveMutation(3)
        self.assertEqual(native.select_probe(),classic.select_probe())
        with self.assertRaises(ValueError):
            native.observe(INPUTS[0],1)
        native.observe(INPUTS[0],True)
        classic.observe(INPUTS[0],True)
        with self.assertRaises(ValueError):
            native.observe(INPUTS[0],True)
        self.assertEqual(native.target_observations,1)
        self.assertEqual(classic.target_observations,1)
        with self.assertRaises(ValueError):
            trial(16,0)

    def test_source_target_relation_is_diagnostic_only(self):
        for row in run()["runs"]:
            self.assertEqual(row["stages"][0]["new_public_observations"],1)
            self.assertIn(row["relation"],("same","complement","unrelated"))
