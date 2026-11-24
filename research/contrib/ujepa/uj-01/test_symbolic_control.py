import unittest
from fractions import Fraction
from symbolic_control import arithmetic, scores, Unsupported


class SymbolicTests(unittest.TestCase):
    def test_exact(self):
        self.assertEqual(arithmetic(b'0.1 + 0.2'), Fraction(3, 10))
        self.assertEqual(arithmetic(b'-(2+3)/4'), Fraction(-5, 4))
        self.assertEqual(arithmetic(b'2+3*4'), 14)

    def test_choice(self):
        self.assertEqual(scores(b'2+3?', [b'4', b'5', b'6']), ([0., 20., 0.], True))

    def test_abstains(self):
        for context, options in [(b'How many apples?', [b'1', b'2']),
                                 (b'1+1', [b'1', b'3']),
                                 (b'1+1', [b'2', b'4/2']),
                                 (b'1+1', [b'2', b'none'])]:
            self.assertEqual(scores(context, options), ([0., 0.], False))

    def test_rejection(self):
        for raw in (b'1/0', b'2**100', b'1//2', b'__import__("os")', b'1,2', b'9'*129, b'9'*100):
            with self.assertRaises(Unsupported):
                arithmetic(raw)


if __name__ == '__main__':
    unittest.main()
