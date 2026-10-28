"""V31R-LOC external bank-owned per-cell feature-slot emulation, NOT native execution.

Preregistered per-cell ownership vs original and the old *central* V31N cache.
Never touches shipped learner, source, ring graph, checkpoint, first-use or holdout.
"""
from __future__ import annotations

from contextlib import contextmanager
import json
import math
import os
from pathlib import Path
import statistics
import subprocess
import sys
import time

from research.itd02_v23_unfamiliar_mapping_audit import train_source
from research.itd02_v31q_varied_public_resource_audit import (
    LENGTHS, EVENTS_PER_BLOCK, verified_diversity, extended_replay,
)
from research.itd02_v31o_full_process_resource_audit import actual_os_peak_resident_bytes
import yggdrasil.itd02_v22_shared_context_ring_dev as v22

ROOT = Path(__file__).resolve().parents[1]
SCHEMA = "yggdrasil.itd02.v31r.bank_cell_local_resource.v1"
ARMS = ("baseline", "bank_local", "v31n_central")
PAIRS = 9
WORKER_TIMEOUT = 120
SOURCE_UPDATES = 16 * 36


class LocalSlot:
    __slots__ = ("cue", "first", "row")

    def __init__(self):
        self.cue = None
        self.first = None
        self.row = None

    def clear(self):
        self.cue = None
        self.first = None
        self.row = None


@contextmanager
def bank_cell_local_adapter():
    """8 slots *per bank instance*, no central/global key/value memo table.

    The original _site_features transports once to populate each owner's row.
    This external Python emulation still centrally invokes the original method:
    DO NOT call this a native distributed computation optimization.
    """
    original_features = v22.SharedContextRingDev._features
    original_first = v22.SharedContextRingDev.accept_first
    original_site = v22._site_features
    original_mix = v22._mix_scalars
    stats = {
        "original_feature_builds": 0,
        "bank_local_feature_hits": 0,
        "validated_bank_episode_resets": 0,
        "max_slots_per_bank": 0,
        "slot_rows_persisted_to_checkpoint": False,
        "original_scalar_mix_unchanged": True,
        "original_site_feature_transport_unchanged": True,
        "module_wide_memo_table_created": False,
        "independent_cell_processes_or_scheduling_proven": False,
    }

    def slots(bank):
        result = getattr(bank, "_v31r_cell_slots", None)
        if result is None:
            result = [LocalSlot() for _ in range(v22.CELLS)]
            bank._v31r_cell_slots = result
        if len(result) != 8 or len({id(x) for x in result}) != 8:
            raise AssertionError("V31R_CELL_SLOT_OWNERSHIP_VIOLATION")
        stats["max_slots_per_bank"] = max(stats["max_slots_per_bank"], len(result))
        return result

    def first(bank, *args, **kwargs):
        reply = original_first(bank, *args, **kwargs)
        for slot in slots(bank):
            slot.clear()
        stats["validated_bank_episode_resets"] += 1
        return reply

    def features(bank):
        bank_slots = slots(bank)
        if all(slot.cue == bank.cue and slot.first == bank.first and
               slot.row is not None for slot in bank_slots):
            stats["bank_local_feature_hits"] += 1
            return [list(slot.row) for slot in bank_slots]
        rows = original_features(bank)
        if len(rows) != 8:
            raise AssertionError("V31R_ORIGINAL_CELL_COUNT_DRIFT")
        for cell, slot in enumerate(bank_slots):
            if len(rows[cell]) != v22.HEAD_FEATURES:
                raise AssertionError("V31R_ORIGINAL_CELL_FEATURE_DIMENSION_DRIFT")
            slot.cue = bank.cue
            slot.first = bank.first
            slot.row = tuple(rows[cell])
        stats["original_feature_builds"] += 1
        return rows

    v22.SharedContextRingDev._features = features
    v22.SharedContextRingDev.accept_first = first
    try:
        yield stats
    finally:
        v22.SharedContextRingDev.accept_first = original_first
        v22.SharedContextRingDev._features = original_features
        if v22._site_features is not original_site:
            raise AssertionError("V31R_CENTRAL_INPUT_MEMO_CONTAMINATION")
        if v22._mix_scalars is not original_mix:
            raise AssertionError("V31R_ORIGINAL_SCALAR_ROUTE_CONTAMINATION")


def run(source, blocks, arm, *, cold=False):
    if arm not in ARMS or blocks not in LENGTHS:
        raise ValueError("V31R_UNKNOWN_ARM_OR_LENGTH")
    if arm == "bank_local":
        with bank_cell_local_adapter() as stats:
            signatures = extended_replay(source, blocks, False, cold=cold)
        if (stats["max_slots_per_bank"] != 8 or
                stats["bank_local_feature_hits"] <= 0 or
                stats["original_feature_builds"] != 2 * blocks * EVENTS_PER_BLOCK or
                stats["validated_bank_episode_resets"] !=
                    2 * blocks * EVENTS_PER_BLOCK or
                stats["module_wide_memo_table_created"] is not False or
                stats["original_scalar_mix_unchanged"] is not True):
            raise AssertionError("V31R_BANK_LOCAL_SCOPE_OR_EPISODE_RESET_DRIFT")
    else:
        signatures = extended_replay(source, blocks, arm == "v31n_central",
                                     cold=cold)
        stats = None
    return signatures, stats


def parity_preflight():
    source = train_source()["pretrained_shared"]
    expected = {}
    for blocks in LENGTHS:
        baseline, _ = run(source, blocks, "baseline")
        for arm in ARMS:
            warm, _ = run(source, blocks, arm)
            cold, _ = run(source, blocks, arm, cold=True)
            if warm != baseline or cold != baseline:
                raise AssertionError("V31R_BASELINE_V31N_LOCAL_OR_COLD_PARITY_BROKEN")
        expected[str(blocks)] = baseline
    return expected


def worker(arm, blocks):
    if arm not in ARMS or blocks not in LENGTHS:
        raise AssertionError("V31R_INVALID_WORKER_REQUEST")
    start = time.process_time_ns()
    before_train = time.process_time_ns()
    source = train_source()["pretrained_shared"]
    after_train = time.process_time_ns()
    signatures, local_stats = run(source, blocks, arm)
    after_replay = time.process_time_ns()
    resident, source_name = actual_os_peak_resident_bytes()
    total = time.process_time_ns()
    if not (0 < before_train < after_train < after_replay <= total and
            0 < resident < 1 << 52):
        raise AssertionError("V31R_INVALID_CPU_OR_TRUE_OS_RESIDENT")
    record = {
        "schema": SCHEMA, "role": "fresh_worker", "arm": arm,
        "host": sys.platform, "blocks": blocks, "events": 24 * blocks,
        "total_process_cpu_ns": total,
        "source_training_cpu_ns": after_train - before_train,
        "replay_cpu_ns": after_replay - after_train,
        "peak_resident_bytes": resident,
        "peak_resident_method": source_name,
        "signatures": signatures,
        "public_diversity": verified_diversity(blocks),
        "bank_cell_local_stats": local_stats,
        "fresh_original_source_pretraining": True,
        "independent_native_cell_execution_claimed": False,
        "native_source_modified": False, "scientific_first_use": False,
    }
    print(json.dumps(record, separators=(",", ":"), sort_keys=True,
                     allow_nan=False))


def launch(arm, blocks):
    if arm not in ARMS or blocks not in LENGTHS:
        raise AssertionError("V31R_DISALLOWED_WORKER_DISPATCH")
    env = dict(os.environ)
    env["PYTHONHASHSEED"] = "0"
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    cmd = [sys.executable, "-B", str(Path(__file__).resolve()),
           "--worker", arm, str(blocks)]
    start = time.perf_counter_ns()
    proc = subprocess.run(cmd, cwd=ROOT, env=env, capture_output=True,
                          text=True, timeout=WORKER_TIMEOUT, check=False)
    wall = time.perf_counter_ns() - start
    if proc.returncode or proc.stderr.strip():
        raise AssertionError("V31R_WORKER_FAILURE_{}_{}_{}_{}".format(
            arm, blocks, proc.returncode, proc.stderr[-1000:]))
    try:
        data = json.loads(proc.stdout)
    except (ValueError, TypeError) as exc:
        raise AssertionError("V31R_WORKER_INVALID_JSON") from exc
    if (type(data) is not dict or data.get("schema") != SCHEMA or
            data.get("role") != "fresh_worker" or
            data.get("arm") != arm or data.get("host") != sys.platform or
            data.get("blocks") != blocks or
            data.get("events") != blocks * EVENTS_PER_BLOCK or
            data.get("public_diversity") != verified_diversity(blocks) or
            data.get("fresh_original_source_pretraining") is not True or
            data.get("independent_native_cell_execution_claimed") is not False or
            data.get("native_source_modified") is not False or
            data.get("scientific_first_use") is not False):
        raise AssertionError("V31R_WORKER_SOURCE_OR_DATA_IDENTITY_DRIFT")
    expected_method = ("LINUX_GETRUSAGE_SELF_RU_MAXRSS_KIB_X1024"
                       if sys.platform == "linux" else
                       "WINDOWS_GETPROCESSMEMORYINFO_PEAKWORKINGSETSIZE_BYTES"
                       if sys.platform == "win32" else None)
    if not expected_method or data.get("peak_resident_method") != expected_method:
        raise AssertionError("V31R_GENUINE_OS_RESIDENT_METER_UNAVAILABLE")
    for field in ("total_process_cpu_ns", "source_training_cpu_ns",
                  "replay_cpu_ns", "peak_resident_bytes"):
        if type(data.get(field)) is not int or data[field] <= 0:
            raise AssertionError("V31R_CPU_RSS_RESOURCE_MISSING_" + field)
    signatures = data.get("signatures")
    if (type(signatures) is not list or len(signatures) != blocks or
            any(type(x) is not dict or
                set(x) != {"block", "trace_sha256", "checkpoint_sha256",
                           "schedule_sha256"} or x["block"] != i+1
                for i,x in enumerate(signatures))):
        raise AssertionError("V31R_MISSING_BLOCK_CHECKPOINT_AND_PUBLIC_SCHEDULE")
    if arm == "bank_local":
        stats = data.get("bank_cell_local_stats")
        if (type(stats) is not dict or
                stats.get("max_slots_per_bank") != 8 or
                stats.get("validated_bank_episode_resets") != 48*blocks or
                stats.get("original_feature_builds") != 48*blocks or
                stats.get("bank_local_feature_hits", 0) <= 0 or
                stats.get("module_wide_memo_table_created") is not False or
                stats.get("original_scalar_mix_unchanged") is not True):
            raise AssertionError("V31R_LOCAL_BANK_OWNER_CUSTODY_INVALID")
    elif data.get("bank_cell_local_stats") is not None:
        raise AssertionError("V31R_CONTROL_CONTAMINATED_WITH_CELL_SLOTS")
    if wall <= 0:
        raise AssertionError("V31R_WORKER_WALL_CLOCK_UNAVAILABLE")
    data["wall_process_ns"] = wall
    return data


def ratio(a,b):
    v = a/b
    if not math.isfinite(v) or v <= 0:
        raise AssertionError("V31R_INVALID_RATIO")
    return v


def audit():
    original = parity_preflight()
    measurements = []
    for blocks in LENGTHS:
        reference = original[str(blocks)]
        for arm in ARMS:
            if launch(arm,blocks)["signatures"] != reference:
                raise AssertionError("V31R_WARMUP_PARITY_INVALID")
        paired, centrals = [], []
        for i in range(PAIRS):
            order = ("baseline","bank_local") if i%2 == 0 else (
                "bank_local","baseline")
            readings = {}
            for arm in order:
                readings[arm] = launch(arm,blocks)
                if readings[arm]["signatures"] != reference:
                    raise AssertionError("V31R_PRIMARY_WORKER_PARITY_INVALID")
            ctrl = launch("v31n_central",blocks)
            if ctrl["signatures"] != reference:
                raise AssertionError("V31R_V31N_CENTRAL_COMPARATOR_PARITY_INVALID")
            a,b = readings["baseline"],readings["bank_local"]
            paired.append({
                "trial":i+1,"order":list(order),
                "baseline_cpu_ns":a["total_process_cpu_ns"],
                "local_cpu_ns":b["total_process_cpu_ns"],
                "central_cpu_ns":ctrl["total_process_cpu_ns"],
                "baseline_resident_bytes":a["peak_resident_bytes"],
                "local_resident_bytes":b["peak_resident_bytes"],
                "central_resident_bytes":ctrl["peak_resident_bytes"],
                "baseline_wall_ns":a["wall_process_ns"],
                "local_wall_ns":b["wall_process_ns"],
                "central_wall_ns":ctrl["wall_process_ns"],
                "local_cpu_ratio":ratio(b["total_process_cpu_ns"],
                                        a["total_process_cpu_ns"]),
                "local_resident_ratio":ratio(b["peak_resident_bytes"],
                                             a["peak_resident_bytes"]),
                "local_wall_ratio":ratio(b["wall_process_ns"],
                                         a["wall_process_ns"]),
                "local_to_central_cpu_ratio":ratio(
                    b["total_process_cpu_ns"],ctrl["total_process_cpu_ns"]),
                "local_to_central_resident_ratio":ratio(
                    b["peak_resident_bytes"],ctrl["peak_resident_bytes"]),
            })
            centrals.append(ctrl)
        med = lambda key: statistics.median(row[key] for row in paired)
        measurements.append({
            "blocks":blocks,"events":blocks*EVENTS_PER_BLOCK,
            "public_diversity":verified_diversity(blocks),
            "full_checkpoint_and_trace_identity":True,
            "cold_restored_bank_cell_local_identity":True,
            "baseline_cpu_median_ns":int(med("baseline_cpu_ns")),
            "local_cpu_median_ns":int(med("local_cpu_ns")),
            "central_cpu_median_ns":int(med("central_cpu_ns")),
            "baseline_resident_median_bytes":int(med("baseline_resident_bytes")),
            "local_resident_median_bytes":int(med("local_resident_bytes")),
            "central_resident_median_bytes":int(med("central_resident_bytes")),
            "local_vs_baseline_cpu_ratio_median":round(med("local_cpu_ratio"),8),
            "local_vs_baseline_resident_ratio_median":round(
                med("local_resident_ratio"),8),
            "local_vs_central_cpu_ratio_median":round(
                med("local_to_central_cpu_ratio"),8),
            "local_vs_central_resident_ratio_median":round(
                med("local_to_central_resident_ratio"),8),
            "local_vs_baseline_wall_ratio_median":round(med("local_wall_ratio"),8),
            "pairs":paired,
        })
    med, long = measurements[1], measurements[2]
    positive = (
        med["local_vs_baseline_cpu_ratio_median"] <= .95 and
        med["local_vs_baseline_resident_ratio_median"] <= 1.10 and
        long["local_vs_baseline_cpu_ratio_median"] <= .85 and
        long["local_vs_baseline_resident_ratio_median"] <= 1.10 and
        long["local_vs_central_cpu_ratio_median"] <= 1.20 and
        long["local_vs_central_resident_ratio_median"] <= 1.10
    )
    report = {
        "schema":SCHEMA,
        "classification":("V31R_LOC_HOST_BANK_LOCAL_EMULATION_RESOURCE_POSITIVE__NO_SCIENCE"
                          if positive else
                          "V31R_LOC_NO_JOINT_BANK_LOCAL_RESOURCE_WIN__NO_SCIENCE"),
        "host":sys.platform,"status":"COMPLETE",
        "fresh_workers_launched":90,
        "predeclared_session_blocks":list(LENGTHS),
        "nine_fixed_ab_ba_pairs_and_nine_central_comparators_each_length":True,
        "source_pretrained_once_every_worker":True,
        "true_os_peak_resident_memory":True,
        "slots_owned_per_original_bank_cell":True,
        "independent_native_cells_executed":False,
        "real_physical_ring_messages_measured":False,
        "v31n_central_cache_installed_in_local_arm":False,
        "source_learning_or_checkpoint_changed":False,
        "source_first_block_pinned":True,
        "all_blockwise_signatures_equal_original_and_cold":True,
        "no_science_first_use":True,"sealed_holdout_evaluated":False,
        "cpu96_gate_le":.95,"cpu384_gate_le":.85,
        "resident96_384_gate_le":1.10,
        "local_to_central_cpu384_gate_le":1.20,
        "local_to_central_peak_resident384_gate_le":1.10,
        "results":measurements,
    }
    print(json.dumps(report,sort_keys=True,separators=(",",":"),allow_nan=False))


if __name__ == "__main__":
    if len(sys.argv)==4 and sys.argv[1]=="--worker":
        worker(sys.argv[2],int(sys.argv[3]))
    elif len(sys.argv)==1:
        audit()
    else:
        raise SystemExit("V31R_UNEXPECTED_CLI")
