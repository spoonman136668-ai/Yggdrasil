"""CS21 source-free actual frozen native original R7 plasticity and exact source cohorts."""
from __future__ import annotations
import sys,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).parent))
from run_cs21_original_native_rank_relevance import (
 TrueNativeRankRelevance,DECKS,REPS,FIT_N,DEV_N,ARMS,GAMMA,seed,sensor
)
class Focused(unittest.TestCase):
 def test_first_original_source_role_seed_identity(self):
  s=[seed(role,di,rep,i) for role,n in (("FIT",FIT_N),("DEV",DEV_N))
     for di in range(2) for rep in REPS for i in range(n)]
  self.assertEqual(len(s),len(set(s)))
  self.assertEqual(len(s),512)
  self.assertEqual(len(ARMS),6)
  self.assertEqual(GAMMA,.75)
 def test_native_local_cells_only_learn_completed_public_outcome(self):
  m=TrueNativeRankRelevance([4.]*13,1.)
  row={"real_source_next_higher":True,"public_seen_rank_hist":(1,)+(0,)*12,
       "public_time_step":0}
  m.learn(row)
  self.assertEqual(m.feedback,1)
  self.assertEqual(len(m.cells),13)
  self.assertEqual([x.updates for x in m.cells],[1]*13)
  self.assertTrue(sensor((1,)+(0,)*12,0,0))
  raw=m.checkpoint()
  cold=TrueNativeRankRelevance.restore(raw)
  self.assertEqual(raw,cold.checkpoint())
  self.assertEqual(cold.feedback,1)
  self.assertEqual(cold.choose(6,(1,)+(0,)*12,1,0),
                   m.choose(6,(1,)+(0,)*12,1,0))
 def test_original_source_reward_tie_never_teaches_a_label(self):
  m=TrueNativeRankRelevance([4.]*13,1.)
  m.learn({"real_source_next_higher":None,
           "public_seen_rank_hist":(1,)+(0,)*12,"public_time_step":0})
  self.assertEqual(m.feedback,0)
  self.assertEqual([x.updates for x in m.cells],[0]*13)
 def test_original_native_rewards_not_implicit_source_known_oracle(self):
  m=TrueNativeRankRelevance([4.]*13,1.)
  self.assertEqual(m.choose(6,(0,0,0,0,0,0,1,0,0,0,0,0,0),1,0),0)
  self.assertFalse(hasattr(m,"deck"))
  self.assertFalse(hasattr(m,"env"))
if __name__=="__main__":
 unittest.main()
