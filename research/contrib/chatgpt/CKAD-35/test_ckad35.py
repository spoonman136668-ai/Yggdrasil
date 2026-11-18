"""CKAD35 negative and non-pilot source-only interface tests."""
import importlib.util
import itertools
import unittest
from pathlib import Path

HERE=Path(__file__).resolve().parent
SPEC=importlib.util.spec_from_file_location("ckad35_frozen_source",HERE/"campaign.py")
C=importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(C)


class CKAD35Tests(unittest.TestCase):
    def test_seed_custody_and_enumeration(self):
        self.assertEqual(C.PILOT,(13851,13852))
        self.assertEqual(C.PRIMARY,(23851,23852,23853))
        self.assertEqual(len(C.TRANSFORMS),7680)
        self.assertEqual(len(C.MONOMIALS),42)
        self.assertFalse(set(C.PILOT)&set(C.PRIMARY))
        with self.assertRaises(ValueError):
            C.score(23851)
        with self.assertRaises(ValueError):
            C.score(99999)

    def test_input_only_design_and_exact_conventional_rank(self):
        for seed in (88735,88736): # DEV fixtures only, not pilot worlds
            donor,fit,cal,held=C.source_partition(seed)
            self.assertEqual((len(donor),len(fit),len(cal),len(held)),(42,10,6,16))
            self.assertEqual(len(set(fit+cal+held)),32)
            self.assertEqual(len(set(donor)),42)
            self.assertEqual(len(C.fit_independent([[x&31,x>>5,0] for x in donor])),42)

    def test_context_transform_does_not_modify_action(self):
        for x in range(64):
            for perm in (tuple(range(5)),tuple(reversed(range(5)))):
                for mask in (0,7,31):
                    out=C.context_transform(x,perm,mask)
                    self.assertEqual(x&32,out&32)
                    self.assertTrue(0<=out<64)

    def test_donor_numeric_memory_cold_transfer_dev_fixture(self):
        seed=88735
        donor,fit,cal,held=C.source_partition(seed)
        bank=C.compile_source_memory(seed,donor,fit,cal,held)
        self.assertTrue(bank["cold_bytes_exact"])
        self.assertTrue(bank["donor_exact_retention"])
        self.assertTrue(bank["target_exact_retention"])
        self.assertTrue(bank["conflict_atomic"])
        self.assertEqual(len(bank["donor_witness"]),3)
        self.assertEqual(len(bank["fit_witness"]),6)
        self.assertEqual(len(bank["calibration"]),6)
        self.assertEqual(len(bank["pressure_witness"]),4)
        self.assertEqual(bank["donor_native_tables"],bank["donor_conventional_tables"])
        for slot in C.DONORS:
            self.assertTrue(all(p in (0.,1.) for p in bank["donor_native_tables"][slot]))

    def test_conventional_analogy_parity_without_target_truth(self):
        seed=88736
        donor,fit,cal,held=C.source_partition(seed)
        bank=C.compile_source_memory(seed,donor,fit,cal,held)
        native=C.compatible(bank["donor_native_tables"],bank["fit_witness"][3],
                            bank["calibration"][3],held)
        exact=C.compatible(bank["donor_conventional_tables"],bank["fit_witness"][3],
                           bank["calibration"][3],held)
        self.assertEqual(native,exact)
        self.assertGreater(native[1]["fit_survivors"],0)
        self.assertGreater(native[1]["calibrated_survivors"],0)
        self.assertEqual(len(native[0]),16)
        self.assertTrue(all(0<=p<=1 for p in native[0]))
        targets,custody=C.native_target_control(seed,bank["fit_witness"],
                                                 bank["calibration"],held)
        self.assertTrue(custody["cold_exact"])
        self.assertEqual(len(targets),6)

    def test_fully_matched_target_only_negative_control(self):
        train=[[0,0,1],[1,0,0]]
        gf=C.fit_independent(train)
        self.assertEqual(C.predict_independent(gf,0),1.)
        self.assertEqual(C.predict_independent(gf,1),0.)
        self.assertEqual(C.predict_independent(gf,63),.5)
        with self.assertRaises(ValueError):
            C.fit_independent([[0,0,1],[0,0,0]])

    def test_stop_requires_both_independent_seeds_and_ood_veto(self):
        def make(seed,loss=.03,ood_veto=3,wrong=0):
            family={a:{"brier":.25,"cases":48} for a in C.ARMS}
            family["native_analogy"]={"brier":loss,"cases":48}
            family["conventional_analogy"]={"brier":loss,"cases":48}
            family["ungated_native_analogy"]={"brier":loss+.01,"cases":48}
            ood={a:{"brier":.35,"cases":48} for a in C.ARMS}
            ood["native_analogy"]={"brier":.25,"cases":48}
            ood["ungated_native_analogy"]={"brier":.4,"cases":48}
            return {"seed":seed,"metrics":{"isomorphic":family,"quartic_shift":ood},
                "committed_primitive_coverage":{"isomorphic":{"native_analogy":.75}},
                "confident_primitive_errors":{"isomorphic":{"native_analogy":0},
                                              "quartic_shift":{"native_analogy":wrong}},
                "target_compatible_counts":{
                    str(6+i):{"zero_survivor_veto":i<ood_veto} for i in range(3)},
                "native_custody":{"donor_exact_retention":True,
                    "target_exact_retention":True,
                    "cold_bytes_exact":True,"conflict_atomic":True},
                "target_native_custody":{"cold_exact":True}}
        a=make(13851);b=make(13852)
        self.assertEqual(C.classify([a,b])["decision"],"ENGINEERING_FEASIBLE")
        self.assertEqual(C.classify([a,make(13852,loss=.22)])["decision"],"SCREEN_NO_GO")
        self.assertEqual(C.classify([a,make(13852,ood_veto=1)])["decision"],"SCREEN_NO_GO")
        self.assertEqual(C.classify([a,make(13852,wrong=1)])["decision"],"SCREEN_NO_GO")
        with self.assertRaises(AssertionError):
            C.classify([b,a])

    def test_graph_is_boolean_on_public_labels(self):
        for g in C.GRAPH:
            for inp in itertools.product((0,1),repeat=3):
                self.assertIn(C.C30.composition(g,inp),(0,1))


if __name__=="__main__":
    unittest.main()
