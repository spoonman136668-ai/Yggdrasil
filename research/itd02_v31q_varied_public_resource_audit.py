"""V31Q: diverse public-context source-only resource audit for original V31N cache.

Frozen resource and parity protocol in itd02_v31q_varied_public_preregistration.
Engineering-only; original native learner, source and scientific holdouts untouched.
"""
from __future__ import annotations

import hashlib
import json
import math
import os
from pathlib import Path
import statistics
import subprocess
import sys
import time
from contextlib import nullcontext

from research.itd02_v23_unfamiliar_mapping_audit import train_source
from research.itd02_v26_calibrated_return_audit import context, reward
from research.itd02_v31i_cold_restart_codec import pack, restore
from research.itd02_v31j_executed_edge_ledger_audit import (
    EXPECTED_CHECKPOINT_SHA, EXPECTED_TRACE_SHA,
)
from research.itd02_v31n_episode_ring_cache_audit import bounded_ring_cache
from research.itd02_v31o_full_process_resource_audit import (
    actual_os_peak_resident_bytes,
)
from yggdrasil.itd02_v17_neighbor_carried_learner_dev import ACTIONS, PUBLIC_CUES, canonical
from yggdrasil.itd02_v31d_distinct_return_dev import DistinctReturnRingDev

ROOT = Path(__file__).resolve().parents[1]
SCHEMA = "yggdrasil.itd02.v31q.long_session_amortization.v1"
LENGTHS = (1, 4, 16)
PAIR_COUNT = 9
MAX_WORKER_SECONDS = 120
EXPECTED_SOURCE_UPDATES = 16 * 36
EVENTS_PER_BLOCK = 24


def digest(value):
    return hashlib.sha256(value).hexdigest()


PUBLIC_FAMILIES = ("cue_second", "source", "triple_parity")
EXPECTED_DIVERSITY = {1: (24, 12), 4: (69, 36), 16: (108, 36)}


def public_events(block_index):
    """Predeclared public 36-context catalogue; original V31I block at index 0."""
    if type(block_index) is not int or not 0 <= block_index < 16:
        raise ValueError("V31Q_INVALID_BLOCK_INDEX")
    rows = []
    for half in range(2):
        family = (("cue_second", "source")[half] if block_index == 0
                  else PUBLIC_FAMILIES[(block_index + half) % 3])
        for i in range(12):
            if block_index == 0:
                case = context(i, 0)
            else:
                k = (7 * block_index + 11 * i + 5 * half) % 36
                case = (PUBLIC_CUES[k // 9], ACTIONS[(k // 3) % 3],
                        ACTIONS[k % 3])
            rows.append((family, case, reward(family, case)))
    if len(rows) != EVENTS_PER_BLOCK:
        raise AssertionError("V31Q_PUBLIC_FAMILY_CONTEXT_SCHEDULE_DRIFT")
    return rows


def verified_diversity(blocks):
    events = [item for b in range(blocks) for item in public_events(b)]
    pairs = {(family, case) for family, case, _ in events}
    contexts = {case for _, case, _ in events}
    families = {family for family, _, _ in events}
    expected = EXPECTED_DIVERSITY[blocks]
    if (len(events) != 24 * blocks or
            (len(pairs), len(contexts)) != expected or
            (blocks > 1 and families != set(PUBLIC_FAMILIES)) or
            (blocks == 1 and families != {"cue_second", "source"})):
        raise AssertionError("V31Q_PUBLIC_SOURCE_VARIETY_CONTRACT_DRIFT")
    return {
        "family_context_pairs": len(pairs),
        "distinct_contexts": len(contexts),
        "public_reward_families": sorted(families),
    }


def extended_replay(source, blocks, cached, *, cold=False):
    """Same real V31D learner: vary ONLY fixed, public environment inputs."""
    if type(blocks) is not int or blocks not in LENGTHS:
        raise ValueError("V31Q_INVALID_PREDECLARED_BLOCK_LENGTH")
    verified_diversity(blocks)  # Fail before updates on any schedule drift.
    model = DistinctReturnRingDev(source)
    signatures = []
    with (bounded_ring_cache() if cached else nullcontext()) as cache_stats:
        for block_index in range(blocks):
            rows = []
            plan = public_events(block_index)
            public_schedule = []
            for family, case, outcome in plan:
                model.start_observation(case[0])
                model.accept_first(case[1])
                pred = model.score(case[2])
                model.accept_second(case[2], outcome)
                rows.append([
                    list(case), round(pred, 12), model.fast,
                    model.bank.slow.parameters_sha256(),
                    model.bank.fast.parameters_sha256(),
                    model.switches,
                ])
                public_schedule.append([family, list(case), outcome])
            if len(rows) != EVENTS_PER_BLOCK:
                raise AssertionError("V31Q_PUBLIC_EVENT_COUNT_DRIFT")
            block_trace_sha = digest(canonical(rows))
            checkpoint = pack(model)
            block_checkpoint_sha = digest(checkpoint)
            if block_index == 0 and (block_trace_sha != EXPECTED_TRACE_SHA or
                    block_checkpoint_sha != EXPECTED_CHECKPOINT_SHA):
                raise AssertionError("V31Q_FIRST_BLOCK_V31I_PROVENANCE_DRIFT")
            signatures.append({
                "block": block_index + 1,
                "trace_sha256": block_trace_sha,
                "checkpoint_sha256": block_checkpoint_sha,
                "schedule_sha256": digest(canonical(public_schedule)),
            })
            if cold and block_index + 1 < blocks:
                model = restore(checkpoint)
        if cached and (
                cache_stats["max_feature_keys"] > 1 or
                cache_stats["max_mix_keys"] > 3 or
                cache_stats["feature_hits"] <= 0 or
                cache_stats["mix_hits"] <= 0 or
                cache_stats["episode_resets"] != 2 * EVENTS_PER_BLOCK * blocks):
            raise AssertionError("V31Q_ORIGINAL_EPISODE_CACHE_SCOPE_DRIFT")
    return signatures


def parity_preflight():
    """Once per host, compare both arms and cold restores at every block."""
    source = train_source()["pretrained_shared"]
    results = {}
    for blocks in LENGTHS:
        pristine = extended_replay(source, blocks, False)
        cached = extended_replay(source, blocks, True)
        pristine_cold = extended_replay(source, blocks, False, cold=True)
        cached_cold = extended_replay(source, blocks, True, cold=True)
        if not (pristine == cached == pristine_cold == cached_cold):
            raise AssertionError("V31Q_CONTINUOUS_COLD_OR_CACHE_STATE_DRIFT")
        results[str(blocks)] = pristine
    return results


def worker(arm, blocks):
    if arm not in ("baseline", "cache") or blocks not in LENGTHS:
        raise AssertionError("V31Q_UNAUTHORIZED_WORKER_ARM_OR_LENGTH")
    # CPU process timer is elapsed CPU since Python process start; includes
    # interpreter imports, source training, execution and validation.
    start_training = time.process_time_ns()
    source = train_source()["pretrained_shared"]
    after_training = time.process_time_ns()
    signatures = extended_replay(source, blocks, arm == "cache")
    after_replay = time.process_time_ns()
    resident, resident_method = actual_os_peak_resident_bytes()
    total_cpu = time.process_time_ns()
    if not (0 < after_training-start_training < total_cpu and
            0 < after_replay-after_training < total_cpu and
            0 < resident < 1 << 52):
        raise AssertionError("V31Q_INVALID_NATIVE_OS_CLOCK_OR_RESIDENT_METER")
    record = {
        "schema": SCHEMA,
        "role": "fresh_worker",
        "arm": arm,
        "host": sys.platform,
        "blocks": blocks,
        "events": blocks * EVENTS_PER_BLOCK,
        "source_pretrained_this_process": True,
        "source_training_updates": EXPECTED_SOURCE_UPDATES,
        "total_process_cpu_ns": total_cpu,
        "source_training_cpu_ns": after_training-start_training,
        "replay_cpu_ns": after_replay-after_training,
        "peak_resident_bytes": resident,
        "peak_resident_method": resident_method,
        "signatures": signatures,
        "public_diversity": verified_diversity(blocks),
        "scientific_first_use": False,
        "native_source_modified": False,
        "parent_harness_cost_included": False,
    }
    print(json.dumps(record, sort_keys=True, separators=(",", ":"), allow_nan=False))


def launch(arm, blocks):
    if arm not in ("baseline", "cache") or blocks not in LENGTHS:
        raise AssertionError("V31Q_UNAUTHORIZED_WORKER_DISPATCH")
    env = dict(os.environ)
    env["PYTHONHASHSEED"] = "0"
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    command = [
        sys.executable, "-B", str(Path(__file__).resolve()),
        "--worker", arm, str(blocks),
    ]
    start = time.perf_counter_ns()
    result = subprocess.run(
        command, cwd=ROOT, env=env, text=True, capture_output=True,
        check=False, timeout=MAX_WORKER_SECONDS,
    )
    full_wall = time.perf_counter_ns() - start
    if result.returncode or result.stderr.strip():
        raise AssertionError(
            "V31Q_WORKER_FAILURE_{}_{}_{}_{}".format(
                arm, blocks, result.returncode, result.stderr[-1200:]))
    try:
        data = json.loads(result.stdout)
    except (ValueError, TypeError) as exc:
        raise AssertionError("V31Q_WORKER_NONJSON_OUTPUT") from exc
    if (type(data) is not dict or
            data.get("schema") != SCHEMA or
            data.get("role") != "fresh_worker" or
            data.get("arm") != arm or
            data.get("host") != sys.platform or
            data.get("blocks") != blocks or
            data.get("events") != blocks * EVENTS_PER_BLOCK or
            data.get("source_pretrained_this_process") is not True or
            data.get("source_training_updates") != EXPECTED_SOURCE_UPDATES or
            data.get("public_diversity") != verified_diversity(blocks) or
            data.get("scientific_first_use") is not False or
            data.get("native_source_modified") is not False):
        raise AssertionError("V31Q_WORKER_IDENTITY_OR_CONTRACT_DRIFT")
    for field in ("total_process_cpu_ns", "source_training_cpu_ns",
                  "replay_cpu_ns", "peak_resident_bytes"):
        value = data.get(field)
        if type(value) is not int or value <= 0:
            raise AssertionError("V31Q_INVALID_WORKER_RESOURCE_" + field)
    method = ("LINUX_GETRUSAGE_SELF_RU_MAXRSS_KIB_X1024" if
              sys.platform == "linux" else
              "WINDOWS_GETPROCESSMEMORYINFO_PEAKWORKINGSETSIZE_BYTES"
              if sys.platform == "win32" else None)
    if not method or data.get("peak_resident_method") != method:
        raise AssertionError("V31Q_OS_RSS_ACCOUNTING_UNAVAILABLE")
    signatures = data.get("signatures")
    if (type(signatures) is not list or len(signatures) != blocks or
            any(type(entry) is not dict or
                set(entry) != {"block", "trace_sha256", "checkpoint_sha256", "schedule_sha256"} or
                entry["block"] != i + 1 or
                any(type(entry[key]) is not str or len(entry[key]) != 64
                    for key in ("trace_sha256", "checkpoint_sha256", "schedule_sha256"))
                for i, entry in enumerate(signatures))):
        raise AssertionError("V31Q_MISSING_PER_BLOCK_TRACE_OR_CHECKPOINT")
    if (signatures[0]["trace_sha256"] != EXPECTED_TRACE_SHA or
            signatures[0]["checkpoint_sha256"] != EXPECTED_CHECKPOINT_SHA):
        raise AssertionError("V31Q_ORIGINAL_FIRST_BLOCK_CHANGED")
    for b, entry in enumerate(signatures):
        schedule = [[family, list(case), outcome]
                    for family, case, outcome in public_events(b)]
        if entry["schedule_sha256"] != digest(canonical(schedule)):
            raise AssertionError("V31Q_PUBLIC_SCHEDULE_SHA_MISMATCH")
    if full_wall <= 0:
        raise AssertionError("V31Q_INVALID_WALL_METER")
    data["wall_process_ns"] = full_wall
    return data


def ratio(a, b):
    value = a / b
    if not (math.isfinite(value) and value > 0):
        raise AssertionError("V31Q_NONFINITE_RESOURCE_RATIO")
    return value


def collect():
    # One unmetered cross-arm + cold-restart proof, exact block-by-block.
    expected = parity_preflight()
    results = []
    for blocks in LENGTHS:
        reference = expected[str(blocks)]
        for arm in ("baseline", "cache"):
            warm = launch(arm, blocks)
            if warm["signatures"] != reference:
                raise AssertionError("V31Q_WARMUP_CHECKPOINT_OR_TRACE_DRIFT")
        pairs = []
        for trial in range(PAIR_COUNT):
            order = ("baseline", "cache") if trial % 2 == 0 else ("cache", "baseline")
            readings = {}
            for arm in order:
                readings[arm] = launch(arm, blocks)
                if readings[arm]["signatures"] != reference:
                    raise AssertionError("V31Q_TRIAL_TRACE_OR_CHECKPOINT_DRIFT")
            baseline = readings["baseline"]
            cache = readings["cache"]
            pairs.append({
                "trial": trial + 1,
                "order": list(order),
                "baseline_cpu_ns": baseline["total_process_cpu_ns"],
                "cache_cpu_ns": cache["total_process_cpu_ns"],
                "baseline_training_cpu_ns": baseline["source_training_cpu_ns"],
                "cache_training_cpu_ns": cache["source_training_cpu_ns"],
                "baseline_replay_cpu_ns": baseline["replay_cpu_ns"],
                "cache_replay_cpu_ns": cache["replay_cpu_ns"],
                "baseline_resident_peak_bytes": baseline["peak_resident_bytes"],
                "cache_resident_peak_bytes": cache["peak_resident_bytes"],
                "baseline_wall_ns": baseline["wall_process_ns"],
                "cache_wall_ns": cache["wall_process_ns"],
                "cpu_ratio": ratio(cache["total_process_cpu_ns"],
                                   baseline["total_process_cpu_ns"]),
                "resident_ratio": ratio(cache["peak_resident_bytes"],
                                        baseline["peak_resident_bytes"]),
                "wall_ratio": ratio(cache["wall_process_ns"],
                                    baseline["wall_process_ns"]),
            })
        med = lambda field: statistics.median(p[field] for p in pairs)
        results.append({
            "blocks": blocks,
            "events": blocks * EVENTS_PER_BLOCK,
            "public_diversity": verified_diversity(blocks),
            "cpu_ratio_median": round(med("cpu_ratio"), 8),
            "resident_ratio_median": round(med("resident_ratio"), 8),
            "wall_ratio_median_secondary": round(med("wall_ratio"), 8),
            "baseline_cpu_median_ns": int(med("baseline_cpu_ns")),
            "cache_cpu_median_ns": int(med("cache_cpu_ns")),
            "baseline_source_training_cpu_median_ns": int(med("baseline_training_cpu_ns")),
            "cache_source_training_cpu_median_ns": int(med("cache_training_cpu_ns")),
            "baseline_replay_cpu_median_ns": int(med("baseline_replay_cpu_ns")),
            "cache_replay_cpu_median_ns": int(med("cache_replay_cpu_ns")),
            "baseline_resident_peak_median_bytes": int(med("baseline_resident_peak_bytes")),
            "cache_resident_peak_median_bytes": int(med("cache_resident_peak_bytes")),
            "provenance_exact_baseline_cache_continuous_cold": True,
            "block_checkpoint_count": blocks,
            "trials_per_arm": PAIR_COUNT,
            "pairs": pairs,
        })
    short, medium, long = results
    # Frozen gates for 4/16; one block intentionally diagnostic.
    medium_pass = (medium["cpu_ratio_median"] <= .95 and
                   medium["resident_ratio_median"] <= 1.10)
    long_pass = (long["cpu_ratio_median"] <= .85 and
                 long["resident_ratio_median"] <= 1.10)
    report = {
        "schema": SCHEMA,
        "host": sys.platform,
        "classification": (
            "V31Q_OPT_HOST_DIVERSE_RESOURCE_POSITIVE__NO_SCIENCE" if
            medium_pass and long_pass else
            "V31Q_OPT_NO_JOINT_DIVERSE_RESOURCE_WIN__NO_SCIENCE"),
        "status": "COMPLETE",
        "preregistered_lengths": list(LENGTHS),
        "worker_warmups_per_arm_per_length": 1,
        "paired_trials_per_length": PAIR_COUNT,
        "fresh_workers_launched": len(LENGTHS) * (2 + 2 * PAIR_COUNT),
        "source_pretraining_once_per_worker": True,
        "preregistered_public_diversity": {"1": {"family_context_pairs": 24, "contexts": 12}, "4": {"family_context_pairs": 69, "contexts": 36}, "16": {"family_context_pairs": 108, "contexts": 36}},
        "original_v31i_first_block_identity_on_every_worker": True,
        "each_block_trace_and_full_checkpoint_equal_control_cache": True,
        "block_cold_restart_parity": True,
        "varied_known_public_reward_families_and_all_36_public_contexts": True,
        "public_feedback_is_synthetic_not_independent_unfamiliar_transfer": True,
        "true_os_resident_peak": True,
        "startup_import_pretraining_replay_worker_cpu_included": True,
        "external_parent_orchestrator_and_ci_cost_excluded": True,
        "scientific_first_use": False,
        "reserved_q_holdout_evaluated": False,
        "native_source_modified": False,
        "native_distributed_memory_demonstrated": False,
        "cross_host_positive_requires_both": True,
        "cpu_gate_4_blocks_le": .95,
        "cpu_gate_16_blocks_le": .85,
        "resident_gate_4_and_16_blocks_le": 1.10,
        "preregistered_4_blocks_pass": medium_pass,
        "preregistered_16_blocks_pass": long_pass,
        "os_rss_measurement_method": (
            "LINUX_GETRUSAGE_SELF_RU_MAXRSS_KIB_X1024" if sys.platform == "linux"
            else "WINDOWS_GETPROCESSMEMORYINFO_PEAKWORKINGSETSIZE_BYTES"),
        "all_results": results,
    }
    print(json.dumps(report, sort_keys=True, separators=(",", ":"), allow_nan=False))


if __name__ == "__main__":
    if len(sys.argv) == 4 and sys.argv[1] == "--worker":
        worker(sys.argv[2], int(sys.argv[3]))
    elif len(sys.argv) == 1:
        collect()
    else:
        raise SystemExit("V31Q_UNAUTHORIZED_CLI")
