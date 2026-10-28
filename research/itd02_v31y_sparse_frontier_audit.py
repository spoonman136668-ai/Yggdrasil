"""V31Y sparse causal signal frontier: external 8-owner exact original ring audit.

All Python owner objects are cooperatively scheduled in a SINGLE process.
Sparse component counts are logical, not physical IPC bytes or energy.
No native model/weight/reward/source/codec edits or scientific first use.
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
from weakref import WeakKeyDictionary

import research.itd02_v31x_linked_neighbor_audit as v31x
from research.itd02_v23_unfamiliar_mapping_audit import train_source
from research.itd02_v31q_varied_public_resource_audit import (
    extended_replay, verified_diversity, EVENTS_PER_BLOCK,
)
from research.itd02_v31o_full_process_resource_audit import (
    actual_os_peak_resident_bytes,
)
from research.itd02_v31j_executed_edge_ledger_audit import (
    EXPECTED_CHECKPOINT_SHA, EXPECTED_TRACE_SHA,
)
from yggdrasil.itd02_v17_neighbor_carried_learner_dev import (
    ACTIONS, ACTION_SITES, CELLS, CHANNELS, HOPS, PUBLIC_CUES, RING,
)
from yggdrasil.itd02_local_ring_memory_dev import OBSERVATIONS, OBS_SITES
from yggdrasil.itd02_v18_intermediate_plasticity_dev import (
    INITIAL_GAIN, HEAD_FEATURES,
)
import yggdrasil.itd02_v22_shared_context_ring_dev as v22

ROOT = Path(__file__).resolve().parents[1]
SCHEMA = "yggdrasil.itd02.v31y.sparse_frontier_local_owner.v1"
ARMS = ("original", "sparse", "v31r", "v31x")
LENGTHS = (4, 16)
PAIRS = 5
MAX_WORKER_SECONDS = 180
SOURCE_UPDATES = 16 * 36


class SparseCell:
    """Private causal sparse state, not a global key/value or answer table."""
    __slots__ = ("identity", "state", "next_state", "row", "cue",
                 "first", "left", "right")

    def __init__(self, identity):
        self.identity = identity
        self.state = {}
        self.next_state = {}
        self.row = None
        self.cue = None
        self.first = None
        self.left = None
        self.right = None

    def clear(self):
        self.state = {}
        self.next_state = {}
        self.row = None
        self.cue = None
        self.first = None


def sparse_owners():
    v31x.w.original_ring_contract()
    cells = [SparseCell(i) for i in range(CELLS)]
    for i, cell in enumerate(cells):
        left, right = RING[i]
        cell.left, cell.right = cells[left], cells[right]
    verify_owners(cells)
    return cells


def valid_sparse(state):
    if (type(state) is not dict or len(state) > CHANNELS or
            any(type(k) is not int or not 0 <= k < CHANNELS or
                type(v) is not float or not math.isfinite(v) or
                not 0.0 < v <= 2.0 for k, v in state.items())):
        raise ValueError("V31Y_INVALID_NONZERO_LOCAL_CHANNEL_OR_VALUE")
    return True


def verify_owners(cells):
    if (type(cells) is not list or len(cells) != CELLS or
            len({id(c) for c in cells}) != CELLS):
        raise AssertionError("V31Y_EIGHT_SEPARATE_CELL_OWNER_INSTANCES_REQUIRED")
    states = []
    for i, c in enumerate(cells):
        if (type(c) is not SparseCell or c.identity != i or
                c.left is not cells[RING[i][0]] or
                c.right is not cells[RING[i][1]] or
                c.left is c or c.right is c or c.left is c.right or
                c.state is c.next_state):
            raise AssertionError("V31Y_NONNEIGHBOR_OR_SHARED_OWNER_STATE")
        valid_sparse(c.state)
        valid_sparse(c.next_state)
        states.extend([id(c.state), id(c.next_state)])
    if len(set(states)) != CELLS * 2:
        raise AssertionError("V31Y_SHARED_OR_ALIASED_PRIVATE_SPARSE_STATE")
    return True


def sparse_features(cells, cue, first):
    if (type(cue) is not str or cue not in PUBLIC_CUES or
            type(first) is not str or first not in ACTIONS):
        raise ValueError("V31Y_ORIGINAL_PUBLIC_FIRST_OR_CUE_REQUIRED")
    verify_owners(cells)  # Fail before episode state change.
    cue_idx = PUBLIC_CUES.index(cue)
    first_idx = ACTIONS.index(first)
    cue_site = OBS_SITES[OBSERVATIONS.index(cue)]
    first_site = ACTION_SITES[first_idx]
    for cell in cells:
        cell.state.clear()
        cell.next_state.clear()
        if cell.identity == cue_site:
            cell.state[cue_idx] = 1.0
        if cell.identity == first_site:
            cell.state[4 + first_idx] = 1.0

    logical_frames = 0
    active_frame_count = 0
    active_components = 0
    hop_cpu_start = time.process_time_ns()
    for _hop in range(HOPS):
        # Synchronous original hop: read ONLY the previous-hop state
        # of the receiver's two adjacent original ring neighbors.
        for cell in cells:
            own = cell.state
            left = cell.left.state
            right = cell.right.state
            # Original max(own, gain * max(left,right)) preserves monotonicity
            # for positive gain; sequential sparse updates are algebraically
            # identical, keeping exact ORIGINAL floating multiplication.
            new = own.copy()
            for neighbor in (left, right):
                logical_frames += 1
                if neighbor:
                    active_frame_count += 1
                    active_components += len(neighbor)
                for channel, value in neighbor.items():
                    candidate = INITIAL_GAIN * value
                    if candidate > new.get(channel, 0.0):
                        bounded = 2.0 if candidate >= 2.0 else candidate
                        if not math.isfinite(bounded):
                            raise ValueError("V31Y_NONFINITE_LOCAL_NEIGHBOR_SIGNAL")
                        new[channel] = bounded
            cell.next_state = new
        # Commit every owner's local next map AFTER all owner neighbor reads.
        for cell in cells:
            cell.state, cell.next_state = cell.next_state, cell.state
    hop_cpu_ns = time.process_time_ns() - hop_cpu_start
    if logical_frames != CELLS * 2 * HOPS:
        raise AssertionError("V31Y_ORIGINAL_DIRECT_NEIGHBOR_HOP_COUNT_DRIFT")
    if active_components >= logical_frames * CHANNELS:
        raise AssertionError("V31Y_NO_SPARSE_SILENT_CHANNEL_ELISION")
    rows = []
    for cell in cells:
        valid_sparse(cell.state)
        signal = [cell.state.get(ch, 0.0) for ch in range(CHANNELS)]
        row = tuple([1.0] + signal + [
            signal[c] * signal[4 + a] for c in range(4) for a in range(3)
        ])
        if len(row) != HEAD_FEATURES:
            raise AssertionError("V31Y_ORIGINAL_FEATURE_EXPANSION_WIDTH_DRIFT")
        cell.row, cell.cue, cell.first = row, cue, first
        rows.append(list(row))
    return rows, {
        "logical_frames": logical_frames,
        "nonempty_frames": active_frame_count,
        "nonzero_channel_components": active_components,
        "original_full_seven_channel_slots": logical_frames * CHANNELS,
        "hop_process_cpu_ns": hop_cpu_ns,
    }


@contextmanager
def sparse_adapter():
    old_features = v22.SharedContextRingDev._features
    old_first = v22.SharedContextRingDev.accept_first
    original_site = v22._site_features
    original_mix = v22._mix_scalars
    owners = WeakKeyDictionary()
    counts = {
        "original_eight_distinct_private_owners_per_bank": 0,
        "feature_builds": 0,
        "accepted_first_invalidations": 0,
        "owner_local_row_hits": 0,
        "logical_directed_neighbor_frames": 0,
        "nonempty_neighbor_frames": 0,
        "nonzero_sparse_channel_components": 0,
        "original_fixed_channel_slots": 0,
        "original_sparse_hop_cpu_ns": 0,
        "global_feature_or_answer_table_created": False,
        "independent_native_processes_or_threads": False,
        "real_ipc_bytes_or_hardware_energy_measured": False,
    }

    def for_bank(bank):
        if bank not in owners:
            owners[bank] = sparse_owners()
        cells = owners[bank]
        if len(cells) != 8 or len({id(x) for x in cells}) != 8:
            raise AssertionError("V31Y_DIFFERENT_BANK_CELL_OWNERS_MERGED")
        counts["original_eight_distinct_private_owners_per_bank"] = 8
        return cells

    def first(bank, *a, **kw):
        result = old_first(bank, *a, **kw)
        for cell in for_bank(bank):
            cell.clear()
        counts["accepted_first_invalidations"] += 1
        return result

    def features(bank):
        bank._check_frozen()
        if bank.cue is None or bank.first is None:
            raise ValueError("V31Y_ORIGINAL_FIRST_PUBLIC_ACTION_UNACCEPTED")
        cells = for_bank(bank)
        if all(c.row is not None and c.cue == bank.cue and
               c.first == bank.first for c in cells):
            counts["owner_local_row_hits"] += 1
            return [list(c.row) for c in cells]
        rows, evidence = sparse_features(cells, bank.cue, bank.first)
        counts["feature_builds"] += 1
        counts["logical_directed_neighbor_frames"] += evidence["logical_frames"]
        counts["nonempty_neighbor_frames"] += evidence["nonempty_frames"]
        counts["nonzero_sparse_channel_components"] += evidence[
            "nonzero_channel_components"]
        counts["original_fixed_channel_slots"] += evidence[
            "original_full_seven_channel_slots"]
        counts["original_sparse_hop_cpu_ns"] += evidence["hop_process_cpu_ns"]
        return rows

    v22.SharedContextRingDev._features = features
    v22.SharedContextRingDev.accept_first = first
    try:
        yield counts
    finally:
        v22.SharedContextRingDev._features = old_features
        v22.SharedContextRingDev.accept_first = old_first
        if (v22._site_features is not original_site or
                v22._mix_scalars is not original_mix):
            raise AssertionError("V31Y_NATIVE_SOURCE_SCALAR_ROUTE_MUTATED")


def run(source, blocks, arm, *, cold=False):
    if blocks not in LENGTHS or arm not in ARMS:
        raise ValueError("V31Y_NONPREREGISTERED_ARM_OR_LENGTH")
    if arm == "sparse":
        with sparse_adapter() as counts:
            sig = extended_replay(source, blocks, False, cold=cold)
        n = 2 * EVENTS_PER_BLOCK * blocks
        if (counts["original_eight_distinct_private_owners_per_bank"] != 8 or
                counts["feature_builds"] != n or
                counts["accepted_first_invalidations"] != n or
                counts["owner_local_row_hits"] <= 0 or
                counts["logical_directed_neighbor_frames"] != n*8*2*HOPS or
                counts["original_fixed_channel_slots"] != n*8*2*HOPS*CHANNELS or
                not 0 < counts["nonzero_sparse_channel_components"] <
                counts["original_fixed_channel_slots"] or
                counts["global_feature_or_answer_table_created"] is not False):
            raise AssertionError("V31Y_UNQUALIFIED_SPARSE_OWNER_OR_EDGE_CUSTODY")
    else:
        x_arm = "linked" if arm == "v31x" else arm
        sig, _ = v31x.run(source, blocks, x_arm, cold=cold)
        counts = None
    return sig, counts


def source_negative_and_parity():
    v31x.w.original_ring_contract()
    for cue in PUBLIC_CUES:
        for first in ACTIONS:
            cells = sparse_owners()
            sparse, e = sparse_features(cells, cue, first)
            if (sparse != v22._site_features(cue, first) or
                    e["logical_frames"] != 8*2*HOPS or
                    e["nonzero_channel_components"] >= 8*2*HOPS*CHANNELS):
                raise AssertionError("V31Y_TWELVE_PUBLIC_EXACT_NATIVE_SOURCE_ROWS_FAILED")
    for cue, first in (("WRONG", ACTIONS[0]), (PUBLIC_CUES[0], "WRONG")):
        try:
            sparse_features(sparse_owners(), cue, first)
        except ValueError:
            pass
        else:
            raise AssertionError("V31Y_UNAUTHORIZED_FIRST_OR_CUE_ACCEPTED")
    altered = sparse_owners()
    altered[2].left = altered[0]
    try:
        verify_owners(altered)
    except AssertionError:
        pass
    else:
        raise AssertionError("V31Y_NONNEIGHBOR_LINK_NEGATIVE_CONTROL_FAILED")
    altered = sparse_owners()
    altered[0].next_state = altered[0].state
    try:
        verify_owners(altered)
    except AssertionError:
        pass
    else:
        raise AssertionError("V31Y_SHARED_PRIVATE_SPARSE_MAP_NEGATIVE_CONTROL_FAILED")
    altered = sparse_owners()
    altered[0].state[1] = float("nan")
    try:
        verify_owners(altered)
    except ValueError:
        pass
    else:
        raise AssertionError("V31Y_NONFINITE_CHANNEL_NEGATIVE_CONTROL_FAILED")
    altered = sparse_owners()
    altered[0].state[CHANNELS] = 0.5
    try:
        verify_owners(altered)
    except ValueError:
        pass
    else:
        raise AssertionError("V31Y_ILLEGAL_CHANNEL_NEGATIVE_CONTROL_FAILED")
    source = train_source()["pretrained_shared"]
    expected = {}
    for blocks in LENGTHS:
        original, _ = run(source, blocks, "original")
        for arm in ARMS:
            ordinary, _ = run(source, blocks, arm)
            cold, _ = run(source, blocks, arm, cold=True)
            if original != ordinary or cold != original:
                raise AssertionError("V31Y_CONTINUOUS_COLD_ORIGINAL_STATE_DRIFT")
        expected[str(blocks)] = original
    return expected


def fresh_worker(arm, blocks):
    before = time.process_time_ns()
    source = train_source()["pretrained_shared"]
    after_train = time.process_time_ns()
    signatures, counts = run(source, blocks, arm)
    after_replay = time.process_time_ns()
    resident, method = actual_os_peak_resident_bytes()
    total_cpu = time.process_time_ns()
    if not (0 < before < after_train < after_replay <= total_cpu and resident > 0):
        raise AssertionError("V31Y_UNAVAILABLE_FULL_PROCESS_CPU_OR_OS_RSS")
    print(json.dumps({
        "schema": SCHEMA, "role": "fresh_worker", "host": sys.platform,
        "arm": arm, "blocks": blocks, "events": blocks * EVENTS_PER_BLOCK,
        "source_training_once_this_process": True, "source_updates": SOURCE_UPDATES,
        "full_process_cpu_ns": total_cpu,
        "source_training_cpu_ns": after_train - before,
        "original_replay_cpu_ns": after_replay - after_train,
        "actual_os_peak_resident_bytes": resident,
        "os_peak_resident_meter": method,
        "signatures": signatures, "known_public_diversity": verified_diversity(blocks),
        "sparse_owner_evidence": counts,
        "native_model_unchanged": True,
        "scientific_first_use": False,
        "independently_scheduled_native_cells_claimed": False,
        "physical_peer_bytes_measured": False,
    }, sort_keys=True, separators=(",", ":"), allow_nan=False))


def fresh(arm, blocks):
    if arm not in ARMS or blocks not in LENGTHS:
        raise ValueError("V31Y_INVALID_FRESH_WORKER")
    env = dict(os.environ)
    env["PYTHONHASHSEED"] = "0"
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    start = time.perf_counter_ns()
    proc = subprocess.run(
        [sys.executable, "-B", str(Path(__file__).resolve()),
         "--worker", arm, str(blocks)], cwd=ROOT, env=env,
        capture_output=True, text=True, check=False, timeout=MAX_WORKER_SECONDS)
    wall = time.perf_counter_ns() - start
    if proc.returncode or proc.stderr.strip():
        raise AssertionError("V31Y_FRESH_WORKER_FAILURE_{}_{}_{}_{}".format(
            arm, blocks, proc.returncode, proc.stderr[-1400:]))
    try:
        d = json.loads(proc.stdout)
    except (TypeError, ValueError) as err:
        raise AssertionError("V31Y_MALFORMED_SOURCE_PROCESS_RESULT") from err
    if (type(d) is not dict or d.get("schema") != SCHEMA or
            d.get("role") != "fresh_worker" or d.get("host") != sys.platform or
            d.get("arm") != arm or d.get("blocks") != blocks or
            d.get("events") != EVENTS_PER_BLOCK * blocks or
            d.get("source_training_once_this_process") is not True or
            d.get("source_updates") != SOURCE_UPDATES or
            d.get("known_public_diversity") != verified_diversity(blocks) or
            d.get("native_model_unchanged") is not True or
            d.get("scientific_first_use") is not False or
            d.get("independently_scheduled_native_cells_claimed") is not False or
            d.get("physical_peer_bytes_measured") is not False):
        raise AssertionError("V31Y_UNAUTHORIZED_WORKER_OR_SOURCE_DRIFT")
    required = ("full_process_cpu_ns", "source_training_cpu_ns",
                "original_replay_cpu_ns", "actual_os_peak_resident_bytes")
    if any(type(d.get(k)) is not int or d[k] <= 0 for k in required):
        raise AssertionError("V31Y_REAL_OS_CPU_OR_PEAK_RSS_MISSING")
    method = ("LINUX_GETRUSAGE_SELF_RU_MAXRSS_KIB_X1024" if sys.platform == "linux"
              else "WINDOWS_GETPROCESSMEMORYINFO_PEAKWORKINGSETSIZE_BYTES"
              if sys.platform == "win32" else None)
    if not method or d.get("os_peak_resident_meter") != method:
        raise AssertionError("V31Y_UNQUALIFIED_PEAK_OS_RESIDENT")
    sig = d.get("signatures")
    if (type(sig) is not list or len(sig) != blocks or
            sig[0]["trace_sha256"] != EXPECTED_TRACE_SHA or
            sig[0]["checkpoint_sha256"] != EXPECTED_CHECKPOINT_SHA):
        raise AssertionError("V31Y_ORIGINAL_V31I_FIRST_BLOCK_DIGEST_CHANGED")
    if arm == "sparse":
        e = d.get("sparse_owner_evidence")
        builds = 2 * EVENTS_PER_BLOCK * blocks
        if (type(e) is not dict or
                e.get("original_eight_distinct_private_owners_per_bank") != 8 or
                e.get("feature_builds") != builds or
                e.get("accepted_first_invalidations") != builds or
                e.get("owner_local_row_hits", 0) <= 0 or
                e.get("logical_directed_neighbor_frames") != builds*8*2*HOPS or
                e.get("original_fixed_channel_slots") != builds*8*2*HOPS*CHANNELS or
                not 0 < e.get("nonzero_sparse_channel_components", 0) <
                builds*8*2*HOPS*CHANNELS or
                e.get("global_feature_or_answer_table_created") is not False):
            raise AssertionError("V31Y_MISSING_SPARSE_PRIVATE_CAUSAL_PROVENANCE")
    elif d.get("sparse_owner_evidence") is not None:
        raise AssertionError("V31Y_ORIGINAL_CONTROL_CONTAMINATED_BY_SPARSE_STATE")
    d["parent_full_subprocess_wall_ns"] = wall
    return d


def divide(a, b):
    out = a / b
    if not math.isfinite(out) or out <= 0:
        raise AssertionError("V31Y_INVALID_OBSERVED_RESOURCE_RATIO")
    return out


def audit():
    expected = source_negative_and_parity()
    results = []
    for blocks in LENGTHS:
        original_signatures = expected[str(blocks)]
        for arm in ARMS:
            if fresh(arm, blocks)["signatures"] != original_signatures:
                raise AssertionError("V31Y_WARMUP_ORIGINAL_SOURCE_PARITY_FAILED")
        pairs = []
        for i in range(PAIRS):
            order = ("original", "sparse") if i % 2 == 0 else ("sparse", "original")
            runs = {arm: fresh(arm, blocks) for arm in order}
            runs["v31r"] = fresh("v31r", blocks)
            runs["v31x"] = fresh("v31x", blocks)
            if any(r["signatures"] != original_signatures for r in runs.values()):
                raise AssertionError("V31Y_ORIGINAL_REWARD_STATE_BLOCK_DIGEST_DRIFT")
            a,b,c,d = (runs["original"], runs["sparse"], runs["v31r"],runs["v31x"])
            pairs.append({
                "pair": i+1, "order": list(order),
                "original_cpu_ns": a["full_process_cpu_ns"],
                "sparse_cpu_ns": b["full_process_cpu_ns"],
                "v31r_cpu_ns": c["full_process_cpu_ns"],
                "v31x_cpu_ns": d["full_process_cpu_ns"],
                "original_rss_bytes": a["actual_os_peak_resident_bytes"],
                "sparse_rss_bytes": b["actual_os_peak_resident_bytes"],
                "v31r_rss_bytes": c["actual_os_peak_resident_bytes"],
                "v31x_rss_bytes": d["actual_os_peak_resident_bytes"],
                "original_wall_ns": a["parent_full_subprocess_wall_ns"],
                "sparse_wall_ns": b["parent_full_subprocess_wall_ns"],
                "sparse_nonzero_components": b["sparse_owner_evidence"][
                    "nonzero_sparse_channel_components"],
                "sparse_fixed_seven_channel_slots": b["sparse_owner_evidence"][
                    "original_fixed_channel_slots"],
                "sparse_active_frame_count": b["sparse_owner_evidence"][
                    "nonempty_neighbor_frames"],
                "logical_original_directed_frames": b["sparse_owner_evidence"][
                    "logical_directed_neighbor_frames"],
                "ratio_cpu_vs_original": divide(b["full_process_cpu_ns"], a["full_process_cpu_ns"]),
                "ratio_rss_vs_original": divide(b["actual_os_peak_resident_bytes"],
                                                a["actual_os_peak_resident_bytes"]),
                "ratio_cpu_vs_v31r": divide(b["full_process_cpu_ns"], c["full_process_cpu_ns"]),
                "ratio_rss_vs_v31r": divide(b["actual_os_peak_resident_bytes"],
                                            c["actual_os_peak_resident_bytes"]),
                "ratio_cpu_vs_v31x": divide(b["full_process_cpu_ns"], d["full_process_cpu_ns"]),
                "ratio_rss_vs_v31x": divide(b["actual_os_peak_resident_bytes"],
                                            d["actual_os_peak_resident_bytes"]),
                "ratio_wall_vs_original": divide(b["parent_full_subprocess_wall_ns"],
                                                  a["parent_full_subprocess_wall_ns"]),
            })
        med = lambda k:statistics.median(x[k] for x in pairs)
        results.append({
            "blocks": blocks, "events": blocks * EVENTS_PER_BLOCK,
            "known_public_diversity": verified_diversity(blocks),
            "median_cpu_vs_original": round(med("ratio_cpu_vs_original"),8),
            "median_rss_vs_original": round(med("ratio_rss_vs_original"),8),
            "median_cpu_vs_v31r": round(med("ratio_cpu_vs_v31r"),8),
            "median_rss_vs_v31r": round(med("ratio_rss_vs_v31r"),8),
            "median_cpu_vs_v31x": round(med("ratio_cpu_vs_v31x"),8),
            "median_rss_vs_v31x": round(med("ratio_rss_vs_v31x"),8),
            "median_wall_vs_original": round(med("ratio_wall_vs_original"),8),
            "median_original_cpu_ns": int(med("original_cpu_ns")),
            "median_sparse_cpu_ns": int(med("sparse_cpu_ns")),
            "median_v31r_cpu_ns": int(med("v31r_cpu_ns")),
            "median_v31x_cpu_ns": int(med("v31x_cpu_ns")),
            "logical_neighbor_frames": 2*blocks*EVENTS_PER_BLOCK*8*2*HOPS,
            "original_fixed_channel_slots": 2*blocks*EVENTS_PER_BLOCK*8*2*HOPS*CHANNELS,
            "median_sparse_nonzero_channel_components": int(med("sparse_nonzero_components")),
            "median_active_frame_count": int(med("sparse_active_frame_count")),
            "original_per_block_and_cold_restore_exact": True,
            "paired_trials": pairs,
        })
    short, long = results
    positive = (
        short["median_cpu_vs_original"] <= .95 and
        short["median_rss_vs_original"] <= 1.10 and
        long["median_cpu_vs_original"] <= .85 and
        long["median_rss_vs_original"] <= 1.10 and
        long["median_cpu_vs_v31r"] <= 1.00 and
        long["median_rss_vs_v31r"] <= 1.10 and
        long["median_cpu_vs_v31x"] <= .95 and
        long["median_rss_vs_v31x"] <= 1.10)
    print(json.dumps({
        "schema": SCHEMA, "host": sys.platform, "status": "COMPLETE",
        "classification": ("V31Y_SPARSE_FRONTIER_HOST_RESOURCE_POSITIVE__NO_SCIENCE"
                           if positive else
                           "V31Y_SPARSE_FRONTIER_NO_JOINT_RESOURCE_WIN__NO_SCIENCE"),
        "fresh_source_trained_processes": 48,
        "fixed_paired_trials_each_length": PAIRS,
        "all_source_learning_and_cold_model_exact": True,
        "private_sparsity_is_causal_not_centralized_answer_table": True,
        "eight_independently_scheduled_native_cells_proven": False,
        "actual_os_ipc_or_physical_energy_measured": False,
        "scientific_first_use": False,
        "cpu96_vs_original_limit":.95, "cpu384_vs_original_limit":.85,
        "rss_limit":1.10,"cpu384_vs_v31r_limit":1.00,
        "cpu384_vs_v31x_limit":.95,
        "results": results,
    },sort_keys=True,separators=(",",":"),allow_nan=False))


if __name__ == "__main__":
    if len(sys.argv) == 4 and sys.argv[1] == "--worker":
        fresh_worker(sys.argv[2], int(sys.argv[3]))
    elif len(sys.argv) == 1:
        audit()
    else:
        raise SystemExit("V31Y_UNAUTHORIZED_ENTRYPOINT")
