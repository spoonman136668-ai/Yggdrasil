"""MR32-P source-only trial orchestrator.

This runner is intentionally separate from CI static tests. It uses frozen
FIT/TRANSFER seeds only when explicitly invoked by the dedicated experiment
workflow after exact-head qualification and source-only review.
"""
from __future__ import annotations

import hashlib
import json
import os
import random
import resource
import time
import tracemalloc

from counterfactual_shapley import (
    Q16, leave_one_out_q16_credits, shapley_q16_credits,
    uniform_q16_credits,
)
from mr32p_evaluator import (
    evaluate_all_coalitions, make_private_task, public_policy_message,
)
from mr32p_policy import initial_state
from mr32p_process import invoke_policy

FIT_SEEDS = (
    2003, 2011, 2017, 2027, 2029, 2039, 2053, 2063,
    2069, 2081, 2083, 2087, 2089, 2099, 2111, 2113,
)
TRANSFER_SEEDS = (
    3001, 3011, 3019, 3023, 3037, 3041, 3049, 3061,
    3067, 3079, 3083, 3089, 3109, 3119, 3121, 3137,
    3163, 3167, 3169, 3181, 3187, 3191, 3203, 3209,
    3217, 3221, 3229, 3251, 3253, 3257, 3259, 3271,
)
METHODS = (
    "random", "fixed_recency", "evidence_only",
    "uniform_mc", "leave_one_out", "shapley",
)
LEARNED = {"uniform_mc", "leave_one_out", "shapley"}
COMPARATORS = METHODS[:-1]
STATE_SNAPSHOT_SCHEMA = "yggdrasil.mr32p.state-snapshot.v1"
RESULT_SCHEMA = "yggdrasil.mr32p.counterfactual-trial.v1"
BOOTSTRAP_SEED = 320116
BOOTSTRAP_DRAWS = 10_000
DELTA_THRESHOLD_Q16 = 1311
PARENT_PROTOCOL_SHA = "f8182087d63513f1bc1031a3a37b355c826a5e14"
PROTOCOL_SHA = "823d006fd8453907a19c608770d682135aba070d"


def _canonical(value: object) -> bytes:
    return json.dumps(
        value, sort_keys=True, separators=(",", ":"),
        ensure_ascii=True, allow_nan=False,
    ).encode("utf-8")


def _sha(value: object) -> str:
    return hashlib.sha256(_canonical(value)).hexdigest()


def snapshot_state(state: dict) -> bytes:
    payload = {"schema": STATE_SNAPSHOT_SCHEMA, "state": state}
    return _canonical({"payload": payload, "sha256": _sha(payload)})


def restore_state(raw: bytes) -> dict:
    try:
        envelope = json.loads(raw.decode("utf-8"))
        payload = envelope["payload"]
        digest = _sha(payload)
    except Exception as exc:
        raise ValueError("MR32P_STATE_SNAPSHOT_FORMAT") from exc
    if digest != envelope.get("sha256"):
        raise ValueError("MR32P_STATE_SNAPSHOT_HASH")
    if payload.get("schema") != STATE_SNAPSHOT_SCHEMA:
        raise ValueError("MR32P_STATE_SNAPSHOT_SCHEMA")
    state = payload.get("state")
    expected = {"schema", "weights", "uses", "last_used", "clock"}
    if not isinstance(state, dict) or set(state) != expected:
        raise ValueError("MR32P_STATE_SNAPSHOT_FIELDS")
    return json.loads(_canonical(state).decode("utf-8"))


def _private_spec_sha(spec) -> str:
    return _sha({
        "seed": spec.seed,
        "regime": spec.regime,
        "episode": spec.episode,
        "public_items": list(spec.public_items),
        "initial_position": spec.initial_position,
        "target_position": spec.target_position,
    })


def _peak_rss() -> tuple[int | None, str]:
    try:
        if os.name == "nt":
            import psutil  # type: ignore
            return int(psutil.Process().memory_info().peak_wset), "windows_peak_working_set"
        import resource as resource_module
        return int(resource_module.getrusage(resource_module.RUSAGE_SELF).ru_maxrss * 1024), "linux_ru_maxrss"
    except Exception:
        return None, "unavailable"


def _credits(method: str, selected_ids: list[int],
             coalition_values: dict[int, int]) -> tuple[int, ...]:
    if method == "uniform_mc":
        return uniform_q16_credits(selected_ids, coalition_values)
    if method == "leave_one_out":
        return leave_one_out_q16_credits(selected_ids, coalition_values)
    if method == "shapley":
        credits, _, _ = shapley_q16_credits(selected_ids, coalition_values)
        return credits
    return ()


def _episode_step(method: str, spec, state: dict, training: bool,
                  policy_cpu: dict, evaluator_cpu: dict,
                  credit_cpu: dict) -> tuple[dict, dict]:
    public_message = public_policy_message(spec, method, state)
    policy_out = invoke_policy(public_message)
    policy_cpu[method] += policy_out["policy_cpu_ns"]
    selected = policy_out["selected_items"]
    receipts = policy_out["use_receipts"]
    if len(selected) != 7 or len(receipts) != 7:
        raise RuntimeError("MR32P_POLICY_USE_COUNT")
    if selected != sorted(selected):
        raise RuntimeError("MR32P_SELECTED_ID_ORDER")

    record_by_id = {row["item_id"]: row for row in public_message["records"]}
    expected_actions = [
        record_by_id[item]["proposed_action"] if item in set(selected) else 0
        for item in spec.public_items
    ]
    if policy_out["actions"] != expected_actions:
        raise RuntimeError("MR32P_POLICY_ACTION_USE_PARITY")

    evaluator_start = time.process_time_ns()
    coalition_values = evaluate_all_coalitions(spec, selected)
    evaluator_cpu[method] += time.process_time_ns() - evaluator_start
    if len(coalition_values) != 128 or set(coalition_values) != set(range(128)):
        raise RuntimeError("MR32P_COALITION_COVERAGE")
    baseline = coalition_values[0]
    observed = coalition_values[127]
    credit_values: tuple[int, ...] = ()

    state_after = policy_out["state_after_episode"]
    if training and method in LEARNED:
        credit_start = time.process_time_ns()
        credit_values = _credits(method, selected, coalition_values)
        credit_cpu[method] += time.process_time_ns() - credit_start
        if len(credit_values) != 7:
            raise RuntimeError("MR32P_CREDIT_COUNT")
        # Coalition player order is sorted item ID; align receipts before the
        # learner API reorders them by immutable event step.
        receipt_by_id = {row["item_id"]: row for row in receipts}
        ordered_receipts = [receipt_by_id[item] for item in selected]
        update_message = {
            "schema": "yggdrasil.mr32p.policy-message.v1",
            "operation": "update",
            "method": method,
            "episode_terminal": True,
            "state": state_after,
            "use_receipts": ordered_receipts,
            "credits_q16": list(credit_values),
        }
        update_out = invoke_policy(update_message)
        policy_cpu[method] += update_out["policy_cpu_ns"]
        state_after = dict(state_after)
        state_after["weights"] = update_out["weights"]

    if sum(credit_values) != (observed - baseline) * Q16 and method == "shapley" and training:
        raise RuntimeError("MR32P_SHAPLEY_CREDIT_EFFICIENCY")
    if method == "uniform_mc" and training:
        if sum(credit_values) != (observed - baseline) * Q16:
            raise RuntimeError("MR32P_UNIFORM_CREDIT_EFFICIENCY")

    episode_receipt = {
        "method": method,
        "seed": spec.seed,
        "regime": spec.regime,
        "episode": spec.episode,
        "public_items": list(spec.public_items),
        "public_actions": policy_out["actions"],
        "selected_items": selected,
        "use_receipts_by_item_id": [
            {k: row[k] for k in ("step", "item_id", "action", "features_q16")}
            for row in receipts
        ],
        "private_spec_sha256": _private_spec_sha(spec),
        "coalition_values": [coalition_values[mask] for mask in range(128)],
        "coalition_values_sha256": _sha([
            coalition_values[mask] for mask in range(128)
        ]),
        "no_memory_return": baseline,
        "terminal_return": observed,
        "terminal_delta": observed - baseline,
        "credit_method": method if training and method in LEARNED else None,
        "credits_q16_by_item_id": list(credit_values),
        "transfer_feedback_applied": False,
    }
    return state_after, episode_receipt


def _bootstrap_lower(differences: list[int]) -> int:
    rng = random.Random(BOOTSTRAP_SEED)
    n = len(differences)
    samples = [
        sum(differences[rng.randrange(n)] for _ in range(n)) // n
        for _ in range(BOOTSTRAP_DRAWS)
    ]
    samples.sort()
    return samples[249]


def run() -> dict:
    start_wall = time.perf_counter_ns()
    start_cpu = time.process_time_ns()
    tracemalloc.start()

    policy_cpu = {method: 0 for method in METHODS}
    evaluator_cpu = {method: 0 for method in METHODS}
    credit_cpu = {method: 0 for method in METHODS}
    fit_states = {method: initial_state() for method in METHODS}
    fit_receipts = []
    fit_feedback_counts = {method: 0 for method in METHODS}
    fit_cluster_receipts = []

    for cluster_index, seed in enumerate(FIT_SEEDS):
        regime = 0 if cluster_index < 8 else 1
        cluster_success = {method: 0 for method in METHODS}
        for episode in range(8):
            spec = make_private_task(seed, regime, episode)
            for method in METHODS:
                next_state, receipt = _episode_step(
                    method, spec, fit_states[method], True,
                    policy_cpu, evaluator_cpu, credit_cpu
                )
                fit_states[method] = next_state
                fit_receipts.append(receipt)
                cluster_success[method] += receipt["terminal_return"]
                if method in LEARNED:
                    fit_feedback_counts[method] += 7
        fit_cluster_receipts.append({
            "seed": seed, "regime": regime, "episode_count": 8,
            "successes": cluster_success,
        })

    checkpoint_bytes = {}
    checkpoints = {}
    checkpoint_sha256 = {}
    fit_weights_sha256 = {}
    for method in METHODS:
        raw = snapshot_state(fit_states[method])
        restored = restore_state(raw)
        if snapshot_state(restored) != raw:
            raise RuntimeError("MR32P_FIT_CHECKPOINT_COLD_RESTORE")
        checkpoints[method] = raw
        checkpoint_bytes[method] = len(raw)
        checkpoint_sha256[method] = hashlib.sha256(raw).hexdigest()
        fit_weights_sha256[method] = _sha(fit_states[method]["weights"])

    transfer_receipts = []
    transfer_cluster_receipts = []
    transfer_feedback_counts = {method: 0 for method in METHODS}
    cold_restore_counts = {method: 0 for method in METHODS}

    for cluster_index, seed in enumerate(TRANSFER_SEEDS):
        regime = 0 if cluster_index < 16 else 1
        cluster_states = {}
        cluster_starts = {}
        cluster_success = {method: 0 for method in METHODS}
        for method in METHODS:
            restored = restore_state(checkpoints[method])
            if snapshot_state(restored) != checkpoints[method]:
                raise RuntimeError("MR32P_TRANSFER_COLD_RESTORE")
            cluster_states[method] = restored
            cluster_starts[method] = hashlib.sha256(snapshot_state(restored)).hexdigest()
            cold_restore_counts[method] += 1

        for episode in range(8):
            spec = make_private_task(seed, regime, episode)
            for method in METHODS:
                next_state, receipt = _episode_step(
                    method, spec, cluster_states[method], False,
                    policy_cpu, evaluator_cpu, credit_cpu
                )
                cluster_states[method] = next_state
                transfer_receipts.append(receipt)
                cluster_success[method] += receipt["terminal_return"]

        end_weights_sha = {}
        end_state_sha = {}
        for method in METHODS:
            state = cluster_states[method]
            weights_sha = _sha(state["weights"])
            if weights_sha != fit_weights_sha256[method]:
                raise RuntimeError("MR32P_TRANSFER_WEIGHTS_CHANGED")
            end_weights_sha[method] = weights_sha
            end_state_sha[method] = hashlib.sha256(snapshot_state(state)).hexdigest()
        transfer_cluster_receipts.append({
            "seed": seed,
            "regime": regime,
            "episode_count": 8,
            "cold_restore_checkpoint_sha256": cluster_starts,
            "terminal_weights_sha256": end_weights_sha,
            "terminal_state_sha256": end_state_sha,
            "feedback_events_applied": {method: 0 for method in METHODS},
            "successes": cluster_success,
        })

    # Each cluster gets equal weight; eight episodes are paired within it.
    cluster_score_q16 = []
    means = {method: 0 for method in METHODS}
    for cluster in transfer_cluster_receipts:
        score = {
            method: cluster["successes"][method] * Q16 // 8
            for method in METHODS
        }
        cluster_score_q16.append({
            "seed": cluster["seed"], "regime": cluster["regime"], **score
        })
    for method in METHODS:
        means[method] = sum(row[method] for row in cluster_score_q16) // len(cluster_score_q16)

    strongest = max(
        COMPARATORS,
        key=lambda method: (means[method], -COMPARATORS.index(method))
    )
    paired = {
        method: [row["shapley"] - row[method] for row in cluster_score_q16]
        for method in COMPARATORS
    }
    wins = {
        method: sum(value > 0 for value in values)
        for method, values in paired.items()
    }
    bootstrap = {
        method: _bootstrap_lower(values)
        for method, values in paired.items()
    }
    regime_wins = {}
    regime_means = {}
    for regime in (0, 1):
        rows = [row for row in cluster_score_q16 if row["regime"] == regime]
        regime_wins[str(regime)] = sum(
            row["shapley"] > row[strongest] for row in rows
        )
        regime_means[str(regime)] = {
            method: sum(row[method] for row in rows) // len(rows)
            for method in METHODS
        }

    delta_q16_sum = sum(paired[strongest])
    mean_delta_q16 = delta_q16_sum // len(TRANSFER_SEEDS)
    candidate_cpu = policy_cpu["shapley"] + credit_cpu["shapley"]
    control_cpu = policy_cpu["leave_one_out"] + credit_cpu["leave_one_out"]
    rss, rss_method = _peak_rss()
    current_mem, peak_mem = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    parent_cpu = time.process_time_ns() - start_cpu
    wall = time.perf_counter_ns() - start_wall

    falsifiers = {
        "delta_at_least_0_02": mean_delta_q16 >= 1311,
        "wins_at_least_24_of_32": wins[strongest] >= 24,
        "wins_at_least_12_of_16_each_regime": all(
            value >= 12 for value in regime_wins.values()
        ),
        "bootstrap_lower_above_zero": bootstrap[strongest] > 0,
        "fit_transfer_seeds_disjoint": not set(FIT_SEEDS).intersection(TRANSFER_SEEDS),
        "transfer_feedback_zero": all(value == 0 for value in transfer_feedback_counts.values()),
        "cold_restore_32_per_method": all(value == 32 for value in cold_restore_counts.values()),
        "shapley_checkpoint_bytes_within_1_25x_loo": (
            checkpoint_bytes["shapley"] * 4 <= checkpoint_bytes["leave_one_out"] * 5
        ),
        "shapley_policy_plus_credit_cpu_within_1_25x_loo": (
            candidate_cpu * 4 <= control_cpu * 5
        ),
    }
    coalition_count = len(fit_receipts) * 128 + len(transfer_receipts) * 128
    result = {
        "schema": RESULT_SCHEMA,
        "classification": "CONTROLLED_SYNTHETIC_DEVELOPMENT_ONLY",
        "source_commit": os.environ.get("GITHUB_SHA"),
        "protocol": {
            "parent_commit": "68f21c26e9cf42390cd1e09d2a2403011827d3cb",
            "protocol_commit": PROTOCOL_SHA,
            "fit_seeds": list(FIT_SEEDS),
            "transfer_seeds": list(TRANSFER_SEEDS),
            "fit_episode_count": len(fit_receipts) // len(METHODS),
            "transfer_episode_count": len(transfer_receipts) // len(METHODS),
            "events_per_episode": 16,
            "coalitions_per_policy_episode": 128,
            "total_coalition_replays": coalition_count,
        },
        "fit": {
            "event_sha256": _sha(fit_receipts),
            "episode_receipt_count": len(fit_receipts),
            "feedback_counts": fit_feedback_counts,
            "cluster_receipts": fit_cluster_receipts,
            "checkpoint_sha256": checkpoint_sha256,
            "checkpoint_bytes": checkpoint_bytes,
            "episode_receipts": fit_receipts,
        },
        "transfer": {
            "event_sha256": _sha(transfer_receipts),
            "episode_receipt_count": len(transfer_receipts),
            "cluster_receipts": transfer_cluster_receipts,
            "feedback_events_applied": transfer_feedback_counts,
            "cold_restore_cluster_count_by_method": cold_restore_counts,
            "method_mean_terminal_success_q16": means,
            "strongest_comparator": strongest,
            "shapley_mean_delta_q16": mean_delta_q16,
            "shapley_mean_delta": mean_delta_q16 / Q16,
            "shapley_wins_by_comparator": wins,
            "bootstrap_lower_q16_by_comparator": bootstrap,
            "regime_mean_terminal_success_q16": regime_means,
            "shapley_wins_by_regime_vs_strongest": regime_wins,
            "cluster_scores_q16": cluster_score_q16,
            "episode_receipts": transfer_receipts,
        },
        "resources": {
            "policy_process_cpu_ns": policy_cpu,
            "coalition_evaluator_cpu_ns": evaluator_cpu,
            "credit_allocator_cpu_ns": credit_cpu,
            "shapley_policy_plus_credit_cpu_ns": candidate_cpu,
            "leave_one_out_policy_plus_credit_cpu_ns": control_cpu,
            "parent_process_cpu_ns": parent_cpu,
            "all_in_cpu_ns": parent_cpu + sum(policy_cpu.values()),
            "process_wall_ns": wall,
            "process_peak_rss_bytes": rss,
            "process_peak_rss_method": rss_method,
            "tracemalloc_current_bytes": current_mem,
            "tracemalloc_peak_bytes": peak_mem,
        },
        "falsifiers": falsifiers,
    }
    result["development_signal"] = all(falsifiers.values())
    return result


if __name__ == "__main__":
    print(json.dumps(run(), sort_keys=True, indent=2, allow_nan=False))
