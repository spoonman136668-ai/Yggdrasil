"""Y-F55 FIT-only constructive online-memory feasibility preflight."""
import importlib.util,pathlib,sys,unittest
p=pathlib.Path(__file__).with_name("source_feasibility.py")
s=importlib.util.spec_from_file_location("y55_witness_fit",p)
m=importlib.util.module_from_spec(s);sys.modules[s.name]=m;s.loader.exec_module(m)
class Tests(unittest.TestCase):
 def test_originals_protected(self):
  self.assertFalse(set(m.FIT)&set(m.DIAG))
  with self.assertRaises(ValueError):m.source(612000,1128)
  with self.assertRaises(ValueError):m.source(611100,1120)
 def test_witness_same_144byte_budget_without_future_question(self):
  stream,q,paths=m.source(611000,1120)
  self.assertEqual(len(stream),72)
  core=set(e for path in paths for e in path["edges"])
  self.assertEqual(sum(e[3] for e in stream if e[:3] in core),16)
  self.assertEqual(sum(e[3] for e in stream if e[:3] not in core),20)
  retained,work=m.witness(stream)
  self.assertEqual(len(retained),12)
  self.assertEqual(sum(len(m.codec.pack(*x)) for x in retained),144)
  self.assertEqual(m.codec.solve(retained,q),q["answer"])
 def test_fit_witness_threshold_precode_only(self):
  r=m.fit_only_report()
  self.assertEqual(r["fit_streams"],64)
  self.assertGreaterEqual(r["public_reference_accuracy"],.25)
  self.assertTrue(r["disjoint_DIAG_unused"])
if __name__=="__main__":unittest.main()
