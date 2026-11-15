"""F20 frozen native memory and public-transfer tests, no protected data."""
import unittest
from f20_native_transfer_falsification import (
    PublicCausalCells, LAWS, TRAIN, TEST, TRIALS, experiences,
    law_action, native_choose, native_fit, raw_retrieval, symbolic_infer, run,
)


class F20(unittest.TestCase):
    def test_training_contexts_identify_six_laws_for_privileged_control(self):
        self.assertEqual((TRAIN, TEST, TRIALS), ((0, 1, 2, 4), (3, 5, 6, 7), 8))
        self.assertEqual(len({tuple(law_action(l, x) for x in TRAIN) for l in LAWS}), 6)

    def test_actual_native_learns_seen_and_abstains_unseen(self):
        for law in LAWS:
            rows = experiences(law)
            self.assertEqual(len(rows), 64)
            native = native_fit(rows)
            restored = PublicCausalCells.restore(native.snapshot())
            for x in TRAIN:
                self.assertEqual(native_choose(native, x), law_action(law, x))
                self.assertEqual(native_choose(restored, x), law_action(law, x))
            for x in TEST:
                self.assertIsNone(native_choose(native, x))
                self.assertIsNone(raw_retrieval(rows, x))
            self.assertEqual(symbolic_infer(rows), (law,))

    def test_active_and_retained_slot_dont_alias(self):
        c = PublicCausalCells()
        c.observe(0, 0, 1)
        c.observe(0, 1, 0)
        self.assertEqual(native_choose(c, 0), 0)
        self.assertIsNone(native_choose(c, 7))
        c.observe(0, 0, 0, retained=True)
        c.observe(0, 1, 1, retained=True)
        self.assertEqual(native_choose(c, 0), 0)
        self.assertEqual(native_choose(c, 7), 1)

    def test_incomplete_action_evidence_and_malformed_context_fail_closed(self):
        c = PublicCausalCells()
        c.observe(0, 0, 1)
        self.assertIsNone(c.choose(0))
        with self.assertRaises(ValueError):
            native_choose(c, True)

    def test_frozen_no_go_metrics(self):
        r = run()
        self.assertEqual(r["classification"], "DEV_NATIVE_CONTEXT_TRANSFER_NO_GO")
        self.assertEqual((r["learned_bytes"], r["checkpoint_bytes"]), (128, 164))
        self.assertEqual((r["public_events"], r["heldout_queries"]), (384, 24))
        self.assertEqual(r["metrics"]["native_train_correct"], 24)
        self.assertEqual(r["metrics"]["native_test_covered"], 0)
        self.assertEqual(r["metrics"]["symbolic_test_correct"], 24)
        self.assertFalse(r["scientific_pass"])
        self.assertTrue(r["strong_symbolic_control_has_privileged_prior"])


if __name__ == "__main__":
    unittest.main()
