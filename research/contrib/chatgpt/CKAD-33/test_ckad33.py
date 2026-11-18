"""CKAD33 non-B interface, source isolation and falsification tests."""
import importlib.util
import itertools
import unittest
from pathlib import Path

from yggdrasil.native_context_accumulator import NativeContextAccumulator
from yggdrasil.native_context_basis import canonical,digest

HERE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location("ckad33_frozen",HERE/"campaign.py")
c=importlib.util.module_from_spec(spec)
spec.loader.exec_module(c)


class CKAD33NativeCompilerTests(unittest.TestCase):
    def test_source_only_full_rank_and_no_held_overlap(self):
        for seed in (87101,87102):  # synthetic unit fixtures; NOT pilot/primary
            fit,cal,held=c.rank_design(seed)
            self.assertEqual((len(fit),len(cal),len(held)),(16,4,12))
            self.assertEqual(len(set(fit+cal+held)),32)
            feature_rows=[[x&15,x>>4,0] for x in fit]
            self.assertEqual(len(c.source_span(feature_rows,2)),16)

    def test_native_numeric_compiler_matches_independent_conventional(self):
        fit,cal,held=c.rank_design(87101)
        law=(1,19,2,8)
        rows=[[x&15,x>>4,c.C30.effect(law,x)] for x in fit]
        native=c.stage(NativeContextAccumulator(4),0,rows,2)
        conv=c.source_span(rows,2)
        self.assertEqual(native.profile_info(0)["rank"],16)
        for x in range(32):
            self.assertEqual(c.read_compiled(native,0,x),
                             float(c.C30.effect(law,x)))
            self.assertEqual(c.forecast_conventional(conv,x,2),
                             float(c.C30.effect(law,x)))
        raw=native.checkpoint()
        cold=NativeContextAccumulator.restore(raw,digest(raw))
        self.assertEqual(cold.checkpoint(),raw)
        self.assertEqual(len(cold._model._profiles[0].support),16)

    def test_cubic_outside_class_revealed_by_unseen_input(self):
        fit,cal,held=c.rank_design(87102)
        law=(1,9,0,7)
        triple=(0,2,4)
        witness=[[x&15,x>>4,c.effect(law,triple,x)] for x in fit]
        native=c.stage(NativeContextAccumulator(4),0,witness,2)
        mismatches=[x for x in range(32) if
                    c.read_compiled(native,0,x)!=c.effect(law,triple,x)]
        self.assertTrue(mismatches)
        # OOD calibration must *not* create new source fits.
        checkpoint=native.checkpoint()
        _=any(x in mismatches for x in cal)
        self.assertEqual(native.checkpoint(),checkpoint)

    def test_native_atomic_conflict_and_retention(self):
        fit,cal,held=c.rank_design(87102)
        first=[[x&15,x>>4,c.C30.effect((0,7,2,6),x)] for x in fit]
        second=[[x&15,x>>4,c.C30.effect((1,13,4,9),x)] for x in fit]
        model=c.stage(c.stage(NativeContextAccumulator(4),0,first,2),1,second,2)
        frozen=model.checkpoint()
        conflict=[list(first[0])]
        conflict[0][2] ^= 1
        with self.assertRaises(ValueError):
            c.stage(model,0,conflict,2)
        self.assertEqual(model.checkpoint(),frozen)
        restored=NativeContextAccumulator.restore(frozen,digest(frozen))
        for x in range(32):
            self.assertEqual(c.read_compiled(restored,0,x),c.read_compiled(model,0,x))
            self.assertEqual(c.read_compiled(restored,1,x),c.read_compiled(model,1,x))

    def test_candidate_source_lock_and_unconsumed_seeds(self):
        self.assertEqual(c.PILOT,(13531,13532))
        self.assertEqual(c.RESERVED_PRIMARY,(23531,23532,23533))
        self.assertFalse(set(c.PILOT)&set(c.RESERVED_PRIMARY))
        with self.assertRaisesRegex(ValueError,"PRIMARY_SEED_FORBIDDEN"):
            c.score(23531)
        for g in c.GRAPHS:
            for vals in itertools.product((0,1),repeat=3):
                self.assertIn(c.C30.composition(g,vals),(0,1))

    def test_negative_gate_arithmetic_requires_both_seeds(self):
        def case(seed,compiled=0.,raw=.25,ood=0.25,naive=.45,
                 unsafe=0,cal=(False,False,False)):
            return {"seed":seed,
             "native_compiler":{"cold_restore_exact":True,
                 "retention_exact_all_32_inputs":True,
                 "conflict_rejection_atomic":True},
             "baseline_native":{"baseline_cold_and_retention_exact":True},
             "metrics":{"quadratic":{"compiled_native":{"brier":compiled},
                         "native_original":{"brier":raw},
                         "gf2_conventional":{"brier":compiled}},
                      "cubic_shift":{"compiled_native":{"brier":ood},
                         "uncalibrated_native":{"brier":naive}}},
             "coverage":{"quadratic":{"compiled_native":1.}},
             "confident_wrong":{"cubic_shift":{"compiled_native":unsafe}},
             "calibration_pass":{str(i+3):cal[i] for i in range(3)}}
        a=case(13531)
        b=case(13532)
        self.assertEqual(c.classify([a,b])["decision"],"ENGINEERING_FEASIBLE")
        self.assertEqual(c.classify([a,case(13532,ood=.60)])["decision"],"SCREEN_NO_GO")
        self.assertEqual(c.classify([a,case(13532,unsafe=1)])["decision"],"SCREEN_NO_GO")
        self.assertEqual(c.classify([a,case(13532) | {
            "native_compiler":{**b["native_compiler"],
                               "cold_restore_exact":False}}])["decision"],"INVALID")

    def test_no_source_oracle_given_to_compiler(self):
        self.assertEqual(c.feature_mask(0,2).bit_count(),1)
        self.assertEqual(c.feature_mask(31,2).bit_count(),16)
        self.assertEqual(c.feature_mask(31,3).bit_count(),26)
        with self.assertRaises(ValueError):
            c.feature_mask(32,2)
        with self.assertRaises(ValueError):
            c.source_span([[0,0,1],[0,0,0]],2)


if __name__=="__main__":
    unittest.main()
