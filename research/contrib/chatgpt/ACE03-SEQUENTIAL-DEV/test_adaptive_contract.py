import hashlib
import subprocess
import sys
import unittest
from pathlib import Path
from adaptive_contract import AdaptiveContract, HEADER, ROW, WARMUP, GATE, LIMIT


def stream(model, begin, end):
    for i in range(begin, end):
        key, pattern = i % 3, (i*31) % 512
        model.predict(key, pattern)
        model.observe(i, key, pattern, tuple((i >> j)&1 for j in range(4)))
    return model


class EngineeringFixtures(unittest.TestCase):
    def test_cold_continuation(self):
        prefix = stream(AdaptiveContract(), 0, 900).checkpoint()
        expected = stream(AdaptiveContract(), 0, 1800).checkpoint()
        code = ('import sys; sys.path.insert(0,sys.argv[1]); from test_adaptive_contract import stream, AdaptiveContract; '
                'm=AdaptiveContract.restore(sys.stdin.buffer.read()); '
                'sys.stdout.buffer.write(stream(m,900,1800).checkpoint())')
        child = subprocess.run([sys.executable, '-B', *(['-O'] if sys.flags.optimize else []),
                                '-c', code, str(Path(__file__).resolve().parent)],
                               input=prefix, capture_output=True, timeout=60)
        self.assertEqual(child.returncode, 0, child.stderr[:4096].decode('utf-8',errors='replace'))
        out = child.stdout
        self.assertEqual(out, expected)

    def test_context_isolation(self):
        m = AdaptiveContract()
        for i in range(300):
            m.observe(i, 0, i % 512, (1,0,1,0))
        prior = tuple(m.predict(0, p) for p in range(512))
        state = tuple(a.pack() for a in m._rows[0])
        for i in range(300, 600):
            m.observe(i, 1, i % 512, (0,1,0,1))
        self.assertEqual(prior, tuple(m.predict(0, p) for p in range(512)))
        self.assertEqual(state, tuple(a.pack() for a in m._rows[0]))

    def test_gate_and_abstention(self):
        m = AdaptiveContract()
        for i in range(WARMUP+GATE-1):
            m.observe(i, 0, i % 512, (1,0,1,0))
        self.assertEqual(m.kinds(0), ('pool',)*4)
        self.assertIsNone(m.predict(None, 0))
        self.assertEqual(m._rows[0][0].n, WARMUP+GATE-1)

    def test_atomic_rejection(self):
        m = stream(AdaptiveContract(), 0, 1)
        before = m.checkpoint()
        for args in [(0,0,0,(0,)*4),(2,0,0,(0,)*4),(1,None,0,(0,)*4),
                     (1,0,512,(0,)*4),(1,0,0,(0,)*3),(1,0,0,(0,0,0,None)),
                     (1,0,0,(0,0,0,True)),(True,0,0,(0,)*4)]:
            with self.assertRaises(ValueError): m.observe(*args)
            self.assertEqual(m.checkpoint(), before)

    def test_same_readout_different_state(self):
        a, b = AdaptiveContract(), AdaptiveContract()
        b.observe(0, 0, 0, (0,)*4)
        b.observe(1, 0, 0, (1,)*4)
        self.assertEqual(a.predict(0,0), b.predict(0,0))
        self.assertNotEqual(a.checkpoint(), b.checkpoint())
        a.observe(0,0,0,(1,)*4)
        b.observe(2,0,0,(1,)*4)
        self.assertNotEqual(a.predict(0,0), b.predict(0,0))

    def test_overflow_atomic(self):
        m = AdaptiveContract(1)
        for a in m._rows[0]:
            a.n, a.pair = LIMIT, 0
        m.cursor = LIMIT
        m = AdaptiveContract.restore(m.checkpoint())
        before = m.checkpoint()
        with self.assertRaises(OverflowError): m.observe(LIMIT,0,0,(0,)*4)
        self.assertEqual(m.checkpoint(), before)

    def test_checkpoint_validation(self):
        raw = stream(AdaptiveContract(), 0, 1).checkpoint()
        for invalid in (raw[:-1], raw+b'x', b'x'+raw[1:]):
            with self.assertRaises(ValueError): AdaptiveContract.restore(invalid)
        payload = bytearray(raw[:-32])
        payload[HEADER.size+2:HEADER.size+4] = b'\xff\xff'
        with self.assertRaises(ValueError):
            AdaptiveContract.restore(bytes(payload)+hashlib.sha256(payload).digest())

    def test_size_and_predict_readonly(self):
        m = AdaptiveContract()
        raw = m.checkpoint()
        self.assertEqual(len(raw), HEADER.size+3*4*ROW.size+32)
        self.assertEqual(AdaptiveContract.restore(raw).checkpoint(), raw)
        m.predict(2,511)
        self.assertEqual(m.checkpoint(), raw)


if __name__ == '__main__': unittest.main()
