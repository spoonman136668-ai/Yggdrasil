#!/usr/bin/env python3
"""F50 nine-world public-only comparison harness: pre-first-use engineering.

Only synthetic-fixture evaluators are accepted here. There is NO development
target construction, source-law oracle, hidden law import, release shortcut,
remote-execution authority or live scientific entrypoint. The future first-use
runner must bind isolated evaluator transport and authentic source checkpoints
under separate exact-SHA qualification.
"""
from hashlib import sha256
import json
import math
from time import process_time

import f50_worlds as world

SCHEMA = "yggdrasil.qtr01.f50.nine-world-preuse-harness.v1"
CHECKPOINTS = (16, 32, 64)
KINDS = (
    "native",
    "graph_conditioned_gru", "law_conditioned_set_mlp",
    "graph_conditioned_logistic",
    "exact_source_bank_bayes", "compositional_grammar_bayes",
    "random", "uniform",
    "native_no_causal_slot_retention", "native_public_outcome_shuffle",
    "native_random_proposals_equal_2048",
    "native_permuted_action_outcome_alignment",
)
TRAINED_SOURCE_KINDS = KINDS[1:4]
FIXTURE_CLASSIFICATION = "ENGINEERING_FIXTURE_ONLY_NO_SCIENTIFIC_RESULT"
MAX_CANDIDATES = 512
HELDOUT = 512


class ComparisonRejected(world.F50Rejected):
    pass


def frozen_plan():
    """Nine frozen high-first worlds; introspects only the *source* protocol."""
    prereg = world.freeze()
    task = prereg["task"]
    if (world.PREREG_BLOB != "4bd3c4e0d3de0e3910094e38c14a0141c97ad380"
        or tuple(task["source_bank_sizes_high_first"]) != world.BANK_SIZES
        or tuple(task["development_seeds"]) != world.DEV_SEEDS
        or task["development_worlds"] != 9
        or task["queries_per_arm"] != list(CHECKPOINTS)
        or task["public_candidates_per_world"] != MAX_CANDIDATES
        or task["evaluator_only_heldout_trajectories_per_world"] != HELDOUT
        or len(KINDS) != 12
        or tuple(k for k in prereg["arms"] if k != "ablations") != KINDS[:8]
        or tuple(prereg["arms"]["ablations"]) != KINDS[8:]):
        raise ComparisonRejected("F50_HARNESS_FROZEN_PROTOCOL_DRIFT")
    return tuple((size, seed) for size in world.BANK_SIZES
                 for seed in world.DEV_SEEDS)


def checkpoint_inventory(source_roles):
    """Read-only *metadata* validation; does not assert any checkpoint exists.

    A science admission must separately verify on-disk bytes and exact-source
    training/receipt. Missing or unsupported 2048/1024 controls are explicitly
    rejected, never silently inferred from the qualified 4096 controls.
    """
    expected_sizes = set(world.BANK_SIZES)
    if type(source_roles) is not dict or set(source_roles) != expected_sizes:
        raise ComparisonRejected("F50_HARNESS_SOURCE_SIZE_ROLE_INCOMPLETE")
    identity = {}
    for size in world.BANK_SIZES:
        roles = source_roles[size]
        if type(roles) is not dict or set(roles) != set(TRAINED_SOURCE_KINDS):
            raise ComparisonRejected("F50_HARNESS_SOURCE_MODEL_ROLE_INCOMPLETE")
        identity[size] = {}
        for kind in TRAINED_SOURCE_KINDS:
            entry = roles[kind]
            if (type(entry) is not dict
                or set(entry) != {"checkpoint_sha256", "source_sha",
                                  "source_dataset_sha256", "prereg_blob"}
                or entry["prereg_blob"] != world.PREREG_BLOB
                or any(type(entry[k]) is not str for k in entry)
                or len(entry["checkpoint_sha256"]) != 64
                or len(entry["source_dataset_sha256"]) != 64
                or len(entry["source_sha"]) != 40
                or any(c not in "0123456789abcdef"
                       for key in ("checkpoint_sha256",
                                   "source_dataset_sha256", "source_sha")
                       for c in entry[key])):
                raise ComparisonRejected("F50_HARNESS_SOURCE_IDENTITY_UNVERIFIED")
            identity[size][kind] = entry["checkpoint_sha256"]
        # All three models must derive from the same exact public source dataset.
        if len({roles[k]["source_dataset_sha256"]
                for k in TRAINED_SOURCE_KINDS}) != 1:
            raise ComparisonRejected("F50_HARNESS_SOURCE_DATA_PARITY_FAILED")
    return identity


def _canonical_pool(candidates, count, *, code):
    if type(candidates) not in (list, tuple) or len(candidates) != count:
        raise ComparisonRejected(code)
    episodes = tuple(world.validate_trajectory(x) for x in candidates)
    if len(set(episodes)) != count:
        raise ComparisonRejected(code)
    return episodes


def _probabilities(arm, heldout):
    if hasattr(arm, "probabilities"):
        values = arm.probabilities(heldout)
    else:
        values = tuple(arm.probability(x) for x in heldout)
    if type(values) not in (list, tuple) or len(values) != HELDOUT:
        raise ComparisonRejected("F50_HARNESS_PREDICTION_COUNT_VIOLATION")
    rows = []
    for bits in values:
        if (type(bits) not in (list, tuple) or len(bits) != 3
            or any(type(x) not in (int, float) or not math.isfinite(x)
                   or not 0 <= x <= 1 for x in bits)):
            raise ComparisonRejected("F50_HARNESS_PREDICTION_INVALID")
        rows.append(tuple(float(x) for x in bits))
    return rows


def run_fixture_arm(size, seed, kind, arm, oracle, cold_restore):
    """Drive exactly 64 public action-consequence queries, with 3 cold scores.

    Evaluator object is read only through four public methods; its target-law
    state is not imported or read. The fixture-only check occurs BEFORE ANY
    selected action. No actual F50 DEV first-use is possible through this API.
    """
    if (size, seed) not in frozen_plan() or kind not in KINDS:
        raise ComparisonRejected("F50_HARNESS_UNREGISTERED_WORLD_OR_ARM")
    if not callable(cold_restore):
        raise ComparisonRejected("F50_HARNESS_COLD_RESTORE_REQUIRED")
    receipt = oracle.public_receipt()
    if (type(receipt) is not dict or receipt.get("fixture_only") is not True
        or receipt.get("public_events_used") != 0
        or receipt.get("protected_cohorts_consumed") != 0):
        raise ComparisonRejected("F50_HARNESS_DEV_FIRST_USE_NOT_AUTHORIZED")
    pool = _canonical_pool(oracle.public_candidates(), MAX_CANDIDATES,
                           code="F50_HARNESS_PUBLIC_POOL_INVALID")
    if tuple(arm.pool) != pool:
        raise ComparisonRejected("F50_HARNESS_ARM_PUBLIC_POOL_MISMATCH")
    if getattr(arm, "target_graph_available", False) is not False:
        raise ComparisonRejected("F50_HARNESS_TARGET_GRAPH_LEAKAGE")
    if getattr(arm, "observed_bits") != 0:
        raise ComparisonRejected("F50_HARNESS_DIRTY_START")
    if getattr(arm, "used", []) != []:
        raise ComparisonRejected("F50_HARNESS_REPLAYED_START")
    start = process_time()
    reported = []
    seen = set()
    for count in range(1, CHECKPOINTS[-1] + 1):
        index, episode = arm.select()
        if (type(index) is not int or not 0 <= index < MAX_CANDIDATES
            or index in seen or world.validate_trajectory(episode) != pool[index]):
            raise ComparisonRejected("F50_HARNESS_ACTION_CUSTODY_FAILED")
        outcome = oracle.public_event(index, episode)
        if (type(outcome) not in (tuple, list) or len(outcome) != 3
            or any(type(v) is not int or v not in (0, 1) for v in outcome)):
            raise ComparisonRejected("F50_HARNESS_PUBLIC_LABEL_INVALID")
        arm.observe(index, outcome)
        seen.add(index)
        if (getattr(arm, "observed_bits") != count * 3
            or len(getattr(arm, "used")) != count):
            raise ComparisonRejected("F50_HARNESS_PUBLIC_BIT_BUDGET_VIOLATION")
        if count not in CHECKPOINTS:
            continue
        packet = arm.cold_checkpoint()
        clone = cold_restore(packet)
        if (type(packet) is not bytes or type(clone.cold_checkpoint()) is not bytes
            or clone.cold_checkpoint() != packet):
            raise ComparisonRejected("F50_HARNESS_COLD_NOT_BIT_EXACT")
        # No evaluator-only inputs are returned before the score checkpoint.
        heldout = _canonical_pool(oracle.heldout_inputs_for_prediction(),
                                  HELDOUT, code="F50_HARNESS_HELDOUT_INPUTS_INVALID")
        if set(heldout) & set(pool):
            raise ComparisonRejected("F50_HARNESS_PUBLIC_HELDOUT_OVERLAP")
        probabilities = _probabilities(arm, heldout)
        score = oracle.score_once(probabilities)
        if (type(score) is not dict
            or score.get("fixture_only") is not True
            or score.get("query_budget") != count
            or score.get("scored_clean_bits") != 3 * HELDOUT
            or score.get("target_law_disclosed") is not False
            or score.get("scientific_pass") is not False
            or type(score.get("clean_heldout_accuracy")) is not float
            or not 0 <= score["clean_heldout_accuracy"] <= 1):
            raise ComparisonRejected("F50_HARNESS_SEALED_SCORE_INVALID")
        reported.append({"budget": count,
                         "fixture_accuracy": score["clean_heldout_accuracy"],
                         "cold_sha256": sha256(packet).hexdigest()})
    receipt = oracle.public_receipt()
    if (receipt.get("public_events_used") != 64
        or receipt.get("observed_public_bits") != 192
        or receipt.get("scored_checkpoints") != list(CHECKPOINTS)
        or receipt.get("protected_cohorts_consumed") != 0):
        raise ComparisonRejected("F50_HARNESS_FINAL_EVALUATOR_CUSTODY_FAILED")
    proposals = getattr(arm, "proposals", 0)
    expected_proposals = 64 * 2048 if (kind == "native"
                         or kind == "compositional_grammar_bayes"
                         or kind.startswith("native_")) else 0
    if proposals != expected_proposals:
        raise ComparisonRejected("F50_HARNESS_PROPOSAL_BUDGET_VIOLATION")
    if getattr(arm, "optimizer_steps", 0) != 0:
        raise ComparisonRejected("F50_HARNESS_UNEXPECTED_TARGET_OPTIMIZER")
    return {"schema": SCHEMA, "size": size, "seed": seed, "arm": kind,
            "checkpoints": reported,
            "observed_public_bits": 192,
            "public_events": 64,
            "proposals": proposals,
            "prediction_accesses": getattr(arm, "prediction_accesses", None),
            "target_cpu_seconds": round(process_time() - start, 6),
            "cold_restores": len(CHECKPOINTS),
            "fixture_only": True,
            "scientific_pass": False,
            "classification": FIXTURE_CLASSIFICATION}


def run_fixture_nine_worlds(make_arm, make_oracle):
    """End-to-end nine-world scheduler with synthetic-only evaluators.

    Producers are externally provided; this source cannot construct DEV laws
    or invoke an evaluator first-use. For each arm/world, make_oracle MUST
    return a fresh fixture evaluator; no cross-arm public feedback sharing.
    """
    if not callable(make_arm) or not callable(make_oracle):
        raise ComparisonRejected("F50_HARNESS_MISSING_FACTORIES")
    report = []
    for size, seed in frozen_plan():
        for kind in KINDS:
            arm, restore = make_arm(size, seed, kind)
            oracle = make_oracle(size, seed, kind)
            report.append(run_fixture_arm(size, seed, kind, arm, oracle, restore))
    if len(report) != 9 * len(KINDS):
        raise ComparisonRejected("F50_HARNESS_NINE_WORLD_COVERAGE_FAILED")
    return {"schema": SCHEMA, "classification": FIXTURE_CLASSIFICATION,
            "world_count": 9, "arms_per_world": len(KINDS),
            "worlds": [list(x) for x in frozen_plan()],
            "arm_runs": report, "development_outcomes_consumed": 0,
            "protected_cohorts_consumed": 0, "scientific_pass": False}


def describe_readiness():
    """A read-only plan, not an assertion that all source models are fitted."""
    return {"schema": SCHEMA,
            "frozen_prereg_blob": world.PREREG_BLOB,
            "worlds_high_first": [list(x) for x in frozen_plan()],
            "arms": list(KINDS),
            "checkpoints": list(CHECKPOINTS),
            "required_source_sizes": list(world.BANK_SIZES),
            "required_trained_roles": list(TRAINED_SOURCE_KINDS),
            "development_first_use": "BLOCKED",
            "classification": "PRE_FIRST_USE_ENGINEERING_ONLY",
            "scientific_pass": False}


if __name__ == "__main__":
    print(json.dumps(describe_readiness(), sort_keys=True))
