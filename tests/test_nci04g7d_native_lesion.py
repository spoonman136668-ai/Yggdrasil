"""NCI-04G7D: actual runtime structural observation, NOT functional recovery."""
import dataclasses
import hashlib
import json
import pathlib
import time
from unittest import mock
import unittest

from yggdrasil.task_runtime import LocalTaskRuntime
from yggdrasil.nci04g7d_native_lesion import NativeNeighborLesionObserver

ROOT = pathlib.Path(__file__).resolve().parents[1]


class NativeStructuralProducerQualification(unittest.TestCase):
    def test_native_neighbor_lesion_has_observed_not_supplied_consequence(self):
        runtime = LocalTaskRuntime()
        bit_state = (1, 0, 1, 0, 1, 0, 1, 0)
        own_prediction_before = runtime.component(bit_state, 7)
        original = runtime.snapshot()
        original_own_role = tuple(runtime.core.roles[7])
        start = time.process_time_ns()
        owner = NativeNeighborLesionObserver(runtime, ROOT)
        evidence = owner.intervene_and_measure(7, 0)
        cpu_ns = time.process_time_ns() - start
        after = runtime.snapshot()

        self.assertEqual(evidence.sender, 7)
        self.assertEqual(evidence.neighbor, 0)
        self.assertEqual((evidence.before_neighbor_damaged, evidence.after_neighbor_damaged), (0, 1))
        def expected_local_hash(damaged):
            raw=json.dumps({"sender":7,"neighbor":0,"sender_role":original_own_role,
                            "neighbor_damaged":damaged},sort_keys=True,separators=(",",":"))
            return hashlib.sha256(raw.encode()).hexdigest()
        self.assertEqual(evidence.before_local_sha256, expected_local_hash(0))
        self.assertEqual(evidence.after_local_sha256, expected_local_hash(1))
        self.assertEqual(len(evidence.source_commit), 40)
        self.assertEqual(len(evidence.source_sha256), 3)
        self.assertEqual(runtime.damaged, {0})
        self.assertEqual(tuple(runtime.core.roles[7]), original_own_role)
        self.assertEqual(runtime.component(bit_state, 7), own_prediction_before)
        self.assertEqual(LocalTaskRuntime.restore(after).snapshot(), after)
        self.assertEqual(runtime.core.events, 0, "structural witness must not masquerade as learning")
        with self.assertRaises(dataclasses.FrozenInstanceError):
            evidence.after_neighbor_damaged = 0
        with self.assertRaises(ValueError):
            owner.intervene_and_measure(7, 0)
        report = {
            "gate": "NCI-04G7D-Y",
            "native_runtime_owns_action": "PASS",
            "source_pinned_runtime": "PASS",
            "measured_adjacent_structural_transition": "PASS",
            "genuine_local_function_consequence": "NOT_OBSERVED",
            "independent_function_source": "MISSING",
            "native_survivor_role_unchanged": True,
            "hard_false_positive_function_recovery_claims": 0,
            "native_structural_snapshot_bytes_before": len(original.encode()),
            "native_structural_snapshot_bytes_after": len(after.encode()),
            "evidence_message_serialized_bytes": len(json.dumps(dataclasses.asdict(evidence)).encode()),
            "candidate_parent_process_cpu_ns": cpu_ns,
            "durable_highwater_across_crash": "NOT_QUALIFIED",
            "paired_cpu_rss_and_memory_nonregression": "NOT_QUALIFIED",
            "learned_transfer": "NOT_PROVEN",
            "scientific_first_use": False,
            "classification": "NATIVE_STRUCTURAL_EVENT_ONLY__SCIENCE_NO_GO"}
        print("NCI04G7D_YGGDRASIL_NATIVE_REPORT=" + json.dumps(report, sort_keys=True))

    def test_reject_non_neighbor_damaged_sender_and_wrong_owner(self):
        runtime = LocalTaskRuntime()
        producer = NativeNeighborLesionObserver(runtime, ROOT)
        initial = runtime.snapshot()
        for sender, target in ((7, 2), (0, 0), (-1, 0), (True, 0), (7, 8)):
            with self.assertRaises(ValueError):
                producer.intervene_and_measure(sender, target)
            self.assertEqual(runtime.snapshot(), initial)
        runtime.lesion([7])
        after = runtime.snapshot()
        with self.assertRaises(ValueError):
            producer.intervene_and_measure(7, 0)
        self.assertEqual(runtime.snapshot(), after)
        with self.assertRaises(TypeError):
            NativeNeighborLesionObserver(object(), ROOT)

    def test_no_observation_without_authenticated_native_source(self):
        runtime = LocalTaskRuntime()
        observer = NativeNeighborLesionObserver(runtime, ROOT)
        original_read = pathlib.Path.read_bytes
        def changed_source(path):
            if path.name == "task_runtime.py":
                return b"tampered-native-runtime-source"
            return original_read(path)
        with mock.patch.object(pathlib.Path, "read_bytes", changed_source):
            with self.assertRaisesRegex(ValueError, "native transition source changed"):
                observer.intervene_and_measure(7, 0)
        self.assertEqual(runtime.damaged, set())


if __name__ == "__main__":
    unittest.main()
