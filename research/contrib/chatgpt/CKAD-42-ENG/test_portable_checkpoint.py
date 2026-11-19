"""CKAD42-ENG fixed fixture negative controls; NO original scientific seeds."""
import importlib.util
import json
import math
import sys
import unittest
from pathlib import Path

from yggdrasil.native_context_basis import digest

HERE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location("ckad42_fixture_unit",HERE/"fixtures.py")
F=importlib.util.module_from_spec(spec)
spec.loader.exec_module(F)
M=F.M


class PortableCheckpointFixtureTests(unittest.TestCase):
    def test_canonical_float_one_ulp_is_stable(self):
        examples=(1.23456789012345,-123.456789012345,0.000000000123456789012345,
                  123456.789012345,0.000000000000000000000000000123456789)
        for value in examples:
            canonical=M._canonical_learning_float(value)
            self.assertEqual(canonical,M._canonical_learning_float(math.nextafter(value,math.inf)))
            self.assertEqual(canonical,M._canonical_learning_float(math.nextafter(value,-math.inf)))
            self.assertEqual(canonical,M._canonical_learning_float(canonical))
        self.assertEqual(M._canonical_learning_float(-0.0),0.0)
        for bad in (math.nan,math.inf,-math.inf):
            with self.assertRaisesRegex(ValueError,"CKAD42_NONFINITE_CHECKPOINT_LEARNING_WEIGHT"):
                M._canonical_learning_float(bad)

    def test_float_codec_changes_checkpoint_not_training_weights(self):
        model=M.NativeInterventionRelations()
        source=[F.fixture_event("cycle",t) for t in range(72)]
        for event in source:
            model.observe(*event)
        original_native_full=model.transition.full.copy()
        original_terminal_short=model.terminal.short.copy()
        old_receipts=model.receipts.copy()
        checkpoint=model.checkpoint()
        self.assertEqual(model.transition.full,original_native_full)
        self.assertEqual(model.terminal.short,original_terminal_short)
        self.assertEqual(model.receipts,old_receipts)
        cold=M.NativeInterventionRelations.restore(checkpoint,digest(checkpoint))
        self.assertEqual(cold.checkpoint(),checkpoint)
        self.assertLessEqual(F._max_forecast_error(F.forecast_grid(model),
                                                   F.forecast_grid(cold)),1e-8)
        self.assertEqual(cold.receipts,model.receipts)
        self.assertEqual(cold.n,model.n)

    def test_checkpoint_ignores_artificial_subulp_perturbation(self):
        model=M.NativeInterventionRelations()
        for t in range(48):
            model.observe(*F.fixture_event("action_interactions",t))
        model.transition.full[0]=1.23456789012345
        model.terminal.short[17]=-12.3456789012345
        model.hedge[0]=.123456789012345
        canonical_before=model.checkpoint()
        raw_before=F._raw_state(model)
        model.transition.full[0]=math.nextafter(model.transition.full[0],math.inf)
        model.terminal.short[17]=math.nextafter(model.terminal.short[17],-math.inf)
        model.hedge[0]=math.nextafter(model.hedge[0],math.inf)
        self.assertNotEqual(F._raw_state(model),raw_before)
        self.assertEqual(model.checkpoint(),canonical_before)
        restored=M.NativeInterventionRelations.restore(canonical_before,
                                                         digest(canonical_before))
        self.assertEqual(restored.checkpoint(),canonical_before)

    def test_fixtures_never_call_original_or_held_world_generator(self):
        self.assertEqual(F.PROTOCOL_COMMIT,"30700bf17c75f1ef18354b82169f3b03c18c7b95")
        self.assertTrue(set(F.FORBIDDEN_SCIENCE_SEEDS).isdisjoint(
            tuple(range(0,3))))
        for kind in F.FIXTURE_KINDS:
            for t in (0,16,119,256,479):
                self.assertEqual(F.fixture_event(kind,t),F.fixture_event(kind,t))
                ident,views,row=F.fixture_event(kind,t)
                self.assertEqual(len(ident),64)
                self.assertEqual(views[0][0],views[1][0])
                self.assertEqual(set(row),{"s1","x1","s2","x2","y"})
        for bad in ("__held_seeds__", "__original_dev__", "pilot"):
            with self.assertRaisesRegex(ValueError,"CKAD42_ENG_FIXTURE_INPUT"):
                F.fixture_event(bad,0)

    def test_duplicate_conflict_and_nonfinite_checkpoint_fail_closed(self):
        model=M.NativeInterventionRelations()
        e=F.fixture_event("rule_shift",0)
        model.observe(*e)
        original=model.checkpoint()
        self.assertIs(model.observe(*e),model)
        altered=dict(e[2]);altered["y"]^=1
        with self.assertRaises(ValueError):
            model.observe(e[0],e[1],altered)
        self.assertEqual(model.checkpoint(),original)
        model.terminal.full[0]=math.inf
        with self.assertRaisesRegex(ValueError,"CKAD42_NONFINITE_CHECKPOINT_LEARNING_WEIGHT"):
            model.checkpoint()
        model.terminal.full[0]=0.0
        fixed=model.checkpoint()
        with self.assertRaisesRegex(ValueError,"CKAD42_CHECKPOINT_SHA_MISMATCH"):
            M.NativeInterventionRelations.restore(fixed,"0"*64)

    def test_fixture_160_event_cold_and_persistence_receipts(self):
        model=M.NativeInterventionRelations()
        for t in range(160):
            model.observe(*F.fixture_event("rule_shift",t))
        before=F.forecast_grid(model)
        raw=model.checkpoint()
        self.assertEqual(len(model.receipts),160)
        self.assertGreater(len(raw),1000)
        cold=M.NativeInterventionRelations.restore(raw,digest(raw))
        self.assertLessEqual(F._max_forecast_error(before,F.forecast_grid(cold)),1e-8)
        self.assertEqual(raw,cold.checkpoint())


if __name__=="__main__":
    unittest.main()
