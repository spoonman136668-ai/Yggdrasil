"""Y-F59 FIT-only novel arrival source and causal memory limits."""
import importlib.util,pathlib,sys,unittest
p=pathlib.Path(__file__).with_name("source_feasibility.py")
spec=importlib.util.spec_from_file_location("y59_source",p)
m=importlib.util.module_from_spec(spec);sys.modules[spec.name]=m;spec.loader.exec_module(m)
class Test(unittest.TestCase):
 def test_denied_diagnostic_and_original(self):
  self.assertFalse(set(m.FIT)&set(m.DIAG))
  with self.assertRaises(ValueError):m.source(711100,1364)
  with self.assertRaises(ValueError):m.source(712000,1368)
 def test_public_arrival_causality_and_lossless_codec(self):
  for fam in m.FAMILY:
   events,q,regime=m.source(711000,fam)
   self.assertIn(regime,("late_core_heads","overlapping_component_frontiers"))
   self.assertEqual(len(events),72)
   self.assertEqual(sum(v[3] for v in events),36)
   memory=m.fixed_deferred_component_buffer(events)
   self.assertLessEqual(len(memory),12)
   self.assertTrue(all(m.unpack(m.pack(z))==z for z in memory))
 def test_offline_public_feasibility_without_query(self):
  events,q,regime=m.source(711000,1360)
  complete=m.full_public_reference(events)
  self.assertEqual(len(complete),12)
  self.assertEqual(sum(len(m.pack(z)) for z in complete),144)
  self.assertEqual(m.solve(complete,q),1)
if __name__=="__main__":unittest.main()
