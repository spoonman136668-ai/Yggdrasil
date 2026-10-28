"""Unequal probe informativeness and equal-information conventional comparisons."""
import unittest
from asymmetric_probe_audit import run,trial
from asymmetric_probe_cells import LocalAsymmetricProbe,HYPOTHESES
from conventional_asymmetric_probe import ConventionalAsymmetric
from unrestricted_operation_cells import INPUTS

class AsymmetricProbeTests(unittest.TestCase):
    def test_hypotheses_have_a_genuinely_unequal_public_split(self):
        self.assertEqual(HYPOTHESES,(0,1,3,7))
        cell=LocalAsymmetricProbe()
        control=ConventionalAsymmetric()
        self.assertEqual(cell.choose(),INPUTS[1])
        self.assertEqual(control.choose(),INPUTS[1])
        self.assertNotEqual(cell.choose(),INPUTS[0])

    def test_all_target_worlds_have_matched_public_budgets(self):
        report=run()
        self.assertEqual(len(report["cases"]),4)
        for row in report["cases"]:
            self.assertEqual(len(row["steps"]),2)
            for step in row["steps"]:
                i=step["round"]
                for name,scores in step["scores"].items():
                    self.assertEqual(sum(scores[k] for k in ("correct","wrong","abstentions")),4-i)
                    self.assertEqual(step["actions"][name],i)
                    self.assertEqual(len(step["public_probes"][name]),i)
                    self.assertGreaterEqual(row["cpu_ns"][name],0)
                self.assertEqual(step["scores"]["local_active"],
                                 step["scores"]["conventional_active"])
                self.assertEqual(step["scores"]["local_fixed"],
                                 step["scores"]["conventional_fixed"])
                self.assertEqual(step["candidate_counts"]["local_active"],
                                 step["candidate_counts"]["conventional_active"])
                self.assertEqual(step["public_probes"]["local_active"],
                                 step["public_probes"]["conventional_active"])

    def test_no_unobserved_target_identity_and_duplicate_input_rejected(self):
        cell=LocalAsymmetricProbe()
        self.assertIsNone(cell.predict(INPUTS[0]))
        cell.observe(INPUTS[1],True)
        with self.assertRaises(ValueError):
            cell.observe(INPUTS[1],True)
        with self.assertRaises(ValueError):
            trial(15)
