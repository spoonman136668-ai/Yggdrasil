"""Adaptive informative probes: retry, abstention, resource ceilings."""
import unittest
from adaptive_probe_audit import run, trial
from adaptive_probe_scheduler import AdaptiveProbeScheduler
from two_hop_evidence_audit import build

class AdaptiveProbeTests(unittest.TestCase):
    def test_clean_and_failed_probe_recovery(self):
        outcomes = run()
        self.assertEqual(outcomes["clean_A"]["selected"], "snapshot")
        self.assertEqual(outcomes["clean_B"]["selected"], "active")
        recovered = outcomes["recover_after_first_failure"]
        self.assertEqual(recovered["selected"], "snapshot")
        self.assertEqual(recovered["rejected_first_hops"], 1)
        self.assertEqual(recovered["confirmed_chains"], 2)
        self.assertLessEqual(recovered["interventions"], 6)

    def test_insufficient_budget_or_unavailable_independence_abstains(self):
        outcomes = run()
        self.assertIsNone(outcomes["low_budget"]["selected"])
        self.assertIsNone(outcomes["one_start_only"]["selected"])
        self.assertLessEqual(outcomes["low_budget"]["interventions"], 4)

    def test_hard_candidate_cap_and_action_budget(self):
        native = build()
        starts = [(b"xA-training", (0, 1)), (b"xB-training", (0, 1))]
        with self.assertRaises(ValueError):
            AdaptiveProbeScheduler(native.active_links, native.archived_links,
                                   starts, candidate_cap=2)
        with self.assertRaises(ValueError):
            AdaptiveProbeScheduler(native.active_links, native.archived_links,
                                   starts, limit=1)
        self.assertEqual(run(), run())

    def test_bounded_storage_and_no_unsupported_choices(self):
        for name, result in run().items():
            if not isinstance(result, dict):
                continue
            self.assertLessEqual(result["stored_examples"], 256)
            self.assertLessEqual(result["transition_records"], 256)
            self.assertIn(result["selected"], (None, "snapshot", "active"))

if __name__ == "__main__":
    unittest.main()
