"""DG1 Sleep01 frozen prospective *synthetic DEV* wake/sleep physical experiment.

Unseen truth is used only by audit and never provided to learners. No
label-bearing dream is ever fitted. Reuses frozen HC09/HC10 *controls*.
"""
from __future__ import annotations

import hashlib
import json
import random
import sys
import time
import tracemalloc
from pathlib import Path

HERE = Path(__file__).resolve().parent
HC10 = HERE.parent / "dg1-hc10-20261113"
if str(HC10) not in sys.path:
    sys.path.insert(0, str(HC10))
from interbank_policy import base, choose as native_choose
from sleep_model import BayesianRunLength, SleepMemory, canonical

SEEDS = {
    "ABA": tuple(range(93001, 93009)),
    "stationary_majority": tuple(range(93009, 93017)),
    "OOD_cubic": tuple(range(93017, 93025)),
}
ARMS = ("sleep_native", "awake_hc09", "replay_no_context",
        "conventional_sleep", "bayes_runlength", "sleep_no_dream")
SLEEP_STEPS = frozenset((8, 16, 24, 32, 40, 48))


class World:
    """Bit-for-bit functional replication of HC11 World with frozen new seeds."""
    def __init__(self, seed, group):
        if group not in SEEDS or seed not in SEEDS[group]:
            raise ValueError("SLEEP01_UNREGISTERED_WORLD")
        self.group = group
        self.sign = []
        self.slope = []
        for action in range(4):
            rng = random.Random(seed * 101 + action * 31)
            self.sign.append(rng.randrange(2))
            self.slope.append(rng.randrange(2))
        self.causal = 0
        self.flips = 0

    def true_next_for_evaluator(self, state, action, phase):
        base.valid_state(state)
        base.valid_action(action)
        if type(phase) is not int or phase not in (0, 1):
            raise ValueError("SLEEP01_INVALID_PHASE")
        left = (state >> ((action + 1) % 4)) & 1
        right = (state >> ((action + 2) % 4)) & 1
        own = (state >> action) & 1
        if self.group == "stationary_majority":
            effect = int(left + right + own >= 2)
        elif self.group == "OOD_cubic":
            effect = int(state == 15)
        else:
            effect = left ^ right ^ (own & self.slope[action])
        effect ^= self.sign[action]
        if self.group == "ABA" and phase == 1:
            effect ^= 1
        return state ^ (effect << action)

    def charge_causal(self, state, action, phase):
        after = self.true_next_for_evaluator(state, action, phase)
        self.causal += 1
        return after

    def charge_flip(self, state, bit):
        base.valid_state(state)
        base.valid_action(bit)
        self.flips += 1
        return state ^ (1 << bit)


def arm_models():
    return {
        "sleep_native": SleepMemory("native", 2, True),
        "awake_hc09": base.DualRegimeCausalCells(),
        "replay_no_context": SleepMemory("native", 1, True),
        "conventional_sleep": SleepMemory("conventional", 2, True),
        "bayes_runlength": BayesianRunLength(),
        "sleep_no_dream": SleepMemory("native", 2, False),
    }


def audit(model, world, observed_pairs, phase):
    counts = {k: 0 for k in ("correct", "wrong_confident", "abstained",
                             "unseen_correct", "unseen_wrong_confident",
                             "unseen_abstained")}
    for s in range(16):
        for a in range(4):
            truth = world.true_next_for_evaluator(s, a, phase)
            prediction = model.predict(s, a)
            outcome = "abstained" if prediction is None else (
                "correct" if prediction == truth else "wrong_confident")
            counts[outcome] += 1
            if (s, a) not in observed_pairs:
                counts["unseen_" + outcome] += 1
    assert sum(counts[k] for k in ("correct", "wrong_confident", "abstained")) == 64
    return counts


def cold_clone(model):
    raw = model.snapshot()
    if isinstance(model, SleepMemory):
        restored = SleepMemory.restore(raw)
    elif isinstance(model, BayesianRunLength):
        restored = BayesianRunLength.restore(raw)
    else:
        restored = base.DualRegimeCausalCells.restore(raw)
    assert restored.snapshot() == raw
    for s in range(16):
        for a in range(4):
            assert model.predict(s, a) == restored.predict(s, a)
    return raw


def one_world(seed, group):
    world = World(seed, group)
    models = arm_models()
    shadow = base.DualRegimeCausalCells()
    state = seed % 16
    fitted = set()
    flips = 0
    steps = 40 if group == "ABA" else 48
    trace = []
    sleep_ns = {arm: 0 for arm in ARMS}
    observe_ns = {arm: 0 for arm in ARMS}
    checkpoints = {}
    started = time.perf_counter_ns()
    for step in range(steps):
        phase = int(group == "ABA" and 16 <= step < 32)
        kind, action = native_choose(shadow, state, flips, 8)
        before = state
        if kind == "causal":
            state = world.charge_causal(before, action, phase)
            shadow.observe(before, action, state)
            fitted.add((before, action))
            for arm, model in models.items():
                t0 = time.perf_counter_ns()
                model.observe(before, action, state)
                observe_ns[arm] += time.perf_counter_ns() - t0
        elif kind == "flip":
            if flips >= 8:
                raise AssertionError("SLEEP01_BUDGET_EXCEEDED")
            state = world.charge_flip(before, action)
            flips += 1
        else:
            raise AssertionError("SLEEP01_UNKNOWN_ACTION")
        trace.append([before, kind, action, state])
        if step + 1 in SLEEP_STEPS:
            for arm, model in models.items():
                if isinstance(model, SleepMemory):
                    t0 = time.perf_counter_ns()
                    model.sleep()
                    sleep_ns[arm] += time.perf_counter_ns() - t0
        if group == "ABA" and step + 1 in (16, 32, 40):
            checkpoints[str(step + 1)] = {arm: audit(model, world, fitted,
                int(step + 1 == 32)) for arm, model in models.items()}
    assert world.causal + world.flips == steps and flips == world.flips <= 8
    assert shadow.observations == world.causal
    raw_checkpoints = {arm: cold_clone(m) for arm, m in models.items()}
    final = {arm: audit(m, world, fitted, 0) for arm, m in models.items()}
    assert final["sleep_native"] == final["sleep_no_dream"], (
        "Unverified dream proposal changed model outputs")
    assert (not isinstance(models["sleep_native"], SleepMemory) or
            len(models["sleep_native"].dream_proposals) <= 8)
    for arm in ARMS:
        if group == "ABA":
            assert checkpoints["40"][arm] == final[arm]
    return {
        "seed": seed, "group": group, "final": final,
        "checkpoints": checkpoints if group == "ABA" else {},
        "charged_real_actions": steps,
        "charged_mechanism_actions": world.causal,
        "charged_exogenous_flips": world.flips,
        "distinct_fitted_pairs": len(fitted),
        "trajectory_sha256": hashlib.sha256(canonical(trace)).hexdigest(),
        "snapshot_bytes": {arm: len(raw) for arm, raw in raw_checkpoints.items()},
        "checkpoint_sha256": {arm: hashlib.sha256(raw).hexdigest()
                              for arm, raw in raw_checkpoints.items()},
        "sleep_ns": sleep_ns, "observe_ns": observe_ns,
        "sleep_unexplained": models["sleep_native"].unexplained,
        "dream_proposals_unverified": len(models["sleep_native"].dream_proposals),
        "whole_world_ns": time.perf_counter_ns() - started,
    }


def run():
    # Trace one representative world. Tracing the entire beam search changes
    # its cost by orders of magnitude; this is a bounded sample, not a claim
    # that full-process peak memory is measured or OS-independent.
    first_group = next(iter(SEEDS))
    first_seed = SEEDS[first_group][0]
    tracemalloc.start()
    first_world = one_world(first_seed, first_group)
    _, heap_peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    worlds = [first_world] + [
        one_world(seed, group) for group, seeds in SEEDS.items()
        for seed in seeds if (group, seed) != (first_group, first_seed)]
    metrics = ("correct", "wrong_confident", "abstained", "unseen_correct",
               "unseen_wrong_confident", "unseen_abstained")
    agg = {
        group: {
            arm: {k: sum(w["final"][arm][k] for w in worlds if w["group"] == group)
                  for k in metrics}
            for arm in ARMS
        } for group in SEEDS
    }
    def g(group, arm, key):
        return agg[group][arm][key]
    primary = (
        g("ABA", "sleep_native", "correct") >= 64 and
        g("ABA", "sleep_native", "wrong_confident") <= 8 and
        g("ABA", "sleep_native", "unseen_correct") >= 24 and
        g("stationary_majority", "sleep_native", "correct") >= 128 and
        g("stationary_majority", "sleep_native", "wrong_confident") <= 8 and
        g("OOD_cubic", "sleep_native", "wrong_confident") <= 8 and
        g("ABA", "sleep_native", "correct") > g("ABA", "awake_hc09", "correct") and
        g("ABA", "sleep_native", "wrong_confident") <=
        g("ABA", "awake_hc09", "wrong_confident"))
    conventional_win = sum(
        g(group, "conventional_sleep", "correct") >= g(group, "sleep_native", "correct")
        and g(group, "conventional_sleep", "wrong_confident") <=
        g(group, "sleep_native", "wrong_confident") for group in SEEDS) >= 2
    coverage_improved = g("ABA", "sleep_native", "correct") > g("ABA", "awake_hc09", "correct")
    classification = ("DEV_SIGNAL_NOT_SCIENCE" if primary else
                      "MIXED_DEV" if coverage_improved else "NEGATIVE_DEV")
    return {
        "schema": "ygg.dg1-sleep01.synthetic-dev.v1",
        "classification": classification, "primary_pass": primary,
        "scientific_acceptance": "UNVERIFIED",
        "conventional_tie_or_better": conventional_win,
        "same_trajectory_per_arm": True, "matched_total_compute": False,
        "frozen_seed_count": sum(map(len, SEEDS.values())),
        "charged_actions_shared_total": sum(w["charged_real_actions"] for w in worlds),
        "total_observation_exposures": sum(w["charged_mechanism_actions"] for w in worlds) * len(ARMS),
        "python_peak_traced_bytes_first_world_only": heap_peak,
        "aggregate": agg, "worlds": worlds,
    }


if __name__ == "__main__":
    print(json.dumps(run(), sort_keys=True, indent=2))
