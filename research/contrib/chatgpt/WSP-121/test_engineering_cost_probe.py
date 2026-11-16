"""Source-safe cost-probe behavioral tests, with no timing threshold assertions."""
from unittest import TestCase
from unittest.mock import patch

import engineering_cost_probe as P
import meta_operator as M
import source_custody as C


class WSP121CostProbeTests(TestCase):
    def test_same_source_receipts_predictions_and_cold_after_matched_work(self):
        with patch.object(M, "original_world",
                          side_effect=AssertionError("WSP121 primary opened")):
            with patch.object(C, "open_original",
                              side_effect=AssertionError("WSP121 original opened")):
                result = P.run_probe(1)
        self.assertEqual(result["status"], "DEVELOPMENT_INFORMATION_ONLY")
        self.assertFalse(result["scientific_pass"])
        self.assertFalse(result["first_use"])
        self.assertFalse(result["native_admission"])
        self.assertEqual(result["source_calls_per_arm"], 24)
        self.assertEqual(result["held_scored_per_arm"], 96)
        self.assertEqual(result["worlds"], [121900, 121901, 121902, 121903])
        self.assertTrue(result["receipts_stable"])
        self.assertEqual(len(result["matched_receipts_sha256"]), 64)
        for arm in P.ARMS:
            values = result["medians"][arm]
            self.assertGreater(values["whole_seconds"], 0)
            self.assertGreater(values["source_seconds"], 0)
            self.assertGreater(values["cold_restore_seconds"], 0)

    def test_denied_original_and_invalid_repeat_counts(self):
        for value in (0, 16, True, 1.5, "7"):
            with self.subTest(value=value), self.assertRaises(ValueError):
                P.run_probe(value)
        for seed in (121000, 121047, 121800, 120800):
            with self.assertRaises(PermissionError):
                C.EngineeringCustodian(seed)
