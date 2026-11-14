"""Source-free structural tests only; NEVER construct WSP98 registered worlds."""
import json
import unittest
from core import (ACTIONS, D, N, PASSIVE_ROWS, DirectWeights, canonical, digest,
                  phi, random_query, result_of, state)

class WSP98CoreTests(unittest.TestCase):
    def test_basis_and_handcoded_causal_gate(self):
        x = (0, 1, 0, 1, 0, 1)
        self.assertEqual(len(phi(x)), 22)
        self.assertEqual(phi(x)[0], 1.0)
        program = ((0, 1, 0, 0, 'AND'), (0, 1, 0, 0, 'OR'),
                   (0, 1, 0, 0, 'XOR'), (0, 1, 0, 0, 'XNOR'),
                   (0, 1, 0, 0, 'NAND'), (0, 1, 0, 0, 'NOR'))
        self.assertEqual(result_of(x, program), (0, 1, 1, 0, 1, 0))
        self.assertEqual(result_of(x, program), result_of(x, program))
        with self.assertRaises(ValueError): state((1, 0))

    def test_no_gradient_full_capacity_and_exact_cold_restore(self):
        m = DirectWeights()
        x = (0, 0, 0, 0, 0, 0)
        y = (0, 1, 0, 1, 0, 1)
        for i in range(PASSIVE_ROWS + ACTIONS):
            m.observe(x, y, expected_index=i)
        self.assertEqual(len(m.w) * len(m.w[0]) + len(m.p) * len(m.p[0]), 616)
        saved = m.snapshot()
        loaded = DirectWeights.restore(saved)
        self.assertEqual(loaded.predict(x), m.predict(x))
        self.assertEqual(loaded.snapshot(), saved)
        with self.assertRaises(ValueError): m.observe(x, y, expected_index=32)
        self.assertIsNone(m.predict((2, 0, 0, 0, 0, 0)))
        forged = json.loads(saved)
        forged['data']['w'][0][0] += 2
        with self.assertRaises(ValueError): DirectWeights.restore(canonical(forged))

    def test_source_blind_feature_only_probe(self):
        m = DirectWeights()
        passive = tuple((0, 0, 0, 0, 0, i % 2) for i in range(PASSIVE_ROWS))
        for i, x in enumerate(passive):
            m.observe(x, (1, 1, 1, 1, 1, 1), expected_index=i)
        q = m.choose(passive, 999, 0)  # 999 is a fixture, not public/reserve
        self.assertEqual(q[2], 1-passive[q[0]][q[1]])
        self.assertEqual(q, m.choose(passive, 999, 0))
        with self.assertRaises(ValueError): m.choose(passive, 999, 1)
        self.assertEqual(random_query(999, 0, passive), random_query(999, 0, passive))

    def test_pure_source_only_no_cohort_access(self):
        import pathlib
        src = pathlib.Path(__file__).with_name('core.py').read_text(encoding='utf-8')
        self.assertNotIn('98101', src)
        self.assertNotIn('98011', src)
        self.assertNotIn('prereg.json', src)
        self.assertNotIn('torch', src)
        self.assertNotIn('numpy', src)

if __name__ == '__main__': unittest.main()
