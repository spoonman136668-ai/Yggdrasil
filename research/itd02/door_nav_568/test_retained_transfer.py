"""Unfamiliar-world retention and independent conventional comparison."""
import unittest
from retained_transfer_audit import run,trial
from retained_cell_transfer import RetainedCellTransfer
from unrestricted_operation_cells import INPUTS

class RetainedTransferTests(unittest.TestCase):
    def test_all_source_target_pairs_with_equal_public_evidence(self):
        rows=run()["runs"]
        self.assertEqual(len(rows),256)
        groups={"same":0,"complement":0,"unrelated":0}
        for r in rows:
            groups[r["relationship_diagnostic"]]+=1
            self.assertEqual(r["source_public_actions"],8)
            self.assertEqual(r["target_public_actions"],1)
            self.assertEqual(r["local_source_updates"],8)
            self.assertEqual(r["local_target_updates"],1)
            self.assertEqual(r["table_target_updates"],1)
            self.assertEqual(r["scratch_target_updates"],1)
            self.assertTrue(r["cold_restore_exact"])
            self.assertLessEqual(r["checkpoint_bytes"],4096)
            for name in ("local","table","scratch"):
                self.assertEqual(sum(r["before"][name].values()),3)
                self.assertEqual(sum(r["after"][name].values()),3)
                self.assertGreaterEqual(r["cpu_ns"][name],0)
            self.assertEqual(r["after"]["local"],r["after"]["table"])
            self.assertEqual(r["before"]["local"]["abstentions"],3)
            self.assertEqual(r["after"]["scratch"]["abstentions"],3)
        self.assertEqual(groups,{"same":16,"complement":16,"unrelated":224})

    def test_related_worlds_transfer_after_only_one_new_probe(self):
        rows=run()["runs"]
        for row in rows:
            if row["relationship_diagnostic"] in ("same","complement"):
                self.assertEqual(row["after"]["local"],
                                 {"correct":3,"wrong":0,"abstentions":0})

    def test_checkpoint_tampering_and_partial_source_refused(self):
        learner=RetainedCellTransfer()
        with self.assertRaises(ValueError):
            learner.observe_new(INPUTS[0],True)
        snapshot=learner.checkpoint()
        with self.assertRaises(ValueError):
            RetainedCellTransfer.restore(snapshot[:-2]+b"xx")
        with self.assertRaises(ValueError):
            learner.train_source((1,False),True)
        with self.assertRaises(ValueError):
            trial(16,0)

    def test_unrelated_pairs_are_not_silently_counted_as_transfer(self):
        unrelated=[r for r in run()["runs"]
                   if r["relationship_diagnostic"]=="unrelated"]
        self.assertGreater(sum(r["after"]["local"]["wrong"] for r in unrelated),0)
