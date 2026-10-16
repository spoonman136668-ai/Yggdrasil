#!/usr/bin/env python3
"""Offline contract tests for F88; never touch scientific cohort generator."""
from __future__ import annotations
import importlib.util,inspect,sys,unittest
from pathlib import Path

path=Path(__file__).with_name("frontier.py")
spec=importlib.util.spec_from_file_location("f88_contract_module",path)
F88=importlib.util.module_from_spec(spec)
sys.modules[spec.name]=F88
spec.loader.exec_module(F88)

class Codec:
    def mirrored(self,r):
        a,b,codes=r
        return b,a,tuple(x^1 for x in reversed(codes))
    def pack(self,a,b,codes):
        assert 1<=len(codes)<=6 and 0<=a<2**32 and 0<=b<2**32
        num=sum(c<<(i*3) for i,c in enumerate(codes))
        return (a.to_bytes(4,"little")+b.to_bytes(4,"little")
            +num.to_bytes(3,"little")+bytes([len(codes)]))
    def unpack(self,p):
        n=p[11];v=int.from_bytes(p[8:11],"little")
        return int.from_bytes(p[:4],"little"),int.from_bytes(p[4:8],"little"),tuple((v>>(i*3))&7 for i in range(n))

class NativeDouble:
    def __init__(self,baseline,after):
        self.baseline=baseline;self.after=after
    def _f60_step(self,memory,event,pack):
        return self.baseline
    def actions(self,memory,event,index,pack):
        return tuple(("append",-1,-1,after,()) for after in (self.baseline,self.after))
    def _valid_memory(self,records,pack):
        assert len(records)<=12

class F88Contracts(unittest.TestCase):
    def setUp(self):
        self.codec=Codec()
    def test_online_exposes_no_question_or_truth(self):
        self.assertEqual(tuple(inspect.signature(F88.online).parameters),
                         ("public","pack","F62","trace"))
    def test_public_relation_language_is_directional_and_exact(self):
        rec=((100,101,(0,2)),(101,102,(4,6)))
        s=F88.public_language(rec,self.codec)
        self.assertIn((100,102,(0,2,4,6)),s[0])
        self.assertIn((102,100,(7,5,3,1)),s[0])
        self.assertNotIn((100,101,(0,)),s[0])
    def test_not_promote_more_sixstep_if_short_relationship_dropped(self):
        old=((10,11,(0,)),)
        new=((10,16,(0,2,4,6,0,2)),)
        selected,detail=F88.decide((),(10,0,11),0,self.codec,NativeDouble(old,new))
        self.assertEqual(selected,old)
        self.assertEqual(detail["override"],0)
    def test_promote_novel_sixstep_with_same_short_language(self):
        old=((10,15,(0,2,4,6,0)),)
        new=((10,16,(0,2,4,6,0,2)),)
        s0=F88.public_language(old,self.codec)
        s1=F88.public_language(new,self.codec)
        self.assertEqual(s0[0],s1[0])
        self.assertLess(s0[2],s1[2])
        selected,detail=F88.decide((),(10,1,16),5,self.codec,NativeDouble(old,new))
        self.assertEqual(selected,new)
        self.assertEqual(detail["override"],1)
    def test_memory_renaming_does_not_change_language_count(self):
        r=((100,101,(0,2)),(101,102,(4,6)),(102,103,(0,2)))
        shifted=tuple((a+10000,b+10000,c) for a,b,c in r)
        s=F88.public_language(r,self.codec)
        u=F88.public_language(shifted,self.codec)
        self.assertEqual(s[1:],u[1:])
        self.assertEqual(len(s[0]),len(u[0]))
    def test_resource_cap_denies_new_action_without_overflow(self):
        baseline=((10,15,(0,2,4,6,0)),)
        new=((10,16,(0,2,4,6,0,2)),)
        old_cap=F88.PATH_CAP
        try:
            F88.PATH_CAP=0
            chosen,info=F88.decide((),(10,1,16),5,self.codec,NativeDouble(baseline,new))
        finally:
            F88.PATH_CAP=old_cap
        self.assertEqual(chosen,baseline)
        self.assertEqual(info["capped"],1)
    def test_boundary_budget_audited_at_native_action(self):
        records=tuple((100+i,200+i,(2,)) for i in range(12))
        lang=F88.public_language(records,self.codec)
        self.assertIsNotNone(lang)
        self.assertGreaterEqual(len(lang[0]),24)
        self.assertTrue(all(1<=len(row[2])<=4 for row in lang[0]))
        self.assertEqual(lang[2],0)

if __name__=="__main__":
    unittest.main()
