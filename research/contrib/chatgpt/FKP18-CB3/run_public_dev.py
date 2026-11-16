"""Frozen CB3 public developmental study; never a protected first-use evaluation."""
from __future__ import annotations
from hashlib import sha256
from itertools import combinations
import json
import random
import statistics
import time

import binding
import gate_binding as learner
import public_source as source

BOOTSTRAP_SEED = 82360
RESAMPLES = 1000

def _query_bitset(state, history):
    return binding._feature_bits(state, history[-1].action,
                                 history[-2].action if len(history) > 1 else 0)

def _choose_truth(bits, features, truth):
    idx = 0
    for f in features:
        idx = (idx << 1) | ((bits >> f) & 1)
    return (truth >> idx) & 1

def _best_three(samples):
    """Source-independent conventional exact three-feature negative reference."""
    best = None
    for group in combinations(range(learner.FEATURES), 3):
        fit = learner._score_bins(samples, group)
        if fit is None:
            continue
        score, mask = fit
        if best is None or score > best[0]:
            best = score, group, mask
        if score == len(samples):
            break
    if best is None:
        raise ValueError("CB3_THREE_FEATURE_NO_PUBLIC_SUPPORT")
    return best

def one_world(seed):
    start = time.perf_counter()
    tape = source.public_training(seed)
    a, b = learner.DiscoveredGateBinder(), learner.ConventionalExhaustiveFour()
    observations = []
    wrong_timing = []
    for row in tape:
        credited, _ = learner._extract(row)
        a.observe_public(row)
        b.observe_public(row)
        if credited is not None:
            observations.append(credited)
            prev = row.history[-1].action
            older = row.history[-2].action if len(row.history) >= 2 else 0
            wrong_timing.append((binding._feature_bits(row.before, prev, older), credited[1]))
    if len(observations) != learner.CREDITS or len(wrong_timing) != learner.CREDITS:
        raise ValueError("CB3_EARNED_CREDIT_COUNT_MISMATCH")
    start_a = time.perf_counter()
    a.seal()
    a_seconds = time.perf_counter() - start_a
    start_b = time.perf_counter()
    b.seal()
    b_seconds = time.perf_counter() - start_b
    global_score, base_a, base_b, global_truth = learner._fit_base(observations)
    three_score, features3, truth3 = _best_three(observations)
    wrong_score, wrong_a, wrong_b, wrong_base_truth = learner._fit_base(wrong_timing)
    wrong_gate = learner._fit_conditional(wrong_timing, wrong_a, wrong_b)
    cold = learner.DiscoveredGateBinder.restore(a.snapshot())
    if a.snapshot() != cold.snapshot():
        raise AssertionError("CB3_COLD_CHECKPOINT_NOT_IDENTICAL")
    features = a.learned
    actual_content, actual_gate = source.source_private_feature_pairs(seed)
    trained_content = tuple(sorted(features[:2]))
    trained_gate = tuple(sorted(features[2:4]))
    test = source.unseen_queries(seed)
    scores = dict(DIRECT_GATE=0, EXACT_FOUR=0, NO_GATE=0,
                  THREE_FEATURE=0, WRONG_DELAY=0, NO_UPDATE=0)
    cold_equal = True
    for state, history, target in test:
        bitset = _query_bitset(state, history)
        policies = {
            "DIRECT_GATE": a.choose_public(state, history),
            "EXACT_FOUR": b.choose_public(state, history),
            "NO_GATE": _choose_truth(bitset, (base_a, base_b), global_truth),
            "THREE_FEATURE": _choose_truth(bitset, features3, truth3),
            "WRONG_DELAY": _choose_truth(bitset, wrong_gate[1:5], wrong_gate[5]),
            "NO_UPDATE": 0,
        }
        if cold.choose_public(state, history) != policies["DIRECT_GATE"]:
            cold_equal = False
        for name, action in policies.items():
            scores[name] += int(action == target)
    if not cold_equal:
        raise AssertionError("CB3_COLD_CHOICES_DIVERGE")
    digest = sha256(json.dumps(
        [(list(row.before), row.action, list(row.after), row.reward)
         for row in tape], separators=(",", ":")).encode("ascii")).hexdigest()
    return {
        "seed": seed,
        "public_earned_credit_count": len(observations),
        "public_action_tape_sha256": digest,
        "actual_content_pair_source_owner_only": list(actual_content),
        "actual_gate_pair_source_owner_only": list(actual_gate),
        "learned_content_pair": list(trained_content),
        "learned_gate_pair": list(trained_gate),
        "content_recovered": trained_content == actual_content,
        "gate_recovered": trained_gate == actual_gate,
        "global_fit_before_gate": global_score,
        "candidate_training_fit": features[6],
        "independent_symbolic_training_fit": b.fitted[0],
        "best_three_feature_training_fit": three_score,
        "wrong_delayed_binding_training_fit": wrong_gate[0],
        "unseen_correct_of_128": scores,
        "cold_checkpoint_sha256": sha256(a.snapshot()).hexdigest(),
        "checkpoint_bytes": len(a.snapshot()),
        "candidate_fit_seconds": a_seconds,
        "independent_exhaustive_fit_seconds": b_seconds,
        "total_world_seconds": time.perf_counter() - start,
    }

def study():
    started = time.perf_counter()
    records = [one_world(s) for s in source.WORLDS]
    means = {key: statistics.mean(item["unseen_correct_of_128"][key] / 128 for item in records)
             for key in ("DIRECT_GATE", "EXACT_FOUR", "NO_GATE", "THREE_FEATURE", "WRONG_DELAY", "NO_UPDATE")}
    d = [(r["unseen_correct_of_128"]["DIRECT_GATE"] -
          r["unseen_correct_of_128"]["EXACT_FOUR"]) / 128 for r in records]
    rng = random.Random(BOOTSTRAP_SEED)
    bs = sorted(statistics.mean(rng.choices(d, k=len(d))) for _ in range(RESAMPLES))
    content_recovered = sum(r["content_recovered"] for r in records)
    gate_recovered = sum(r["gate_recovered"] for r in records)
    frozen = {
        "candidate_content_pair_12_of_16": content_recovered >= 12,
        "candidate_gate_pair_12_of_16": gate_recovered >= 12,
        "candidate_accuracy_at_least_0_95": means["DIRECT_GATE"] >= .95,
        "strong_control_accuracy_at_least_0_95": means["EXACT_FOUR"] >= .95,
        "no_gate_accuracy_at_most_0_85": means["NO_GATE"] <= .85,
        "three_feature_accuracy_at_most_0_95": means["THREE_FEATURE"] <= .95,
        "candidate_minus_symbolic_at_least_0_02": statistics.mean(d) >= .02,
        "paired_bootstrap_lower95_gt_0_01": bs[24] > .01,
    }
    stable = [{k: v for k, v in r.items()
               if k not in ("candidate_fit_seconds", "independent_exhaustive_fit_seconds", "total_world_seconds")}
              for r in records]
    return {
        "schema": "yggdrasil.cb3.public-gate-discovery-result.v1",
        "classification": "PUBLIC_DEV_DISCOVERY_GATE_NO_SCIENTIFIC_UNIQUE_GAIN" if
        all(frozen[k] for k in list(frozen)[:6]) and not all(list(frozen.values())[6:])
        else "PUBLIC_DEV_MIXED_OR_NO_GO",
        "research_only": True,
        "science_pass": False,
        "protected_first_use": False,
        "worlds": len(records),
        "train_actual_public_actions": len(records) * source.TRAIN_ROWS,
        "train_delayed_credited_events": len(records) * learner.CREDITS,
        "unseen_actual_source_scored_actions": len(records) * source.TEST_ROWS * len(means),
        "means": means,
        "content_recovered": content_recovered,
        "gate_recovered": gate_recovered,
        "candidate_minus_strong_mean": statistics.mean(d),
        "paired_bootstrap_95": [bs[24], bs[975]],
        "frozen_predicates": frozen,
        "candidate_checkpoint_bytes": records[0]["checkpoint_bytes"],
        "total_candidate_fit_wall_seconds": sum(r["candidate_fit_seconds"] for r in records),
        "total_independent_symbolic_fit_wall_seconds": sum(r["independent_exhaustive_fit_seconds"] for r in records),
        "all_public_world_records_sha256": sha256(json.dumps(stable, sort_keys=True,
                                            separators=(",", ":")).encode("ascii")).hexdigest(),
        "elapsed_seconds": time.perf_counter() - started,
        "per_world": stable,
    }

if __name__ == "__main__":
    print(json.dumps(study(), indent=2, sort_keys=True))
