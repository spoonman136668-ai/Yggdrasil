"""WSP-12 rule-selection behavior, safety, and negative controls."""
import hashlib
import json
import unittest
from rule_memory import (GRAMMAR, HIDDEN, GRADIENT_STEPS, MAGIC,
                         NumericRuleMemory, ThresholdVM, context,
                         independent_symbolic, oracle_truth)


def observations(code):
    return tuple((context(mask), oracle_truth(code, context(mask)))
                 for mask in GRAMMAR)


class NumericRuleTests(unittest.TestCase):
    def test_numeric_threshold_kernel_and_xor(self):
        vm = ThresholdVM()
        for a in (0, 1):
            for b in (0, 1):
                self.assertEqual(vm.xor(a, b), a ^ b)
                self.assertEqual(vm.and_(a, b), a & b)
                self.assertEqual(vm.or_(a, b), a | b)
                self.assertEqual(vm.not_(a), 1-a)

    def test_all_2048_worlds_exact_on_hidden_and_symbolic_tie(self):
        direct = symbolic = 0
        for code in range(2048):
            model = NumericRuleMemory()
            events = observations(code)
            for x, y in events:
                self.assertTrue(model.observe(x, y))
            self.assertEqual(model.seen, [1]*11)
            self.assertEqual(
                model.weights,
                [(code >> j) & 1 for j in range(11)])
            for mask in HIDDEN:
                goal = oracle_truth(code, context(mask))
                direct += model.predict(context(mask)) == goal
                symbolic += independent_symbolic(events, context(mask)) == goal
        self.assertEqual((direct, symbolic), (10240, 10240))

    def test_hidden_cubic_is_unidentifiable_and_must_fail(self):
        errors = 0
        for code in range(2048):
            model = NumericRuleMemory()
            for x, y in observations(code):
                self.assertTrue(model.observe(x, y))
                # Cubic x0*x1*x2 is zero on all public contexts.
                self.assertFalse(all(x[:3]))
            for mask in HIDDEN:
                x = context(mask)
                target = oracle_truth(code, x) ^ int(all(x[:3]))
                errors += model.predict(x) != target
        self.assertEqual(errors, 4096)

    def test_linear_only_and_ablation_controls(self):
        linear = ablated = zero = 0
        for code in range(2048):
            full = NumericRuleMemory()
            only = NumericRuleMemory()
            events = observations(code)
            for x, y in events[:5]:
                self.assertTrue(only.observe(x, y))
            for x, y in events:
                self.assertTrue(full.observe(x, y))
            damaged = NumericRuleMemory.restore(full.checkpoint())
            damaged.weights[5:] = [0] * 6
            for mask in HIDDEN:
                x = context(mask)
                y = oracle_truth(code, x)
                linear += only.predict(x) == y
                ablated += damaged.predict(x) == y
                zero += y == 0
        self.assertEqual((linear, ablated, zero), (5120, 5120, 5120))

    def test_all_cold_restores_and_no_gradient(self):
        for code in range(2048):
            model = NumericRuleMemory()
            for x, y in observations(code):
                model.observe(x, y)
            data = model.checkpoint()
            restored = NumericRuleMemory.restore(data)
            self.assertEqual(restored.checkpoint(), data)
            self.assertEqual(model.weights, restored.weights)
            for mask in HIDDEN:
                self.assertEqual(
                    model.predict(context(mask)),
                    restored.predict(context(mask)))
        self.assertEqual(GRADIENT_STEPS, 0)

    def test_public_evidence_only_and_safe_repeated_witness(self):
        model = NumericRuleMemory()
        with self.assertRaisesRegex(ValueError, "OUT_OF_ORDER"):
            model.observe(context(3), 1)
        self.assertEqual(model.weights, [0]*11)
        for x, y in observations(53):
            self.assertTrue(model.observe(x, y))
        old = model.checkpoint()
        self.assertTrue(model.observe(context(3), oracle_truth(53, context(3))))
        self.assertEqual(old, model.checkpoint())

    def test_true_contradiction_latches_without_rule_repair(self):
        for code in range(32):
            model = NumericRuleMemory()
            for x, y in observations(code):
                model.observe(x, y)
            weights_before = model.weights[:]
            self.assertFalse(model.observe(context(7),
                                            oracle_truth(code, context(7)) ^ 1))
            self.assertEqual(model.fault, 1)
            self.assertIsNone(model.predict(context(15)))
            self.assertEqual(model.weights, weights_before)
            self.assertFalse(model.observe(context(7), 0))

    def test_input_validation_and_canonical_checkpoints(self):
        model = NumericRuleMemory()
        bad = ((0,0,0), (False,0,0,0), [0,0,0,0], (0,0,0,2))
        for x in bad:
            with self.assertRaisesRegex(ValueError, "WSP12_INVALID_CONTEXT"):
                model.observe(x, 0)
        for value in (-1, 2, False, "0"):
            with self.assertRaisesRegex(ValueError, "WSP12_INVALID_OUTCOME"):
                model.observe(context(0), value)
        data = model.checkpoint()
        for bad_raw in (data[:-1], data+b"x", data[:-1]+bytes([data[-1]^1])):
            with self.assertRaisesRegex(ValueError, "WSP12_CHECKPOINT_REJECTED"):
                NumericRuleMemory.restore(bad_raw)
        model.weights[7] = 1
        with self.assertRaisesRegex(ValueError, "WSP12_NONCANONICAL_STATE"):
            model.checkpoint()

    def test_validly_digested_noncanonical_restore_fails(self):
        model = NumericRuleMemory()
        raw = model.checkpoint()
        obj = json.loads(raw[9:-32].decode("ascii"))
        obj["seen"][3] = 1
        body = json.dumps(obj, sort_keys=True, separators=(",", ":")).encode("ascii")
        prefix = MAGIC + len(body).to_bytes(4, "big") + body
        forged = prefix + hashlib.sha256(prefix).digest()
        with self.assertRaisesRegex(ValueError, "WSP12_CHECKPOINT_REJECTED"):
            NumericRuleMemory.restore(forged)


if __name__ == "__main__":
    unittest.main()
