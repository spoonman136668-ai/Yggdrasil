"""Measured CPU-only native training plus cold-restart development probe.

This is NOT a retail-device result, original Shuttle experiment, approved
source cohort, scientific comparison, conventional-control measurement, or
proof of useful cognition. Uses a known SOURCE-FREE public fixture only.

Captures whole Python+original native-cell+durable-journal process costs,
including exact source-free reset, chosen actions, reward updates, fsync,
checkpoint and cold restore on the SAME process. OS peak resident memory is
best effort and explicitly NULL when unavailable; no invented energy data.
No paid API, CUDA library, online dependency, or new trainer.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
from pathlib import Path
import platform
import statistics
import sys
import tempfile
import time

from .itd02_local_ring_memory_dev import ACTIONS
from .itd02_native_training_session_dev import NativeTrainingSessionDev
from .itd02_public_source_journal_dev import (
    JournaledPublicSourceDev, load_verified_native_model, inspect_custody,
)

FIXTURE_SHA = hashlib.sha256(b"YGG-ITD02-SOURCE-FREE-CPU-PROBE-V1").hexdigest()
ROLE = "OWNER_PUBLIC_FIT_DEVELOPMENT_ONLY"
MODE = "SOURCE_FREE_HOSTED_CI_ENGINEERING_NOT_RETAIL_OR_SCIENCE"


class SourceFreeCpuFixture:
    """In-repo artificial public-only events; NOT a genuine task world."""

    def __init__(self, steps: int):
        if type(steps) is not int or not 1 <= steps <= 64:
            raise ValueError("SOURCE_FREE_PROBE_BUDGET")
        self.steps = steps
        self.count = 0
        self.reset = False

    def reset_public(self):
        if self.reset:
            raise ValueError("SOURCE_FREE_PROBE_REPEAT_RESET")
        self.reset = True
        return "docked_MRV"

    def step_public(self, action):
        if not self.reset or self.count >= self.steps or action not in ACTIONS:
            raise ValueError("SOURCE_FREE_PROBE_STEP_INVALID")
        self.count += 1
        # Deterministic artificial feedback probes native update/persistence.
        # It is not a hidden dynamics model, policy oracle, or goal success.
        reward = 10 if self.count % 3 == 0 else 0
        observation = ("Nothing", "LRV", "MRV", "docked_LRV")[
            (self.count - 1) % 4]
        return observation, reward, False, self.count == self.steps


def _peak_resident_bytes():
    if sys.platform.startswith("linux"):
        try:
            for line in Path("/proc/self/status").read_text("ascii").splitlines():
                if line.startswith("VmHWM:"):
                    return int(line.split()[1]) * 1024
        except (OSError, IndexError, ValueError):
            return None
    if os.name == "nt":
        # PROCESS_MEMORY_COUNTERS.PeakWorkingSetSize, read through the
        # Windows OS; no psutil, PyTorch, driver or CUDA dependency.
        try:
            import ctypes
            from ctypes import wintypes

            class Counters(ctypes.Structure):
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

            process = ctypes.WinDLL("kernel32", use_last_error=True)
            api = ctypes.WinDLL("psapi", use_last_error=True)
            process.GetCurrentProcess.restype = wintypes.HANDLE
            api.GetProcessMemoryInfo.argtypes = [
                wintypes.HANDLE, ctypes.POINTER(Counters), wintypes.DWORD]
            api.GetProcessMemoryInfo.restype = wintypes.BOOL
            counters = Counters()
            counters.cb = ctypes.sizeof(Counters)
            ok = api.GetProcessMemoryInfo(
                process.GetCurrentProcess(), ctypes.byref(counters), counters.cb)
            return int(counters.PeakWorkingSetSize) if ok else None
        except (OSError, AttributeError, TypeError, ValueError):
            return None
    return None


def _percentile(values, quantile):
    if not values:
        raise ValueError("NO_PROBE_SAMPLES")
    ordered = sorted(values)
    return round(ordered[max(0, math.ceil(quantile * len(ordered)) - 1)], 3)


def run_probe(*, episodes=4, steps=4):
    if (type(episodes) is not int or not 1 <= episodes <= 32 or
            type(steps) is not int or not 1 <= steps <= 64):
        raise ValueError("SOURCE_FREE_CPU_PROBE_LIMIT")

    wall_started = time.perf_counter_ns()
    cpu_started = time.process_time_ns()
    peak_before = _peak_resident_bytes()
    model = None
    episode_ms = []
    cold_restore_ms = []
    original_identities = None
    final_identities = None
    confirmed_steps = 0
    committed_episodes = 0
    disk_bytes = 0
    with tempfile.TemporaryDirectory(prefix="ygg-cpu-probe-") as folder:
        for i in range(episodes):
            directory = Path(folder) / ("episode-" + str(i + 1))
            start_episode = time.perf_counter_ns()
            source = SourceFreeCpuFixture(steps)
            session = NativeTrainingSessionDev(model=model, max_steps=steps)
            if original_identities is None:
                original_identities = session.model.model_identities()
            with JournaledPublicSourceDev(
                directory, source,
                episode_id="source-free-cpu-" + str(i + 1),
                source_sha256=FIXTURE_SHA, max_steps=steps, role=ROLE,
            ) as custody:
                result = custody.execute_one(session)
            if (result["steps"] != steps or result["terminal"] or
                    not result["truncated"] or
                    result["custody"]["status"] != "COMMITTED"):
                raise ValueError("SOURCE_FREE_CPU_PROBE_EPISODE_INVALID")
            verified = inspect_custody(
                directory, expected_source_sha256=FIXTURE_SHA)
            if verified["steps"] != steps or not verified["checkpoint_verified"]:
                raise ValueError("SOURCE_FREE_CPU_PROBE_CUSTODY_INVALID")
            confirmed_steps += verified["steps"]
            committed_episodes += 1
            restore_at = time.perf_counter_ns()
            model = load_verified_native_model(
                directory, expected_source_sha256=FIXTURE_SHA)
            cold_restore_ms.append(
                (time.perf_counter_ns() - restore_at) / 1_000_000)
            if model.model_identities() != session.model.model_identities():
                raise ValueError("SOURCE_FREE_CPU_PROBE_NATIVE_RESTORE_DRIFT")
            final_identities = model.model_identities()
            episode_ms.append(
                (time.perf_counter_ns() - start_episode) / 1_000_000)
            disk_bytes += sum(
                p.stat().st_size for p in directory.iterdir() if p.is_file())
    elapsed_wall_ns = time.perf_counter_ns() - wall_started
    elapsed_cpu_ns = time.process_time_ns() - cpu_started
    peak_after = _peak_resident_bytes()
    if confirmed_steps != episodes * steps or committed_episodes != episodes:
        raise ValueError("SOURCE_FREE_CPU_PROBE_STEP_ACCOUNTING")
    if original_identities is None or final_identities is None:
        raise ValueError("SOURCE_FREE_CPU_PROBE_MISSING_NATIVE_IDENTITIES")

    return {
        "schema": "yggdrasil.itd02.source-free-cpu-probe.v1",
        "status": "SOURCE_FREE_DEVELOPMENT_ONLY",
        "environment": MODE,
        "model": "original-Yggdrasil-local-eight-cell-native-task-runtime",
        "platform": platform.system(),
        "architecture": platform.machine(),
        "python_version": platform.python_version(),
        "logical_cores": os.cpu_count(),
        "gpu_required": False,
        "paid_api_required": False,
        "episodes": committed_episodes,
        "public_interactions": confirmed_steps,
        "wall_ms": round(elapsed_wall_ns / 1_000_000, 3),
        "process_cpu_ms": round(elapsed_cpu_ns / 1_000_000, 3),
        "interactions_per_wall_second": round(
            confirmed_steps * 1_000_000_000 / elapsed_wall_ns, 4),
        "episode_p50_ms": _percentile(episode_ms, .5),
        "episode_p95_ms": _percentile(episode_ms, .95),
        "cold_restore_p95_ms": _percentile(cold_restore_ms, .95),
        "initial_peak_rss_bytes": peak_before,
        "final_peak_rss_bytes": peak_after,
        "durable_storage_bytes": disk_bytes,
        "bytes_per_interaction": round(disk_bytes / confirmed_steps, 2),
        "original_native_parameter_changed": (
            original_identities["native"] != final_identities["native"]),
        "native_memory_parameter_changed": (
            original_identities["memory"] != final_identities["memory"]),
        "energy_joules": None,
        "gpu_vram_bytes": None,
        "process_tree_peak_rss_bytes": None,
        "true_retail_hardware_qualification": False,
        "authentic_original_world_executed": False,
        "independent_scientific_qualification": False,
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--episodes", type=int, default=4)
    parser.add_argument("--steps", type=int, default=4)
    args = parser.parse_args()
    report = run_probe(episodes=args.episodes, steps=args.steps)
    print(json.dumps(report, sort_keys=True, separators=(",", ":")))


if __name__ == "__main__":
    main()
