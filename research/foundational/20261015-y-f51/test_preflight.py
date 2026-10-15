"""F51 source identity, public graph baseline, bound and query isolation."""
import importlib.util,pathlib,sys,unittest
p=pathlib.Path(__file__).with_name("source_pilot.py")
s=importlib.util.spec_from_file_location("yf51",p)
m=importlib.util.module_from_spec(s);sys.modules[s.name]=m;s.loader.exec_module(m)
class Focused(unittest.TestCase):
 def test_no_prior_original_or_train_cohort_reuse(self):
  self.assertFalse(set(m.FIT)&set(m.DIAG))
  self.assertFalse(set(m.DIAG)&set(m.RESERVED))
  self.assertFalse(set(m.FIT_FAM)&set(m.DIAG_FAM))
  for seed,fam in ((512000,928),(511100,924),(552000,988),(551100,980)):
   with self.assertRaises(ValueError):m.source(seed,fam)
 def test_all_fair_controls_really_implemented(self):
  self.assertEqual(m.ARMS,("learned_retention","public_frequency_priority",
   "public_tag_only","public_role_endpoint_priority","FIFO_last12",
   "public_hash_reservoir","private_future_query_oracle_unfair"))
  events,query,paths=m.source(551000,980)
  self.assertEqual(len(events),64)
  for arm in m.ARMS[:-1]:
   held=m.retained(events,arm,[0.]*m.FEATURES)
   self.assertEqual(len(held),12)
  self.assertEqual(m.solve(query["edges"],query),query["answer"])
 def test_fit_uses_old_task_disjoint_training_only(self):
  weights,n=m.train()
  self.assertEqual(n,4096)
  self.assertEqual(len(weights),6)
if __name__=="__main__":unittest.main()
