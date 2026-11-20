"""G27 non-promoting shadow prediction controls; authentic cold readout runs in CI."""
from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path
import json
import sys
import unittest

from yggdrasil.native_context_basis import canonical, digest

ROOT = Path(__file__).resolve().parents[1]
HERE = ROOT / "research/contrib/chatgpt/CAUSAL-AMALGAM"
sys.path.insert(0, str(HERE))
MODULE_SPEC = spec_from_file_location("g27_shadow_readout", HERE / "headwise_shadow_readout.py")
MOD = module_from_spec(MODULE_SPEC)
MODULE_SPEC.loader.exec_module(MOD)
FIXTURE_SPEC = spec_from_file_location(
    "g27_original_g26_fixture", Path(__file__).with_name("test_amalgam_headwise_capsule.py"))
FIXTURE = module_from_spec(FIXTURE_SPEC)
FIXTURE_SPEC.loader.exec_module(FIXTURE)


class ReadOnlyShadowTests(unittest.TestCase):
    def setUp(self):
        self.anchor, self.after = FIXTURE.cases()
        self.raw, self.pin = FIXTURE.CAP.seal_capsule(
            self.anchor, self.anchor, self.after)

    def test_never_accepts_fixture_as_authentic_native_cold_restore(self):
        with self.assertRaisesRegex(ValueError, "G27_NATIVE_TYPE_REQUIRED"):
            MOD.materialize_research_readout(
                self.raw, self.pin, self.anchor, self.anchor, self.after,
                native_parent=b"irrelevant", native_pin="0" * 64,
                donor_parent=b"irrelevant", donor_pin="0" * 64)

    def test_frozen_prediction_does_not_change_its_original_source(self):
        before = self.after.checkpoint()
        shadow = MOD.FrozenShadowReadout(self.after, self.after._heads)
        views = ((0, 0), (0, 1))
        for first in (0, 1):
            for p in shadow.specialist_forecasts(views, first):
                self.assertGreaterEqual(p, 0)
                self.assertLessEqual(p, 1)
            for state in (0, 1):
                for second in (0, 1):
                    for p in shadow.specialist_forecasts(views, first, state, second):
                        self.assertGreaterEqual(p, 0)
                        self.assertLessEqual(p, 1)
        self.assertEqual(before, self.after.checkpoint())

    def test_research_readout_has_no_checkpoint_or_update_authority(self):
        shadow = MOD.FrozenShadowReadout(self.after, self.after._heads)
        with self.assertRaisesRegex(ValueError, "G27_NOT_AN_OFFICIAL_NATIVE_CHECKPOINT"):
            shadow.checkpoint()
        with self.assertRaisesRegex(ValueError, "G27_READ_ONLY_NO_TRAINING"):
            shadow.observe_experience("unconsumed", ((0, 0), (0, 1)), {})

    def test_detects_mutated_native_source_and_selected_head(self):
        first = MOD.FrozenShadowReadout(self.after, self.after._heads)
        self.after.native._ledger = self.after.native._ledger[:-1]
        with self.assertRaisesRegex(ValueError, "G27_SOURCE_MODEL_MUTATED"):
            first.specialist_forecasts(((0, 0), (0, 1)), 0)
        model = FIXTURE.cases()[1]
        second = MOD.FrozenShadowReadout(model, model._heads)
        second._heads[0].predictor_bias[0] += 0.25
        with self.assertRaisesRegex(ValueError, "G27_SELECTED_HEAD_MUTATED"):
            second.specialist_forecasts(((0, 0), (0, 1)), 0)

    def test_rehashed_g26_capsule_weight_forgery_is_still_rejected(self):
        record = json.loads(self.raw)
        record["selected_head_data"][0]["predictor_bias"][0] += 0.2
        forged = canonical(record)
        with self.assertRaisesRegex(ValueError, "G26_SOURCE_RECOMPUTE_MISMATCH"):
            FIXTURE.CAP.restore_capsule(
                forged, digest(forged), self.anchor, self.anchor, self.after)


if __name__ == "__main__":
    unittest.main()
