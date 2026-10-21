"""MR13 source-birth audit: no demonstrated heterogeneous native-cell effects.

Uses only pre-existing original G7A native simulator and original G7 source
classification. A source-readiness check, not novel experiment or new learner.
Neither MR9's scientific/evaluation data nor any protected first-use is used.
"""
import importlib.util
import json
import pathlib
import subprocess
import tempfile
import unittest

from yggdrasil.task_runtime import LocalTaskRuntime
from yggdrasil.nci04g7a_environment_adapter import BoundedLocalEnvironment

ROOT = pathlib.Path(__file__).resolve().parents[1]
WORLD = "scripts/nci04g7a_environment.py"
PSEUDO = "yggdrasil/nci04g7_source_producer.py"


class NativeSourceBirthHeterogeneity(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory(prefix="mr13-git-source-")
        self.addCleanup(tmp.cleanup)
        self.root = pathlib.Path(tmp.name) / "native"
        subprocess.run(["git", "clone", "--quiet", "--no-hardlinks",
                        "--no-checkout", str(ROOT), str(self.root)],
                       capture_output=True, check=True)
        subprocess.run(["git", "-C", str(self.root), "config",
                        "core.autocrlf", "false"],
                       capture_output=True, check=True)
        self.sha = subprocess.check_output(
            ["git", "-C", str(ROOT), "rev-parse", "HEAD"],
            text=True).strip()
        subprocess.run(["git", "-C", str(self.root), "checkout",
                        "--quiet", "--detach", self.sha],
                       check=True, capture_output=True)

    def test_native_source_has_one_action_conditioned_law_for_all_cell_positions(self):
        spec = importlib.util.spec_from_file_location(
            "mr13_original_g7a_source", self.root / WORLD
        )
        self.assertIsNotNone(spec)
        world = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(world)

        # Static source-birth observations exhaust every three-bit local
        # input with BOTH original intervention actions for all eight cells.
        # The damaged-cell bit is visible in the request but NEVER used as
        # a target label or teacher. No model is present during this check.
        conditional_by_role = []
        all_observations = 0
        for sender in range(8):
            recipient = (sender - 1) % 8
            other = (sender + 1) % 8
            observed = {}
            for bits3 in range(8):
                prior = [0]*8
                prior[sender] = bits3 & 1
                prior[other] = (bits3 >> 1) & 1
                prior[recipient] = (bits3 >> 2) & 1
                for action in (0, 1):
                    response = world.measure({
                        "prior": prior, "action": action,
                        "sender": sender, "damaged": recipient
                    })
                    self.assertEqual(
                        response["source"],
                        "SOURCE_PINNED_SIMULATED_ENVIRONMENT_NOT_EXTERNAL_SENSOR"
                    )
                    bit = response["observed_sender_next_bit"]
                    self.assertEqual(bit, prior[sender] ^ prior[other] ^ action)
                    observed[(bits3,action)] = bit
                    all_observations += 1
            conditional_by_role.append(observed)
        self.assertEqual(all_observations, 128)
        self.assertTrue(all(row == conditional_by_role[0]
                            for row in conditional_by_role))
        # A native H/role learner cannot discover distinct necessary
        # position-specific functions if the source provides the same
        # local causal law at every position.
        print("MR13_ORIGINAL_SOURCE_CAUSAL_HOMOGENEITY=" + json.dumps({
            "source_commit": self.sha,
            "original_native_world": WORLD,
            "all_original_source_measures": all_observations,
            "cell_positions": 8,
            "local_contexts": 8,
            "native_actions": 2,
            "exactly_same_action_conditioned_truth_table_at_every_cell": True,
            "distinct_cell_specific_causal_laws_source_observable": False,
            "external_source_sensor_attested": False,
            "this_test_trained_no_model": True,
            "independent_scientific_first_use": False,
            "scientific_admission": "NO_GO",
        }, sort_keys=True))

    def test_real_git_source_process_falsifier_and_pseudo_producer_boundary(self):
        # Execute 16 original independent G7A source subprocesses using its
        # genuine Git/source verifying adapter. Rotate one local context
        # and action across each cell. No new event generator/test oracle.
        original = self.root / PSEUDO
        committed = subprocess.check_output(
            ["git", "-C", str(self.root), "show", "HEAD:"+PSEUDO]
        )
        self.assertEqual(original.read_bytes(), committed)
        self.assertIn(b"INTERNAL_NATIVE_MODEL_EMITTED_PSEUDO_OBSERVATION",
                      committed)
        self.assertIn(b"not_externally_observed", committed)
        measurements = []
        for sender in range(8):
            recipient = (sender - 1) % 8
            prior = [0]*8
            prior[sender] = 1
            prior[(sender + 1)%8] = 0
            prior[recipient] = 1
            cell_responses = []
            for action in (0,1):
                rt = LocalTaskRuntime()
                rt.lesion([recipient])
                before = rt.snapshot()
                wire, receipt = BoundedLocalEnvironment(
                    self.root, rt).observe(
                        prior, action, recipient, sender, 10+sender*2+action
                    )
                self.assertEqual(len(wire), 38)
                self.assertEqual(receipt["producer"]["source_commit"], self.sha)
                self.assertFalse(receipt["producer"]["external_sensor_attestation"])
                self.assertEqual(receipt["postlesion_damaged_target_labels"], 0)
                self.assertEqual(rt.core.roles[recipient], [0.]*3)
                self.assertNotEqual(before, rt.snapshot())
                cell_responses.append(receipt["measured_sender_next_bit"])
            measurements.append(cell_responses)
        self.assertEqual(measurements, [[1,0]]*8)
        print("MR13_ORIGINAL_NATIVE_HETEROGENEITY_RECEIPT=" + json.dumps({
            "source_commit": self.sha,
            "native_subprocess_observations": 16,
            "identical_local_source_inputs_all_cells": True,
            "identical_action_conditioned_outcomes_all_cells": True,
            "source_native_process_observation": "INTERNALLY_AUTHORED_SIMULATION",
            "alternate_g7_producer": "MODEL_EMITTED_PSEUDO_OBSERVATION",
            "different_real_external_function_families_identified": 0,
            "original_packet_bytes": 16*38,
            "native_model_coefficients_changed": False,
            "scientific_first_use": False,
            "disposition": "HETEROGENEOUS_NATIVE_CAUSAL_SOURCE_NOT_AVAILABLE",
        }, sort_keys=True))


if __name__ == "__main__":
    unittest.main()
