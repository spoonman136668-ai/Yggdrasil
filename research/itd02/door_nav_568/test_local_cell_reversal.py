"""Regression gates for action-owned bounded R7 cell reversal."""
import unittest
from local_cell_reversal_audit import run
from local_cell_reversal_candidate import ReversalColony
from native_cell_recency_bridge_audit import public_context, public_features

class ReversalTests(unittest.TestCase):
    def test_matched_feedback_cost_and_restore(self):
        data=run()
        for name,n in (("two_observations",24),("one_observation",12)):
            row=data[name]
            self.assertEqual(row["actions"],n)
            self.assertEqual(row["updates"],n)
            self.assertEqual(row["control_examples"],n)
            self.assertEqual(row["neighbor_messages"],8*n)
            self.assertTrue(row["cold_restore_exact"])
            self.assertTrue(row["archive_unchanged"])
            self.assertLessEqual(row["candidate_checkpoint_bytes"],32768)
            self.assertEqual(len(row["stages"]),6)
            for stage in row["stages"]:
                for model in ("prior","candidate","control"):
                    self.assertEqual(sum(stage[model].values()),2)

    def test_reverses_with_two_samples_and_preserves_history(self):
        rows=run()["two_observations"]["stages"]
        self.assertEqual([s["candidate"]["correct"] for s in rows],[2]*6)
        self.assertEqual([s["candidate"]["wrong"] for s in rows],[0]*6)
        self.assertEqual([s["control"]["correct"] for s in rows],[2]*6)
        self.assertGreater(sum(s["prior"]["wrong"] for s in rows),0)

    def test_early_feedback_and_unauthenticated_restore_refused(self):
        colony=ReversalColony()
        key=(b"M1-intermediate",2)
        ctx,bits=public_context(key),public_features(key)
        self.assertIsNone(colony.predict_public(ctx,bits))
        with self.assertRaises(ValueError):
            colony.learn_completed_public_feedback(ctx,bits,True,1)
        colony.learn_completed_public_feedback(ctx,bits,True,2)
        self.assertIsNone(colony.predict_public(ctx,bits))
        blob=colony.checkpoint()
        with self.assertRaises(ValueError):
            ReversalColony.restore(blob[:-2]+b"xx")
