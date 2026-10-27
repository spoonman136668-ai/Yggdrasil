"""Evidence-selected three-step memory: action ownership and abstention."""
import unittest
from evidence_selected_three_step import EvidenceSelectedThreeStep
from evidence_selection_audit import run
from public_transition_planner import PublicTransitionPlanner
from test_three_step_feature_cells import fit

class EvidenceSelectorTests(unittest.TestCase):
    def test_audit_is_deterministic_and_bounded(self):
        a = run()
        self.assertEqual(a, run())
        for key in ("B_changed", "A_prior_context"):
            candidate = a[key]
            self.assertEqual(candidate["extra_probe_interactions"], 2)
            self.assertLessEqual(candidate["stored_examples"], candidate["max_examples"])
            self.assertIn(candidate["decision"], (None, 0, 1))

    def test_no_evidence_abstains_and_duplicate_probe_is_rejected(self):
        candidate = EvidenceSelectedThreeStep()
        fit(candidate, PublicTransitionPlanner())
        candidate.freeze_boundary()
        candidate.observe(b"xA-test", [0, 1])
        self.assertIsNone(candidate.choose())
        candidate.learn(0, b"M1-intermediate", 0, False)
        candidate.begin_probe()
        for _ in range(2):
            candidate.observe(b"xA-test", [0, 1])
            candidate.learn(0, b"M1-intermediate", 0, False)
        self.assertFalse(candidate.resolve_probe())
        self.assertIsNone(candidate.selected)

    def test_capacity_and_ownership_fail_closed(self):
        candidate = EvidenceSelectedThreeStep(probe_limit=2)
        fit(candidate, PublicTransitionPlanner())
        candidate.freeze_boundary()
        candidate.begin_probe()
        candidate.observe(b"zA-new", [0])
        with self.assertRaises(ValueError):
            candidate.learn(1, b"M1-intermediate", 0, False)
        candidate.learn(0, b"M1-intermediate", 0, False)
        candidate.observe(b"zB-new", [0])
        candidate.learn(0, b"D2-intermediate", 0, False)
        candidate.observe(b"zC-new", [0])
        with self.assertRaises(ValueError):
            candidate.learn(0, b"D2-intermediate", 0, False)
        self.assertEqual(len(candidate.evidence), 2)

if __name__ == "__main__":
    unittest.main()
