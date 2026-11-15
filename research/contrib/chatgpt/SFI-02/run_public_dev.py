"""SFI-02 frozen PUBLIC developmental policy comparison. NOT scientific held test.

Models see exclusively current publicly observable state/history, plus reward
only AFTER their action. Source evaluator is isolated in this harness; only
its private oracle reference can inspect a law, never a learning arm.
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

from microfeedback import (DirectMicrofeedback, ConventionalExactSymbolic,
                           ExactContextTable, WrongCredit)

SOURCE_BLOB = "643abf8af9047ef888a0d9952f71df2d2b18dcdb"
WORLD_COUNT = 32
SCORE_STEPS = 16
SEED = 20261115
ARMS = ("MICROFEEDBACK", "EXACT_SYMBOLIC", "CONTEXT_TABLE", "WRONG_CREDIT", "PUBLIC_RANDOM", "ORACLE_UPPER")


def _load_source():
    location = Path(__file__).resolve().parent.parent / "SFI-01" / "source_audit.py"
    if not location.exists():
        # Local authoring source path is independent of the checked-out source.
        location = Path(__file__).resolve().parent.parent / "sfi01_work" / "source_audit.py"
    raw = location.read_bytes()
    git_sha = hashlib.sha1(b"blob " + str(len(raw)).encode("ascii") + b"\x00" + raw).hexdigest()
    if git_sha != SOURCE_BLOB:
        raise RuntimeError("SFI02_PINNED_SOURCE_BLOB_MISMATCH")
    spec = importlib.util.spec_from_file_location("sfi01_pinned_source_for_source_owner", location)
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def _public_tape(source, seed, world):
    data = []
    for action in source.exploration(seed):
        data.append(world.step(action))
    raw = json.dumps([[list(r.before), r.action, list(r.after), r.reward, r.done,
                       [[list(h.before), h.action, h.reward, list(h.after), h.done]
                        for h in r.history]] for r in data],
                     sort_keys=True, separators=(",", ":")).encode("ascii")
    return data, hashlib.sha256(raw).hexdigest()


def world_comparison(source, seed):
    arm_scores = {}
    arm_goals = {}
    public_custody = set()
    model_support = {}
    process_seconds = {}
    for label in ARMS:
        started = time.perf_counter()
        world = source._SourceWorld(seed)
        model = ({
            "MICROFEEDBACK": DirectMicrofeedback,
            "EXACT_SYMBOLIC": ConventionalExactSymbolic,
            "CONTEXT_TABLE": ExactContextTable,
            "WRONG_CREDIT": WrongCredit,
        }[label]() if label in ("MICROFEEDBACK", "EXACT_SYMBOLIC", "CONTEXT_TABLE", "WRONG_CREDIT") else None)
        tape, common = _public_tape(source, seed, world)
        public_custody.add(common)
        if model is not None:
            for public in tape:
                model.observe_public(public)
        if label in ("MICROFEEDBACK", "EXACT_SYMBOLIC"):
            model_support[label] = model.hypothesis_count
        rng = random.Random((seed ^ 0x5F102) + SEED)
        goal_count = 0
        earned = 0.0
        for _ in range(SCORE_STEPS):
            if label == "ORACLE_UPPER":
                chosen = source._choose_oracle(world)
            elif label == "PUBLIC_RANDOM":
                chosen = rng.randrange(8)
            else:
                chosen = model.choose_public(world.state, world.public_history())
            # Real consequence is obtained only *after* choosing an action.
            public = world.step(chosen)
            earned += public.reward
            goal_count += int(public.done)
            if model is not None:
                model.observe_public(public)
        arm_scores[label] = earned
        arm_goals[label] = goal_count
        process_seconds[label] = time.perf_counter() - started
    if len(public_custody) != 1:
        raise RuntimeError("SFI02_COMMON_PUBLIC_TAPE_MISMATCH")
    return {"seed": seed, "public_tape_sha256": next(iter(public_custody)),
            "returns": arm_scores, "goal_events": arm_goals,
            "hypothesis_count_after_24": model_support,
            "process_seconds": process_seconds}


def study():
    source = _load_source()
    started = time.perf_counter()
    worlds = [world_comparison(source, seed) for seed in range(WORLD_COUNT)]
    mean = {label: statistics.mean(w["returns"][label] for w in worlds) for label in ARMS}
    goals = {label: sum(w["goal_events"][label] > 0 for w in worlds) for label in ARMS}
    gap = [w["returns"]["MICROFEEDBACK"] - w["returns"]["EXACT_SYMBOLIC"] for w in worlds]
    random_source = random.Random(SEED)
    replicates = sorted(statistics.mean(random_source.choices(gap, k=WORLD_COUNT)) for _ in range(1000))
    lower, upper = replicates[24], replicates[975]
    criteria = {
        "candidate_vs_symbolic_delta_min_0_10": statistics.mean(gap) >= 0.10,
        "candidate_vs_symbolic_bootstrap_lower_gt_0_02": lower > 0.02,
        "candidate_goal_worlds_at_least_8": goals["MICROFEEDBACK"] >= 8,
        "candidate_earned_mean_at_least_zero": mean["MICROFEEDBACK"] >= 0,
        "candidate_vs_tabular_min_1": mean["MICROFEEDBACK"] - mean["CONTEXT_TABLE"] >= 1.0,
    }
    stable = [{k: v for k, v in item.items() if k != "process_seconds"} for item in worlds]
    raw = json.dumps(stable, sort_keys=True, separators=(",", ":")).encode("ascii")
    per_arm_time = {label: sum(w["process_seconds"][label] for w in worlds) for label in ARMS}
    return {
        "schema": "yggdrasil.sfi02.sourceblind-public-dev-result.v1",
        "study": "SFI-02-LOCAL-MICROFEEDBACK-COMPOSITIONAL-PROGRAM-INDUCTION",
        "classification": ("PUBLIC_DEV_GATE_MET_BUT_NOT_INDEPENDENT_SCIENCE" if all(criteria.values())
                           else "PUBLIC_DEV_NO_GO_OR_INCOMPLETE"),
        "original_held_first_use": False,
        "preregistered_scientific_pass": False,
        "worlds": WORLD_COUNT,
        "arms": len(ARMS),
        "common_exploration_steps_per_arm_world": 24,
        "actual_scored_action_steps_per_arm_world": SCORE_STEPS,
        "total_real_source_steps": WORLD_COUNT * len(ARMS) * (24 + SCORE_STEPS),
        "means": mean,
        "goal_world_counts": goals,
        "candidate_minus_exact_symbolic_per_world": gap,
        "candidate_minus_exact_symbolic_mean": statistics.mean(gap),
        "paired_bootstrap_95": [lower, upper],
        "candidate_vs_table_mean": mean["MICROFEEDBACK"] - mean["CONTEXT_TABLE"],
        "frozen_predicates": criteria,
        "all_predicates_met": all(criteria.values()),
        "hypothesis_support_after_24": {a: [x["hypothesis_count_after_24"][a] for x in worlds]
                                         for a in ("MICROFEEDBACK", "EXACT_SYMBOLIC")},
        "raw_parameter_bytes": {"MICROFEEDBACK": DirectMicrofeedback.raw_parameter_bytes,
                                "EXACT_SYMBOLIC": ConventionalExactSymbolic.raw_parameter_bytes,
                                "CONTEXT_TABLE_MAX": ExactContextTable.raw_parameter_ceiling_bytes,
                                "WRONG_CREDIT": WrongCredit.raw_parameter_bytes},
        "per_arm_source_and_model_wall_seconds": per_arm_time,
        "total_wall_seconds": time.perf_counter() - started,
        "public_per_world_scores_sha256": hashlib.sha256(raw).hexdigest(),
        "world_details": stable,
    }


if __name__ == "__main__":
    print(json.dumps(study(), indent=2, sort_keys=True))
