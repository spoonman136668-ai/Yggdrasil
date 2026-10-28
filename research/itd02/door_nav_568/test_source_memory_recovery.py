"""Source-memory contradiction detection with conventional custody."""
import unittest
from source_memory_recovery_audit import run,trial
from recovering_local_probe import RecoveringLocalProbe
from recovering_conventional_probe import RecoveringConventionalProbe
from unrestricted_operation_cells import INPUTS

class SourceRecoveryTests(unittest.TestCase):
    def test_all_targets_and_identical_public_budget(self):
        cases=run()["cases"]
        self.assertEqual(len(cases),16)
        self.assertEqual(sum(c["in_memory_diagnostic"] for c in cases),4)
        for case in cases:
            self.assertEqual(case["public_source_feedback_per_arm"],32)
            for stage in case["stages"]:
                self.assertEqual(stage["candidate_target_feedback"],2*stage["step"])
                self.assertEqual(stage["conventional_target_feedback"],2*stage["step"])
                self.assertEqual(stage["scores"]["local_recovery"],
                                 stage["scores"]["conventional_recovery"])
                self.assertEqual(stage["fallback"]["local_recovery"],
                                 stage["fallback"]["conventional_recovery"])
                self.assertEqual(stage["remaining_source"]["local_recovery"],
                                 stage["remaining_source"]["conventional_recovery"])
                for arm,score in stage["scores"].items():
                    self.assertEqual(sum(score[k] for k in ("correct","wrong","abstentions")),
                                     score["unseen"])
                    self.assertGreaterEqual(case["cpu_ns"][arm],0)

    def test_detected_contradiction_abstains_on_unseen_public_inputs(self):
        cases=run()["cases"]
        self.assertTrue(any(stage["fallback"]["local_recovery"] for c in cases for stage in c["stages"]))
        for case in cases:
            for stage in case["stages"]:
                if stage["fallback"]["local_recovery"]:
                    score=stage["scores"]["local_recovery"]
                    self.assertEqual(score["wrong"],0)
                    self.assertEqual(score["correct"],0)
                    self.assertEqual(score["abstentions"],score["unseen"])

    def test_recovery_does_not_promise_unknown_family_safety(self):
        cases=run()["cases"]
        outsider=[c for c in cases if not c["in_memory_diagnostic"]]
        self.assertEqual(len(outsider),12)
        self.assertTrue(any(stage["scores"]["local_recovery"]["wrong"]>0
                            for c in outsider for stage in c["stages"]))

    def test_invalid_public_feedback_rejected(self):
        for model in (RecoveringLocalProbe(),RecoveringConventionalProbe()):
            with self.assertRaises(ValueError):
                model.observe_target(INPUTS[0],1)
        with self.assertRaises(ValueError):
            trial(16)

    def test_detection_limits_are_scientific_negative_controls(self):
        cases=run()["cases"]
        unfamiliar=[case for case in cases if not case["in_memory_diagnostic"]]
        expected=((16,12,0),(16,0,0),(4,8,8))
        for index,(wrong,abstain,detected) in enumerate(expected):
            self.assertEqual(sum(case["stages"][index]["scores"]["local_recovery"]["wrong"]
                                 for case in unfamiliar),wrong)
            self.assertEqual(sum(case["stages"][index]["scores"]["local_recovery"]["abstentions"]
                                 for case in unfamiliar),abstain)
            self.assertEqual(sum(case["stages"][index]["fallback"]["local_recovery"]
                                 for case in unfamiliar),detected)
        for case in cases:
            for stage in case["stages"]:
                self.assertEqual(stage["scores"]["local_recovery"],
                                 stage["scores"]["conventional_recovery"])
                self.assertEqual(stage["scores"]["local_recovery"],
                                 stage["scores"]["source_only"])
