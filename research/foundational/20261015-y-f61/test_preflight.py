"""F61 FIT-TRAIN-only preflight; no validation/DIAG/original materialization."""
import importlib.util,json,inspect,pathlib,sys,unittest
HERE=pathlib.Path(__file__).resolve().parent
p=HERE/"source_pilot.py"
spec=importlib.util.spec_from_file_location("y61_frozen_source_under_test",p)
m=importlib.util.module_from_spec(spec);sys.modules[spec.name]=m;spec.loader.exec_module(m)
class F61Preflight(unittest.TestCase):
    def test_frozen_prereg_and_source_identity(self):
        p=json.loads((HERE/"prereg.json").read_text())
        self.assertEqual(p["schema"],"yggdrasil.f61.learned-future-task-value-retention.prereg.v1")
        self.assertEqual(p["stage"],"PRECODE_FROZEN_NO_FIT_USE")
        self.assertEqual([m.FIT.start,m.FIT.stop],p["fit"]["seeds"])
        self.assertEqual([m.TRAIN.start,m.TRAIN.stop],p["fit"]["training"])
        self.assertEqual([m.VALIDATE.start,m.VALIDATE.stop],p["fit"]["validation"])
        self.assertEqual(list(m.FAMILIES),p["fit"]["families"])
        self.assertEqual([m.DIAG.start,m.DIAG.stop],p["diagnostic_NOT_AUTHORIZED"]["seeds"])
        self.assertEqual([m.ORIGINAL.start,m.ORIGINAL.stop],p["original_NOT_RESERVED"]["seeds"])
        self.assertEqual(list(m.ARMS),p["frozen_controls"])
        self.assertFalse(set(m.TRAIN)&set(m.VALIDATE))
        self.assertFalse(set(m.FAMILIES)&set(p["diagnostic_NOT_AUTHORIZED"]["families"]))
        self.assertEqual(m.CAP,12);self.assertEqual(m.PARAMS,12)
    def test_protected_source_denials(self):
        for seed,family in ((741100,1424),(742000,1428),
                            (741000,1424),(741100,1420)):
            with self.assertRaises(ValueError):m.source(seed,family)
    def test_public_tags_do_not_enter_online_policy(self):
        self.assertEqual(list(inspect.signature(m.learned_online).parameters),
                         ["public","w"])
        self.assertNotIn("question",m.learned_online.__code__.co_varnames)
        public,q,paths,regime=m.source(741000,1420)
        self.assertEqual(len(public),72)
        self.assertEqual(sum(e[3] for e in public),36)
        self.assertTrue(all(0<=e[1]<4 for e in public))
        self.assertEqual(len(paths),4)
        exposed=tuple(e[:3] for e in public)
        retention,work=m.learned_online(exposed,(0,)*12)
        self.assertLessEqual(len(retention),12)
        self.assertGreater(work,0)
        self.assertTrue(all(len(m.codec.pack(*r))==12 for r in retention))
        self.assertTrue(all(m.codec.unpack(m.codec.pack(*r))==r for r in retention))
        with self.assertRaises((ValueError,AssertionError,IndexError)):
            m.learned_online(public,(0,)*12)
    def test_exact_historical_controls_stay_distinct_and_query_blind(self):
        public,q,paths,regime=m.source(741001,1421)
        exposed=tuple(x[:3] for x in public)
        a=m.fixed_online(exposed,"F60_like_fixed_online")
        b=m.f60.online_fixed(exposed)
        self.assertEqual(a,b)
        a=m.fixed_online(exposed,"frozen_F59_deferred")
        b=m.f59.fixed_deferred_component_buffer(exposed)
        self.assertEqual(a,b)
        a=m.fixed_online(exposed,"frozen_F58_frontier")
        b=m.f58.frontier_online(exposed)
        self.assertEqual(a,b)
        witness=m.f60.offline_public_witness(exposed)
        self.assertEqual(len(witness),12)
        self.assertEqual(m.codec.solve(witness,q),q["answer"])
        for arm in m.ARMS[1:6]:
            memory=m.fixed_online(exposed,arm)
            self.assertLessEqual(len(memory),12)
            self.assertTrue(all(len(m.codec.pack(*r))==12 for r in memory))
    def test_training_only_and_nonzero_learning(self):
        w,n,pos=m.learn()
        self.assertEqual(len(w),12)
        self.assertTrue(all(type(x)==int and -127<=x<=127 for x in w))
        self.assertNotEqual(w,(0,)*12)
        self.assertGreater(n,1000);self.assertGreater(pos,0)
    def test_validation_entrypoint_is_inaccessible(self):
        self.assertFalse(hasattr(m,"run_diagnostic"))
        self.assertFalse(hasattr(m,"run_validation"))
if __name__=="__main__":unittest.main()
