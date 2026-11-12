"""SELFTEST-only invariance ablation. Same stored weights, different readout prior."""
import unittest
from source import build_world
from direct_writer import DirectWeightWriter
from order_invariant_ablation import OrderInvariantReadout


class OrderAblationTests(unittest.TestCase):
    def test_identical_write_weights_and_serialized_state(self):
        w=build_world('SELFTEST',9001,'identity')
        a,b=DirectWeightWriter(),OrderInvariantReadout()
        for row in w.phase_a+w.phase_b:
            a.observe(row)
            b.observe(row)
        self.assertEqual(a.numeric_weight_count(),b.numeric_weight_count())
        self.assertEqual(a.entity_weights,b.entity_weights)
        self.assertEqual(a.effect_weights,b.effect_weights)
        self.assertEqual(a.capacity_bits(),b.capacity_bits())
        self.assertEqual(a.snapshot(),b.snapshot())
        self.assertEqual(OrderInvariantReadout.restore(b.snapshot()).snapshot(),b.snapshot())

    def test_explicit_symmetry_transfer_not_oracle(self):
        w=build_world('SELFTEST',9001,'identity')
        a,b=DirectWeightWriter(),OrderInvariantReadout()
        for row in w.phase_a+w.phase_b:
            a.observe(row);b.observe(row)
        # Diagnostic, not a qualification threshold. Full results stored in repo.
        direct=sum(a.predict(row.before,row.acoustic_bits)==row.after for row in w.heldout_b)
        ablated=sum(b.predict(row.before,row.acoustic_bits)==row.after for row in w.heldout_b)
        self.assertGreater(ablated,direct)
        self.assertEqual(b.actions,42)

    def test_unknown_bits_abstain_without_evidence(self):
        model=OrderInvariantReadout()
        self.assertIsNone(model.predict((0,)*8,'01010'*3))
        with self.assertRaises(ValueError):
            model.predict((0,)*8,'not_binary')

if __name__ == '__main__': unittest.main()
