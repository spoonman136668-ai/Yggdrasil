"""Y-F39 source and training-only trust gate, no heldout cohort."""
import importlib.util,pathlib,unittest
P=pathlib.Path(__file__).with_name("train_only.py")
s=importlib.util.spec_from_file_location("yf39",P)
m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
class CredibilityGate(unittest.TestCase):
    def test_source_custody_and_disjoint_cohorts(self):
        self.assertFalse(set(m.TRAIN)&set(m.EVAL))
        self.assertFalse(set(m.EVAL)&set(m.RESERVED))
        with self.assertRaises(ValueError):m.source(292800,288,0,0,0,9)
    def test_reference_features_exclude_private_mode(self):
        refs=m.public_refs(291800,280,0,0)
        self.assertEqual(len(refs),24)
        public=m.correlations(refs)
        hidden=m.source(291800,280,0,0,0,9000)
        self.assertEqual(len(m.public_features(refs,public,hidden[2][0],hidden[3])),m.WEIGHTS)
    def test_exact_two_purchases_and_duplicate_rejection(self):
        _,mode,channels,pol=m.source(291800,281,0,0,0,9000)
        p=m.PaidPort(channels)
        p.buy(0);p.buy(1)
        self.assertEqual(len(p.trace),2)
        with self.assertRaises(ValueError):p.buy(2)
    def test_train_only_learned_credibility_parameters(self):
        weights,count=m.train_gate()
        self.assertEqual(len(weights),6)
        self.assertGreater(count,0)
        self.assertLessEqual(len(weights)*8,576)
        refs=m.public_refs(291800,281,0,0)
        corr=m.correlations(refs)
        self.assertIn(m.choose("learned_trust_gate",.3,1,refs,corr,weights),(1,2,3))
if __name__=="__main__":unittest.main()
