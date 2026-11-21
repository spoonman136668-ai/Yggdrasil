"""G29 source-free prestate and per-head plasticity negative controls."""
from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path
import sys
import unittest

HERE = Path(__file__).resolve().parents[1] / "research/contrib/chatgpt/CAUSAL-AMALGAM"
sys.path.insert(0, str(HERE))
SPEC = spec_from_file_location("g29_update_projection", HERE / "post_witness_projection.py")
G29 = module_from_spec(SPEC)
SPEC.loader.exec_module(G29)
FIX = spec_from_file_location(
    "g29_prior_g25_fixture", Path(__file__).with_name(
        "test_amalgam_headwise_consolidation.py"))
BASE = module_from_spec(FIX)
FIX.loader.exec_module(BASE)


class ProjectionTests(unittest.TestCase):
    def setUp(self):
        self.anchor = BASE._Core(BASE._history())
        self.before = self.anchor.clone()
        row = ("consumed-24", ((0, 0), (0, 1)), 0, 0, 0, 0)
        self.after = self.before.clone(BASE._history() + (row,))
        for head in self.after._heads:
            head.steps += 3

    def test_safe_zero_update_and_all_heads_result(self):
        checkpoint = (self.anchor.checkpoint(), self.before.checkpoint(),
                      self.after.checkpoint())
        heads, report = G29.assess_one_more_witness(
            self.anchor, self.before, self.after)
        self.assertEqual(len(heads), 4)
        self.assertTrue(report["all_old_heads_within_comparison"])
        self.assertTrue(report["both_transition_heads_nonzero"])
        self.assertEqual([v["alpha"] for v in report["heads"].values()],
                         [1.0] * 4)
        self.assertFalse(report["next_event_label_used_to_select_alpha"])
        self.assertFalse(report["scientific_pass"])
        self.assertEqual(checkpoint, (
            self.anchor.checkpoint(), self.before.checkpoint(),
            self.after.checkpoint()))

    def test_bounded_head_rejects_full_weight_drift_but_other_heads_continue(self):
        self.after._heads[0].predictor_bias = [-3.0, 3.0]
        heads, report = G29.assess_one_more_witness(
            self.anchor, self.before, self.after)
        self.assertEqual(report["heads"]["direct_transition"]["alpha"], 0.0)
        self.assertEqual(heads[0].predictor_bias,
                         self.before._heads[0].predictor_bias)
        self.assertEqual(heads[0].steps, self.after._heads[0].steps)
        self.assertEqual(report["heads"]["direct_reward"]["alpha"], 1.0)

    def test_forged_prefix_or_second_event_rejected(self):
        bad = self.after.clone()
        rows = list(bad.native._ledger)
        rows[0] = ("forged",) + rows[0][1:]
        bad.native._ledger = tuple(rows)
        with self.assertRaisesRegex(ValueError, "G29_ONE_WITNESS_PREFIX"):
            G29.assess_one_more_witness(self.anchor, self.before, bad)
        double = self.after.clone()
        double.native._ledger += (double.native._ledger[-1],)
        with self.assertRaisesRegex(ValueError, "G29_ONE_WITNESS_PREFIX"):
            G29.assess_one_more_witness(self.anchor, self.before, double)

    def test_prestate_retention_violation_fails_closed(self):
        bad_pre = self.before.clone()
        bad_pre._heads[0].predictor_bias = [-3.0, 3.0]
        bad_post = bad_pre.clone(self.after.native._ledger)
        for h in bad_post._heads:
            h.steps += 3
        with self.assertRaisesRegex(ValueError, "G29_PRESTATE_RETENTION_BREACH"):
            G29.assess_one_more_witness(self.anchor, bad_pre, bad_post)

    def test_wrong_head_class_or_step_count_rejected(self):
        swapped = self.after.clone()
        swapped._heads = swapped._heads[::-1]
        with self.assertRaisesRegex(ValueError, "HEAD4_HEAD_IDENTITY"):
            G29.assess_one_more_witness(self.anchor, self.before, swapped)
        skipped = self.after.clone()
        skipped._heads[1].steps -= 1
        with self.assertRaisesRegex(ValueError, "G29_HEAD_UPDATE_STEPS"):
            G29.assess_one_more_witness(self.anchor, self.before, skipped)

    def test_frozen_four_sample_summarizer_is_not_automatic_gain(self):
        samples = []
        for ordinal in (1, 32, 33, 64):
            samples.append({"ordinal": ordinal, "analysis": {
                "all_old_heads_within_comparison": True,
                "both_transition_heads_nonzero": False,
                "transition_mean_next_postfit_brier_better_than_frozen": True}})
        summary = G29.summarize_four_frozen_samples(samples)
        self.assertEqual(summary["development_classification"],
                         "DEV_MIXED_OR_NO_GO")
        self.assertFalse(summary["scientific_pass"])
        samples[0]["ordinal"] = 2
        with self.assertRaisesRegex(ValueError, "G29_SAMPLE_ORDINALS"):
            G29.summarize_four_frozen_samples(samples)


if __name__ == "__main__":
    unittest.main()
