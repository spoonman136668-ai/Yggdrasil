"""WSP-13 focused tests. Full 1024-world science lives in run_dev.py."""
import hashlib
import json
import unittest
from composite_memory import (BASE, BASE_CODE, GRADIENT_STEPS, HIDDEN,
                              MAGIC, N, SLOTS, TRIPLES, NumericRuleBuilder,
                              ThresholdVM, oracle_truth, stimulus, symbolic_exact)


def exposures(code):
    return tuple((stimulus(mask), oracle_truth(code, stimulus(mask)))
                 for mask in BASE + TRIPLES)


def build(code):
    model = NumericRuleBuilder()
    for x, y in exposures(code):
        model.observe_training(x, y)
    return model


class WSP13CompositeTests(unittest.TestCase):
    def test_only_threshold_kernel_and_numerical_xor(self):
        vm = ThresholdVM()
        for a in (0,1):
            for b in (0,1):
                self.assertEqual(vm.and_(a,b), a & b)
                self.assertEqual(vm.or_(a,b), a | b)
                self.assertEqual(vm.xor(a,b), a ^ b)
                self.assertEqual(vm.not_(a), 1-a)

    def test_unprogrammed_composite_sites_are_blank(self):
        model = NumericRuleBuilder()
        self.assertEqual(model.feature_occupied, [0]*SLOTS)
        self.assertEqual(model.feature_addresses, [[0]*N for _ in range(SLOTS)])
        self.assertEqual(model.witness_occupied, [0]*SLOTS)
        self.assertEqual(model.base_weights, [0]*len(BASE))
        self.assertFalse(model.is_complete())

    def test_numeric_feature_addresses_create_and_generalize(self):
        for code in (0,1,3,17,127,255,512,1023):
            model = build(code)
            self.assertTrue(model.is_complete())
            expected_masks = [TRIPLES[i] for i in range(10) if (code >> i) & 1]
            actual_masks = [
                sum(bit << i for i, bit in enumerate(addr))
                for occupied, addr in zip(model.feature_occupied,
                                          model.feature_addresses) if occupied]
            self.assertEqual(actual_masks, expected_masks)
            self.assertEqual(model.witness_occupied, [1]*10)
            for m in HIDDEN:
                self.assertEqual(model.predict(stimulus(m)),
                                 oracle_truth(code, stimulus(m)))

    def test_matched_exact_symbolic_solver(self):
        for code in (0,1,3,127,255,512,1023):
            obs = exposures(code)
            model = build(code)
            for m in HIDDEN:
                x = stimulus(m)
                self.assertEqual(symbolic_exact(obs, x),
                                 model.predict(x))

    def test_ablate_new_features_destroys_higher_order_transfer(self):
        selected_code = 1
        healthy = build(selected_code)
        damaged = NumericRuleBuilder.restore(healthy.snapshot())
        damaged.feature_occupied = [0]*SLOTS
        damaged.feature_addresses = [[0]*N for _ in range(SLOTS)]
        affected = [m for m in HIDDEN if (TRIPLES[0] & m) == TRIPLES[0]]
        self.assertEqual(len(affected), 3)
        for m in affected:
            x = stimulus(m)
            self.assertNotEqual(healthy.predict(x), damaged.predict(x))

    def test_hidden_fourth_order_counterexample(self):
        for code in (0,1,3,127,1023):
            model = build(code)
            errors = 0
            for m in HIDDEN:
                x = stimulus(m)
                target = oracle_truth(code,x) ^ int(all(x[:4]))
                errors += model.predict(x) != target
            self.assertEqual(errors, 2)
            self.assertFalse(model.verify_new_witness(stimulus(15),
                             oracle_truth(code, stimulus(15)) ^ 1))
            self.assertIsNone(model.predict(stimulus(31)))

    def test_checkpoint_restores_independent_worlds(self):
        for code in (0,1,127,512,1023):
            model = build(code)
            raw = model.snapshot()
            copy = NumericRuleBuilder.restore(raw)
            self.assertEqual(copy.snapshot(), raw)
            self.assertEqual(copy.architecture_sha256(), model.architecture_sha256())
            for m in HIDDEN:
                self.assertEqual(copy.predict(stimulus(m)),
                                 model.predict(stimulus(m)))
        self.assertEqual(GRADIENT_STEPS, 0)

    def test_duplicate_invalid_order_and_custody_fail(self):
        model = NumericRuleBuilder()
        with self.assertRaisesRegex(ValueError,"OUT_OF_ORDER"):
            model.observe_training(stimulus(1), 0)
        with self.assertRaisesRegex(ValueError, "INVALID_CONTEXT"):
            model.observe_training([0]*5, 0)
        with self.assertRaisesRegex(ValueError, "INVALID_LABEL"):
            model.observe_training(stimulus(0), True)
        for x,y in exposures(7)[:16]:
            model.observe_training(x,y)
        triple=stimulus(TRIPLES[0])
        model.observe_training(triple,oracle_truth(7,triple))
        with self.assertRaisesRegex(ValueError,"DUPLICATE"):
            model.observe_training(triple,oracle_truth(7,triple))
        self.assertEqual(sum(model.witness_occupied),1)

    def test_tamper_and_noncanonical_state_rejected(self):
        model = build(21)
        raw = model.snapshot()
        for bad in (raw[:-1],raw+b"x",raw[:-1]+bytes([raw[-1]^1])):
            with self.assertRaisesRegex(ValueError,"WSP13_CHECKPOINT_REJECTED"):
                NumericRuleBuilder.restore(bad)
        data = json.loads(raw[9:-32].decode("ascii"))
        data["feature_addresses"][9][0] = 1
        body = json.dumps(data,sort_keys=True,separators=(",",":")).encode("ascii")
        prefix=MAGIC+len(body).to_bytes(4,"big")+body
        with self.assertRaisesRegex(ValueError,"WSP13_CHECKPOINT_REJECTED"):
            NumericRuleBuilder.restore(prefix+hashlib.sha256(prefix).digest())

    def test_new_witness_must_follow_complete_exposure(self):
        model=NumericRuleBuilder()
        with self.assertRaisesRegex(ValueError,"INCOMPLETE"):
            model.verify_new_witness(stimulus(15),1)
        for x,y in exposures(0):
            self.assertTrue(model.observe_training(x,y))
        with self.assertRaisesRegex(ValueError,"EXHAUSTED"):
            model.observe_training(stimulus(7),0)


if __name__ == "__main__":
    unittest.main()
