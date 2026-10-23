"""CS14 focused actual R7 LocalCell action ownership and cold protection."""
from __future__ import annotations
import json
import unittest
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from cs14_action_owned_native_cells import ActionOwnedNativeCells,LocalCell
from run_cs14_original_action_owned_native import Explore,ARMS,seed,FIT_N,VALID_N,DEV_N

class ActionOwnedLocalTests(unittest.TestCase):
 def test_exact_original_localcell_ownership_and_both_consequences(self):
    m=ActionOwnedNativeCells()
    untouched={(s,a):m.buckets[(s,a)]["reward"].updates for s in (0,1) for a in (0,1)}
    m.learn_completed_public_consequence(1,0,1,0,2)
    self.assertIsInstance(m.buckets[(1,0)]["reward"],LocalCell)
    self.assertEqual(m.buckets[(1,0)]["reward"].updates,1)
    self.assertEqual(m.buckets[(1,0)]["next_state"].updates,1)
    self.assertEqual(m.completed_feedback_updates,1)
    for s,a in ((0,0),(0,1),(1,1)):
        self.assertEqual(m.buckets[(s,a)]["reward"].updates,untouched[(s,a)])
        self.assertEqual(m.buckets[(s,a)]["next_state"].updates,0)
 def test_both_actions_owned_and_reward_based_public_policy(self):
    m=ActionOwnedNativeCells()
    for _ in range(60):
        for s in (0,1):
            for a in (0,1):
                y=int(s==a)
                nxt=int(s==a)
                m.learn_completed_public_consequence(s,a,y,nxt,2)
    self.assertEqual(m.completed_feedback_updates,240)
    self.assertEqual(m.choose(0),0)
    self.assertEqual(m.choose(1),1)
    self.assertGreater(m.predict_next(0,0),m.predict_next(0,1))
    self.assertGreater(m.predict_reward(1,1),m.predict_reward(1,0))
 def test_cold_checkpoint_byte_exact_and_tamper_fails(self):
    m=ActionOwnedNativeCells()
    m.learn_completed_public_consequence(0,1,1,0,2)
    raw=m.checkpoint()
    clone=ActionOwnedNativeCells.restore(raw)
    self.assertEqual(raw,clone.checkpoint())
    self.assertEqual(m.predict_next(0,1),clone.predict_next(0,1))
    x=json.loads(raw);x["payload"]["buckets"]["0:1"]["reward"]["fast"]+=1
    with self.assertRaises(ValueError):
        ActionOwnedNativeCells.restore(json.dumps(x,sort_keys=True).encode())
 def test_action_and_delayed_public_consequence_mandatory(self):
    m=ActionOwnedNativeCells()
    with self.assertRaises(ValueError):m.learn_completed_public_consequence(0,0,1,0,1)
    with self.assertRaises(ValueError):m.learn_completed_public_consequence(0,2,1,0,2)
    with self.assertRaises(ValueError):m.learn_completed_public_consequence(0,0,1,2,2)
    self.assertEqual(m.completed_feedback_updates,0)
 def test_original_role_seed_separation_and_fixed_arm_set(self):
    ids={seed(role,r,i) for role,n in (("FIT",FIT_N),("VALID",VALID_N),("DEV",DEV_N))
         for r in range(3) for i in range(n)}
    self.assertEqual(len(ids),3*(FIT_N+VALID_N+DEV_N))
    self.assertEqual(len(ARMS),7)
    self.assertEqual([Explore(0).choose(0),Explore(1).choose(1)],[0,1])
if __name__=="__main__":
 unittest.main()
