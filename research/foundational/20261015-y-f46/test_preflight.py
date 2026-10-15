import importlib.util,pathlib,sys,unittest
p=pathlib.Path(__file__).parent/"source_pilot.py"
s=importlib.util.spec_from_file_location("yf46",p)
m=importlib.util.module_from_spec(s);sys.modules[s.name]=m;s.loader.exec_module(m)
class F46(unittest.TestCase):
 def test_parent_frozen_originals_never_used(self):
  for seed in (401000,402000,382000):
   with self.assertRaises(ValueError):m.prior.source(seed,520,0,2,0,90000)
  self.assertEqual((m.DIAGNOSTIC.start,m.DIAGNOSTIC.stop),(401100,401108))
  self.assertEqual(tuple(m.prior.ARMS)[-2],"count_matched_shuffled_intervention_pairs")
 def test_shuffled_public_anchor_counts_and_deterministic_labels(self):
  pairs=m.prior.public_pairs(401100,520,2,0)
  shuffled=tuple((p[0],pairs[(i+1)%len(pairs)][1]) for i,p in enumerate(pairs))
  self.assertEqual(len(pairs),12)
  self.assertEqual(len(shuffled),12)
  self.assertEqual(sum(len(x) for x in shuffled),24)
  self.assertNotEqual(pairs,shuffled)
  self.assertTrue(all(a[0]==b[0] for a,b in zip(pairs,shuffled)))
 def test_mechanism_and_task_changed(self):
  self.assertNotEqual(m.prior.task((1,1,0),520),m.prior.task((1,1,0),521))
if __name__=="__main__":unittest.main()
