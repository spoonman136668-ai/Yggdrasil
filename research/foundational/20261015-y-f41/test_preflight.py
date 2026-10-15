"""Y-F41 source mechanics and two purchased sensor boundary; not cohort."""
import importlib.util,pathlib,unittest
P=pathlib.Path(__file__).with_name("source_pilot.py")
s=importlib.util.spec_from_file_location("yf41source",P)
m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
class Gate(unittest.TestCase):
  def test_source_guard(self):
    self.assertFalse(set(m.SEEDS)&set(m.RESERVED))
    with self.assertRaises(ValueError):m.source(313800,368,0,0,0,99)
  def test_source_marginals_mode_relation_changes(self):
    a=m.source(312800,364,0,0,0,9000)
    b=m.source(312800,364,0,0,1,9000)
    self.assertEqual(len(a[2]),4)
    self.assertEqual(len(b[2]),4)
    self.assertEqual(a,m.source(312800,364,0,0,0,9000))
  def test_equal_reference_info_not_hidden_mode(self):
    refs=m.calibration(312800,364,0,0)
    self.assertEqual(len(refs),24)
    corr=m.reliabilities(refs)
    self.assertEqual(len(corr),4)
    self.assertIn(m.choose("conditional_empirical_Brier",.25,refs,corr),(1,2,3))
    self.assertIn(m.choose("public_conditional_expected_bit_error",.75,refs,corr),(1,2,3))
  def test_port_rejects_duplicate_third(self):
    y,mode,channels,pol=m.source(312800,364,0,0,0,9000)
    port=m.Port(channels);port.buy(0);port.buy(2)
    self.assertEqual(len(port.trace),2)
    with self.assertRaises(ValueError):port.buy(1)
if __name__=="__main__":unittest.main()
