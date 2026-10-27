"""Local R7 specialization must retain both learned relationships."""
import unittest
from local_cell_specialization import SpecializedColony
from local_cell_specialization_audit import measure
from multi_relation_interference_audit import PATTERNS, UNSEEN, CTX

class LocalSpecializationTests(unittest.TestCase):
    def test_two_relationships_and_no_invented_unseen_predictions(self):
        result = measure()
        end = result["phases"][-1]
        self.assertEqual(end["specialized_training"],
                         {"correct":2,"wrong":0,"abstentions":0})
        self.assertEqual(end["original_training"],
                         {"correct":1,"wrong":0,"abstentions":1})
        self.assertEqual(end["tabular_training"],
                         {"correct":2,"wrong":0,"abstentions":0})
        self.assertEqual(end["specialized_unseen"]["wrong"],0)
        self.assertEqual(end["specialized_unseen"]["abstentions"],2)
        self.assertEqual(result["actions"],4)
        self.assertEqual(result["specialized_updates"],4)
        self.assertEqual(result["original_updates"],4)
        self.assertEqual(result["conventional_examples"],4)
        self.assertEqual(result["specialized_messages"],32)
        self.assertTrue(result["cold_restore_equal"])

    def test_incomplete_evidence_and_capacity(self):
        m = SpecializedColony()
        bits, outcome = PATTERNS[0]
        self.assertIsNone(m.predict_public(CTX,bits))
        with self.assertRaises(ValueError):
            m.learn_completed_public_feedback(CTX,bits,outcome,1)
        m.learn_completed_public_feedback(CTX,bits,outcome,2)
        self.assertIsNone(m.predict_public(CTX,bits))
        m.learn_completed_public_feedback(CTX,bits,outcome,2)
        self.assertEqual(m.predict_public(CTX,bits),outcome)
        # Fill the second local receptive field before checking the cap.
        other_bits, other_outcome = PATTERNS[1]
        for _ in range(2):
            m.learn_completed_public_feedback(CTX,other_bits,other_outcome,2)
        # Each cell has at most two local receptive field identities.
        with self.assertRaises(ValueError):
            m.learn_completed_public_feedback(CTX,(False,False,True,True),True,2)
        self.assertEqual(m.feedback_updates,4)

    def test_tampered_state_refused(self):
        m = SpecializedColony()
        for bits, outcome in PATTERNS:
            for _ in range(2):
                m.learn_completed_public_feedback(CTX,bits,outcome,2)
        restored = SpecializedColony.restore(m.checkpoint())
        for bits,_ in PATTERNS + UNSEEN:
            self.assertEqual(m.predict_public(CTX,bits),
                             restored.predict_public(CTX,bits))
        with self.assertRaises((ValueError,TypeError)):
            SpecializedColony.restore(m.checkpoint()[:-2]+b"xx")
