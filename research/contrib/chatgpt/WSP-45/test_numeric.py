import unittest
from numeric import NumericLearner,ActionModel


class Tests(unittest.TestCase):
    def test_numeric_address_winner_order(self):
        model=NumericLearner(4);visited=[]
        for _ in range(16):
            address=model.choose();visited.append(address);model.observe(address,address)
        self.assertEqual(visited,sorted(range(16),key=lambda i:(i.bit_count(),i)))
        self.assertIsNone(model.choose())

    def test_linear_unseen_generalization(self):
        m=NumericLearner(4)
        def f(x):return ((x&3).bit_count()%2)*7 ^ ((x>>2&1)*8) ^ 2
        for _ in range(5):
            x=m.choose();m.observe(x,f(x))
        self.assertEqual([m.predict(x) for x in range(16)],[f(x) for x in range(16)])
        self.assertTrue(m.canonical())

    def test_full_arbitrary_compile_and_point_repair(self):
        m=NumericLearner(4);truth=[(x*x+3*x+7)%16 for x in range(16)]
        for _ in range(16):
            x=m.choose();m.observe(x,truth[x])
        self.assertEqual([m.predict(x) for x in range(16)],truth)
        truth[9]^=4;m.observe(9,truth[9])
        self.assertEqual(m.fault,1)
        self.assertEqual([m.predict(x) for x in range(16)],truth)

    def test_idempotence_and_numeric_certificate(self):
        m=NumericLearner(4);m.observe(3,7);snap=m.snapshot();m.observe(3,7)
        self.assertEqual(m.snapshot(),snap)
        self.assertEqual(sum(any(r) for r in m.coefficients()),0)
        self.assertEqual(m.partial[3],[1,1,1,0])

    def test_cold_replay_and_corruption(self):
        m=NumericLearner(4)
        for _ in range(5):
            x=m.choose();m.observe(x,x^3)
        snap=m.snapshot();r=NumericLearner.restore(snap)
        self.assertEqual(r.snapshot(),snap)
        self.assertEqual([r.predict(x) for x in range(16)],[m.predict(x) for x in range(16)])
        with self.assertRaises(ValueError):NumericLearner.restore(snap+b'x')
        with self.assertRaises(ValueError):m.observe(-1,0)
        with self.assertRaises(ValueError):m.observe(1,16)

    def test_memory_lesion_suppresses_information(self):
        m=NumericLearner(4);m.observe(0,7)
        self.assertEqual(m.predict(15),7)
        erased=NumericLearner(4)
        self.assertEqual(erased.predict(15),0)


if __name__=='__main__':unittest.main()
