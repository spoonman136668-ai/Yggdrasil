"""NKR-06: independent offline-install, strong source pins and read-only facts."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

import yggdrasil.native_knowledge_activation as module
from yggdrasil.native_factual_weights import PACK, SCHEMA as SOURCE_SCHEMA, canonical, digest
from yggdrasil.public_causal_cells import PublicCausalCells

TRIPLES = sorted((
    (1, 2, 3), (1, 2, 4), (3, 7, 9), (4, 7, 10),
    (3, 8, 19), (2, 8, 6), (2, 9, 8), (5, 5, 12),
    (1, 3, 7), (9, 3, 17), (10, 3, 18), (11, 5, 21),
    (11, 6, 13), (12, 2, 4), (13, 7, 8), (17, 4, 16),
    (18, 2, 22), (20, 2, 23), (21, 5, 17), (23, 6, 13),
    (23, 7, 16), (24, 6, 19), (25, 8, 29), (26, 7, 30),
))
TRAIN_SHA = "a" * 64
ARCHIVE_SHA = "b" * 64


def create_pinned_fixture(directory):
    where = Path(directory)
    where.mkdir(parents=True, exist_ok=True)
    packed = b"".join(PACK.pack(*x) for x in TRIPLES)
    (where / "facts.uint32le").write_bytes(packed)
    manifest = {
        "schema": SOURCE_SCHEMA,
        "data_kind": "historical-train-only-QPQ",
        "source_archive_sha256": ARCHIVE_SHA,
        "source_train_sha256": TRAIN_SHA,
        "records": len(TRIPLES),
        "numeric_bytes": len(packed),
        "distinct_relation_types": len({x[1] for x in TRIPLES}),
        "packed_sha256": hashlib.sha256(packed).hexdigest(),
        "accepted_native": False,
        "scientific_pass": False,
        "original_valid_test_read": False,
        "historical_queries_previously_consumed": True,
        "first_triple": list(TRIPLES[0]),
        "last_triple": list(TRIPLES[-1]),
    }
    raw = canonical(manifest)
    (where / "manifest.json").write_bytes(raw)
    return {
        "PINNED_MANIFEST_SHA": digest(raw),
        "PINNED_PACKED_SHA": digest(packed),
        "PINNED_TRAIN_SHA": TRAIN_SHA,
        "PINNED_ARCHIVE_SHA": ARCHIVE_SHA,
        "PINNED_ROWS": len(TRIPLES),
        "PINNED_RELATIONS": manifest["distinct_relation_types"],
        "PINNED_BYTES": len(packed),
    }


class NativeActivationTests(unittest.TestCase):
    def test_production_contract_pinned_to_real_previous_historical_image(self):
        self.assertEqual(module.PINNED_ARTIFACT_ID, 14220169461)
        self.assertEqual(module.PINNED_SOURCE_RUN, 43856374741)
        self.assertEqual(module.PINNED_ROWS, 21343681)
        self.assertEqual(module.PINNED_RELATIONS, 828)
        self.assertEqual(module.PINNED_BYTES, 256124172)
        self.assertEqual(module.PINNED_MANIFEST_SHA,
                         "aa2d56e72284a042aee72587028642110327307b483de667586f105f018ebe8f")

    def test_install_and_source_grounded_native_session_without_owner_mutation(self):
        with tempfile.TemporaryDirectory() as tmp:
            source = Path(tmp) / "staged"
            target_parent = Path(tmp) / "installed"
            target_parent.mkdir()
            contract = create_pinned_fixture(source)
            before = PublicCausalCells().snapshot()
            with patch.multiple(module, **contract):
                receipt = module.install_offline_image(source, target_parent, "typed-facts")
                self.assertFalse(receipt["accepted_native"])
                self.assertEqual(receipt["installed_source_rows"], len(TRIPLES))
                dest = target_parent / "typed-facts"
                self.assertTrue((dest / "activation.json").is_file())
                self.assertEqual((dest / "facts.uint32le").read_bytes(),
                                 (source / "facts.uint32le").read_bytes())
                with module.open_installed_session(dest) as session:
                    row = session.fact(1, 2, 3)
                    self.assertEqual(row["classification"], "HISTORICAL_TRAIN_FACT")
                    self.assertTrue(row["witnessed"])
                    self.assertFalse(row["native_accepted"])
                    self.assertFalse(row["can_write_causal_consequence"])
                    self.assertEqual(session.fact(1, 2, 9000)["classification"],
                                     "UNKNOWN_ABSTAIN")
                    self.assertEqual(session.objects(1, 2)["objects"], [3, 4])
                    candidates = session.hypothesize(1, 2, 7)
                    self.assertEqual(candidates["objects"], [9, 10])
                    self.assertEqual(candidates["classification"],
                                     "UNVERIFIED_PATH_HYPOTHESES")
                    self.assertFalse(candidates["verified_new_knowledge"])
                    self.assertFalse(candidates["can_write_causal_consequence"])
            self.assertEqual(PublicCausalCells().snapshot(), before)

    def test_fail_closed_existing_target_and_unusable_partial_install(self):
        with tempfile.TemporaryDirectory() as tmp:
            src = Path(tmp) / "source"
            parent = Path(tmp) / "dest"
            parent.mkdir()
            contract = create_pinned_fixture(src)
            with patch.multiple(module, **contract):
                module.install_offline_image(src, parent, "target")
                with self.assertRaises(FileExistsError):
                    module.install_offline_image(src, parent, "target")
                with self.assertRaises(ValueError):
                    module.install_offline_image(src, parent, "../escape")
                (parent / "partial").mkdir()
                with self.assertRaisesRegex(ValueError, "NKR06_NO_ACTIVATION_RECEIPT"):
                    module.open_installed_session(parent / "partial")
                done = parent / "target"
                doc = json.loads((done / "activation.json").read_bytes())
                doc["native_accepted"] = True
                (done / "activation.json").write_bytes(canonical(doc))
                with self.assertRaisesRegex(ValueError, "NKR06_ACTIVATION_PIN_MISMATCH"):
                    module.open_installed_session(done)

    def test_mismatched_source_bytes_and_hashes_refuse_local_install(self):
        with tempfile.TemporaryDirectory() as tmp:
            src = Path(tmp) / "source"
            parent = Path(tmp) / "destination"
            parent.mkdir()
            contract = create_pinned_fixture(src)
            with patch.multiple(module, **contract):
                with patch.object(module, "PINNED_MANIFEST_SHA", "0" * 64):
                    with self.assertRaisesRegex(ValueError, "NKR05_MANIFEST_PIN_MISMATCH"):
                        module.install_offline_image(src, parent, "bad-pin")
                self.assertFalse((parent / "bad-pin").exists())
                img = src / "facts.uint32le"
                old = img.read_bytes()
                img.write_bytes(old[:-1] + bytes((old[-1] ^ 1,)))
                with self.assertRaisesRegex(ValueError, "NKR05_IMAGE_HASH_DRIFT"):
                    module.install_offline_image(src, parent, "bad-bytes")
                self.assertFalse((parent / "bad-bytes").exists())
                img.write_bytes(old)
                with patch.object(module, "PINNED_ROWS", len(TRIPLES) + 1):
                    with self.assertRaisesRegex(ValueError, "NKR06_SOURCE_CONTRACT_DRIFT"):
                        module.install_offline_image(src, parent, "bad-count")

    def test_atomic_rollback_on_failed_local_copy(self):
        with tempfile.TemporaryDirectory() as tmp:
            src = Path(tmp) / "source"
            parent = Path(tmp) / "dest"
            parent.mkdir()
            contract = create_pinned_fixture(src)
            with patch.multiple(module, **contract):
                with patch.object(module.shutil, "copyfileobj", side_effect=OSError("injected")):
                    with self.assertRaisesRegex(OSError, "injected"):
                        module.install_offline_image(src, parent, "failure")
                self.assertFalse((parent / "failure").exists())
                # Read-only trusted source survived unsuccessful staging.
                with module._open_image(src) as original:
                    self.assertEqual(len(original), len(TRIPLES))

    def test_source_symlink_refused_and_parent_type_checked(self):
        with tempfile.TemporaryDirectory() as tmp:
            src = Path(tmp) / "source"
            parent = Path(tmp) / "dest"
            parent.mkdir()
            contract = create_pinned_fixture(src)
            with patch.multiple(module, **contract):
                raw = src / "manifest.json"
                data = raw.read_bytes()
                raw.unlink()
                try:
                    raw.symlink_to(src / "actual-manifest.json")
                except OSError:
                    # Nonprivileged Windows hosts may lack symlink permission.
                    raw.write_bytes(data)
                else:
                    (src / "actual-manifest.json").write_bytes(data)
                    with self.assertRaisesRegex(ValueError, "NKR06_SOURCE_MISSING_OR_SYMLINK"):
                        module.install_offline_image(src, parent, "bad-symlink")
                with self.assertRaisesRegex(ValueError, "NKR06_PARENT_NOT_OWNED_DIRECTORY"):
                    module.install_offline_image(src, parent / "missing", "bad-parent")


if __name__ == "__main__":
    unittest.main()
