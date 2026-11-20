"""KNOW35 mock-only controls: no HELD seeds, proof or private source access."""
import json
import unittest

from know33_local_metaplastic_dev import canonical, digest
from know34_local_contradiction_dev import private_law_bit
from know35_two_regime_bank_dev import TwoBankCells


def public_x(t):
    # Same deterministic 16-pair public support as KNOW34; no private source.
    c, a = t % 8, (t // 8) % 2
    return c ^ (a << 1)


class Know35MockOnly(unittest.TestCase):
    def test_two_regimes_survive_a_b_a_b_without_oracle_gate(self):
        model = TwoBankCells()
        uninterrupted = TwoBankCells()
        old_a = None
        old_b = None
        for t in range(256):
            x = public_x(t)
            law = "B1" if (64 <= t < 128 or 192 <= t < 256) else "A"
            model.observe(t, x, private_law_bit(law, x))
            uninterrupted.observe(t, x, private_law_bit("A", x))
            if t == 63:
                old_a = [model.bank_prob(0, i) for i in range(8)]
                self.assertEqual(model.active, [0, 0, 0, 0])
            if t == 127:
                old_b = [model.bank_prob(1, i) for i in range(4, 8)]
                self.assertEqual(model.active, [0, 0, 1, 1])
                self.assertEqual([model.bank_prob(0, i) for i in range(8)], old_a)
            if t == 191:
                self.assertEqual(model.active, [0, 0, 0, 0])
                self.assertEqual([model.bank_prob(1, i) for i in range(4, 8)],
                                 old_b)
                self.assertEqual(model.checkpoint(),
                                 TwoBankCells.restore(model.checkpoint(),
                                                      digest(model.checkpoint())).checkpoint())
        self.assertEqual(model.active, [0, 0, 1, 1])
        self.assertEqual(model.switches, 6)
        self.assertEqual([model.bank_prob(0, i) for i in range(8)], old_a)
        self.assertEqual([model.bank_prob(1, i) for i in range(4, 8)], old_b)
        self.assertEqual([uninterrupted.prob(i) for i in range(8)], old_a)
        for x in range(8):
            # Functionally correct readout on this noise-free mock only.
            expected = private_law_bit("B1", x)
            self.assertEqual(model.prob(x) > 0.5, bool(expected))
        restored = TwoBankCells.restore(model.checkpoint(), digest(model.checkpoint()))
        self.assertEqual(restored.checkpoint(), model.checkpoint())
        self.assertEqual([restored.prob(x) for x in range(8)],
                         [model.prob(x) for x in range(8)])
        self.assertLess(len(model.checkpoint()), 4096)

    def test_reject_invalid_events_and_corrupt_cold_state(self):
        m = TwoBankCells()
        for args in [(1, 0, 0), (0, 8, 1), (0, 0, 2),
                     (0, 0, True), (0, False, 1)]:
            with self.subTest(args=args), self.assertRaises(ValueError):
                m.observe(*args)
        m.observe(0, 0, 1)
        raw = m.checkpoint()
        with self.assertRaises(ValueError):
            TwoBankCells.restore(raw + b"x", digest(raw))
        with self.assertRaises(ValueError):
            TwoBankCells.restore(raw, "0" * 64)
        data = json.loads(raw)
        data["seen"][0][0] = 6
        tampered = canonical(data)
        with self.assertRaises(ValueError):
            TwoBankCells.restore(tampered, digest(tampered))
        duplicate = raw.replace(b'"schema":', b'"schema":"bad","schema":', 1)
        with self.assertRaises(ValueError):
            TwoBankCells.restore(duplicate, digest(duplicate))
        with self.assertRaises(ValueError):
            m.bank_prob(True, 0)


if __name__ == "__main__":
    unittest.main()
