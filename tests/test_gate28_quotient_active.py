"""Cold, active and forced quotient development comparison; no primary seeds."""
import json
import sys
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parents[1] / (
    "research/contrib/chatgpt/self-assembling-topologies/gate28")
sys.path.insert(0, str(HERE))
import quotient_active as qac


class TestGate28QuotientActive(unittest.TestCase):
    def test_frozen_seed_and_arm_fences(self):
        prereg = json.loads((HERE / "quotient_active_prereg.json").read_text())
        self.assertEqual({k: tuple(v) for k, v in prereg["seeds"].items()},
                         qac.SEEDS)
        self.assertEqual(tuple(prereg["arms"]), qac.ARMS)
        for seed in (501000, 502001, 503000, 900211, 900331):
            with self.assertRaisesRegex(ValueError, "QAC_UNFROZEN_SEED"):
                qac.guard(seed, "diagnostic_shifted")
        with self.assertRaisesRegex(ValueError, "QAC_WORLD_COVERAGE"):
            qac.score([])

    def test_frozen_six_world_active_forced_cold(self):
        records = [qac.evaluate(seed, cohort)
                   for cohort, seeds in qac.SEEDS.items() for seed in seeds]
        for row in records:
            self.assertEqual(row["distinct_processes"], 3)
            self.assertFalse(row["primary_scored"])
            for phase in ("A", "B", "R"):
                rows = row["phases"][phase]
                self.assertEqual(len(rows), 2 * len(qac.ARMS))
                self.assertEqual(len({rows[a + ".forced"]["exposure_sha256"]
                                      for a in qac.ARMS}), 1)
                for item in rows.values():
                    self.assertLessEqual(item["peak_rule_work"], 8192)
                    self.assertLessEqual(item["checkpoint_bytes"], 16384)
        report = qac.score(records)
        self.assertIn(report["status"], ("QAC_DIAGNOSTIC_NO_GO",
                                         "QAC_DIAGNOSTIC_TARGETS_MET_NOT_SCIENCE"))
        self.assertFalse(report["primary_scored"])
        self.assertFalse(report["scientific_gain_verified"])
        # A source-verified negative is a successful engineering test.
        print("G28_QAC_FROZEN_DIAGNOSTIC", json.dumps(report, sort_keys=True))
