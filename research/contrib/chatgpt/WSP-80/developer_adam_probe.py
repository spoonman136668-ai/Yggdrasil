"""Real three-restart Adam developer-only WSP80 probe (not scientific)."""
from hashlib import sha256
from pathlib import Path
from time import perf_counter_ns, process_time_ns
import json
import os
import subprocess
import sys

from private_experiment import (collect_developer_sessions,
    freeze_developer_models, score_after_prelabel_freeze)
from source import World


def stable_hash(value):
    return sha256(json.dumps(value, sort_keys=True, separators=(",", ":"),
                             allow_nan=False).encode("ascii")).hexdigest()


def main():
    if sys.argv[1:] != ["--developer-only"]:
        raise PermissionError("only unregistered developer source 9001 is allowed")
    source_commit = subprocess.run(["git", "rev-parse", "HEAD"],
        text=True, check=True, capture_output=True).stdout.strip()
    if os.environ.get("GITHUB_SHA") and source_commit != os.environ["GITHUB_SHA"]:
        raise RuntimeError("source checkout differs from workflow SHA")
    world = World(9001, "quartic_positive", tuple(range(6)), tuple(range(6)))
    start_wall, start_cpu = perf_counter_ns(), process_time_ns()
    paid = collect_developer_sessions(world, seed=9001)
    frozen = freeze_developer_models(paid, seed=9001, train_conventional=True)
    # This is the FIRST call that may retrieve the evaluator's private labels.
    scored = score_after_prelabel_freeze(world, frozen, seed=9001)
    total_wall = perf_counter_ns() - start_wall
    total_cpu = process_time_ns() - start_cpu
    envelope = json.loads(frozen["prelabel"])
    costs = envelope["payload"]["cost_receipts"]
    trials = costs["MLP_trials"]
    if not (len(trials) == 3 and sorted(x["restart"] for x in trials) == [0,1,2]
            and all(1 <= x["gradient_updates"] <= 6000 for x in trials)
            and sum(x["gradient_updates"] for x in trials) ==
                costs["MLP_gradient_updates_total"]
            and costs["MLP_fully_trained"] ==
                (max(x["train_exact"] for x in trials) >= 0.95)
            and costs["MLP_numeric_parameters"] == 614):
        raise AssertionError("three genuine Adam restart receipts missing")
    if scored["paid_action_count"] != 384 or len(paid["random_ledger"]) != 384:
        raise AssertionError("paid-action ledger custody incomplete")
    if scored["prelabel_sha256"] != envelope["sha256"]:
        raise AssertionError("prelabel identity mismatch")
    metrics = {}
    for name, value in scored["scores"].items():
        if sum(value["physical"].values()) != 384 or sum(value["two_action"].values()) != 32:
            raise AssertionError("incomplete 384-query/32-composition metrics")
        metrics[name] = {
            "correct": value["physical"]["correct"],
            "wrong": value["physical"]["wrong_confident"],
            "never_paid_correct": value["genuinely_unpaid"]["correct"],
            "two_action_correct": value["two_action"]["correct"]}
    baseline_cpu = costs["MLP_train_cpu_ns"] + costs["MLP_infer_cpu_ns"]
    candidate_cpu = costs["candidate_train_cpu_ns"] + costs["candidate_infer_cpu_ns"]
    summary = {
        "schema": "wsp80.developer-real-adam-probe.v1",
        "classification": "DEVELOPMENT_ONLY_SCIENTIFIC_UNVERIFIED",
        "source_sha": source_commit,
        "developer_seed": 9001,
        "developer_world_sha256": world.receipt()["hidden_source_sha256"],
        "candidate_ledger_sha256": stable_hash([
            [e.before, e.action, e.after, e.action_cost]
            for e in paid["candidate_ledger"]]),
        "random_ledger_sha256": stable_hash([
            [e.before, e.action, e.after, e.action_cost]
            for e in paid["random_ledger"]]),
        "paid_actions_per_session": 384,
        "separately_paid_stageA_per_session": 144,
        "frozen_prelabel_sha256": frozen["prelabel_sha256"],
        "genuine_Adam_restarts": trials,
        "MLP_converged_exact_95pct": costs["MLP_fully_trained"],
        "MLP_best_paid_training_accuracy": costs["MLP_train_exact"],
        "MLP_total_gradient_updates": costs["MLP_gradient_updates_total"],
        "MLP_cpu_train_infer_ns": baseline_cpu,
        "candidate_partial_cpu_train_infer_ns": candidate_cpu,
        "candidate_vs_MLP_partial_cpu_ratio":
            candidate_cpu / baseline_cpu if baseline_cpu else None,
        "whole_probe_cpu_ns": total_cpu,
        "whole_probe_wall_ns": total_wall,
        "tracemalloc_peak_readout_only_bytes_diagnostic":
            frozen["memory_peak_traced_bytes_diagnostic"],
        "process_peak_RSS_qualified": False,
        "whole_process_cost_parity_qualified": False,
        "registered_16_worlds_evaluated": False,
        "developer_only_metrics": metrics,
    }
    print("WSP80_REAL_ADAM_DEV_RESULT=" + json.dumps(
        summary, sort_keys=True, separators=(",", ":"), allow_nan=False), flush=True)
    print("WSP80_REAL_ADAM_DEV_ENGINEERING=PASS; SCIENTIFIC=UNVERIFIED", flush=True)


if __name__ == "__main__":
    main()
