#!/usr/bin/env python3
"""F85 isolated exact solver controls; no research cohorts are accessed."""
from __future__ import annotations
import importlib.util
from pathlib import Path
import sys
import unittest

PATH=Path(__file__).resolve().with_name("global_solver.py")
spec=importlib.util.spec_from_file_location("f85_global_solver_readonly",PATH)
mod=importlib.util.module_from_spec(spec)
sys.modules[spec.name]=mod
spec.loader.exec_module(mod)


class CodecDouble:
    """Only the frozen 12-byte packing and exact reversal semantics."""
    def pack(self,a,b,codes):
        assert 0<=a<2**32 and 0<=b<2**32 and 1<=len(codes)<=6
        value=sum(code<<(i*3) for i,code in enumerate(codes))
        return a.to_bytes(4,"little")+b.to_bytes(4,"little")+value.to_bytes(3,"little")+bytes([len(codes)])
    def unpack(self,p):
        a=int.from_bytes(p[:4],"little")
        b=int.from_bytes(p[4:8],"little")
        val=int.from_bytes(p[8:11],"little")
        length=p[11]
        return a,b,tuple((val>>(i*3))&7 for i in range(length))
    def mirrored(self,r):
        a,b,codes=r
        return b,a,tuple(c^1 for c in reversed(codes))


class F85FrozenSolverTests(unittest.TestCase):
    def setUp(self):
        self.codec=CodecDouble()
        self.query=dict(start=100,ops=((0,1),(1,1),(2,1),(3,1)))
        self.correct=((100,101,(0,)),(100,102,(0,)),
                      (101,103,(2,)),(103,104,(4,)),(104,105,(6,)))

    def test_global_unique_terminal_over_intermediate_ambiguity(self):
        got,diag=mod.solve_global(self.correct,self.query,self.codec)
        self.assertEqual(got,105)
        self.assertEqual(diag["distinct_final_endpoints"],1)
        self.assertLess(diag["persistent_memory_bytes"],144)

    def test_real_terminal_ambiguity_is_abstention(self):
        records=self.correct+((102,106,(2,)),(106,107,(4,)),(107,108,(6,)))
        result,diag=mod.solve_global(records,self.query,self.codec)
        self.assertIsNone(result)
        self.assertEqual(diag["distinct_final_endpoints"],2)

    def test_missing_necessary_record_fails_closed(self):
        answer,_=mod.solve_global(self.correct[:-1],self.query,self.codec)
        self.assertIsNone(answer)

    def test_reversed_record_codes_are_oriented_correctly(self):
        records=((100,101,(0,)),(102,101,(3,)),(102,103,(4,)),(103,104,(6,)))
        result,_=mod.solve_global(records,self.query,self.codec)
        self.assertEqual(result,104)

    def test_work_limit_abstains(self):
        result,diag=mod.solve_global(self.correct,self.query,self.codec,
                                     max_transitions=1)
        self.assertIsNone(result)
        self.assertTrue(diag["resource_cap_triggered"])

    def test_six_step_record_chain(self):
        q=dict(start=100,ops=((0,1),(1,-1),(2,1),(3,-1),(0,1),(1,-1)))
        mem=((100,102,(0,3)),(102,105,(4,7,0)),(106,105,(2,)))
        result,detail=mod.solve_global(mem,q,self.codec)
        self.assertEqual(result,106)
        self.assertEqual(detail["distinct_final_endpoints"],1)

    def test_invalid_overlength_retained_memory_rejected(self):
        r=tuple((100+i,200+i,(0,)) for i in range(13))
        with self.assertRaises(AssertionError):
            mod.solve_global(r,self.query,self.codec)


if __name__=="__main__":
    unittest.main()
