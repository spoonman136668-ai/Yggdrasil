"""F92 pure method tests; never construct synthetic scientific cases."""
import importlib.util,inspect,sys,unittest
from pathlib import Path
p=Path(__file__).with_name("dense_path_credit.py")
s=importlib.util.spec_from_file_location("f92_unit",p)
M=importlib.util.module_from_spec(s);sys.modules[s.name]=M;s.loader.exec_module(M)
class Pack:
 def mirrored(self,r):
  a,b,c=r;return b,a,tuple(x^1 for x in reversed(c))
 def pack(self,a,b,c):return bytes(12)
class F91:
 def vector(self,baseline,after):
  return (1.,)+tuple(after[i]-baseline[i] for i in range(1,12))
 def score(self,w,x):
  import math
  return 1/(1+math.exp(-sum(v*k/48 for v,k in zip(w,x))))
class Native:
 def __init__(self):
  self.base=((1,2,(0,)),)
  self.alt=((1,2,(0,)),(2,3,(2,)))
 def _f60_step(self,before,event,pack):return self.base
 def actions(self,before,event,index,pack):
  b=(1.,)+(0.,)*11;other=(1.,1.)+(0.,)*10
  return (("append",-1,-1,self.base,b),("append",-1,-1,self.alt,other))
 def _valid_memory(self,state,pack):assert len(state)<=12
class Tests(unittest.TestCase):
 def test_online_is_query_blind(self):
  self.assertEqual(tuple(inspect.signature(M.online).parameters),
   ("public","benefit","harm","pack","F62","F91","trace"))
 def test_public_prefix_composition(self):
  records=((10,11,(0,2)),(11,12,(4,6)))
  q={"start":10,"ops":((0,1),(1,1),(2,1),(3,1))}
  self.assertEqual(M.prefix_hops(records,q,Pack()),4)
 def test_prefix_is_not_full_match_when_middle_missing(self):
  records=((10,11,(0,)),(11,12,(4,)))
  q={"start":10,"ops":((0,1),(1,1),(2,1),(3,1))}
  self.assertEqual(M.prefix_hops(records,q,Pack()),1)
 def test_before_minimum_index_inactive(self):
  after,change,n=M.choose((),(1,0,2),23,False,(96,)*12,(-96,)*12,Pack(),Native(),F91())
  self.assertFalse(change);self.assertEqual(n,0)
 def test_one_bit_latch(self):
  after,change,n=M.choose((),(1,0,2),71,True,(96,)*12,(-96,)*12,Pack(),Native(),F91())
  self.assertFalse(change);self.assertEqual(n,0)
 def test_bounded_single_native_action(self):
  after,change,n=M.choose((),(1,0,2),71,False,(96,)*12,(-96,)*12,Pack(),Native(),F91())
  self.assertTrue(change);self.assertEqual(n,1)
  self.assertEqual(after,Native().alt)
 def test_nonqualifying_predictor_is_exact_baseline(self):
  after,change,n=M.choose((),(1,0,2),71,False,(0,)*12,(0,)*12,Pack(),Native(),F91())
  self.assertFalse(change);self.assertEqual(after,Native().base)
 def test_full_online_latch(self):
  public=tuple((100+i,i%4,101+i) for i in range(72))
  mem,trace,receipt=M.online(public,(96,)*12,(-96,)*12,Pack(),Native(),F91(),True)
  self.assertEqual(len(trace),72)
  self.assertLessEqual(receipt["interventions"],1)
  self.assertEqual(receipt["latch_bits"],1)
if __name__=="__main__":unittest.main()
