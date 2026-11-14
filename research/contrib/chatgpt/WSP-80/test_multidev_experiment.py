"""WSP80 unregistered 8-world developer cohort negative/custody tests only.

No source.World instance is constructed; no registered or developmental
experimental observations are consumed by these unit tests.
"""
from pathlib import Path
from unittest import TestCase
import json
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))
from multidev_experiment import (
    DEVELOPMENT, PROTECTED, FROZEN_DEV_PREREG_COMMIT, FROZEN_DEV_PREREG_BLOB,
    FROZEN_REGISTERED_PREREG_BLOB, roles_channels, diagnostic_classification,
    validate_source_custody,
)


class EightWorldDeveloperAdmission(TestCase):
    @classmethod
    def setUpClass(cls):
        cls.frozen = json.loads(Path(__file__).with_name(
            "dev_multi_prereg.json").read_text(encoding="utf-8"))

    def test_protocol_committed_first_and_exact_frozen_tree_proof(self):
        custody = validate_source_custody()
        self.assertEqual(custody["developer_protocol_first_commit"],
                         FROZEN_DEV_PREREG_COMMIT)
        self.assertEqual(custody["blobs"][
            "research/contrib/chatgpt/WSP-80/dev_multi_prereg.json"],
                         FROZEN_DEV_PREREG_BLOB)
        self.assertEqual(custody["blobs"][
            "research/contrib/chatgpt/WSP-80/prereg.json"],
                         FROZEN_REGISTERED_PREREG_BLOB)

    def test_all_families_and_seeds_exact_frozen_developer_only(self):
        self.assertEqual(list(DEVELOPMENT), [
            (x["seed"], x["family"]) for x in self.frozen["source"]["cohort"]])
        self.assertEqual(len(DEVELOPMENT), 8)
        self.assertFalse(set(s for s, _ in DEVELOPMENT) & PROTECTED)
        self.assertEqual(self.frozen["source"]["paid_action_budget_all_worlds"],
                         8 * 2 * 384)
        self.assertFalse(
            self.frozen["authority"]["registered_first_use"])

    def test_shuffled_roles_are_repeatable_and_domain_separated(self):
        results = []
        for seed, family in DEVELOPMENT:
            first = roles_channels(seed, family)
            second = roles_channels(seed, family)
            self.assertEqual(first, second)
            for perm in first:
                self.assertEqual(sorted(perm), list(range(6)))
            results.append(first)
        self.assertGreater(len(set(results)), 4)

    def test_every_registered_or_out_of_cohort_source_rejected(self):
        for seed in range(5601, 5617):
            with self.assertRaises(PermissionError):
                roles_channels(seed, "quartic_positive")
        for seed in (9001, 9100, 9109, 10000):
            with self.assertRaises(PermissionError):
                roles_channels(seed, "quartic_positive")
        with self.assertRaises(PermissionError):
            roles_channels(9101, "quartic_complemented")

    def test_frozen_diagnostics_are_not_success_by_construction(self):
        records = []
        for seed, family in DEVELOPMENT:
            # Synthetic classification receipt, not a simulation or model test.
            scores = {model: {
                "correct": 200, "wrong_confident": 0,
                "abstain": 184, "never_paid_correct": 80,
                "two_action_correct": 20}
                for model in ("candidate", "fixed_degree3",
                              "random_candidate", "mlp_matched")}
            records.append({
                "seed": seed, "family": family, "metrics": scores,
                "paid_incompatible_action_count": 0,
                "symbolic_matches_candidate_all_public": 1,
                "adam_converged": True,
                "stageA_correct_retained": 5,
                "stageA_preverified_confident_correct": 5})
        fail = diagnostic_classification(records, self.frozen)
        self.assertEqual(fail["classification"],
                         "DEV_MULTIWORLD_DIAGNOSTICS_NEGATIVE")
        self.assertFalse(fail["checks"]["quartic_paid_incompatibility"])
        self.assertFalse(fail["checks"]["quartic_gain_over_fixed"])
        self.assertFalse(fail["checks"]["gain_vs_matched_MLP"])
        # Preserve the original frozen threshold; diagnostic cannot self-pass.
        self.assertEqual(self.frozen["predeclared_development_diagnostics"][
            "quartic_worlds_with_paid_incompatibility_min"], 1)

    def test_no_registered_generator_or_new_authority_path(self):
        code = Path(__file__).with_name("multidev_experiment.py").read_text("utf8")
        self.assertNotIn("build_world(", code)
        self.assertNotIn("source.build_world", code)
        self.assertNotIn("scientific_first_use=True", code)
        self.assertIn("World(seed, family, roles, channels)", code)
        self.assertIn("score_frozen(frozen[\"prelabel\"]", code)


if __name__ == "__main__":
    import unittest
    unittest.main()
