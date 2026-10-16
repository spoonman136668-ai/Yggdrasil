#!/usr/bin/env python3
"""F87B independent public-only contract tests; no cohorts are accessed."""
from __future__ import annotations
import importlib.util,inspect,sys,unittest
from pathlib import Path
p=Path(__file__).with_name("bridge_reserve.py")
spec=importlib.util.spec_from_file_location("f87b_source_only_unit",p)
M=importlib.util.module_from_spec(spec);sys.modules[spec.name]=M;spec.loader.exec_module(M)
class Codec:
 def edge_record(self,e):return e[0],e[2],(2*e[1],)
class Contract:
 def __init__(self,baseline,candidates):
  self.baseline=baseline;self.candidates=candidates
 def _f60_step(self,memory,event,pack):return self.baseline
 def actions(self,memory,event,index,pack):
  return tuple(("append",-1,-1,state,()) for state in self.candidates)
 def _valid_memory(self,after,pack):
  assert len(after)<=12
  assert all(1<=len(r[2])<=6 for r in after)
class Tests(unittest.TestCase):
 def test_no_query_or_labels_are_inputs(self):
  self.assertEqual(tuple(inspect.signature(M.online).parameters),
                   ("public","pack","F62","trace"))
 def test_no_bridge_if_only_one_existing_record_contains_both_endpoints(self):
  self.assertFalse(M.bridge_detect(((10,20,(0,2)),),(10,1,20)))
 def test_two_distinct_existing_records_create_public_bridge(self):
  self.assertTrue(M.bridge_detect(((10,11,(0,)),(20,21,(4,))),(10,1,20)))
 def test_nonbridge_never_overrides_f60(self):
  memory=((10,11,(0,)),)
  base=memory+((30,40,(2,)),)
  state,trig,over=M.decision(memory,(30,1,40),1,Codec(),Contract(base,[base]))
  self.assertEqual(state,base)
  self.assertFalse(trig);self.assertFalse(over)
 def test_bridge_retains_raw_incoming_from_legal_candidates(self):
  m=((10,11,(0,)),(20,21,(4,)))
  raw=(10,20,(2,))
  baseline=((10,20,(0,2)),m[1])
  candidate=m+(raw,)
  c=Contract(baseline,[baseline,candidate])
  result,trig,over=M.decision(m,(10,1,20),2,Codec(),c)
  self.assertEqual(result,candidate)
  self.assertTrue(trig);self.assertTrue(over)
 def test_fail_closed_without_candidate_retaining_raw(self):
  m=((10,11,(0,)),(20,21,(4,)))
  base=((10,20,(0,2)),m[1])
  res,trig,over=M.decision(m,(10,1,20),2,Codec(),Contract(base,[base]))
  self.assertEqual(res,base)
  self.assertTrue(trig);self.assertFalse(over)
if __name__=="__main__":unittest.main()
