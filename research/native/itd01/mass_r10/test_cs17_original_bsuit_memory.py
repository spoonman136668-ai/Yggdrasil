"""CS17 source-free focus: real unmodified native action cell + cue ownership."""
from __future__ import annotations
import sys,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from run_cs17_original_bsuit_memory import (
 NativeTransientCue,PlainCue,LearnedNative,Episodic,Tabular,Logistic,
 QueryOnly,source_seed,LENGTHS,ARMS,REPLICAS,FIT_N,VALID_N,DEV_N
)
class Focused(unittest.TestCase):
 def test_cue_original_native_cell_owns_one_public_capture(self):
  bits=(1,0,1,0,1,0)
  a=NativeTransientCue();a.capture(bits)
  self.assertEqual(tuple(a.at(i) for i in range(6)),bits)
  self.assertEqual([x["updates"] for x in a.source_state()],[1]*6)
  b=NativeTransientCue()
  self.assertEqual(tuple(b.at(i) for i in range(6)),(0,)*6)
 def test_genuine_action_feedback_native_model_checkpoint(self):
  m=LearnedNative()
  for i in range(192):
   bit=i%2;action=(i//2)%2
   m.fit({"original_source_public_queried_cue_bit":bit,
          "original_source_terminal_action":action,
          "original_source_terminal_reward":1. if bit==action else -1.})
  state=m.trained_state()
  info=m.cold_restore()
  self.assertEqual(m.trained_state(),state)
  self.assertEqual(info["genuine_original_terminal_feedback_updates"],192)
  self.assertEqual(m.choose(0,0),0)
  self.assertEqual(m.choose(1,5),1)
 def test_conventional_equal_fit_no_source_law_privilege(self):
  models=[Episodic(),Tabular(),Logistic(),QueryOnly()]
  for i in range(192):
   bit=(i//2)%2;action=i%2;q=i%6
   z={"original_source_public_queried_cue_bit":bit,
      "original_source_terminal_action":action,
      "original_source_terminal_reward":1. if action==bit else -1.,
      "original_source_public_final_query":q}
   for m in models:m.fit(z)
  for m in models:
   self.assertIn(m.choose(1,3),(0,1))
   self.assertGreater(len(m.trained_state()),0)
 def test_exact_predeclared_cohorts_and_source_seed_roles(self):
  self.assertEqual(LENGTHS,(9,25))
  self.assertEqual(len(ARMS),7)
  self.assertEqual(REPLICAS,(0,1,2))
  seeds={source_seed(role,di,r,i) for role,n in
       (("FIT",FIT_N),("VALID",VALID_N),("DEV",DEV_N))
       for di in range(2) for r in REPLICAS for i in range(n)}
  self.assertEqual(len(seeds),2*3*(FIT_N+VALID_N+DEV_N))
if __name__=="__main__":
 unittest.main()
