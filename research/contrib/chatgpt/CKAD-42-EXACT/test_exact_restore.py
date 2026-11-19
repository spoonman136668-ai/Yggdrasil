"""CKAD42-EXACT: nonlossy, deterministic engineering-fixture qualification.

Never scores prior scientific DEV or reserved pilot/primary seeds.
"""
from __future__ import annotations
import importlib.util
import json
import math
import sys
import unittest
from pathlib import Path

from yggdrasil.native_context_basis import digest

HERE=Path(__file__).resolve().parent
FIX=HERE.parent/"CKAD-42-ENG"/"fixtures.py"
spec=importlib.util.spec_from_file_location("ckad42_exact_original_fixture",FIX)
F=importlib.util.module_from_spec(spec)
spec.loader.exec_module(F)
M=F.M


class NonlossyCKAD42Tests(unittest.TestCase):
    def test_fixed_provenance_and_no_scientific_replay(self):
        protocol=json.loads((HERE/"protocol.json").read_text())
        self.assertEqual(protocol["parent"],"6550ee5a5a23c82e27995bf618506fbfaaf445dc")
        self.assertEqual(F.FORBIDDEN_SCIENCE_SEEDS,
                         (42111,42112,42211,42212,42311,42312,42313))
        self.assertEqual(M.DEV,(42111,42112))
        self.assertTrue(set(M.DEV).isdisjoint(M.PILOT+M.PRIMARY))
        self.assertEqual(F.FIXTURE_KINDS,("cycle","rule_shift","action_interactions"))

    def test_pinned_source_likelihoods_exact_binary64(self):
        self.assertEqual(M._SOURCE_LOGS[2][0].hex(),"-0x1.4cd6b97964179p-3")
        self.assertEqual(M._SOURCE_LOGS[2][1].hex(),"-0x1.e5a9a7c3ac418p+0")
        self.assertEqual(M._SOURCE_LOGS[4][0].hex(),"-0x1.af8e8210a415cp-4")
        self.assertEqual(M._SOURCE_LOGS[4][1].hex(),"-0x1.26bb1bbb55515p+1")
        self.assertEqual(M._PORTABLE_DECIMAL_CONTEXT.prec,42)

    def test_decimal_exp_precision_and_fail_closed(self):
        for value in (-1000.0,-80.0,-30.0,-3.5,-1.0,-.001,0.0,1.0):
            got=M._portable_exp(value)
            expected=math.exp(value)
            self.assertAlmostEqual(got,expected,delta=max(1e-16,expected*1e-13))
            self.assertEqual(got,M._portable_exp(value))
        for value in (float("nan"),float("inf"),float("-inf")):
            with self.assertRaisesRegex(ValueError,"CKAD42_NONFINITE_EXP_INPUT"):
                M._portable_exp(value)
        with self.assertRaisesRegex(ValueError,"CKAD42_NONFINITE_EXP_INPUT"):
            M._portable_exp(1)

    def test_snapshot_preserves_original_floats_without_quantization(self):
        model=M.NativeInterventionRelations()
        for t in range(32):
            model.observe(*F.fixture_event("cycle",t))
        # Deliberate non-round-number low bits: do not hide them at persistence.
        model.transition.full[0]=1.23456789012345
        model.terminal.short[17]=-12.3456789012345
        model.hedge[0]=0.123456789012345
        before=[model.transition.full[0],model.terminal.short[17],model.hedge[0]]
        raw=model.checkpoint()
        contents=json.loads(raw)
        self.assertEqual(contents["transition"]["full"][0],before[0])
        self.assertEqual(contents["terminal"]["short"][17],before[1])
        self.assertEqual(contents["hedge"][0],before[2])
        self.assertEqual(raw,F._raw_state(model))
        restored=M.NativeInterventionRelations.restore(raw,digest(raw))
        self.assertEqual(restored.checkpoint(),raw)
        self.assertEqual(F._max_forecast_error(F.forecast_grid(model),
                                               F.forecast_grid(restored)),0.0)

    def test_one_ulp_change_is_preserved_and_not_collapsed(self):
        model=M.NativeInterventionRelations()
        model.transition.full[0]=1.23456789012345
        before=model.checkpoint()
        model.transition.full[0]=math.nextafter(model.transition.full[0],math.inf)
        after=model.checkpoint()
        self.assertNotEqual(before,after)
        self.assertNotEqual(digest(before),digest(after))
        self.assertEqual(M.NativeInterventionRelations.restore(after,digest(after)).checkpoint(),after)

    def test_original_fixture_cold_exact_and_source_atomicity(self):
        model=M.NativeInterventionRelations()
        for t in range(36):
            model.observe(*F.fixture_event("action_interactions",t))
        snapshot=model.checkpoint()
        cold=M.NativeInterventionRelations.restore(snapshot,digest(snapshot))
        self.assertEqual(F.forecast_grid(model),F.forecast_grid(cold))
        last=F.fixture_event("action_interactions",35)
        self.assertIs(model.observe(*last),model)
        modified=dict(last[2]);modified["y"]^=1
        with self.assertRaisesRegex(ValueError,"CKAD42_CONFLICTING_SOURCE_ID"):
            model.observe(last[0],last[1],modified)
        self.assertEqual(model.checkpoint(),snapshot)

    def test_all_fixture_events_have_valid_public_consequences(self):
        ids=set()
        for kind in F.FIXTURE_KINDS:
            for t in (0,1,16,119,159,319,479):
                key,views,row=F.fixture_event(kind,t)
                self.assertNotIn(key,ids)
                ids.add(key)
                self.assertEqual(row["s1"],views[0][0])
                self.assertEqual(views[0][0],views[1][0])
                self.assertEqual(set(row),{"s1","x1","s2","x2","y"})
                self.assertTrue(all(type(v) is int and v in (0,1)
                                    for v in row.values()))


if __name__=="__main__":
    unittest.main()
