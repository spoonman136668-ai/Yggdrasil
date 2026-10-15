"""Y-F57 focused FIT-only policy evidence checks (no validation use)."""
import importlib.util,pathlib,sys,unittest
p=pathlib.Path(__file__).with_name("learned_streaming_policy.py")
s=importlib.util.spec_from_file_location("y57_policy_preflight",p)
m=importlib.util.module_from_spec(s);sys.modules[s.name]=m;s.loader.exec_module(m)
class Checks(unittest.TestCase):
 def test_fit_custody(self):
  self.assertTrue(set(m.TRAIN).isdisjoint(m.VALID))
  self.assertTrue(set(m.TRAIN).isdisjoint(m.src.DIAG))
  self.assertTrue(set(m.VALID).isdisjoint(m.src.ORIGINAL))
  with self.assertRaises(ValueError):m.src.source(651100,1204)
 def test_online_compact_state(self):
  stream,question,regime=m.src.source(651000,1200)
  weights=(4,1,-1,4,0,1)
  memory=m.learned_memory(stream,weights)
  self.assertLessEqual(len(memory),12)
  self.assertLessEqual(sum(len(m.codec.pack(*r)) for r in memory),144)
  self.assertTrue(all(m.codec.unpack(m.codec.pack(*r))==r for r in memory))
  self.assertEqual(len(stream),72)
 def test_deterministic_fit_training(self):
  weights,n,candidates=m.train()
  self.assertEqual(len(weights),6)
  self.assertTrue(all(-8<=v<=8 for v in weights))
  self.assertGreaterEqual(candidates,4)
  self.assertLessEqual(candidates,64)
  self.assertEqual(n,m.eval_policy(weights,m.TRAIN))
if __name__=="__main__":unittest.main()
