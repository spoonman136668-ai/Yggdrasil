"""F97 no-cohort contracts: public causality, exact native action, frozen counts."""
from __future__ import annotations
import importlib.util,inspect,sys,unittest
from pathlib import Path
f=Path(__file__).with_name("paired_join_risk.py")
spec=importlib.util.spec_from_file_location("f97_pure",f)
M=importlib.util.module_from_spec(spec);sys.modules[spec.name]=M;spec.loader.exec_module(M)
BASE=((1,2,(0,)),)
OTHER=((1,2,(0,)),(2,3,(2,)))
class Pack:
 def pack(self,a,b,c):return bytes(12)
class F62:
 def _f60_step(self,before,event,pack):return BASE
 def actions(self,before,event,index,pack):
  return (("append",-1,-1,BASE,()),("append",-1,-1,OTHER,()))
 def _valid_memory(self,mem,pack):assert len(mem)<=12
class Tests(unittest.TestCase):
 def test_no_question_or_future_inference_api(self):
  self.assertEqual(tuple(inspect.signature(M.online).parameters),
   ("public","approved","pack","F62","trace"))
 def test_public_only_category(self):
  action=("append",-1,0,OTHER,())
  self.assertEqual(M.category(BASE,(2,1,3),27,action),(1,1,1,0,1))
 def test_no_approval_means_exact_f60(self):
  state,changed,n=M.decide(BASE,(2,1,3),27,False,{},Pack(),F62())
  self.assertEqual(state,BASE);self.assertFalse(changed);self.assertEqual(n,1)
 def test_verified_public_category_can_intervene(self):
  key=M.category(BASE,(2,1,3),27,("append",-1,-1,OTHER,()))
  state,changed,n=M.decide(BASE,(2,1,3),27,False,{key:(3,16)},Pack(),F62())
  self.assertEqual(state,OTHER);self.assertTrue(changed)
 def test_late_only_and_single_latch(self):
  approved={M.category(BASE,(2,1,3),49,("append",-1,-1,OTHER,())):(8,50)}
  for index,used in ((49,False),(27,True)):
   st,changed,_=M.decide(BASE,(2,1,3),index,used,approved,Pack(),F62())
   self.assertEqual(st,BASE);self.assertFalse(changed)
 def test_risk_gate_requires_two_beneficial_and_no_harm(self):
  rows=[
    {(0,0,0,0,0):[2,0,10],(0,1,0,0,0):[2,1,10]},
    {(0,0,1,0,0):[1,0,22],(0,1,1,0,0):[2,0,1]}]
  trained,receipt=M.fit(rows)
  self.assertEqual(trained,{(0,0,0,0,0):(2,12)})
  self.assertEqual(receipt["eligible_categories"],1)
 def test_full_72_causal_steps_bounded_to_one_intervention(self):
  public=tuple((100+i,i%4,101+i) for i in range(72))
  out,trace,stats=M.online(public,{},Pack(),F62(),True)
  self.assertEqual(out,BASE);self.assertEqual(len(trace),72)
  self.assertEqual(stats["interventions"],0);self.assertEqual(stats["latch_bits"],1)
if __name__=="__main__":unittest.main()
