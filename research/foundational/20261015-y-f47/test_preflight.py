"""Source-only controls; no complete prospective F47 training cohort."""
import importlib.util,pathlib,sys,unittest
p=pathlib.Path(__file__).with_name("source_pilot.py")
s=importlib.util.spec_from_file_location("yf47_preflight",p)
m=importlib.util.module_from_spec(s);sys.modules[s.name]=m;s.loader.exec_module(m)

class Preflight(unittest.TestCase):
 def test_strictly_disjoint_train_diag_and_original_identities(self):
  self.assertFalse(set(m.FIT)&set(m.DIAG))
  self.assertFalse(set(m.FIT_FAM)&set(m.DIAG_FAM))
  self.assertFalse(set(m.DIAG)&set(m.RESERVED))
  self.assertFalse(set(m.DIAG_FAM)&set(m.RESERVED_FAM))
  for args in ((432000,588,0,2,0,1000),(431000,580,0,2,0,1000),
               (431100,584,0,0,0,1000)):
   with self.assertRaises(ValueError):m.source(*args)
 def test_robust_and_ERM_share_features_and_labels(self):
  ref=m.references(431000,580,0,0)
  self.assertEqual(len(ref),24)
  corr=m.prior.prior.reliabilities(ref)
  self.assertEqual(len(m.features(.7,0,1,ref,corr)),m.FEATURE_DIM)
  subset=[x for i,x in zip(range(24),m.training_examples())]
  robust=m.RiskModel().fit(subset,True,epochs=1)
  erm=m.RiskModel().fit(subset,False,epochs=1)
  self.assertEqual(robust.training_count,erm.training_count)
  self.assertEqual(len(robust.packed_weights()),144)
  self.assertTrue(any(abs(w)>1e-10 for ws in robust.weights.values() for w in ws))
 def test_two_paid_reads(self):
  _,_,readings=m.source(431100,584,0,2,0,97000)
  port=m.Port(readings);port.buy(0);port.buy(2)
  with self.assertRaises(ValueError):port.buy(1)
 def test_all_controls_public(self):
  ref=m.references(431000,580,0,0)
  corr=m.prior.prior.reliabilities(ref)
  model=m.RiskModel()
  for arm in m.ARMS[:-1]:
   self.assertIn(m.select(arm,.7,1,ref,corr,model,model,.17),(1,2,3))
 def test_new_task_roles(self):
  outs=[m.task((True,True,False),fam) for fam in m.DIAG_FAM]
  self.assertGreater(len(set(outs)),1)

if __name__=="__main__":unittest.main()
