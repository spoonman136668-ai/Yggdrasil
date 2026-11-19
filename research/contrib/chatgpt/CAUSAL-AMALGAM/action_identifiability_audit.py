"""Pure read-only prospective causal-source suitability check.

This is an evaluator-side *design proof obligation*, never an original-source
actor, model training function, source-owner admission, or learner API.  Its
input matrices are DECLARED oracle/source probabilities, not observed held
labels.  Unauthenticated claims and generated test fixtures can be analyzed
for mathematical consistency but never earn original-world first-use or
scientific acceptance.
"""
from fractions import Fraction
import json
from math import log
from pathlib import Path
import re

HERE = Path(__file__).resolve().parent
PROTOCOL = HERE / "action_identifiability_prereg.json"
HEX40 = re.compile(r"[0-9a-f]{40}\Z")
HEX64 = re.compile(r"[0-9a-f]{64}\Z")
TOKEN = re.compile(r"[A-Za-z0-9][A-Za-z0-9_.:/-]{0,127}\Z")
SPLITS = ("TRANSFER_CHANGED", "TRANSFER_UNCHANGED")
SCHEMA = "yggdrasil.amalgam.action-identifiability-design-candidate.v1"


def require(ok, error):
    if not ok:
        raise ValueError("ACTION_IDENTIFIABILITY_" + error)


def _fraction(value):
    require(type(value) is str and
            re.fullmatch(r"(?:0|[1-9][0-9]{0,11})/[1-9][0-9]{0,11}", value)
            is not None, "RATIONAL")
    num, den = (int(v) for v in value.split("/"))
    require(num <= den, "PROBABILITY_RANGE")
    # Using exact rational input prevents accidental acceptance of a
    # rounded-tie mechanism as a different held law.
    return Fraction(num, den)


def _entropy(p):
    p = float(p)
    if p == 0 or p == 1:
        return 0.0
    return -p * log(p) - (1.0 - p) * log(1.0 - p)


def _js_binary(a, b):
    """Equal-prior binary-regime Jensen-Shannon information in nats."""
    return _entropy((a + b) / 2) - (_entropy(a) + _entropy(b)) / 2


def audit_candidate(candidate, prereg=None):
    """Audit declared source laws without interacting with any environment.

    The pre-use source owner MUST separately verify novelty, repository blobs,
    license, authenticated untouched rosters, actor, lease, and GO readback.
    Even a mechanically suitable declaration is not scientific evidence or
    source admission.  This method has no executable-effect capabilities.
    """
    if prereg is None:
        prereg = json.loads(PROTOCOL.read_bytes())
    require(type(prereg) is dict and
            prereg.get("schema") == "yggdrasil.amalgam.action-identifiability-design.v1"
            and prereg.get("source_first_use_allowed") is False
            and prereg.get("owner_gate", {}).get("state") == "NOT_AUTHORIZED"
            and prereg.get("owner_gate", {}).get("source_actions_authorized_by_this_protocol") == 0,
            "FROZEN_SOURCE_FENCE")
    policy = prereg["design_certificate"]
    costs = prereg["proposed_science"]["budgets"]
    require(policy["require_action_rank_reversal"] is True and
            policy["min_changed_distinct_mechanism_families"] >= 4 and
            policy["min_unchanged_control_families"] >= 2 and
            costs["no_source_actions_before_owner_live_go"] is True,
            "FROZEN_PROTOCOL")
    effect = _fraction(policy["min_changed_held_cell_effect"])
    asymmetry = float(_fraction(policy["min_information_asymmetry_nats"]))
    require(0 < effect <= 1 and 0 < asymmetry < log(2),
            "DESIGN_MINIMUM_INVALID")

    require(type(candidate) is dict and set(candidate) == {
        "schema", "declared_source_commit", "declared_source_blob_sha256",
        "declared_evaluator_manifest_sha256", "owner_admission", "cells"},
        "CANDIDATE_SCHEMA")
    require(candidate["schema"] == SCHEMA and
            candidate["owner_admission"] == "ABSENT_EXTERNAL_OWNER_UNVERIFIED",
            "CANDIDATE_MUST_REMAIN_DISARMED")
    require(type(candidate["declared_source_commit"]) is str and
            HEX40.fullmatch(candidate["declared_source_commit"]) is not None and
            all(type(candidate[k]) is str and HEX64.fullmatch(candidate[k])
                for k in ("declared_source_blob_sha256",
                          "declared_evaluator_manifest_sha256")),
            "SOURCE_PINS_DECLARED_NOT_VERIFIED")
    cells = candidate["cells"]
    require(type(cells) is list and 0 < len(cells) <= 64,
            "CELL_COUNT")

    kinds = {"TRANSFER_CHANGED": set(), "TRANSFER_UNCHANGED": set()}
    seen_worlds = set()
    world_owner = {}
    seed_owner = {}
    seen_mechanism_hashes = set()
    evidence_families = {}
    winning_actions = set()
    reported = []
    budget = 0

    for entry in cells:
        require(type(entry) is dict and set(entry) == {
            "family_id", "mechanism_sha256", "world_id", "seed_id",
            "split", "context_id", "held_action", "old", "new",
            "per_arm_action_cap", "evaluator_only"},
            "CELL_SHAPE")
        require(all(type(entry[k]) is str and
                    TOKEN.fullmatch(entry[k]) is not None
                    for k in ("family_id", "world_id", "context_id")),
                "CELL_IDENTITY")
        require(type(entry["seed_id"]) is int and entry["seed_id"] >= 0 and
                entry["seed_id"] not in prereg["source_boundaries"]["consumed_mdp_original_seeds"],
                "CONSUMED_OR_INVALID_SEED")
        require(type(entry["mechanism_sha256"]) is str and
                HEX64.fullmatch(entry["mechanism_sha256"]) is not None,
                "MECHANISM_DECLARATION")
        require(entry["split"] in SPLITS and
                type(entry["held_action"]) is int and
                entry["held_action"] in (0, 1) and
                entry["evaluator_only"] is True,
                "SPLIT_ACTION_OR_VISIBILITY")
        cap = entry["per_arm_action_cap"]
        require(type(cap) is int and 0 <= cap <= costs["per_family_per_arm_actual_actions_cap"],
                "PER_FAMILY_ACTION_CAP")
        budget += cap
        key = (entry["world_id"], entry["context_id"])
        require(key not in seen_worlds, "DUPLICATE_WORLD_CONTEXT")
        seen_worlds.add(key)
        family = entry["family_id"]
        world_identity = (family, entry["split"], entry["seed_id"])
        prior_world = world_owner.get(entry["world_id"])
        require(prior_world is None or prior_world == world_identity,
                "WORLD_COHORT_CONFLICT")
        world_owner[entry["world_id"]] = world_identity
        prior_seed = seed_owner.get(entry["seed_id"])
        require(prior_seed is None or prior_seed == entry["world_id"],
                "SEED_ASSIGNED_MULTIPLE_WORLDS")
        seed_owner[entry["seed_id"]] = entry["world_id"]
        signature = entry["mechanism_sha256"]
        old = entry["old"]
        new = entry["new"]
        require(type(old) is list and type(new) is list and
                len(old) == len(new) == 2,
                "TWO_SOURCE_NATIVE_ACTIONS_REQUIRED")
        p0, p1 = (_fraction(x) for x in old)
        q0, q1 = (_fraction(x) for x in new)
        held_delta = abs((q0, q1)[entry["held_action"]] -
                         (p0, p1)[entry["held_action"]])
        info = (_js_binary(p0, q0), _js_binary(p1, q1))
        ranking = info[0] - info[1]
        if entry["split"] == "TRANSFER_CHANGED":
            require(held_delta >= effect, "HELD_LAW_UNCHANGED")
            require(abs(ranking) >= asymmetry, "ACTION_INFORMATION_TIE")
            winning_actions.add(0 if ranking > 0 else 1)
        else:
            require(p0 == q0 and p1 == q1, "NEGATIVE_CONTROL_CHANGED")
            require(info[0] == 0 and info[1] == 0,
                    "NEGATIVE_CONTROL_NOT_NULL")

        prior = evidence_families.get(family)
        require(prior is None or prior == (signature, entry["split"]),
                "FAMILY_CONTRACT_CONFLICT")
        if prior is None:
            require(signature not in seen_mechanism_hashes,
                    "SAME_MECHANISM_CLAIMED_AS_DIFFERENT_FAMILY")
            seen_mechanism_hashes.add(signature)
            evidence_families[family] = (signature, entry["split"])
        kinds[entry["split"]].add(family)
        reported.append({
            "family_id": family,
            "world_id": entry["world_id"],
            "context_id": entry["context_id"],
            "split": entry["split"],
            "held_action_effect": str(held_delta),
            "equal_prior_action_information_nats": [round(v, 12) for v in info],
            "most_informative_action": (0 if ranking > 0 else 1) if ranking else None,
            "oracle_declarations_are_verified": False,
        })

    require(len(kinds["TRANSFER_CHANGED"]) >=
            policy["min_changed_distinct_mechanism_families"],
            "INSUFFICIENT_CHANGED_FAMILIES")
    require(len(kinds["TRANSFER_UNCHANGED"]) >=
            policy["min_unchanged_control_families"],
            "INSUFFICIENT_NEGATIVE_FAMILIES")
    require(winning_actions == {0, 1}, "NO_ACTION_INFORMATION_RANK_REVERSAL")
    # Every compared arm consumes its own source actions; per-arm budgeting
    # alone would understate the true source cost if used as a future plan.
    arms = prereg["proposed_science"]["arms"]
    require(type(arms) is list and len(arms) >= 2 and
            all(type(arm) is str and TOKEN.fullmatch(arm) is not None
                for arm in arms) and len(set(arms)) == len(arms),
            "CONTROL_ARM_CONTRACT")
    total_budget = budget * len(arms)
    require(total_budget <= costs["total_source_action_ceiling_not_authorization"],
            "SOURCE_CEILING_EXCEEDED")
    return {
        "schema": "yggdrasil.amalgam.action-identifiability-design-audit.v1",
        "declared_mechanical_design_suitable": True,
        "declared_changed_families": len(kinds["TRANSFER_CHANGED"]),
        "declared_unchanged_controls": len(kinds["TRANSFER_UNCHANGED"]),
        "both_actions_need_conditional_selection": True,
        "declared_action_budget_sum_per_arm_not_approval": budget,
        "declared_control_arms": len(arms),
        "declared_total_action_budget_all_arms_not_approval": total_budget,
        "cells": reported,
        "source_identity_independently_verified": False,
        "novelty_independently_verified": False,
        "original_source_actions_performed": 0,
        "first_use_allowed": False,
        "scientific_pass": False,
        "model_training_performed": False,
        "decision_authority": "NONE_DESIGN_CHECK_ONLY",
        "deployment": "NONE",
    }
