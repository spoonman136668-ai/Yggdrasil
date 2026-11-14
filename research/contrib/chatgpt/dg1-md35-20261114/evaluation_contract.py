"""MD35 prospective evaluation arithmetic; NO cohort generation or execution.

A trusted, separately authorized harness must collect charged public receipts,
verify original source/ledger/first-use custody, and deliver aligned blocks.
This module does not construct physical worlds, call learners, fit a model,
open protected cohorts, or admit a scientific result. Its mechanical tests
use handwritten non-reserved toy worlds only.

Every statistic is a *block*-level statistic. No episode bootstrap, hidden
law oracle, trial re-selection, or post-result threshold tuning is permitted.
"""
import hashlib
import json
import math
import random
from collections import Counter
from pathlib import Path

from public_actions import PublicEpisode, require_public_blocks


HERE = Path(__file__).resolve().parent
LOCK = json.loads((HERE / "prereg.json").read_text("utf-8"))
if LOCK["schema"] != "yggdrasil.dg1-md35-strong-conventional-controls-prereg.v1":
    raise AssertionError("MD35_EVAL_FROZEN_PREREG_REQUIRED")
EVAL_COHORTS = ("unfamiliar_transfer", "independent_cold")
CONVENTIONAL = ("bayesian", "recurrent", "model_based_rl")
BOOTSTRAP_SEED = 35045
BOOTSTRAP_RESAMPLES = 2000
SATURATION = 0.89
UNDERQUALIFIED = 0.10
MIN_UTILITY, MAX_UTILITY = -0.68, 0.94
PRESPECIFIED_FAMILIES = ("braid", "inhibitor", "crossbridge")


def canonical(value):
    return json.dumps(value, ensure_ascii=True, sort_keys=True,
                      separators=(",", ":"), allow_nan=False)


def sha256_json(value):
    return hashlib.sha256(canonical(value).encode("ascii")).hexdigest()


def verified_checkpoint_digest(model):
    """Fingerprint training-only checkpoint before independent cold restore."""
    if not callable(getattr(model, "checkpoint", None)):
        raise AssertionError("MD35_UNTRAINED_OR_INVALID_CHECKPOINT")
    return sha256_json(model.checkpoint())


def assert_frozen_checkpoint(model, trained_digest):
    """Verify weights/trained statistics did not adapt on heldout cohorts."""
    if type(trained_digest) is not str or len(trained_digest) != 64:
        raise AssertionError("MD35_UNPINNED_TRAIN_CHECKPOINT")
    actual = verified_checkpoint_digest(model)
    if actual != trained_digest:
        raise AssertionError("MD35_HELDOUT_WEIGHT_MUTATION")
    return actual


def _check_episode(ep, context):
    if type(ep) is not PublicEpisode or ep.context != context:
        raise AssertionError("MD35_EVAL_NONPUBLIC_OR_BAD_CONTEXT")
    if (type(ep.events) is not tuple or len(ep.events) not in (3, 4)
            or type(ep.trace_sha256) is not str
            or len(ep.trace_sha256) != 64
            or any(c not in "0123456789abcdef" for c in ep.trace_sha256)):
        raise AssertionError("MD35_EVAL_UNVERIFIED_RECEIPT_SHAPE")
    stage = 0
    diagnostics = 0
    route1 = 0
    success = 0
    costs = 0.0
    for row in ep.events:
        if type(row) is not tuple or len(row) != 5:
            raise AssertionError("MD35_EVAL_NONPUBLIC_EVENT")
        phase, kind, argument, reward, bit = row
        if type(phase) is not int or phase != stage or type(reward) is not float:
            raise AssertionError("MD35_EVAL_MISSING_CHARGED_STEP")
        if kind == "diagnostic":
            if (diagnostics != 0 or reward != -0.09 or
                    type(bit) is not int or bit not in (0, 1)):
                raise AssertionError("MD35_EVAL_UNPAID_OR_DUPLICATE_DIAGNOSTIC")
            if (stage == 0 and argument != 0) or (stage == 2 and argument != 0) or (
                    stage == 1 and (type(argument) is not int or
                                    argument not in (0, 1))):
                raise AssertionError("MD35_EVAL_UNREGISTERED_PUBLIC_PROBE")
            diagnostics += 1
        else:
            if type(bit) is not int or bit != -1:
                raise AssertionError("MD35_EVAL_FREE_PRIVATE_SENSOR")
            if kind == "actuator" and stage == 0:
                if argument != context or reward != -0.02:
                    raise AssertionError("MD35_EVAL_WRONG_CHARGED_PRECURSOR")
            elif kind == "route" and stage == 1:
                if type(argument) is not int or argument not in (0, 1):
                    raise AssertionError("MD35_EVAL_ILLEGAL_ROUTE")
                if reward != (-0.02 if argument == 0 else -0.05):
                    raise AssertionError("MD35_EVAL_ROUTE_COST_OMITTED")
                route1 = argument
            elif kind == "terminal" and stage == 2:
                if (type(argument) is not int or argument not in range(4) or
                        reward not in (0.98, -0.52)):
                    raise AssertionError("MD35_EVAL_BAD_TERMINAL_REWARD")
                success = int(reward == 0.98)
            else:
                raise AssertionError("MD35_EVAL_CAUSAL_ORDER_INVALID")
            stage += 1
        costs += reward
    if (stage != 3 or len(ep.events) != 3 + diagnostics or
            not math.isfinite(ep.net_utility) or
            abs(ep.net_utility - costs) > 1e-9 or
            ep.net_utility < MIN_UTILITY - 1e-8 or
            ep.net_utility > MAX_UTILITY + 1e-8):
        raise AssertionError("MD35_EVAL_UNPAID_OR_IMPOSSIBLE_NET_UTILITY")
    return ep.net_utility, diagnostics, route1, success


def _block_metrics(block):
    require_public_blocks((block,), expected_count=1)
    episodes = tuple(_check_episode(ep, c) for c, ep in enumerate(block))
    return {
        "block_net_utility": sum(x[0] for x in episodes) / 4,
        "first_episode_net": episodes[0][0],
        "last_episode_net": episodes[3][0],
        "paid_diagnostics": sum(x[1] for x in episodes),
        "route1_actions": sum(x[2] for x in episodes),
        "goal_successes": sum(x[3] for x in episodes),
        "physically_paid_actions": sum(len(ep.events) for ep in block),
    }


def block_bootstrap(values, *, seed=BOOTSTRAP_SEED):
    """Exactly 2,000 percentile draws, independently resampled law *blocks*."""
    if (type(values) not in (tuple, list) or not values or
            any(type(x) not in (int, float) or not math.isfinite(x)
                for x in values) or type(seed) is not int):
        raise AssertionError("MD35_BOOTSTRAP_INVALID_BLOCKS")
    rng = random.Random(seed)
    n = len(values)
    estimates = []
    for _ in range(BOOTSTRAP_RESAMPLES):
        estimates.append(sum(values[rng.randrange(n)]
                             for _ in range(n)) / n)
    estimates.sort()
    lo = estimates[int(0.025 * (BOOTSTRAP_RESAMPLES - 1))]
    hi = estimates[int(0.975 * (BOOTSTRAP_RESAMPLES - 1))]
    return {
        "seed": seed, "resamples": BOOTSTRAP_RESAMPLES,
        "block_count": n, "low95": lo, "high95": hi,
    }


def _cohort_metrics(blocks, cohort):
    if cohort not in EVAL_COHORTS:
        raise AssertionError("MD35_EVAL_NOT_FROZEN_HELDOUT_COHORT")
    expected = LOCK["reserved_cohorts_not_opened"][cohort]["blocks"]
    source = require_public_blocks(blocks, expected_count=expected)
    rows = [_block_metrics(block) for block in source]
    mean = lambda key: sum(r[key] for r in rows) / len(rows)
    mean_net = mean("block_net_utility")
    return {
        "cohort": cohort,
        "source_only_arithmetic": True,
        "not_scientific_admission": True,
        "blocks": expected,
        "episodes": 4 * expected,
        "mean_net_utility": mean_net,
        "block_bootstrap_95": block_bootstrap(
            [r["block_net_utility"] for r in rows]),
        "success_rate": mean("goal_successes") / 4,
        "diagnostics_per_episode": mean("paid_diagnostics") / 4,
        "route1_fraction": mean("route1_actions") / 4,
        "later_minus_first_episode_utility": mean("last_episode_net") -
                                             mean("first_episode_net"),
        "physically_paid_actions": sum(r["physically_paid_actions"] for r in rows),
        "public_block_receipts": [sha256_json([ep.trace_sha256 for ep in block])
                                   for block in source],
        # A claimed causal retention gain requires the registered
        # independent memory-reset ablation, not just this descriptive metric.
        "retention_causality_claim": "NOT_TESTED",
    }


def summarize_unopened_shape_only(blocks, cohort):
    """Arithmetic helper, NOT an authorization to score any protected first-use.

    The caller must separately prove custody and authority. Never label
    this return as scientific qualification without a source-sealed runner.
    """
    return _cohort_metrics(blocks, cohort)


def _require_matching_harness_block_commitments(left, right, count):
    """Check opaque *harness-only* identity alignment, not authenticity.

    Each commitment must originate from an independently source-pinned,
    first-use-authorized trusted harness and bind exact prereg/cohort/block,
    seed identities, private world law, and source. A caller can fabricate
    matching hashes: the scorer is NOT a signer, ledger, or independent witness.
    Never give these private commitments to policies, trainers or models.
    """
    for values in (left, right):
        if (type(values) not in (tuple, list) or len(values) != count or
                any(type(value) is not str or len(value) != 64 or
                    any(c not in "0123456789abcdef" for c in value)
                    for value in values) or
                len(set(values)) != count):
            raise AssertionError("MD35_PAIRED_HARNESS_IDENTITY_REQUIRED")
    if tuple(left) != tuple(right):
        raise AssertionError("MD35_PAIRED_HIDDEN_LAW_BLOCK_MISMATCH")


def paired_net_bootstrap(left_blocks, right_blocks, cohort, *,
                         left_block_commitments=None,
                         right_block_commitments=None):
    """Matched block resampling; never silently pair unrelated private laws.

    Scoring arithmetic is NOT independent scientific admission. The harness
    must also separately prove commitment authenticity, original source,
    owner/ledger/first-use custody and identical physical world allocation.
    """
    if cohort not in EVAL_COHORTS:
        raise AssertionError("MD35_EVAL_NOT_FROZEN_HELDOUT_COHORT")
    count = LOCK["reserved_cohorts_not_opened"][cohort]["blocks"]
    left = require_public_blocks(left_blocks, expected_count=count)
    right = require_public_blocks(right_blocks, expected_count=count)
    _require_matching_harness_block_commitments(
        left_block_commitments, right_block_commitments, count)
    diff = [_block_metrics(a)["block_net_utility"] -
            _block_metrics(b)["block_net_utility"]
            for a, b in zip(left, right)]
    return {"mean_paired_delta": sum(diff) / count,
            "block_bootstrap_95": block_bootstrap(diff),
            "harness_only_commitments_shape_matched": True,
            "independent_harness_authenticity_verified": False,
            "not_scientific_admission": True}


def harness_only_family_breakdown(blocks, family_labels, cohort):
    """Harness-only metadata, never delivered to policy/GRU/Bayes/RL."""
    if cohort not in EVAL_COHORTS:
        raise AssertionError("MD35_EVAL_NOT_FROZEN_HELDOUT_COHORT")
    n = LOCK["reserved_cohorts_not_opened"][cohort]["blocks"]
    source = require_public_blocks(blocks, expected_count=n)
    if (type(family_labels) not in (list, tuple) or len(family_labels) != n):
        raise AssertionError("MD35_EVAL_PRIVATE_LABELS_HARNESS_ONLY")
    buckets = {}
    factorial = Counter()
    for block_index, (block, label) in enumerate(zip(source, family_labels)):
        if (type(label) not in (list, tuple) or len(label) != 3 or
                label[0] not in PRESPECIFIED_FAMILIES or
                type(label[1]) is not int or label[1] not in range(4) or
                type(label[2]) is not bool):
            raise AssertionError("MD35_EVAL_PRIVATE_LABEL_SCHEMA")
        expected = (
            PRESPECIFIED_FAMILIES[block_index % 3],
            (block_index // 3) % 4,
            ((block_index // 12) % 2) == 1,
        )
        if tuple(label) != expected:
            raise AssertionError("MD35_EVAL_FROZEN_PRIVATE_LAW_ALLOCATION_DRIFT")
        key = (label[0], label[1], label[2])
        factorial[key] += 1
        buckets.setdefault(label[0], []).append(
            _block_metrics(block)["block_net_utility"])
    if len(factorial) != 24 or set(factorial.values()) != {n // 24}:
        raise AssertionError("MD35_EVAL_HARNESS_FACTORIAL_IMBALANCE")
    return {name: {"blocks": len(vals), "mean_net_utility": sum(vals) / len(vals)}
            for name, vals in sorted(buckets.items())}


def preregistered_headroom_status(qualified_scores):
    """Pure decision rule; numeric inputs are NOT themselves qualification."""
    if type(qualified_scores) is not dict or set(qualified_scores) != set(CONVENTIONAL):
        raise AssertionError("MD35_INCOMPLETE_STRONG_CONVENTIONAL_CONTROLS")
    for model, score in qualified_scores.items():
        if (type(score) is not dict or
                set(score) != set(EVAL_COHORTS) or
                any(type(score[c]) not in (int, float) or
                    not math.isfinite(score[c]) or
                    not MIN_UTILITY - 1e-8 <= score[c] <= MAX_UTILITY + 1e-8
                    for c in EVAL_COHORTS)):
            raise AssertionError("MD35_INVALID_UNQUALIFIED_CONTROL_SCORE")
    if any(all(score[c] >= SATURATION for c in EVAL_COHORTS)
           for score in qualified_scores.values()):
        return "TRIVIAL_FOR_NOVEL_GAIN_STOP"
    if not any(all(score[c] > UNDERQUALIFIED for c in EVAL_COHORTS)
               for score in qualified_scores.values()):
        return "CONTROLS_UNDERQUALIFIED_OR_UNIDENTIFIABLE_NO_NATIVE_GATE"
    return "DEVELOPING_TASK_HEADROOM_ONLY"


def compute_parity_report(comparators):
    """Compare equal *available* legal actions; report distinct actions used.

    The frozen prereg grants every public episode at most one paid diagnostic.
    Diagnostic abstention is a legal policy decision charged to the utility
    score, not unequal experimental opportunity. Whole-process CPU parity
    remains mandatory for matched-compute superiority claims.
    """
    if (type(comparators) is not dict or len(comparators) < 2):
        raise AssertionError("MD35_COMPUTE_PARITY_REQUIRES_COMPARATORS")
    # Frozen prereg caps FITTING/SELECTION at 900 CPU seconds, not
    # whole-process CPU. Evaluation, checkpoint IO and scoring MUST also be
    # counted in total CPU/wall receipts even if they exceed the fit cap.
    required = {
        "fit_selection_cpu_seconds", "whole_process_cpu_seconds",
        "whole_process_wall_seconds", "paid_actions", "public_episodes",
        "available_paid_action_slots",
    }
    for row in comparators.values():
        if type(row) is not dict or set(row) != required:
            raise AssertionError("MD35_COMPUTE_RECEIPT_INCOMPLETE")
        fit, total, wall = (
            row["fit_selection_cpu_seconds"],
            row["whole_process_cpu_seconds"],
            row["whole_process_wall_seconds"],
        )
        if (any(type(x) not in (float, int) or
                not math.isfinite(x) or x <= 0 for x in (fit, total, wall))
                or fit > 900 or total < fit
                or type(row["paid_actions"]) is not int
                or type(row["public_episodes"]) is not int
                or row["public_episodes"] < 1
                or type(row["available_paid_action_slots"]) is not int
                or row["available_paid_action_slots"] !=
                   4 * row["public_episodes"]
                or not 3 * row["public_episodes"] <= row["paid_actions"] <=
                   row["available_paid_action_slots"]):
            raise AssertionError("MD35_COMPUTE_OR_PHYSICAL_ACTION_INVALID")
    cpu = [row["whole_process_cpu_seconds"] for row in comparators.values()]
    actions = [row["paid_actions"] for row in comparators.values()]
    opportunity = [row["available_paid_action_slots"]
                   for row in comparators.values()]
    info = [row["public_episodes"] for row in comparators.values()]
    fair_cpu = max(cpu) <= min(cpu) * 1.1
    equal_opportunity = len(set(opportunity)) == 1
    equal_information = len(set(info)) == 1
    return {
        "matched_compute": fair_cpu,
        # Descriptive difference in probes actually chosen; a valid policy
        # may skip the 0.09 diagnostic and keep equal action availability.
        "matched_paid_actions": max(actions) <= min(actions) * 1.1,
        "matched_action_opportunity": equal_opportunity,
        "matched_information": equal_information,
        "per_control_receipts": comparators,
        "matched_superiority_claim_permitted": (
            fair_cpu and equal_opportunity and equal_information),
        "lower_compute_pareto_possible_but_not_proven": True,
    }
