"""WSP53 conventional-control contract tests: SELFTEST only, not convergence."""
import json
import unittest
from dataclasses import replace
from conventional import RawBitRNN, Row, HIDDEN, MAX_PARAMETERS, MAX_UPDATES
from source import build_world

class ConventionalContracts(unittest.TestCase):
    def test_dimensions_gradients_and_determinism(self):
        for family in ("anchored_effect","noncommuting_order"):
            world=build_world(family,"SELFTEST",9901,"identity")
            m=RawBitRNN(family=family)
            twin=RawBitRNN(family=family)
            self.assertEqual(m.parameter_count(),twin.parameter_count())
            self.assertLessEqual(m.parameter_count(),MAX_PARAMETERS)
            for row in world.phase_a:
                m.observe(row);twin.observe(row)
            with self.assertRaises(ValueError):
                m.observe(world.phase_a[0])
            m.seal_a();twin.seal_a()
            first=m.snapshot()
            m.train(2);twin.train(2)
            self.assertNotEqual(first,m.snapshot())
            self.assertEqual(m.snapshot(),twin.snapshot())
            self.assertTrue(0<=m.train_diagnostic()["accuracy"]<=1)
            self.assertEqual(m.predict(world.phase_a[0].before,
                                      world.phase_a[0].acoustic_bits),
                             RawBitRNN.restore(m.snapshot()).predict(
                                     world.phase_a[0].before,world.phase_a[0].acoustic_bits))
            for row in world.phase_b:
                m.observe(row)
            self.assertEqual(len(m.rows),60)
            with self.assertRaises(ValueError):
                m.observe(world.phase_b[0])
            self.assertEqual(RawBitRNN.restore(m.snapshot()).capacity_bits(),m.capacity_bits())

    def test_rejects_invalid_state_and_tamper(self):
        m=RawBitRNN(family="anchored_effect")
        b=(0,)*16
        r=Row(b,"011010101001",(1,)+(0,)*15)
        for bad in (replace(r,action_cost=0),replace(r,reset_cost=1),
                    replace(r,before=b[:-1]),replace(r,acoustic_bits="abc")):
            with self.assertRaises(ValueError):
                m.observe(bad)
        self.assertEqual(len(m.rows),0)
        with self.assertRaises(ValueError):
            m.train(1)
        for _ in range(48):
            m.observe(r)
        with self.assertRaises(ValueError):
            m.train(MAX_UPDATES+1)
        with self.assertRaises(ValueError):
            m.seal_a() if m.phase_b else m.observe(r)
        m.seal_a()
        x=json.loads(m.snapshot())
        x["payload"]["weights"]["init"][0]=999.0
        with self.assertRaises(ValueError):
            RawBitRNN.restore(json.dumps(x))

if __name__=="__main__":
    unittest.main()
