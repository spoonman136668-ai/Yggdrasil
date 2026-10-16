"""Y-F60 FIT-only public corridor continuity and 144-byte witness."""
import importlib.util,pathlib,sys,unittest
p=pathlib.Path(__file__).with_name("source_feasibility.py")
t=importlib.util.spec_from_file_location("y60_source",p)
m=importlib.util.module_from_spec(t);sys.modules[t.name]=m;t.loader.exec_module(m)
class Tests(unittest.TestCase):
 def test_denied_protected_source(self):
  self.assertFalse(set(m.FIT)&set(m.DIAG))
  with self.assertRaises(ValueError):m.source(731100,1404)
  with self.assertRaises(ValueError):m.source(732000,1408)
 def test_both_new_public_arrival_patterns(self):
  for fam in m.FIT_FAMILIES:
   public,q,regime=m.source(731000,fam)
   self.assertIn(regime,("public_corridor_bursts","rolling_public_frontiers"))
   self.assertEqual(len(public),72)
   self.assertEqual(sum(e[3] for e in public),36)
   full=m.offline_public_witness(public)
   self.assertEqual(len(full),12)
   self.assertEqual(sum(len(m.codec.pack(*rec)) for rec in full),144)
   self.assertEqual(m.codec.solve(full,q),q["answer"])
 def test_fixed_online_causal_storage(self):
  stream,q,regime=m.source(731000,1400)
  memory=m.online_fixed(stream)
  self.assertLessEqual(len(memory),12)
  self.assertTrue(all(m.codec.unpack(m.codec.pack(*z))==z for z in memory))
if __name__=="__main__":unittest.main()
