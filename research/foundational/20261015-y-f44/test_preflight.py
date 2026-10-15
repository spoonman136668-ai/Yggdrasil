"""Y-F44 source-only preflight, no complete train/diagnostic cohort run."""
import importlib.util,pathlib,sys,unittest
p=pathlib.Path(__file__).with_name("source_pilot.py")
s=importlib.util.spec_from_file_location("yf44_preflight",p)
m=importlib.util.module_from_spec(s);sys.modules[s.name]=m;s.loader.exec_module(m)

class Gate(unittest.TestCase):
    def test_source_and_mechanism_holdout(self):
        self.assertFalse(set(m.FIT)&set(m.DIAGNOSTIC))
        self.assertFalse(set(m.DIAGNOSTIC)&set(m.RESERVED))
        self.assertFalse(set(m.FAMILIES)&set(m.RESERVED_FAMILIES))
        with self.assertRaises(ValueError):m.source(361000,440,0,2,0,2)
        with self.assertRaises(ValueError):m.source(361100,440,0,0,0,2)
        with self.assertRaises(ValueError):m.source(362000,444,0,2,0,2)
    def test_matched_paired_first(self):
        a=m.source(361100,440,0,2,0,90000)
        b=m.source(361100,440,0,2,1,90000)
        self.assertEqual(a[0],b[0])
        self.assertEqual(a[2][0],b[2][0])
    def test_anchors_are_public_and_no_hidden_mechanism_feature(self):
        ref=m.references(361000,440,0,0)
        self.assertEqual(len(ref),24)
        corr=m.prior.reliabilities(ref)
        f=m.feature(.7,0,1,ref,corr)
        self.assertEqual(len(f),m.FEATURE_DIM)
        model=m.LatentRisk()
        self.assertEqual(len(model.packed_bytes()),168)
        subset=[row for i,row in zip(range(24),m.training_examples())]
        model.fit(subset,epochs=2)
        self.assertTrue(any(abs(x)>1e-9 for ws in model.weights.values() for x in ws))
    def test_two_physical_read_port(self):
        _,_,v=m.source(361100,440,0,2,0,90000)
        port=m.Port(v);port.buy(0);port.buy(1)
        with self.assertRaises(ValueError):port.buy(2)
        with self.assertRaises(ValueError):port.buy(1)
    def test_public_selector_controls(self):
        ref=m.references(361000,440,0,0)
        corr=m.prior.reliabilities(ref)
        model=m.LatentRisk()
        for arm in m.ARMS[:-1]:
            chosen=m.select(arm,.75,1,ref,corr,model,.17)
            self.assertIn(chosen,(1,2,3))
    def test_task_probabilities_bounded(self):
        for fam in m.FAMILIES:
            p=m.predicted_task_probability((.2,.4,.9),fam)
            self.assertGreater(p,0)
            self.assertLess(p,1)

if __name__=="__main__":unittest.main()
