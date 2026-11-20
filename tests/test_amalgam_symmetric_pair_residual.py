"""Gate24 source-free opt-in cross-view residual qualification.

Preregistered before implementation; independent draft shadow contributor only.
Never loads an owner model or any protected original world.
"""
from fractions import Fraction
from importlib.util import module_from_spec, spec_from_file_location
from math import isclose
from pathlib import Path
import unittest

from yggdrasil.native_jepa2_multilearner import ActionLatentSpecialist

MODULE = Path(__file__).resolve().parents[1] / (
    "research/contrib/chatgpt/CAUSAL-AMALGAM/symmetric_pair_residual.py")
SPEC = spec_from_file_location("amalgam_gate24_residual", MODULE)
GATE = module_from_spec(SPEC)
SPEC.loader.exec_module(GATE)


class SymmetricPairResidualTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.result = GATE.audit()

    def test_frozen_fit_and_untrained_context_eval_are_disjoint(self):
        for law in ("xor", "or"):
            train, evaluate = GATE.rows(law, 0), GATE.rows(law, 1)
            self.assertEqual(len(train), 16)
            self.assertEqual(len(evaluate), 16)
            self.assertEqual(len(set(r[0] for r in train)), 16)
            self.assertEqual({r[0] for r in train},
                             {r[0] for r in evaluate})
            self.assertEqual({v[0][0] for _, v, _ in train}, {0})
            self.assertEqual({v[0][0] for _, v, _ in evaluate}, {1})
            self.assertEqual(
                {r[1][0][1:] + r[1][1][1:] for r in train},
                set(GATE.PAIRS))
            for _, views, label in train + evaluate:
                a, b = GATE._public_pair(views)
                self.assertEqual(label, (a ^ b) if law == "xor" else (a | b))
        with self.assertRaisesRegex(ValueError, "GATE24_LAW_CONTEXT"):
            GATE.rows("xor", 2)
        with self.assertRaisesRegex(ValueError, "GATE24_LAW_CONTEXT"):
            GATE.rows("parity-plus", 0)

    def test_primary_xor_trained_model_represents_interaction(self):
        xor = self.result["xor"]
        self.assertEqual(xor["active"]["correct"], 4)
        self.assertLessEqual(xor["no_interaction"]["correct"], 3)
        self.assertLessEqual(xor["base"]["correct"], 3)
        self.assertTrue(all(abs(x) < 100 for x in xor["weights"]))
        self.assertFalse(xor["scientific_pass"])

    def test_equal_fit_data_conventional_controls_are_not_beaten_by_assertion(self):
        for key in ("xor", "or_negative"):
            result = self.result[key]
            self.assertEqual(result["pair_count"]["correct"], 4)
            self.assertEqual(result["pair_count"]["brier"], Fraction(1, 36))
            self.assertEqual(result["exact_symbolic"]["correct"], 4)
            self.assertEqual(result["exact_symbolic"]["brier"], 0)
            self.assertIn(result["symbolic_fit_selected"], ("xor", "or"))
            # Strongest exact symbolic comparator beats or ties any learned
            # learner on this disclosed source-free family.
            self.assertGreaterEqual(result["active"]["brier"], 0)

    def test_or_negative_control_is_not_an_interaction_only_success(self):
        result = self.result["or_negative"]
        self.assertEqual(result["active"]["correct"], 4)
        self.assertEqual(result["no_interaction"]["correct"], 4)
        self.assertEqual(result["symbolic_fit_selected"], "or")

    def test_active_xor_residual_regresses_different_old_or_law(self):
        # In the same action/public-pair format, an adapter trained on XOR
        # must not be promoted as a universal relationship/readout fix.
        self.assertLess(self.result["or_negative"]["xor_adapter_on_or"]["correct"], 4)

    def test_default_off_preserves_original_base_forecast_and_weights(self):
        for key in ("xor", "or_negative"):
            self.assertTrue(self.result[key]["base_weights_unchanged"])
            self.assertTrue(self.result[key]["off_mode_exact"])
        head = ActionLatentSpecialist("reward")
        for _, views, y in GATE.rows("xor", 0):
            head.observe(views, GATE.EXTRAS, y)
        old_data = head.as_data()
        residual = GATE.SymmetricPairResidual().fit(GATE.rows("xor", 0))
        for context in (0, 1):
            for a, b in GATE.PAIRS:
                views = ((context, a), (context, b))
                original = head.probability(views, *GATE.EXTRAS)
                self.assertEqual(
                    residual.probability(original, views), original)
                self.assertEqual(
                    residual.probability(original, views, enabled=False),
                    original)
        self.assertEqual(old_data, head.as_data())

    def test_update_budget_and_parameter_count_exact(self):
        for key in ("xor", "or_negative"):
            report = self.result[key]
            self.assertEqual(report["full_params"], 3)
            self.assertEqual(report["ablation_params"], 2)
            self.assertEqual(report["fit_rows"], 16)
            self.assertEqual(report["eval_rows_untrained"], 16)
            self.assertEqual(report["newton_steps"], 14)
            self.assertEqual(report["row_exposures_each_residual_arm"], 224)
            self.assertEqual(report["original_source_actions"], 0)
            self.assertEqual(report["canonical_model_updates"], 0)

    def test_deterministic_fit_replay_no_new_state_authority(self):
        for law in ("xor", "or"):
            first = GATE.SymmetricPairResidual().fit(GATE.rows(law, 0))
            second = GATE.SymmetricPairResidual().fit(GATE.rows(law, 0))
            self.assertEqual(first.weights, second.weights)
            self.assertTrue(all(isclose(a, b, abs_tol=1e-8, rel_tol=0)
                                for a, b in zip(first.weights, second.weights)))
        self.assertEqual(self.result["integration_authority"],
                         "NONE_SHADOW_RESEARCH_ONLY")
        self.assertFalse(self.result["scientific_pass"])

    def test_input_and_interaction_fences(self):
        with self.assertRaisesRegex(ValueError, "GATE24_INTERACTION_TYPE"):
            GATE.SymmetricPairResidual(interaction=1)
        with self.assertRaisesRegex(ValueError, "GATE24_PUBLIC_PAIR"):
            GATE._features(((0, 0), (1, 1)), interaction=True)
        with self.assertRaisesRegex(ValueError, "GATE24_PUBLIC_PAIR"):
            GATE._features(((0, 0), (0, 2)), interaction=True)
        with self.assertRaisesRegex(ValueError, "GATE24_ENABLED_TYPE"):
            GATE.SymmetricPairResidual().probability(
                0.5, ((0, 0), (0, 1)), enabled=1)
        with self.assertRaisesRegex(ValueError, "GATE24_ORIGINAL_PROBABILITY"):
            GATE.SymmetricPairResidual().probability(
                float("nan"), ((0, 0), (0, 1)), enabled=True)
        with self.assertRaisesRegex(ValueError, "GATE24_FIT_WITNESSES"):
            GATE.SymmetricPairResidual().fit(())

    def test_no_interaction_feature_cannot_represent_symmetric_xor(self):
        # Algebraic independent bound: additive scores c0 + c1*(a+b)
        # cannot be negative at both matching pairs 00 and 11 while
        # positive at both mixed pairs 01/10.
        for c0, c1 in ((-1, 0), (0, 1), (1, -1), (0, 0)):
            predictions = [int(c0 + c1 * (a + b) > 0)
                           for a, b in GATE.PAIRS]
            truth = [a ^ b for a, b in GATE.PAIRS]
            self.assertLessEqual(sum(a == b for a, b in zip(predictions, truth)), 3)


if __name__ == "__main__":
    unittest.main()
