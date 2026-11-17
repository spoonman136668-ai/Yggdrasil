"""WSP158 source-owned original FIT-only calibration safety, no held score here."""
from __future__ import annotations
import importlib.util
from fractions import Fraction
from pathlib import Path
import unittest

from yggdrasil.public_causal_cells import PublicCausalCells
from yggdrasil.native_stage_calibration import (
    ProgrammedNativeStageCalibration,alpha_fraction,GRID_NUMERATOR,
    COMPOSITE_BYTES,ORIGINAL_NATIVE_BYTES
)

ROOT=Path(__file__).resolve().parents[1]
DEV=ROOT/"research"/"contrib"/"chatgpt"/"WSP-158"/"development.py"
s=importlib.util.spec_from_file_location("_wsp158_pre_score_dev",DEV)
D=importlib.util.module_from_spec(s)
s.loader.exec_module(D)

class ProgrammedNativeCalibrationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.history=D.W.read_original_fit()

    def test_01_native_164_byte_inheritance_and_202_byte_cold_program(self):
        native=PublicCausalCells()
        raw=native.snapshot()
        self.assertEqual(len(raw),ORIGINAL_NATIVE_BYTES)
        candidate=ProgrammedNativeStageCalibration(raw,0,4)
        self.assertEqual(candidate.weights,(0,4))
        self.assertEqual(len(candidate.checkpoint()),COMPOSITE_BYTES)
        restored=ProgrammedNativeStageCalibration.restore(candidate.checkpoint())
        self.assertEqual(restored.checkpoint(),candidate.checkpoint())
        self.assertEqual(restored.native_checkpoint(),raw)
        self.assertEqual(native.snapshot(),raw)

    def test_02_exact_gridded_native_fractional_probability(self):
        n=PublicCausalCells()
        for x in (1,1,1,0):
            n.observe(0,1,x)
        original=n.snapshot()
        for idx in range(len(GRID_NUMERATOR)):
            out=ProgrammedNativeStageCalibration(original,idx,idx)
            alpha=alpha_fraction(idx)
            expected=(Fraction(3)+alpha)/(4+2*alpha)
            self.assertEqual(out.probability(0,1,0),expected)
            self.assertEqual(out.probability(0,1,1),expected)
            self.assertEqual(out.probability(0,0,0),Fraction(1,2))
            self.assertEqual(ProgrammedNativeStageCalibration.restore(
                out.checkpoint()).probability(0,1,0),expected)
        self.assertEqual(n.snapshot(),original)

    def test_03_invalid_bad_program_and_original_native_denied(self):
        raw=PublicCausalCells().snapshot()
        for a,b in ((True,1),(0,False),(-1,3),(5,4),(0,6)):
            with self.subTest(alpha=(a,b)):
                with self.assertRaises(ValueError):
                    ProgrammedNativeStageCalibration(raw,a,b)
        bad=bytearray(raw)
        bad[-1]^=1
        with self.assertRaises(ValueError):
            ProgrammedNativeStageCalibration(bytes(bad),1,1)
        with self.assertRaises(ValueError):
            ProgrammedNativeStageCalibration(raw[:-1],1,1)
        with self.assertRaises(ValueError):
            ProgrammedNativeStageCalibration(bytearray(raw),1,1)
        with self.assertRaises(ValueError):alpha_fraction(True)
        with self.assertRaises(ValueError):alpha_fraction(5)

    def test_04_tampered_composite_and_bad_version_denied(self):
        raw=ProgrammedNativeStageCalibration(PublicCausalCells().snapshot(),3,3).checkpoint()
        for position in (0,4,67,len(raw)-35,len(raw)-34,len(raw)-1):
            corrupt=bytearray(raw);corrupt[position]^=1
            with self.subTest(position=position):
                with self.assertRaises(ValueError):
                    ProgrammedNativeStageCalibration.restore(bytes(corrupt))
        for mutated in (raw[:-1],raw+b"\0",bytearray(raw),b"BAD!"+raw[4:]):
            with self.assertRaises(ValueError):
                ProgrammedNativeStageCalibration.restore(mutated)

    def test_05_invalid_public_slot_stage_retained_and_action_denied(self):
        out=ProgrammedNativeStageCalibration(PublicCausalCells().snapshot(),2,4)
        for a,action,stage,retained in (
            (0,0,True,False),(0,1,2,False),(-1,0,0,False),
            (7,0,0,False),(9,0,0,True),(0,2,0,False),
            (0,False,0,False),(0,0,0,1)):
            with self.subTest(request=(a,action,stage,retained)):
                with self.assertRaises(ValueError):
                    out.probability(a,action,stage,retained=retained)

    def test_06_original_three_replica_source_and_calibration_fit_rows(self):
        self.assertEqual(tuple(len(s) for s in self.history),(256,256,256))
        for r,source in enumerate(self.history):
            self.assertEqual(source[0]["seed"],1100000+10000*r)
            fit=tuple(source[:64]); valid=tuple(source[64:128])
            D.validate_fit_valid(fit,valid)
            selected,loss=D.select_calibration(fit,valid)
            independent,ind_loss=D._select_independent(fit,valid)
            self.assertEqual(selected,independent)
            self.assertEqual(loss,ind_loss)
            self.assertTrue(all(0<=i<5 for i in selected))

    def test_07_violation_of_fit_valid_split_and_seed_custody(self):
        source=self.history[0]
        fit=tuple(source[:64]);valid=tuple(source[64:128])
        for mutated_fit,mutated_valid in (
            (fit[:-1],valid),
            (fit,valid[:-1]),
            (tuple(dict(x) if i else {**x,"seed":1200000}
                   for i,x in enumerate(fit)),valid),
            (fit,tuple(dict(x) if i else {**x,"s2":None}
                       for i,x in enumerate(valid))),
            (fit,tuple(dict(x) if i else {**x,"seed":valid[1]["seed"]}
                       for i,x in enumerate(valid))),
        ):
            with self.assertRaises(ValueError):
                D.select_calibration(mutated_fit,mutated_valid)

    def test_08_original_native_exact_independent_equal_source_scores(self):
        for source in self.history:
            fit=tuple(source[:64]);valid=tuple(source[64:128])
            counts=D._independent_counts(fit)
            native=D.W.fit_native(fit)
            selection,loss=D.select_calibration(fit,valid)
            for target in D.TARGETS:
                index=selection[0 if target=="transition" else 1]
                m=ProgrammedNativeStageCalibration(native.snapshot(),
                   index if target=="transition" else 3,
                   index if target=="reward" else 3)
                for row in valid:
                    slot,action,truth=D.W.observation(row,target)
                    adr,ret=D.W.addr(slot)
                    pred=m.probability(adr,action,
                                      0 if target=="transition" else 1,
                                      retained=ret)
                    self.assertEqual(pred,
                        D._independent_p(counts,row,target,index))
                    self.assertIn(truth,(0,1))
            self.assertEqual(native.snapshot(),D.W.fit_native(fit).snapshot())

    def test_09_poison_historical_scored_suffix_does_not_change_program_or_checkpoint(self):
        for source in self.history:
            fit=tuple(source[:64]);valid=tuple(source[64:128])
            before=D.select_calibration(fit,valid)
            snap=D.W.fit_native(source[:192]).snapshot()
            poisoned=tuple(dict(x) for x in source)
            for i in range(192,256):
                poisoned[i]["s2"]^=1
                poisoned[i]["y"]^=1
            self.assertEqual(D.select_calibration(tuple(poisoned[:64]),
                                                  tuple(poisoned[64:128])),before)
            self.assertEqual(D.W.fit_native(poisoned[:192]).snapshot(),snap)
            self.assertNotEqual(poisoned[192],source[192])

    def test_10_two_weights_do_not_change_any_original_count_or_control(self):
        for source in self.history:
            native=D.W.fit_native(source[:192])
            original=native.snapshot()
            for a in (0,1,2,3,4):
                for b in (0,1,2,3,4):
                    op=ProgrammedNativeStageCalibration(original,a,b)
                    self.assertEqual(
                        ProgrammedNativeStageCalibration.restore(op.checkpoint())
                        .native_checkpoint(),original)
            self.assertEqual(native.snapshot(),original)
        script=DEV.read_text()
        for banned in ("import causal_gym","from causal_gym","env.reset(",
                       "env.do(","get_original_world(","source_private"):
            self.assertNotIn(banned,script)

if __name__=="__main__":
    unittest.main()
