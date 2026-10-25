"""C36 synthetic fixtures only. No new source physics in unit tests."""
import unittest
from research.mass_r7c36 import run as c
from research.native.itd02.r1.native_policy import PublicGrid

def row(family):
 pub={"x":4,"y":4,"goal_x":8,"goal_y":8,"direction":0,"front_blocked":False}
 d={}
 for a in range(3):
  for b in range(3):
   d[str(a)+str(b)]={"completed_two_original_actions":True,
      "actual_selected_source_actions":[{"action":a},{"action":b}],
      "real_two_step_goal_distance_improvement":float(a==0)}
 return {"family":family,"public_initial":pub,"all_nine_original_physical_pairs":d}

class FrozenC36(unittest.TestCase):
 def test_frozen_source_unchanged_and_unconsumed_worlds(self):
  c.prereg()
  self.assertEqual(c.P["trainOnly"]["expectedTruePairActions"],279)
  self.assertEqual(c.P["mechanism"]["frozenRidgePenalty"],10)
  self.assertTrue(c.P["limitations"]["notProtectedFirstUse"])
  self.assertTrue(c.P["governance"]["originalR3NeverModified"])
  self.assertEqual(len(set(sum((list(z) for z in c.P["freshPublicEpisodeEvaluation"].values()),[]))),8)
 def test_true_physical_pair_only_no_model_privileged_source(self):
  fit=[row(f) for f in c.P["freshPublicEpisodeEvaluation"] for _ in range(5)]
  motors={str(i):{k:1} for i,k in enumerate(["1,0","0,1","-1,0","0,-1"])}
  model=c.CausalOptions(fit,motors)
  self.assertEqual(model.fitted,len(fit)*3)
  restored=c.CausalOptions.from_snapshot(model.snapshot())
  self.assertEqual(restored.model_sha,model.model_sha)
  sample=fit[0]["public_initial"]
  self.assertEqual(len(c.feature(fit[0],(0,2))),14)
  self.assertEqual(model.predict(fit[0]["family"],sample,(0,2),"causal_two_step"),
                   restored.predict(fit[0]["family"],sample,(0,2),"causal_two_step"))
  sample["hidden_grid"]="forbidden"
  with self.assertRaises(ValueError):restored.predict(fit[0]["family"],sample,(0,2),"causal_two_step")
 def test_native_action_choice_does_not_exceed_r3_forward_rights(self):
  fit=[row(f) for f in c.P["freshPublicEpisodeEvaluation"] for _ in range(5)]
  motors={str(i):{k:1} for i,k in enumerate(["1,0","0,1","-1,0","0,-1"])}
  m=c.CausalOptions(fit,motors)
  nav=c.make_nav(motors,(19,19))
  s=PublicGrid(4,4,8,8,0,False)
  r3,ch,commit,complete=c.choose_action(nav,m,"MiniGrid-FourRooms-v0",s,"original_r3",None,None,False)
  self.assertEqual(r3,ch)
  self.assertFalse(commit)
  self.assertFalse(complete)
if __name__=="__main__":unittest.main()
