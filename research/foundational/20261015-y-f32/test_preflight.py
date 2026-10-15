"""Y-F32 preflight: public metadata, physically purchased evidence, no holdout."""
import importlib.util,pathlib,sys,unittest
p=pathlib.Path(__file__).with_name("pilot.py")
spec=importlib.util.spec_from_file_location("yf32",p)
m=importlib.util.module_from_spec(spec);sys.modules[spec.name]=m;spec.loader.exec_module(m)
class Contract(unittest.TestCase):
    def test_reserved_original_excluded(self):
        self.assertFalse(set(m.SEEDS)&set(m.RESERVED_SEEDS))
        self.assertFalse(set(m.FAMILIES)&set(m.RESERVED_FAMILIES))
    def test_public_anchor_budget(self):
        a=m.anchors(191800,170,0)
        self.assertEqual(len(a),8)
        self.assertEqual(a,m.anchors(191800,170,0))
        self.assertEqual(len(m.calibration(a).reliability),4)
    def test_counterfactual_two_read_custody(self):
        a=m.anchors(191800,170,0);pub=m.calibration(a)
        _,_,values,orientation=m.obs(191800,0,170,0,9000)
        receipt=m.custody.evaluate_policy(values,pub,lambda _:0,
            lambda public,first:m.choose(first.value,orientation,a,public,"conditional_empirical"),
            576,m.ANCHORS*5*8)
        self.assertEqual(receipt.physical_reads,2)
        self.assertEqual(receipt.trace[0].sensor,0)
        self.assertIn(receipt.trace[1].sensor,(1,2,3))
    def test_public_orientation_conditioning_probe(self):
        data=[(0,0,1),(1,1,1),(0,1,-1),(1,0,-1)]*5
        self.assertLess(m.mutual_info(data,False),1e-9)
        self.assertGreater(m.mutual_info(data,True),.9)
if __name__=="__main__":unittest.main()
