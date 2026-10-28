"""V31O external all-in fresh Python process CPU and OS peak RSS audit.

No learner/source modifications. This is development engineering, NO SCIENCE.
Frozen protocol: research/itd02_v31o_full_process_preregistration.md.
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

from research.itd02_v23_unfamiliar_mapping_audit import train_source
from research.itd02_v31i_cold_restart_audit import replay
from research.itd02_v31j_executed_edge_ledger_audit import (
    EXPECTED_CHECKPOINT_SHA, EXPECTED_TRACE_SHA,
)
from research.itd02_v31n_episode_ring_cache_audit import run as run_v31n
from yggdrasil.itd02_v17_neighbor_carried_learner_dev import canonical

ROOT = Path(__file__).resolve().parents[1]
SCHEMA = "yggdrasil.itd02.v31o.full_fresh_process_resource.v1"
TRIAL_PAIRS = 9
MAX_WORKER_SECONDS = 120


def actual_os_peak_resident_bytes():
    """True process peak resident metric; fail closed on unsupported OS."""
    if sys.platform == "linux":
        import resource
        native = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
        value = native * 1024  # Linux ru_maxrss is KiB, unlike macOS.
        method = "LINUX_GETRUSAGE_SELF_RU_MAXRSS_KIB_X1024"
    elif sys.platform == "win32":
        import ctypes
        from ctypes import wintypes

        class PROCESS_MEMORY_COUNTERS(ctypes.Structure):
            _fields_ = [
                ("cb", wintypes.DWORD),
                ("PageFaultCount", wintypes.DWORD),
                ("PeakWorkingSetSize", ctypes.c_size_t),
                ("WorkingSetSize", ctypes.c_size_t),
                ("QuotaPeakPagedPoolUsage", ctypes.c_size_t),
                ("QuotaPagedPoolUsage", ctypes.c_size_t),
                ("QuotaPeakNonPagedPoolUsage", ctypes.c_size_t),
                ("QuotaNonPagedPoolUsage", ctypes.c_size_t),
                ("PagefileUsage", ctypes.c_size_t),
                ("PeakPagefileUsage", ctypes.c_size_t),
            ]

        kernel = ctypes.WinDLL("kernel32", use_last_error=True)
        psapi = ctypes.WinDLL("psapi", use_last_error=True)
        current = kernel.GetCurrentProcess
        current.argtypes = []
        current.restype = wintypes.HANDLE
        get_info = psapi.GetProcessMemoryInfo
        get_info.argtypes = [
            wintypes.HANDLE, ctypes.POINTER(PROCESS_MEMORY_COUNTERS),
            wintypes.DWORD,
        ]
        get_info.restype = wintypes.BOOL
        metrics = PROCESS_MEMORY_COUNTERS()
        metrics.cb = ctypes.sizeof(metrics)
        if not get_info(current(), ctypes.byref(metrics), metrics.cb):
            raise RuntimeError(
                "V31O_WINDOWS_GETPROCESSMEMORYINFO_FAILED_{}".format(
                    ctypes.get_last_error()))
        value = int(metrics.PeakWorkingSetSize)
        if value < int(metrics.WorkingSetSize):
            raise AssertionError("V31O_WINDOWS_PEAK_LT_CURRENT_RESIDENT")
        method = "WINDOWS_GETPROCESSMEMORYINFO_PEAKWORKINGSETSIZE_BYTES"
    else:
        raise RuntimeError("V31O_OS_PEAK_RESIDENT_METER_UNSUPPORTED")
    if type(value) is not int or not (0 < value < (1 << 52)):
        raise AssertionError("V31O_UNAVAILABLE_OR_INVALID_OS_PEAK_RSS")
    return value, method


def validate_exact(rows, checkpoint):
    if type(rows) is not list or len(rows) != 24:
        raise AssertionError("V31O_PUBLIC_EVENT_SET_DRIFT")
    if (hashlib.sha256(canonical(rows)).hexdigest() != EXPECTED_TRACE_SHA
            or hashlib.sha256(checkpoint).hexdigest() != EXPECTED_CHECKPOINT_SHA):
        raise AssertionError("V31O_ORIGINAL_TRACE_CHECKPOINT_IDENTITY_DRIFT")


def worker(arm):
    if arm not in ("baseline", "cache"):
        raise ValueError("V31O_UNKNOWN_ARM")
    # process_time_ns since process start includes Python startup and imports.
    start_training = time.process_time_ns()
    source = train_source()["pretrained_shared"]
    after_training = time.process_time_ns()
    if arm == "baseline":
        rows, checkpoint = replay(source, False)
    else:
        rows, checkpoint = run_v31n(source, True, False)
    after_replay = time.process_time_ns()
    validate_exact(rows, checkpoint)
    peak, method = actual_os_peak_resident_bytes()
    # Take total at process end, after checkpoint and OS RSS observation.
    total_cpu = time.process_time_ns()
    record = {
        "schema": SCHEMA,
        "role": "isolated_worker",
        "arm": arm,
        "host": sys.platform,
        "events": 24,
        "total_process_cpu_ns": total_cpu,
        "source_training_cpu_ns": after_training - start_training,
        "replay_cpu_ns": after_replay - after_training,
        "peak_resident_bytes": peak,
        "peak_resident_method": method,
        "trace_sha256": EXPECTED_TRACE_SHA,
        "checkpoint_sha256": EXPECTED_CHECKPOINT_SHA,
        "source_pretrained_this_process": True,
        "exact_v31i_identity": True,
        "model_modified": False,
        "scientific_first_use": False,
        "parent_harness_cost_included": False,
    }
    if not (0 < record["replay_cpu_ns"] <= total_cpu and
            0 < record["source_training_cpu_ns"] < total_cpu):
        raise AssertionError("V31O_CLOCK_OR_TRAINING_PROVENANCE_INVALID")
    print(json.dumps(record, sort_keys=True, separators=(",", ":"),
                     allow_nan=False))


def launch(arm):
    if arm not in ("baseline", "cache"):
        raise AssertionError("V31O_INVALID_ARM_DISPATCH")
    env = os.environ.copy()
    env["PYTHONHASHSEED"] = "0"
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    args = [sys.executable, "-B", str(Path(__file__).resolve()),
            "--worker", arm]
    begin_wall = time.perf_counter_ns()
    result = subprocess.run(
        args, cwd=ROOT, env=env, capture_output=True, text=True,
        timeout=MAX_WORKER_SECONDS, check=False)
    elapsed_wall = time.perf_counter_ns() - begin_wall
    if result.returncode or result.stderr.strip():
        raise AssertionError(
            "V31O_WORKER_FAILURE_" + arm + "_" +
            str(result.returncode) + "_" + result.stderr[-1000:])
    try:
        record = json.loads(result.stdout)
    except (json.JSONDecodeError, TypeError) as exc:
        raise AssertionError("V31O_WORKER_NO_VALID_JSON") from exc
    if (type(record) is not dict or record.get("schema") != SCHEMA or
            record.get("role") != "isolated_worker" or
            record.get("arm") != arm or
            record.get("host") != sys.platform or
            record.get("events") != 24 or
            record.get("trace_sha256") != EXPECTED_TRACE_SHA or
            record.get("checkpoint_sha256") != EXPECTED_CHECKPOINT_SHA or
            record.get("exact_v31i_identity") is not True or
            record.get("source_pretrained_this_process") is not True or
            record.get("scientific_first_use") is not False or
            record.get("model_modified") is not False):
        raise AssertionError("V31O_WORKER_SOURCE_IDENTITY_INVALID")
    for field in ("total_process_cpu_ns", "source_training_cpu_ns",
                  "replay_cpu_ns", "peak_resident_bytes"):
        value = record.get(field)
        if type(value) is not int or value <= 0:
            raise AssertionError("V31O_INVALID_OS_METRIC_" + field)
    expected_method = ("LINUX_GETRUSAGE_SELF_RU_MAXRSS_KIB_X1024"
                       if sys.platform == "linux" else
                       "WINDOWS_GETPROCESSMEMORYINFO_PEAKWORKINGSETSIZE_BYTES"
                       if sys.platform == "win32" else None)
    if record.get("peak_resident_method") != expected_method:
        raise AssertionError("V31O_MISSING_NATIVE_OS_PEAK_RESIDENT_PROVENANCE")
    if elapsed_wall <= 0:
        raise AssertionError("V31O_INVALID_FRESH_PROCESS_WALL_CLOCK")
    record["parent_measured_full_worker_wall_ns"] = elapsed_wall
    return record


def ratio(a, b):
    if not (math.isfinite(a) and math.isfinite(b) and a > 0 and b > 0):
        raise AssertionError("V31O_RATIO_METER_INVALID")
    return a / b


def audit():
    # Strict warm-up once per arm, complete separate processes.
    for arm in ("baseline", "cache"):
        launch(arm)
    pairs = []
    for n in range(TRIAL_PAIRS):
        order = ("baseline", "cache") if n % 2 == 0 else ("cache", "baseline")
        observations = {}
        for arm in order:
            observations[arm] = launch(arm)
        a, b = observations["baseline"], observations["cache"]
        pairs.append({
            "index": n + 1,
            "launch_order": list(order),
            "baseline_cpu_ns": a["total_process_cpu_ns"],
            "cache_cpu_ns": b["total_process_cpu_ns"],
            "baseline_source_training_cpu_ns": a["source_training_cpu_ns"],
            "cache_source_training_cpu_ns": b["source_training_cpu_ns"],
            "baseline_replay_cpu_ns": a["replay_cpu_ns"],
            "cache_replay_cpu_ns": b["replay_cpu_ns"],
            "baseline_peak_resident_bytes": a["peak_resident_bytes"],
            "cache_peak_resident_bytes": b["peak_resident_bytes"],
            "baseline_wall_ns": a["parent_measured_full_worker_wall_ns"],
            "cache_wall_ns": b["parent_measured_full_worker_wall_ns"],
            "paired_cpu_ratio": ratio(b["total_process_cpu_ns"],
                                     a["total_process_cpu_ns"]),
            "paired_peak_resident_ratio": ratio(b["peak_resident_bytes"],
                                                a["peak_resident_bytes"]),
            "paired_wall_ratio": ratio(b["parent_measured_full_worker_wall_ns"],
                                       a["parent_measured_full_worker_wall_ns"]),
        })
    med = lambda key: statistics.median(row[key] for row in pairs)
    cpu = med("paired_cpu_ratio")
    rss = med("paired_peak_resident_ratio")
    result = {
        "schema": SCHEMA,
        "classification": ("V31O_OPT_HOST_ALL_IN_PROCESS_RESOURCE_POSITIVE__NO_SCIENCE"
                           if cpu <= .95 and rss <= 1.10 else
                           "V31O_OPT_NO_ALL_IN_RESOURCE_WIN__NO_SCIENCE"),
        "host": sys.platform,
        "status": "COMPLETE",
        "worker_per_arm_warmups": 1,
        "paired_trials": TRIAL_PAIRS,
        "fresh_workers_launched": 2 + 2 * TRIAL_PAIRS,
        "events_per_worker": 24,
        "source_pretrained_every_worker": True,
        "includes_python_startup_import_training_and_replay": True,
        "parent_orchestrator_cpu_excluded": True,
        "actions_setup_cost_excluded": True,
        "actual_host_os_peak_resident_meter": True,
        "peak_resident_method": ("LINUX_GETRUSAGE_SELF_RU_MAXRSS_KIB_X1024"
                                 if sys.platform == "linux" else
                                 "WINDOWS_GETPROCESSMEMORYINFO_PEAKWORKINGSETSIZE_BYTES"),
        "linux_and_windows_peak_resident_absolutes_not_cross_comparable": True,
        "both_hosts_required": True,
        "scientific_first_use": False,
        "reserved_q_holdout_evaluated": False,
        "model_modified": False,
        "retail_all_in_hardware_qualified": False,
        "native_distributed_cache": False,
        "original_trace_sha256": EXPECTED_TRACE_SHA,
        "original_checkpoint_sha256": EXPECTED_CHECKPOINT_SHA,
        "median_baseline_cpu_ns": int(med("baseline_cpu_ns")),
        "median_cache_cpu_ns": int(med("cache_cpu_ns")),
        "median_baseline_source_training_cpu_ns": int(
            med("baseline_source_training_cpu_ns")),
        "median_cache_source_training_cpu_ns": int(
            med("cache_source_training_cpu_ns")),
        "median_baseline_replay_cpu_ns": int(med("baseline_replay_cpu_ns")),
        "median_cache_replay_cpu_ns": int(med("cache_replay_cpu_ns")),
        "median_baseline_peak_resident_bytes": int(
            med("baseline_peak_resident_bytes")),
        "median_cache_peak_resident_bytes": int(
            med("cache_peak_resident_bytes")),
        "median_baseline_wall_ns": int(med("baseline_wall_ns")),
        "median_cache_wall_ns": int(med("cache_wall_ns")),
        "median_paired_cpu_ratio": round(cpu, 8),
        "median_paired_peak_resident_ratio": round(rss, 8),
        "median_paired_wall_ratio": round(med("paired_wall_ratio"), 8),
        "frozen_positive_cpu_ratio_le": .95,
        "frozen_positive_peak_resident_ratio_le": 1.10,
        "pairs": pairs,
    }
    print(json.dumps(result, sort_keys=True, separators=(",", ":"),
                     allow_nan=False))


if __name__ == "__main__":
    if len(sys.argv) == 3 and sys.argv[1] == "--worker":
        worker(sys.argv[2])
    elif len(sys.argv) == 1:
        audit()
    else:
        raise SystemExit("V31O_INVALID_CLI")
