#!/usr/bin/env python3
"""CPU-only, offline native Yggdrasil engineering soak on SOURCE-FREE toy data.

This program NEVER reads or steps the original published Shuttle benchmark.
The tiny toy consequence rule below is invented for wiring and budget tests;
its reward, action counts, and measured resource use are NOT intelligence
evidence, scientific first-use, or verified retail-PC performance.

Each fresh Python child selects its own actions using the unchanged native
Yggdrasil model, journals effects, checkpoints its learned state, then exits.
The NEXT child cold-restores that model after checking journal custody.
No external API, GPU, scheduler, transformer, or model-writing agent involved.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from yggdrasil.itd02_native_training_session_dev import NativeTrainingSessionDev
from yggdrasil.itd02_public_source_journal_dev import (
    JournaledPublicSourceDev, inspect_custody, load_verified_native_model,
)

SOURCE_FREE = "SOURCE_FREE_TOY_ONLY_NO_ORIGINAL_WORLD"
FIXTURE_SHA = hashlib.sha256(b"itd02-yggdrasil-source-free-offline-soak-v1").hexdigest()
MAX_EPISODES = 24
MAX_STEPS = 32


class ToyPublicConsequence:
    """Original-source-independent tiny development fixture. NOT Shuttle."""

    def __init__(self, steps: int, *, crash: bool = False):
        self.limit = steps
        self.count = 0
        self.crash = crash
        self.reset_count = 0

    def reset_public(self):
        self.reset_count += 1
        if self.reset_count != 1:
            raise RuntimeError("SOURCE_FREE_RESET_REPLAY")
        return "MRV"

    def step_public(self, action):
        if action not in ("TurnAround", "GoForward", "Backup"):
            raise ValueError("SOURCE_FREE_ILLEGAL_ACTION")
        self.count += 1
        if self.crash:
            # Journal's step_intent MUST be fsynced before this hard exit.
            os._exit(87)
        reward = 10 if action == "Backup" else -3 if action == "GoForward" else 0
        observations = ("MRV", "Nothing", "LRV", "docked_MRV")
        return observations[self.count % len(observations)], reward, False, (
            self.count == self.limit)


def peak_self_rss_bytes():
    """Own-process peak RSS only; none means platform source unavailable."""
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
            info = Counters()
            info.cb = ctypes.sizeof(info)
            kernel = ctypes.WinDLL("kernel32", use_last_error=True)
            psapi = ctypes.WinDLL("psapi", use_last_error=True)
            # ctypes' default c_int return would truncate pseudo-HANDLE on
            # 64-bit Windows, making GetProcessMemoryInfo return NULL.
            current = kernel.GetCurrentProcess
            current.argtypes = []
            current.restype = wintypes.HANDLE
            get_counters = psapi.GetProcessMemoryInfo
            get_counters.argtypes = [
                wintypes.HANDLE, ctypes.POINTER(Counters), wintypes.DWORD]
            get_counters.restype = wintypes.BOOL
            ok = get_counters(current(), ctypes.byref(info), info.cb)
            if ok and info.PeakWorkingSetSize > 0:
                return int(info.PeakWorkingSetSize)
        except (AttributeError, ImportError, OSError, ValueError):
            return None
        return None
    try:
        import resource
        size = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
        # macOS ru_maxrss is already bytes; Linux reports KiB.
        return int(size if sys.platform == "darwin" else size * 1024)
    except (ImportError, OSError, ValueError):
        return None


def episode_dir(root, index):
    return root / "episodes" / f"{index:03d}"


def child(root, index, steps, crash_index):
    base = episode_dir(root, index)
    if index:
        previous = episode_dir(root, index - 1)
        model = load_verified_native_model(
            previous, expected_source_sha256=FIXTURE_SHA)
        prior = inspect_custody(
            previous, expected_source_sha256=FIXTURE_SHA)
        if prior["status"] != "COMMITTED" or prior["steps"] != steps:
            raise RuntimeError("SOURCE_FREE_PREVIOUS_EPISODE_NOT_COMMITTED")
    else:
        model = None
    session = NativeTrainingSessionDev(model=model, max_steps=steps)
    before = session.model.model_identities()
    source = ToyPublicConsequence(steps, crash=(index == crash_index))
    cpu_start = time.process_time_ns()
    wall_start = time.perf_counter_ns()
    with JournaledPublicSourceDev(
        base, source, episode_id=f"sourcefree-{index:03d}",
        source_sha256=FIXTURE_SHA,
        max_steps=steps, role="OWNER_PUBLIC_FIT_DEVELOPMENT_ONLY",
    ) as owner:
        result = owner.execute_one(session)
    wall_ns = time.perf_counter_ns() - wall_start
    cpu_ns = time.process_time_ns() - cpu_start
    if result["steps"] != steps or not result["truncated"] or result["terminal"]:
        raise RuntimeError("SOURCE_FREE_EXPECTED_TRUNCATION_MISSING")
    if source.count != steps or source.reset_count != 1:
        raise RuntimeError("SOURCE_FREE_SOURCE_ACTION_ACCOUNTING")
    receipt = inspect_custody(base, expected_source_sha256=FIXTURE_SHA)
    if receipt != result["custody"]:
        raise RuntimeError("SOURCE_FREE_CUSTODY_MISMATCH")
    outcome = {
        "mode": SOURCE_FREE,
        "index": index,
        "steps": steps,
        "reward_toy_only": result["reward"],
        "native_before": before,
        "native_after": session.model.model_identities(),
        "native_transitions": result["transitions"],
        "journal_head": receipt["head"],
        "journal_events": receipt["event_count"],
        "wall_ns": wall_ns,
        # Windows' process_time_ns can round a sub-tick episode to zero.
        # Unknown is NOT zero CPU usage; never invent a precision we lack.
        "process_cpu_ns": cpu_ns if cpu_ns > 0 else None,
        "peak_self_rss_bytes": peak_self_rss_bytes(),
        "checkpoint_bytes": (base / "learned-checkpoint.bin").stat().st_size,
        "journal_bytes": (base / "public-events.jsonl").stat().st_size,
    }
    print(json.dumps(outcome, sort_keys=True))


def soak(root, episodes, steps, crash_index):
    total_wall_start = time.perf_counter_ns()
    if root.exists():
        raise RuntimeError("SOURCE_FREE_FRESH_RUN_ROOT_REQUIRED")
    root.mkdir(parents=True, exist_ok=False, mode=0o700)
    (root / "episodes").mkdir(mode=0o700)
    rows = []
    for i in range(episodes):
        cmd = [sys.executable, "-B", str(Path(__file__).resolve()),
               "--child", "--root", str(root),
               "--episode", str(i), "--steps", str(steps),
               "--crash-episode", str(crash_index)]
        env = dict(os.environ, PYTHONDONTWRITEBYTECODE="1")
        run = subprocess.run(cmd, cwd=ROOT, env=env,
                             capture_output=True, text=True, timeout=60)
        if run.returncode:
            # Fail closed. NEVER reissue a potentially consumed source step.
            current = episode_dir(root, i)
            status = inspect_custody(current) if current.exists() else None
            raise RuntimeError(
                "SOURCE_FREE_CHILD_STOPPED_WITHOUT_REPLAY "
                f"episode={i} rc={run.returncode} custody={status and status['status']} "
                f"stderr={run.stderr[-240:]}")
        data = json.loads(run.stdout)
        if (type(data) is not dict or data.get("mode") != SOURCE_FREE or
                data.get("index") != i or data.get("steps") != steps or
                data.get("native_transitions") != (i+1) * steps):
            raise RuntimeError("SOURCE_FREE_CHILD_METER_OR_SEQUENCE_INVALID")
        if i and data["native_before"] != rows[-1]["native_after"]:
            raise RuntimeError("SOURCE_FREE_MODEL_STATE_NOT_RETAINED")
        rows.append(data)
    result = {
        "status": "SOURCE_FREE_ENGINEERING_ONLY",
        "original_source_episodes": 0,
        "protected_first_use": False,
        "retail_pc_qualified": False,
        "source_free_fixture_sha256": FIXTURE_SHA,
        "os": sys.platform,
        "episodes": episodes,
        "steps_per_episode": steps,
        "total_native_interactions": episodes * steps,
        "cold_process_restarts": max(0, episodes - 1),
        "total_child_cpu_ns": (
            sum(r["process_cpu_ns"] for r in rows)
            if all(r["process_cpu_ns"] is not None for r in rows)
            else None),
        "total_child_wall_ns": sum(r["wall_ns"] for r in rows),
        # Unlike child timing, this includes starting each new Python
        # interpreter and verifying its durable previous checkpoint.
        "total_host_wall_ns": time.perf_counter_ns() - total_wall_start,
        "observed_peak_child_rss_bytes": (
            max(r["peak_self_rss_bytes"] for r in rows)
            if all(r["peak_self_rss_bytes"] is not None for r in rows)
            else None),
        "journal_and_checkpoint_bytes": sum(
            r["journal_bytes"] + r["checkpoint_bytes"] for r in rows),
        "process_tree_peak_rss_bytes": None,
        "power_joules": None,
        "native_parameter_identity_changed": any(
            r["native_before"] != r["native_after"] for r in rows),
        "per_episode": rows,
    }
    path = root / "source-free-metrics.json"
    with path.open("x", encoding="utf-8") as out:
        json.dump(result, out, indent=2, sort_keys=True)
        out.write("\n")
        out.flush()
        os.fsync(out.fileno())
    return result


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, required=True)
    parser.add_argument("--episodes", type=int, default=4)
    parser.add_argument("--steps", type=int, default=8)
    parser.add_argument("--child", action="store_true")
    parser.add_argument("--episode", type=int, default=0)
    parser.add_argument("--crash-episode", type=int, default=-1)
    args = parser.parse_args()
    if not (1 <= args.episodes <= MAX_EPISODES and
            1 <= args.steps <= MAX_STEPS and
            -1 <= args.crash_episode < MAX_EPISODES):
        parser.error("SOURCE_FREE_BOUNDED_BUDGET_REQUIRED")
    if args.child:
        if not 0 <= args.episode < MAX_EPISODES:
            parser.error("SOURCE_FREE_EPISODE_INDEX_INVALID")
        child(args.root.resolve(), args.episode,
              args.steps, args.crash_episode)
    else:
        result = soak(args.root.resolve(), args.episodes,
                      args.steps, args.crash_episode)
        print(json.dumps({
            key: value for key, value in result.items()
            if key != "per_episode"}, sort_keys=True))


if __name__ == "__main__":
    main()
