"""WSP80 isolated development-only training/readout CPU and peak RSS audit.

No registered scientific sources, FIRST-use, scientific acceptance, hidden
labels or evaluator private truth. Parent creates one common genuinely charged
developer-9001 public ledger; isolated fresh child processes each fit exactly
that same ledger. Each model is evaluated for forced + native-confidence
cold predictions over all 384 PUBLIC state/action queries. No disk artifacts.
Process CPU excludes common action acquisition and interpreter startup; process
peak RSS includes interpreter imports. No scientific cost parity claim.
"""
from __future__ import annotations

import ctypes
from hashlib import sha256
from itertools import product
import json
import os
from pathlib import Path
import subprocess
import sys
from time import perf_counter_ns, process_time_ns
from types import SimpleNamespace

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[3]
DEV = 9001
CHARGES = 384
STAGE_A = 144
SOURCE_BLOB = "c5d0ab0dcf38b2f2dec1e60d7d8346eb2c2697d2"
PREREG_BLOB = "0e96f4e0eff1ced7f87b754a2ad4fbb75c7b3d58"
FROZEN_ADAM_BLOB = "90bca703948c71e482892d2be830682201342368"


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"),
                      allow_nan=False)


def digest(value):
    return sha256(canonical(value).encode("ascii")).hexdigest()


def git(*args):
    return subprocess.run(["git", *args], cwd=REPO, text=True, check=True,
                          capture_output=True).stdout.strip()


def verify_readonly_custody():
    sha = git("rev-parse", "HEAD")
    if len(sha) != 40 or (os.getenv("GITHUB_SHA") and os.getenv("GITHUB_SHA") != sha):
        raise RuntimeError("exact source SHA drift")
    identities = {
        "research/contrib/chatgpt/WSP-80/source.py": SOURCE_BLOB,
        "research/contrib/chatgpt/WSP-80/prereg.json": PREREG_BLOB,
        "research/contrib/chatgpt/WSP-77/fully_trained_mlp6.py": FROZEN_ADAM_BLOB,
    }
    for path, blob in identities.items():
        if git("rev-parse", "HEAD:" + path) != blob:
            raise RuntimeError("frozen research identity changed: " + path)
    if git("status", "--porcelain"):
        raise RuntimeError("source checkout dirty")
    return sha, identities


def peak_rss_bytes():
    """Exact OS process high-water resident set; fail closed if unsupported."""
    if sys.platform.startswith("linux"):
        import resource
        return int(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss) * 1024
    if sys.platform == "win32":
        from ctypes import wintypes
        size_t = ctypes.c_size_t
        class MemoryCounters(ctypes.Structure):
            _fields_ = [
                ("cb", wintypes.DWORD),
                ("PageFaultCount", wintypes.DWORD),
                ("PeakWorkingSetSize", size_t),
                ("WorkingSetSize", size_t),
                ("QuotaPeakPagedPoolUsage", size_t),
                ("QuotaPagedPoolUsage", size_t),
                ("QuotaPeakNonPagedPoolUsage", size_t),
                ("QuotaNonPagedPoolUsage", size_t),
                ("PagefileUsage", size_t),
                ("PeakPagefileUsage", size_t),
                ("PrivateUsage", size_t),
            ]
        kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
        kernel32.GetCurrentProcess.restype = ctypes.c_void_p
        psapi = ctypes.WinDLL("psapi", use_last_error=True)
        psapi.GetProcessMemoryInfo.argtypes = [
            ctypes.c_void_p, ctypes.POINTER(MemoryCounters), wintypes.DWORD]
        psapi.GetProcessMemoryInfo.restype = wintypes.BOOL
        counters = MemoryCounters()
        counters.cb = ctypes.sizeof(MemoryCounters)
        ok = psapi.GetProcessMemoryInfo(
            kernel32.GetCurrentProcess(), ctypes.byref(counters), counters.cb)
        if not ok or counters.PeakWorkingSetSize < 4096:
            raise OSError("Windows PeakWorkingSetSize unavailable")
        return int(counters.PeakWorkingSetSize)
    raise RuntimeError("unsupported OS for native process RSS")


def normalized_rows(rows):
    if type(rows) is not list or len(rows) != CHARGES:
        raise ValueError("missing matched 384-action public ledger")
    from controls import paid_rows
    experiences = []
    for row in rows:
        if type(row) is not list or len(row) != 4:
            raise ValueError("invalid observation shape")
        before, action, after, cost = row
        if type(before) is not list or type(after) is not list:
            raise ValueError("not a public state tuple")
        experiences.append(SimpleNamespace(
            before=tuple(before), action=action, after=tuple(after),
            action_cost=cost))
    paid_rows(experiences)
    return experiences


def run_child(arm):
    if arm not in ("programmed", "adam"):
        raise PermissionError("unsupported developer comparator")
    wire = sys.stdin.read(CHARGES * 140)
    rows = json.loads(wire)
    ledger = normalized_rows(rows)
    ledger_digest = digest(rows)
    states = tuple(product((0, 1), repeat=6))
    queries = tuple((s, action) for s in states for action in range(6))
    start_wall, start_cpu = perf_counter_ns(), process_time_ns()
    if arm == "programmed":
        from structural_weights import PaidStructuralWeightEditor
        model = PaidStructuralWeightEditor()
        for event in ledger:
            model.charge(event.before, event.action, event.after, event.action_cost)
        train_receipt = model.compile()
        model = PaidStructuralWeightEditor.restore(model.snapshot())
        if model.charges != CHARGES:
            raise AssertionError("programmed cold-restoration charge mismatch")
    else:
        from controls import ConventionalAdam384
        model = ConventionalAdam384(DEV)
        train_receipt = model.fit(ledger)
        if (len(train_receipt["trials"]) != 3
                or sorted(t["restart"] for t in train_receipt["trials"]) != [0, 1, 2]):
            raise AssertionError("real three-restart Adam training incomplete")
    train_cpu = process_time_ns() - start_cpu
    train_wall = perf_counter_ns() - start_wall
    output = []
    for state, action in queries:
        if arm == "programmed":
            forced = model.predict(state, action, force=True)
            native = model.predict(state, action)
        else:
            forced = model.predict(state, action, confidence=False)
            native = model.predict(state, action, confidence=True)
        output.append([forced, native])
    total_cpu = process_time_ns() - start_cpu
    total_wall = perf_counter_ns() - start_wall
    summary = {
        "schema": "wsp80.isolated-developer-cost-arm.v1",
        "classification": "DEV_ONLY_NOT_SCIENTIFIC",
        "arm": arm,
        "paid_actions": len(ledger),
        "paid_ledger_sha256": ledger_digest,
        "public_prediction_sha256": digest(output),
        "cold_public_query_pairs": len(queries),
        "prediction_passes_per_pair": 2,
        "training_cpu_ns": train_cpu,
        "training_wall_ns": train_wall,
        "native_and_forced_readout_cpu_ns": total_cpu - train_cpu,
        "native_and_forced_readout_wall_ns": total_wall - train_wall,
        "train_plus_readout_process_cpu_ns": total_cpu,
        "train_plus_readout_process_wall_ns": total_wall,
        "peak_process_rss_bytes": peak_rss_bytes(),
        "genuine_training_converged": (
            train_receipt["fully_trained"] if arm == "adam" else None),
        "train_receipt": train_receipt,
    }
    print(canonical(summary), flush=True)


def run_parent():
    if sys.argv[1:] != ["--developer-only"]:
        raise PermissionError("registered world access forbidden")
    sha, frozen_blobs = verify_readonly_custody()
    from private_experiment import collect_developer_sessions
    from source import World
    world = World(DEV, "quartic_positive", tuple(range(6)), tuple(range(6)))
    shared_start = process_time_ns()
    paid = collect_developer_sessions(world, seed=DEV)
    shared_acquisition_cpu = process_time_ns() - shared_start
    events = paid["candidate_ledger"]
    rows = [[list(x.before), x.action, list(x.after), x.action_cost]
            for x in events]
    stdin_content = canonical(rows)
    common_digest = digest(rows)
    arms = {}
    for arm in ("programmed", "adam"):
        child = subprocess.run([sys.executable, str(HERE / "developer_cost_process.py"),
                                "--child", arm],
                               input=stdin_content, capture_output=True,
                               text=True, timeout=1500, check=True,
                               env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1"})
        record = json.loads(child.stdout.strip())
        if (record["arm"] != arm or
                record["paid_ledger_sha256"] != common_digest or
                record["paid_actions"] != CHARGES or
                record["cold_public_query_pairs"] != 384 or
                record["prediction_passes_per_pair"] != 2 or
                record["peak_process_rss_bytes"] <= 0 or
                record["train_plus_readout_process_cpu_ns"] <= 0):
            raise AssertionError("incomplete isolated process measurement")
        arms[arm] = record
    ratio = (arms["programmed"]["train_plus_readout_process_cpu_ns"] /
             arms["adam"]["train_plus_readout_process_cpu_ns"])
    if not arms["adam"]["genuine_training_converged"]:
        classification = "DEV_MLP_INCOMPLETE"
    else:
        classification = "DEV_ISOLATED_COST_MEASURED"
    output = {
        "schema": "wsp80.isolated-developer-cost-probe.v1",
        "classification": classification,
        "source_commit_sha": sha,
        "frozen_git_blobs": frozen_blobs,
        "registered_selftest_used": False,
        "candidate_paid_actions": CHARGES,
        "independently_paid_random_actions": len(paid["random_ledger"]),
        "common_stageA_each": STAGE_A,
        "candidate_ledger_sha256": common_digest,
        "shared_developer_acquisition_cpu_ns_unattributed": shared_acquisition_cpu,
        "arms": arms,
        "programmed_to_adam_isolated_cpu_ratio": ratio,
        "whole_process_end_to_end_cost_parity_qualified": False,
        "source_admission_approved": False,
        "scientific_signal": "UNVERIFIED",
    }
    print("WSP80_ISOLATED_COST_DEV_RESULT=" + canonical(output), flush=True)


if __name__ == "__main__":
    if sys.argv[1:2] == ["--child"]:
        if len(sys.argv) != 3:
            raise PermissionError("invalid child")
        run_child(sys.argv[2])
    else:
        run_parent()
