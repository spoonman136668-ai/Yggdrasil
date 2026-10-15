"""F40 train-only public source and two-read guarantees; no EVAL cohort."""
import importlib.util,pathlib,unittest
P=pathlib.Path(__file__).with_name("train_only.py")
s=importlib.util.spec_from_file_location("yf40",P)
m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
class Gate(unittest.TestCase):
    def test_reserved_and_disjoint_ids(self):
        self.assertFalse(set(m.TRAIN)&set(m.EVAL))
        self.assertFalse(set(m.EVAL)&set(m.RESERVED))
        with self.assertRaises(ValueError):m.source(303800,340,0,0,0,1)
    def test_matched_first_marginals_not_direct_flag(self):
        # Same ±.30 source construction in both regimes, but different
        # dependence on private latent mode; public variance is not flag.
        a=m.source(301800,330,0,0,0,9000)
        b=m.source(301800,330,0,0,1,9000)
        self.assertEqual(len(a[2]),4)
        self.assertEqual(len(b[2]),4)
        self.assertNotEqual(a,b)
    def test_public_source_and_purchase_custody(self):
        refs=m.refs(301800,330,0,0)
        self.assertEqual(len(refs),24)
        corr=m.correlations(refs)
        hidden=m.source(301800,330,0,0,0,9000)
        self.assertEqual(len(m.public_features(hidden[2][0],hidden[3],refs,corr)),8)
        p=m.Port(hidden[2]);p.buy(0);p.buy(1)
        self.assertEqual(len(p.trace),2)
        with self.assertRaises(ValueError):p.buy(2)
    def test_train_only_supervision_and_inference_bytes(self):
        w,g,n,examples=m.train()
        self.assertEqual(len(w),8)
        self.assertGreater(n,0)
        self.assertGreater(examples,0)
        self.assertLessEqual(8*8,576)
        ref=m.refs(301800,330,0,0);corr=m.correlations(ref)
        self.assertIn(m.choose("learned_contextual_credibility",.25,1,ref,corr,w,g),(1,2,3))
if __name__=="__main__":unittest.main()
