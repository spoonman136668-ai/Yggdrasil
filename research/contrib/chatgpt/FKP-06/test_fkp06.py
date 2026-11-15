import importlib.util
from pathlib import Path
import unittest
spec=importlib.util.spec_from_file_location('fkp06',str(Path(__file__).with_name('fkp06.py')))
mod=importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)

class FKP06Tests(unittest.TestCase):
    def test_finite_family_four_essential_parents(self):
        hypotheses=mod.laws()
        self.assertEqual(len(hypotheses),107880)
        for law in (hypotheses[0],hypotheses[10000],hypotheses[-1]):
            self.assertEqual(len(set(law)),4)
            for i in law:
                others=sum(1 << k for k in law if k != i)
                self.assertTrue(any(mod.consequence(law, a) != mod.consequence(law,a ^ (1 << i))
                                    for a in (others, others | (1 << i), 0)))
    def test_public_held_disjoint_and_deterministic(self):
        x,y=mod.inputs()
        self.assertEqual((len(x),len(y),len(set(x+y))),(128,256,384))
        self.assertEqual((x,y),mod.inputs())
        self.assertEqual(mod.secret_index(700),mod.secret_index(700))
        with self.assertRaises(AssertionError):mod.secret_index(1700)
    def test_paid_actions_bounded(self):
        w=mod.PublicWorld(700,mod.laws(),2)
        self.assertIn(w.observe(0),(0,1))
        with self.assertRaises(ValueError):w.observe(0)
        with self.assertRaises(ValueError):w.evaluator_truth([0])
        w.observe(1)
        with self.assertRaises(ValueError):w.observe(2)
        self.assertEqual(len(w.evaluator_truth([0,1])),2)
    def test_reference_preserves_true_law(self):
        h=mod.laws()
        a=0xAAAA5555
        mask=mod.response_mask(a,h)
        idx=mod.secret_index(700)
        bit=(mask>>idx)&1
        self.assertEqual(bit,mod.consequence(h[idx],a))
        alive=((1<<len(h))-1)&(mask if bit else ~mask)
        self.assertTrue((alive>>idx)&1)
        self.assertGreater(alive.bit_count(),0)

if __name__=='__main__':unittest.main()
