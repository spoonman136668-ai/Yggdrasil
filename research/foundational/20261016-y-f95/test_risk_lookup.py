"""F95 query-blind native risk lookup contract tests; no source cohorts used."""
import importlib.util,inspect,sys,unittest
from pathlib import Path
p=Path(__file__).with_name("risk_lookup.py")
s=importlib.util.spec_from_file_location("f95_unit",p)
M=importlib.util.module_from_spec(s);sys.modules[s.name]=M;s.loader.exec_module(M)
BASE=((10,11,(0,)),(20,21,(2,)))
ALT=((10,11,(0,)),(20,21,(2,)),(11,20,(4,)))
def f(v):
 return (1.,v)+(0.,)*10
class Native:
 def _f60_step(self,memory,event,codec):return BASE
 def actions(self,memory,event,index,codec):
  return (("append",-1,-1,BASE,f(0)),("append",-1,-1,ALT,f(1)))
 def _valid_memory(self,records,codec):assert len(records)<=12
class Codec:
 def pack(self,a,b,ops):return bytes(12)
class Tests(unittest.TestCase):
 def test_inference_has_no_future_question_or_answer(self):
  self.assertEqual(tuple(inspect.signature(M.online).parameters),
                    ("public","policy","codec","F62","trace"))
 def test_public_key_uses_only_six_public_native_features(self):
  key=M.public_key(35,(11,2,20),("append",-1,-1,ALT,f(1)),BASE)
  self.assertEqual(key,(1,2,0,1,0,1))
  self.assertEqual(M.key_text(key),"1:2:0:1:0:1")
 def test_frozen_allowed_bucket_selects_native_action(self):
  event=(11,2,20)
  k=M.key_text(M.public_key(35,event,("append",-1,-1,ALT,f(1)),BASE))
  state,change,n=M.choose((),event,35,False,{k:3},Codec(),Native())
  self.assertEqual(state,ALT);self.assertTrue(change);self.assertEqual(n,1)
 def test_early_late_and_latch_refuse_intervention(self):
  e=(11,2,20);k=M.key_text(M.public_key(35,e,("append",-1,-1,ALT,f(1)),BASE))
  for index,used in ((11,False),(48,False),(35,True)):
   state,change,n=M.choose((),e,index,used,{k:4},Codec(),Native())
   self.assertEqual(state,BASE);self.assertFalse(change);self.assertEqual(n,0)
 def test_untrained_bucket_stays_exact_F60(self):
  state,change,n=M.choose((),(11,2,20),35,False,{},Codec(),Native())
  self.assertEqual(state,BASE);self.assertFalse(change);self.assertEqual(n,1)
 def test_overlap_protection(self):
  self.assertTrue(M.eligible_overlap(BASE,ALT))
  worse=((10,11,(0,)),)
  many=tuple((i,i+1,(0,)) for i in range(12))
  self.assertFalse(M.eligible_overlap(many,many[:9]))
  self.assertTrue(M.eligible_overlap(BASE,worse))
 def test_full_72_public_only_receipts_and_one_latch(self):
  public=tuple((11,i%4,20) for i in range(72))
  event=public[35]
  k=M.key_text(M.public_key(35,event,("append",-1,-1,ALT,f(1)),BASE))
  state,trace,info=M.online(public,{k:2},Codec(),Native(),True)
  self.assertEqual(len(trace),72)
  self.assertLessEqual(info["native_interventions"],1)
  self.assertEqual(info["latch_bits"],1)
  self.assertLessEqual(len(state),12)
 def test_policy_types_fail_closed(self):
  with self.assertRaises(AssertionError):
   M.choose((),(11,2,20),35,False,{"a":-1},Codec(),Native())
if __name__=="__main__":unittest.main()
