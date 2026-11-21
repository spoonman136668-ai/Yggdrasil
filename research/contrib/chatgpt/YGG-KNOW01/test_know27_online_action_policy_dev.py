"""KNOW27 frozen source, action policy, provenance and cold controls."""
import json
import unittest
from know27_online_action_policy_dev import (
  SCHEMA,PROTO,PREREG,MODE,SEEDS,ABA_SEEDS,ARM,COST,LAWS,
  protocol,source,witness,true_bit,law_table,
  JointHypothesis,choose,expected_variance_reduction,new_model,
  run_world,proof,digest,fit_source,TRUE_MAPS
)

class KNOW27Tests(unittest.TestCase):
  def test_prereg_source_and_disjoint_held(self):
    d=protocol()
    self.assertEqual(d["schema"],PROTO)
    self.assertEqual(PREREG,"e48bcdffadec0be864ae6192ce6429a2906a98cf")
    self.assertEqual(d["held_stationary"]["action_witnesses_per_policy"],768)
    self.assertEqual(d["held_ABA"]["action_witnesses_per_policy"],192)
    self.assertEqual(COST,.002)
    self.assertTrue(set(SEEDS).isdisjoint(ABA_SEEDS))
    self.assertTrue(set(SEEDS+ABA_SEEDS).isdisjoint((13331,13347,14001,14007,14101)))
    self.assertEqual(MODE,"engineering_fixture_only")
    self.assertEqual(len({law_table(x) for x in LAWS}),4)
  def test_no_private_input_into_public_policy(self):
    m=JointHypothesis([1/6.]*6)
    e=expected_variance_reduction(m,0)
    self.assertEqual(len(e),4)
    self.assertTrue(all(isinstance(x,float) for x in e))
    a=choose("fit_evi",m,0,0)
    self.assertIn(a,(0,1,2,3))
    self.assertEqual(choose("fit_cyclic",m,0,7),3)
    self.assertEqual(choose("passive_p05",m,0,7),0)
    with self.assertRaises(ValueError):
      choose("fit_map_x2",m,0,0)
  def test_private_source_reject_and_one_consequence(self):
    for arg in [(True,14011,0,0),(0,True,0,0),(0,14011,32,0),
                (0,14011,0,True),(0,13331,0,0),
                (3,14011,0,0)]:
      with self.assertRaises(ValueError):
        source(*arg)
    with self.assertRaises(ValueError):
      source(0,14011,0,0,source_mode="original_owner")
    with self.assertRaises(ValueError):
      witness(0,14111,"H2",0,0,"ABA")
    for mid in range(3):
      for seed in SEEDS:
        for t in range(32):
          self.assertIn(witness(mid,seed,"H0",t,t%4),(0,1))
  def test_cold_replay_invariant(self):
    prior,_=fit_source(0)
    m=new_model("fit_evi",prior,0)
    for t in range(12):
      c=t%4;a=choose("fit_evi",m,c,t)
      y=witness(0,SEEDS[0],"H0",t,a)
      m.observe(t,c,a,y)
    raw=m.checkpoint()
    restored=JointHypothesis.restore(raw,digest(raw))
    self.assertEqual(raw,restored.checkpoint())
    self.assertEqual([m.prob(c,0) for c in range(8)],
                     [restored.prob(c,0) for c in range(8)])
    with self.assertRaises(ValueError):
      JointHypothesis.restore(raw,"0"*64)
    altered=raw.replace(b'"accepted_native":false',b'"accepted_native":true')
    with self.assertRaises(ValueError):
      JointHypothesis.restore(altered,digest(altered))
    duplicate=raw.replace(b'"events":',b'"events":[],"events":')
    with self.assertRaises(ValueError):
      JointHypothesis.restore(duplicate,digest(duplicate))
    with self.assertRaises(ValueError):
      m.observe(11,3,0,0)
  def test_held_budget_and_ABA_no_reset(self):
    prior,_=fit_source(0)
    r=run_world("fit_evi",0,SEEDS[0],"H0",0,prior)
    self.assertEqual(len(r["actions"]),32)
    self.assertEqual(r["events"],32)
    self.assertGreaterEqual(r["cost"],0.)
    b=run_world("fit_evi",0,ABA_SEEDS[0],"H0",0,prior,kind="ABA")
    self.assertEqual(len(b["actions"]),32)
    self.assertIsNotNone(b["pre_B"])
    self.assertIsNotNone(b["pre_return"])
    self.assertGreater(b["bytes"],0)
  def test_full_frozen_proof(self):
    r=proof()
    self.assertEqual(r["schema"],SCHEMA)
    self.assertEqual(r["prereg_commit"],PREREG)
    self.assertEqual((r["held_stationary_worlds"],r["held_ABA_worlds"]),(24,6))
    self.assertEqual((r["held_stationary_actions_per_policy"],r["held_ABA_actions_per_policy"]),(768,192))
    self.assertEqual(set(r["metrics"]),set(ARM))
    self.assertEqual(len(r["hypotheses"]),6)
    self.assertEqual(r["engineering_gate"],"PASS")
    self.assertEqual(r["scientific_gate"],"SCIENCE_NO_GO_SYNTHETIC_NOT_NATIVE")
    self.assertFalse(r["accepted_native_modified"])
    self.assertFalse(r["protected_original_first_use"])
    self.assertEqual(r["deployment"],"NONE")
    self.assertTrue(all(0<=m["total_active"]<=768 for m in r["metrics"].values()))

if __name__=="__main__":
  unittest.main()
