"""Prospective public recheck outcomes and action-budget accounting."""
import unittest
from two_hop_evidence_audit import build
from remembering_probe_scheduler import PublicExceptionMemory
from revalidating_probe_scheduler import RevalidatingProbeScheduler

STARTS = [(b"xA-training", (0, 1)), (b"xB-training", (0, 1))]

def agent(memory, limit=6):
    model = build()
    return model, RevalidatingProbeScheduler(
        model.active_links, model.archived_links, STARTS, memory, limit=limit)

class RevalidationTests(unittest.TestCase):
    def test_physical_recheck_rehabilitates_stale_exception(self):
        memory = PublicExceptionMemory(capacity=2)
        model, first = agent(memory)
        failed_key = first.next_probe()
        self.assertIsNone(first.first_outcome(b"Z9-unexpected"))
        _, later = agent(memory)
        self.assertNotIn(failed_key, [c[0] for c in later.candidates])
        self.assertEqual(later.request_recheck(failed_key), failed_key)
        self.assertIsNone(later.next_probe())
        self.assertTrue(later.finish_recheck(model.active_links[failed_key]))
        self.assertNotIn(failed_key, memory.exceptions)
        self.assertIn(failed_key, [c[0] for c in later.candidates])
        self.assertEqual((later.actions, later.rechecks), (1, 1))
        self.assertIsNone(later.decision())

    def test_conflicting_recheck_preserves_negative_memory(self):
        memory = PublicExceptionMemory(capacity=2)
        model, session = agent(memory)
        key = session.next_probe()
        session.first_outcome(b"Z9-unexpected")
        _, later = agent(memory)
        self.assertEqual(later.request_recheck(key), key)
        self.assertFalse(later.finish_recheck(b"Y8-still-unexpected"))
        self.assertEqual(memory.exceptions[key][1], b"Y8-still-unexpected")
        self.assertNotIn(key, [c[0] for c in later.candidates])
        self.assertIsNone(later.decision())

    def test_budget_and_unowned_rechecks_refuse(self):
        memory = PublicExceptionMemory(capacity=1)
        model, first = agent(memory)
        key = first.next_probe()
        first.first_outcome(b"Z9-unexpected")
        _, limited = agent(memory, limit=2)
        self.assertEqual(limited.request_recheck(key), key)
        with self.assertRaises(ValueError):
            limited.finish_recheck(None)
        self.assertEqual(limited.request_recheck(key), None)
        self.assertFalse(limited.finish_recheck(b"Y8-unexpected"))
        self.assertEqual(limited.request_recheck((b"other", 1)), None)
        self.assertEqual(limited.request_recheck(key), key)
        self.assertFalse(limited.finish_recheck(b"Y8-unexpected"))
        self.assertEqual(limited.request_recheck(key), None)
        self.assertEqual(limited.actions, 2)

    def test_no_model_rewrite_from_a_single_public_recheck(self):
        memory = PublicExceptionMemory()
        model, first = agent(memory)
        key = first.next_probe()
        original = dict(model.active_links)
        first.first_outcome(b"Z9-unexpected")
        later = RevalidatingProbeScheduler(model.active_links, model.archived_links,
                                           STARTS, memory)
        later.request_recheck(key)
        self.assertTrue(later.finish_recheck(original[key]))
        self.assertEqual(model.active_links, original)
        self.assertEqual(len(memory.exceptions), 0)

if __name__ == "__main__":
    unittest.main()
