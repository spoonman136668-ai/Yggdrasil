"""Causal two-hop disambiguation, adversarial negative and bounded custody."""
import unittest
from two_hop_evidence_audit import run, build, FIRST
from two_hop_evidence_selector import TwoHopEvidenceSelector

class TwoHopEvidenceTests(unittest.TestCase):
    def test_two_distinct_longer_probes_disambiguate_tied_first_hop(self):
        report = run()
        for name, selected in (("A_return", "snapshot"),
                               ("B_continues", "active")):
            result = report[name]
            self.assertTrue(result["first_hop_agrees"])
            self.assertTrue(result["admitted"])
            self.assertEqual(result["selected"], selected)
            self.assertEqual(result["probe_actions"], 4)
            self.assertLessEqual(result["active_transition_records"], 128)
            self.assertLessEqual(result["archive_transition_records"], 128)
            self.assertLessEqual(result["stored_examples"], 256)

    def test_joint_second_hop_corruption_is_a_scientific_negative(self):
        result = run()["A_corrupted"]
        self.assertTrue(result["admitted"])
        self.assertEqual(result["selected"], "active")
        self.assertNotEqual(result["selected"], result["expected"])

    def test_unlinked_chain_refuses_to_forge_evidence(self):
        learner = build()
        learner.begin_chain_probe()
        frame, action, middle = FIRST[0]
        learner.observe(frame, [0, 1])
        learner.learn(action, middle, 0, False)
        learner.observe(b"not-public-successor", [2])
        with self.assertRaises(ValueError):
            learner.learn(2, b"R3-positive", 0, False)

    def test_insufficient_independent_chains_abstain(self):
        learner = build()
        learner.begin_chain_probe()
        frame, action, middle = FIRST[0]
        learner.observe(frame, [0, 1])
        learner.learn(action, middle, 0, False)
        learner.observe(middle, [2])
        learner.learn(2, b"R3-positive", 0, False)
        self.assertFalse(learner.resolve_chain_probe())
        self.assertIsNone(learner.selected)

    def test_repeatability(self):
        self.assertEqual(run(), run())

if __name__ == "__main__":
    unittest.main()
