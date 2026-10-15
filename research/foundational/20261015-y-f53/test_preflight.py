"""Y-F53 FIT-only preflight: no heldout scientific test case used."""
import importlib.util,pathlib,sys,unittest
p=pathlib.Path(__file__).with_name("source_pilot.py")
s=importlib.util.spec_from_file_location("y53_preflight",p)
m=importlib.util.module_from_spec(s);sys.modules[s.name]=m;s.loader.exec_module(m)
class Test(unittest.TestCase):
 def test_source_isolation(self):
  self.assertFalse(set(m.FIT)&set(m.DIAG))
  self.assertFalse(set(m.FIT_FAM)&set(m.DIAG_FAM))
  with self.assertRaises(ValueError):m.source(572000,1008)
  with self.assertRaises(ValueError):m.source(571100,1000)
 def test_true_structure_and_codec(self):
  events,q,paths,motifs=m.source(571000,1000)
  self.assertEqual(len(events),72)
  self.assertEqual(len(paths),4)
  self.assertIn(len(q["ops"]),(4,6,8))
  self.assertEqual(len(motifs),12)
  for p in paths:
   for i in range(8):
    for n in range(1,min(6,8-i)+1):
     chunk=m.chunk_from_path(p,i,n)
     self.assertEqual(len(m.codec.pack(*chunk)),12)
     self.assertEqual(m.codec.unpack(m.codec.pack(*chunk)),chunk)
  self.assertEqual(m.codec.solve(
   [m.codec.edge_record(e) for e in paths[0]["edges"]],
   dict(start=paths[0]["start"],ops=paths[0]["ops"],answer=paths[0]["answer"])),paths[0]["answer"])
 def test_fit_only_and_memory(self):
  w,n,byte=m.train()
  self.assertEqual(len(w),9)
  self.assertEqual(len(byte),9)
  self.assertTrue(n>=64*100)
  public,q,paths,motifs=m.source(571000,1001)
  for arm in m.ARMS[:-1]:
   kept=m.retain(public,arm,w)
   self.assertLessEqual(len(kept),12)
   self.assertLessEqual(sum(len(m.codec.pack(*r)) for r in kept),144)
if __name__=="__main__":unittest.main()
