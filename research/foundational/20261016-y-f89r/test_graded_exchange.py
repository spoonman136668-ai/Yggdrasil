#!/usr/bin/env python3
"""F89 non-scientific contract tests; never construct or inspect source cases."""
from __future__ import annotations
import importlib.util,inspect,sys,unittest
from pathlib import Path

file=Path(__file__).with_name("graded_exchange.py")
spec=importlib.util.spec_from_file_location("f89_isolated_methods",file)
M=importlib.util.module_from_spec(spec)
sys.modules[spec.name]=M
spec.loader.exec_module(M)

B=((10,11,(0,)),)
C=((10,11,(0,)),(20,21,(2,)))
D=((20,21,(2,)),)
E=((10,11,(0,)),(30,31,(4,)))
class Legal:
 def __init__(self,base,alternatives):
  self.base=base
  self.alternatives=alternatives
 def _f60_step(self,before,event,codec):
  return self.base
 def actions(self,before,event,index,codec):
  return tuple(("append",-1,-1,x,()) for x in [self.base]+list(self.alternatives))
 def _valid_memory(self,after,codec):
  assert len(after)<=12 and all(1<=len(r[2])<=6 for r in after)
def mocklanguage(config):
 def inner(after,codec):
  return config[after]
 return inner

class F89Contracts(unittest.TestCase):
 def test_no_question_answer_or_source_family_in_online_API(self):
  self.assertEqual(tuple(inspect.signature(M.online).parameters),
                   ("public","pack","F62","language","trace"))
 def test_strict_long_coverage_with_one_lost_short_accepts(self):
  rule=mocklanguage({B:(frozenset({"a","b","c"}),0,1,4),
                     C:(frozenset({"a","b"}),0,3,4)})
  state,meta=M.decide((),(10,0,11),3,None,Legal(B,[C]),rule)
  self.assertEqual(state,C)
  self.assertEqual(meta["short_lost"],1)
  self.assertEqual(meta["long_gain"],4)
  self.assertEqual(meta["override"],1)
 def test_four_short_losses_rejected_no_matter_how_many_long_gains(self):
  rule=mocklanguage({B:(frozenset({"a","b","c","d"}),0,0,4),
                     C:(frozenset(),0,99,4)})
  state,meta=M.decide((),(10,0,11),3,None,Legal(B,[C]),rule)
  self.assertEqual(state,B)
  self.assertEqual(meta["override"],0)
 def test_long_gain_insufficient_for_short_loss(self):
  rule=mocklanguage({B:(frozenset({"a","b"}),0,0,4),
                     C:(frozenset({"b"}),0,1,4)})
  state,meta=M.decide((),(10,0,11),3,None,Legal(B,[C]),rule)
  self.assertEqual(state,B)
  self.assertEqual(meta["eligible"],0)
 def test_strict_gain_with_zero_losses(self):
  rule=mocklanguage({B:(frozenset({"a"}),1,0,4),
                     C:(frozenset({"a"}),2,0,4)})
  state,meta=M.decide((),(10,0,11),3,None,Legal(B,[C]),rule)
  self.assertEqual(state,C)
  self.assertEqual(meta["long_gain"],1)
 def test_scoring_ignores_numeric_node_identity(self):
  shifted=lambda state:tuple((a+10000,b+10000,c) for a,b,c in state)
  rule=mocklanguage({B:(frozenset({"a","b","c"}),0,0,4),
                     C:(frozenset({"b","c"}),0,2,4)})
  rule2=mocklanguage({shifted(B):(frozenset({"a","b","c"}),0,0,4),
                     shifted(C):(frozenset({"b","c"}),0,2,4)})
  x,y=M.decide((),(10,0,11),1,None,Legal(B,[C]),rule)
  p,q=M.decide((),(10010,0,10011),1,None,
               Legal(shifted(B),[shifted(C)]),rule2)
  self.assertEqual(y,q)
  self.assertEqual(x,C)
  self.assertEqual(p,shifted(C))
 def test_fail_closed_on_cap(self):
  rule=mocklanguage({B:None,C:(frozenset(),0,100,100)})
  state,meta=M.decide((),(10,0,11),1,None,Legal(B,[C]),rule)
  self.assertEqual(state,B)
  self.assertEqual(meta["capped"],1)
  rule=mocklanguage({B:(frozenset(),0,0,0),C:None})
  state,meta=M.decide((),(10,0,11),1,None,Legal(B,[C]),rule)
  self.assertEqual(state,B)
  self.assertEqual(meta["capped"],1)
 def test_deterministic_native_enumeration_tiebreak(self):
  rule=mocklanguage({B:(frozenset({"x"}),0,0,0),
                     C:(frozenset({"x"}),0,2,0),
                     E:(frozenset({"x"}),0,2,0)})
  state,meta=M.decide((),(10,0,11),1,None,Legal(B,[C,E]),rule)
  self.assertEqual(state,C)
  self.assertEqual(meta["eligible"],2)
 def test_full_72_arrivals_accounting_does_not_raise(self):
  """Regression for the aborted F89 science job's override/overrides typo."""
  baseline=B
  public=tuple((10000+2*i,i%4,10001+2*i) for i in range(72))
  class Fixed:
   def _f60_step(self,before,event,codec):
    return baseline
   def actions(self,before,event,index,codec):
    return (("append",-1,-1,baseline,()),)
   def _valid_memory(self,after,codec):
    assert len(after)<=12
  lookup=mocklanguage({B:(frozenset({"a"}),0,0,1)})
  class ToyPack:
   def pack(self,a,b,codes):
    return bytes(12)
  state,trace,counts=M.online(public,ToyPack(),Fixed(),lookup,True)
  self.assertEqual(state,B)
  self.assertEqual(len(trace),72)
  self.assertEqual(counts,dict(overrides=0,capped=0,eligible=0,
                               short_lost=0,long_gain=0))
if __name__=="__main__":
 unittest.main()
