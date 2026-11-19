"""Source-free contract tests for the immutable native-to-shadow checkpoint bridge."""
from hashlib import sha256
from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path
import sys
import unittest
from unittest.mock import patch

RESEARCH = Path(__file__).resolve().parents[1] / "research/contrib/chatgpt/CAUSAL-AMALGAM"
SPEC = spec_from_file_location("amalgam_relation_custody_for_tests",
                               RESEARCH / "relation_custody.py")
CUSTODY = module_from_spec(SPEC)
with patch.object(sys, "path", [str(RESEARCH), *sys.path]):
    SPEC.loader.exec_module(CUSTODY)

RAW = b"source-free-placeholder-not-a-real-native-checkpoint"
SHA = sha256(RAW).hexdigest()


def fixture_rows(projection=0, *, ambiguous=False):
    rows = []
    for context in (0, 1):
        for first in (0, 1):
            for trial in range(6):
                if projection == 0:
                    views = ((context, 0), (context, 1))
                else:
                    views = ((0, context), (1, context))
                identifier = sha256(f"custody/{projection}/{len(rows)}".encode()).hexdigest()
                # A public-transition fixture only; no original source actions.
                rows.append((identifier, views, first, first ^ context ^ (trial == 0),
                             0, 0))
    if ambiguous:
        rows.append((sha256(b"ambiguous").hexdigest(), ((0, 0), (1, 1)),
                     0, 1, 1, 0))
    return tuple(rows)


class FakeReader:
    def __init__(self, records, projection=0, *, count=None):
        self._ledger = records
        self._projection = projection
        self._count = len(records) if count is None else count

    def info(self):
        return {"projection": self._projection, "count": self._count}


class FakeNative:
    def __init__(self, records, projection=0, *, count=None):
        self.reader = FakeReader(records, projection, count=count)
        self.read_count = 0

    def checkpoint(self):
        self.read_count += 1
        return RAW

    def _episode_reader(self):
        return self.reader


class RelationNativeCustodyTests(unittest.TestCase):
    def audit(self, native):
        with patch.object(CUSTODY.NativeCumulativeLearner, "restore", return_value=native) as restore:
            result = CUSTODY.audit_native_checkpoint(RAW, SHA)
            restore.assert_called_once_with(RAW, SHA)
            return result

    def test_projection_zero_authentic_ledger_interface(self):
        records = fixture_rows()
        native = FakeNative(records)
        result = self.audit(native)
        self.assertEqual(result["verified_native_projection"], 0)
        self.assertEqual(result["retained_native_witnesses"], 24)
        self.assertEqual(result["aligned_public_witnesses"], 24)
        self.assertEqual(result["masked_proposals"], 4)
        self.assertEqual(result["historical_masked_held_count"], 24)
        self.assertIs(result["scientific_pass"], False)
        self.assertEqual(result["source_actions"], 0)
        self.assertEqual(result["checkpoint_updates"], 0)
        self.assertEqual(native.reader._ledger, records)
        self.assertGreater(native.read_count, 1)
        self.assertTrue(all(x["decision_eligible"] is False
                            for x in result["masked_readouts"]))

    def test_projection_one_uses_learned_coordinate(self):
        result = self.audit(FakeNative(fixture_rows(1), projection=1))
        self.assertEqual(result["verified_native_projection"], 1)
        self.assertEqual(result["skipped_ambiguous_views"], 0)
        self.assertEqual(result["masked_proposals"], 4)
        self.assertEqual(result["historical_masked_held_count"], 24)

    def test_misaligned_public_views_are_excluded_not_imputed(self):
        for projection in (0, 1):
            with self.subTest(projection=projection):
                result = self.audit(FakeNative(
                    fixture_rows(projection, ambiguous=True), projection))
                self.assertEqual(result["skipped_ambiguous_views"], 1)
                self.assertEqual(result["retained_native_witnesses"], 25)
                self.assertEqual(result["aligned_public_witnesses"], 24)

    def test_wrong_pin_rejects_before_native_restore(self):
        with patch.object(CUSTODY.NativeCumulativeLearner, "restore") as restore:
            with self.assertRaisesRegex(ValueError, "RELATION_NATIVE_CHECKPOINT_PIN"):
                CUSTODY.audit_native_checkpoint(RAW, "0" * 64)
            restore.assert_not_called()

    def test_empty_or_unknown_projection_fails_closed(self):
        for projection in (None, 2):
            with self.subTest(projection=projection):
                with patch.object(CUSTODY.NativeCumulativeLearner, "restore",
                                  return_value=FakeNative(fixture_rows(), projection)):
                    with self.assertRaisesRegex(ValueError, "RELATION_NATIVE_PROJECTION"):
                        CUSTODY.audit_native_checkpoint(RAW, SHA)

    def test_empty_and_inconsistent_native_ledgers_reject(self):
        for records, wrong_count in (((), 0), (fixture_rows(), 1)):
            with self.subTest(rows=len(records)):
                native = FakeNative(records, count=wrong_count)
                with patch.object(CUSTODY.NativeCumulativeLearner, "restore",
                                  return_value=native):
                    with self.assertRaisesRegex(ValueError, "RELATION_NATIVE_LEDGER_COUNT"):
                        CUSTODY.audit_native_checkpoint(RAW, SHA)

    def test_native_restore_forgery_rejected(self):
        with patch.object(CUSTODY.NativeCumulativeLearner, "restore",
                          side_effect=ValueError("INTEGRATED_CHECKPOINT_PIN")):
            with self.assertRaisesRegex(ValueError, "INTEGRATED_CHECKPOINT_PIN"):
                CUSTODY.audit_native_checkpoint(RAW, SHA)

    def test_changed_checkpoint_bytes_rejected_before_reading_ledger(self):
        native = FakeNative(fixture_rows())
        native.checkpoint = lambda: b"changed"
        with patch.object(CUSTODY.NativeCumulativeLearner, "restore",
                          return_value=native):
            with self.assertRaisesRegex(ValueError, "RELATION_NATIVE_COLD_BYTES"):
                CUSTODY.audit_native_checkpoint(RAW, SHA)


if __name__ == "__main__":
    unittest.main()
