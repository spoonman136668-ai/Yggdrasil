"""MR11: existing native world counterfactual action observability falsifier.

Retains frozen MR7/MR8/MR9/MR10 negatives; no invented task, answer-label
oracle, new learning rules or protected scientific source first-use. Source
is the original G7A Git-pinned internally simulated native environment.
The original H/G6 sensor interface omits ACTION from local causal features.
"""
import json
import pathlib
import subprocess
import tempfile
import unittest

from yggdrasil.task_runtime import LocalTaskRuntime
from yggdrasil.nci04g7a_environment_adapter import BoundedLocalEnvironment
from yggdrasil.nci04g5_local_residual import (
    LocalResidualAdapter, local_features, WIRE_BYTES,
)

ROOT = pathlib.Path(__file__).resolve().parents[1]


class NativeActionIdentifiability(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="mr11-source-pin-")
        self.addCleanup(self.temp.cleanup)
        self.root = pathlib.Path(self.temp.name) / "native"
        subprocess.run(["git", "clone", "--quiet", "--no-hardlinks",
                        "--no-checkout", str(ROOT), str(self.root)],
                       check=True, capture_output=True)
        subprocess.run(["git", "-C", str(self.root), "config",
                        "core.autocrlf", "false"], check=True, capture_output=True)
        self.sha = subprocess.check_output(
            ["git", "-C", str(ROOT), "rev-parse", "HEAD"],
            text=True).strip()
        subprocess.run(["git", "-C", str(self.root), "checkout", "--quiet",
                        "--detach", self.sha], check=True, capture_output=True)

    def test_original_native_world_counterfactual_effect_is_not_in_predictor_inputs(self):
        # Each of the eight original three-local-bit contexts is tested with
        # both G7A interventions. Both worlds begin at EXACTLY one unchanged
        # post-lesion source snapshot. This test never teaches damaged labels.
        source = LocalTaskRuntime()
        source.lesion([0])
        baseline = source.snapshot()
        original_genome = source.core.genome
        pairs = []
        original_wire_bytes = 0
        matched_source = None
        for code in range(8):
            # Damaged recipient=0, intact sender=1, sender's other neighbor=2.
            # For each sender local 3-bit context, hold all 8 bits constant
            # while changing the *real* native intervention action alone.
            bits = [0] * 8
            bits[1] = code & 1
            bits[0] = (code >> 1) & 1
            bits[2] = (code >> 2) & 1
            sensor_prior = (bits[1], bits[0], bits[2])
            native_features = tuple(source.features(bits, 1))
            g6_features = tuple(local_features(sensor_prior))
            results = []
            for action in (0, 1):
                fork = LocalTaskRuntime.restore(baseline)
                wire, receipt = BoundedLocalEnvironment(
                    self.root, fork).observe(bits, action, 0, 1, code*2+action)
                self.assertEqual(len(wire), WIRE_BYTES)
                original_wire_bytes += len(wire)
                self.assertFalse(receipt["external_sensor"])
                self.assertEqual(receipt["postlesion_damaged_target_labels"], 0)
                self.assertEqual(receipt["action"], action)
                self.assertEqual(receipt["observed_world"],
                                 "DETERMINISTIC_SIMULATED_CAUSAL_TRANSITION")
                identity = (receipt["producer"]["source_commit"],
                            receipt["producer"]["environment_sha256"])
                if matched_source is None:
                    matched_source = identity
                self.assertEqual(matched_source, identity)
                self.assertEqual(fork.core.genome, original_genome)
                self.assertEqual(fork.core.roles[0], source.core.roles[0])
                self.assertEqual(fork.core.events, source.core.events + 1)
                payload = LocalResidualAdapter(
                    LocalTaskRuntime.restore(baseline)).verify(wire, baseline)
                # Original 38-byte receipt has observed result and residual,
                # but NO explicitly attested pre-outcome causal action field.
                self.assertNotIn("action", payload)
                self.assertEqual(payload["sender"], 1)
                self.assertEqual(payload["recipient"], 0)
                self.assertEqual(payload["own_next_bit"],
                                 receipt["measured_sender_next_bit"])
                self.assertEqual(
                    tuple(source.features(bits, 1)), native_features)
                self.assertEqual(
                    tuple(local_features(sensor_prior)), g6_features)
                results.append(receipt["measured_sender_next_bit"])
            # Same local inputs, same starting trained/role state, different
            # causal action -> opposite actual native consequences.
            self.assertEqual(results[0] ^ results[1], 1)
            pairs.append(results)

        self.assertEqual(source.snapshot(), baseline)
        self.assertEqual(len(pairs), 8)
        # Any single pre-outcome probability p conditioned only on local
        # features must predict identically for a pair. For opposite binary
        # truths y0=0,y1=1, Brier=(p^2+(1-p)^2)/2 >= 1/4.
        # An action-aware source-inspection control can in principle disambiguate,
        # but this is NOT an independently blinded scientific comparator.
        lower_bound = 0.25
        self.assertEqual(original_wire_bytes, 16 * 38)
        print("MR11_NATIVE_CAUSAL_ACTION_OBSERVABILITY=" + json.dumps({
            "source_commit": self.sha,
            "source": "existing G7A Git-verified native simulator",
            "local_context_pairs": len(pairs),
            "original_native_process_observations": 16,
            "same_state_same_local_features_different_action": True,
            "opposite_counterfactual_native_results": len(pairs),
            "native_predictor_explicit_action_feature": False,
            "survivor_credit_explicit_action_feature": False,
            "original_wire_explicit_action_field": False,
            "original_wire_bytes": original_wire_bytes,
            "best_balanced_pair_brier_without_action": lower_bound,
            "action_aware_inspection_control": "NECESSARY, NOT INDEPENDENTLY QUALIFIED",
            "external_sensor_attested": False,
            "source_native_functional_specialization": "NOT_DEMONSTRATED",
            "original_runtime_unchanged": True,
            "scientific_first_use": False,
            "science_admission": "BLOCKED",
        }, sort_keys=True))


if __name__ == "__main__":
    unittest.main()
