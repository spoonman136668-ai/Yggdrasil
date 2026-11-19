"""Evaluator-side suitability tests; all matrices are synthetic declarations.

These assertions execute no original-world source, action actor, learner,
training, held label, owner authorization or checkpoint update.
"""
from copy import deepcopy
from hashlib import sha256
from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path
import json
import unittest

HERE = Path(__file__).resolve().parents[1] / "research/contrib/chatgpt/CAUSAL-AMALGAM"
SPEC = spec_from_file_location("amalgam_identifiability_design_for_tests",
                               HERE / "action_identifiability_audit.py")
AUDIT = module_from_spec(SPEC)
SPEC.loader.exec_module(AUDIT)


def hash_for(value):
    return sha256(value.encode("ascii")).hexdigest()


def cell(index, kind, winning):
    if kind == "TRANSFER_UNCHANGED":
        old = ["1/4", "3/4"]
        new = old[:]
        held = 0
    elif winning == 0:
        old = ["1/10", "1/2"]
        new = ["9/10", "1/2"]
        held = 0
    else:
        old = ["1/2", "1/10"]
        new = ["1/2", "9/10"]
        held = 1
    return {
        "family_id": f"fixture-family-{index}",
        "mechanism_sha256": hash_for(f"fixture-source-law-{index}"),
        "world_id": f"fixture-world-{index}",
        "seed_id": 771000 + index,
        "split": kind,
        "context_id": f"context-{index}",
        "held_action": held,
        "old": old,
        "new": new,
        "per_arm_action_cap": 16,
        "evaluator_only": True,
    }


def candidate():
    return {
        "schema": AUDIT.SCHEMA,
        "declared_source_commit": "c" * 40,
        "declared_source_blob_sha256": "a" * 64,
        "declared_evaluator_manifest_sha256": "b" * 64,
        "owner_admission": "ABSENT_EXTERNAL_OWNER_UNVERIFIED",
        "cells": [
            cell(0, "TRANSFER_CHANGED", 0),
            cell(1, "TRANSFER_CHANGED", 1),
            cell(2, "TRANSFER_CHANGED", 0),
            cell(3, "TRANSFER_CHANGED", 1),
            cell(4, "TRANSFER_UNCHANGED", None),
            cell(5, "TRANSFER_UNCHANGED", None),
        ],
    }


class ProspectiveActionIdentifiabilityTests(unittest.TestCase):
    def setUp(self):
        self.sample = candidate()

    def rejects(self, label):
        with self.assertRaisesRegex(ValueError, "ACTION_IDENTIFIABILITY_" + label):
            AUDIT.audit_candidate(self.sample)

    def test_frozen_design_is_statically_suitable_but_never_authorized(self):
        result = AUDIT.audit_candidate(self.sample)
        self.assertTrue(result["declared_mechanical_design_suitable"])
        self.assertEqual(result["declared_changed_families"], 4)
        self.assertEqual(result["declared_unchanged_controls"], 2)
        self.assertTrue(result["both_actions_need_conditional_selection"])
        self.assertEqual(result["declared_action_budget_sum_not_approval"], 96)
        self.assertEqual(len(result["cells"]), 6)
        self.assertEqual(result["original_source_actions_performed"], 0)
        self.assertFalse(result["first_use_allowed"])
        self.assertFalse(result["scientific_pass"])
        self.assertFalse(result["model_training_performed"])
        self.assertFalse(result["source_identity_independently_verified"])
        self.assertFalse(result["novelty_independently_verified"])
        self.assertEqual(result["decision_authority"], "NONE_DESIGN_CHECK_ONLY")

    def test_action_information_reversal_is_a_genuine_discrimination_test(self):
        x = AUDIT.audit_candidate(self.sample)
        kinds = x["cells"][:4]
        self.assertEqual([r["most_informative_action"] for r in kinds],
                         [0, 1, 0, 1])
        self.assertTrue(all(r["held_action_effect"] == "4/5" for r in kinds))
        self.assertTrue(all(max(r["equal_prior_action_information_nats"]) > 0.05
                            for r in kinds))
        self.assertTrue(all(r["equal_prior_action_information_nats"] == [0.0, 0.0]
                            for r in x["cells"][4:]))

    def test_all_changed_families_same_best_action_fails(self):
        for i in (1, 3):
            self.sample["cells"][i]["old"] = ["1/10", "1/2"]
            self.sample["cells"][i]["new"] = ["9/10", "1/2"]
            self.sample["cells"][i]["held_action"] = 0
        self.rejects("NO_ACTION_INFORMATION_RANK_REVERSAL")

    def test_original_benchmark_equal_information_actions_fail(self):
        # Each action produces an equally informative Bernoulli switch,
        # so an active chooser cannot beat the best constant action by
        # regime-discrimination information alone.
        self.sample["cells"][0]["old"] = ["1/10", "9/10"]
        self.sample["cells"][0]["new"] = ["9/10", "1/10"]
        self.rejects("ACTION_INFORMATION_TIE")

    def test_claimed_changed_held_cell_must_really_change(self):
        self.sample["cells"][0]["held_action"] = 1
        self.rejects("HELD_LAW_UNCHANGED")

    def test_below_predeclared_held_law_margin_fails(self):
        self.sample["cells"][0]["new"][0] = "1/5"
        self.rejects("HELD_LAW_UNCHANGED")

    def test_null_negative_control_must_not_contain_hidden_change(self):
        self.sample["cells"][4]["new"][0] = "1/2"
        self.rejects("NEGATIVE_CONTROL_CHANGED")

    def test_missing_changed_family_roster_fails(self):
        self.sample["cells"].pop(3)
        self.rejects("INSUFFICIENT_CHANGED_FAMILIES")

    def test_missing_unchanged_control_roster_fails(self):
        self.sample["cells"].pop(5)
        self.rejects("INSUFFICIENT_NEGATIVE_FAMILIES")

    def test_duplicate_world_and_context_fails(self):
        self.sample["cells"][1]["world_id"] = self.sample["cells"][0]["world_id"]
        self.sample["cells"][1]["context_id"] = self.sample["cells"][0]["context_id"]
        self.rejects("DUPLICATE_WORLD_CONTEXT")

    def test_duplicate_mechanism_as_another_family_fails(self):
        self.sample["cells"][1]["mechanism_sha256"] = (
            self.sample["cells"][0]["mechanism_sha256"])
        self.rejects("SAME_MECHANISM_CLAIMED_AS_DIFFERENT_FAMILY")

    def test_consumed_original_mdp_seed_fails(self):
        self.sample["cells"][0]["seed_id"] = 996100
        self.rejects("CONSUMED_OR_INVALID_SEED")

    def test_external_owner_claim_cannot_promote_this_tool(self):
        self.sample["owner_admission"] = "GO"
        self.rejects("CANDIDATE_MUST_REMAIN_DISARMED")

    def test_missing_source_identity_fails(self):
        self.sample["declared_source_commit"] = "not-a-source-pin"
        self.rejects("SOURCE_PINS_DECLARED_NOT_VERIFIED")

    def test_unsupported_multiaction_source_requires_new_protocol(self):
        self.sample["cells"][0]["old"].append("1/2")
        self.sample["cells"][0]["new"].append("1/2")
        self.rejects("TWO_SOURCE_NATIVE_ACTIONS_REQUIRED")

    def test_invalid_probability_and_float_rejected(self):
        self.sample["cells"][0]["old"][0] = "11/10"
        self.rejects("PROBABILITY_RANGE")
        self.sample = candidate()
        self.sample["cells"][0]["old"][0] = 0.1
        self.rejects("RATIONAL")

    def test_candidate_cannot_override_preregistered_gate(self):
        self.sample["source_first_use_allowed"] = True
        self.rejects("CANDIDATE_SCHEMA")
        self.sample.pop("source_first_use_allowed")
        config = json.loads(AUDIT.PROTOCOL.read_bytes())
        config["source_first_use_allowed"] = True
        with self.assertRaisesRegex(ValueError, "ACTION_IDENTIFIABILITY_FROZEN_SOURCE_FENCE"):
            AUDIT.audit_candidate(self.sample, prereg=config)

    def test_action_budget_cannot_exceed_frozen_per_family_limit(self):
        self.sample["cells"][0]["per_arm_action_cap"] = 129
        self.rejects("PER_FAMILY_ACTION_CAP")

    def test_non_evaluator_input_is_rejected(self):
        self.sample["cells"][0]["evaluator_only"] = False
        self.rejects("SPLIT_ACTION_OR_VISIBILITY")

    def test_design_is_pure_and_deterministic(self):
        before = deepcopy(self.sample)
        a = AUDIT.audit_candidate(self.sample)
        b = AUDIT.audit_candidate(self.sample)
        self.assertEqual(self.sample, before)
        self.assertEqual(a, b)
        self.assertFalse(a["first_use_allowed"])


if __name__ == "__main__":
    unittest.main()
