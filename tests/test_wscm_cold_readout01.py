"""Focused native readout ablation contracts; no source first-use or mutation."""
import hashlib
from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path
import tempfile
import unittest

from yggdrasil.native_episode_experience import NativeEpisodeExperience

PATH = (Path(__file__).resolve().parents[1] /
        "research/contrib/chatgpt/WSCM-COLD-READ-01/cold_ablation.py")
SPEC = spec_from_file_location("wscm_cold_read", PATH)
MODULE = module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


def fixture():
    native = NativeEpisodeExperience()
    for i in range(32):
        public = i % 2
        views = ((public, i % 2), (public, (i+1) % 2))
        row = {"s1": public, "x1": i % 2, "s2": (i // 2) % 2,
               "x2": (i // 3) % 2, "y": (i // 4) % 2}
        native = native.observe(f"{i:064x}", views, row)
    return native.begin_context(novel=True)


class ColdReadoutContractTests(unittest.TestCase):
    def test_original_default_forecast_unchanged(self):
        x = fixture()
        before = x.checkpoint()
        for context in (0, 1):
            for action in (0, 1):
                self.assertEqual(MODULE.forecast(x, (context, 0), action),
                                 x.context_forecast((context, 0), action))
                for state in (0, 1):
                    self.assertEqual(
                        MODULE.forecast(x, (context, 0), action, state, 1),
                        x.context_forecast((context, 0), action, state, 1))
        self.assertEqual(x.checkpoint(), before)

    def test_full_and_pooled_are_exact_existing_native_reads(self):
        x = fixture()
        for variant in ("full", "pooled"):
            for context in (0, 1):
                for action in (0, 1):
                    value = MODULE.forecast(x, (context, 0), action, arm=variant)
                    self.assertTrue(0 < value < 1)
            self.assertEqual(x.checkpoint(), x.consolidate().checkpoint())

    def test_same_after_actual_native_cold_restore(self):
        x = fixture()
        blob = x.checkpoint()
        restored = NativeEpisodeExperience.restore(blob, hashlib.sha256(blob).hexdigest())
        for variant in ("default", "full", "pooled"):
            for context in (0, 1):
                self.assertEqual(
                    MODULE.forecast(x, (context, 0), 1, arm=variant),
                    MODULE.forecast(restored, (context, 0), 1, arm=variant))
                self.assertEqual(
                    MODULE.forecast(x, (context, 0), 1, 0, 1, arm=variant),
                    MODULE.forecast(restored, (context, 0), 1, 0, 1, arm=variant))

    def test_invalid_variant_fails_closed(self):
        with self.assertRaisesRegex(ValueError, "WSCM_READOUT_ARM"):
            MODULE.forecast(fixture(), (0, 0), 0, arm="fitted_oracle")

    def test_forged_joint_artifact_fails_before_restore(self):
        with tempfile.TemporaryDirectory() as tmp:
            p = Path(tmp) / "amalgam-joint-state.json"
            p.write_text('{"native_ascii":"fake"}')
            with self.assertRaisesRegex(ValueError, "WSCM_JOINT_ARTIFACT_SHA"):
                MODULE.load_native(p)

    def test_git_blob_and_rounding(self):
        raw = b"native"
        self.assertEqual(MODULE._git_blob(raw),
                         hashlib.sha1(b"blob 6\x00native").hexdigest())
        self.assertEqual(round(MODULE.forecast(fixture(), (0,0), 0) * 1000000),
                         round(fixture().context_forecast((0,0),0)*1000000))


if __name__=="__main__":
    unittest.main()
