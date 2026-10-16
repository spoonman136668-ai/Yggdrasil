#!/usr/bin/env python3
"""F91 source-native contracts only; no scientific cohort accessed."""
from __future__ import annotations
import importlib.util,inspect,sys,unittest
from pathlib import Path
p=Path(__file__).with_name("conservative_credit.py")
s=importlib.util.spec_from_file_location("f91_unit",p)
M=importlib.util.module_from_spec(s);sys.modules[s.name]=M;s.loader.exec_module(M)
BASE=((1,2,(0,)),)
ALT=((1,2,(0,)),(2,3,(2,)))
def f(value):return (1.,float(value))+(0.,)*10
class Pack:
 def pack(self,a,b,codes):return bytes(12)
class Native:
 def __init__(self,base=BASE,alt=ALT):self.base=base;self.alt=alt
 def _f60_step(self,memory,event,pack):return self.base
 def actions(self,memory,event,index,pack):
  return (("append",-1,-1,self.base,(1.,0.)+(0.,)*10),
          ("append",-1,-1,self.alt,(1.,1.)+(0.,)*10))
 def _valid_memory(self,records,pack):assert len(records)<=12
class Contracts(unittest.TestCase):
 def test_query_blind_signature(self):
  self.assertEqual(tuple(inspect.signature(M.online).parameters),
    ("public","benefit","harm","pack","F62","trace"))
 def test_inference_below_late_gate_is_F60(self):
  b=(96,)*12;h=(-96,)*12
  x,u,n=M.choose((),(1,0,2),47,False,b,h,Pack(),Native())
  self.assertEqual(x,BASE);self.assertFalse(u);self.assertEqual(n,0)
 def test_intervention_latch_blocks_second_action(self):
  b=(96,)*12;h=(-96,)*12
  x,u,n=M.choose((),(1,0,2),71,True,b,h,Pack(),Native())
  self.assertEqual(x,BASE);self.assertFalse(u)
 def test_zero_head_falls_back(self):
  x,u,n=M.choose((),(1,0,2),71,False,(0,)*12,(0,)*12,Pack(),Native())
  self.assertEqual(x,BASE);self.assertFalse(u);self.assertEqual(n,1)
 def test_high_benefit_low_harm_allows_one_legal_alternative(self):
  b=(96,)*12;h=(-96,)*12
  x,u,n=M.choose((),(1,0,2),71,False,b,h,Pack(),Native())
  self.assertEqual(x,ALT);self.assertTrue(u)
 def test_overlap_gate_blocks_damaging_replace(self):
  base=tuple((i,i+1,(0,)) for i in range(1,13))
  alt=tuple((i+100,i+101,(2,)) for i in range(1,13))
  x,u,_=M.choose((),(1,0,2),71,False,(96,)*12,(-96,)*12,Pack(),Native(base,alt))
  self.assertEqual(x,base);self.assertFalse(u)
 def test_training_separates_signed_harm_and_gain(self):
  pos=M.fit([(f(1),1)]*6)
  neg=M.fit([(f(1),-1)]*6)
  self.assertEqual(len(pos[0]),12);self.assertEqual(len(pos[1]),12)
  self.assertGreater(pos[0][0],pos[1][0])
  self.assertGreater(neg[1][0],neg[0][0])
 def test_24_signed_int8_and_determinism(self):
  ex=[(f(i%3),[-1,0,1][i%3]) for i in range(60)]
  a=M.fit(ex);b=M.fit(ex)
  self.assertEqual(a,b)
  self.assertTrue(all(type(x) is int and -96<=x<=96 for x in a[0]+a[1]))
 def test_full_72_steps_latch_budget_and_no_future(self):
  events=tuple((100+i,i%4,101+i) for i in range(72))
  mem,receipts,stats=M.online(events,(96,)*12,(-96,)*12,Pack(),Native(),True)
  self.assertEqual(len(receipts),72)
  self.assertLessEqual(stats["interventions"],1)
  self.assertEqual(stats["latch_extra_bits"],1)
  self.assertLessEqual(len(mem),12)
if __name__=="__main__":unittest.main()
