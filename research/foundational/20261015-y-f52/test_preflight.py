import importlib.util,json,pathlib,sys,unittest
p=pathlib.Path(__file__).with_name("source_pilot.py")
spec=importlib.util.spec_from_file_location("y_f52",p)
m=importlib.util.module_from_spec(spec);sys.modules[spec.name]=m;spec.loader.exec_module(m)
pr=json.loads(pathlib.Path(__file__).with_name("prereg.json").read_text())
class Qualification(unittest.TestCase):
 def test_exact_frozen_arm_set_and_capacity(self):
  self.assertEqual(m.ARMS,(pr["candidate"],*pr["baseline_controls"],pr["unfair_control"]))
  self.assertEqual(m.CAPACITY,12);self.assertEqual(m.EVENTS,64);self.assertEqual(m.F_DIM,8)
 def test_cohort_identity_and_primary_original_exclusion(self):
  self.assertFalse(set(m.FIT)&set(m.DIAG));self.assertFalse(set(m.DIAG)&set(m.RESERVED))
  self.assertEqual([m.DIAG.start,m.DIAG.stop],pr["diagnostic_seeds"])
  for seed,fam in ((572000,1028),(531100,924),(571000,1024)):
   with self.assertRaises(ValueError):m.source(seed,fam)
 def test_fit_only_graph_features_and_query_isolation(self):
  events,query,paths=m.source(571000,1020)
  self.assertEqual(len(events),64);self.assertEqual(len(paths),4)
  self.assertEqual(len(query["chain"]),4)
  self.assertEqual(m.solve(query["edges"],query),query["answer"])
  features=m.public_features(events[0],events[:13],0)
  self.assertEqual(len(features),8)
  for a in m.ARMS[:-1]:
   kept,_=m.held_after_ingestion(events,a,[0.]*m.F_DIM)
   self.assertEqual(len(kept),12)
 def test_fit_uses_only_source_fit_cohorts(self):
  w,n=m.train()
  self.assertEqual(n,16*4*64)
  self.assertEqual(len(w),8)
if __name__=="__main__":unittest.main()
