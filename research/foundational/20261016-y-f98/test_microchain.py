"""F98 no-source-contract tests: native causal microchain construction and grammar."""
from __future__ import annotations
import importlib.util,inspect,sys,unittest
from pathlib import Path
p=Path(__file__).with_name("microchain.py")
s=importlib.util.spec_from_file_location("f98_contracts",p)
M=importlib.util.module_from_spec(s);sys.modules[s.name]=M;s.loader.exec_module(M)
GRAMMAR=((0,2),)+tuple((i,j) for i in range(8) for j in range(8) if (i,j)!=(0,2))[:15]
class Pack:
 def pack(self,a,b,c):return bytes(12)
class Native:
 def __init__(self):
  self.base=((100,101,(0,)),)
  self.alt=((100,101,(0,2)),)
 def _f60_step(self,memory,event,pack):return self.base
 def actions(self,memory,event,index,pack):
  return (("append",-1,-1,self.base,()),("merge",0,-1,self.alt,()))
 def _valid_memory(self,mem,pack):assert len(mem)<=12
class Tests(unittest.TestCase):
 def test_query_blind_online(self):
  self.assertEqual(tuple(inspect.signature(M.online).parameters),
    ("public","grammar","pack","F62","trace"))
 def test_no_hindsight_task_input_in_decision(self):
  self.assertEqual(tuple(inspect.signature(M.decide).parameters),
    ("memory","event","index","spent","grammar","pack","F62"))
 def test_two_hop_structural_roles_forward_and_inverse(self):
  stream=[(100,0,101),(101,1,102)]
  stream.extend((300+2*i,i%4,301+2*i) for i in range(70))
  counts=M.two_hop_counts(tuple(stream))
  self.assertEqual(counts[(0,2)],1)
  self.assertEqual(counts[(3,1)],1)
  self.assertNotIn((0,1),counts)
 def test_deterministic_grammar_rank_and_count(self):
  stream=tuple((100+2*i,i%4,101+2*i) for i in range(72))
  a,c=M.learn_graph_grammar((stream,))
  b,d=M.learn_graph_grammar((stream,))
  self.assertEqual(a,b);self.assertEqual(c,d)
  self.assertEqual(len(a),16)
 def test_internal_memory_bigrams_only(self):
  self.assertEqual(M.grammar_coverage(((1,2,(0,2,4)),),GRAMMAR),frozenset({(0,2),(2,4)} & set(GRAMMAR)))
 def test_eligible_microchain_is_genuine_source_native_action(self):
  state,changed,n,gain=M.decide((),(100,0,101),9,0,GRAMMAR,Pack(),Native())
  self.assertTrue(changed)
  self.assertEqual(state,Native().alt)
  self.assertEqual(gain,1)
 def test_hard_two_deviation_gate_and_late_gate(self):
  for index,used in ((5,2),(50,0)):
   state,changed,n,gain=M.decide((),(100,0,101),index,used,GRAMMAR,Pack(),Native())
   self.assertFalse(changed)
   self.assertEqual(state,Native().base)
 def test_full_72_native_prefixes_and_latch(self):
  public=tuple((100+i,i%4,101+i) for i in range(72))
  memory,traces,stats=M.online(public,GRAMMAR,Pack(),Native(),True)
  self.assertLessEqual(stats["interventions"],2)
  self.assertEqual(len(traces),72)
  self.assertEqual(stats["model_extra_bytes"],32)
  self.assertEqual(stats["extra_latch_bits"],2)
  self.assertLessEqual(len(memory),12)
if __name__=="__main__":unittest.main()
