#!/usr/bin/env python3
"""F90 pure source/action contract tests. No registered/synthetic cohorts read."""
from __future__ import annotations
import importlib.util,inspect,sys,unittest
from pathlib import Path
p=Path(__file__).with_name("temporal_credit.py")
s=importlib.util.spec_from_file_location("f90_temporal_unit",p)
M=importlib.util.module_from_spec(s);sys.modules[s.name]=M;s.loader.exec_module(M)
def feats(v):
 return (float(v),)+(0.0,)*11
class Pack:
 def pack(self,a,b,codes):
  assert len(codes)>0 and len(codes)<=6
  return bytes(12)
class F62:
 def __init__(self):
  self.base=((1,2,(0,)),)
  self.alt=((1,2,(0,)),(2,3,(2,)))
 def _f60_step(self,memory,event,pack):return self.base
 def actions(self,memory,event,index,pack):
  return (("append",-1,-1,self.base,feats(0)),
          ("append",-1,-1,self.alt,feats(1)))
 def _valid_memory(self,memory,pack):
  assert len(memory)<=12
class SourceFake:
 def __init__(self):self.events=[]
 def _f60_step(self,memory,event,pack):
  self.events.append(event)
  return ((event[0],event[2],(0,)),)
 def actions(self,memory,event,index,pack):
  baseline=self._f60_step(memory,event,pack)
  return (("append",-1,-1,baseline,feats(0)),)
 def _finish_fixed(self,memory,suffix,pack):
  return memory
class SolverFake:
 def solve_global(self,records,question,pack):
  return (question.get("expected_prediction"),{})
class F90Tests(unittest.TestCase):
 def test_online_has_no_question_answer_future_or_seed(self):
  self.assertEqual(tuple(inspect.signature(M.online).parameters),
   ("public","quant_weights","pack","F62","trace"))
 def test_no_weight_prefers_original_F60(self):
  f=F62()
  after,override,number,score=M.choose((),(1,0,2),0,(0,)*12,Pack(),f)
  self.assertEqual(after,f.base)
  self.assertFalse(override);self.assertEqual(number,1)
 def test_positive_weight_selects_source_native_state(self):
  f=F62()
  after,override,number,score=M.choose((),(1,0,2),0,(96,)+(0,)*11,Pack(),f)
  self.assertEqual(after,f.alt)
  self.assertTrue(override)
  self.assertGreaterEqual(score,.25)
 def test_negative_weight_falls_back(self):
  f=F62()
  after,override,_,_=M.choose((),(1,0,2),0,(-96,)+(0,)*11,Pack(),f)
  self.assertEqual(after,f.base)
  self.assertFalse(override)
 def test_weights_are_bounded_twelve_int8(self):
  q=M.train([((1.0,)+(0.,)*11,1)]*8)
  self.assertEqual(len(q),12)
  self.assertTrue(all(type(v) is int and -96<=v<=96 for v in q))
  self.assertGreater(q[0],0)
  z=M.train([((1.0,)+(0.,)*11,0)])
  self.assertEqual(z,(0,)*12)
 def test_signed_negative_training_credit(self):
  v=M.train([((1.0,)+(0.,)*11,-1)]*6)
  self.assertLess(v[0],0)
 def test_invalid_training_credit_fails_closed(self):
  with self.assertRaises(AssertionError):
   M.train([((1.,)+(0.,)*11,3)])
 def test_full_72_events_without_question(self):
  public=tuple((100+2*i,i%4,101+2*i) for i in range(72))
  f=F62()
  final,trace,stats=M.online(public,(0,)*12,Pack(),f,True)
  self.assertEqual(final,f.base)
  self.assertEqual(len(trace),72)
  self.assertEqual(stats["interventions"],0)
  self.assertEqual(stats["alternatives_scored"],72)
 def test_teacher_train_only_rejects_missing_checkpoints(self):
  with self.assertRaises(AssertionError):
   M.collect_training_examples(tuple((0,0,0) for _ in range(71)),
      {"start":0,"ops":(),"answer":0},Pack(),SourceFake(),SolverFake())
if __name__=="__main__":
 unittest.main()
