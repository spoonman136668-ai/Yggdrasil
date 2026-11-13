"""Frozen HC11 public action-consequence confidence experiment.

No hidden regime/true transition is passed to a learner. Truth is accessed
only when charging one physical action and by evaluator-only audit calls.
"""
from __future__ import annotations

import hashlib
import json
import random
import time
import tracemalloc

from gate import EvidenceGate, base, control, native_choose, conventional_choose

SEEDS = {
    "ABA": tuple(range(91001, 91009)),
    "stationary_majority": tuple(range(91009, 91017)),
    "OOD_cubic": tuple(range(91017, 91025)),
}
ARMS = ("native_gate2", "conventional_gate2", "native_gate1",
        "native_ungated", "conventional_ungated")


class World:
    def __init__(self, seed, group):
        if group not in SEEDS or seed not in SEEDS[group]:
            raise ValueError("HC11_UNREGISTERED_WORLD")
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
            raise ValueError("HC11_INVALID_PHASE")
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


def audit(model, world, seen, phase):
    result = {key: 0 for key in (
        "correct", "wrong_confident", "abstained", "unseen_correct",
        "unseen_wrong_confident", "unseen_abstained")}
    for state in range(16):
        for action in range(4):
            true = world.true_next_for_evaluator(state, action, phase)
            got = model.predict(state, action)
            outcome = ("abstained" if got is None else
                       "correct" if got == true else "wrong_confident")
            result[outcome] += 1
            if (state, action) not in seen:
                result["unseen_" + outcome] += 1
    assert sum(result[k] for k in ("correct", "wrong_confident", "abstained")) == 64
    return result


def arm_model(arm):
    if arm == "native_gate2":
        return EvidenceGate("native", 2)
    if arm == "conventional_gate2":
        return EvidenceGate("conventional", 2)
    if arm == "native_gate1":
        return EvidenceGate("native", 1)
    if arm == "native_ungated":
        return base.DualRegimeCausalCells()
    if arm == "conventional_ungated":
        return control.ConventionalContextModel()
    raise ValueError("HC11_UNKNOWN_ARM")


def choose(arm, model, state, flips):
    if isinstance(model, EvidenceGate):
        return model.choose(state, flips, 8)
    if arm == "native_ungated":
        return native_choose(model, state, flips, 8)
    return conventional_choose(model, state, flips, 8)


def one_arm(seed, group, arm):
    world = World(seed, group)
    model = arm_model(arm)
    state = seed % 16
    fitted = set()
    ledger = []
    decisions_ns = 0
    checkpoints = {}
    flips = 0
    steps = 40 if group == "ABA" else 48
    start = time.perf_counter_ns()
    for step in range(steps):
        phase = int(group == "ABA" and 16 <= step < 32)
        start_choice = time.perf_counter_ns()
        kind, action = choose(arm, model, state, flips)
        decisions_ns += time.perf_counter_ns() - start_choice
        before = state
        if kind == "causal":
            state = world.charge_causal(before, action, phase)
            model.observe(before, action, state)
            fitted.add((before, action))
        elif kind == "flip":
            if flips >= 8:
                raise AssertionError("HC11_UNCHARGED_FLIP")
            state = world.charge_flip(before, action)
            flips += 1
            # A forced physical state flip is not a mechanism observation.
        else:
            raise AssertionError("HC11_UNKNOWN_PHYSICAL_ACTION")
        ledger.append([before, kind, action, state])
        if group == "ABA" and step + 1 in (16, 32, 40):
            checkpoints[str(step + 1)] = audit(
                model, world, fitted, int(step + 1 == 32))
    whole_ns = time.perf_counter_ns() - start
    assert world.causal + world.flips == steps and flips == world.flips <= 8
    actual = (model.model if isinstance(model, EvidenceGate) else model)
    assert (actual.observations if isinstance(actual, base.DualRegimeCausalCells)
            else actual.n) == world.causal
    snap = model.snapshot()
    if isinstance(model, EvidenceGate):
        restored = EvidenceGate.restore(snap)
    elif arm == "native_ungated":
        restored = base.DualRegimeCausalCells.restore(snap)
    else:
        restored = control.ConventionalContextModel.restore(snap)
    assert snap == restored.snapshot() and len(snap) <= 4096
    assert all(model.predict(s, a) == restored.predict(s, a)
               for s in range(16) for a in range(4))
    final_phase = 0
    final = audit(model, world, fitted, final_phase)
    if group == "ABA":
        assert final == checkpoints["40"]
    return {
        "final": final,
        "intermediate_evaluator_only": checkpoints,
        "charged_real_actions": steps,
        "charged_mechanism_actions": world.causal,
        "charged_exogenous_flips": world.flips,
        "distinct_fitted_pairs": len(fitted),
        "witness_entries": len(model.witness) if isinstance(model, EvidenceGate) else 0,
        "witness_epoch_resets": model.epoch if isinstance(model, EvidenceGate) else 0,
        "context_changes": actual.reactivations if hasattr(actual, "reactivations") else actual.switches,
        "unexplained_events": actual.unresolved_events if hasattr(actual, "unresolved_events") else actual.unexplained,
        "snapshot_bytes": len(snap),
        "cold_restore_identical": True,
        "ledger_sha256": hashlib.sha256(base.encode(ledger)).hexdigest(),
        "decision_ns": decisions_ns,
        "whole_learning_ns": whole_ns,
    }


def one_world(seed, group):
    arms = {a: one_arm(seed, group, a) for a in ARMS}
    expected = 40 if group == "ABA" else 48
    assert all(r["charged_real_actions"] == expected for r in arms.values())
    return {"seed": seed, "group": group, "arms": arms}


def run():
    tracemalloc.start()
    worlds = [one_world(seed, group) for group, seeds in SEEDS.items() for seed in seeds]
    _, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    keys = ("correct", "wrong_confident", "abstained",
            "unseen_correct", "unseen_wrong_confident", "unseen_abstained")
    aggregates = {
        group: {
            arm: {k: sum(w["arms"][arm]["final"][k] for w in worlds
                         if w["group"] == group) for k in keys}
            for arm in ARMS
        } for group in SEEDS
    }
    def score(group, arm, key):
        return aggregates[group][arm][key]
    primary = (
        score("ABA", "native_gate2", "correct") >= 32 and
        score("ABA", "native_gate2", "wrong_confident") == 0 and
        score("stationary_majority", "native_gate2", "correct") >= 64 and
        score("stationary_majority", "native_gate2", "wrong_confident") == 0 and
        score("OOD_cubic", "native_gate2", "wrong_confident") == 0 and
        score("ABA", "native_gate2", "wrong_confident") <
        score("ABA", "native_ungated", "wrong_confident") and
        score("OOD_cubic", "native_gate2", "wrong_confident") <
        score("OOD_cubic", "native_ungated", "wrong_confident")
    )
    errors_reduced = (
        score("ABA", "native_gate2", "wrong_confident") <
        score("ABA", "native_ungated", "wrong_confident") and
        score("OOD_cubic", "native_gate2", "wrong_confident") <
        score("OOD_cubic", "native_ungated", "wrong_confident"))
    classification = ("DEV_SAFETY_COVERAGE_SIGNAL_NOT_SCIENCE" if primary else
                      "MIXED_DEV" if errors_reduced else "NEGATIVE_DEV")
    conventional_tie_or_better = all(
        score(g, "conventional_gate2", "correct") >= score(g, "native_gate2", "correct")
        and score(g, "conventional_gate2", "wrong_confident") <=
        score(g, "native_gate2", "wrong_confident") for g in SEEDS)
    return {
        "schema": "ygg.dg1-hc11.physical-witness-gate-dev.v1",
        "classification": classification,
        "scientific_acceptance": "UNVERIFIED",
        "primary_pass": primary,
        "conventional_tie_or_better": conventional_tie_or_better,
        "same_physical_action_budget": True,
        "matched_total_compute": False,
        "additional_witness_memory_vs_ungated": True,
        "aggregate": aggregates,
        "charged_actions_all_arms": sum(
            w["arms"][a]["charged_real_actions"] for w in worlds for a in ARMS),
        "python_peak_traced_bytes": peak,
        "worlds": worlds,
    }


if __name__ == "__main__":
    print(json.dumps(run(), sort_keys=True, indent=2))
