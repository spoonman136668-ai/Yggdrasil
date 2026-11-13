"""DG1-MC01 focused source-only checks, not scientific acceptance."""
import unittest

from yggdrasil.local_causal_motif_dev import LocalCausalMotifDev


class LocalCausalMotifDevTests(unittest.TestCase):
    def test_fixed_cell_cap_and_initial_no_change(self):
        m = LocalCausalMotifDev()
        self.assertEqual((m.ACTIVE_SLOTS, m.RETAINED_SLOTS), (7, 9))
        self.assertEqual((m.WEIGHTS, m.LEARNED_BYTES), (28, 224))
        self.assertEqual(len(m.snapshot()), m.CHECKPOINT_BYTES)
        self.assertEqual(m.predict(10, 2), 10)
        self.assertEqual(m.updates, 0)

    def test_local_public_update_and_no_oracle(self):
        m = LocalCausalMotifDev()
        # Cell-0's left and right bits are public observations, not rules.
        for _ in range(10):
            m.observe(0b0010, 0, 0b0011)
            m.observe(0b1000, 0, 0b1000)
        self.assertEqual(m.updates, 20)
        self.assertTrue(any(abs(w) > 0 for w in m._weights[0]))
        self.assertEqual(m._weights[1], [0.0] * 4)
        self.assertEqual(m.predict(3, 2), 3)

    def test_no_neighbor_control_cannot_use_neighbor_coordinates(self):
        m = LocalCausalMotifDev(neighbor_features=False)
        for _ in range(16):
            m.observe(0b0010, 0, 0b0011)
        self.assertEqual(m._weights[0][1:], [0.0] * 3)
        self.assertFalse(m.neighbor_features)

    def test_invalid_public_transition_is_atomic(self):
        m = LocalCausalMotifDev()
        original = m.snapshot()
        bad = ((16, 0, 0), (0, 4, 0), (0, 0, 16),
               (0, 0, 2), (True, 0, 0), (0, False, 0),
               (0, 0, True))
        for before, action, after in bad:
            with self.subTest(before=before, action=action, after=after):
                with self.assertRaises(ValueError):
                    m.observe(before, action, after)
                self.assertEqual(m.snapshot(), original)
        with self.assertRaises(ValueError):
            m.predict(-1, 0)
        with self.assertRaises(ValueError):
            m.rollout(0, (1, 2, 3))

    def test_cold_restore_and_identical_future_updates(self):
        m = LocalCausalMotifDev()
        for a in (0, 1, 2, 3):
            m.observe(0, a, 1 << a)
        snap = m.snapshot()
        n = LocalCausalMotifDev.restore(snap)
        self.assertEqual(n.snapshot(), snap)
        for x in (m, n):
            x.observe(1, 2, 5)
        self.assertEqual(m.snapshot(), n.snapshot())
        for state in range(16):
            for a in range(4):
                self.assertEqual(m.predict(state, a), n.predict(state, a))
                self.assertEqual(m.rollout(state, [a, (a+1) % 4]),
                                 n.rollout(state, [a, (a+1) % 4]))

    def test_checkpoint_integrity_and_mode(self):
        m = LocalCausalMotifDev(neighbor_features=False)
        m.observe(0, 2, 4)
        snap = m.snapshot()
        self.assertFalse(LocalCausalMotifDev.restore(snap).neighbor_features)
        tampered = bytearray(snap)
        tampered[13] ^= 1
        for candidate in (bytes(tampered), snap[:-1], bytearray(snap),
                          b"FAIL" + snap[4:]):
            with self.subTest(candidate_type=str(type(candidate))):
                with self.assertRaises(ValueError):
                    LocalCausalMotifDev.restore(candidate)

    def test_budget_cannot_be_exceeded(self):
        m = LocalCausalMotifDev()
        for i in range(m.MAX_UPDATES):
            m.observe(0, i % 4, 0)
        frozen = m.snapshot()
        with self.assertRaisesRegex(ValueError, "BUDGET"):
            m.observe(0, 0, 0)
        self.assertEqual(m.snapshot(), frozen)


if __name__ == "__main__":
    unittest.main()
