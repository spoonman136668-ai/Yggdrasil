"""Source-only tests: no heldout evaluation or original execution."""
import importlib.util,pathlib,unittest
P=pathlib.Path(__file__).with_name("source_pilot.py")
s=importlib.util.spec_from_file_location("yf38",P);m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
class Contract(unittest.TestCase):
    def test_reserved_and_split_guards(self):
        self.assertFalse(set(m.SEEDS)&set(m.RESERVED_SEEDS))
        self.assertFalse(set(m.TRAIN)&set(m.VALIDATION))
        with self.assertRaises(ValueError):m.source(282800,274,0,0,0,1)
    def test_public_anchors_are_mode_blind(self):
        anchors=m.refs(281800,270,0,0)
        self.assertEqual(len(anchors),24)
        self.assertTrue(all(len(v)==4 and y in (0,1) for y,v in anchors))
        self.assertEqual(len(m.correlations(anchors)),4)
    def test_exact_two_paid_purchases(self):
        _,hidden,values,pol=m.source(281800,270,0,0,0,9000)
        port=m.Port(values)
        first=port.buy(0)
        j=m.choose("empirical_Brier",first,pol,m.refs(281800,270,0,0),
                   m.correlations(m.refs(281800,270,0,0)))
        self.assertIn(j,(1,2,3))
        port.buy(j)
        with self.assertRaises(ValueError):port.buy(0)
        with self.assertRaises(ValueError):port.buy(3)
        self.assertEqual(len(port.trace),2)
    def test_source_first_reading_informativeness_intervention(self):
        anchors=m.refs(281800,270,0,0);c=m.correlations(anchors)
        pol=m.source(281800,270,0,0,0,9000)[3]
        self.assertNotEqual(m.choose("public_polarity",.2,pol,anchors,c),
                            m.choose("public_polarity",.8,pol,anchors,c))
    def test_evaluator_information_is_separate(self):
        examples=[(0,0,0),(1,1,0),(0,1,1),(1,0,1)]*3
        self.assertGreaterEqual(m.conditional_information(examples)[0],0)
        self.assertEqual(set(m.holdout_logloss(examples,examples)),set(m.CONDITIONS))
if __name__=="__main__":unittest.main()
