"""Source-safe FKP-17 preregistration invariants. Never imports a simulator.

These are contract checks only; they cannot establish scientific benefit,
Yggdrasil acceptance, or permission to first-use a held world.
"""
import json
import unittest
from pathlib import Path

PREREG = Path(__file__).with_name("prereg.json")


def read_contract():
    with PREREG.open(encoding="utf-8") as stream:
        return json.load(stream)


def require_disjoint_splits(contract):
    splits = contract["frozen_splits"]
    cohorts = {}
    for name in ("foundation", "train", "validation", "fresh_dev",
                 "transfer_reserved"):
        row = splits[name]
        lo, hi = row["world_seed_start"], row["world_seed_end"]
        assert type(lo) is int and type(hi) is int
        assert hi >= lo
        assert hi - lo + 1 == row["worlds"]
        cohorts[name] = set(range(lo, hi + 1))
    for left, s1 in cohorts.items():
        for right, s2 in cohorts.items():
            if left < right:
                assert not (s1 & s2), (left, right)
    assert not (cohorts["fresh_dev"] & set(range(976500, 976532)))
    return cohorts


def verify_source_safe_contract(p):
    assert p["schema"] == "yggdrasil.external-research-prereg.v1"
    assert p["experiment_id"] == "FKP-17-STRUCTURED-FOUNDATION-NOVEL-CAUSAL-LAWS"
    assert p["phase"] == "PROTOCOL_ONLY_BEFORE_SOURCE_IMPLEMENTATION_AND_BEFORE_NEW_FIRST_USE"
    assert p["accepted_native_main"] == "5e74f8db85b2f5839c42148c0dfba69a88b1a2c9"
    assert p["predecessor"]["scientific_pass"] is False
    cohorts = require_disjoint_splits(p)
    assert len(cohorts["fresh_dev"]) == 32 and len(cohorts["transfer_reserved"]) == 64
    assert p["frozen_splits"]["reuse_of_fkp16_dev"] is False
    arms = p["equal_information_arms"]
    assert {"STRUCTURED", "FLAT", "SHUFFLED", "MINIMAL", "NO_UPDATE",
            "BAYES_SYMBOLIC", "RECURRENT", "COUNT_RETRIEVAL"} <= set(arms)
    f = p["fairness"]
    assert f["foundation_records_each_informed_arm"] == p["frozen_splits"]["foundation"]["total_records"] == 32768
    assert f["identical_shared_exploration_tape_actions_per_world"] == 24
    assert f["held_on_policy_scored_actions_per_world"] == 16
    assert f["source_hidden_labels_not_seen_until_action_committed"] is True
    assert f["prior_information_digest_same_for_structured_flat_shuffled_bayes_recurrent_counts"] is True
    assert p["frozen_metrics"]["dev_required_absolute_gain"] >= 0.10
    assert p["frozen_metrics"]["dev_world_bootstrap_lower_95_gt"] > 0
    assert p["frozen_metrics"]["valid_dev_worlds_min"] >= 24
    fence = p["stop_and_reporting"]
    assert fence["no_protected_first_use"] is True
    assert fence["no_runner_or_scheduler_mutation"] is True
    assert fence["no_paid_api"] is True
    assert "No merge" in fence["integration"]
    assert p["source_law_separation"] if "source_law_separation" in p else True
    return True


class FrozenProtocolTests(unittest.TestCase):
    def test_readback_contract(self):
        self.assertTrue(verify_source_safe_contract(read_contract()))

    def test_reject_overlapping_held_world(self):
        p = read_contract()
        p["frozen_splits"]["fresh_dev"]["world_seed_start"] = 978200
        p["frozen_splits"]["fresh_dev"]["world_seed_end"] = 978231
        with self.assertRaises(AssertionError):
            verify_source_safe_contract(p)

    def test_reject_overlap_with_consumed_fkp16(self):
        p = read_contract()
        p["frozen_splits"]["fresh_dev"]["world_seed_start"] = 976500
        p["frozen_splits"]["fresh_dev"]["world_seed_end"] = 976531
        with self.assertRaises(AssertionError):
            verify_source_safe_contract(p)

    def test_reject_loss_of_flat_control(self):
        p = read_contract()
        del p["equal_information_arms"]["FLAT"]
        with self.assertRaises(AssertionError):
            verify_source_safe_contract(p)

    def test_reject_unmatched_prior_information(self):
        p = read_contract()
        p["fairness"]["foundation_records_each_informed_arm"] -= 1
        with self.assertRaises(AssertionError):
            verify_source_safe_contract(p)

    def test_reject_precommitted_threshold_weakening(self):
        p = read_contract()
        p["frozen_metrics"]["dev_required_absolute_gain"] = 0
        with self.assertRaises(AssertionError):
            verify_source_safe_contract(p)

    def test_reject_first_use_authority_widening(self):
        p = read_contract()
        p["stop_and_reporting"]["no_protected_first_use"] = False
        with self.assertRaises(AssertionError):
            verify_source_safe_contract(p)

    def test_reject_predecessor_science_inflation(self):
        p = read_contract()
        p["predecessor"]["scientific_pass"] = True
        with self.assertRaises(AssertionError):
            verify_source_safe_contract(p)


if __name__ == "__main__":
    unittest.main()
