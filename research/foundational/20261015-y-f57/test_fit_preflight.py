"""Y-F57 FIT-only feasibility unit checks."""
import importlib.util,pathlib,sys,unittest
p=pathlib.Path(__file__).with_name("source_feasibility.py")
s=importlib.util.spec_from_file_location("y57_source_checks",p)
m=importlib.util.module_from_spec(s);sys.modules[s.name]=m;s.loader.exec_module(m)
class Qualification(unittest.TestCase):
 def test_registered_identity(self):
  self.assertFalse(set(m.FIT)&set(m.DIAG))
  self.assertFalse(set(m.FIT_FAMILIES)&set(m.DIAG_FAMILIES))
  with self.assertRaises(ValueError):m.source(651100,1204)
 def test_full_public_prefixes(self):
  for family in m.FIT_FAMILIES:
   for seed in (651000,651001,651002):
    stream,question,regime=m.source(seed,family)
    packed=m.offline_public_witness(stream)
    self.assertEqual(len(packed),12)
    self.assertEqual(sum(len(m.codec.pack(*r)) for r in packed),144)
    self.assertEqual(m.codec.solve(packed,question),question["answer"])
 def test_online_budget(self):
  stream,question,regime=m.source(651000,1200)
  memory=m.online_fixed(stream)
  self.assertLessEqual(len(memory),12)
  self.assertEqual(sum(x[3] for x in stream),36)
if __name__=="__main__":unittest.main()
