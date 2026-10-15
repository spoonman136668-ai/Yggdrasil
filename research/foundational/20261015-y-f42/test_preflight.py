"""F42 source preflight never touches prospective heldout case outcomes."""
import importlib.util,pathlib,sys,unittest
p=pathlib.Path(__file__).with_name("source_pilot.py")
s=importlib.util.spec_from_file_location("yf42",p);m=importlib.util.module_from_spec(s);sys.modules[s.name]=m;s.loader.exec_module(m)
class Gate(unittest.TestCase):
  def test_identity_guard(self):
    self.assertFalse(set(m.SEEDS)&set(m.RESERVED))
    with self.assertRaises(ValueError):m.source(323800,384,0,0,0,9000)
  def test_first_channel_matched_exactly(self):
    for cond in (0,1):
      a=m.source(322800,380,0,0,cond,9000)
      self.assertEqual(len(a[2]),4)
    self.assertEqual(m.source(322800,380,0,0,0,9000)[2][0],
                     m.source(322800,380,0,0,1,9000)[2][0])
  def test_public_references_match_first_and_label(self):
    a=m.reference(322800,380,0,0)
    b=m.reference(322800,380,0,1)
    self.assertEqual(len(a),24)
    self.assertTrue(all(x[0]==y[0] and x[1][0]==y[1][0] for x,y in zip(a,b)))
  def test_incremental_gate_uses_strongest_conditional_control(self):
    scores={
      "conditional_empirical_Brier":{"accuracy":.86},
      "public_Gaussian_mode_posterior":{"accuracy":.83},
      "static_reference":{"accuracy":.72},
      "first_masked":{"accuracy":.72},
    }
    gain,baseline=m.fair_incremental_gain(scores)
    self.assertAlmostEqual(baseline,.86)
    self.assertAlmostEqual(gain,-.03)
  def test_physical_two_read_boundary(self):
    _,_,vals,pol=m.source(322800,380,0,0,0,9000)
    port=m.prior.Port(vals)
    port.buy(0);port.buy(1)
    self.assertEqual(len(port.trace),2)
    with self.assertRaises(ValueError):port.buy(2)
if __name__=="__main__":unittest.main()
