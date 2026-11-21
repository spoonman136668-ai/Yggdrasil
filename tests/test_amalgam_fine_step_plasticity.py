"""G30 frozen-finer-grid source-free guard and zero-learning controls."""
from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path
import sys
import unittest

HERE = Path(__file__).resolve().parents[1] / "research/contrib/chatgpt/CAUSAL-AMALGAM"
sys.path.insert(0, str(HERE))
SPEC = spec_from_file_location("g30_fixed_refinement", HERE / "fine_step_plasticity.py")
G30 = module_from_spec(SPEC)
SPEC.loader.exec_module(G30)
FIX = spec_from_file_location(
    "g30_reused_fixture", Path(__file__).with_name(
        "test_amalgam_headwise_consolidation.py"))
BASE = module_from_spec(FIX)
FIX.loader.exec_module(BASE)


class FixedRefinementTests(unittest.TestCase):
    def setUp(self):
        self.anchor = BASE._Core(BASE._history())
        self.before = self.anchor.clone()
        new = ("consumed", ((0, 0), (0, 1)), 0, 0, 0, 0)
        self.after = self.before.clone(BASE._history() + (new,))
        for h in self.after._heads:
            h.steps += 3

    def test_frozen_alphas_not_user_selectable(self):
        self.assertEqual(G30.FINE_ALPHAS,
                         (1., .5, .25, .125, .0625, .03125, .015625, 0.))
        for value in (.03, .75, 0, "0.125", float("nan"), 0.1):
            with self.subTest(alpha=str(value)):
                with self.assertRaisesRegex(ValueError, "G30_ALPHA_NOT_FROZEN"):
                    G30._blend_fine(
                        self.before._heads[0], self.after._heads[0], value)

    def test_fake_step_update_never_called_real_learning(self):
        originals = tuple(m.checkpoint() for m in (
            self.anchor, self.before, self.after))
        heads, report = G30.evaluate_fine_steps(
            self.anchor, self.before, self.after)
        self.assertEqual(len(heads), 4)
        self.assertTrue(report["all_old_heads_within_original_bound"])
        self.assertFalse(report["both_transitions_have_real_weight_updates"])
        self.assertFalse(report["scientific_pass"])
        self.assertEqual(tuple(m.checkpoint() for m in (
            self.anchor, self.before, self.after)), originals)

    def test_rejects_duplicate_or_mismatched_prefix(self):
        fake = self.after.clone()
        fake.native._ledger += (fake.native._ledger[-1],)
        with self.assertRaisesRegex(ValueError, "G29_ONE_WITNESS_PREFIX"):
            G30.evaluate_fine_steps(self.anchor, self.before, fake)
        fake = self.after.clone()
        fake.native._ledger = (("other",) + fake.native._ledger[0][1:],) + (
            fake.native._ledger[1:])
        with self.assertRaisesRegex(ValueError, "G29_ONE_WITNESS_PREFIX"):
            G30.evaluate_fine_steps(self.anchor, self.before, fake)

    def test_old_prestate_breach_fail_closed(self):
        altered = self.before.clone()
        altered._heads[0].predictor_bias = [-3.0, 3.0]
        following = altered.clone(self.after.native._ledger)
        for h in following._heads:
            h.steps += 3
        with self.assertRaisesRegex(ValueError, "G29_PRESTATE_RETENTION_BREACH"):
            G30.evaluate_fine_steps(self.anchor, altered, following)

    def test_nonfinite_and_missing_training_step_rejected(self):
        fake = self.after.clone()
        fake._heads[1].steps -= 1
        with self.assertRaisesRegex(ValueError, "G29_HEAD_UPDATE_STEPS"):
            G30.evaluate_fine_steps(self.anchor, self.before, fake)
        fake = self.after.clone()
        fake._heads[1].predictor_bias[0] = float("nan")
        with self.assertRaises(ValueError):
            G30.evaluate_fine_steps(self.anchor, self.before, fake)

    def test_four_case_rule_rejects_missing_and_no_learning(self):
        samples = [{"ordinal":n, "analysis": {
            "all_old_heads_within_original_bound": True,
            "both_transitions_have_real_weight_updates": False,
            "transition_next_postfit_better_than_frozen": False,
            "transition_next_postfit_better_than_coarse": False,
            "transition_next_postfit_not_worse_than_coarse": True,
        }} for n in G30.FROZEN_ORDINALS]
        report = G30.summarize_fine_samples(samples)
        self.assertEqual(report["development_classification"],
                         "DEV_FINE_STEP_NO_GO")
        self.assertFalse(report["scientific_pass"])
        samples[0]["ordinal"] = 99
        with self.assertRaisesRegex(ValueError, "G30_FROZEN_SAMPLE_ORDER"):
            G30.summarize_fine_samples(samples)


if __name__ == "__main__":
    unittest.main()
