"""WSP-10 deterministic controls and negative checks."""
import hashlib
import json
import unittest

from crossbar import DirectCrossbar, GRADIENT_STEPS


class DirectCrossbarTests(unittest.TestCase):
    def test_full_representability_and_symbolic_control(self):
        count = 0
        for n in (2, 3):
            for mask in range(1 << (1 << n)):
                c = DirectCrossbar.from_spec(n, mask)
                for i in range(1 << n):
                    bits = tuple((i >> k) & 1 for k in range(n))
                    self.assertEqual(c.evaluate(bits), (mask >> i) & 1)
                    count += 1
        self.assertEqual(count, 2112)

    def test_all_task_specific_weights_initially_zero(self):
        for n in (2, 3):
            c = DirectCrossbar(n)
            self.assertEqual(c.active_connections(), 0)
            self.assertTrue(all(c.evaluate(tuple((i >> j) & 1 for j in range(n))) == 0
                                for i in range(1 << n)))

    def test_program_connectivity_budget(self):
        self.assertEqual(len(DirectCrossbar(3).weights), 56)
        self.assertEqual(len(DirectCrossbar(2).weights), 20)
        self.assertEqual(DirectCrossbar.from_spec(3, 255).active_connections(), 32)
        self.assertEqual(DirectCrossbar.from_spec(3, 0).active_connections(), 0)

    def test_gate_to_output_ablation(self):
        detected = 0
        for n in (2, 3):
            for mask in range(1, 1 << (1 << n)):
                c = DirectCrossbar.from_spec(n, mask)
                i = next(i for i in range(1 << n) if (mask >> i) & 1)
                c.weights[i*c.stride + 2*n] = 0
                detected += c.evaluate(tuple((i >> j) & 1 for j in range(n))) == 0
        self.assertEqual(detected, 270)

    def test_snapshot_restore_every_world(self):
        for n in (2, 3):
            for mask in range(1 << (1 << n)):
                c = DirectCrossbar.from_spec(n, mask)
                raw = c.snapshot()
                self.assertEqual(DirectCrossbar.restore(raw).snapshot(), raw)

    def test_snapshot_tamper_rejected(self):
        c = DirectCrossbar.from_spec(3, 0b10111010)
        raw = c.snapshot()
        with self.assertRaisesRegex(ValueError, "WSP10_CHECKPOINT_REJECTED"):
            DirectCrossbar.restore(raw[:-1]+bytes([raw[-1]^1]))
        with self.assertRaisesRegex(ValueError, "WSP10_CHECKPOINT_REJECTED"):
            DirectCrossbar.restore(raw+b"x")

    def test_correctly_digested_noncanonical_checkpoint_rejected(self):
        c = DirectCrossbar.from_spec(3, 2)
        raw = c.snapshot()
        data = json.loads(raw[8:-32].decode("ascii"))
        data["weights"][0] = 1
        body = json.dumps(data, sort_keys=True, separators=(",", ":")).encode("ascii")
        prefix = b"WSPX"+len(body).to_bytes(4, "big")+body
        forged = prefix+hashlib.sha256(prefix).digest()
        with self.assertRaisesRegex(ValueError, "WSP10_CHECKPOINT_REJECTED"):
            DirectCrossbar.restore(forged)

    def test_invalid_dimensions_masks_and_inputs(self):
        for n, mask in ((1, 0), (4, 0), (3, 256), (3, -1), (3, True), (True, 0)):
            with self.assertRaises(ValueError):
                DirectCrossbar.from_spec(n, mask)
        c = DirectCrossbar(3)
        for bits in ((0,1,0,1), (0,1), (0,True,1), [0,1,0], (0,-1,0)):
            with self.assertRaisesRegex(ValueError, "WSP10_INVALID_INPUT_BITS"):
                c.evaluate(bits)

    def test_input_bit_permutation_is_a_real_negative(self):
        c = DirectCrossbar.from_spec(3, 2)
        self.assertEqual(c.evaluate((1, 0, 0)), 1)
        self.assertEqual(c.evaluate((0, 1, 0)), 0)

    def test_no_gradient_and_predict_does_not_change_weights(self):
        c = DirectCrossbar.from_spec(3, 0x69)
        old = c.programmed_sha256()
        for i in range(8):
            c.evaluate(tuple((i >> j) & 1 for j in range(3)))
        self.assertEqual(c.programmed_sha256(), old)
        self.assertEqual(GRADIENT_STEPS, 0)

    def test_independent_instances(self):
        a = DirectCrossbar.from_spec(3, 1)
        b = DirectCrossbar.from_spec(3, 2)
        self.assertNotEqual(a.programmed_sha256(), b.programmed_sha256())
        a.weights[2*3] = 0
        self.assertEqual(b.evaluate((1,0,0)), 1)

    def test_fixed_architecture_identity_and_clean_compiler(self):
        a = DirectCrossbar(3)
        b = DirectCrossbar.from_spec(3, 255)
        self.assertEqual(a.architecture_sha256, b.architecture_sha256)
        self.assertNotEqual(a.programmed_sha256(), b.programmed_sha256())
        with self.assertRaisesRegex(ValueError, "WSP10_NONCANONICAL_WEIGHTS"):
            b.weights[0] = 3
            b.snapshot()


if __name__ == "__main__":
    unittest.main()
