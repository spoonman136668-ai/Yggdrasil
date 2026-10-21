"""MR7: independently exercise existing G7A producer -> NCI-04H repair.

Native development-only source/transport falsifier; NO new source families,
protected first-use, new learner, role targets or scientific acceptance.
"""
import json
import pathlib
import unittest

from yggdrasil.task_runtime import LocalTaskRuntime
from yggdrasil.nci04g7a_environment_adapter import BoundedLocalEnvironment
from yggdrasil.nci04g5_local_residual import LocalResidualAdapter
from yggdrasil.nci04h_local_repair import LocalCausalRepair


ROOT = pathlib.Path(__file__).resolve().parents[1]


class NativePairSnapshotCustody(unittest.TestCase):
    def test_existing_consecutive_native_observations_cannot_be_jointly_consumed(self):
        runtime = LocalTaskRuntime()
        runtime.lesion([0])
        before_first = runtime.snapshot()
        original_damaged_role = list(runtime.core.roles[0])
        bits = [1, 0, 1, 0, 1, 0, 1, 0]
        observer = BoundedLocalEnvironment(ROOT, runtime)

        # Use ONLY the original Git-pinned, model-independent simulated
        # environment producer. Unlike H's unit fixture, each genuine native
        # observation updates its intact sender before the next is produced.
        packet_left, proof_left = observer.observe(bits, 0, 0, 1, 5)
        before_second = runtime.snapshot()
        packet_right, proof_right = observer.observe(bits, 0, 0, 7, 5)
        current = runtime.snapshot()

        self.assertNotEqual(before_first, before_second)
        self.assertNotEqual(before_second, current)
        self.assertFalse(proof_left["producer"]["external_sensor_attestation"])
        self.assertFalse(proof_right["producer"]["external_sensor_attestation"])
        self.assertEqual(proof_left["postlesion_damaged_target_labels"], 0)
        self.assertEqual(proof_right["postlesion_damaged_target_labels"], 0)

        # Both original messages are authentic relative to their individual
        # exact source snapshots. Neither describes the final snapshot that
        # NCI-04H's atomic repair API requires for the pair.
        adapter = LocalResidualAdapter(runtime)
        self.assertEqual(adapter.verify(packet_left, before_first)["sender"], 1)
        self.assertEqual(adapter.verify(packet_right, before_second)["sender"], 7)
        with self.assertRaisesRegex(ValueError, "source snapshot digest mismatch"):
            LocalCausalRepair(runtime).observe_and_recover(
                0, (bits[0], bits[7], bits[1]),
                [packet_left, packet_right], current)

        self.assertEqual(runtime.snapshot(), current)
        self.assertEqual(runtime.core.roles[0], original_damaged_role)
        self.assertEqual(len(packet_left) + len(packet_right), 76)
        print("MR7_NATIVE_CONSECUTIVE_PACKET_CUSTODY=" + json.dumps({
            "result": "REPRODUCED_EXPECTED_INTEGRATION_BLOCK",
            "source": "existing native G7A model-independent Git-pinned simulated producer",
            "two_individually_valid_packet_snapshots": True,
            "snapshots_after_successive_sender_updates_differ": True,
            "repair_requires_identical_current_snapshot": True,
            "joint_native_repair": "REJECTED_WITHOUT_DAMAGED_ROLE_MUTATION",
            "lost_function_recovered": False,
            "external_sensor_authentication": False,
            "total_wire_bytes": 76,
            "new_learned_coefficients": 0,
            "protected_scientific_first_use": False,
        }, sort_keys=True))


if __name__ == "__main__":
    unittest.main()
