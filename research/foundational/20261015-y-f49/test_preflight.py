import importlib.util,pathlib,sys,unittest
p=pathlib.Path(__file__).with_name("source_pilot.py")
s=importlib.util.spec_from_file_location("y_f49",p)
m=importlib.util.module_from_spec(s);sys.modules[s.name]=m;s.loader.exec_module(m)
class Preflight(unittest.TestCase):
 def test_only_disjoint_train_and_no_original(self):
  self.assertFalse(set(m.DIAG)&set(m.RESERVED))
  self.assertFalse(set(m.DIAG)&set(m.OLD_RESERVED))
  for args in ((472000,724,0,2,0,50000),(421100,720,0,2,0,50000)):
   with self.assertRaises(ValueError):m.source(*args)
 def test_intervention_truth_and_public_shuffle(self):
  pair=m.pairs(471100,720,2,0)
  self.assertEqual(len(pair),12)
  self.assertTrue(all(a[0]==b[0] for a,b in pair))
  self.assertEqual(sorted(str(v) for v in m.flatten(pair)),
                   sorted(str(v) for v in m.flatten(m.shuffled(pair))))
  self.assertNotEqual(pair,m.shuffled(pair))
 def test_shared_policy_class_and_bounded_two_read(self):
  pair=m.pairs(471100,720,2,0)
  corr=m.base.reliabilities(m.flatten(pair))
  for arm in m.ARMS[:-1]:
   self.assertIn(m.decision(arm,.6,pair,corr),(1,2,3))
if __name__=="__main__":unittest.main()
