"""Mass Research frozen source-only local-neighbor causal ablation tests."""
import ast
import itertools
import math
import unittest
from pathlib import Path

import mass_neighbor_audit as audit
from native_cells import Colony, LocalCell


class NativeNeighborMechanismFalsification(unittest.TestCase):
    def test_all_32_frozen_cell_state_sensor_pairs_agree_without_neighbors(self):
        r = audit.audit()
        self.assertEqual(r["evaluated_synthetic_counterfactuals"], 32)
        self.assertTrue(r["all_original_predictions_match_zero_neighbor"])
        self.assertLess(r["max_ring_identity_absolute_rounding_error"], 1e-11)
        self.assertEqual(r["native_neighbor_messages_counter_source"],
                         "8_PER_FEEDBACK_NOT_WIRE_BYTES")
        self.assertFalse(r["scientific_first_use"])
        self.assertFalse(r["original_r7_training_or_scoring"])

    def test_all_gains_larger_than_negative_one_preserve_sign_away_from_ties(self):
        for fast, slow in audit.SMOKE_FIXTURES:
            p = audit._fixture(fast, slow)
            for values in itertools.product((False, True), repeat=4):
                local = [c.signal(v) for c, v in zip(p.cells["A"], values)]
                base = sum(local)
                self.assertGreater(abs(base), .05)
                for gain in audit.COUNTERFACTUAL_GAINS:
                    with self.subTest(gain=gain, values=values):
                        self.assertGreater(1+gain, 0)
                        self.assertAlmostEqual(audit._votes(local,gain),
                                               (1+gain)*base, places=10)
                        self.assertEqual(audit._votes(local,gain)>0,
                                         base>0)

    def test_global_counter_is_not_message_volume(self):
        original = Path(audit.__file__).with_name("native_cells.py").read_text()
        self.assertIn("self.neighbor_messages+=8", original)
        self.assertNotIn("neighbor_messages+=", original.split(
            "    def predict(",1)[1].split(
                "    def learn_completed_public_feedback(",1)[0])
        self.assertTrue(audit._identity_check())

    def test_input_and_original_source_are_not_modified(self):
        p = audit._fixture(*audit.SMOKE_FIXTURES[0])
        snap = p.checkpoint()
        for values in itertools.product((False, True), repeat=4):
            p.predict("A", values)
        self.assertEqual(p.checkpoint(),snap)

    def test_no_native_training_generator_firstuse_or_runner_dispatch(self):
        code = Path(audit.__file__).read_text()
        tree = ast.parse(code)
        forbidden={"study","_examples","PublicDevGenerator",
                   "learn_completed_public_feedback","dispatch","subprocess"}
        for node in ast.walk(tree):
            if isinstance(node,ast.Call):
                fn = node.func
                label = fn.id if isinstance(fn,ast.Name) else (
                    fn.attr if isinstance(fn,ast.Attribute) else "?")
                self.assertNotIn(label,forbidden)
        self.assertNotIn("orig_H1H2_fixture",code)

if __name__ == "__main__":
    unittest.main()
