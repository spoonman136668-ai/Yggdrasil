"""NC2 frozen diagnostic and engineering negatives. No native first use."""
import json
import sys
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parents[1] / (
    "research/contrib/chatgpt/self-assembling-topologies/gate28")
sys.path.insert(0, str(HERE))
import dense_reference as dense
import recovery_calibration as nc2


class TestGate28RecoveryCalibration(unittest.TestCase):
    def test_filter_and_checkpoint_negatives(self):
        self.assertEqual(nc2.advance(0.5, 0.5, 1), 0.5)
        self.assertGreater(nc2.advance(0.5, 0.9, 1), 0.5)
        self.assertLess(nc2.advance(0.5, 0.9, 0), 0.5)
        low = nc2.HAZARD
        for _ in range(32):
            low = nc2.advance(low, 0.9, 1)
        self.assertGreater(low, 0.9)
        raw = nc2.pack(dense.new("dense_causal_reward"), 0.5, None)
        self.assertEqual(nc2.pack(*nc2.unpack(raw)), raw)
        item = json.loads(raw)
        item["payload"]["weight"] = 0.99
        with self.assertRaises(ValueError):
            nc2.unpack(json.dumps(item).encode("ascii"))
        with self.assertRaisesRegex(ValueError, "NC2_FROZEN_SEED"):
            nc2.evaluate(501000, "diagnostic_shifted")
        with self.assertRaisesRegex(ValueError, "NC2_TRIAL_COVERAGE"):
            nc2.score([])

    def test_frozen_twelve_world_diagnostic(self):
        prereg = json.loads((HERE / "recovery_calibration_prereg.json").read_text())
        self.assertEqual({k: tuple(v) for k, v in prereg["seeds"].items()},
                         nc2.SEEDS)
        self.assertEqual(prereg["thresholds"]["noise_R_brier_max"], 0.270)
        self.assertEqual(prereg["thresholds"]["stationary_R_degradation_max"],
                         0.015)
        records = [nc2.evaluate(seed, cohort)
                   for cohort, seeds in nc2.SEEDS.items() for seed in seeds]
        report = nc2.score(records)
        self.assertEqual(report["worlds"], 12)
        self.assertFalse(report["primary_scored"])
        self.assertFalse(report["scientific_gain_verified"])
        self.assertIn(report["status"], ("NC2_DIAGNOSTIC_TARGETS_MET_NOT_SCIENCE",
                                         "NC2_DIAGNOSTIC_NO_GO"))
        print("G28_NC2_FROZEN_DIAGNOSTIC", json.dumps(report, sort_keys=True))
