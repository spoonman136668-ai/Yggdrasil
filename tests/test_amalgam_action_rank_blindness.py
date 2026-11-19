"""Source-free hidden-family oracle-vs-learner information negative controls."""
from copy import deepcopy
from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path
import sys
import unittest
from unittest.mock import patch

HERE = Path(__file__).resolve().parents[1] / "research/contrib/chatgpt/CAUSAL-AMALGAM"
SPEC = spec_from_file_location("amalgam_hidden_family_for_tests",
                               HERE / "action_rank_blindness.py")
AUDIT = module_from_spec(SPEC)
with patch.object(sys, "path", [str(HERE), *sys.path]):
    SPEC.loader.exec_module(AUDIT)


def blind_twins():
    # Identical public prefix, two latent families with opposite oracle ranks.
    return [
        {"family_id": "family-A", "prior": "1/2",
         "old": ["1/10", "1/2"], "new": ["9/10", "1/2"]},
        {"family_id": "family-B", "prior": "1/2",
         "old": ["1/2", "1/10"], "new": ["1/2", "9/10"]},
    ]


class HiddenFamilyFirstProbeTests(unittest.TestCase):
    def test_oracle_rank_reverses_but_blind_first_actions_tie(self):
        x = AUDIT.audit_hidden_family_first_probe(
            blind_twins(), identical_public_prefix=True)
        self.assertTrue(x["oracle_action_rank_reverses"])
        self.assertEqual(x["blind_best_first_action"], None)
        self.assertAlmostEqual(x["blind_action_information_nats"][0],
                               x["blind_action_information_nats"][1], places=13)
        self.assertAlmostEqual(x["blind_action_information_nats"][0],
                               0.08228287850505178, places=12)
        self.assertAlmostEqual(x["conditional_oracle_information_nats"],
                               0.3680642071684971, places=12)
        self.assertAlmostEqual(x["oracle_information_advantage_nats"],
                               0.2857813286634453, places=12)
        self.assertEqual([f["evaluator_only_best_action"]
                          for f in x["oracle_family_information"]], [0, 1])
        self.assertEqual(x["scope"],
                         "SINGLE_BLIND_FIRST_PROBE_REGIME_INFORMATION_NOT_FUTURE_CONTROL")

    def test_no_first_use_or_policy_or_science_authority(self):
        x = AUDIT.audit_hidden_family_first_probe(
            blind_twins(), identical_public_prefix=True)
        for field in ("public_prefix_equivalence_independently_verified",
                      "source_identity_authenticated",
                      "learner_causal_action_selection_improved",
                      "first_use_allowed", "scientific_pass"):
            self.assertIs(x[field], False)
        self.assertEqual(x["source_actions"], 0)
        self.assertEqual(x["training_updates"], 0)
        self.assertEqual(x["decision_authority"], "NONE_EVALUATOR_DESIGN_ONLY")

    def test_source_blind_action_can_genuinely_have_strict_information_rank(self):
        families = [
            {"family_id": "A", "prior": "1/2",
             "old": ["1/10", "1/2"], "new": ["9/10", "1/2"]},
            {"family_id": "B", "prior": "1/2",
             "old": ["1/5", "1/2"], "new": ["4/5", "1/2"]},
        ]
        x = AUDIT.audit_hidden_family_first_probe(
            families, identical_public_prefix=True)
        self.assertFalse(x["oracle_action_rank_reverses"])
        self.assertEqual(x["blind_best_first_action"], 0)
        self.assertGreater(x["blind_first_action_information_gap_nats"], 0.2)
        self.assertEqual(x["blind_action_information_nats"][1], 0)

    def test_unobservable_family_is_not_claimed_known_by_any_flag(self):
        x = AUDIT.audit_hidden_family_first_probe(
            blind_twins(), identical_public_prefix=True)
        self.assertFalse(x["public_prefix_equivalence_independently_verified"])
        self.assertTrue(x["oracle_information_advantage_nats"] > 0.28)

    def test_true_public_family_cue_requires_different_protocol(self):
        with self.assertRaisesRegex(
                ValueError, "ACTION_IDENTIFIABILITY_PUBLIC_PREFIX_NOT_PROVEN_BY_THIS_TOOL"):
            AUDIT.audit_hidden_family_first_probe(
                blind_twins(), identical_public_prefix=False)

    def test_claimed_public_prefix_must_be_literal_true(self):
        for invalid in (1, None, "true"):
            with self.subTest(invalid=invalid):
                with self.assertRaisesRegex(
                        ValueError, "ACTION_IDENTIFIABILITY_PUBLIC_PREFIX_NOT_PROVEN"):
                    AUDIT.audit_hidden_family_first_probe(
                        blind_twins(), identical_public_prefix=invalid)

    def test_family_priors_must_sum_to_one(self):
        sample = blind_twins()
        sample[0]["prior"] = "1/4"
        with self.assertRaisesRegex(ValueError,
                                    "ACTION_IDENTIFIABILITY_FAMILY_PRIORS_NOT_NORMALIZED"):
            AUDIT.audit_hidden_family_first_probe(
                sample, identical_public_prefix=True)

    def test_zero_prior_fails_and_never_claims_a_source_family(self):
        sample = blind_twins()
        sample[0]["prior"] = "0/1"
        with self.assertRaisesRegex(ValueError, "ACTION_IDENTIFIABILITY_FAMILY_PRIOR"):
            AUDIT.audit_hidden_family_first_probe(
                sample, identical_public_prefix=True)

    def test_invalid_binary_law_rejected(self):
        sample = blind_twins()
        sample[1]["new"].append("1/2")
        with self.assertRaisesRegex(ValueError, "ACTION_IDENTIFIABILITY_BINARY_PROBE_LAW"):
            AUDIT.audit_hidden_family_first_probe(
                sample, identical_public_prefix=True)

    def test_duplicate_family_claim_rejected(self):
        sample = blind_twins()
        sample[1]["family_id"] = sample[0]["family_id"]
        with self.assertRaisesRegex(ValueError, "ACTION_IDENTIFIABILITY_FAMILY_ID"):
            AUDIT.audit_hidden_family_first_probe(
                sample, identical_public_prefix=True)

    def test_prohibited_probability_or_float_rejected(self):
        sample = blind_twins()
        sample[0]["old"][0] = "11/10"
        with self.assertRaisesRegex(ValueError, "ACTION_IDENTIFIABILITY_PROBABILITY_RANGE"):
            AUDIT.audit_hidden_family_first_probe(sample, identical_public_prefix=True)
        sample = blind_twins()
        sample[0]["old"][0] = 0.1
        with self.assertRaisesRegex(ValueError, "ACTION_IDENTIFIABILITY_RATIONAL"):
            AUDIT.audit_hidden_family_first_probe(sample, identical_public_prefix=True)

    def test_reordering_families_does_not_produce_new_evidence(self):
        sample = blind_twins()
        left = AUDIT.audit_hidden_family_first_probe(
            sample, identical_public_prefix=True)
        right = AUDIT.audit_hidden_family_first_probe(
            sample[::-1], identical_public_prefix=True)
        self.assertEqual(left["blind_action_information_nats"],
                         right["blind_action_information_nats"])
        self.assertAlmostEqual(left["conditional_oracle_information_nats"],
                               right["conditional_oracle_information_nats"])
        self.assertFalse(left["scientific_pass"])

    def test_inputs_unmodified_by_evaluator(self):
        sample = blind_twins()
        before = deepcopy(sample)
        x = AUDIT.audit_hidden_family_first_probe(
            sample, identical_public_prefix=True)
        self.assertEqual(sample, before)
        self.assertFalse(x["source_identity_authenticated"])

    def test_family_count_fails_closed(self):
        with self.assertRaisesRegex(ValueError, "ACTION_IDENTIFIABILITY_HIDDEN_FAMILY_LIST"):
            AUDIT.audit_hidden_family_first_probe(
                blind_twins()[:1], identical_public_prefix=True)


if __name__ == "__main__":
    unittest.main()
