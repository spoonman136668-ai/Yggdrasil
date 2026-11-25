import hashlib
import subprocess
import sys
import unittest
from fractions import Fraction
from shared_count_control import SharedCountControl, HEADER, CELL, LIMIT


def stream(model, begin, end):
    for seq in range(begin, end):
        key, pattern = seq % 3, (seq * 31) % 512
        bits = tuple((seq >> j) & 1 for j in range(4))
        model.observe(seq, key, pattern, bits)
    return model


class SharedCountTests(unittest.TestCase):
    def test_exact_reference(self):
        m = SharedCountControl()
        counts = {}
        for i in range(3072):
            key, pattern = i % 3, (i * 31) % 512
            bits = tuple((i >> j) & 1 for j in range(4))
            row = counts.setdefault((key, pattern), [[0, 0] for _ in range(4)])
            self.assertEqual(m.predict(key, pattern), tuple(Fraction(k + 1, n + 2) for n, k in row))
            m.observe(i, key, pattern, bits)
            for j, y in enumerate(bits):
                row[j][0] += 1
                row[j][1] += y
        for (key, pattern), row in counts.items():
            self.assertEqual(m.predict(key, pattern), tuple(Fraction(k + 1, n + 2) for n, k in row))

    def test_fresh_process_continuation(self):
        prefix = stream(SharedCountControl(), 0, 1536).checkpoint()
        expected = stream(SharedCountControl(), 0, 3072).checkpoint()
        code = ('import sys; from test_shared_count_control import stream, SharedCountControl; '
                'm=SharedCountControl.restore(sys.stdin.buffer.read()); '
                'sys.stdout.buffer.write(stream(m,1536,3072).checkpoint())')
        p = subprocess.run([sys.executable, '-B', '-c', code], input=prefix, capture_output=True, check=True)
        self.assertEqual(p.stdout, expected)

    def test_prediction_collision(self):
        a, b = SharedCountControl(), SharedCountControl()
        a.observe(0, 0, 0, (0,)*4)
        for i in range(64):
            b.observe(i, 0, 0, (int(i < 21),)*4)
        self.assertEqual(a.predict(0, 0), b.predict(0, 0))
        self.assertNotEqual(a.checkpoint(), b.checkpoint())
        a.observe(1, 0, 0, (1,)*4)
        b.observe(64, 0, 0, (1,)*4)
        self.assertEqual(a.predict(0, 0)[0], Fraction(1, 2))
        self.assertEqual(b.predict(0, 0)[0], Fraction(23, 67))

    def test_invalid_events_atomic(self):
        m = stream(SharedCountControl(), 0, 1)
        before = m.checkpoint()
        for args in [(0,0,0,(0,)*4),(2,0,0,(0,)*4),(1,3,0,(0,)*4),
                     (1,0,512,(0,)*4),(1,0,0,(0,)*3),(1,0,0,(0,0,0,None)),
                     (1,0,0,(0,0,0,True)),(True,0,0,(0,)*4)]:
            with self.assertRaises(ValueError): m.observe(*args)
            self.assertEqual(m.checkpoint(), before)

    def test_overflow_atomic(self):
        m = SharedCountControl(1)
        for i in range(LIMIT): m.observe(i, 0, 0, (1,0,1,0))
        before = m.checkpoint()
        with self.assertRaises(OverflowError): m.observe(LIMIT, 0, 0, (0,)*4)
        self.assertEqual(m.checkpoint(), before)

    def test_corruption_and_semantic_validation(self):
        raw = stream(SharedCountControl(), 0, 1).checkpoint()
        for invalid in (raw[:-1], raw + b'x', b'x'+raw[1:]):
            with self.assertRaises(ValueError): SharedCountControl.restore(invalid)
        for offset, replacement in [(HEADER.size+2, b'\xff\xff'), (12, b'\x02')]:
            payload = bytearray(raw[:-32]); payload[offset:offset+len(replacement)] = replacement
            with self.assertRaises(ValueError): SharedCountControl.restore(bytes(payload)+hashlib.sha256(payload).digest())

    def test_size_and_read_only(self):
        m = SharedCountControl()
        raw = m.checkpoint()
        self.assertEqual(len(raw), 3*512*10+HEADER.size+32)
        self.assertEqual(SharedCountControl.restore(raw).checkpoint(), raw)
        m.predict(2, 511)
        self.assertEqual(m.checkpoint(), raw)

if __name__ == '__main__': unittest.main()
