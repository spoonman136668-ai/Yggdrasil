"""V31X: original eight linked-neighbor cell owners, frozen four-arm experiment.

Only external Python evaluation. Original learner, native source, rewards,
Q1–Q3 first-use holdouts, main and any research authority remain unchanged.
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

import research.itd02_v31w_dual_buffer_owner_audit as w
from research.itd02_v23_unfamiliar_mapping_audit import train_source
from research.itd02_v31q_varied_public_resource_audit import (
    extended_replay, verified_diversity, EVENTS_PER_BLOCK,
)
from research.itd02_v31o_full_process_resource_audit import actual_os_peak_resident_bytes
from research.itd02_v31j_executed_edge_ledger_audit import (
    EXPECTED_TRACE_SHA, EXPECTED_CHECKPOINT_SHA,
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
SCHEMA = "yggdrasil.itd02.v31x.linked_neighbor_original_ring.v1"
ARMS = ("original", "linked", "v31r", "v31w")
LENGTHS = (4, 16)
PAIRS = 5
MAX_WORKER_SECONDS = 180
SOURCE_UPDATES = 16*36


class LinkedCell:
    """Own state/scratch/feature row; two immutable pointers only to ring peers."""
    __slots__ = ("identity", "state", "scratch", "row", "cue", "first",
                 "left", "right")

    def __init__(self, identity):
        self.identity = identity
        self.state = [0.0] * CHANNELS
        self.scratch = [0.0] * CHANNELS
        self.row = None
        self.cue = None
        self.first = None
        self.left = None
        self.right = None

    def clear(self):
        self.row = None
        self.cue = None
        self.first = None


def owned_cells():
    w.original_ring_contract()
    cells = [LinkedCell(i) for i in range(CELLS)]
    for i, cell in enumerate(cells):
        left, right = RING[i]
        cell.left = cells[left]
        cell.right = cells[right]
    verify_links(cells)
    return cells


def verify_links(cells):
    if (type(cells) is not list or len(cells) != CELLS or
            len({id(c) for c in cells}) != CELLS):
        raise AssertionError("V31X_EIGHT_DISTINCT_PRIVATE_CELL_OWNERS_REQUIRED")
    for i, cell in enumerate(cells):
        if (type(cell) is not LinkedCell or cell.identity != i or
                cell.left is not cells[RING[i][0]] or
                cell.right is not cells[RING[i][1]] or
                cell.left is cell or cell.right is cell or
                cell.left is cell.right or
                len(cell.state) != CHANNELS or
                len(cell.scratch) != CHANNELS or
                cell.state is cell.scratch):
            raise AssertionError("V31X_NONNEIGHBOR_OR_ALIASED_CELL_STATE")
    return True


def original_linked_rows(cells, cue, first):
    """Four rounds; actual scalar reads ONLY through each owner's two peer links."""
    if type(cue) is not str or cue not in PUBLIC_CUES:
        raise ValueError("V31X_UNKNOWN_ORIGINAL_PUBLIC_CUE")
    if type(first) is not str or first not in ACTIONS:
        raise ValueError("V31X_UNKNOWN_ORIGINAL_PUBLIC_FIRST_ACTION")
    cue_channel = PUBLIC_CUES.index(cue)
    action_channel = ACTIONS.index(first)
    cue_site = OBS_SITES[OBSERVATIONS.index(cue)]
    action_site = ACTION_SITES[action_channel]

    for cell in cells:
        v = cell.state
        for k in range(CHANNELS):
            v[k] = 0.0
        if cell.identity == cue_site:
            v[cue_channel] = 1.0
        if cell.identity == action_site:
            v[4 + action_channel] = 1.0

    start = time.process_time_ns()
    for hop in range(HOPS):
        # Read precisely two original ring neighbor OWNERS' PREVIOUS-hop states.
        # No global precomputed signal table or transitive neighbor shortcut.
        for cell in cells:
            prior = cell.state
            left = cell.left.state
            right = cell.right.state
            next_row = cell.scratch
            for k in range(CHANNELS):
                neighbor = left[k] if left[k] >= right[k] else right[k]
                incoming = INITIAL_GAIN * neighbor
                own = prior[k]
                top = own if own >= incoming else incoming
                next_row[k] = 2.0 if top >= 2.0 else top
        # Synchronous original ring boundary: switch ONLY each owner's buffers.
        for cell in cells:
            cell.state, cell.scratch = cell.scratch, cell.state
    hop_cpu_ns = time.process_time_ns() - start

    rows = []
    for cell in cells:
        x = cell.state
        if any(not math.isfinite(v) or not 0.0 <= v <= 2.0 for v in x):
            raise AssertionError("V31X_NONFINITE_OR_OUT_OF_BOUNDS_PRIVATE_SIGNAL")
        row = tuple([1.0] + list(x) + [
            x[c] * x[4+a] for c in range(4) for a in range(3)
        ])
        if len(row) != HEAD_FEATURES:
            raise AssertionError("V31X_ORIGINAL_FEATURE_DIMENSION_DRIFT")
        cell.row = row
        cell.cue, cell.first = cue, first
        rows.append(list(row))
    return rows, CELLS*2*HOPS, hop_cpu_ns


@contextmanager
def linked_adapter():
    native_features = v22.SharedContextRingDev._features
    native_first = v22.SharedContextRingDev.accept_first
    native_site = v22._site_features
    native_scalar = v22._mix_scalars
    owned = WeakKeyDictionary()
    stats = {
        "max_distinct_cell_owners_per_bank": 0,
        "original_source_feature_builds": 0,
        "validated_bank_first_resets": 0,
        "owner_local_feature_hits": 0,
        "logical_neighbor_directed_messages": 0,
        "inner_hop_diagnostic_process_cpu_ns": 0,
        "module_global_feature_table_created": False,
        "nonneighbor_or_transitive_owner_links": False,
        "separate_os_cell_threads_or_processes": False,
        "native_scalar_route_or_checkpoint_changed": False,
        "physical_message_bytes_measured": False,
    }
    def get_owners(bank):
        if bank not in owned:
            owned[bank] = owned_cells()
        cells = owned[bank]
        if len(cells) != CELLS:
            raise AssertionError("V31X_ORIGINAL_EIGHT_CELL_BANK_SCOPE_LOST")
        stats["max_distinct_cell_owners_per_bank"] = max(
            stats["max_distinct_cell_owners_per_bank"], len(cells))
        return cells

    def accepted_first(bank, *a, **kw):
        response = native_first(bank, *a, **kw)
        for cell in get_owners(bank):
            cell.clear()
        stats["validated_bank_first_resets"] += 1
        return response

    def features(bank):
        bank._check_frozen()
        if bank.cue is None or bank.first is None:
            raise ValueError("V31X_VALIDATED_FIRST_PUBLIC_ACTION_REQUIRED")
        cells = get_owners(bank)
        if all(c.row is not None and c.cue == bank.cue and
               c.first == bank.first for c in cells):
            stats["owner_local_feature_hits"] += 1
            return [list(c.row) for c in cells]
        rows, messages, hop_ns = original_linked_rows(
            cells, bank.cue, bank.first)
        stats["original_source_feature_builds"] += 1
        stats["logical_neighbor_directed_messages"] += messages
        stats["inner_hop_diagnostic_process_cpu_ns"] += hop_ns
        return rows

    v22.SharedContextRingDev._features = features
    v22.SharedContextRingDev.accept_first = accepted_first
    try:
        yield stats
    finally:
        v22.SharedContextRingDev._features = native_features
        v22.SharedContextRingDev.accept_first = native_first
        if v22._site_features is not native_site or v22._mix_scalars is not native_scalar:
            raise AssertionError("V31X_ORIGINAL_SITE_OR_NEIGHBOR_SCALAR_ROUTE_MUTATED")


def run(source, blocks, arm, *, cold=False):
    if blocks not in LENGTHS or arm not in ARMS:
        raise ValueError("V31X_INVALID_PREDECLARED_ARM_OR_LENGTH")
    if arm == "linked":
        with linked_adapter() as stats:
            signatures = extended_replay(source, blocks, False, cold=cold)
        count = 2 * EVENTS_PER_BLOCK * blocks
        if (stats["max_distinct_cell_owners_per_bank"] != 8 or
                stats["original_source_feature_builds"] != count or
                stats["validated_bank_first_resets"] != count or
                stats["owner_local_feature_hits"] <= 0 or
                stats["logical_neighbor_directed_messages"] != count * 8*2*HOPS or
                stats["module_global_feature_table_created"] is not False or
                stats["nonneighbor_or_transitive_owner_links"] is not False or
                stats["separate_os_cell_threads_or_processes"] is not False):
            raise AssertionError("V31X_LINKED_OWNER_OR_RING_MESSAGE_ACCOUNTING_DRIFT")
    else:
        mapped = "dual_buffer" if arm == "v31w" else arm
        signatures, _unused = w.run(source, blocks, mapped, cold=cold)
        stats = None
    return signatures, stats


def negative_and_parity():
    w.original_ring_contract()
    for cue in PUBLIC_CUES:
        for first in ACTIONS:
            cells = owned_cells()
            rows, messages, _ = original_linked_rows(cells, cue, first)
            if rows != v22._site_features(cue, first) or messages != 64:
                raise AssertionError("V31X_ALL_TWELVE_ORIGINAL_CUE_FIRST_FEATURES_DRIFT")
            if not verify_links(cells):
                raise AssertionError("V31X_ORIGINAL_SOURCE_RING_NOT_VERIFIED")
    for cue, first in (("UNKNOWN", ACTIONS[0]), (PUBLIC_CUES[0], "UNKNOWN")):
        try:
            original_linked_rows(owned_cells(), cue, first)
        except ValueError:
            continue
        raise AssertionError("V31X_UNAUTHORIZED_PUBLIC_CUE_OR_FIRST_ACCEPTED")
    broken = owned_cells()
    broken[3].left = broken[1]
    try:
        verify_links(broken)
    except AssertionError:
        pass
    else:
        raise AssertionError("V31X_NONNEIGHBOR_LINK_NEGATIVE_CONTROL_FAILED")
    broken = owned_cells()
    broken[0].scratch = broken[0].state
    try:
        verify_links(broken)
    except AssertionError:
        pass
    else:
        raise AssertionError("V31X_SHARED_SCRATCH_BUFFER_NEGATIVE_CONTROL_FAILED")
    # Inject invalid state in source-independent guard path, prove it is rejected.
    broken = owned_cells()
    broken[0].state[0] = float("nan")
    try:
        require_finite_private_state(broken)
    except ValueError:
        pass
    else:
        raise AssertionError("V31X_NONFINITE_PRIVATE_STATE_NEGATIVE_CONTROL_FAILED")
    source = train_source()["pretrained_shared"]
    expected = {}
    for blocks in LENGTHS:
        original, _ = run(source, blocks, "original")
        for arm in ARMS:
            ordinary, _ = run(source, blocks, arm)
            cold, _ = run(source, blocks, arm, cold=True)
            if original != ordinary or cold != original:
                raise AssertionError("V31X_ORIGINAL_COLD_RESTORE_OR_MODEL_PARITY_DRIFT")
        expected[str(blocks)] = original
    return expected


def require_finite_private_state(cells):
    for cell in cells:
        if (any(type(x) not in (float,int) or
                not math.isfinite(x) or not 0 <= x <= 2 for x in cell.state)
                or any(type(x) not in (float,int) or
                       not math.isfinite(x) or not 0 <= x <= 2 for x in cell.scratch)):
            raise ValueError("V31X_INVALID_PRIVATE_CELL_SOURCE_STATE")
    return True


def worker(arm, blocks):
    if arm not in ARMS or blocks not in LENGTHS:
        raise ValueError("V31X_BAD_WORKER_ARM")
    started = time.process_time_ns()
    source = train_source()["pretrained_shared"]
    trained = time.process_time_ns()
    signatures, stats = run(source, blocks, arm)
    replayed = time.process_time_ns()
    resident, meter = actual_os_peak_resident_bytes()
    total = time.process_time_ns()
    if not (0 < started < trained < replayed <= total and resident > 0):
        raise AssertionError("V31X_PROCESS_RESOURCE_MISSING")
    print(json.dumps({
        "schema": SCHEMA, "role":"fresh_worker", "host":sys.platform,
        "arm":arm,"blocks":blocks,"events":24*blocks,
        "original_source_pretrained_once":True,
        "source_train_updates":16*36,
        "whole_process_cpu_ns":total,
        "original_source_cpu_ns":trained-started,
        "learner_replay_cpu_ns":replayed-trained,
        "actual_os_peak_rss_bytes":resident,
        "os_rss_method":meter,
        "signatures":signatures,
        "diversity":verified_diversity(blocks),
        "linked_stats":stats if arm=="linked" else None,
        "native_learner_original_unchanged":True,
        "physical_transfer_bytes_measured":False,
        "scientific_first_use":False,
    },sort_keys=True,separators=(",",":"),allow_nan=False))


def launch(arm, blocks):
    env = dict(os.environ)
    env["PYTHONHASHSEED"]="0"
    env["PYTHONDONTWRITEBYTECODE"]="1"
    start = time.perf_counter_ns()
    p = subprocess.run(
        [sys.executable, "-B", str(Path(__file__).resolve()),
         "--worker", arm, str(blocks)], cwd=ROOT, env=env,
        capture_output=True, text=True, check=False, timeout=MAX_WORKER_SECONDS)
    wall = time.perf_counter_ns()-start
    if p.returncode or p.stderr.strip():
        raise AssertionError("V31X_FRESH_WORKER_FAILED_{}_{}_{}_{}".format(
            arm, blocks, p.returncode, p.stderr[-1500:]))
    try:
        v = json.loads(p.stdout)
    except (ValueError,TypeError) as e:
        raise AssertionError("V31X_FRESH_PROCESS_OUTPUT_BAD_JSON") from e
    if (type(v) is not dict or v.get("schema")!=SCHEMA or
            v.get("role")!="fresh_worker" or v.get("host")!=sys.platform or
            v.get("arm")!=arm or v.get("blocks")!=blocks or
            v.get("events")!=24*blocks or
            v.get("diversity")!=verified_diversity(blocks) or
            v.get("original_source_pretrained_once") is not True or
            v.get("source_train_updates")!=16*36 or
            v.get("native_learner_original_unchanged") is not True or
            v.get("physical_transfer_bytes_measured") is not False or
            v.get("scientific_first_use") is not False):
        raise AssertionError("V31X_WORKER_SOURCE_IDENTITY_OR_ORIGINAL_ROUTE_DRIFT")
    method = ("LINUX_GETRUSAGE_SELF_RU_MAXRSS_KIB_X1024" if sys.platform=="linux"
              else "WINDOWS_GETPROCESSMEMORYINFO_PEAKWORKINGSETSIZE_BYTES"
              if sys.platform=="win32" else None)
    if not method or v.get("os_rss_method")!=method:
        raise AssertionError("V31X_GENUINE_HOST_OS_RSS_METER_UNAVAILABLE")
    for k in ("whole_process_cpu_ns","original_source_cpu_ns",
              "learner_replay_cpu_ns","actual_os_peak_rss_bytes"):
        if type(v.get(k)) is not int or v[k]<=0:
            raise AssertionError("V31X_UNMETERED_"+k)
    sig=v.get("signatures")
    if (type(sig) is not list or len(sig)!=blocks or
            sig[0]["trace_sha256"]!=EXPECTED_TRACE_SHA or
            sig[0]["checkpoint_sha256"]!=EXPECTED_CHECKPOINT_SHA):
        raise AssertionError("V31X_FROZEN_FIRST_BLOCK_IDENTITY_CHANGED")
    if arm=="linked":
        e=v.get("linked_stats")
        count=2*24*blocks
        if (type(e) is not dict or
                e.get("max_distinct_cell_owners_per_bank")!=8 or
                e.get("original_source_feature_builds")!=count or
                e.get("validated_bank_first_resets")!=count or
                e.get("owner_local_feature_hits",0)<=0 or
                e.get("logical_neighbor_directed_messages")!=count*8*2*HOPS or
                e.get("module_global_feature_table_created") is not False):
            raise AssertionError("V31X_CROSS_PROCESS_CELL_OWNER_CUSTODY_MISSING")
    elif v.get("linked_stats") is not None:
        raise AssertionError("V31X_BASELINE_HAS_CANDIDATE_OWNERS")
    v["parent_full_subprocess_wall_ns"]=wall
    return v


def ratio(a,b):
    x=a/b
    if not math.isfinite(x) or x<=0:
        raise AssertionError("V31X_UNSUPPORTED_RATIO")
    return x


def audit():
    reference=negative_and_parity()
    results=[]
    for blocks in LENGTHS:
        signatures=reference[str(blocks)]
        for arm in ARMS:
            if launch(arm,blocks)["signatures"]!=signatures:
                raise AssertionError("V31X_WARMUP_ORIGINAL_LEARNING_OR_CHECKPOINT_DRIFT")
        comparisons=[]
        for i in range(PAIRS):
            order=("original","linked") if i%2==0 else ("linked","original")
            runs={arm:launch(arm,blocks) for arm in order}
            runs["v31r"]=launch("v31r",blocks)
            runs["v31w"]=launch("v31w",blocks)
            if any(x["signatures"]!=signatures for x in runs.values()):
                raise AssertionError("V31X_ALL_ARMS_PUBLIC_REWARD_OR_STATE_DIFFER")
            a,b,c,d=(runs["original"],runs["linked"],runs["v31r"],runs["v31w"])
            comparisons.append({
                "trial":i+1,"order":list(order),
                "original_cpu_ns":a["whole_process_cpu_ns"],
                "linked_cpu_ns":b["whole_process_cpu_ns"],
                "v31r_cpu_ns":c["whole_process_cpu_ns"],
                "v31w_cpu_ns":d["whole_process_cpu_ns"],
                "original_os_peak_rss_bytes":a["actual_os_peak_rss_bytes"],
                "linked_os_peak_rss_bytes":b["actual_os_peak_rss_bytes"],
                "v31r_os_peak_rss_bytes":c["actual_os_peak_rss_bytes"],
                "v31w_os_peak_rss_bytes":d["actual_os_peak_rss_bytes"],
                "original_wall_ns":a["parent_full_subprocess_wall_ns"],
                "linked_wall_ns":b["parent_full_subprocess_wall_ns"],
                "v31r_wall_ns":c["parent_full_subprocess_wall_ns"],
                "v31w_wall_ns":d["parent_full_subprocess_wall_ns"],
                "linked_inner_hop_cpu_diagnostic_ns":
                    b["linked_stats"]["inner_hop_diagnostic_process_cpu_ns"],
                "logical_original_neighbor_messages":
                    b["linked_stats"]["logical_neighbor_directed_messages"],
                "ratio_cpu_vs_original":ratio(b["whole_process_cpu_ns"],a["whole_process_cpu_ns"]),
                "ratio_rss_vs_original":ratio(b["actual_os_peak_rss_bytes"],a["actual_os_peak_rss_bytes"]),
                "ratio_cpu_vs_v31r":ratio(b["whole_process_cpu_ns"],c["whole_process_cpu_ns"]),
                "ratio_rss_vs_v31r":ratio(b["actual_os_peak_rss_bytes"],c["actual_os_peak_rss_bytes"]),
                "ratio_cpu_vs_v31w":ratio(b["whole_process_cpu_ns"],d["whole_process_cpu_ns"]),
                "ratio_rss_vs_v31w":ratio(b["actual_os_peak_rss_bytes"],d["actual_os_peak_rss_bytes"]),
                "ratio_wall_vs_original":ratio(b["parent_full_subprocess_wall_ns"],a["parent_full_subprocess_wall_ns"]),
            })
        med=lambda key:statistics.median(x[key] for x in comparisons)
        results.append({
            "blocks":blocks, "events":24*blocks,
            "verified_public_diversity":verified_diversity(blocks),
            "ratio_cpu_vs_original_median":round(med("ratio_cpu_vs_original"),8),
            "ratio_rss_vs_original_median":round(med("ratio_rss_vs_original"),8),
            "ratio_cpu_vs_v31r_median":round(med("ratio_cpu_vs_v31r"),8),
            "ratio_rss_vs_v31r_median":round(med("ratio_rss_vs_v31r"),8),
            "ratio_cpu_vs_v31w_median":round(med("ratio_cpu_vs_v31w"),8),
            "ratio_rss_vs_v31w_median":round(med("ratio_rss_vs_v31w"),8),
            "ratio_wall_vs_original_median":round(med("ratio_wall_vs_original"),8),
            "original_cpu_median_ns":int(med("original_cpu_ns")),
            "linked_cpu_median_ns":int(med("linked_cpu_ns")),
            "v31r_cpu_median_ns":int(med("v31r_cpu_ns")),
            "v31w_cpu_median_ns":int(med("v31w_cpu_ns")),
            "logical_neighbor_messages":2*24*blocks*8*2*HOPS,
            "paired_trials":comparisons,
            "original_and_cold_checkpoints_exact":True,
        })
    short,long=results
    qualified=(
        short["ratio_cpu_vs_original_median"]<=.95 and
        short["ratio_rss_vs_original_median"]<=1.10 and
        long["ratio_cpu_vs_original_median"]<=.85 and
        long["ratio_rss_vs_original_median"]<=1.10 and
        long["ratio_cpu_vs_v31r_median"]<=1.00 and
        long["ratio_rss_vs_v31r_median"]<=1.10 and
        long["ratio_cpu_vs_v31w_median"]<=.95 and
        long["ratio_rss_vs_v31w_median"]<=1.10)
    print(json.dumps({
        "schema":SCHEMA,"host":sys.platform,"status":"COMPLETE",
        "classification":("V31X_LINKED_HOST_RESOURCE_POSITIVE__NO_SCIENCE"
                          if qualified else
                          "V31X_LINKED_NO_JOINT_RESOURCE_WIN__NO_SCIENCE"),
        "fresh_source_trained_processes":48,
        "frozen_pairs_each_length":PAIRS,
        "original_source_checkpoint_cold_restore_every_block_exact":True,
        "two_neighbor_links_per_private_cell":True,
        "independently_executing_native_cells_proven":False,
        "physical_ipc_bytes_or_energy_measured":False,
        "native_learner_changed":False,
        "scientific_first_use":False,
        "cpu96_vs_original_le":.95,
        "cpu384_vs_original_le":.85,
        "peak_os_resident_ratio_le":1.10,
        "cpu384_vs_v31r_le":1.00,
        "cpu384_vs_v31w_le":.95,
        "results":results,
    },sort_keys=True,separators=(",",":"),allow_nan=False))


if __name__=="__main__":
    if len(sys.argv)==4 and sys.argv[1]=="--worker":
        worker(sys.argv[2],int(sys.argv[3]))
    elif len(sys.argv)==1:
        audit()
    else:
        raise SystemExit("V31X_ILLEGAL_COMMAND")
