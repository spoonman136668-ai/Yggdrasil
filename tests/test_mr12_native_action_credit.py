"""MR12 native-only action/outcome learning seam; engineering acceptance.

The existing MR11 original counterfactual observations are reused only for
interface testing, NOT as a new scientific evaluation or transfer claim.
"""
import json
import pathlib
import subprocess
import tempfile
import unittest

from yggdrasil.task_runtime import LocalTaskRuntime
from yggdrasil.nci04j_action_credit import (
    NativeActionLocalCredit, action_local_features,
)


ROOT = pathlib.Path(__file__).resolve().parents[1]


class NativeActionCausalCredit(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory(prefix="mr12-exact-source-")
        self.addCleanup(temp.cleanup)
        self.checkout = pathlib.Path(temp.name) / "source"
        subprocess.run(["git", "clone", "--quiet", "--no-hardlinks",
                        "--no-checkout", str(ROOT), str(self.checkout)],
                       check=True, capture_output=True)
        subprocess.run(["git", "-C", str(self.checkout), "config",
                        "core.autocrlf", "false"], check=True, capture_output=True)
        self.sha = subprocess.check_output(
            ["git", "-C", str(ROOT), "rev-parse", "HEAD"], text=True).strip()
        subprocess.run(["git", "-C", str(self.checkout), "checkout",
                        "--quiet", "--detach", self.sha],
                       check=True, capture_output=True)

    def test_actual_native_causal_action_is_seen_prior_to_own_consequence(self):
        runtime = LocalTaskRuntime()
        runtime.lesion([0])
        bits = [0] * 8
        learned = NativeActionLocalCredit(self.checkout, runtime)
        before = runtime.snapshot()
        feature0 = action_local_features(runtime, bits, 1, 0)
        feature1 = action_local_features(runtime, bits, 1, 1)
        self.assertEqual(len(feature0), 7)
        self.assertEqual(feature0[:6], feature1[:6])
        self.assertEqual(feature0[-1], -1.)
        self.assertEqual(feature1[-1], 1.)
        p0 = learned.predict(bits, 1, 0)
        p1 = learned.predict(bits, 1, 1)
        receipt0 = learned.observe_native(bits, 0, 0, 1, 5)
        receipt1 = learned.observe_native(bits, 1, 0, 1, 6)

        self.assertEqual(receipt0["native_observed_outcome"], 0)
        self.assertEqual(receipt1["native_observed_outcome"], 1)
        self.assertEqual(receipt0["native_action"], 0)
        self.assertEqual(receipt1["native_action"], 1)
        self.assertEqual(receipt0["pre_outcome_prediction"], p0)
        self.assertEqual(receipt1["source_commit"], self.sha)
        self.assertEqual(receipt0["source_sha256"], receipt1["source_sha256"])
        self.assertNotEqual(runtime.snapshot(), before)
        self.assertNotEqual(learned.predict(bits, 1, 0), p0)
        self.assertEqual(runtime.core.events, 2)
        self.assertEqual(receipt0["wire_bytes"] + receipt1["wire_bytes"], 76)
        self.assertEqual(receipt1["fixed_native_coefficients"], 45)
        self.assertEqual(receipt1["new_trainable_parameters"], 0)
        self.assertFalse(receipt1["external_sensor_attested"])
        self.assertFalse(receipt1["independent_scientific_first_use"])
        self.assertFalse(receipt1["native_action_generalization_qualified"])
        self.assertEqual(runtime.core.roles[0], [0.]*3)
        self.assertEqual(LocalTaskRuntime.restore(runtime.snapshot()).snapshot(),
                         runtime.snapshot())
        self.assertEqual(sum(len(row) for row in runtime.core.genome) +
                         sum(len(row) for row in runtime.core.roles), 45)
        # Fully trained conventional Beta-smoothed conditional count sees
        # exactly the same two native action outcomes, no additional cases.
        count = {0: [0, 0], 1: [0, 0]}
        for receipt in (receipt0, receipt1):
            count[receipt["native_action"]][receipt["native_observed_outcome"]] += 1
        conventional_p0 = (count[0][1]+1)/(sum(count[0])+2)
        conventional_p1 = (count[1][1]+1)/(sum(count[1])+2)
        print("MR12_NATIVE_CAUSAL_ACTION_CREDIT=" + json.dumps({
            "gate": "MR12-action-feature-and-source-verified-native-learning",
            "source_commit": self.sha,
            "executed_native_outcomes": [0, 1],
            "action0_prediction_before_training": p0,
            "action1_prediction_before_training": p1,
            "action0_prediction_after_training": learned.predict(bits, 1, 0),
            "action1_prediction_after_training": learned.predict(bits, 1, 1),
            "conditional_count_trained_action0": conventional_p0,
            "conditional_count_trained_action1": conventional_p1,
            "observation_identity": "G7A-G5-source-bound-action-and-own-outcome",
            "native_packet_bytes": 76,
            "native_existing_coefficients": 45,
            "native_added_parameters": 0,
            "damaged_target_label_supplied": False,
            "exact_cold_restart": True,
            "source_simulated_not_external_sensor": True,
            "independent_scientific_first_use": False,
            "unfamiliar_task_transfer": "NOT_TESTED",
            "native_function_recovery": "NOT_TESTED",
            "all_in_matched_cpu_rss": "NOT_QUALIFIED",
            "scientific_admission": "NO_GO",
        }, sort_keys=True))

    def test_invalid_actions_source_and_target_fail_closed(self):
        rt = LocalTaskRuntime()
        rt.lesion([0])
        s0 = rt.snapshot()
        native = NativeActionLocalCredit(self.checkout, rt)
        for call in (
            lambda: native.observe_native([0]*8, 2, 0, 1, 1),
            lambda: native.observe_native([0]*8, 0, 0, 3, 1),
            lambda: native.observe_native([0]*8, 0, 1, 0, 1),
            lambda: native.observe_native([0]*8, 0, 0, 1, -1),
            lambda: native.observe_native([0]*7, 0, 0, 1, 1),
            lambda: native.predict([0]*8, 1, -1),
        ):
            with self.assertRaises(ValueError):
                call()
            self.assertEqual(rt.snapshot(), s0)
        # Untrusted native source must not be interpreted as model feedback.
        with self.assertRaises((ValueError, OSError, FileNotFoundError)):
            NativeActionLocalCredit(self.checkout / "does-not-exist", rt).observe_native(
                [0]*8, 0, 0, 1, 1
            )
        self.assertEqual(rt.snapshot(), s0)


if __name__ == "__main__":
    unittest.main()
