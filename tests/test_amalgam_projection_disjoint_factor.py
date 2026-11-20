"""Source-free negative control for nuisance-factor planning blind spots.

Exercises the existing, unmodified NativeEpisodeExperience and production
_two_stage_plan rather than installing another learner/owner/controller.
"""
from importlib.util import spec_from_file_location, module_from_spec
from pathlib import Path
import unittest

HERE = (Path(__file__).resolve().parents[1] /
        "research/contrib/chatgpt/CAUSAL-AMALGAM")
SPEC = spec_from_file_location(
    "projection_disjoint_factor_audit_for_tests",
    HERE / "projection_disjoint_factor_audit.py")
AUDIT = module_from_spec(SPEC)
SPEC.loader.exec_module(AUDIT)


class ProjectionDisjointFactorTests(unittest.TestCase):
    def test_native_context_projection_cannot_use_public_second_factor(self):
        result = AUDIT.evaluate(disjoint=True)
        self.assertTrue(result["source_free_fixture"])
        self.assertEqual(result["witnesses"], 16)
        self.assertEqual(result["projection"], 0)
        self.assertTrue(result["same_native_context_forecast_across_secondary_bit"])
        self.assertTrue(result["same_native_two_stage_plan_across_secondary_bit"])
        self.assertEqual(len(set(
            result["native_terminal_actions_by_public_secondary_bit"])), 1)

    def test_equal_information_strong_baseline_can_choose_each_relevant_action(self):
        result = AUDIT.evaluate(disjoint=True)
        self.assertEqual(
            result["same_fit_public_count_control_actions"], [0, 1])
        self.assertEqual(result["native_equal_context_reward"], "1/2")
        self.assertEqual(result["fully_fitted_public_count_reward"], "1")
        self.assertFalse(result["scientific_pass"])

    def test_same_law_negative_control_removes_the_gap(self):
        result = AUDIT.evaluate(disjoint=False)
        self.assertEqual(
            result["same_fit_public_count_control_actions"], [0, 0])
        self.assertEqual(result["fully_fitted_public_count_reward"], "1")
        self.assertEqual(result["native_equal_context_reward"], "1")
        self.assertTrue(result["same_native_two_stage_plan_across_secondary_bit"])

    def test_frozen_16_source_free_witness_rows_have_no_family_label(self):
        records = list(AUDIT.witness_records(disjoint=True))
        self.assertEqual(len(records), 16)
        self.assertEqual(len({event[0] for event in records}), 16)
        self.assertEqual(
            {tuple(row) for _, _, row in records},
            {("s1", "x1", "s2", "x2", "y")})
        self.assertEqual({views[0][0] for _, views, _ in records}, {0})
        self.assertEqual({views[1][0] for _, views, _ in records}, {0})
        self.assertEqual({views[0][1] for _, views, _ in records}, {0, 1})
        self.assertTrue(all(views[0][1] != views[1][1]
                            for _, views, _ in records))
        for _, views, row in records:
            self.assertEqual(row["y"], int(row["x2"] == views[0][1]))
            self.assertEqual(row["s2"], 0)

    def test_result_explicitly_denies_real_science_or_model_mutations(self):
        for case in (True, False):
            with self.subTest(case=case):
                report = AUDIT.evaluate(disjoint=case)
                self.assertEqual(report["original_world_source_actions"], 0)
                self.assertEqual(report["canonical_checkpoint_mutations"], 0)
                self.assertFalse(report["model_promoted"])
                self.assertFalse(report["old_checkpoint_or_witnesses_modified"])
                self.assertEqual(report["decision_authority"],
                                 "NONE_RESEARCH_FIXTURE_ONLY")
                self.assertFalse(report["scientific_pass"])

    def test_invalid_fixture_kind_rejected(self):
        for invalid in (None, 1, "true"):
            with self.subTest(invalid=invalid):
                with self.assertRaisesRegex(ValueError,
                                            "PROJECTION_FIXTURE_KIND"):
                    list(AUDIT.witness_records(disjoint=invalid))

    def test_reproducible_fixture_receipt(self):
        self.assertEqual(AUDIT.audit(), AUDIT.audit())
        self.assertTrue(AUDIT.audit()["disjoint"]["causally_relevant_secondary_bit"])
        self.assertFalse(AUDIT.audit()["same_law_negative"]["causally_relevant_secondary_bit"])


if __name__ == "__main__":
    unittest.main()
