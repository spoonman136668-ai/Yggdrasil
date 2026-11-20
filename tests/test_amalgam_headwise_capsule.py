"""G26 real JEPA specialist sidecar: same-process and separate-process cold controls."""
from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path
import json
import subprocess
import sys
import tempfile
import unittest

from yggdrasil.native_context_basis import canonical, digest

HERE = Path(__file__).resolve().parents[1] / "research/contrib/chatgpt/CAUSAL-AMALGAM"
sys.path.insert(0, str(HERE))
CAPSPEC = spec_from_file_location("g26_capsule", HERE / "headwise_capsule.py")
CAP = module_from_spec(CAPSPEC)
CAPSPEC.loader.exec_module(CAP)

# Existing fixture classes and already-authored real direct/temporal JEPA heads.
BASESPEC = spec_from_file_location(
    "g26_preexisting_real_head_fixture",
    Path(__file__).with_name("test_amalgam_headwise_consolidation.py"))
BASE = module_from_spec(BASESPEC)
BASESPEC.loader.exec_module(BASE)


def cases():
    anchor = BASE._Core(BASE._history())
    after = anchor.clone(BASE._history() + (
        ("consumed-24", ((0, 0), (0, 1)), 0, 0, 0, 0),))
    return anchor, after


class SourceBoundColdCapsule(unittest.TestCase):
    def setUp(self):
        self.anchor, self.after = cases()

    def test_canonical_roundtrip_recomputes_exact_original_weights(self):
        before = (self.anchor.checkpoint(), self.after.checkpoint())
        raw, pin = CAP.seal_capsule(self.anchor, self.anchor, self.after)
        heads, proof = CAP.restore_capsule(
            raw, pin, self.anchor, self.anchor, self.after)
        self.assertLess(len(raw), CAP.MAX_CAPSULE_BYTES)
        self.assertEqual(proof["capsule_sha256"], pin)
        self.assertTrue(proof["source_checkpoint_pins_verified"])
        self.assertTrue(proof["selected_head_bytes_recomputed"])
        self.assertEqual(len(heads), 4)
        self.assertFalse(proof["canonical_native_model_restored"])
        self.assertFalse(proof["official_source_equivalent_restore_supported"])
        self.assertFalse(proof["scientific_pass"])
        data = json.loads(raw)
        self.assertEqual(
            canonical(data["selected_head_data"]),
            canonical([CAP._saved(h) for h in heads]))
        self.assertEqual(before, (self.anchor.checkpoint(), self.after.checkpoint()))

    def test_forged_weights_even_with_rehashed_capsule_rejected(self):
        raw, _ = CAP.seal_capsule(self.anchor, self.anchor, self.after)
        item = json.loads(raw)
        item["selected_head_data"][0]["predictor_bias"][0] += 0.3
        forged = canonical(item)
        with self.assertRaisesRegex(ValueError, "SOURCE_RECOMPUTE_MISMATCH"):
            CAP.restore_capsule(
                forged, digest(forged), self.anchor, self.anchor, self.after)

    def test_forged_alpha_even_with_rehashed_capsule_rejected(self):
        raw, _ = CAP.seal_capsule(self.anchor, self.anchor, self.after)
        item = json.loads(raw)
        item["alpha_by_head"]["direct_transition"] = 0.0
        forged = canonical(item)
        with self.assertRaisesRegex(ValueError, "SOURCE_RECOMPUTE_MISMATCH"):
            CAP.restore_capsule(
                forged, digest(forged), self.anchor, self.anchor, self.after)

    def test_forged_origin_or_source_refit_rejected(self):
        raw, pin = CAP.seal_capsule(self.anchor, self.anchor, self.after)
        item = json.loads(raw)
        item["source"]["old_ledger_sha256"] = "0" * 64
        forged = canonical(item)
        with self.assertRaisesRegex(ValueError, "SOURCE_RECOMPUTE_MISMATCH"):
            CAP.restore_capsule(
                forged, digest(forged), self.anchor, self.anchor, self.after)
        bad_source = self.after.clone()
        bad_source._heads[0].predictor_bias[0] += 0.4
        with self.assertRaisesRegex(ValueError, "SOURCE_RECOMPUTE_MISMATCH"):
            CAP.restore_capsule(
                raw, pin, self.anchor, self.anchor, bad_source)

    def test_truncated_noncanonical_or_wrong_proposal_fail_closed(self):
        raw, pin = CAP.seal_capsule(self.anchor, self.anchor, self.after)
        with self.assertRaisesRegex(ValueError, "CAPSULE_PIN"):
            CAP.restore_capsule(
                raw[:-1], pin, self.anchor, self.anchor, self.after)
        data = json.loads(raw)
        reordered = json.dumps(data, indent=1).encode("ascii")
        with self.assertRaisesRegex(ValueError, "CAPSULE_SCHEMA"):
            CAP.restore_capsule(
                reordered, digest(reordered), self.anchor, self.anchor, self.after)
        wrong = self.after.clone(self.anchor.native._ledger)
        with self.assertRaisesRegex(ValueError, "EXACTLY_ONE"):
            CAP.restore_capsule(raw, pin, self.anchor, self.anchor, wrong)

    def test_process_exit_and_fresh_process_source_reconstruction(self):
        raw, pin = CAP.seal_capsule(self.anchor, self.anchor, self.after)
        expected_heads, receipt = CAP.restore_capsule(
            raw, pin, self.anchor, self.anchor, self.after)
        expected = digest(canonical([CAP._saved(h) for h in expected_heads]))
        with tempfile.TemporaryDirectory() as temp:
            location = Path(temp) / "source-bound-capsule.json"
            location.write_bytes(raw)
            # The child re-imports source-free *real* JEPA head implementations
            # and reconstructs original/proposed fixtures without sharing any
            # Python object with its parent. This is NOT owner cold restore.
            script = """
from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path
import sys
from yggdrasil.native_context_basis import canonical, digest
here = Path(sys.argv[2])
spec = spec_from_file_location('child_fixture', here)
module = module_from_spec(spec)
spec.loader.exec_module(module)
anchor = module.BASE._Core(module.BASE._history())
proposed = anchor.clone(module.BASE._history() + (
    ('consumed-24', ((0, 0), (0, 1)), 0, 0, 0, 0),))
raw = Path(sys.argv[1]).read_bytes()
heads, receipt = module.CAP.restore_capsule(
    raw, digest(raw), anchor, anchor, proposed)
assert receipt['canonical_native_model_restored'] is False
print(digest(canonical([module.CAP._saved(h) for h in heads])))
"""
            process = subprocess.run(
                [sys.executable, "-c", script, str(location), __file__],
                cwd=str(Path(__file__).resolve().parents[1]),
                text=True, capture_output=True, check=True, timeout=50)
            self.assertEqual(process.stdout.strip(), expected)
            self.assertFalse(receipt["scientific_pass"])


if __name__ == "__main__":
    unittest.main()
