"""Offline negative controls for the QTR-01 bounded custody tool; no donor data consumed."""
import hashlib
import importlib.util
import json
from pathlib import Path
import unittest
from unittest import mock

p = Path(__file__).with_name("verify_donor.py")
spec = importlib.util.spec_from_file_location("qtr01_verify_donor", p)
module = importlib.util.module_from_spec(spec)
import sys
sys.modules[spec.name] = module
spec.loader.exec_module(module)


class DonorInputTests(unittest.TestCase):
    def test_pinned_revisions_and_fixed_allowlist(self):
        self.assertEqual(len(module.SOURCES), 3)
        for s in module.SOURCES:
            self.assertTrue(s.url.startswith("https://huggingface.co/"))
            self.assertIn("/resolve/", s.url)
            self.assertLessEqual(s.max_bytes, 1_000_000)
            self.assertNotIn("/main/", s.url)

    def test_hash_matching_and_mismatch(self):
        data = b"fixture-data"
        s = module.Source("fixture", "https://example.test/fixture", "fixture", 100,
                          hashlib.sha256(data).hexdigest(), "utility")
        self.assertEqual(module.check_sha(s, data), hashlib.sha256(data).hexdigest())
        with self.assertRaisesRegex(module.CheckError, "HASH_MISMATCH"):
            module.check_sha(s, b"tampered")
        with self.assertRaisesRegex(module.CheckError, "BYTE_BOUND"):
            module.check_sha(s, b"x" * 101)
        with self.assertRaisesRegex(module.CheckError, "BYTE_BOUND"):
            module.check_sha(s, b"")

    def test_bounded_http_stream(self):
        class Response:
            def __init__(self, content): self.data = content
            def __enter__(self): return self
            def __exit__(self, *args): return False
            def read(self, n):
                self.read_requested = n
                return self.data[:n]
        with mock.patch.object(module.urllib.request, "urlopen", return_value=Response(b"x" * 25)):
            with self.assertRaisesRegex(module.CheckError, "SOURCE_TOO_LARGE"):
                module.get_bounded("https://example.test/file", 10)

    def test_utility_valid_and_rejects_invalid(self):
        rec = module.check_utility(b'{"layer":1,"feature":2,"dCE":0.5,"dM":-2}\n')
        self.assertEqual(rec["jsonl_records"], 1)
        self.assertIn("SEMANTIC_SCHEMA_UNVERIFIED", rec["validation"])
        for payload in (b"", b"bad-json", b"[]", b"{}\n\n", b'{"dCE":NaN}', b'{"dM":"bad"}', b"\xff"):
            with self.subTest(payload=payload), self.assertRaises(module.CheckError):
                module.check_utility(payload)

    def test_parquet_non_parquet_fails_closed(self):
        for payload in (b"", b"PAR1xxx", b"abc---PAR1"):
            with self.subTest(payload=payload), self.assertRaisesRegex(module.CheckError, "MAGIC_INVALID"):
                module.check_parquet(payload, "layers")

    def test_unavailable_bytes_cannot_pass(self):
        with mock.patch.object(module, "read_local", side_effect=module.CheckError("MISSING_FILE")):
            with self.assertRaises(module.CheckError):
                module.read_local(Path("/does-not-exist"), module.SOURCES[0])


if __name__ == "__main__":
    unittest.main()
