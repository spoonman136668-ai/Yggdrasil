"""Y-F52 source-only fit preflight; no diagnostic/original evaluation."""
import importlib.util,pathlib,sys,unittest
p=pathlib.Path(__file__).with_name("source_pilot.py")
s=importlib.util.spec_from_file_location("yf52_preflight",p)
m=importlib.util.module_from_spec(s);sys.modules[s.name]=m;s.loader.exec_module(m)
class Test(unittest.TestCase):
 def test_identity_and_stream(self):
  self.assertFalse(set(m.FIT)&set(m.DIAG))
  with self.assertRaises(ValueError):m.source(552000,968)
  with self.assertRaises(ValueError):m.source(551100,960)
  events,q,paths=m.source(551000,960)
  self.assertEqual(len(events),72)
  self.assertIn(len(q["ops"]),(4,6))
  self.assertEqual(len(paths),4)
 def test_exact_serialized_payload_and_composition(self):
  a=(3,22,(0,2,5))
  self.assertEqual(len(m.pack(*a)),12)
  self.assertEqual(m.unpack(m.pack(*a)),a)
  self.assertEqual(m.mirrored(m.mirrored(a)),a)
  self.assertEqual(m.join((1,2,(0,)),(2,3,(2,))),(1,3,(0,2)))
 def test_retention_hard_cap_and_oracle(self):
  ev,q,paths=m.source(551000,961)
  for arm in m.ARMS[:-1]:
   records=m.memory_after_stream(ev,arm,[0.]*m.DIMS)
   self.assertEqual(len(records),12)
   self.assertLessEqual(sum(len(m.pack(*r)) for r in records),144)
  self.assertEqual(m.solve([m.edge_record(e) for e in m.question_edges(ev,q)],q),q["answer"])
 def test_fit_only(self):
  w,n=m.train()
  self.assertEqual(n,16*4*72)
  self.assertEqual(len(w),m.DIMS)
  self.assertTrue(any(abs(x)>1e-8 for x in w))
if __name__=="__main__":unittest.main()
