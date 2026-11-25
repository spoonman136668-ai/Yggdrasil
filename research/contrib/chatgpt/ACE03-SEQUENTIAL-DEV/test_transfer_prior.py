"""Deterministic engineering fixtures, not scientific outcomes."""
import hashlib
import subprocess
import sys
import unittest
from pathlib import Path

from adaptive_contract import AdaptiveContract, LIMIT
from transfer_prior import TransferContract, HEADER, BLOCK, SLOT


def train(model, key, count, y):
    for _ in range(count):
        i = model.cursor
        model.observe(i,key,i%512,(y,)*4)
    return model


class TransferFixtures(unittest.TestCase):
    def test_original_independence_and_successor_influence(self):
        original = train(AdaptiveContract(),0,512,1)
        candidate = train(TransferContract(),0,512,1)
        self.assertEqual(original.predict(2,0),(.5,)*4)
        self.assertGreater(candidate.predict(2,0)[0],.5)
        self.assertEqual(candidate._rows[2][0].n,0)

    def test_old_context_snapshot_isolation(self):
        m = train(TransferContract(),0,512,1)
        old = tuple(m.predict(0,p) for p in range(512))
        train(m,1,512,0)
        self.assertEqual(old,tuple(m.predict(0,p) for p in range(512)))

    def test_conflicting_prior_loses_weight(self):
        m = train(TransferContract(),0,512,1)
        self.assertGreater(m.predict(1,0)[0],.5)
        train(m,1,128,0)
        self.assertLess(m._log_odds[1][0],0.)
        self.assertLess(m.predict(1,0)[0],.5)

    def test_fresh_process(self):
        m = train(TransferContract(),0,512,1)
        train(m,1,256,0)
        prefix = m.checkpoint()
        expected = train(m,2,256,1).checkpoint()
        code = ('import sys; sys.path.insert(0,sys.argv[1]); from test_transfer_prior import train, TransferContract; '
                'm=TransferContract.restore(sys.stdin.buffer.read()); '
                'sys.stdout.buffer.write(train(m,2,256,1).checkpoint())')
        child = subprocess.run([sys.executable, '-B', *(['-O'] if sys.flags.optimize else []),
                                '-c', code, str(Path(__file__).resolve().parent)],
                               input=prefix, capture_output=True, timeout=60)
        self.assertEqual(child.returncode, 0, child.stderr[:4096].decode('utf-8',errors='replace'))
        got = child.stdout
        self.assertEqual(expected,got)

    def test_read_only_and_invalid_event(self):
        m = train(TransferContract(),0,2,1)
        raw = m.checkpoint()
        m.predict(2,0)
        self.assertIsNone(m.predict(None,0))
        for args in [(0,0,0,(0,)*4),(2,0,512,(0,)*4),(2,None,0,(0,)*4),
                     (2,0,0,(0,)*3),(2,0,0,(0,0,0,True))]:
            with self.assertRaises(ValueError): m.observe(*args)
            self.assertEqual(raw,m.checkpoint())

    def test_capacity_and_corruption(self):
        m = TransferContract()
        raw = m.checkpoint()
        self.assertEqual(len(raw),HEADER.size+BLOCK+3*SLOT+32)
        self.assertLessEqual(len(raw),15412)
        self.assertEqual(TransferContract.restore(raw).checkpoint(),raw)
        for invalid in (raw[:-1],raw+b'x',b'x'+raw[1:]):
            with self.assertRaises(ValueError): TransferContract.restore(invalid)
        payload = bytearray(raw[:-32])
        payload[HEADER.size+BLOCK] = 1
        with self.assertRaises(ValueError):
            TransferContract.restore(bytes(payload)+hashlib.sha256(payload).digest())

    def test_shared_limit(self):
        m = TransferContract(1)
        for a in m._rows[0]+m._shared:
            a.n,a.pair = LIMIT,0
        m._prior[0] = [type(a)() for a in m._shared]
        m.cursor = LIMIT
        m = TransferContract.restore(m.checkpoint())
        raw = m.checkpoint()
        with self.assertRaises(ValueError): m.observe(LIMIT,0,0,(0,)*4)
        self.assertEqual(raw,m.checkpoint())


if __name__ == '__main__': unittest.main()
