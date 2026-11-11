import unittest
from operator_layer import OperatorLayer, basis, COEFFICIENTS

def signals():
    return tuple(((i >> 2) & 1, (i >> 1) & 1, i & 1) for i in range(8))

class OperatorConstructionTests(unittest.TestCase):
    def test_all_bit_monomials_and_fixed_capacity(self):
        self.assertEqual(len(COEFFICIENTS), 256)
        self.assertEqual(len({c for c in COEFFICIENTS}), 256)
        self.assertEqual(basis((1,1,1)), (1,1,1,1,1,1,1,1))
        self.assertEqual(basis((0,0,0)), (1,0,0,0,0,0,0,0))

    def test_blank_state_has_no_named_rule_or_supervised_fact(self):
        layer = OperatorLayer()
        self.assertEqual(len(layer.observations), 0)
        self.assertEqual(sum(layer.eligible), 256)
        raw = layer.snapshot()
        self.assertEqual(OperatorLayer.restore(raw).snapshot(), raw)
        self.assertNotIn(b"xor", raw.lower())
        self.assertNotIn(b"switch", raw.lower())

    def test_universal_operator_basis_reconstructs_xor_without_name(self):
        xs = signals()
        rows = tuple((x, x[0]^x[1]) for x in xs)
        layer = OperatorLayer(rows)
        self.assertEqual(sum(layer.eligible), 1)
        self.assertEqual(tuple(layer.predict(x) for x in xs),
                         tuple(x[0]^x[1] for x in xs))

    def test_universal_operator_basis_reconstructs_switch_without_name(self):
        xs = signals()
        rows = tuple((x, x[0] if x[2] == 0 else x[1]) for x in xs)
        layer = OperatorLayer(rows)
        self.assertEqual(sum(layer.eligible), 1)
        self.assertEqual(tuple(layer.predict(x) for x in xs),
                         tuple(x[0] if x[2] == 0 else x[1] for x in xs))
        self.assertEqual(sum(OperatorLayer(rows, linear_only=True).eligible), 0)

    def test_idempotent_real_evidence_and_cold_state(self):
        layer = OperatorLayer([((0,1,0),1),((1,0,1),0)])
        before = layer.snapshot()
        layer.observe((0,1,0),1)
        self.assertEqual(layer.snapshot(), before)
        cold = OperatorLayer.restore(before)
        self.assertEqual(cold.snapshot(), before)
        for x in signals():
            self.assertEqual(layer.predict(x),cold.predict(x))

    def test_contradictory_observation_fails_closed(self):
        layer = OperatorLayer([((0,1,0),1)])
        before = layer.snapshot()
        with self.assertRaises(ValueError):
            layer.observe((0,1,0),0)
        self.assertEqual(before,layer.snapshot())

    def test_malformed_binary_fails_closed(self):
        for bad in ((0,1,2),(1,-1,0),(1,0,0,1)):
            with self.assertRaises(ValueError):
                OperatorLayer([(bad,1)])
        with self.assertRaises(ValueError):
            OperatorLayer([((1,0,0),2)])
        with self.assertRaises(ValueError):
            OperatorLayer(linear_only=1)

    def test_checkpoint_tampering_rejected(self):
        raw = OperatorLayer([((1,0,1),0)]).snapshot()
        with self.assertRaises(ValueError):
            OperatorLayer.restore(raw[:-1]+bytes([raw[-1]^1]))
        with self.assertRaises(ValueError):
            OperatorLayer.restore(raw[:-1])
        with self.assertRaises(ValueError):
            OperatorLayer.restore(b"invalid")

    def test_same_evidence_same_weight_state(self):
        cases = [((0,1,0),1),((1,0,1),0),((1,1,1),1)]
        first, second = OperatorLayer(cases), OperatorLayer(cases)
        self.assertEqual(first.snapshot(), second.snapshot())
        self.assertEqual(tuple(first.predict(x) for x in signals()),
                         tuple(second.predict(x) for x in signals()))

if __name__ == "__main__":
    unittest.main()
