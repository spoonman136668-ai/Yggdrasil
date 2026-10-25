"""C37 offline FIT rights, native/R3 isolation, and factorial intervention falsifiers.

These are synthetic tests, not original-world scientific episodes.
"""
import unittest
from research.mass_r7c37 import run as c
from research.native.itd02.r1.native_policy import PublicGrid

def original_fixture(family):
 public={"x":4,"y":4,"goal_x":9,"goal_y":9,"direction":0,"front_blocked":False}
 trials={}
 for first in range(3):
  for second in range(3):
   trials[str(first)+str(second)]={
    "completed_two_original_actions":True,
    "actual_selected_source_actions":[{"action":first},{"action":second}],
    "real_two_step_goal_distance_improvement":float(first==0)}
 return {"family":family,"public_initial":public,
         "all_nine_original_physical_pairs":trials}

def trained():
 sample=[original_fixture(f) for f in c.P["new_original_public_development_worlds"] for _ in range(7)]
 motors={str(d):{k:1} for d,k in enumerate(["1,0","0,1","-1,0","0,-1"])}
 return c.CausalOptions(sample,motors)

class SourceOnlyC37(unittest.TestCase):
 def test_frozen_genuine_FIT_and_fresh_worlds(self):
  c.prereg()
  self.assertEqual(len(c.ARMS),8)
  self.assertEqual(sum(map(len,c.P["new_original_public_development_worlds"].values())),24)
  self.assertTrue(c.P["governance"]["neverScientificProtectedFirstUse"])
  self.assertFalse(set(c.P["new_original_public_development_worlds"]["MiniGrid-FourRooms-v0"])&
                   {86101,86103,86105,86107})
 def test_equal_FIT_model_for_every_source_actor(self):
  m=trained()
  self.assertEqual(m.fitted,42)
  self.assertEqual(m.model_sha,c.CausalOptions.from_snapshot(m.snapshot()).model_sha)
  self.assertTrue(all(c.predictor_mode(k) for k in c.ARMS))
  self.assertFalse(c.has_veto("native_no_veto"))
  self.assertTrue(c.has_veto("native_veto"))
 def test_source_only_and_original_R3_protected(self):
  m=trained()
  nav=c.make_nav(m.motors,(19,19))
  s=PublicGrid(4,4,9,9,0,False)
  proposed,selected,commit,pending=c.choose_action(nav,m,"MiniGrid-FourRooms-v0",s,
                            "original_r3",None,None,False)
  self.assertEqual(proposed,selected)
  self.assertFalse(commit)
  self.assertFalse(pending)
  p=s.__dict__.copy();p["hidden_world_grid"]="forbidden"
  with self.assertRaises(ValueError):
   m.predict("MiniGrid-FourRooms-v0",p,(0,2),"causal_two_step")
 def test_cannot_override_R3_forward(self):
  m=trained()
  nav=c.make_nav(m.motors,(19,19))
  s=PublicGrid(4,4,9,9,0,False)
  first=c.choose_action(nav,m,"MiniGrid-FourRooms-v0",s,"native_veto",None,None,False)
  if first[0]==2:self.assertEqual(first[1],2)
 def test_goal_motor_only_FIT_actual_forward_effects(self):
  m=trained()
  s=PublicGrid(4,4,9,9,0,False)
  self.assertEqual(type(c.motor_progress(m,s,0)),float)
  self.assertEqual(type(c.motor_progress(m,s,1)),float)

if __name__=="__main__":unittest.main()
