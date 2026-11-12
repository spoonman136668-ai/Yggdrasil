"""WSP53 warm64 numeric-address source-only fixture tests (no DEV/PRIMARY)."""
from dataclasses import replace
import unittest
from source import build_world
from warm64 import Warm64AddressWriter,STEPS

class WarmContracts(unittest.TestCase):
    def test_full_48_12_budget_cold_restore_and_gradient_routes(self):
        for family in ("anchored_effect","noncommuting_order"):
            w=build_world(family,"SELFTEST",9902,"identity")
            m=Warm64AddressWriter(family=family)
            for row in w.phase_a:
                m.observe(row)
            self.assertEqual(m.actions,48)
            with self.assertRaises(ValueError):
                m.observe(w.phase_b[0])
            m.seal_a()
            self.assertEqual(m.updates,STEPS)
            self.assertGreater(m.numeric_weight_count(),0)
            self.assertTrue(m.coefficients)
            before=w.heldout_a[0]
            after=m.predict(before.before,before.acoustic_bits)
            for row in w.phase_b:
                m.observe(row)
            self.assertEqual(m.actions,60)
            cold=Warm64AddressWriter.restore(m.snapshot())
            self.assertEqual(cold.updates,STEPS)
            self.assertEqual(cold.numeric_weight_count(),m.numeric_weight_count())
            self.assertEqual(cold.capacity_bits(),m.capacity_bits())
            self.assertEqual(cold.predict(before.before,before.acoustic_bits),
                             m.predict(before.before,before.acoustic_bits))
            with self.assertRaises(ValueError):
                m.observe(w.phase_b[0])
            with self.assertRaises(ValueError):
                m.seal_a()

    def test_counterexample_and_snapshot_tamper(self):
        w=build_world("anchored_effect","SELFTEST",9901,"permuted")
        m=Warm64AddressWriter(family="anchored_effect")
        with self.assertRaises(ValueError):
            m.seal_a()
        with self.assertRaises(ValueError):
            m.observe(replace(w.phase_a[0],action_cost=0))
        self.assertEqual(m.actions,0)
        for row in w.phase_a:
            m.observe(row)
        m.seal_a()
        with self.assertRaises(ValueError):
            Warm64AddressWriter.restore(m.snapshot().replace("warm64-direct","warm64_fake"))

if __name__=="__main__":
    unittest.main()
