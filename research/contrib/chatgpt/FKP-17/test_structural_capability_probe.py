"""Source-safe FKP-17 frozen-architecture counterexample qualification.

The toy public trajectories are fully synthetic and NOT owner-protected law
worlds. Tests certify representation collision, not empirical transfer.
"""
import ast
from pathlib import Path
import unittest

import public_policies as structured
import source_fixture as fixture
import strong_controls as independent
import structural_capability_probe as probe


class RepresentationCollisionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        facts = tuple(row for _, _, row in fixture.foundation_facts())
        cls.candidate = structured.PublicRelationArm(
            "STRUCTURED").fit_public_foundation(facts)
        cls.control = independent.SymbolicBayes().fit_public_foundation(facts)
        cls.proof = probe.audit_frozen_public_arms(cls.candidate, cls.control)

    def test_freeze_facts_and_actual_control_identity(self):
        self.assertEqual(self.candidate.received_foundation_count, 32768)
        self.assertEqual(self.control.foundation_count, 32768)
        self.assertEqual(self.candidate.foundation_sha256,
                         self.control.foundation_sha256)
        self.assertEqual(self.proof["source_prior_public_sha256"],
                         "c8400f67e8d26147de702c0c9bdba1f05581ee6f70635b3e9c90d73d6af81ecf")
        self.assertLess(self.candidate.learned_bytes, 1048576)
        self.assertLess(self.control.memory_bytes, 1048576)

    def test_two_physical_cycles_same_initial_and_final_state(self):
        a = probe.conditional_cycle(2)
        b = probe.conditional_cycle(0)
        self.assertEqual(a[0].before, b[0].before)
        self.assertEqual(a[-1].after, b[-1].after)
        self.assertEqual(a[0].before, a[-1].after)
        self.assertEqual(b[0].before, b[-1].after)
        self.assertGreater(a[0].reward, 0)
        self.assertLess(b[0].reward, 0)
        self.assertEqual(sum(row.reward for row in a), 0.0)
        self.assertEqual(sum(row.reward for row in b), 0.0)
        self.assertEqual((a[0].action, a[1].action), (3, 3))
        self.assertEqual((b[0].action, b[1].action), (3, 3))
        self.assertEqual(probe._transition_history(a[0]), a[1].history[0])
        self.assertEqual(probe._transition_history(b[0]), b[1].history[0])

    def test_frozen_candidate_erases_state_conditioned_relationship(self):
        self.assertTrue(
            self.proof["candidate_same_complete_state_after_distinct_conditional_laws"])
        self.assertTrue(
            self.proof["candidate_same_choice_after_distinct_conditional_laws"])
        self.assertTrue(self.proof["independent_conditional_symbolic_control_distinguishes"])
        self.assertEqual(self.proof["true_next_action3_rewards_for_two_laws"],
                         [0.125, -0.125])
        self.assertEqual(self.proof["safe_action4_reward_both_laws"], 0.0)
        self.assertEqual(self.proof["best_of_two_tested_actions_by_law"], [3, 4])

    def test_temporal_action_order_erased_with_same_present_state(self):
        ab = probe.temporal_cycle(2)
        ba = probe.temporal_cycle(5)
        self.assertEqual(tuple(x.action for x in ab), (2, 5))
        self.assertEqual(tuple(x.action for x in ba), (5, 2))
        self.assertEqual(ab[-1].after, ba[-1].after)
        self.assertTrue(self.proof["candidate_same_complete_state_after_reordered_events"])
        self.assertTrue(self.proof["candidate_same_choice_after_reordered_events"])

    def test_readiness_fence_rejects_even_positive_development_scores(self):
        self.assertEqual(self.proof["classification"],
                         "STRUCTURED_REPRESENTATION_NOT_READY_FOR_DELAYED_CONTEXT_LAW")
        with self.assertRaisesRegex(
                ValueError, "STRUCTURED_DELAYED_CONTEXT_REPRESENTATION_NO_GO"):
            probe.require_unfamiliar_law_representational_readiness(self.proof)
        with self.assertRaisesRegex(ValueError, "UNVERIFIED_OTHER_REPRESENTATION"):
            probe.require_unfamiliar_law_representational_readiness({})
        self.assertFalse(self.proof["scientific_pass"])
        self.assertFalse(self.proof["held_dev_opened"])
        self.assertFalse(self.proof["reserved_transfer_opened"])
        self.assertFalse(self.proof["native_model_promoted"])

    def test_source_type_and_mismatched_prior_refused(self):
        with self.assertRaises(ValueError):
            probe.conditional_cycle(1)
        with self.assertRaises(ValueError):
            probe.temporal_cycle(3)
        wrong = structured.PublicRelationArm("FLAT")
        with self.assertRaisesRegex(ValueError, "FROZEN_STRUCTURED"):
            probe.audit_frozen_public_arms(wrong, self.control)
        untrained = structured.PublicRelationArm("STRUCTURED")
        with self.assertRaisesRegex(ValueError, "FULL_PUBLIC_PRIOR"):
            probe.audit_frozen_public_arms(untrained, self.control)
        untrained_symbolic = independent.SymbolicBayes()
        with self.assertRaisesRegex(ValueError, "FULL_SYMBOLIC_PRIOR"):
            probe.audit_frozen_public_arms(self.candidate, untrained_symbolic)

    def test_strict_real_public_input_and_history_are_preserved(self):
        public = probe.conditional_cycle(2)
        self.assertEqual(public[0]._fields,
                         ("before", "action", "after", "reward", "done", "history"))
        self.assertEqual(public[0].history, ())
        self.assertEqual(public[1].history[-1].after, public[1].before)
        malformed = public[1]._replace(history=(object(),))
        original = self.candidate.state_receipt()
        with self.assertRaises(ValueError):
            self.candidate.observe_public(malformed)
        self.assertEqual(self.candidate.state_receipt(), original)

    def test_capability_probe_independent_of_source_generator_and_held(self):
        code = Path(probe.__file__).read_text(encoding="utf-8")
        tree = ast.parse(code)
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                self.assertNotIn("source_fixture", [x.name for x in node.names])
            if isinstance(node, ast.ImportFrom):
                self.assertNotIn(node.module, (
                    "source_fixture", "yggdrasil", "recurrent_control"))
        self.assertIn("CONSTRUCTIVE_PUBLIC_TOY_COUNTEREXAMPLE_NOT_PROTECTED_DATA",
                      code)
        self.assertNotIn("def open_dev(", code)
        self.assertNotIn("allow_dev=True", code)


if __name__ == "__main__":
    unittest.main()
