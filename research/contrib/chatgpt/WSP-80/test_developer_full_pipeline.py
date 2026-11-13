"""WSP80 full developer pipeline only: no registered-world training in unit tests."""
import json
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).parent))
from developer_full_pipeline import (
    validate_arm, validate_paid_receipt, REFERENCE_LEDGER,
    REFERENCE_PREDICTION, DEVELOPER_SEED, PAID_ACTIONS, canonical,
)


class PipelineDevelopmentTests(unittest.TestCase):
    def test_only_two_matched_developer_arms_supported(self):
        self.assertEqual(validate_arm("programmed"), "programmed")
        self.assertEqual(validate_arm("adam"), "adam")
        for forbidden in ("primary", "registered", "5601", "SELFTEST", "random"):
            with self.assertRaises(PermissionError):
                validate_arm(forbidden)

    def receipt(self, arm):
        r = {
            "schema": "wsp80.full-dev-arm.v1",
            "arm": arm,
            "source_commit_sha": "a" * 40,
            "developer_seed": 9001,
            "registered_seed_consumed": False,
            "paid_actions": 384,
            "common_stageA_actions": 144,
            "ledger_digest": REFERENCE_LEDGER,
            "prediction_digest": REFERENCE_PREDICTION[arm],
            "public_queries": 384,
            "prediction_modes_per_query": 2,
            "script_process_cpu_ns": 12,
            "peak_process_rss_bytes": 123456,
        }
        if arm == "adam":
            r["adam_training_trials"] = [
                {"restart": i, "gradient_updates": 600}
                for i in range(3)]
            r["adam_trained_at_least_95pct"] = True
        return r

    def test_matched_positive_developer_receipts_and_canonical_hash(self):
        for arm in ("programmed", "adam"):
            self.assertTrue(validate_paid_receipt(self.receipt(arm), arm, "a" * 40))
        self.assertEqual(canonical({"b": 2, "a": 1}), '{"a":1,"b":2}')

    def test_protected_or_missing_receipts_fail_closed(self):
        for arm in ("programmed", "adam"):
            for key, bad in (("registered_seed_consumed", True),
                             ("developer_seed", 5601),
                             ("ledger_digest", "bad"),
                             ("prediction_digest", "bad"),
                             ("paid_actions", 383),
                             ("peak_process_rss_bytes", 0)):
                receipt = self.receipt(arm)
                receipt[key] = bad
                with self.assertRaises(ValueError):
                    validate_paid_receipt(receipt, arm, "a" * 40)
        bad = self.receipt("adam")
        bad["adam_trained_at_least_95pct"] = False
        with self.assertRaises(ValueError):
            validate_paid_receipt(bad, "adam", "a" * 40)

    def test_source_only_literal_developer_world_and_no_registered_generator(self):
        file = Path(__file__).with_name("developer_full_pipeline.py").read_text()
        self.assertEqual(DEVELOPER_SEED, 9001)
        self.assertEqual(PAID_ACTIONS, 384)
        self.assertNotIn("build_world(", file)
        self.assertNotIn("source.SEEDS", file)
        self.assertIn("audit_static_readonly()", file)
        self.assertIn("run_order = (\"programmed\", \"adam\", \"adam\", \"programmed\")", file)


if __name__ == "__main__":
    unittest.main()
