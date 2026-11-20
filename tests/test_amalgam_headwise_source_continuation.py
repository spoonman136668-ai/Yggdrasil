"""G28 envelope negatives: only source-authenticated archived CI can train/recover."""
from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path
import json
import sys
import unittest

from yggdrasil.native_context_basis import canonical, digest

ROOT = Path(__file__).resolve().parents[1]
HERE = ROOT / "research/contrib/chatgpt/CAUSAL-AMALGAM"
sys.path.insert(0, str(HERE))
SPEC = spec_from_file_location("g28_continuation", HERE / "headwise_source_continuation.py")
G28 = module_from_spec(SPEC)
SPEC.loader.exec_module(G28)
FIXSPEC = spec_from_file_location(
    "g28_preexisting_g26_fixture", Path(__file__).with_name(
        "test_amalgam_headwise_capsule.py"))
FIX = module_from_spec(FIXSPEC)
FIXSPEC.loader.exec_module(FIX)


def parents():
    return dict(native_parent=b"not real", native_pin="0" * 64,
                donor_parent=b"not real", donor_pin="0" * 64)


def fixture():
    anchor, proposed = FIX.cases()
    capsule, pin = FIX.CAP.seal_capsule(anchor, anchor, proposed)
    return anchor, proposed, capsule, pin


class SourceBoundContinuationTests(unittest.TestCase):
    def test_source_free_fixture_cannot_impersonate_native(self):
        anchor, proposed, capsule, pin = fixture()
        with self.assertRaisesRegex(ValueError, "G28_NATIVE_SOURCE_REQUIRED"):
            G28.seal_consumed_continuation(
                capsule, pin, anchor, anchor, proposed, b"", 1, **parents())

    def test_frozen_samples_and_trace_hash(self):
        for position in (0, 2, 31, 34, 65, 96, -1, True):
            with self.subTest(position=position):
                with self.assertRaisesRegex(ValueError, "G28_FROZEN_ORDINAL"):
                    G28._next_event([{} for _ in range(96)], position)
        with self.assertRaisesRegex(ValueError, "G28_FROZEN_TRACE_PIN"):
            G28._read_trace(b"[]")

    def test_wrong_checksum_rejected_before_any_source_inputs(self):
        anchor, proposed, capsule, pin = fixture()
        with self.assertRaisesRegex(ValueError, "G28_ENVELOPE_PIN"):
            G28.recover_consumed_continuation(
                b"{}", "0" * 64, capsule, pin, anchor, anchor, proposed,
                b"", 1, **parents())

    def test_rehashed_forged_fields_rejected_before_any_source_inputs(self):
        good = {
            "schema": G28.SCHEMA, "sample_ordinal": 1, "next_ordinal": 2,
            "trace_sha256": G28.ORIGINAL_TRACE_SHA256,
            "anchor_sha256": "0" * 64, "current_sha256": "0" * 64,
            "proposal_sha256": "0" * 64, "capsule_sha256": "0" * 64,
            "next_packet_sha256": "0" * 64, "native_after_sha256": "0" * 64,
            "heads_after_sha256": "0" * 64, "core_after_sha256": "0" * 64,
            "core_after_ascii": "[]", "owner_authorized": False,
            "official_native_checkpoint": False, "scientific_pass": False,
        }
        anchor, proposed, capsule, pin = fixture()
        for field, value in (("official_native_checkpoint", True),
                             ("owner_authorized", True),
                             ("scientific_pass", True),
                             ("next_ordinal", 3), ("trace_sha256", "0" * 64),
                             ("sample_ordinal", 32)):
            with self.subTest(field=field):
                forged = dict(good, **{field: value})
                raw = canonical(forged)
                with self.assertRaisesRegex(ValueError, "G28_ENVELOPE_SCHEMA"):
                    G28.recover_consumed_continuation(
                        raw, digest(raw), capsule, pin, anchor, anchor,
                        proposed, b"", 1, **parents())

    def test_noncanonical_encoding_or_extra_key_rejected(self):
        anchor, proposed, capsule, pin = fixture()
        # Rehashed but wrong schema shape; never attempts source reconstruction.
        for doc in ({"schema": G28.SCHEMA}, {"schema": G28.SCHEMA,
                                             "unexpected": "extra"}):
            raw = canonical(doc)
            with self.assertRaisesRegex(ValueError, "G28_ENVELOPE_SCHEMA"):
                G28.recover_consumed_continuation(
                    raw, digest(raw), capsule, pin, anchor, anchor,
                    proposed, b"", 1, **parents())


if __name__ == "__main__":
    unittest.main()
