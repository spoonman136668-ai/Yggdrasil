"""Exhaustive four-message learning and identifiability gates."""
import unittest
from unrestricted_operation_cells import INPUTS,UnrestrictedMessageCells
from conventional_version_space import ConventionalVersionSpace
from unrestricted_operation_audit import run,trial

class UnrestrictedOperationTests(unittest.TestCase):
    def test_all_sixteen_functions_and_all_four_heldout_pairs(self):
        rows=run()["experiments"]
        self.assertEqual(len(rows),64)
        for r in rows:
            self.assertEqual(r["prior_public_observations"],6)
            self.assertEqual(r["additional_public_observations"],2)
            self.assertEqual(r["native_observations"],8)
            self.assertEqual(r["conventional_observations"],8)
            self.assertEqual(r["prior_hypothesis_counts"],{"native":2,"conventional":2})
            self.assertEqual(r["final_hypothesis_counts"],{"native":1,"conventional":1})
            for agent in ("native","conventional"):
                self.assertEqual(r["before"][agent],
                                 {"correct":0,"wrong":0,"abstention":1})
                self.assertEqual(r["after_public_probe"][agent],
                                 {"correct":1,"wrong":0,"abstention":0})
                self.assertEqual(r["public_probe"][agent],r["heldout"])
                self.assertGreaterEqual(r["cpu_ns"][agent],0)
            self.assertGreater(r["native_python_bytes"],0)
            self.assertGreater(r["conventional_python_bytes"],0)

    def test_public_evidence_is_required_and_validated(self):
        a=UnrestrictedMessageCells()
        b=ConventionalVersionSpace()
        self.assertEqual(len(a.possible_operations()),16)
        self.assertEqual(len(b.possible_operations()),16)
        self.assertIsNone(a.predict(INPUTS[0]))
        self.assertIsNone(b.predict(INPUTS[0]))
        with self.assertRaises(ValueError):
            a.observe((1,False),False)
        with self.assertRaises(ValueError):
            b.observe(INPUTS[0],1)
        with self.assertRaises(ValueError):
            trial(16,INPUTS[0])

    def test_first_example_does_not_invent_complete_public_evidence(self):
        a=UnrestrictedMessageCells()
        b=ConventionalVersionSpace()
        a.observe(INPUTS[0],True)
        b.observe(INPUTS[0],True)
        self.assertEqual(len(a.possible_operations()),16)
        self.assertEqual(len(b.possible_operations()),16)
        a.observe(INPUTS[0],True)
        b.observe(INPUTS[0],True)
        self.assertEqual(a.possible_operations(),b.possible_operations())
        self.assertEqual(len(a.possible_operations()),8)

if __name__=="__main__":
    unittest.main()
