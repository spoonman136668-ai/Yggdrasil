"""Action-owned compositional learning and independent conventional controls."""
import unittest
from public_composition_transfer_audit import run,trial
from compositional_local_cells import CompositionalLocalCells

class PublicCompositionTests(unittest.TestCase):
    def test_eight_heldout_compositions_and_equal_budgets(self):
        report=run()
        self.assertEqual(len(report["runs"]),8)
        for row in report["runs"]:
            self.assertEqual(row["public_pair_actions"],16)
            self.assertEqual(row["public_final_actions"],6)
            self.assertEqual(row["total_public_actions"],22)
            self.assertEqual(row["native_observations"],22)
            self.assertEqual(row["factorized_observations"],22)
            self.assertEqual(row["tabular_final_observations"],6)
            self.assertEqual(row["native_messages"],tuple(row["heldout"]))
            self.assertIsNotNone(row["native_coefficients"])
            for policy in ("native","factorized","tabular"):
                self.assertEqual(sum(row["heldout_results"][policy].values()),1)
                self.assertGreaterEqual(row["cpu_ns"][policy],0)
            self.assertEqual(row["heldout_results"]["native"],
                             row["heldout_results"]["factorized"])
            self.assertEqual(row["heldout_results"]["native"]["correct"],1)
            self.assertEqual(row["heldout_results"]["tabular"]["abstention"],1)

    def test_without_intermediate_feedback_predictions_abstain(self):
        local=CompositionalLocalCells()
        self.assertIsNone(local.predict((False,False,True,False)))
        with self.assertRaises(ValueError):
            local.observe_final((False,False,True,False),True)

    def test_two_samples_required_and_affine_rank_not_oracle(self):
        local=CompositionalLocalCells()
        for i in (0,1):
            for pair in ((False,False),(True,False)):
                local.observe_pair(i,pair,pair[0]^pair[1])
                self.assertIsNone(local.pair_cells[i].predict(pair))
                local.observe_pair(i,pair,pair[0]^pair[1])
        first=(False,False,False,False)
        local.observe_final(first,False)
        local.observe_final(first,False)
        self.assertIsNone(local.predict((True,False,True,False)))
        with self.assertRaises(ValueError):
            local.observe_pair(2,(True,False),True)

    def test_non_affine_negative_transfer_is_not_promotion(self):
        rows=run()["non_affine_negative"]
        self.assertEqual(len(rows),8)
        for row in rows:
            self.assertEqual(row["total_public_actions"],22)
            self.assertEqual(row["heldout_results"]["native"],
                             row["heldout_results"]["factorized"])
            self.assertEqual(row["heldout_results"]["native"]["wrong"],1)
            self.assertEqual(row["heldout_results"]["tabular"]["abstention"],1)
        with self.assertRaises(ValueError):
            trial(rule="unsupported")

if __name__=="__main__":
    unittest.main()
