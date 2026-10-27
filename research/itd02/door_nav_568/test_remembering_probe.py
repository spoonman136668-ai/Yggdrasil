"""Verify bounded memory for unexpected public probe transitions."""
import unittest
from remembering_probe_scheduler import PublicExceptionMemory, RememberingProbeScheduler
from two_hop_evidence_audit import build

class RememberingProbeTests(unittest.TestCase):
    def test_retains_first_failure_and_avoids_retry_next_session(self):
        native = build()
        memory = PublicExceptionMemory(capacity=2)
        starts = [(b"xA-training", (0, 1)), (b"xB-training", (0, 1))]
        first = RememberingProbeScheduler(native.active_links,
                                          native.archived_links, starts, memory)
        key = first.next_probe()
        self.assertIsNone(first.first_outcome(b"Z9-unexpected"))
        self.assertEqual(len(memory.exceptions), 1)
        second = RememberingProbeScheduler(native.active_links,
                                           native.archived_links, starts, memory)
        next_key = second.next_probe()
        self.assertNotEqual(next_key, key)
        self.assertLessEqual(len(second.candidates), 3)
        # Public consequences are supplied only after scheduling each action.
        from two_hop_evidence_audit import SECOND
        successors = {(frame, action): old for frame, action, old, newer in SECOND}
        while next_key is not None:
            follow = second.first_outcome(native.active_links[next_key])
            if follow is not None:
                second.second_outcome(successors[follow])
            if second.decision() is not None:
                break
            next_key = second.next_probe()
        self.assertEqual(second.decision(), "snapshot")
        self.assertEqual(second.actions, 4)
        self.assertEqual(len(memory.exceptions), 1)

    def test_capacity_rejects_additional_exceptions(self):
        memory = PublicExceptionMemory(capacity=1)
        memory.unexpected((b"x", 0), b"M", b"Z")
        with self.assertRaises(ValueError):
            memory.unexpected((b"y", 0), b"M", b"Y")
        self.assertEqual(len(memory.exceptions), 1)
        memory.corroborated((b"x", 0))
        self.assertEqual(len(memory.exceptions), 0)

    def test_storage_is_not_inferred_as_new_physics(self):
        native = build()
        memory = PublicExceptionMemory()
        starts = [(b"xA-training", (0, 1)), (b"xB-training", (0, 1))]
        original = dict(native.active_links)
        scheduler = RememberingProbeScheduler(native.active_links,
                                               native.archived_links, starts, memory)
        scheduler.next_probe()
        scheduler.first_outcome(b"Z9-unexpected")
        self.assertEqual(native.active_links, original)

if __name__ == "__main__":
    unittest.main()
