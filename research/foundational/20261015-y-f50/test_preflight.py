"""Y-F50 focused memory/control and query isolation tests (no diagnosis)."""
import importlib.util,pathlib,sys,unittest
p=pathlib.Path(__file__).with_name("source_pilot.py")
spec=importlib.util.spec_from_file_location("yf50_preflight",p)
m=importlib.util.module_from_spec(spec);sys.modules[spec.name]=m;spec.loader.exec_module(m)
class Preflight(unittest.TestCase):
 def test_disjoint(self):
  self.assertFalse(set(m.FIT)&set(m.DIAG))
  self.assertFalse(set(m.FIT_FAM)&set(m.DIAG_FAM))
  with self.assertRaises(ValueError):m.source(512000,828)
  with self.assertRaises(ValueError):m.source(511100,820)
 def test_frozen_memory_and_roles(self):
  events,query,paths=m.source(511000,820)
  self.assertEqual(len(events),64)
  self.assertEqual(len(paths),4)
  self.assertEqual(len(query["chain"]),3)
  self.assertEqual(m.solve(query["edges"],query),query["answer"])
  for mode in m.ARMS[:-1]:
   held=m.retained(events,mode,[0.]*m.FEATURES)
   self.assertEqual(len(held),12)
 def test_train_labels_not_diagnostic(self):
  w,n=m.train()
  self.assertEqual(n,16*4*64)
  self.assertEqual(len(w),m.FEATURES)
  self.assertTrue(any(abs(x)>1e-6 for x in w))
if __name__=="__main__":unittest.main()
