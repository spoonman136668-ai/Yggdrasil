"""Y-F55: no prospective diagnostic source used in train/validation."""
import importlib.util,pathlib,sys,unittest
p=pathlib.Path(__file__).with_name("online_fit_validation.py")
sp=importlib.util.spec_from_file_location("y55_online_validation",p)
m=importlib.util.module_from_spec(sp);sys.modules[sp.name]=m;sp.loader.exec_module(m)
class Test(unittest.TestCase):
 def test_no_diagnostic_or_original_seeds(self):
  self.assertTrue(set(m.TRAIN_SEEDS).isdisjoint(m.VALID_SEEDS))
  self.assertTrue(set(m.VALID_SEEDS).isdisjoint(m.src.DIAG))
  self.assertTrue(set(m.TRAIN_SEEDS).isdisjoint(m.src.ORIGINAL))
 def test_training_produces_quantized_global_state_weights(self):
  learned,code,n=m.fit()
  self.assertEqual(len(code),12)
  self.assertEqual(n,8*4*72)
  self.assertTrue(all(-127<=v<=127 for v in code))
 def test_online_equal_byte_controls(self):
  weights,_,_=m.fit()
  stream,q,paths=m.src.source(611000,1120)
  mem=m.prior.retain([e[:3] for e in stream],
       "learned_global_relation_state",weights)
  self.assertLessEqual(len(mem),12)
  self.assertLessEqual(12*len(mem),144)
if __name__=="__main__":unittest.main()
