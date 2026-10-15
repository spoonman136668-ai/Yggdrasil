"""Source-only tests; never execute whole future diagnostic or originals."""
import importlib.util,pathlib,sys,unittest
p=pathlib.Path(__file__).with_name("source_pilot.py")
s=importlib.util.spec_from_file_location("yf43",p)
m=importlib.util.module_from_spec(s)
sys.modules[s.name]=m
s.loader.exec_module(m)

class Preflight(unittest.TestCase):
    def test_source_split_and_holdout_exclusion(self):
        self.assertFalse(set(m.FIT_SEEDS)&set(m.DIAGNOSTIC_SEEDS))
        self.assertFalse(set(m.DIAGNOSTIC_SEEDS)&set(m.RESERVED_SEEDS))
        self.assertFalse(set(m.FAMILIES)&set(m.RESERVED_FAMILIES))
        with self.assertRaises(ValueError):
            m.source(343000,404,0,0,0,80001)
        with self.assertRaises(ValueError):
            list(m.training_examples((342100,),(400,)))
    def test_paired_public_first_is_exact(self):
        a=m.source(342000,400,0,0,0,90000)
        b=m.source(342000,400,0,0,1,90000)
        self.assertEqual(a[2][0],b[2][0])
        self.assertEqual(a[0],b[0])
    def test_context_has_no_private_source_fields(self):
        y,mode,channels=m.source(342000,400,0,0,0,90000)
        ref=m.references(342000,400,0,0)
        corr=m.reliabilities(ref)
        self.assertEqual(len(m.feature(channels[0],0,1,corr)),12)
        model=m.LearnedTaskRisk()
        self.assertEqual(len(model.packed_parameter_bytes()),144)
        # Training for a single disjoint fit identity checks actual weight update.
        model.fit(m.training_examples((342000,),(400,)),epochs=2)
        self.assertTrue(any(abs(x)>1e-10 for ws in model.weights.values() for x in ws))
        self.assertEqual(len(model.packed_parameter_bytes()),144)
    def test_physical_budget_and_duplicate(self):
        _,_,values=m.source(342000,400,0,0,0,90000)
        port=m.PurchasePort(values)
        port.buy(0)
        with self.assertRaises(ValueError):port.buy(0)
        port.buy(1)
        with self.assertRaises(ValueError):port.buy(2)
    def test_learner_cannot_fit_diagnostic_labels(self):
        with self.assertRaises(ValueError):
            list(m.training_examples((342100,),(400,)))
    def test_controls_public_only(self):
        ref=m.references(342000,400,0,0)
        corr=m.reliabilities(ref)
        model=m.LearnedTaskRisk()
        for arm in m.ARMS[:-1]:
            j=m.select(arm,.7,1,ref,corr,model,.17)
            self.assertIn(j,(1,2,3))
    def test_downstream_typed_tasks_distinct(self):
        outcomes=[m.task((True,True,False),f) for f in m.FAMILIES]
        self.assertGreater(len(set(outcomes)),1)

if __name__=="__main__":
    unittest.main()
