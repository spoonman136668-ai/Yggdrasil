"""Y-F56 FIT-only public component-memory qualification."""
import importlib.util,pathlib,sys,unittest
path=pathlib.Path(__file__).with_name("source_feasibility.py")
sp=importlib.util.spec_from_file_location("y56_fitonly",path)
m=importlib.util.module_from_spec(sp);sys.modules[sp.name]=m;sp.loader.exec_module(m)
class Qualification(unittest.TestCase):
 def test_original_and_diag_rejected(self):
  self.assertFalse(set(m.FIT)&set(m.DIAG))
  self.assertFalse(set(m.FIT_FAMILIES)&set(m.DIAG_FAMILIES))
  with self.assertRaises(ValueError):m.source(631100,1164)
  with self.assertRaises(ValueError):m.source(632000,1168)
 def test_query_blind_serialization(self):
  public,q,regime=m.source(631000,1160)
  self.assertEqual(len(public),72)
  self.assertEqual(sum(e[3] for e in public),36)
  mem=m.online_fixed(public)
  self.assertLessEqual(len(mem),12)
  self.assertLessEqual(len(mem)*12,144)
  self.assertTrue(all(m.codec.unpack(m.codec.pack(*r))==r for r in mem))
 def test_offline_public_reference(self):
  public,q,regime=m.source(631000,1160)
  witness=m.offline_public_witness(public)
  self.assertEqual(m.codec.solve(witness,q),q["answer"])
  self.assertLessEqual(len(witness)*12,144)
if __name__=="__main__":unittest.main()
