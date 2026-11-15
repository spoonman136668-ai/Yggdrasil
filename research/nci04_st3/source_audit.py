"""Frozen ST3 source-only causal-law identifiability preflight.

Runs only training-law and training-seed in-house DEV task source.
No candidate, control, training, held-development law or protected first-use.
This is a screening result, not scientific generalization evidence.
"""
from collections import defaultdict
from hashlib import sha256
import argparse
import json
from pathlib import Path
import subprocess
import time

from research.nci04_st3.causal_switchboard import (
    HiddenLawSwitchboard, choose_blind_action, bits, byte, source_mask,
    STEPS, _canonical
)

PREREG_SHA = "63133626dbd914c2d525dbd7358c87fdcfcabdc7"
PREREG_BLOB = "ce51862f6b5af6a130b6ad93c30f019131bfeb16"
PROTOCOL = Path(__file__).with_name("frozen_protocol.json")
TRAIN_LAWS = (3, 5, 7, 11, 13, 17, 19, 23)
TRAIN_SEEDS = tuple(range(100, 112))
HELD_LAWS = (29, 31, 37, 41)
HELD_SEEDS = tuple(range(201, 209))


def verify_prereg():
    p = json.loads(PROTOCOL.read_text("utf-8"))
    if (p.get("schema") != "yggdrasil.nci04.st3.intervention-law.dev.v1" or
        p.get("status") !=
            "FROZEN_BEFORE_SOURCE_MODEL_IMPLEMENTATION_OR_OUTCOME" or
        tuple(p["source"]["train_laws"]) != TRAIN_LAWS or
        tuple(p["source"]["train_seeds"]) != TRAIN_SEEDS or
        tuple(p["source"]["held_dev_laws"]) != HELD_LAWS or
        tuple(p["source"]["held_dev_seeds"]) != HELD_SEEDS or
        p["source"]["steps_per_episode"] != STEPS or
        p["source"]["no_protected_first_use"] is not True or
        p["bounds"]["merge"] is not False or
        p["bounds"]["scientific_first_use"] is not False):
        raise ValueError("ST3_SOURCE_FROZEN_PREREG_MISMATCH")
    git_blob = subprocess.check_output(
        ["git", "rev-parse", "HEAD:research/nci04_st3/frozen_protocol.json"],
        text=True
    ).strip()
    if git_blob != PREREG_BLOB:
        raise ValueError("ST3_SOURCE_FROZEN_BLOB_DRIFT")
    if subprocess.run(
        ["git", "merge-base", "--is-ancestor", PREREG_SHA, "HEAD"],
        check=False
    ).returncode:
        raise ValueError("ST3_SOURCE_PREREG_ANCESTOR_MISSING")
    return p


def deterministic_traces(laws=TRAIN_LAWS, seeds=TRAIN_SEEDS):
    # Public inputs are the ONLY inputs that will eventually reach models.
    by_input = defaultdict(set)
    receipts = []
    total_steps = 0
    action_totals = [0] * 4
    for law in laws:
        for seed in seeds:
            world = HiddenLawSwitchboard(law, seed)
            trace = sha256()
            prior_change = (0,) * 8
            for t in range(STEPS):
                before = world.public()
                action = choose_blind_action(seed, t)
                after, target = world.step(action)
                if tuple(int(a != b) for a,b in zip(before,after)) != target:
                    raise ValueError("ST3_REAL_ACTION_CONSEQUENCE_INCONSISTENT")
                # Evidence group uses exact bytes (not hash collisions);
                # hidden law is compared by evaluator after all outcomes.
                by_input[(before, action)].add((law,target))
                trace.update(bytes((*before, *prior_change, action, *after, *target)))
                action_totals[action] += 1
                total_steps += 1
                prior_change = target
                if t == 11:
                    snap = world.snapshot()
                    world = HiddenLawSwitchboard.restore(snap)
                    if world.snapshot() != snap:
                        raise ValueError("ST3_SOURCE_COLD_RESTORE_DRIFT")
            receipts.append({
                "law_id_evaluator_only": law,
                "seed_source_only": seed,
                "steps": STEPS,
                "original_action_public_consequences_sha256": trace.hexdigest(),
                "learner_or_held_score_computed": False,
            })
    strict_alias_groups = 0
    distinct_contrasting_law_pairs = set()
    for key, evidence in by_input.items():
        laws_by_result = defaultdict(set)
        for law, outcome in evidence:
            laws_by_result[outcome].add(law)
        if len(laws_by_result) < 2:
            continue
        different = list(laws_by_result.values())
        pairs = [
            tuple(sorted((left,right)))
            for i, lhs in enumerate(different)
            for rhs in different[i+1:]
            for left in lhs for right in rhs if left != right
        ]
        if pairs:
            strict_alias_groups += 1
            distinct_contrasting_law_pairs.update(pairs)
    return {
        "episodes": len(receipts), "source_steps": total_steps,
        "action_totals": action_totals,
        "unique_same_public_and_action_different_hidden_law_outcome_keys":
            strict_alias_groups,
        "distinct_contrasting_law_pairs": len(distinct_contrasting_law_pairs),
        "source_trace_sha256": sha256(_canonical(receipts).encode("utf-8")).hexdigest(),
        "source_receipts": receipts
    }


def delayed_intervention_counterfactual(laws=TRAIN_LAWS):
    # Only SOURCE internals in this diagnostic; the model receives no
    # paired private worlds or counterfactual truth. These are not training.
    contrasted = []
    for law in laws:
        a = HiddenLawSwitchboard(law, 100)
        b = HiddenLawSwitchboard(law, 100)
        a.step(2)  # schedules delayed effect but has no immediate mask
        b.step(3)  # does not schedule it
        if a.public() != b.public():
            raise ValueError("ST3_DELAY_PROBE_HAS_IMMEDIATE_EFFECT")
        next_a, outcome_a = a.step(3)
        next_b, outcome_b = b.step(3)
        # Both worlds had same full public state and chosen current action;
        # only the PRIOR intervention changed their hidden pending cause.
        if (next_a != next_b) != (source_mask(law,2) != 0):
            raise ValueError("ST3_DELAYED_SOURCE_CONSEQUENCE_DRIFT")
        if next_a != next_b:
            contrasted.append(law)
    return contrasted


def stage0_verdict(source, delayed):
    if (type(source) is not dict or
        type(delayed) is not list or
        type(source.get("unique_same_public_and_action_different_hidden_law_outcome_keys")) is not int):
        raise ValueError("ST3_SOURCE_INVALID_HEADROOM_RECEIPT")
    checks = {
        "at_least_8_exact_public_action_alias_keys":
            source["unique_same_public_and_action_different_hidden_law_outcome_keys"] >= 8,
        "at_least_2_laws_with_delayed_counterfactual":
            len(delayed) >= 2,
        "all_training_source_episodes_accounted":
            source["episodes"] == len(TRAIN_LAWS) * len(TRAIN_SEEDS) and
            source["source_steps"] == len(TRAIN_LAWS) * len(TRAIN_SEEDS) * STEPS,
        "all_four_actions_actually_executed":
            len(source["action_totals"]) == 4 and
            min(source["action_totals"]) > 0,
    }
    return {
        "checks": checks,
        "disposition": (
            "SOURCE_TASK_IDENTIFIABLE_DEV_ONLY" if all(checks.values())
            else "SOURCE_TASK_INVALID_NO_GO"
        ),
    }


def main(output):
    started = time.perf_counter_ns()
    verify_prereg()
    collected = deterministic_traces()
    delayed = delayed_intervention_counterfactual()
    verdict = stage0_verdict(collected, delayed)
    doc = {
        "schema": "yggdrasil.nci04.st3.source-stage0.v1",
        "source_type": "IN_HOUSE_DEV_NOT_INDEPENDENT_FIRST_USE",
        "frozen_protocol_git_blob": PREREG_BLOB,
        "prereg_commit": PREREG_SHA,
        "source_evidence": collected,
        "source_only_delayed_counterfactual_laws": delayed,
        "headroom": verdict,
        "candidate_or_control_trained": False,
        "held_development_laws_opened": False,
        "protected_scientific_first_use": False,
        "scientific_pass": False,
        "source_only_process_wall_ns": time.perf_counter_ns()-started,
    }
    output.write_text(_canonical(doc)+"\n",encoding="utf-8")
    print("ST3_SOURCE_EPISODES="+str(collected["episodes"]))
    print("ST3_SOURCE_ACTIONS="+str(collected["source_steps"]))
    print("ST3_SOURCE_ALIAS_KEYS="+str(collected["unique_same_public_and_action_different_hidden_law_outcome_keys"]))
    print("ST3_SOURCE_DELAYED_LAWS="+str(len(delayed)))
    print("ST3_STAGE0_DISPOSITION="+verdict["disposition"])
    print("ST3_NO_PROTECTED_FIRST_USE=PASS")
    return doc


if __name__ == "__main__":
    cli = argparse.ArgumentParser()
    cli.add_argument("--output", required=True, type=Path)
    args = cli.parse_args()
    main(args.output)
