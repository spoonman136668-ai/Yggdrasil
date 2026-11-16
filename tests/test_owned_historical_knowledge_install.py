"""NKR-07: source-safe authenticated-artifact owner-local installer tests."""
from __future__ import annotations

from datetime import datetime, timezone
import json
from pathlib import Path
import shutil
import tempfile
import unittest
from unittest.mock import patch

import scripts.install_owned_historical_knowledge as installer
import yggdrasil.native_knowledge_activation as activation
from test_native_knowledge_activation import create_pinned_fixture, TRIPLES
from yggdrasil.public_causal_cells import PublicCausalCells

BEFORE_EXPIRY = datetime(2026, 11, 16, 12, 0, tzinfo=timezone.utc)


def original_metadata():
    return {
        "id": 14220169461,
        "name": "NKR05-21M-full-historical-TRAIN-native-factual-weights",
        "expired": False,
        "digest": "sha256:c7265cabac91b8762fb5d65209eef44fa79a8fbf3d9a6f61300ef60ded0a5275",
        "size_in_bytes": 256126168,
        "expires_at": "2026-12-16T11:20:20Z",
        "workflow_run": {
            "id": 43856374741,
            "head_sha": "c4b4e97726f6541197913ad405a47d4c4019a3cf",
        }
    }


class FakeGh:
    """No real subprocess, network, credential or owner write in fixture tests."""
    def __init__(self, source):
        self.source = Path(source)
        self.calls = []
        self.metadata = original_metadata()

    def __call__(self, args, *, timeout):
        self.calls.append((list(args), timeout))
        if args[0] == "api":
            self.assert_metadata_route(args)
            return json.dumps(self.metadata)
        if args[:2] != ["run", "download"]:
            raise AssertionError("NKR07_UNEXPECTED_GH_ACTION")
        if (args[2] != str(installer.PINNED_SOURCE_RUN)
                or args[3:7] != ["-R", installer.REPO, "-n",
                                 installer.ARTIFACT_NAME]
                or args[7] != "-D"):
            raise AssertionError("NKR07_WRONG_GH_DOWNLOAD_ROUTE")
        dest = Path(args[8])
        for file in self.source.iterdir():
            shutil.copyfile(file, dest / file.name)
        return ""

    @staticmethod
    def assert_metadata_route(args):
        if args != ["api", "repos/spoonman136668-ai/Yggdrasil/actions/artifacts/14220169461"]:
            raise AssertionError("NKR07_WRONG_GH_META_ROUTE")


class OwnerInstallerTests(unittest.TestCase):
    def test_frozen_source_identity_and_expiry_contract(self):
        self.assertTrue(installer.verify_source_metadata(original_metadata(),
                                                           now=BEFORE_EXPIRY))
        self.assertEqual(installer.PINNED_ARTIFACT_ID, 14220169461)
        self.assertEqual(installer.PINNED_ROWS, 21343681)
        self.assertEqual(installer.PINNED_PACKED_SHA,
                         "6dd87ba5bbf5fd7ecaffa6d48f674e34ce2a7cc7fa748ec7698d2c0a4cdae3d1")
        self.assertEqual(installer.PINNED_MANIFEST_SHA,
                         "aa2d56e72284a042aee72587028642110327307b483de667586f105f018ebe8f")

    def test_strict_artifact_identity_and_expired_refusal(self):
        baseline = original_metadata()
        for key, wrong in (
            ("id", 0), ("name", "other"), ("expired", True),
            ("digest", "sha256:" + "0" * 64), ("size_in_bytes", 1),
        ):
            changed = dict(baseline)
            changed[key] = wrong
            with self.subTest(key=key), self.assertRaises(ValueError):
                installer.verify_source_metadata(changed, now=BEFORE_EXPIRY)
        for key, wrong in (("id", 0), ("head_sha", "0"*40)):
            changed = dict(baseline)
            changed["workflow_run"] = dict(baseline["workflow_run"])
            changed["workflow_run"][key] = wrong
            with self.subTest(key=key), self.assertRaises(ValueError):
                installer.verify_source_metadata(changed, now=BEFORE_EXPIRY)
        with self.assertRaisesRegex(ValueError, "NKR07_ORIGINAL_ARTIFACT_EXPIRED"):
            installer.verify_source_metadata(
                baseline, now=datetime(2026,12,16,12,0,tzinfo=timezone.utc))

    def test_owner_selected_destination_installs_full_pinned_fixture_without_native_mutation(self):
        with tempfile.TemporaryDirectory() as tmp:
            source = Path(tmp) / "source"
            parent = Path(tmp) / "owner"
            parent.mkdir()
            contract = create_pinned_fixture(source)
            (source / "receipt.json").write_text("{}", encoding="ascii")
            fake = FakeGh(source)
            before = PublicCausalCells().snapshot()
            with patch.multiple(activation, **contract), patch.object(
                    installer, "PINNED_ROWS", len(TRIPLES)):
                result = installer.stage_owner_knowledge(
                    parent, "native-facts", now=BEFORE_EXPIRY, gh_runner=fake)
                self.assertEqual(result["classification"], "OWNER_LOCAL_RESEARCH_IMAGE_READY")
                self.assertEqual(result["installed_source_rows"], len(TRIPLES))
                self.assertFalse(result["accepted_native"])
                self.assertFalse(result["native_owner_activated"])
                self.assertEqual(len(fake.calls), 2)
                target = parent / "native-facts"
                self.assertTrue((target / "activation.json").is_file())
                with activation.open_installed_session(target) as session:
                    self.assertTrue(session.fact(*TRIPLES[0])["witnessed"])
                    self.assertEqual(session.fact(4_294_967_295,
                                                 4_294_967_295,
                                                 4_294_967_295)["classification"],
                                     "UNKNOWN_ABSTAIN")
            self.assertEqual(PublicCausalCells().snapshot(), before)

    def test_missing_parent_unsafe_name_and_existing_target_prevent_gh_access(self):
        with tempfile.TemporaryDirectory() as tmp:
            parent = Path(tmp)
            src = parent / "source"
            src.mkdir()
            fake = FakeGh(src)
            with self.assertRaisesRegex(ValueError, "NKR07_OWNER_PARENT_MISSING"):
                installer.stage_owner_knowledge(parent / "missing",
                                                gh_runner=fake, now=BEFORE_EXPIRY)
            with self.assertRaisesRegex(ValueError, "NKR07_INSTALL_NAME_INVALID"):
                installer.stage_owner_knowledge(parent, "../escape",
                                                gh_runner=fake, now=BEFORE_EXPIRY)
            (parent / "existing").mkdir()
            with self.assertRaises(FileExistsError):
                installer.stage_owner_knowledge(parent, "existing",
                                                gh_runner=fake, now=BEFORE_EXPIRY)
            self.assertEqual(fake.calls, [])

    def test_metadata_failure_happens_before_download_or_owner_install(self):
        with tempfile.TemporaryDirectory() as tmp:
            parent = Path(tmp) / "owner"
            parent.mkdir()
            fake = FakeGh(parent)
            fake.metadata["workflow_run"]["head_sha"] = "0"*40
            with self.assertRaisesRegex(ValueError, "NKR07_ORIGINAL_ARTIFACT_IDENTITY_DRIFT"):
                installer.stage_owner_knowledge(
                    parent, "native-facts", now=BEFORE_EXPIRY, gh_runner=fake)
            self.assertEqual(len(fake.calls), 1)
            self.assertFalse((parent / "native-facts").exists())

    def test_unrecognized_download_and_bad_payload_prevent_owner_install(self):
        with tempfile.TemporaryDirectory() as tmp:
            parent = Path(tmp) / "owner"
            source = Path(tmp) / "source"
            parent.mkdir()
            contract = create_pinned_fixture(source)
            fake = FakeGh(source)
            with patch.multiple(activation, **contract), patch.object(
                    installer, "PINNED_ROWS", len(TRIPLES)):
                with self.assertRaisesRegex(ValueError, "NKR07_ARTIFACT_MEMBER_MISMATCH"):
                    installer.stage_owner_knowledge(
                        parent, "native-facts", now=BEFORE_EXPIRY, gh_runner=fake)
                self.assertFalse((parent / "native-facts").exists())
                (source / "receipt.json").write_bytes(b"{}")
                old = (source / "facts.uint32le").read_bytes()
                (source / "facts.uint32le").write_bytes(
                    old[:-1] + bytes((old[-1] ^ 1,)))
                with self.assertRaisesRegex(ValueError, "NKR05_IMAGE_HASH_DRIFT"):
                    installer.stage_owner_knowledge(
                        parent, "native-facts", now=BEFORE_EXPIRY, gh_runner=fake)
                self.assertFalse((parent / "native-facts").exists())


if __name__ == "__main__":
    unittest.main()
