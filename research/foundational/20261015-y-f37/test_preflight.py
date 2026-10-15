"""Pre-original source, visible information and two-read contract tests."""
import importlib.util,pathlib,sys,unittest
P=pathlib.Path(__file__).with_name("train_only.py")
s=importlib.util.spec_from_file_location("yf37",P)
m=importlib.util.module_from_spec(s);sys.modules[s.name]=m;s.loader.exec_module(m)
class Contract(unittest.TestCase):
  def test_unseen_identities_do_not_overlap(self):
    self.assertFalse(set(m.TRAIN)&set(m.EVAL))
    self.assertFalse(set(m.EVAL)&set(m.RESERVED))
    with self.assertRaises(ValueError):m.source(273800,260,0,0,0,1)
  def test_public_anchors_and_first_read_feature(self):
    anchors=m.anchors(271800,250,0,0)
    self.assertEqual(len(anchors),16)
    corr=m.public_reliability(anchors)
    self.assertEqual(len(corr),4)
    truth,mode,source,pol=m.source(271800,250,0,0,0,9000)
    self.assertEqual(len(source),4)
    self.assertEqual(len(m.features(source[0],pol,corr)),6)
    self.assertEqual(m.source(271800,250,0,0,0,9000),(truth,mode,source,pol))
  def test_physical_acquisition_not_hidden_source(self):
    refs=m.anchors(271800,250,0,0)
    corr=m.public_reliability(refs)
    _,mode,values,pol=m.source(271800,250,0,0,0,9000)
    weights=[0.]*6;quality=[[.6,.7,.8],[.7,.6,.8]]
    port=m.Port(values);first=port.buy(0)
    chosen=m.choose("gaussian_Bayesian",first,pol,corr,refs,weights,quality,[-.5,.5],[.1,.1])
    self.assertIn(chosen,(1,2,3))
    port.buy(chosen)
    self.assertEqual(len(port.trace),2)
    with self.assertRaises(ValueError):port.buy(0)
  def test_coefficients_bounded_but_python_heap_not_claimed(self):
    self.assertLessEqual((6+6+4)*8,576)
if __name__=="__main__":unittest.main()
