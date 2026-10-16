"""Y-F55 FIT-only learned causal-memory preflight; never samples DIAG."""
import importlib.util,pathlib,sys,unittest,inspect
p=pathlib.Path(__file__).with_name("source_pilot.py")
s=importlib.util.spec_from_file_location("y_f55_fit_learned",p)
m=importlib.util.module_from_spec(s);sys.modules[s.name]=m;s.loader.exec_module(m)
class F55FIT(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.weights,cls.samples,cls.positives=m.train()
    def test_cohorts_and_no_original(self):
        self.assertEqual((m.base.FIT.start,m.base.FIT.stop),(611000,611016))
        self.assertEqual((m.base.DIAG.start,m.base.DIAG.stop),(611100,611116))
        self.assertEqual((m.base.ORIGINAL.start,m.base.ORIGINAL.stop),(612000,612016))
        with self.assertRaises(ValueError):m.base.source(612000,1128)
        with self.assertRaises(ValueError):m.base.source(611000,1124)
    def test_genuine_fit_supervision_and_quantization(self):
        self.assertGreater(self.samples,1000)
        self.assertGreater(self.positives,0)
        self.assertEqual(len(self.weights),8)
        self.assertTrue(all(type(x) is int and -127<=x<=127 for x in self.weights))
        self.assertNotEqual(tuple(self.weights),(0,)*8)
    def test_future_query_not_part_of_action_interface(self):
        self.assertEqual(list(inspect.signature(m.retain_online).parameters),
                         ["public","arm","quant","debug"])
        self.assertNotIn("future",m.retain_online.__code__.co_varnames)
    def test_real_public_fit_witnesses_and_online_byte_limits(self):
        for seed,fam in ((611000,1120),(611001,1121)):
            public,q,_truth=m.base.source(seed,fam)
            reference,work=m.base.witness(public)
            self.assertEqual(len(reference),12)
            self.assertGreater(work,72)
            self.assertEqual(m.codec.solve(reference,q),q["answer"])
            for arm in m.ARMS[:-1]:
                mem,ops=m.retain_online(public,arm,self.weights,debug=True)
                self.assertLessEqual(len(mem),12)
                self.assertLessEqual(sum(len(m.codec.pack(*r)) for r in mem),144)
                self.assertTrue(all(m.codec.unpack(m.codec.pack(*r))==r for r in mem))
                self.assertGreater(ops,0)
    def test_fit_only_reserved_seed_guard(self):
        self.assertFalse(set(m.base.FIT)&set(m.base.DIAG))
        self.assertFalse(set(m.base.FIT_FAM)&set(m.base.DIAG_FAM))
if __name__=="__main__":unittest.main()
