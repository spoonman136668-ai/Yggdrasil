"""C35 synthetic-only prereg and real two-action source custody falsifiers."""
import unittest
from research.mass_r7c35 import run as c

def public(x):
 return {"x":x,"y":4,"goal_x":8,"goal_y":4,
         "direction":0,"front_blocked":False}

def pair(a,b):
 initial=public(3)
 intermediate=public(4) if a==2 else initial
 end=public(5) if b==2 else intermediate
 real=[{"action":a,"before":initial,"after":intermediate,
        "reward":0.,"term":False,"trunc":False},
       {"action":b,"before":intermediate,"after":end,
        "reward":0.,"term":False,"trunc":False}]
 return {"pair":[a,b],"actual_selected_source_actions":real,
   "completed_two_original_actions":True,
   "actually_observed_next_front_blocked":False,
   "physical_trace_sha256":c.fp(real)}

def sample(family):
 return {"family":family,"public_initial":public(3),
  "all_nine_original_physical_pairs":{
      str(a)+str(b):pair(a,b) for a,b in c.PAIRS}}

class C35SourceOnly(unittest.TestCase):
 def test_frozen_no_old_consumed_worlds(self):
  p=c.validate()
  self.assertEqual(len(c.PAIRS),9)
  self.assertEqual(c.TICKS,(0,3,6))
  self.assertTrue(all(len(x["FIT"])==8 and len(x["FIT_CHECK"])==4
       and not set(x["FIT"])&set(x["FIT_CHECK"])
       for x in p["worlds"].values()))
  self.assertFalse(p["limits"]["noNativeNoveltyClaim"])
 def test_no_source_privileged_model_feature(self):
  a=sample("MiniGrid-FourRooms-v0")
  self.assertEqual(len(c.features(a,(1,2))),20)
  a["public_initial"]["private_map"]=0
  with self.assertRaises(ValueError):c.features(a,(1,2))
 def test_same_true_pair_exposure_and_two_action_labels(self):
  data=[sample(f) for f in c.P["worlds"] for _ in range(4)]
  model=c.Models(data)
  self.assertEqual(model.n,9*len(data))
  s=model.score(data[0],(2,0))
  self.assertEqual(set(s),{"two_step_source_conditional","equal_source_pair_prior",
     "strong_independent_full_public_linear","observed_context_FIT_count"})
  data[0]["all_nine_original_physical_pairs"]["00"]["actual_selected_source_actions"][1]["action"]=2
  with self.assertRaises(ValueError):c.Models(data)
 def test_true_physical_second_action_required(self):
  data=[sample(f) for f in c.P["worlds"]]
  data[0]["all_nine_original_physical_pairs"]["01"]["completed_two_original_actions"]=False
  with self.assertRaises(ValueError):c.Models(data)
if __name__=="__main__":unittest.main()
