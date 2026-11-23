"""Engineering-only fixtures; none of the frozen primary seeds are consumed."""
import hashlib
import json
import unittest
from cce02 import IdentityEcology, posterior, validate, TRAIN_LIMIT


class CCE02Tests(unittest.TestCase):
    @staticmethod
    def fixed_fixture(positive=True):
        for _ in range(64):
            for p in (0, 1):
                for z in (0, 1):
                    for t in (0, 1):
                        # Probe 0 reveals terminal reward identity; probe 1
                        # independent of identity, balanced per tuple via cycle.
                        h = z if (p == 0 and positive) else (_ % 2)
                        yield p, z, t, int(t == h)

    def test_prior_and_invalid_public_event(self):
        ec = IdentityEcology()
        self.assertEqual(0.5, ec.p_reward(1, probe=0, observation=0))
        self.assertEqual(0.5, ec.p_reward(0))
        for args in ((0, 1, True, 0), (0, 2, 1, 0), (0, 1, 1, None),
                     (0, '0', 1, 1), (-1, 1, 1, 1)):
            with self.assertRaises(ValueError):
                ec.observe(*args)
        self.assertEqual(0, ec.events)

    def test_empty_freeze_forbidden(self):
        ec = IdentityEcology()
        with self.assertRaises(ValueError):
            ec.freeze()
        with self.assertRaises(ValueError):
            ec.choose_probe()

    def test_positive_hand_fixture_admits_probe_zero(self):
        ec = IdentityEcology()
        for event in self.fixed_fixture(positive=True):
            ec.observe(*event)
        self.assertEqual(TRAIN_LIMIT, ec.events)
        self.assertEqual(0, ec.freeze())
        self.assertEqual(0, ec.choose_probe())
        self.assertEqual(0, ec.choose(0))
        self.assertEqual(1, ec.choose(1))
        with self.assertRaises(ValueError):
            ec.observe(0, 0, 0, 1)

    def test_negative_hand_fixture_no_spurious_claim(self):
        ec = IdentityEcology()
        for event in self.fixed_fixture(positive=False):
            ec.observe(*event)
        self.assertIsNone(ec.freeze())
        self.assertEqual(1, ec.choose_probe())

    def test_exact_cold_continuity_and_tamper(self):
        ec = IdentityEcology()
        for event in self.fixed_fixture():
            ec.observe(*event)
        ec.freeze()
        snapshot = ec.snapshot()
        restored = IdentityEcology.restore(snapshot)
        self.assertEqual(snapshot, restored.snapshot())
        self.assertEqual(ec.choose_probe(), restored.choose_probe())
        for p in (0, 1):
            for z in (0, 1):
                for t in (0, 1):
                    self.assertEqual(ec.p_reward(t, probe=p, observation=z),
                                     restored.p_reward(t, probe=p, observation=z))
        bad = bytearray(snapshot)
        bad[-1] ^= 0x01
        with self.assertRaises(ValueError):
            IdentityEcology.restore(bytes(bad))

    def test_semantically_forged_checksum_rejected(self):
        ec = IdentityEcology()
        ec.observe(0, 1, 0, 1)
        state = json.loads(ec.snapshot().split(b'.', 2)[2])
        state['pooled'][0][1] += 1
        raw = json.dumps(state, sort_keys=True, separators=(',', ':')).encode('ascii')
        forged = b'CCE02.' + hashlib.sha256(raw).hexdigest().encode('ascii') + b'.' + raw
        with self.assertRaisesRegex(ValueError, 'CCE02_CHECKPOINT_REJECTED'):
            IdentityEcology.restore(forged)

    def test_frozen_budget_and_prediction_guards(self):
        ec = IdentityEcology()
        for event in self.fixed_fixture():
            ec.observe(*event)
        with self.assertRaises(ValueError):
            ec.observe(0, 0, 0, 0)
        ec.freeze()
        with self.assertRaises(ValueError):
            ec.freeze()
        with self.assertRaises(ValueError):
            ec.choose_terminal(2, 0)

    def test_sham_signal_no_supervised_hidden_identity(self):
        ec = IdentityEcology()
        self.assertEqual(4, len(ec.signatures) * len(ec.signatures[0]))
        self.assertFalse(hasattr(ec, 'hidden_regime'))
        with self.assertRaises(ValueError):
            validate(0, 1, 1, 3)

if __name__ == '__main__':
    unittest.main()
