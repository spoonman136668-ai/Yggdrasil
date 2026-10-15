"""Y-F51 source-only checks, no prospective DIAG experiment during preflight."""
import importlib.util,pathlib,sys,unittest
p=pathlib.Path(__file__).with_name("source_pilot.py")
s=importlib.util.spec_from_file_location("y51_preflight",p)
m=importlib.util.module_from_spec(s);sys.modules[s.name]=m;s.loader.exec_module(m)
class Preflight(unittest.TestCase):
 def test_strict_identities(self):
  self.assertFalse(set(m.FIT)&set(m.DIAG))
  self.assertFalse(set(m.FIT_FAM)&set(m.DIAG_FAM))
  with self.assertRaises(ValueError):m.source(532000,928)
  with self.assertRaises(ValueError):m.source(531100,920)
 def test_tag_balance_and_query_boundary(self):
  events,q,paths=m.source(531000,920)
  core={e for path in paths for e in path["edges"]}
  self.assertEqual(len(events),64)
  self.assertEqual(sum(e[3] for e in events if e[:3] in core),8)
  self.assertEqual(sum(e[3] for e in events if e[:3] not in core),24)
  self.assertEqual(len(q["chain"]),4)
  self.assertEqual(m.solve(q["edges"],q),q["answer"])
 def test_retention_uses_only_cap_12(self):
  events,q,paths=m.source(531000,921)
  for arm in m.ARMS[:-1]:
   indices,_=m.held_after_ingestion(events,arm,[0.]*m.F_DIM)
   self.assertEqual(len(indices),12)
   self.assertEqual(len(set(indices)),12)
 def test_real_fit(self):
  weights,n=m.train()
  self.assertEqual(n,64*64)
  self.assertEqual(len(weights),m.F_DIM)
  self.assertTrue(any(abs(w)>1e-9 for w in weights))
if __name__=="__main__":unittest.main()
