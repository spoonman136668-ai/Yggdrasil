"""Y-F45 source-only tests, no diagnostic cohort execution."""
import importlib.util,pathlib,sys,unittest
p=pathlib.Path(__file__).with_name("source_pilot.py")
spec=importlib.util.spec_from_file_location("y_f45_preflight",p)
m=importlib.util.module_from_spec(spec);sys.modules[spec.name]=m;spec.loader.exec_module(m)
class Preflight(unittest.TestCase):
  def test_train_mechanism_and_original_isolation(self):
      self.assertFalse(set(m.FIT)&set(m.DIAGNOSTIC))
      self.assertFalse(set(m.DIAGNOSTIC)&set(m.RESERVED))
      self.assertFalse(set(m.FAMILIES)&set(m.RESERVED_FAMILIES))
      for args in ((381000,480,0,2,0,70000),(381100,480,0,0,0,70000),(382000,484,0,2,0,70000)):
          with self.assertRaises(ValueError):m.source(*args)
  def test_paired_public_anchor_truth_fixed(self):
      pairs=m.public_pairs(381000,480,0,0)
      self.assertEqual(len(pairs),12)
      self.assertEqual(len(m.flat(pairs)),24)
      self.assertTrue(all(a[0]==b[0] for a,b in pairs))
      self.assertTrue(any(a[1][0]!=b[1][0] for a,b in pairs))
  def test_learned_parameters_and_no_private_features(self):
      pairs=m.public_pairs(381000,480,0,0)
      corr=m.prior.reliabilities(m.flat(pairs))
      f=m.anchor_features(.7,1,1,pairs,corr)
      self.assertEqual(len(f),m.FEATURE_DIM)
      model=m.InvariantRisk()
      self.assertEqual(len(model.packed()),132)
      small=[z for i,z in zip(range(12),m.training_examples())]
      model.fit(small,epochs=1)
      self.assertTrue(any(abs(x)>1e-9 for w in model.weights.values() for x in w))
      self.assertEqual(len(model.packed()),132)
  def test_public_controls_and_intervention_ablation(self):
      pairs=m.public_pairs(381000,480,0,0)
      corr=m.prior.reliabilities(m.flat(pairs))
      model=m.InvariantRisk()
      for arm in m.ARMS[:-1]:
          self.assertIn(m.select(arm,.65,1,pairs,corr,model,.17),(1,2,3))
  def test_two_read_port(self):
      _,_,vals=m.source(381100,480,1,2,0,97000)
      port=m.Port(vals)
      port.buy(0);port.buy(2)
      with self.assertRaises(ValueError):port.buy(1)
      with self.assertRaises(ValueError):port.buy(2)
  def test_distinct_typed_tasks(self):
      self.assertGreater(len(set(m.task((True,True,False),f) for f in m.FAMILIES)),1)
if __name__=="__main__":unittest.main()
