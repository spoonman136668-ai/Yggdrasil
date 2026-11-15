"""Frozen SFI-03 PUBLIC development harness with isolated source-owner oracle.

This is NOT original held science, an accepted model or an independent
blinded evaluator. No FKP17 protected source is instantiated or read.
"""
from __future__ import annotations

import hashlib
import importlib.util
import json
from pathlib import Path
import random
import statistics
import sys
import time

import operator_induction as learner

HERE = Path(__file__).resolve().parent
SOURCE_BLOB = "9aebb3e545783a677c3c2de69b97e87e7c74cf87"
OLD_BLOB = "82367dd5fdcb76361a06caeec7da7c4b4dac86bb"
ARMS = ("DIRECT_NEW", "SYMBOLIC_NEW", "OLD_FIXED", "EXACT_TABLE",
        "WRONG_CREDIT", "RANDOM", "ORACLE")
BOOTSTRAP_SEED = 20261115


def _load_pinned(relative, blob, alias):
    path = (HERE / relative).resolve()
    raw = path.read_bytes()
    actual = hashlib.sha1(
        b"blob " + str(len(raw)).encode("ascii") + b"\x00" + raw
    ).hexdigest()
    if actual != blob:
        raise RuntimeError(f"SFI03_PINNED_SOURCE_MISMATCH:{alias}:{actual}")
    spec = importlib.util.spec_from_file_location(alias, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[alias] = module
    spec.loader.exec_module(module)
    return module


def _old_grammar_representability(source, old):
    # Source-owner offline map check, never supplied to candidate, symbolic or
    # pre-outcome action selection. Covers all 8×8×2 public parent/context cases.
    cases = tuple((p, q, c) for p in range(8) for q in range(8) for c in range(2))
    old_sigs = {bytes(old.execute_program(program, p, q, c) for p, q, c in cases)
                for program in old.CATALOG}
    return [
        (family, shift, bytes(source.target(family, shift, p, q, c) for p, q, c in cases) in old_sigs)
        for family in range(4) for shift in range(8)
    ]


class OldOnly:
    def __init__(self, old):
        self._model = old.DirectMicrofeedback()
        self.exhausted = False

    def observe_public(self, row):
        if self.exhausted:
            return
        try:
            self._model.observe_public(row)
        except ValueError as exc:
            if "CONTRADICTORY_EVIDENCE" not in str(exc):
                raise
            self.exhausted = True

    def choose_public(self, state, history):
        return 0 if self.exhausted else self._model.choose_public(state, history)


def _receipt(rows):
    raw = json.dumps([
        [list(r.before), r.action, list(r.after), r.reward, r.done,
         [[list(p.before), p.action, p.reward, list(p.after), p.done]
          for p in r.history]] for r in rows
    ], separators=(",", ":"), sort_keys=True).encode("ascii")
    return hashlib.sha256(raw).hexdigest()


def one_world(source, old, seed):
    scores, goals, hypotheses = {}, {}, {}
    tapes = set()
    failure = {}
    timing = {}
    for name in ARMS:
        started = time.perf_counter()
        world = source.PublicWorld(seed)
        model = {
            "DIRECT_NEW": lambda: learner.DirectMicrofeedbackExpansion(),
            "SYMBOLIC_NEW": lambda: learner.IndependentExactBoolean(),
            "OLD_FIXED": lambda: OldOnly(old),
            "EXACT_TABLE": lambda: old.ExactContextTable(),
            "WRONG_CREDIT": lambda: old.WrongCredit(),
        }[name]() if name in ("DIRECT_NEW", "SYMBOLIC_NEW", "OLD_FIXED",
                             "EXACT_TABLE", "WRONG_CREDIT") else None
        rows = [world.step(action) for action in source.exploration(seed)]
        tapes.add(_receipt(rows))
        if model is not None:
            for row in rows:
                model.observe_public(row)
        if name in ("DIRECT_NEW", "SYMBOLIC_NEW"):
            hypotheses[name] = model.hypotheses
        if name == "OLD_FIXED":
            failure["old_exhausted_after_24"] = model.exhausted
        random_control = random.Random(seed ^ 0x5F103)
        total = 0.0
        done_count = 0
        for _ in range(source.SCORE):
            if name == "ORACLE":
                action = source.oracle_action(world)
            elif name == "RANDOM":
                action = random_control.randrange(8)
            else:
                action = model.choose_public(world.state, world.public_history())
            row = world.step(action)
            total += row.reward
            done_count += int(row.done)
            if model is not None:
                model.observe_public(row)
        if name == "OLD_FIXED":
            failure["old_exhausted_after_scoring"] = model.exhausted
        scores[name] = total
        goals[name] = done_count
        timing[name] = time.perf_counter() - started
    if len(tapes) != 1:
        raise AssertionError("SFI03_PUBLIC_EXPLORATION_DATA_NOT_EQUAL")
    if hypotheses["DIRECT_NEW"] != hypotheses["SYMBOLIC_NEW"]:
        raise AssertionError("SFI03_EQUAL_PROGRAM_SUPPORT_MISMATCH")
    return {
        "seed": seed, "common_public_tape_sha256": next(iter(tapes)),
        "earned_16_step_returns": scores, "goal_events": goals,
        "support_after_24": hypotheses, "old_representability": failure,
        "wall_seconds": timing
    }


def study():
    start = time.perf_counter()
    source = _load_pinned("public_source.py", SOURCE_BLOB, "sfi03_source_owner")
    old = _load_pinned("../SFI-02/microfeedback.py", OLD_BLOB, "sfi02_old_fixed_control")
    representable = _old_grammar_representability(source, old)
    worlds = [one_world(source, old, seed) for seed in source.WORLD_SEEDS]
    means = {name: statistics.mean(w["earned_16_step_returns"][name] for w in worlds)
             for name in ARMS}
    goal_worlds = {name: sum(w["goal_events"][name] > 0 for w in worlds)
                   for name in ARMS}
    paired = [w["earned_16_step_returns"]["DIRECT_NEW"] -
              w["earned_16_step_returns"]["SYMBOLIC_NEW"] for w in worlds]
    rng = random.Random(BOOTSTRAP_SEED)
    bs = sorted(statistics.mean(rng.choices(paired, k=len(worlds))) for _ in range(1000))
    compatible8 = None  # Not computed; do not assert source-identifiability pass.
    criteria = {
        "outside_previous_grammar_at_least_24": sum(not flag for _, _, flag in representable) >= 24,
        "oracle_goal_worlds_at_least_24": goal_worlds["ORACLE"] >= 24,
        "random_goal_worlds_at_most_8": goal_worlds["RANDOM"] <= 8,
        "oracle_reward_headroom_at_least_2": means["ORACLE"] - means["RANDOM"] >= 2,
        "candidate_goal_worlds_at_least_12": goal_worlds["DIRECT_NEW"] >= 12,
        "candidate_mean_reward_nonnegative": means["DIRECT_NEW"] >= 0,
        "candidate_beats_old_fixed_by_1": means["DIRECT_NEW"] - means["OLD_FIXED"] >= 1,
        "candidate_beats_exact_symbolic_by_0_10": statistics.mean(paired) >= .10,
        "paired_lower95_gt_0_02": bs[24] > .02
    }
    stable = [{k:v for k,v in row.items() if k!="wall_seconds"} for row in worlds]
    stable_sha = hashlib.sha256(json.dumps(stable, sort_keys=True,
                                         separators=(",", ":")).encode("ascii")).hexdigest()
    return {
        "classification": "PUBLIC_DEV_NO_GO_OR_UNVERIFIED" if not all(criteria.values()) else
                          "PUBLIC_DEV_THRESHOLDS_MET_NOT_SCIENCE",
        "frozen_predicates": criteria,
        "source_private_first_use": False,
        "worlds": len(worlds), "actual_simulated_source_actions": len(worlds)*len(ARMS)*40,
        "new_forms_outside_previous_4096_grammar": sum(not flag for _,_,flag in representable),
        "old_grammar_representability": representable,
        "source_ambiguity_at_8": compatible8,
        "means": means, "goal_worlds": goal_worlds,
        "candidate_minus_symbolic_mean": statistics.mean(paired),
        "candidate_minus_symbolic_bootstrap_95": [bs[24], bs[975]],
        "earned_source_records_sha256": stable_sha,
        "worlds_detail": stable,
        "wall_seconds_total": time.perf_counter()-start
    }


if __name__ == "__main__":
    print(json.dumps(study(), indent=2, sort_keys=True))
