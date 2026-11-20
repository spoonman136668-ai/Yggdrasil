"""Source-free DWSA-27 checks: synthetic checkpoint arrays only, no source actor."""
import importlib.util
import io
import json
from pathlib import Path
import struct
import subprocess
import sys
import tempfile
import unittest
import warnings
import zipfile

HERE = Path(__file__).resolve().parents[1] / "research/contrib/chatgpt/DWSA-27"
SPEC = importlib.util.spec_from_file_location("dwsa27_identity", HERE / "predictor_identity.py")
identity = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(identity)


def npy(shape, values, dtype="<f4", order=False):
    header = repr({"descr": dtype, "fortran_order": order, "shape": shape})
    # NPY v1 10-byte prefix; entire header ends at 16-byte boundary.
    padding = (-10 - len(header) - 1) % 16
    head = (header + " " * padding + "\n").encode("ascii")
    return b"\x93NUMPY\x01\x00" + struct.pack("<H", len(head)) + head + struct.pack("<%df" % len(values), *values)


def fake_archive(path, *, changed=0.0, extra=0, invalid=None, compressed=False, duplicate=False):
    method = zipfile.ZIP_DEFLATED if compressed else zipfile.ZIP_STORED
    with zipfile.ZipFile(path, "w", compression=method) as z:
        for name, shape in identity.FIELDS:
            n = 1
            for v in shape:
                n *= v
            values = [float((i % 11) - 5) / 8 for i in range(n)]
            if name == "pred.1.W.npy":
                values[0] += changed
            if invalid == "nonfinite" and name == "pred.0.W.npy":
                values[0] = float("nan")
            dtype = ">f4" if invalid == "dtype" and name == "pred.0.W.npy" else "<f4"
            order = invalid == "fortran" and name == "pred.0.W.npy"
            body = npy(shape, values, dtype, order)
            z.writestr(name, body)
            if duplicate and name == "pred.0.W.npy":
                with warnings.catch_warnings():
                    warnings.simplefilter("ignore", UserWarning)
                    z.writestr(name, body)
        z.writestr("enc.extra.npy", bytes([extra]))


class PredictorIdentityTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.a = Path(self.tmp.name) / "a.npz"
        self.b = Path(self.tmp.name) / "b.npz"

    def test_source_blob_different_predictor_identical(self):
        fake_archive(self.a, extra=1)
        fake_archive(self.b, extra=2)
        a = identity.inspect(self.a)
        b = identity.inspect(self.b)
        self.assertNotEqual(a["git_blob_sha1"], b["git_blob_sha1"])
        self.assertEqual(a["predictor_sha256"], b["predictor_sha256"])
        report = identity.compare([self.a, self.b])
        self.assertEqual(report["status"], "DUPLICATE_PREDICTOR_FOUND")
        self.assertEqual(report["unique_predictor_count"], 1)
        self.assertEqual(report["duplicates"], [[str(self.a), str(self.b)]])
        self.assertEqual(report["donor_forward_calls"], 0)
        self.assertEqual(report["research_result"], "NOT_EVALUATED")

    def test_predictor_change_detected(self):
        fake_archive(self.a)
        fake_archive(self.b, changed=0.125)
        report = identity.compare([self.a, self.b])
        self.assertEqual(report["status"], "DISTINCT_PREDICTORS")
        self.assertEqual(report["unique_predictor_count"], 2)
        self.assertFalse(report["duplicates"])

    def test_git_source_pin_refusal(self):
        fake_archive(self.a)
        self.assertEqual(identity.inspect(self.a, expected_blob_sha1=identity.inspect(self.a)["git_blob_sha1"])["path"], str(self.a))
        with self.assertRaisesRegex(identity.SourceRejected, "SOURCE_GIT_SHA1"):
            identity.inspect(self.a, expected_blob_sha1="0" * 40)

    def test_reject_bad_shapes_dtypes_nonfinite_or_fortran(self):
        for bad in ("dtype", "nonfinite", "fortran"):
            with self.subTest(bad=bad):
                fake_archive(self.a, invalid=bad)
                with self.assertRaises(identity.SourceRejected):
                    identity.inspect(self.a)

    def test_reject_compressed_and_duplicate_members(self):
        fake_archive(self.a, compressed=True)
        with self.assertRaisesRegex(identity.SourceRejected, "UNSAFE_MEMBER"):
            identity.inspect(self.a)
        fake_archive(self.a, duplicate=True)
        with self.assertRaisesRegex(identity.SourceRejected, "DUPLICATE_MEMBER"):
            identity.inspect(self.a)

    def test_reject_tamper_and_roster(self):
        fake_archive(self.a)
        with self.assertRaisesRegex(identity.SourceRejected, "SOURCE_ROSTER"):
            identity.compare([self.a, self.a])
        with open(self.a, "r+b") as f:
            f.seek(0)
            f.write(b"XXXX")
        with self.assertRaises(identity.SourceRejected):
            identity.inspect(self.a)

    def test_cli_duplicate_refused_and_distinct_accepted(self):
        fake_archive(self.a, extra=1)
        fake_archive(self.b, extra=2)
        argv = [sys.executable, str(HERE / "predictor_identity.py"), "--require-distinct", str(self.a), str(self.b)]
        denied = subprocess.run(argv, capture_output=True, text=True, check=False)
        self.assertEqual(denied.returncode, 2, denied.stderr)
        self.assertEqual(json.loads(denied.stdout)["status"], "DUPLICATE_PREDICTOR_FOUND")
        fake_archive(self.b, changed=0.25)
        passed = subprocess.run(argv, capture_output=True, text=True, check=False)
        self.assertEqual(passed.returncode, 0, passed.stderr)
        self.assertEqual(json.loads(passed.stdout)["status"], "DISTINCT_PREDICTORS")


if __name__ == "__main__":
    unittest.main()
