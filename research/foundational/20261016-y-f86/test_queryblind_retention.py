#!/usr/bin/env python3
"""F86 public-only unit tests; do not generate or inspect scientific cohorts."""
from __future__ import annotations
import importlib.util
import inspect
from pathlib import Path
import sys
import unittest

FILE=Path(__file__).with_name("queryblind_retention.py")
spec=importlib.util.spec_from_file_location("f86_method_unit_only",FILE)
M=importlib.util.module_from_spec(spec)
sys.modules[spec.name]=M
spec.loader.exec_module(M)


class Codec:
    def pack(self,a,b,codes):
        assert 0<=a<2**32 and 0<=b<2**32
        assert len(codes)<=6 and len(codes)>=1
        payload=sum(c<<(3*i) for i,c in enumerate(codes))
        return (a.to_bytes(4,"little")+b.to_bytes(4,"little")+
                payload.to_bytes(3,"little")+bytes([len(codes)]))
    def unpack(self,data):
        n=data[-1]
        payload=int.from_bytes(data[8:11],"little")
        return (int.from_bytes(data[:4],"little"),
                int.from_bytes(data[4:8],"little"),
                tuple((payload>>(3*i))&7 for i in range(n)))


class LegalRawAppend:
    """Contract double of the frozen F62 legal append/evict subset."""
    @staticmethod
    def _valid_memory(records,codec):
        assert len(records)<=12
        assert all(codec.unpack(codec.pack(*r))==r for r in records)
    @staticmethod
    def actions(memory,event,index,codec):
        incoming=(event[0],event[2],(2*event[1],))
        extended=memory+(incoming,)
        drops=(-1,) if len(extended)<=12 else range(len(extended))
        return tuple(("append",-1,drop,
          tuple(rec for i,rec in enumerate(extended) if i!=drop),
          (0.0,)) for drop in drops)


class F86CausalUnitTests(unittest.TestCase):
    def test_online_has_no_question_seed_or_answer_input(self):
        names=tuple(inspect.signature(M.online).parameters)
        self.assertEqual(names,("public","pack","F62","trace"))

    def test_favors_lossless_composition(self):
        original=((1,2,(0,)),(2,3,(2,)))
        merged=((1,3,(0,2)),)
        self.assertGreater(M.priority(original,merged,17),
                           M.priority(original,original,17))

    def test_id_renaming_keeps_score(self):
        initial=((100,101,(0,)),(101,103,(2,3)),(106,107,(5,)))
        final=((100,103,(0,2,3)),(106,107,(5,)))
        translated=lambda records:tuple(
            (a+10000,b+10000,codes) for a,b,codes in records)
        self.assertEqual(M.priority(initial,final,7),
                         M.priority(translated(initial),translated(final),7))

    def test_changes_are_only_native_actions_and_bounded(self):
        public=tuple((1000+2*i,i%4,1001+2*i) for i in range(72))
        final,trace,selected=M.online(public,Codec(),LegalRawAppend,True)
        self.assertEqual(len(trace),72)
        self.assertEqual(len(selected),72)
        self.assertLessEqual(len(final),12)
        self.assertTrue(all(len(t)<=12 for t in trace))
        self.assertTrue(all(kind=="append" for kind,_,_ in selected))

    def test_no_hindsight_target_can_influence_online(self):
        public=tuple((1000+2*i,i%4,1001+2*i) for i in range(72))
        a=M.online(public,Codec(),LegalRawAppend,True)
        b=M.online(public,Codec(),LegalRawAppend,True)
        self.assertEqual(a,b)

    def test_no_numeric_node_magnitude_bias(self):
        before=((50,51,(2,)),(52,50,(4,)))
        a=((50,51,(2,)),(52,50,(4,)),(52,60,(6,)))
        b=((400000,400001,(2,)),(52,400000,(4,)),(52,60,(6,)))
        renamed=((400000,400001,(2,)),(52,400000,(4,)))
        self.assertEqual(M.priority(before,a,21),
                         M.priority(renamed,b,21))


if __name__=="__main__":
    unittest.main()
