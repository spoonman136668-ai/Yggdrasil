"""Y-F34 strictly train-only independent source interface checks."""
import importlib.util,pathlib,sys,unittest
P=pathlib.Path(__file__).with_name("source_pilot.py")
s=importlib.util.spec_from_file_location("yf34pilot",P)
m=importlib.util.module_from_spec(s);sys.modules[s.name]=m;s.loader.exec_module(m)
class Contract(unittest.TestCase):
    def test_identity_enforcement(self):
        self.assertFalse(set(m.SEEDS)&set(m.RESERVED_SEEDS))
        self.assertFalse(set(m.FAMILIES)&set(m.RESERVED_FAMILIES))
        with self.assertRaises(ValueError):m.physical(212800,0,194,0,0,1)
    def test_new_mechanisms_and_contexts(self):
        a=m.physical(211800,0,190,0,0,8)
        b=m.physical(211800,0,190,0,1,8)
        self.assertEqual(len(a[2]),4)
        self.assertNotEqual(a[2],b[2])
        self.assertEqual(m.physical(211800,0,190,0,0,8),a)
    def test_public_calibration_and_purchase_port(self):
        a=m.public_reference(211800,190,0,0)
        self.assertEqual(len(a),16)
        pub=m.calibration(a)
        _,_,channels,polarity=m.physical(211800,0,190,0,0,99)
        rec=m.custody.evaluate_policy(channels,pub,lambda _:0,
            lambda info,first:m.choose("empirical_brier",first.value,polarity,a,info),
            576,m.EXTERNAL_ANCHOR_BYTES)
        self.assertEqual(rec.physical_reads,2)
        self.assertEqual(rec.trace[0].sensor,0)
        self.assertIn(rec.trace[1].sensor,(1,2,3))
    def test_evaluator_only_information_distinct(self):
        rows=[(0,0,1),(1,1,1),(0,1,-1),(1,0,-1)]*4
        self.assertAlmostEqual(m.group_mi(rows,True),
            m.independent.mi(rows,True),places=10)
if __name__=="__main__":unittest.main()
