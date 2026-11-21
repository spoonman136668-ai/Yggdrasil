"""Synthetic static-file custody/security regression, never original source execution."""
import importlib.util
from pathlib import Path
import hashlib
import pickle
import tempfile
import unittest
import zipfile
import warnings

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "research/contrib/chatgpt/DWSA-31/checkpoint_scan.py"
SPEC = importlib.util.spec_from_file_location("dwsa31_checkpoint_scan", SCRIPT)
scanmod = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(scanmod)


def make_zip(path, *, payload=b"\x80\x02cposix\nsystem\n.",
             mode=zipfile.ZIP_STORED, double=False, danger=False, missing=False):
    with zipfile.ZipFile(path, "w", compression=mode) as zf:
        if not missing:
            zf.writestr("model/data.pkl", payload)
        zf.writestr("model/data/0", b"\x01" * 32)
        if danger:
            zf.writestr("../outside", b"bad")
        if double:
            with warnings.catch_warnings():
                warnings.simplefilter("ignore", UserWarning)
                zf.writestr("model/data/0", b"\x01" * 32)
        zf.writestr("model/version", b"3")


class StaticScanTests(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        self.file = Path(temp.name) / "untrusted.pt"

    def audit_fixture(self):
        raw = self.file.read_bytes()
        return scanmod.scan(self.file, expected_sha256=hashlib.sha256(raw).hexdigest(),
                            expected_size=len(raw))

    def test_static_pickle_scans_global_without_exec(self):
        make_zip(self.file)
        old = pickle.loads
        try:
            def blocked(*args, **kwargs):
                raise AssertionError("pickle.loads MUST NOT BE CALLED")
            pickle.loads = blocked
            out = self.audit_fixture()
        finally:
            pickle.loads = old
        self.assertIn("posix.system", out["static_global_references"])
        self.assertFalse(out["deserialization_executed"])
        self.assertFalse(out["weights_extracted"])
        self.assertEqual(out["raw_storage_member_count"], 1)

    def test_original_hash_and_length_mandatory(self):
        make_zip(self.file)
        with self.assertRaisesRegex(scanmod.UnsafeOrUnverified, "SOURCE_BYTE_IDENTITY"):
            scanmod.scan(self.file)
        with self.assertRaisesRegex(scanmod.UnsafeOrUnverified, "SOURCE_BYTE_IDENTITY"):
            scanmod.scan(self.file, expected_sha256="0" * 64,
                         expected_size=self.file.stat().st_size)

    def test_reject_duplicate_zip_member(self):
        make_zip(self.file, double=True)
        with self.assertRaisesRegex(scanmod.UnsafeOrUnverified, "DUPLICATE"):
            self.audit_fixture()

    def test_reject_compressed_zip_member(self):
        make_zip(self.file, mode=zipfile.ZIP_DEFLATED)
        with self.assertRaisesRegex(scanmod.UnsafeOrUnverified, "UNSAFE_ZIP"):
            self.audit_fixture()

    def test_reject_traversal_zip_member(self):
        make_zip(self.file, danger=True)
        with self.assertRaisesRegex(scanmod.UnsafeOrUnverified, "UNSAFE_ZIP"):
            self.audit_fixture()

    def test_reject_pickle_trailing_bytes(self):
        make_zip(self.file, payload=b"\x80\x02N." + b"garbage")
        with self.assertRaisesRegex(scanmod.UnsafeOrUnverified, "TRAILING"):
            self.audit_fixture()

    def test_reject_no_data_pickle(self):
        make_zip(self.file, missing=True)
        with self.assertRaisesRegex(scanmod.UnsafeOrUnverified, "PICKLE_MEMBER"):
            self.audit_fixture()

    def test_reject_non_zip(self):
        self.file.write_bytes(b"this is not a checkpoint")
        with self.assertRaisesRegex(scanmod.UnsafeOrUnverified, "ARCHIVE"):
            self.audit_fixture()

    def test_reject_nonfinite_provided_pin_and_opaque_extension(self):
        make_zip(self.file)
        with self.assertRaisesRegex(scanmod.UnsafeOrUnverified, "INVALID_EXPECTED_HASH"):
            scanmod.scan(self.file, expected_sha256="bad")
        make_zip(self.file, payload=b"\x80\x02\x82\x01.")
        with self.assertRaisesRegex(scanmod.UnsafeOrUnverified, "OPAQUE_EXTENSION"):
            self.audit_fixture()


if __name__ == "__main__":
    unittest.main()
