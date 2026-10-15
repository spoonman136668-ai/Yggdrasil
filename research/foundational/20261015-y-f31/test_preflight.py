"""Y-F31 train-only headroom source controls. Does not touch reserved tests."""
import importlib.util,pathlib,sys,unittest
p=pathlib.Path(__file__).with_name("pilot.py")
spec=importlib.util.spec_from_file_location("yf31pilot",p)
m=importlib.util.module_from_spec(spec);sys.modules[spec.name]=m;spec.loader.exec_module(m)
class Check(unittest.TestCase):
    def test_split(self):
        self.assertFalse(set(m.PILOT_SEEDS)&set(m.RESERVED_TEST_SEEDS))
        self.assertFalse(set(m.PILOT_FAMILIES)&set(m.RESERVED_TEST_FAMILIES))
    def test_anchor_budget(self):
        a=m.anchors_for(181000,0,0)
        self.assertEqual(len(a),8)
        self.assertEqual(a,m.anchors_for(181000,0,0))
    def test_physical_two_read_identity(self):
        a=m.anchors_for(181001,0,0)
        _,_,v=m.make(181001,1,0,0,111)
        for method in m.ARMS[:-1]:
            j=m.decision(v[0],a,method)
            self.assertIn(j,(1,2,3))
            self.assertEqual(len((v[0],v[j])),2)
    def test_entropy_range(self):
        self.assertAlmostEqual(m.information([(0,0),(1,1)]),1.)
if __name__=="__main__":unittest.main()
