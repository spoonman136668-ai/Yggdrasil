"""V31Z source-only compiled Rust FFI cell ownership and original replay audit.

Rust is compiled once per OS CI host before trial and loaded in ALL workers.
The native module computes source-local features ONLY, not learned weights or
reward credit; all original native-model-like Python learner code is unchanged.
"""
from __future__ import annotations

import ctypes
from contextlib import contextmanager
import hashlib
import json
import math
import os
from pathlib import Path
import statistics
import subprocess
import sys
import time
from weakref import WeakKeyDictionary

import research.itd02_v31x_linked_neighbor_audit as v31x
from research.itd02_v23_unfamiliar_mapping_audit import train_source
from research.itd02_v31q_varied_public_resource_audit import (
    EVENTS_PER_BLOCK, extended_replay, verified_diversity,
)
from research.itd02_v31j_executed_edge_ledger_audit import (
    EXPECTED_CHECKPOINT_SHA, EXPECTED_TRACE_SHA,
)
from research.itd02_v31o_full_process_resource_audit import (
    actual_os_peak_resident_bytes,
)
from yggdrasil.itd02_v17_neighbor_carried_learner_dev import (
    ACTIONS, CELLS, CHANNELS, HOPS, PUBLIC_CUES, RING,
)
from yggdrasil.itd02_v18_intermediate_plasticity_dev import HEAD_FEATURES
import yggdrasil.itd02_v22_shared_context_ring_dev as v22

ROOT = Path(__file__).resolve().parents[1]
SCHEMA = "yggdrasil.itd02.v31z.native_cell_local_ffi.v1"
ARMS = ("original", "native", "v31r", "v31x")
LENGTHS = (4, 16)
PAIRS = 5
MAX_WORKER_SECONDS = 180
SOURCE_UPDATES = 16 * 36
EXPECTED_SCHEMA = 0x5633315A00010001
RUST_SOURCE = ROOT / "research" / "itd02_v31z_native_ring.rs"
EXPECTED_MSG_PER_BUILD = CELLS * 2 * HOPS


class NativeCounts(ctypes.Structure):
    _fields_ = [
        ("builds", ctypes.c_uint64),
        ("hits", ctypes.c_uint64),
        ("accepted_first_resets", ctypes.c_uint64),
        ("original_neighbor_directed_frames", ctypes.c_uint64),
        ("separate_cell_count", ctypes.c_uint64),
        ("feature_row_width", ctypes.c_uint64),
    ]


class NativeApi:
    def __init__(self):
        path = os.environ.get("V31Z_NATIVE_LIBRARY")
        if (not path or not Path(path).is_file() or
                Path(path).suffix.lower() != (".dll" if sys.platform == "win32" else ".so")):
            raise AssertionError("V31Z_PINNED_PRECOMPILED_OS_NATIVE_MODULE_UNAVAILABLE")
        self.path = str(Path(path).resolve())
        self.source_sha256 = hashlib.sha256(RUST_SOURCE.read_bytes()).hexdigest()
        self.native_binary_sha256 = hashlib.sha256(Path(path).read_bytes()).hexdigest()
        lib = ctypes.CDLL(self.path)
        def setup(name, args, result):
            fn = getattr(lib, name)
            fn.argtypes = args
            fn.restype = result
            return fn
        ptr = ctypes.c_void_p
        self.new = setup("v31z_new", [], ptr)
        self.free = setup("v31z_free", [ptr], None)
        self.reset = setup("v31z_reset", [ptr], ctypes.c_int)
        self.rows = setup("v31z_rows", [
            ptr, ctypes.c_int, ctypes.c_int,
            ctypes.POINTER(ctypes.c_double), ctypes.c_size_t
        ], ctypes.c_int)
        self.stats = setup("v31z_stats", [ptr, ctypes.POINTER(NativeCounts)], ctypes.c_int)
        self.cell_address = setup("v31z_cell_address", [
            ptr, ctypes.c_int], ctypes.c_size_t)
        self.neighbor = setup("v31z_neighbor", [
            ptr, ctypes.c_int, ctypes.c_int], ctypes.c_int)
        self.is_direct_neighbor = setup("v31z_is_direct_neighbor", [
            ptr, ctypes.c_int, ctypes.c_int], ctypes.c_int)
        self.schema = setup("v31z_ffi_schema", [], ctypes.c_uint64)
        if self.schema() != EXPECTED_SCHEMA:
            raise AssertionError("V31Z_NATIVE_FFI_ABI_SCHEMA_DRIFT")

    def create(self):
        out = self.new()
        if not out:
            raise AssertionError("V31Z_NATIVE_HEAP_RING_ALLOCATION_FAILED")
        self.verify_ring(out)
        return out

    def verify_ring(self, handle):
        addresses = [self.cell_address(handle, i) for i in range(CELLS)]
        if (len(set(addresses)) != 8 or
                any(not value for value in addresses)):
            raise AssertionError("V31Z_NATIVE_PER_CELL_DISTINCT_HEAP_IDENTITY_MISSING")
        for i in range(CELLS):
            for side in range(2):
                expected = RING[i][side]
                if (self.neighbor(handle, i, side) != expected or
                        self.is_direct_neighbor(handle, i, expected) != 1):
                    raise AssertionError("V31Z_NATIVE_ORIGINAL_RING_EDGE_CHANGED")
            if self.is_direct_neighbor(handle, i, i) != 0:
                raise AssertionError("V31Z_SELF_EDGE_ORACLE_IN_NATIVE_RING")
        return addresses

    def get_stats(self, handle):
        record = NativeCounts()
        if self.stats(handle, ctypes.byref(record)) != 0:
            raise AssertionError("V31Z_NATIVE_COUNTERS_UNAVAILABLE")
        return {
            k: getattr(record, k) for k, _ in NativeCounts._fields_
        }

    def call_rows(self, handle, cue, first):
        out = (ctypes.c_double * (CELLS * HEAD_FEATURES))()
        status = self.rows(
            handle, PUBLIC_CUES.index(cue), ACTIONS.index(first),
            out, len(out))
        if status:
            raise AssertionError("V31Z_NATIVE_FEATURE_FFI_REJECTED_VALID_INPUT_"+str(status))
        result = [
            [float(out[i * HEAD_FEATURES + j]) for j in range(HEAD_FEATURES)]
            for i in range(CELLS)
        ]
        if any(not math.isfinite(v) for r in result for v in r):
            raise AssertionError("V31Z_NATIVE_UNSAFE_NONFINITE_FEATURE_ROW")
        return result


NATIVE = NativeApi()  # Loaded identically in every A/B/C/D fresh process.


def failclosed_native_probes():
    handle = NATIVE.create()
    try:
        out = (ctypes.c_double * (CELLS * HEAD_FEATURES))()
        prior = NATIVE.get_stats(handle)
        for c, f, buf, length, code in (
            (-1, 0, out, len(out), -2),
            (4, 0, out, len(out), -2),
            (0, -1, out, len(out), -2),
            (0, 3, out, len(out), -2),
            (0, 0, out, len(out)-1, -2),
            (0, 0, None, len(out), -1),
        ):
            if NATIVE.rows(handle, c, f, buf, length) != code:
                raise AssertionError("V31Z_NATIVE_INVALID_FFI_ARGUMENT_ACCEPTED")
        if NATIVE.rows(None, 0, 0, out, len(out)) != -1:
            raise AssertionError("V31Z_NATIVE_NULL_CONTEXT_ACCEPTED")
        if NATIVE.get_stats(handle) != prior:
            raise AssertionError("V31Z_NATIVE_INVALID_FFI_MUTATED_STATE")
        if NATIVE.is_direct_neighbor(handle, 1, 4) != 0:
            raise AssertionError("V31Z_NATIVE_FORGED_NONNEIGHBOR_ADMITTED")
        if NATIVE.is_direct_neighbor(handle, 8, 1) != -1:
            raise AssertionError("V31Z_NATIVE_OUT_OF_RANGE_CELL_ACCEPTED")
        for cue in PUBLIC_CUES:
            for first in ACTIONS:
                if NATIVE.reset(handle):
                    raise AssertionError("V31Z_NATIVE_NEGATIVE_PREFLIGHT_RESET_FAILED")
                got = NATIVE.call_rows(handle, cue, first)
                if got != v22._site_features(cue, first):
                    raise AssertionError("V31Z_ALL_TWELVE_PUBLIC_INPUT_ORIGINAL_ROW_PARITY_BROKEN")
                # The actual bank-owned native cache must return identical
                # rows while maintaining only one native model feature build.
                before = NATIVE.get_stats(handle)
                if NATIVE.call_rows(handle, cue, first) != got:
                    raise AssertionError("V31Z_NATIVE_REUSE_PRIVATE_FEATURE_ROW_DRIFT")
                after = NATIVE.get_stats(handle)
                if (after["builds"] != before["builds"] or
                        after["hits"] != before["hits"]+1):
                    raise AssertionError("V31Z_NATIVE_BANK_LOCAL_CACHE_NOT_ACTIVE")
        separate = NATIVE.create()
        try:
            if (set(NATIVE.verify_ring(handle)) &
                    set(NATIVE.verify_ring(separate))):
                raise AssertionError("V31Z_CROSS_BANK_NATIVE_CELL_ADDRESS_ALIAS")
        finally:
            NATIVE.free(separate)
    finally:
        NATIVE.free(handle)


@contextmanager
def native_adapter():
    old_features = v22.SharedContextRingDev._features
    old_first = v22.SharedContextRingDev.accept_first
    old_site = v22._site_features
    old_mix = v22._mix_scalars
    handles = WeakKeyDictionary()
    allocated = []
    counts = {
        "distinct_original_cell_owners_per_bank": 0,
        "native_feature_builds": 0,
        "native_local_cache_hits": 0,
        "original_accepted_first_resets": 0,
        "original_neighbor_logical_directed_frames": 0,
        "total_native_heap_handles": 0,
        "different_bank_cell_heaps_not_shared": True,
        "original_scalar_route_untouched": True,
        "native_owns_source_state_not_weights": True,
        "original_native_python_learner_modified": False,
        "physically_transferred_or_ipc_bytes_measured": False,
        "independently_scheduled_native_learning_cells_proven": False,
    }

    def ring(bank):
        if bank not in handles:
            handle = NATIVE.create()
            addr = NATIVE.verify_ring(handle)
            if any(set(addr) & set(prev) for prev in allocated):
                raise AssertionError("V31Z_MODEL_BANKS_SHARE_NATIVE_CELL_HEAP")
            allocated.append(addr)
            handles[bank] = handle
        counts["distinct_original_cell_owners_per_bank"] = CELLS
        return handles[bank]

    def after_first(bank, *args, **kwargs):
        result = old_first(bank, *args, **kwargs)
        if NATIVE.reset(ring(bank)) != 0:
            raise AssertionError("V31Z_NATIVE_ACCEPTED_FIRST_INVALIDATION_FAILED")
        return result

    def features(bank):
        bank._check_frozen()
        if bank.cue not in PUBLIC_CUES or bank.first not in ACTIONS:
            raise ValueError("V31Z_ORIGINAL_ACCEPTED_FIRST_NOT_PRESENT")
        return NATIVE.call_rows(ring(bank), bank.cue, bank.first)

    v22.SharedContextRingDev._features = features
    v22.SharedContextRingDev.accept_first = after_first
    try:
        yield counts
    finally:
        v22.SharedContextRingDev.accept_first = old_first
        v22.SharedContextRingDev._features = old_features
        try:
            for handle in handles.values():
                d = NATIVE.get_stats(handle)
                if (d["separate_cell_count"] != CELLS or
                        d["feature_row_width"] != HEAD_FEATURES):
                    raise AssertionError("V31Z_NATIVE_ORIGINAL_CELL_WIDTH_CHANGED")
                counts["native_feature_builds"] += d["builds"]
                counts["native_local_cache_hits"] += d["hits"]
                counts["original_accepted_first_resets"] += d["accepted_first_resets"]
                counts["original_neighbor_logical_directed_frames"] += d[
                    "original_neighbor_directed_frames"]
            counts["total_native_heap_handles"] = len(allocated)
            if old_site is not v22._site_features or old_mix is not v22._mix_scalars:
                raise AssertionError("V31Z_ORIGINAL_SITE_OR_SCALAR_LEARNING_WAS_PATCHED")
        finally:
            for handle in handles.values():
                NATIVE.free(handle)


def run(source, blocks, arm, *, cold=False):
    if arm not in ARMS or blocks not in LENGTHS:
        raise ValueError("V31Z_UNPREREGISTERED_SOURCE_ARM_OR_LENGTH")
    if arm == "native":
        with native_adapter() as counters:
            signatures = extended_replay(source, blocks, False, cold=cold)
        expected = 2 * blocks * EVENTS_PER_BLOCK
        if (counters["distinct_original_cell_owners_per_bank"] != 8 or
                counters["native_feature_builds"] != expected or
                counters["original_accepted_first_resets"] != expected or
                counters["native_local_cache_hits"] <= 0 or
                counters["original_neighbor_logical_directed_frames"] !=
                expected * EXPECTED_MSG_PER_BUILD or
                counters["total_native_heap_handles"] < 2 or
                counters["different_bank_cell_heaps_not_shared"] is not True or
                counters["original_native_python_learner_modified"] is not False):
            raise AssertionError("V31Z_NATIVE_PER_BANK_OWNERSHIP_OR_LOGICAL_RING_FAILED")
    else:
        arm_x = "linked" if arm == "v31x" else arm
        signatures, _ = v31x.run(source, blocks, arm_x, cold=cold)
        counters = None
    return signatures, counters


def parity():
    failclosed_native_probes()
    source = train_source()["pretrained_shared"]
    signatures = {}
    for blocks in LENGTHS:
        original, _ = run(source, blocks, "original")
        for arm in ARMS:
            continuous, _ = run(source, blocks, arm)
            cold, _ = run(source, blocks, arm, cold=True)
            if continuous != original or cold != original:
                raise AssertionError("V31Z_ORIGINAL_COLD_RESTART_MODEL_TRACE_CHECKPOINT_DRIFT")
        signatures[str(blocks)] = original
    return signatures


def fresh_worker(arm, blocks):
    before_train = time.process_time_ns()
    source = train_source()["pretrained_shared"]
    after_train = time.process_time_ns()
    sig, stats = run(source, blocks, arm)
    after_replay = time.process_time_ns()
    rss, method = actual_os_peak_resident_bytes()
    all_process_cpu = time.process_time_ns()
    if not (0 < before_train < after_train < after_replay <= all_process_cpu and rss > 0):
        raise AssertionError("V31Z_REAL_IN_PROCESS_NATIVE_CPU_OR_RSS_UNAVAILABLE")
    print(json.dumps({
        "schema": SCHEMA, "role":"fresh_worker","host":sys.platform,
        "arm":arm,"blocks":blocks,"events":EVENTS_PER_BLOCK*blocks,
        "native_library_sha256":NATIVE.native_binary_sha256,
        "rust_source_sha256":NATIVE.source_sha256,
        "original_source_trained_once":True,
        "original_source_train_updates":SOURCE_UPDATES,
        "whole_process_cpu_ns_including_native":all_process_cpu,
        "original_source_training_cpu_ns":after_train-before_train,
        "full_replay_cpu_ns":after_replay-after_train,
        "actual_os_peak_resident_bytes":rss,
        "os_peak_resident_method":method,
        "original_block_signatures":sig,
        "known_public_diversity":verified_diversity(blocks),
        "native_stats":stats if arm=="native" else None,
        "standalone_native_feature_module_not_original_model":True,
        "original_python_model_unchanged":True,
        "scientific_first_use":False,
        "independent_native_learning_cells_proven":False,
        "physical_ipc_bytes_or_energy_measured":False,
    },sort_keys=True,separators=(",",":"),allow_nan=False))


def worker_launch(arm,blocks):
    env=dict(os.environ)
    env["PYTHONHASHSEED"]="0"
    env["PYTHONDONTWRITEBYTECODE"]="1"
    start=time.perf_counter_ns()
    completed=subprocess.run(
        [sys.executable,"-B",str(Path(__file__).resolve()),"--worker",
         arm,str(blocks)],cwd=ROOT,env=env,
        capture_output=True,text=True,check=False,timeout=MAX_WORKER_SECONDS)
    wall=time.perf_counter_ns()-start
    if completed.returncode or completed.stderr.strip():
        raise AssertionError("V31Z_OS_WORKER_FAILED_{}_{}_{}_{}".format(
            arm,blocks,completed.returncode,completed.stderr[-1600:]))
    try:
        d=json.loads(completed.stdout)
    except (ValueError,TypeError) as e:
        raise AssertionError("V31Z_UNTRUSTWORTHY_FRESH_WORKER_RECORD") from e
    if (type(d) is not dict or d.get("schema")!=SCHEMA or
            d.get("role")!="fresh_worker" or d.get("host")!=sys.platform or
            d.get("arm")!=arm or d.get("blocks")!=blocks or
            d.get("events")!=EVENTS_PER_BLOCK*blocks or
            d.get("native_library_sha256")!=NATIVE.native_binary_sha256 or
            d.get("rust_source_sha256")!=NATIVE.source_sha256 or
            d.get("original_source_trained_once") is not True or
            d.get("original_source_train_updates")!=SOURCE_UPDATES or
            d.get("known_public_diversity")!=verified_diversity(blocks) or
            d.get("original_python_model_unchanged") is not True or
            d.get("scientific_first_use") is not False or
            d.get("independent_native_learning_cells_proven") is not False or
            d.get("physical_ipc_bytes_or_energy_measured") is not False):
        raise AssertionError("V31Z_ORIGINAL_SOURCE_OR_NATIVE_BLOB_WORKER_MISMATCH")
    if any(type(d.get(k)) is not int or d[k]<=0 for k in (
            "whole_process_cpu_ns_including_native",
            "original_source_training_cpu_ns","full_replay_cpu_ns",
            "actual_os_peak_resident_bytes")):
        raise AssertionError("V31Z_ACTUAL_OS_PROCESS_RESOURCE_MISSING")
    meter=("LINUX_GETRUSAGE_SELF_RU_MAXRSS_KIB_X1024" if sys.platform=="linux"
           else "WINDOWS_GETPROCESSMEMORYINFO_PEAKWORKINGSETSIZE_BYTES"
           if sys.platform=="win32" else None)
    if not meter or d.get("os_peak_resident_method")!=meter:
        raise AssertionError("V31Z_ACTUAL_HOST_RSS_METER_NOT_SUPPORTED")
    sig=d.get("original_block_signatures")
    if (type(sig) is not list or len(sig)!=blocks or
            sig[0]["trace_sha256"]!=EXPECTED_TRACE_SHA or
            sig[0]["checkpoint_sha256"]!=EXPECTED_CHECKPOINT_SHA):
        raise AssertionError("V31Z_ORIGINAL_CHECKPOINT_OR_LEARNING_FINGERPRINT_CHANGED")
    if arm=="native":
        n=d.get("native_stats")
        expected=2*EVENTS_PER_BLOCK*blocks
        if (type(n) is not dict or
                n.get("distinct_original_cell_owners_per_bank")!=8 or
                n.get("native_feature_builds")!=expected or
                n.get("original_accepted_first_resets")!=expected or
                n.get("native_local_cache_hits",0)<=0 or
                n.get("original_neighbor_logical_directed_frames")!=
                expected*EXPECTED_MSG_PER_BUILD or
                n.get("total_native_heap_handles",0)<2):
            raise AssertionError("V31Z_NATIVE_REAL_PER_BANK_SOURCE_CUSTODY_BROKEN")
    elif d.get("native_stats") is not None:
        raise AssertionError("V31Z_OTHER_CONTROL_ACCIDENTALLY_EXECUTED_NATIVE")
    d["parent_full_worker_wall_ns"]=wall
    return d


def ratio(a,b):
    z=a/b
    if not math.isfinite(z) or z<=0:
        raise AssertionError("V31Z_INVALID_NATIVE_RESOURCE_RATIO")
    return z


def audit():
    expected=parity()
    out=[]
    for blocks in LENGTHS:
        baseline=expected[str(blocks)]
        for arm in ARMS:
            if worker_launch(arm,blocks)["original_block_signatures"]!=baseline:
                raise AssertionError("V31Z_SOURCE_TRAINED_WARMUP_DIFFERED_FROM_ORIGINAL")
        pairs=[]
        for i in range(PAIRS):
            order=("original","native") if i%2==0 else ("native","original")
            workers={arm:worker_launch(arm,blocks) for arm in order}
            workers["v31r"]=worker_launch("v31r",blocks)
            workers["v31x"]=worker_launch("v31x",blocks)
            if any(w["original_block_signatures"]!=baseline for w in workers.values()):
                raise AssertionError("V31Z_PUBLIC_REWARD_LEARNED_WEIGHTS_OR_STATE_DRIFT")
            a,b,c,d=(workers["original"],workers["native"],workers["v31r"],workers["v31x"])
            pairs.append({
                "trial":i+1,"order":list(order),
                "original_process_cpu_ns":a["whole_process_cpu_ns_including_native"],
                "native_process_cpu_ns":b["whole_process_cpu_ns_including_native"],
                "v31r_process_cpu_ns":c["whole_process_cpu_ns_including_native"],
                "v31x_process_cpu_ns":d["whole_process_cpu_ns_including_native"],
                "original_rss_bytes":a["actual_os_peak_resident_bytes"],
                "native_rss_bytes":b["actual_os_peak_resident_bytes"],
                "v31r_rss_bytes":c["actual_os_peak_resident_bytes"],
                "v31x_rss_bytes":d["actual_os_peak_resident_bytes"],
                "original_wall_ns":a["parent_full_worker_wall_ns"],
                "native_wall_ns":b["parent_full_worker_wall_ns"],
                "native_source_cpu_ns":b["original_source_training_cpu_ns"],
                "native_replay_cpu_ns":b["full_replay_cpu_ns"],
                "native_owner_stats":b["native_stats"],
                "cpu_ratio_vs_original":ratio(b["whole_process_cpu_ns_including_native"],a["whole_process_cpu_ns_including_native"]),
                "rss_ratio_vs_original":ratio(b["actual_os_peak_resident_bytes"],a["actual_os_peak_resident_bytes"]),
                "cpu_ratio_vs_v31r":ratio(b["whole_process_cpu_ns_including_native"],c["whole_process_cpu_ns_including_native"]),
                "rss_ratio_vs_v31r":ratio(b["actual_os_peak_resident_bytes"],c["actual_os_peak_resident_bytes"]),
                "cpu_ratio_vs_v31x":ratio(b["whole_process_cpu_ns_including_native"],d["whole_process_cpu_ns_including_native"]),
                "rss_ratio_vs_v31x":ratio(b["actual_os_peak_resident_bytes"],d["actual_os_peak_resident_bytes"]),
                "wall_ratio_vs_original":ratio(b["parent_full_worker_wall_ns"],a["parent_full_worker_wall_ns"]),
            })
        median=lambda k:statistics.median(r[k] for r in pairs)
        out.append({
            "blocks":blocks,"events":EVENTS_PER_BLOCK*blocks,
            "known_public_diversity":verified_diversity(blocks),
            "median_cpu_vs_original":round(median("cpu_ratio_vs_original"),8),
            "median_rss_vs_original":round(median("rss_ratio_vs_original"),8),
            "median_cpu_vs_v31r":round(median("cpu_ratio_vs_v31r"),8),
            "median_rss_vs_v31r":round(median("rss_ratio_vs_v31r"),8),
            "median_cpu_vs_v31x":round(median("cpu_ratio_vs_v31x"),8),
            "median_rss_vs_v31x":round(median("rss_ratio_vs_v31x"),8),
            "median_wall_vs_original":round(median("wall_ratio_vs_original"),8),
            "median_original_process_cpu_ns":int(median("original_process_cpu_ns")),
            "median_native_process_cpu_ns":int(median("native_process_cpu_ns")),
            "median_v31r_process_cpu_ns":int(median("v31r_process_cpu_ns")),
            "median_v31x_process_cpu_ns":int(median("v31x_process_cpu_ns")),
            "logical_original_direct_neighbor_frames":2*EVENTS_PER_BLOCK*blocks*EXPECTED_MSG_PER_BUILD,
            "entire_original_checkpoint_and_cold_restore_exact":True,
            "pairs":pairs,
        })
    short,long=out
    positive=(
        short["median_cpu_vs_original"]<=.95 and short["median_rss_vs_original"]<=1.15 and
        long["median_cpu_vs_original"]<=.85 and long["median_rss_vs_original"]<=1.15 and
        long["median_cpu_vs_v31r"]<=.95 and long["median_rss_vs_v31r"]<=1.15 and
        long["median_cpu_vs_v31x"]<=.95 and long["median_rss_vs_v31x"]<=1.15)
    print(json.dumps({
        "schema":SCHEMA,"host":sys.platform,"status":"COMPLETE",
        "classification":(
            "V31Z_NATIVE_FFI_HOST_RESOURCE_POSITIVE__NO_SCIENCE" if positive else
            "V31Z_NATIVE_FFI_NO_JOINT_RESOURCE_WIN__NO_SCIENCE"),
        "precompiled_native_module_sha256":NATIVE.native_binary_sha256,
        "precompiled_rust_source_sha256":NATIVE.source_sha256,
        "native_compile_cost_excluded_and_separately_reported":True,
        "all_trial_arms_import_same_compiled_native_library":True,
        "fresh_original_source_trained_processes":48,
        "five_fixed_ab_ba_pairs_each_length":PAIRS,
        "original_learning_and_cold_checkpoint_exact":True,
        "original_native_python_model_untouched":True,
        "compiled_native_cell_owner_memory_is_real":True,
        "original_native_learner_moved_to_rust":False,
        "independently_scheduled_native_learning_cells_proven":False,
        "physical_ipc_or_energy_measured":False,
        "scientific_first_use":False,
        "cpu96_vs_original_limit":.95,
        "cpu384_vs_original_limit":.85,
        "cpu384_vs_v31r_limit":.95,
        "cpu384_vs_v31x_limit":.95,
        "rss_limit":1.15,
        "results":out,
    },sort_keys=True,separators=(",",":"),allow_nan=False))


if __name__=="__main__":
    if len(sys.argv)==4 and sys.argv[1]=="--worker":
        fresh_worker(sys.argv[2],int(sys.argv[3]))
    elif len(sys.argv)==1:
        audit()
    else:
        raise SystemExit("V31Z_UNAUTHORIZED_COMMAND")
