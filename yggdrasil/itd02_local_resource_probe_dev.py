"""Honest local process-cost baseline for the ORIGINAL eight-cell native learner.

Uses deliberately SOURCE-FREE public fixture interactions only. A hosted CI
runner is NOT an out-of-box retail machine, a permitted original Shuttle
experiment, independent science, or a minimum-spec qualification.

The native model chooses each action and performs local learning. The probe
measures the WHOLE single-process training/checkpoint flow, not a kernel-only
microbenchmark. Unknown OS counters are JSON null, never invented zeros.
"""
from __future__ import annotations

import argparse
import json
import os
import platform
from pathlib import Path
import sys
import tempfile
import time
import tracemalloc
import hashlib

from .itd02_native_training_session_dev import NativeTrainingSessionDev
from .itd02_public_source_journal_dev import (
    JournaledPublicSourceDev, load_verified_native_model
)

FIXTURE_SOURCE = hashlib.sha256(
    b"Yggdrasil ITD-02 self-declared SOURCE-FREE cost fixture v1").hexdigest()
ROLE = "OWNER_PUBLIC_FIT_DEVELOPMENT_ONLY"
MAX_EPISODES = 4
MAX_STEPS = 128


class SourceFreeMeterFixture:
    """Generated toy feedback, NOT the published Shuttle environment."""
    def __init__(self, max_steps):
        self.t = 0
        self.max_steps = max_steps
        self.actions = 0

    def reset_public(self):
        return "docked_MRV"

    def step_public(self, action):
        self.t += 1
        self.actions += 1
        # No original state, original model file, or protected source.
        obs = "Nothing" if self.t % 2 else "docked_MRV"
        reward = 10 if action == "Backup" and self.t % 4 == 0 else 0
        return obs, reward, False, self.t == self.max_steps


def _peak_process_rss_bytes():
    """Process peak resident memory; None if OS measurement unavailable."""
    if sys.platform.startswith("linux"):
        try:
            for line in Path("/proc/self/status").read_text().splitlines():
                if line.startswith("VmHWM:"):
                    words = line.split()
                    if len(words) == 3 and words[2] == "kB":
                        return int(words[1]) * 1024
        except (OSError, ValueError):
            pass
        return None
    if sys.platform == "win32":
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
            kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
            psapi = ctypes.WinDLL("psapi", use_last_error=True)
            kernel32.GetCurrentProcess.restype = wintypes.HANDLE
            psapi.GetProcessMemoryInfo.argtypes = [
                wintypes.HANDLE, ctypes.POINTER(Counters), wintypes.DWORD]
            psapi.GetProcessMemoryInfo.restype = wintypes.BOOL
            counters = Counters()
            counters.cb = ctypes.sizeof(Counters)
            if not psapi.GetProcessMemoryInfo(
                kernel32.GetCurrentProcess(), ctypes.byref(counters),
                counters.cb
            ):
                return None
            return int(counters.PeakWorkingSetSize)
        except (AttributeError, OSError, TypeError, ValueError):
            pass
        return None
    return None


def run_source_free_resource_probe(*, episodes=3, steps=16):
    if (type(episodes) is not int or not 1 <= episodes <= MAX_EPISODES or
            type(steps) is not int or not 1 <= steps <= MAX_STEPS):
        raise ValueError("SOURCE_FREE_METER_BUDGET_INVALID")
    # Include full model construction, native updates, all per-step source
    # journals, fsyncs, checksum verification and learned-state reload.
    before_cpu = time.process_time_ns()
    before_wall = time.perf_counter_ns()
    tracemalloc.start()
    total_steps = 0
    disk_bytes = 0
    checkpoint_bytes = 0
    learned = None
    last_hash = None
    with tempfile.TemporaryDirectory(prefix="ygg-itd02-sourcefree-meter-") as root:
        for episode in range(episodes):
            directory = Path(root) / ("episode-%d" % episode)
            fixture = SourceFreeMeterFixture(steps)
            session = NativeTrainingSessionDev(model=learned, max_steps=steps)
            with JournaledPublicSourceDev(
                directory, fixture, episode_id="source-free-meter-%d" % episode,
                source_sha256=FIXTURE_SOURCE, max_steps=steps, role=ROLE,
            ) as custody:
                result = custody.execute_one(session)
            if (result["custody"]["status"] != "COMMITTED"
                    or not result["truncated"] or result["terminal"]
                    or result["steps"] != steps or fixture.actions != steps):
                raise ValueError("SOURCE_FREE_METER_CUSTODY_FAILED")
            learned = load_verified_native_model(
                directory, expected_source_sha256=FIXTURE_SOURCE)
            last_hash = learned.model_identities()
            total_steps += result["steps"]
            disk_bytes += (directory / "public-events.jsonl").stat().st_size
            size = (directory / "learned-checkpoint.bin").stat().st_size
            checkpoint_bytes += size
        peak_py = tracemalloc.get_traced_memory()[1]
        rss_peak = _peak_process_rss_bytes()
    tracemalloc.stop()
    wall_ns = time.perf_counter_ns() - before_wall
    cpu_ns = time.process_time_ns() - before_cpu
    return {
        "schema": "ygg.itd02.source-free-local-resource-probe.v1",
        "evidence_class": "SOURCE_FREE_HOSTED_CI_ENGINEERING_ONLY",
        "authentic_environment_steps": 0,
        "scientific_first_use": False,
        "consumer_retail_acceptance": False,
        "os": platform.system(),
        "machine": platform.machine(),
        "python": platform.python_version(),
        "episodes": episodes,
        "public_interactions": total_steps,
        "training_and_checkpoint_wall_ns": wall_ns,
        "training_and_checkpoint_cpu_ns": cpu_ns,
        "whole_process_peak_rss_bytes": rss_peak,
        "python_tracemalloc_peak_bytes": peak_py,
        "durable_journal_bytes": disk_bytes,
        "checkpoint_bytes": checkpoint_bytes,
        "mean_whole_pipeline_wall_us_per_interaction": (
            round(wall_ns / total_steps / 1000, 3)),
        "native_model_identities": last_hash,
        "peak_power_watts": None,
        "gpu_vram_bytes": None,
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--episodes", type=int, default=3)
    parser.add_argument("--steps", type=int, default=16)
    parser.add_argument("--output", type=Path)
    opts = parser.parse_args()
    receipt = run_source_free_resource_probe(
        episodes=opts.episodes, steps=opts.steps)
    content = json.dumps(receipt, sort_keys=True, indent=2) + "\n"
    if opts.output is not None:
        opts.output.write_text(content, encoding="utf-8")
    print("YGG_ITD02_SOURCEFREE_RESOURCE_PROBE_PASS")
    print(content, end="")


if __name__ == "__main__":
    main()
