#!/usr/bin/env python3
"""F50 frozen development numeric-envelope audit: NO scientific admission.

The evaluator first-use runner is the ONLY producer of authentic DEV results.
This pure function cannot open targets, infer hidden labels, or authorize
first-use. Synthetic/mocked inputs in tests validate decision logic ONLY.

A numeric threshold match is INSUFFICIENT for GO: full-source training,
source/action parity, independent target novelty, negative canary, cost,
once-only target custody, and independent science verification are separate.
"""
from decimal import Decimal
from math import isfinite

import f50_worlds as world
import f50_comparison_harness as harness

SCHEMA = "yggdrasil.qtr01.f50.development-numeric-envelope.v1"
CONTROLS = harness.KINDS[1:8]
NEGATIVES = harness.KINDS[8:]
N_WORLDS = len(world.BANK_SIZES) * len(world.DEV_SEEDS)
N_RUNS = N_WORLDS * len(harness.KINDS)
CHECKPOINTS = (16, 32, 64)


class NumericAuditRejected(RuntimeError):
    pass


def require(value, name):
    if not value:
        raise NumericAuditRejected("F50_NUMERIC_AUDIT_" + name)


def _score(value):
    require(type(value) is float and isfinite(value)
            and 0 <= value <= 1, "INVALID_CLEAN_ACCURACY")
    return Decimal(str(value))


def _cpu(value):
    require(type(value) in (int, float) and isfinite(value)
            and 0 <= value, "INVALID_TARGET_CPU")
    return Decimal(str(value))


def _check_row(row, size, seed, kind):
    require(type(row) is dict
            and row.get("schema") == harness.SCHEMA
            and row.get("size") == size
            and row.get("seed") == seed
            and row.get("arm") == kind
            and row.get("fixture_only") is False
            and row.get("scientific_pass") is False
            and row.get("classification") == "DEV_F50_UNCLASSIFIED"
            and row.get("public_events") == 64
            and row.get("observed_public_bits") == 192
            and row.get("cold_restores") == 3
            and type(row.get("prediction_accesses")) is int
            and row["prediction_accesses"] >= 0,
            "NONDEVELOPMENT_OR_INCOMPLETE_RUN")
    expected_proposals = (64 * 2048 if kind == "native"
                          or kind == "compositional_grammar_bayes"
                          or kind in NEGATIVES else 0)
    require(type(row.get("proposals")) is int
            and row["proposals"] == expected_proposals,
            "PROPOSAL_BUDGET_DRIFT")
    checks = row.get("checkpoints")
    require(type(checks) is list and len(checks) == 3
            and [c.get("budget") for c in checks] == list(CHECKPOINTS),
            "SCORE_CHECKPOINT_DRIFT")
    values = {}
    for c in checks:
        budget = c["budget"]
        require(type(c) is dict
                and type(c.get("cold_sha256")) is str
                and len(c["cold_sha256"]) == 64
                and all(ch in "0123456789abcdef"
                        for ch in c["cold_sha256"])
                and "fixture_accuracy" not in c,
                "UNCUSTODIED_OR_FIXTURE_SCORE")
        values[budget] = _score(c.get("clean_heldout_accuracy"))
    seconds = _cpu(row.get("target_cpu_seconds"))
    return values, seconds


def audit_numeric_envelope(report):
    """Validate all 108 authentic-shape rows; return diagnostic, NEVER GO.

    The numeric audit does NOT assert that a row comes from an independent
    target run. This fact requires upstream once-only owner custody and
    separate verification of model bytes, source compute and label secrecy.
    Even a fabricated all-pass report returns scientific_pass=False.
    """
    plan = harness.frozen_plan()
    require(type(report) is dict
            and report.get("schema") == harness.SCHEMA
            and report.get("classification") == "DEV_F50_UNCLASSIFIED"
            and report.get("scientific_pass") is False
            and report.get("independent_classification_required") is True
            and report.get("world_count") == N_WORLDS
            and report.get("arms_per_world") == len(harness.KINDS)
            and report.get("worlds") == [list(p) for p in plan]
            and report.get("development_outcomes_consumed") == N_RUNS * 64 * 3
            and report.get("protected_cohorts_consumed") == 0,
            "REPORT_NOT_ADMITTED_SHAPE")
    rows = report.get("arm_runs")
    require(type(rows) is list and len(rows) == N_RUNS,
            "INCOMPLETE_108_ROW_CUSTODY")
    scores = {}
    times = {}
    ordered = ((size,seed,kind) for size,seed in plan for kind in harness.KINDS)
    for row, (size,seed,kind) in zip(rows, ordered):
        values, seconds = _check_row(row,size,seed,kind)
        scores[(size,seed,kind)], times[(size,seed,kind)] = values, seconds
    require(len(scores) == N_RUNS, "DUPLICATE_WORLD_ARM")

    mean = lambda values: sum(values,Decimal(0))/Decimal(len(values))
    b32means = {
        kind: mean([scores[(s,seed,kind)][32] for s,seed in plan])
        for kind in harness.KINDS
    }
    conventional = harness.TRAINED_SOURCE_KINDS
    best_conventional = max(b32means[kind] for kind in conventional)
    best_control_kind = max(CONTROLS,
                            key=lambda kind:(b32means[kind], -CONTROLS.index(kind)))
    best_control_mean = b32means[best_control_kind]
    native_mean = b32means["native"]

    reasons = []
    if native_mean - best_control_mean < Decimal("0.05"):
        reasons.append("NATIVE_MEAN_GAIN_BELOW_005")
    # Frozen criterion is +0.02 per unseen FAMILY (one seed, 3 sizes)
    # against the WORLDWISE strongest control. A +0.02 test in each of
    # nine worlds would improperly strengthen the frozen criterion.
    family_gaps, world_gaps = {}, {}
    for seed in world.DEV_SEEDS:
        gaps = []
        for size in world.BANK_SIZES:
            native32 = scores[(size, seed, "native")][32]
            best_world32 = max(scores[(size, seed, k)][32] for k in CONTROLS)
            gap = native32 - best_world32
            world_gaps[(size, seed)] = gap
            gaps.append(gap)
        family_gaps[seed] = mean(gaps)
        if family_gaps[seed] < Decimal("0.02"):
            reasons.append("FAMILY_B32_GAP_" + str(seed))
    for size,seed in plan:
        native32 = scores[(size,seed,"native")][32]
        best_world64 = max(scores[(size,seed,k)][64] for k in CONTROLS)
        if scores[(size,seed,"native")][64]-best_world64 < Decimal("-0.01"):
            reasons.append("B64_REGRESSION_"+str(size)+"_"+str(seed))
        if any(native32-scores[(size,seed,k)][32] <= Decimal("0.01")
               for k in NEGATIVES):
            reasons.append("NEGATIVE_MATCH_"+str(size)+"_"+str(seed))
    headroom_over = all(
        scores[(s,seed,k)][32] >= Decimal("0.95")
        for s,seed in plan for k in harness.KINDS)
    headroom_under = best_conventional < Decimal("0.55")
    resource_breach = any(seconds > Decimal("1200") for seconds in times.values())
    if headroom_over or headroom_under:
        status="TASK_HEADROOM_INVALID"
    elif resource_breach:
        status="RESOURCE_STOP"
    elif reasons:
        status="NUMERIC_THRESHOLDS_NO_GO"
    else:
        status="NUMERIC_THRESHOLDS_MET_CUSTODY_AND_COST_UNVERIFIED"
    return {
        "schema":SCHEMA, "classification":"DEV_F50_UNCLASSIFIED",
        "numeric_diagnostic":status, "numeric_reasons":reasons,
        "world_arm_rows":len(scores),
        "native_b32_mean":str(native_mean),
        "best_control_kind":best_control_kind,
        "best_single_control_b32_mean":str(best_control_mean),
        "best_conventional_b32_mean":str(best_conventional),
        "family_gap_interpretation":"three_bank_mean_of_worldwise_best_control_gaps",
        "family_b32_gaps":{str(seed):str(family_gaps[seed])
                           for seed in world.DEV_SEEDS},
        "world_b32_gaps":{str(size)+"_"+str(seed):str(world_gaps[(size,seed)])
                          for size,seed in plan},
        "source_training_cost_verified":False,
        "total_process_cpu_cost_verified":False,
        "source_and_action_parity_independently_verified":False,
        "development_once_only_custody_verified":False,
        "scientific_pass":False, "independent_science_qualification_required":True,
    }
