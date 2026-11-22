"""NKR-17: exact audit of all 56 random two-action policies per world.

The original NKR-16 frozen source and learner are NOT modified. Reuses
already-consumed deterministic NKR-12 conjunction worlds, not new external
science or independent first use. All schedule choices precede their public
source consequences. The evaluator sees source truth ONLY after the selected
observations are in evidence and excluded from the cold denominator.
"""
from __future__ import annotations

from collections import Counter
from fractions import Fraction
import importlib.util
import itertools
import json
import math
from pathlib import Path
import sys
import time

ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(ROOT))

from yggdrasil.native_operator_discovery import NativeOperatorDiscovery
from yggdrasil.native_intervention_repair import canonical, digest
from yggdrasil.public_causal_cells import PublicCausalCells


def source_module(label, relpath):
    spec = importlib.util.spec_from_file_location(
        label, Path(__file__).resolve().parents[1] / relpath)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


fixture = source_module("nkr17_original_nkr12", "NKR-12/experiment.py")
native = source_module("nkr17_original_nkr16", "NKR-16/experiment.py")
TRAIN = (0, 1, 2, 4, 8, 3, 5, 10)
COLD = (6, 7, 9, 11, 12, 13, 14, 15)
ALL_SCHEDULES = tuple(itertools.permutations(COLD, 2))
assert len(ALL_SCHEDULES) == 56 and len(set(ALL_SCHEDULES)) == 56


def fit_initial_public(source_rows):
    """Independent exact source-only baseline and grammar fitting.

    Does not call native policy, native mask filter, NKR-12 symbolic fit,
    source hidden masks, evaluator truth tables or protected cold labels.
    """
    positions = ((0, 1), (0, 0)) + tuple(
        (x, a) for x in TRAIN[1:] for a in (0, 1))
    if (type(source_rows) not in (list, tuple)
            or len(source_rows) != 16
            or tuple((x, a) for _, x, a, _ in source_rows) != positions):
        raise ValueError("NKR17_INITIAL_EVIDENCE_ACTION_SEQUENCE_DRIFT")
    d = {(x, a): y for _, x, a, y in source_rows}
    intercept = d[(0, 0)]
    base_mask = sum(1 << i for i in range(4)
                    if d[(1 << i, 0)] != intercept)
    def base(x):
        return intercept ^ ((x & base_mask).bit_count() & 1)
    if any(base(x) != d[(x, 0)] for x in TRAIN):
        raise ValueError("NKR17_INITIAL_VISIBLE_BASELINE_INVALID")
    candidates = tuple(
        m for m in range(1, 16)
        if all(
            int((x & m) == m) == (d[(x, 1)] ^ d[(x, 0)])
            for x in TRAIN
        ))
    if not candidates:
        raise ValueError("NKR17_NO_SUPPORTED_INITIAL_CONJUNCTION")
    return intercept, base_mask, candidates


def baseline_value(params, x):
    intercept, mask, _ = params
    return intercept ^ ((x & mask).bit_count() & 1)


def filter_observation(candidates, x, observed_effect):
    """Only a chosen public intervention can filter masks."""
    filtered = tuple(
        m for m in candidates if int((x & m) == m) == observed_effect
    )
    if not filtered:
        raise ValueError("NKR17_PUBLIC_OBSERVATION_CONTRADICTS_ALL_MASKS")
    return filtered


def independent_active_next(candidates, already):
    remaining = [x for x in COLD if x not in already]
    if not remaining:
        return None
    # n_yes*n_no orders exactly like H2(p); deterministic and float-free.
    return min(remaining, key=lambda x: (
        -(sum(int((x & m) == m) for m in candidates)
          * sum(int((x & m) != m) for m in candidates)),
        x))


def run_ordered_schedule(world, schedule, *, assert_active=False):
    """Actually execute the selected effects; score ONLY other 6 queries."""
    if (type(world) is not int or not 0 <= world < 12
            or type(schedule) not in (tuple, list)
            or len(schedule) != 2
            or any(type(x) is not int or x not in COLD for x in schedule)
            or schedule[0] == schedule[1]):
        raise ValueError("NKR17_SCHEDULE_OUTSIDE_FROZEN_SOURCE_SCOPE")
    env = fixture.IndependentActionWorld(world)
    observed = fixture.observations(env)
    params = fit_initial_public(observed)
    candidates = params[2]
    receipts = []
    for round_index, x in enumerate(schedule):
        selected = tuple(schedule[:round_index])
        if assert_active and independent_active_next(candidates, selected) != x:
            raise ValueError("NKR17_ACTIVE_POLICY_NOT_INDEPENDENT_ENTROPY_MAX")
        # Exactly one original simulated source action is executed AFTER
        # this fixed choice. Hidden-world masks are evaluator-private.
        observed_value = env.execute(x, 1)
        outcome_effect = observed_value ^ baseline_value(params, x)
        candidates = filter_observation(candidates, x, outcome_effect)
        rows = [(f"selected-public-action-{round_index:02d}",
                 x, 1, observed_value)]
        public = fixture.bundle(
            "nkr17-exact-public-" + digest(canonical(rows))[:16], rows)
        receipts.append(digest(public))
    correct = covered = wrong = 0
    remaining = tuple(x for x in COLD if x not in schedule)
    assert len(remaining) == 6
    for x in remaining:
        possibilities = {
            baseline_value(params, x) ^ int((x & mask) == mask)
            for mask in candidates
        }
        pred = next(iter(possibilities)) if len(possibilities) == 1 else None
        # This evaluation consequence is NOT a learner observation.
        truth = env.execute(x, 1)
        correct += int(pred is not None and pred == truth)
        covered += int(pred is not None)
        wrong += int(pred is not None and pred != truth)
    return {
        "world": world, "schedule": list(schedule),
        "public_extra_actions": 2, "unprobed_cold_queries": 6,
        "correct": correct, "covered": covered, "wrong": wrong,
        "abstentions": 6 - covered, "remaining_masks": len(candidates),
        "selected_receipts": receipts,
    }


def exact_distribution(histograms):
    """Exact 12-fold convolution, no Monte Carlo, floats or model fitting."""
    pmf = Counter({0: 1})
    for histogram in histograms:
        if sum(histogram.values()) != 56:
            raise ValueError("NKR17_NOT_56_UNIFORM_ORDERED_RANDOM_POLICIES")
        nxt = Counter()
        for current_total, multiplicity in pmf.items():
            for score, policies in histogram.items():
                nxt[current_total + score] += multiplicity * policies
        pmf = nxt
    assert sum(pmf.values()) == 56 ** 12
    return dict(sorted(pmf.items()))


def quantile(pmf, numerator, denominator):
    total = sum(pmf.values())
    threshold = total * numerator
    cumulative = 0
    for score, count in sorted(pmf.items()):
        cumulative += count * denominator
        if cumulative >= threshold:
            return score
    raise ValueError("NKR17_DISTRIBUTION_MISSING_QUANTILE")


def run_frozen():
    begin = time.monotonic()
    original_owner = PublicCausalCells().snapshot()
    per_world = []
    histograms = []
    active_total = 0
    seeded_total = 0
    oracle_total = 0
    active_covered = seeded_covered = 0
    all_errors = 0
    old_retention = 0
    all_random_actions = 0
    for world in range(12):
        env = fixture.IndependentActionWorld(world)
        warm_rows = fixture.observations(env, warm=True)
        raw = fixture.bundle(
            "nkr17-old-source-" + digest(canonical(warm_rows))[:16],
            warm_rows)
        old = NativeOperatorDiscovery.from_warmup(raw, digest(raw))
        old_sha = old.checkpoint_sha256
        old_checkpoint = old.checkpoint()
        for x in range(16):
            for action in (0, 1):
                # Historical synthetic source replay is old-domain
                # retention only; not new learner training.
                actual_old = env.execute(x, action, warm=True)
                old_retention += int(old.prior(x, action) == actual_old)
        if old.checkpoint() != old_checkpoint or old.checkpoint_sha256 != old_sha:
            raise AssertionError("NKR17_ORIGINAL_OLD_KNOWLEDGE_MUTATED")
        scores = []
        coverages = []
        schedule_pairs = []
        for schedule in ALL_SCHEDULES:
            result = run_ordered_schedule(world, schedule)
            all_random_actions += result["public_extra_actions"]
            all_errors += result["wrong"]
            scores.append(result["correct"])
            coverages.append(result["covered"])
            schedule_pairs.append(tuple(schedule))
        if any(a != b for a, b in zip(scores, coverages)):
            raise AssertionError("NKR17_STRONG_CONJUNCTION_CONTROL_CONFIDENTLY_WRONG")
        hist = Counter(scores)
        if sum(hist.values()) != 56:
            raise AssertionError("NKR17_ORDERED_POLICIES_NOT_EXHAUSTIVE")
        histograms.append(hist)
        # The ORIGINAL NKR16 native controller is invoked unmodified and
        # its chosen actions verified by an independent entropy computation.
        old_native = native.run_one_world(world, "structured", "active")
        active = run_ordered_schedule(
            world, tuple(old_native["selected"]), assert_active=True)
        old_random = native.run_one_world(world, "structured", "random")
        seeded = run_ordered_schedule(world, tuple(old_random["selected"]))
        if ((active["correct"], active["covered"], active["wrong"]) !=
                (old_native["unprobed_generalization_correct"],
                 old_native["unprobed_generalization_coverage"],
                 old_native["unprobed_generalization_wrong"])):
            raise AssertionError("NKR17_NATIVE_ACTIVE_EXACT_SOURCE_SCORE_DRIFT")
        if ((seeded["correct"], seeded["covered"], seeded["wrong"]) !=
                (old_random["unprobed_generalization_correct"],
                 old_random["unprobed_generalization_coverage"],
                 old_random["unprobed_generalization_wrong"])):
            raise AssertionError("NKR17_NATIVE_SEEDED_RANDOM_SCORE_DRIFT")
        active_total += active["correct"]
        seeded_total += seeded["correct"]
        active_covered += active["covered"]
        seeded_covered += seeded["covered"]
        oracle_total += max(scores)
        per_world.append({
            "world":world,"native_active_selected":active["schedule"],
            "native_active_correct":active["correct"],
            "original_seeded_random_selected":seeded["schedule"],
            "original_seeded_random_correct":seeded["correct"],
            "exact_random_score_histogram":dict(sorted(hist.items())),
            "exact_random_mean_correct":sum(scores)/56,
            "exact_random_max_correct":max(scores),
            "number_random_schedules_at_or_above_active":
                sum(s >= active["correct"] for s in scores),
            "old_checkpoint_sha256":old_sha,
        })
    if old_retention != 384 or all_random_actions != 12 * 56 * 2:
        raise AssertionError("NKR17_ACTION_COST_OR_RETENTION_DRIFT")
    if (active_total != 56 or seeded_total != 38
            or active_covered != 56 or seeded_covered != 38
            or all_errors != 0):
        raise AssertionError("NKR17_FROZEN_NKR16_SCORE_OR_NO_ERROR_DRIFT")
    pmf = exact_distribution(histograms)
    all_assignments = 56 ** 12
    weighted_total = sum(k * v for k, v in pmf.items())
    expected = Fraction(weighted_total, all_assignments)
    variance = Fraction(
        sum(k*k*v for k,v in pmf.items()), all_assignments
    ) - expected*expected
    tail_count = sum(n for k, n in pmf.items() if k >= active_total)
    tail = Fraction(tail_count, all_assignments)
    robust = (
        active_total >= float(expected) + 4
        and tail <= Fraction(1,20)
        and all_errors == 0
    )
    if PublicCausalCells().snapshot() != original_owner:
        raise AssertionError("NKR17_ACCEPTED_NATIVE_CAUSAL_OWNER_MUTATION")
    return {
        "schema":"yggdrasil.nkr17.exhaustive-random-policy-audit.v1",
        "classification": (
            "EXHAUSTIVE_RANDOM_CONTROL_DEV_ROBUST"
            if robust else "EXHAUSTIVE_RANDOM_CONTROL_NOT_ROBUST"),
        "status":"FROZEN_DEV_ANALYSIS_OF_ALREADY_CONSUMED_SOURCE",
        "engineering_contract_pass":True,
        "random_robustness_threshold_met":robust,
        "scientific_pass":False,"native_accepted":False,
        "external_authentic_experience":False,
        "random_source":"all_ordered_8x7_uniform_policy_pairs",
        "schedules_per_world":56,"worlds":12,
        "total_random_schedule_arms":672,
        "total_random_schedule_public_actions":all_random_actions,
        "native_active_total_correct":active_total,
        "original_seed_random_total_correct":seeded_total,
        "active_vs_one_seed_extra_correct":active_total-seeded_total,
        "active_total_coverage":active_covered,
        "seed_random_total_coverage":seeded_covered,
        "all_672_schedule_confidently_wrong":all_errors,
        "old_retention_correct":old_retention,
        "oracle_offline_12_world_best_total":oracle_total,
        "random_expected_correct_exact":str(expected),
        "random_expected_correct":float(expected),
        "random_variance_exact":str(variance),
        "random_stddev":math.sqrt(float(variance)),
        "random_tail_at_or_above_active_exact":str(tail),
        "random_tail_at_or_above_active":float(tail),
        "random_tail_assignments":str(tail_count),
        "random_assignment_count":str(all_assignments),
        "random_percentiles":{
            "p05":quantile(pmf,5,100),
            "p50":quantile(pmf,50,100),
            "p95":quantile(pmf,95,100)},
        "random_total_score_histogram":dict(sorted(pmf.items())),
        "per_world":per_world,
        "original_model_source_unmodified":True,
        "source_custody":"sha_pinned_synthetic_source_only",
        "wall_seconds":time.monotonic()-begin,
    }


if __name__=="__main__":
    print("NKR17_EXACT_RANDOM_AUDIT="+json.dumps(
        run_frozen(),sort_keys=True,separators=(",",":")),flush=True)
