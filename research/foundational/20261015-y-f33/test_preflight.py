"""Y-F33 source-only tests; never run reserved original or full pilot."""
import importlib.util,pathlib,sys,unittest
here=pathlib.Path(__file__).resolve().parent
s=importlib.util.spec_from_file_location("yf33_source",here/"source_pilot.py")
m=importlib.util.module_from_spec(s);sys.modules[s.name]=m;s.loader.exec_module(m)

class Gate(unittest.TestCase):
    def test_disjoint_identities_and_reserved_rejection(self):
        self.assertFalse(set(m.SEEDS)&set(m.RESERVED_SEEDS))
        self.assertFalse(set(m.FAMILIES)&set(m.RESERVED_FAMILIES))
        with self.assertRaises(ValueError):m.source(202800,0,184,0,0,4)
    def test_two_distinct_sensor_mechanisms(self):
        a=m.source(201800,1,180,0,0,22)
        b=m.source(201800,1,180,0,1,22)
        self.assertEqual(len(a[2]),4)
        self.assertNotEqual(a[2],b[2])
    def test_public_calibration_and_two_purchase_port(self):
        a=m.anchors(201800,180,0,0)
        self.assertEqual(len(a),12)
        pub=m.calibrate(a)
        _,hidden,values,polarity=m.source(201800,1,180,0,0,33)
        receipt=m.prior.custody.evaluate_policy(values,pub,lambda _:0,
           lambda public,first:m.prior.choose(first.value,polarity,a,public,"static"),576,12*5*8)
        self.assertEqual(receipt.physical_reads,2)
        self.assertNotEqual(receipt.trace[0].sensor,receipt.trace[1].sensor)
    def test_evaluator_is_separate_from_decision(self):
        examples=[(0,0,1),(0,0,1),(1,1,1),(1,1,1),
                  (0,1,-1),(1,0,-1),(0,1,-1),(1,0,-1)]
        self.assertGreaterEqual(m.evaluator.mi(examples,True),0)
        self.assertEqual(m.evaluator.independently_audit(
            {"evaluator_only_private_mode_information":examples})["evaluator_private_records"],8)
if __name__=="__main__":unittest.main()
