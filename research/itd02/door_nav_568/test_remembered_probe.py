"""Retained exception reduces redundant probe actions, within finite memory."""
import unittest
from remembering_probe_scheduler import PublicExceptionMemory, RememberingProbeScheduler
from remembered_probe_audit import run
from two_hop_evidence_audit import build

class RememberingProbeTests(unittest.TestCase):
    def test_retained_failure_reduces_repeated_probe_cost(self):
        report = run()
        first = report["first_session"]
        second = report["second_session_with_memory"]
        self.assertEqual(first["selected"], "snapshot")
        self.assertEqual(first["actions"], 5)
        self.assertEqual(first["rejections"], 1)
        self.assertEqual(second["selected"], "snapshot")
        self.assertEqual(second["actions"], 4)
        self.assertEqual(second["rejections"], 0)
        self.assertEqual(second["known_exceptions"], 1)
        self.assertEqual(report["unremembered_failure_baseline"]["interventions"], 5)
        self.assertEqual(report, run())

    def test_exception_memory_limit_and_explicit_revision(self):
        memory = PublicExceptionMemory(capacity=1)
        memory.unexpected((b"a", 0), b"b", b"c")
        with self.assertRaises(ValueError):
            memory.unexpected((b"x", 0), b"y", b"z")
        memory.corroborated((b"a", 0))
        self.assertEqual(memory.exceptions, {})
        memory.unexpected((b"x", 0), b"y", b"z")
        self.assertEqual(len(memory.exceptions), 1)

    def test_no_available_corroborating_probe_abstains(self):
        native = build()
        starts = [(b"xA-training", (0, 1)), (b"xB-training", (0, 1))]
        memory = PublicExceptionMemory()
        for a in (0, 1):
            memory.unexpected((b"xA-training", a), b"M1-intermediate", b"Z9")
        scheduler = RememberingProbeScheduler(
            native.active_links, native.archived_links, starts, memory)
        self.assertIsNone(scheduler.decision())
        first = scheduler.next_probe()
        self.assertIsNotNone(first)
        self.assertEqual(first[0], b"xB-training")
        self.assertIsNone(scheduler.decision())

if __name__ == "__main__":
    unittest.main()
