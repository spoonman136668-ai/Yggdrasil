"""Y-F32 train-only source observability checks; withheld original untouched."""
import importlib.util,sys,unittest
from pathlib import Path
p=Path(__file__).with_name("pilot.py")
spec=importlib.util.spec_from_file_location("yf32",p)
m=importlib.util.module_from_spec(spec);sys.modules[spec.name]=m;spec.loader.exec_module(m)
class TestSource(unittest.TestCase):
    def test_disjoint_reserved_sources(self):
        self.assertFalse(set(m.SEEDS)&set(m.RESERVED))
        self.assertEqual(m.RESERVED_FAMILIES,(174,175,176,177))
    def test_calibration_not_given_latent_mode(self):
        calibration=m.anchors(183100,0,0)
        self.assertEqual(len(calibration),12)
        self.assertEqual(len(calibration[0]),2)
        self.assertEqual(len(calibration[0][1]),4)
    def test_physical_two_read_order_and_cost(self):
        calib=m.anchors(183100,0,0)
        y,hidden,source=m.source(183101,1,0,0,100)
        pub=m.custody.PublicSensorInfo((0.,0.,0.,0.),(0.,0.,0.,0.))
        sample=m.custody.evaluate_policy(source,pub,lambda _:0,
            lambda info,first:m.decide(calib,first,"polarity"),576,480)
        self.assertEqual(sample.physical_reads,2)
        self.assertEqual(sample.trace[0].sensor,0)
        self.assertIn(sample.trace[1].sensor,(1,2))
    def test_counterfactual_marker_changes_selection(self):
        refs=m.anchors(183102,0,1)
        low=m.custody.PurchasedReading(0,.2)
        high=m.custody.PurchasedReading(0,.8)
        self.assertNotEqual(m.decide(refs,low,"polarity"),
                            m.decide(refs,high,"polarity"))
    def test_mutual_information(self):
        same=[(0,0),(0,0),(1,1),(1,1)]
        self.assertAlmostEqual(m.latent_information(same),1.)
        independent=[(0,0),(0,1),(1,0),(1,1)]
        self.assertAlmostEqual(m.latent_information(independent),0.)
if __name__=="__main__":unittest.main()
