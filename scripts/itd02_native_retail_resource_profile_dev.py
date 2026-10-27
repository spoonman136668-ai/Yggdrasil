"""CPU-only development resource profile for the original Yggdrasil learner.

NO original Shuttle source read, reset, step, seed, or holdout. A separately
identified, source-FREE public-shaped toy owner executes bounded interactions.
This profiles the WHOLE Python/native-session/journal/checkpoint path on a
runner, not native inference in isolation. Hosted CI is NOT an out-of-box
retail-PC qualification or a genuine intelligence result.

Usage: python -B scripts/itd02_native_retail_resource_profile_dev.py
       --episodes 8 --steps 16 --output /tmp/profile.json
"""
from __future__ import annotations

import argparse
import ctypes
import hashlib
import json
import os
from pathlib import Path
import platform
import tempfile
import time

from yggdrasil.itd02_native_training_session_dev import NativeTrainingSessionDev
from yggdrasil.itd02_public_source_journal_dev import (
    JournaledPublicSourceDev, load_verified_native_model,
)

FIXTURE_ID = hashlib.sha256(
    b"ITD02-SOURCE-FREE-RETAIL-RESOURCE-PROFILE-NOT-ORIGINAL-SHUTTLE"
).hexdigest()
SCHEMA = "ygg.itd02.source-free.whole-process-resource-profile.dev.v1"
OBSERVATIONS = ("Nothing", "docked_MRV", "LRV", "MRV", "docked_LRV")


class SourceFreeOwner:
    """Not an independently acquired environment: measures plumbing ONLY."""

    def __init__(self, steps: int):
        self.limit = steps
        self.count = 0
        self.started = False

    def reset_public(self):
        if self.started:
            raise ValueError("TOY_FIXTURE_RESTART_FORBIDDEN")
        self.started = True
        return "docked_MRV"

    def step_public(self, action):
        if not self.started or self.count >= self.limit:
            raise ValueError("TOY_FIXTURE_STEP_INVALID")
        self.count += 1
        reward = 10 if action == "Backup" else 0
        return (OBSERVATIONS[self.count % len(OBSERVATIONS)], reward,
                False, self.count == self.limit)


def process_memory():
    """Current+high-water process RSS, null if unavailable; never invent 0."""
    if platform.system() == "Windows":
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
        item = Counters()
        item.cb = ctypes.sizeof(item)
        handle = ctypes.windll.kernel32.GetCurrentProcess()
        valid = ctypes.windll.psapi.GetProcessMemoryInfo(
            handle, ctypes.byref(item), item.cb)
        if valid:
            return int(item.WorkingSetSize), int(item.PeakWorkingSetSize)
        return None, None
    if platform.system() == "Linux":
        try:
            status = Path("/proc/self/status").read_text("utf-8")
            entries = {}
            for line in status.splitlines():
                key, _, value = line.partition(":")
                if key in ("VmRSS", "VmHWM"):
                    fields = value.split()
                    if len(fields) == 2 and fields[1] == "kB":
                        entries[key] = int(fields[0]) * 1024
            return entries.get("VmRSS"), entries.get("VmHWM")
        except (OSError, ValueError):
            return None, None
    return None, None


def profile(episodes: int, steps: int):
    if type(episodes) is not int or not 1 <= episodes <= 64:
        raise ValueError("PROFILE_EPISODE_BUDGET")
    if type(steps) is not int or not 1 <= steps <= 512:
        raise ValueError("PROFILE_STEP_BUDGET")
    initial_rss, initial_high = process_memory()
    wall_start = time.perf_counter_ns()
    cpu_start = time.process_time_ns()
    last_model = None
    identities = []
    completed = 0
    total_bytes = 0
    checkpoint_bytes = 0
    episode_ms = []

    with tempfile.TemporaryDirectory(prefix="ygg-sourcefree-profile-") as scratch:
        for index in range(episodes):
            folder = Path(scratch) / ("episode-%03d" % index)
            fixture = SourceFreeOwner(steps)
            session = NativeTrainingSessionDev(model=last_model, max_steps=steps)
            start = time.perf_counter_ns()
            with JournaledPublicSourceDev(
                folder, fixture, episode_id="sourcefree-profile-%03d" % index,
                source_sha256=FIXTURE_ID, max_steps=steps,
                role="OWNER_PUBLIC_FIT_DEVELOPMENT_ONLY",
            ) as owner:
                result = owner.execute_one(session)
            episode_ms.append((time.perf_counter_ns() - start) / 1_000_000)
            if (result["steps"] != steps or result["terminal"] or
                    not result["truncated"] or
                    result["custody"]["status"] != "COMMITTED" or
                    result["custody"]["source_sha256"] != FIXTURE_ID):
                raise RuntimeError("TOY_PROFILE_CUSTODY_INCOMPLETE")
            model = load_verified_native_model(
                folder, expected_source_sha256=FIXTURE_ID)
            if model.transitions != (index + 1) * steps:
                raise RuntimeError("TOY_PROFILE_NATIVE_TRANSITIONS_NOT_RETAINED")
            identities.append(model.model_identities())
            last_model = model
            completed += fixture.count
            total_bytes += (folder / "public-events.jsonl").stat().st_size
            checkpoint_bytes += (folder / "learned-checkpoint.bin").stat().st_size

    cpu_ns = time.process_time_ns() - cpu_start
    wall_ns = time.perf_counter_ns() - wall_start
    final_rss, final_high = process_memory()
    if completed != episodes * steps or len(identities) != episodes:
        raise RuntimeError("TOY_PROFILE_STEP_ACCOUNTING_MISMATCH")
    report = {
        "schema": SCHEMA,
        "classification": "SOURCE_FREE_ENGINEERING_ONLY",
        "not_scientific_first_use": True,
        "not_retail_hardware_acceptance": True,
        "source_sha256": FIXTURE_ID,
        "source_is_original_published_shuttle": False,
        "architecture": "unchanged-Yggdrasil-eight-cell-native-local-task-runtime",
        "environment": {
            "os": platform.system(),
            "architecture": platform.machine(),
            "logical_cpu_count": os.cpu_count(),
            "python_version": platform.python_version(),
            "local_python_development_environment_required": True,
            "paid_api_calls": 0,
            "gpu_path_used": False,
            "child_processes_spawned": 0,
        },
        "episodes": episodes,
        "public_action_interactions": completed,
        "native_cold_restores": episodes,
        "wall_seconds": round(wall_ns / 1e9, 6),
        "process_cpu_seconds": round(cpu_ns / 1e9, 6),
        "end_to_end_interactions_per_wall_second": round(
            completed / (wall_ns / 1e9), 4),
        "average_wall_ms_per_public_interaction_including_fsynchronization": round(
            wall_ns / 1e6 / completed, 5),
        "maximum_episode_wall_ms": round(max(episode_ms), 4),
        "resident_memory_start_bytes": initial_rss,
        "resident_memory_final_bytes": final_rss,
        "peak_process_resident_bytes": final_high,
        "baseline_peak_process_resident_bytes": initial_high,
        "total_on_disk_public_event_journal_bytes": total_bytes,
        "total_on_disk_checkpoints_bytes": checkpoint_bytes,
        "checkpoint_bytes_per_episode": round(checkpoint_bytes / episodes, 2),
        "process_tree_memory_bytes": None,
        "gpu_memory_bytes": None,
        "power_watts": None,
        "energy_joules": None,
        "temperatures_celsius": None,
        "retail_clean_install_verified": False,
        "independent_scientific_advantage": None,
    }
    return report


def main():
    cli = argparse.ArgumentParser()
    cli.add_argument("--episodes", type=int, default=8)
    cli.add_argument("--steps", type=int, default=16)
    cli.add_argument("--output", type=Path)
    args = cli.parse_args()
    result = profile(args.episodes, args.steps)
    raw = json.dumps(result, sort_keys=True, indent=2) + "\n"
    if args.output:
        args.output.write_text(raw, encoding="utf-8")
    print(raw, end="")


if __name__ == "__main__":
    main()
