"""Train-only scientific interface checks; do not evaluate heldout rows."""
import importlib.util,pathlib,sys,unittest
P=pathlib.Path(__file__).with_name("train_only.py")
spec=importlib.util.spec_from_file_location("yf35",P)
m=importlib.util.module_from_spec(spec);sys.modules[spec.name]=m;spec.loader.exec_module(m)
class Gate(unittest.TestCase):
  def test_identity_separation(self):
    self.assertFalse(set(m.TRAIN)&set(m.EVAL))
    self.assertFalse(set(m.TRAIN_FAMILIES)&set(m.EVAL_FAMILIES))
    with self.assertRaises(ValueError):m.physical(212800,0,194,0,0,10)
  def test_public_calibration_and_sensor_visibility(self):
    a=m.source_reference(221800,210,0,0)
    self.assertEqual(len(a),16)
    pub=m.public_calibration(a)
    self.assertEqual(len(pub.reliability),4)
    truth,mode,channels,pol=m.physical(221800,0,210,0,0,9000)
    self.assertEqual(len(m.features(1,channels[0],pol,pub)),8)
    self.assertEqual(m.physical(221800,0,210,0,0,9000),(truth,mode,channels,pol))
  def test_sequential_real_acquisition(self):
    anchors=m.source_reference(221800,210,0,0)
    pub=m.public_calibration(anchors)
    _,_,values,pol=m.physical(221801,1,210,0,0,9001)
    weights=[[0.]*8 for _ in range(3)]
    receipt=m.custody.evaluate_policy(values,pub,lambda _:0,
      lambda p,first:m.public_choice("polarity_bayes",first.value,pol,anchors,p,weights),
      576,16*5*8)
    self.assertEqual(receipt.physical_reads,2)
    self.assertEqual(receipt.trace[0].sensor,0)
    self.assertIn(receipt.trace[1].sensor,(1,2,3))
  def test_weight_dimension_and_budget(self):
    self.assertEqual(3*m.NFEATURES,24)
    self.assertLessEqual(3*m.NFEATURES*8,m.NATIVE_CAP)
if __name__=="__main__":unittest.main()
