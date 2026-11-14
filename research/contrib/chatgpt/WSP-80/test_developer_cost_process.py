"""WSP80 isolated process-cost developer regression, never SELFTEST worlds."""
from pathlib import Path
import os
import sys
import unittest
from unittest import mock

sys.path.insert(0, str(Path(__file__).parent))
from developer_cost_process import (
    DEV, SOURCE_BLOB, PREREG_BLOB, FROZEN_ADAM_BLOB,
    canonical, digest, normalized_rows, peak_rss_bytes, verify_readonly_custody,
)


class IsolatedDeveloperCostTests(unittest.TestCase):
    def rows(self):
        zero = [0] * 6
        return [[zero.copy(), 0, zero.copy(), 1] for _ in range(384)]

    def test_same_paid_ledger_has_canonical_cross_platform_hash(self):
        rows = self.rows()
        self.assertEqual(digest(rows), digest(rows))
        self.assertEqual(len(normalized_rows(rows)), 384)
        self.assertEqual(canonical({"b": 2, "a": 1}), '{"a":1,"b":2}')

    def test_incomplete_unpaid_and_discontinuous_ledger_rejected(self):
        rows = self.rows()
        with self.assertRaises(ValueError):
            normalized_rows(rows[:-1])
        bad = self.rows()
        bad[40][-1] = 0
        with self.assertRaises(ValueError):
            normalized_rows(bad)
        bad = self.rows()
        bad[40][0][0] = 1
        with self.assertRaises(ValueError):
            normalized_rows(bad)

    def test_real_process_resident_highwater_available(self):
        self.assertGreater(peak_rss_bytes(), 1024 * 1024)

    def test_pinned_source_contract_rejects_drift(self):
        self.assertEqual(len(SOURCE_BLOB), 40)
        self.assertEqual(len(PREREG_BLOB), 40)
        self.assertEqual(len(FROZEN_ADAM_BLOB), 40)
        with mock.patch.dict(os.environ, {"GITHUB_SHA": "a" * 40}):
            with mock.patch("developer_cost_process.git", side_effect=[
                    "a" * 40, "0" * 40]):
                with self.assertRaisesRegex(RuntimeError, "frozen research identity"):
                    verify_readonly_custody()

    def test_public_cost_child_has_no_registered_source_admission(self):
        content = Path(__file__).with_name("developer_cost_process.py").read_text("utf8")
        self.assertEqual(DEV, 9001)
        self.assertIn("DEV = 9001", content)
        self.assertNotIn("build_world(", content)
        self.assertNotIn("source.SEEDS", content)
        self.assertNotIn("PRIMARY", content)


if __name__ == "__main__":
    unittest.main()
