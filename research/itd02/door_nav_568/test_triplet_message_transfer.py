"""Matched public evidence qualification for triplet-cell communications."""
import unittest
from triplet_message_cells import TripletMessageCells
from triplet_message_transfer_audit import run,ConventionalTripletVote
from specialization_scaling_audit import families

class TripletTransferTests(unittest.TestCase):
    def test_no_public_evidence_and_budget(self):
        local=TripletMessageCells(capacity=8)
        bits,label=families(3)[0]
        self.assertIsNone(local.predict(bits))
        local.observe(bits,label)
        self.assertIsNone(local.predict(bits))
        local.observe(bits,label)
        self.assertEqual(local.predict(bits),label)
        self.assertEqual(local.updates,2)
        self.assertEqual(local.records(),4)
        with self.assertRaises(ValueError):
            TripletMessageCells(capacity=9)

    def test_equal_learning_actions_and_measured_uncertainty(self):
        experiments=run()["experiments"]
        self.assertEqual(len(experiments),18)
        for case in experiments:
            self.assertEqual(case["actions"],2*case["count"])
            self.assertEqual(set(case["updates"].values()),{case["actions"]})
            self.assertLessEqual(case["local_records"],32)
            self.assertLessEqual(case["tabular_triplet_records"],32)
            for arm in ("local","triplet_table","linear","tabular"):
                self.assertEqual(sum(case["train"][arm].values()),case["count"])
                self.assertEqual(sum(case["heldout"][arm].values()),16-case["count"])
                self.assertGreaterEqual(case["cpu_ns"][arm],0)

    def test_conventional_triplet_receives_same_public_information(self):
        local=TripletMessageCells()
        comparator=ConventionalTripletVote()
        for bits,label in families(17)[:6]:
            for _ in range(2):
                local.observe(bits,label)
                comparator.observe(bits,label)
        for bits,_ in families(17):
            self.assertEqual(local.predict(bits),comparator.predict(bits))

    def test_scientific_equivalence_and_parity_failure_are_pinned(self):
        rows=run()["experiments"]
        for row in rows:
            self.assertEqual(row["heldout"]["local"],
                             row["heldout"]["triplet_table"])
            self.assertEqual(row["train"]["local"],
                             row["train"]["triplet_table"])
        for rule,correct,wrong in (("parity",0,17),("first_bit",15,0)):
            subset=[row for row in rows if row["rule"]==rule]
            self.assertEqual(sum(row["heldout"]["local"]["correct"]
                                 for row in subset),correct)
            self.assertEqual(sum(row["heldout"]["local"]["wrong"]
                                 for row in subset),wrong)
