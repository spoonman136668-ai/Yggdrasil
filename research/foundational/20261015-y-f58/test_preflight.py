"""Y-F58 public graph frontier source and protected cohort exclusion."""
import importlib.util,pathlib,sys,unittest
p=pathlib.Path(__file__).with_name("source_feasibility.py")
sp=importlib.util.spec_from_file_location("y58_fit",p)
m=importlib.util.module_from_spec(sp);sys.modules[sp.name]=m;sp.loader.exec_module(m)
class Tests(unittest.TestCase):
 def test_source_exclusion(self):
  with self.assertRaises(ValueError):m.source(691100,1324)
  with self.assertRaises(ValueError):m.source(692000,1328)
  self.assertTrue(set(m.FIT).isdisjoint(m.DIAG))
 def test_both_arrival_regimes_and_public_witness(self):
  for fam in m.FAMILY:
   stream,q,regime=m.source(691000,fam)
   self.assertIn(regime,("delayed_component_anchors","alternating_fragments"))
   self.assertEqual(len(stream),72)
   self.assertEqual(sum(x[3] for x in stream),36)
   full=m.full_public_reference(stream)
   self.assertEqual(len(full),12)
   self.assertEqual(sum(len(m.pack(r)) for r in full),144)
   self.assertEqual(m.solve(full,q),1)
 def test_causal_frontier_lossless_budget(self):
  stream,q,regime=m.source(691000,1320)
  mem=m.frontier_online(stream)
  self.assertLessEqual(len(mem),12)
  self.assertTrue(all(m.unpack(m.pack(r))==r for r in mem))
if __name__=="__main__":unittest.main()
