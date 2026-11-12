"""WSP53 raw acoustic sparse-address source-independent engineering checks."""
from dataclasses import dataclass,replace
import unittest
from direct_writer import SparseAcousticWriter,segment,grounded_change,MODES

@dataclass(frozen=True)
class Observation:
    before:tuple
    acoustic_bits:str
    after:tuple
    action_cost:int=1
    reset_cost:int=0

class Contracts(unittest.TestCase):
    def test_segment_and_anchor(self):
        self.assertTrue(segment("010101010101"))
        self.assertTrue(all(len(p)==3 for p in segment("010101010101")))
        self.assertEqual(grounded_change("anchored_effect",(0,)*16,
                         (2,)+(0,)*7+(1,)+(0,)*7),(0,(-1,2,1)))
        self.assertEqual(grounded_change("noncommuting_order",(0,)*8,
                         (2,)+(0,)*7),(0,(0,2,-1)))
        self.assertIsNone(grounded_change("noncommuting_order",(0,)*8,(0,)*8))

    def test_modes_write_and_cold_restore(self):
        for family in ("anchored_effect","noncommuting_order"):
            before=(0,)*(16 if family=="anchored_effect" else 8)
            after=((2,)+(0,)*7+(1,)+(0,)*7 if family=="anchored_effect"
                   else (2,)+(0,)*7)
            r=Observation(before,"101001011000",after)
            for mode in MODES:
                with self.subTest(family=family,mode=mode):
                    m=SparseAcousticWriter(family=family,mode=mode)
                    m.observe(r);m.observe(r)
                    self.assertEqual(m.actions,2)
                    self.assertEqual(m.informative,2)
                    self.assertGreater(m.numeric_weight_count(),0)
                    cold=SparseAcousticWriter.restore(m.snapshot())
                    self.assertEqual(cold.predict(before,r.acoustic_bits),
                                     m.predict(before,r.acoustic_bits))
                    self.assertIsNone(cold.predict(before,"010101010101"))
                    self.assertEqual(cold.capacity_bits(),m.capacity_bits())

    def test_conflict_budget_and_tamper(self):
        before=(0,)*8
        r=Observation(before,"100111000111",(2,)+(0,)*7)
        m=SparseAcousticWriter(family="noncommuting_order")
        m.observe(r)
        m.observe(replace(r,after=(3,)+(0,)*7))
        self.assertIsNone(m.predict(before,r.acoustic_bits))
        self.assertIsNone(SparseAcousticWriter.restore(m.snapshot()).predict(before,r.acoustic_bits))
        for _ in range(58):
            m.observe(r)
        with self.assertRaises(ValueError):
            m.observe(r)
        with self.assertRaises(ValueError):
            SparseAcousticWriter.restore(m.snapshot().replace("pure_direct","count_only"))
        with self.assertRaises(ValueError):
            m.observe(replace(r,action_cost=0))

if __name__=="__main__":
    unittest.main()
