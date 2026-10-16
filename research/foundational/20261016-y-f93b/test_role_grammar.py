"""F93B pure grammar/causal-contract unit tests; no scientific source access."""
import importlib.util,inspect,sys,unittest
from pathlib import Path
file=Path(__file__).with_name("role_grammar.py")
spec=importlib.util.spec_from_file_location("f93b_unit",file)
M=importlib.util.module_from_spec(spec);sys.modules[spec.name]=M
spec.loader.exec_module(M)
GRAMMAR=((0,2,4,6,0,2),)
BASE=((1,2,(0,)),(2,3,(2,)),(3,4,(4,)),(4,5,(6,)),(5,6,(0,)))
ALT=BASE+((6,7,(2,)),)
class Pack:
 def mirrored(self,r):
  a,b,c=r;return b,a,tuple(x^1 for x in reversed(c))
 def pack(self,a,b,c):return bytes(12)
class Source:
 def _f60_step(self,before,event,pack):return BASE
 def actions(self,before,event,index,pack):
  return (("append",-1,-1,BASE,()),("append",-1,-1,ALT,()))
 def _valid_memory(self,memory,pack):assert len(memory)<=12
class Tests(unittest.TestCase):
 def test_no_query_future_or_answer_in_online(self):
  self.assertEqual(tuple(inspect.signature(M.online).parameters),
   ("public","grammar","pack","F62","trace"))
 def test_training_deterministic_count_and_tie_break(self):
  p=lambda codes:{"ops":tuple((x//2,(-1 if x%2 else 1)) for x in codes)}
  a=(0,2,4,6,0,2);b=(2,0,4,6,0,2)
  grammar,stats=M.fit([p(a),p(b),p(a)])
  self.assertEqual(grammar,(a,b));self.assertEqual(stats["six_step_train_questions"],3)
 def test_composable_route_only_when_complete(self):
  self.assertEqual(len(M.coverage(BASE,GRAMMAR,Pack())),0)
  self.assertEqual(M.coverage(ALT,GRAMMAR,Pack()),frozenset({(0,1,7)}))
 def test_causal_native_action_selected_late(self):
  after,used,candidates,caps=M.decision((),(1,0,2),40,False,GRAMMAR,Pack(),Source())
  self.assertEqual(after,ALT);self.assertTrue(used);self.assertEqual(candidates,1)
 def test_early_and_latch_block(self):
  for i,used in ((35,False),(71,True)):
   after,yes,n,_=M.decision((),(1,0,2),i,used,GRAMMAR,Pack(),Source())
   self.assertEqual(after,BASE);self.assertFalse(yes);self.assertEqual(n,0)
 def test_coverage_cap_fails_closed(self):
  self.assertIsNone(M.coverage(ALT,GRAMMAR,Pack(),cap=0))
 def test_full_72_source_only_receipts(self):
  public=tuple((100+i,i%4,101+i) for i in range(72))
  state,trace,receipt=M.online(public,GRAMMAR,Pack(),Source(),True)
  self.assertEqual(len(trace),72)
  self.assertLessEqual(receipt["interventions"],1)
  self.assertEqual(receipt["latch_bits"],1)
  self.assertLessEqual(len(state),12)
if __name__=="__main__":unittest.main()
