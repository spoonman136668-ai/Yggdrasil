"""Nonstudy engineering parity and rollback fixtures for internal state copies."""
import unittest
from unittest.mock import patch

from adaptive_contract import State
from transfer_prior import TransferContract, clone


def legacy_clone(rows):
    return [State.unpack(a.pack()) for a in rows]


class TransactionCopyFixtures(unittest.TestCase):
    def test_copy_independence(self):
        a = State()
        for i in range(400):
            a.update(i % 512, i % 2)
        c = clone([a])[0]
        self.assertEqual(a.pack(), c.pack())
        for attr in ('corr', 'w', 'loss'):
            self.assertIsNot(getattr(a, attr), getattr(c, attr))
        before = a.pack()
        c.update(17, 1)
        self.assertEqual(a.pack(), before)

    def test_legacy_parity(self):
        fast, legacy = TransferContract(), TransferContract()
        # Generic deterministic fixture; never invoke the study generator.
        for i in range(1800):
            k = (i // 300) % 3
            p = (i * 31 + 7) % 512
            y = tuple((i >> j) & 1 for j in range(4))
            self.assertEqual(fast.predict(k, p), legacy.predict(k, p))
            fast.observe(i, k, p, y)
            with patch('transfer_prior.clone', legacy_clone):
                legacy.observe(i, k, p, y)
            self.assertEqual(fast.checkpoint(), legacy.checkpoint())
            if i in (299, 899, 1499):
                fast = TransferContract.restore(fast.checkpoint())
                legacy = TransferContract.restore(legacy.checkpoint())
                for key in range(3):
                    for pattern in range(512):
                        self.assertEqual(fast.predict(key, pattern),
                                         legacy.predict(key, pattern))

    def test_partial_update_failure_rolls_back(self):
        m = TransferContract()
        for i in range(300):
            m.observe(i, 0, i % 512, (1, 0, 1, 0))
        before = m.checkpoint()
        original = State.update
        for key in (0, 1):
            for failure_at in (2, 5, 8):
                calls = 0
                def fail_after_update(state, pattern, y):
                    nonlocal calls
                    original(state, pattern, y)
                    calls += 1
                    if calls == failure_at:
                        raise RuntimeError('injected transaction failure')
                with patch.object(State, 'update', fail_after_update):
                    with self.assertRaises(RuntimeError):
                        m.observe(m.cursor, key, 42, (0, 1, 0, 1))
                self.assertEqual(calls, failure_at)
                self.assertEqual(m.checkpoint(), before)


if __name__ == '__main__':
    unittest.main()
