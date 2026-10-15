"""Y-F54 source-only FIT provenance regression. NEVER execute diagnostic.

The original two F54 diagnostic attempts are consumed/FAILED; this validates
only that a later repair could support a separately preregistered experiment.
"""
import importlib.util,pathlib,sys,unittest
PATH=pathlib.Path(__file__).with_name("source_pilot.py")
s=importlib.util.spec_from_file_location("y_f54_fit_witness_repair",PATH)
m=importlib.util.module_from_spec(s);sys.modules[s.name]=m;s.loader.exec_module(m)
def witness(record,events):
    u,steps,v,indices,latest,tag=record
    assert len(steps)==len(indices)
    assert 1<=len(steps)<=3
    assert all(0<=i<len(events) for i in indices)
    cursor=u
    for (role,d),i in zip(steps,indices):
        edge=events[i]
        assert role==edge[1] and d in (-1,1)
        assert cursor==(edge[0] if d==1 else edge[2])
        cursor=edge[2] if d==1 else edge[0]
    assert cursor==v
    return True
class FITWitness(unittest.TestCase):
    def test_inversion_reverses_order_of_support(self):
        rec=(12,((0,1),(1,-1)),42,(3,8),8,0.)
        inv=m.inverted(rec)
        self.assertEqual(inv[3],(8,3))
        self.assertEqual(m.inverted(inv),rec)
    def test_all_fit_arms_have_real_public_witnesses(self):
        for seed,family in ((611000,1220),(611001,1221),(611002,1222)):
            events,question,paths=m.source(seed,family)
            self.assertEqual(len(events),64)
            for arm in m.ARMS[:-1]:
                mem=m.ingest(events,arm,[0.]*m.DIM)
                self.assertLessEqual(len(mem),m.CAP)
                for r in mem:
                    self.assertTrue(witness(r,events))
                    self.assertEqual(m.report_record(r)["serialized_payload_bytes"],12)
    def test_no_original_or_cross_fold_source(self):
        with self.assertRaises(ValueError):m.source(612000,1228)
        with self.assertRaises(ValueError):m.source(611000,1224)
    def test_used_diagnostic_cohorts_not_consumed_again(self):
        self.assertEqual((m.DIAG.start,m.DIAG.stop),(611100,611116))
        self.assertEqual(tuple(m.DIAG_FAM),(1224,1225,1226,1227))
        # These are identities for exclusion, not inputs to this test.
if __name__=="__main__":unittest.main()
