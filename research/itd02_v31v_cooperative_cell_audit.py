"""V31V cooperative eight original cell owners, external engineering only.

No original/native learner edits. Logical direct-neighbor Python frames are
not independently executing cells, physical messages, or real transport bytes.
"""
from __future__ import annotations

from contextlib import contextmanager, nullcontext
import json
import math
import os
from pathlib import Path
import statistics
import subprocess
import sys
import time
from weakref import WeakKeyDictionary

from research.itd02_v23_unfamiliar_mapping_audit import train_source
from research.itd02_v31q_varied_public_resource_audit import (
    extended_replay, verified_diversity, public_events, EVENTS_PER_BLOCK,
)
from research.itd02_v31r_bank_cell_locality_audit import bank_cell_local_adapter
from research.itd02_v31o_full_process_resource_audit import actual_os_peak_resident_bytes
from research.itd02_v31s_eight_process_ring_audit import (
    expected_local_pulse, wire, unwire,
)
from research.itd02_v31j_executed_edge_ledger_audit import (
    EXPECTED_TRACE_SHA, EXPECTED_CHECKPOINT_SHA,
)
from yggdrasil.itd02_v17_neighbor_carried_learner_dev import (
    ACTIONS, CELLS, CHANNELS, HOPS, PUBLIC_CUES, RING,
)
from yggdrasil.itd02_v18_intermediate_plasticity_dev import (
    INITIAL_GAIN, HEAD_FEATURES,
)
import yggdrasil.itd02_v22_shared_context_ring_dev as v22

ROOT = Path(__file__).resolve().parents[1]
SCHEMA = "yggdrasil.itd02.v31v.cooperative_cell_local.v1"
LENGTHS = (4, 16)
ARMS = ("original", "cooperative", "v31r")
PAIRS = 5
MAX_WORKER_SECONDS = 180
EXPECTED_SOURCE_UPDATES = 16 * 36


def validate_packet(frame, source, epoch, hop):
    if type(frame) is not tuple or len(frame) != 4:
        raise ValueError("V31V_NOT_AN_IMMUTABLE_NEIGHBOR_FRAME")
    s,e,h,row = frame
    if (type(s) is not int or s != source or
            type(e) is not int or e != epoch or
            type(h) is not int or h != hop or
            type(row) is not tuple or len(row) != CHANNELS or
            any(type(v) not in (int, float) or not math.isfinite(v) or
                not 0 <= v <= 2 for v in row)):
        raise ValueError("V31V_NONNEIGHBOR_STALE_OR_NONFINITE_FRAME")
    return row


def negative_packet_control():
    good = (2, 17, 3, (0.0,) * CHANNELS)
    if validate_packet(good, 2, 17, 3) != (0.0,) * CHANNELS:
        raise AssertionError("V31V_VALID_NEIGHBOR_REJECTED")
    bad = [
        (good, 3, 17, 3),
        (good, 2, 18, 3),
        (good, 2, 17, 2),
        ([2,17,3,[0.0]*CHANNELS], 2,17,3),
        ((2,17,3,(float("nan"),)*CHANNELS),2,17,3),
        ((2,17,3,(4.0,)*CHANNELS),2,17,3),
    ]
    for frame, s, e, h in bad:
        try:
            validate_packet(frame, s, e, h)
        except ValueError:
            continue
        raise AssertionError("V31V_UNTRUSTED_OR_REMOTE_PACKET_ACCEPTED")


class OwnerCell:
    __slots__ = ("id", "pulse", "state", "row", "cached_cue", "cached_first")

    def __init__(self, cell):
        self.id = cell
        self.pulse = None
        self.state = None
        self.row = None
        self.cached_cue = None
        self.cached_first = None

    def clear(self):
        self.pulse = None
        self.state = None
        self.row = None
        self.cached_cue = None
        self.cached_first = None

    def begin(self, cue, first):
        self.pulse = expected_local_pulse(self.id, cue, first)
        self.state = list(self.pulse)

    def send(self, epoch, hop):
        return (self.id, epoch, hop, tuple(self.state))

    def receive(self, left, right, epoch, hop):
        a = validate_packet(left, RING[self.id][0], epoch, hop)
        b = validate_packet(right, RING[self.id][1], epoch, hop)
        self.state = [
            min(2.0, max(self.state[ch], INITIAL_GAIN * max(a[ch], b[ch])))
            for ch in range(CHANNELS)
        ]

    def commit(self, cue, first):
        local = self.state
        feature = [1.0] + list(local) + [
            local[c] * local[4 + a] for c in range(4) for a in range(3)
        ]
        if len(feature) != HEAD_FEATURES:
            raise AssertionError("V31V_ORIGINAL_CELL_FEATURE_DIMENSION_DRIFT")
        self.row = tuple(feature)
        self.cached_cue = cue
        self.cached_first = first


def build_owner_rows(cells, cue, first, epoch):
    if (type(cells) is not list or len(cells) != 8 or
            len({id(cell) for cell in cells}) != 8 or
            any(cell.id != i for i, cell in enumerate(cells)) or
            type(epoch) is not int or epoch <= 0):
        raise AssertionError("V31V_CELL_OWNER_SCOPE_OR_EPOCH_DRIFT")
    for cell in cells:
        cell.begin(cue, first)
    directed = 0
    start = time.process_time_ns()
    for hop in range(HOPS):
        # Cooperative scheduler reads only owner-emitted immutable neighbor frames.
        frames = [cell.send(epoch, hop) for cell in cells]
        for cell in cells:
            left, right = RING[cell.id]
            cell.receive(frames[left], frames[right], epoch, hop)
            directed += 2
    hop_cpu = time.process_time_ns() - start
    for cell in cells:
        cell.commit(cue, first)
    return [list(cell.row) for cell in cells], directed, hop_cpu


@contextmanager
def cooperative_cell_adapter():
    old_features = v22.SharedContextRingDev._features
    old_first = v22.SharedContextRingDev.accept_first
    original_site = v22._site_features
    original_mix = v22._mix_scalars
    owners = WeakKeyDictionary()
    stats = {
        "original_bank_cell_owner_count": 8,
        "original_feature_builds": 0,
        "cell_local_feature_hits": 0,
        "validated_bank_episode_resets": 0,
        "directed_neighbor_messages": 0,
        "max_distinct_cell_owners_per_bank": 0,
        "hop_cpu_ns": 0,
        "total_feature_cpu_ns": 0,
        "native_model_or_scalar_mix_modified": False,
        "independent_os_cell_threads_or_processes": False,
        "actual_physical_bytes_measured": False,
    }
    epoch = [0]

    def cells_for(bank):
        if bank not in owners:
            owners[bank] = [OwnerCell(i) for i in range(CELLS)]
        cells = owners[bank]
        if len(cells) != CELLS or len({id(c) for c in cells}) != CELLS:
            raise AssertionError("V31V_PER_BANK_EIGHT_INDEPENDENT_OWNER_INSTANCES_DRIFT")
        stats["max_distinct_cell_owners_per_bank"] = max(
            stats["max_distinct_cell_owners_per_bank"], len(cells))
        return cells

    def first(bank, *args, **kwargs):
        result = old_first(bank, *args, **kwargs)
        for cell in cells_for(bank):
            cell.clear()
        stats["validated_bank_episode_resets"] += 1
        return result

    def features(bank):
        t = time.process_time_ns()
        bank._check_frozen()
        if bank.cue is None or bank.first is None:
            raise ValueError("V31V_ORIGINAL_PUBLIC_FIRST_REQUIRED")
        cells = cells_for(bank)
        if all(c.row is not None and c.cached_cue == bank.cue and
               c.cached_first == bank.first for c in cells):
            stats["cell_local_feature_hits"] += 1
            rows = [list(c.row) for c in cells]
        else:
            epoch[0] += 1
            rows, directed, hop_cpu = build_owner_rows(
                cells, bank.cue, bank.first, epoch[0])
            stats["original_feature_builds"] += 1
            stats["directed_neighbor_messages"] += directed
            stats["hop_cpu_ns"] += hop_cpu
        stats["total_feature_cpu_ns"] += time.process_time_ns() - t
        return rows

    v22.SharedContextRingDev._features = features
    v22.SharedContextRingDev.accept_first = first
    try:
        yield stats
    finally:
        v22.SharedContextRingDev.accept_first = old_first
        v22.SharedContextRingDev._features = old_features
        if v22._site_features is not original_site or v22._mix_scalars is not original_mix:
            raise AssertionError("V31V_ORIGINAL_SITE_OR_SCALAR_ROUTE_WAS_MUTATED")


def run(source, blocks, arm, *, cold=False):
    if arm not in ARMS or blocks not in LENGTHS:
        raise AssertionError("V31V_BAD_PREDECLARED_ARM_OR_LENGTH")
    if arm == "cooperative":
        with cooperative_cell_adapter() as stats:
            sig = extended_replay(source, blocks, False, cold=cold)
        expected = 2 * blocks * EVENTS_PER_BLOCK
        if (stats["max_distinct_cell_owners_per_bank"] != 8 or
                stats["original_feature_builds"] != expected or
                stats["validated_bank_episode_resets"] != expected or
                stats["directed_neighbor_messages"] != expected*8*2*HOPS or
                stats["cell_local_feature_hits"] <= 0 or
                stats["native_model_or_scalar_mix_modified"] is not False):
            raise AssertionError("V31V_COOPERATIVE_SOURCE_FEATURE_OR_NEIGHBOR_SCOPE_DRIFT")
    elif arm == "v31r":
        with bank_cell_local_adapter() as stats:
            sig = extended_replay(source, blocks, False, cold=cold)
        expected = 2 * blocks * EVENTS_PER_BLOCK
        if (stats["max_slots_per_bank"] != 8 or
                stats["original_feature_builds"] != expected or
                stats["validated_bank_episode_resets"] != expected or
                stats["bank_local_feature_hits"] <= 0):
            raise AssertionError("V31V_FROZEN_V31R_COMPARATOR_SCOPE_DRIFT")
    else:
        sig = extended_replay(source, blocks, False, cold=cold)
        stats = None
    return sig, stats


def per_host_preflight():
    negative_packet_control()
    for cue in PUBLIC_CUES:
        for first in ACTIONS:
            cells = [OwnerCell(i) for i in range(8)]
            rows, cnt, _ = build_owner_rows(cells, cue, first, 1)
            if rows != v22._site_features(cue, first) or cnt != 8*2*HOPS:
                raise AssertionError("V31V_ALL_TWELVE_PUBLIC_ORIGINAL_FEATURE_ROWS_PARITY_FAILED")
    source = train_source()["pretrained_shared"]
    refs = {}
    for blocks in LENGTHS:
        a, _ = run(source, blocks, "original")
        for arm in ARMS:
            warm, _ = run(source, blocks, arm)
            cold, _ = run(source, blocks, arm, cold=True)
            if warm != a or cold != a:
                raise AssertionError("V31V_ORIGINAL_STATE_OR_COLD_RESTART_PARITY_DRIFT")
        refs[str(blocks)] = a
    return refs


def overhead_diagnostic():
    """128 fixed public input cases per operation; NOT a causal decomposition."""
    fixed = [(PUBLIC_CUES[(i*7)%4], ACTIONS[(i*5)%3]) for i in range(128)]
    t = time.process_time_ns()
    for cue,first in fixed:
        rows = v22._site_features(cue,first)
        if len(rows) != CELLS:
            raise AssertionError("V31V_SOURCE_DIAGNOSTIC_ROW_DRIFT")
    original_ns = time.process_time_ns() - t
    t = time.process_time_ns()
    for k,(cue,first) in enumerate(fixed):
        rows, count, _ = build_owner_rows([OwnerCell(i) for i in range(8)],
                                         cue,first,k+1)
        if len(rows) != CELLS or count != CELLS*2*HOPS:
            raise AssertionError("V31V_COOPERATIVE_DIAGNOSTIC_COUNT_DRIFT")
    coop_ns = time.process_time_ns() - t
    frame = {"episode":1,"hop":0,"source":2,"row":[0.0]*CHANNELS}
    t = time.process_time_ns()
    for _ in range(128):
        raw = wire(frame)
        if unwire(raw) != frame:
            raise AssertionError("V31V_JSON_ROUNDTRIP_DRIFT")
    json_ns = time.process_time_ns() - t
    if min(original_ns,coop_ns,json_ns) <= 0:
        raise AssertionError("V31V_INVALID_MECHANISM_CPU_DIAGNOSTIC")
    return {
        "repetitions_each":128,
        "original_site_features_process_cpu_ns":original_ns,
        "cooperative_owner_build_process_cpu_ns":coop_ns,
        "single_json_frame_roundtrip_128_process_cpu_ns":json_ns,
        "single_json_frame_serialized_length_bytes":len(wire(frame)),
        "seven_float_logical_payload_bytes":56,
        "interpretation":"DESCRIPTIVE_DIFFERENT_OPERATIONS_NOT_CAUSAL_COST_ADDITIVITY",
    }


def worker(arm, blocks):
    if arm not in ARMS or blocks not in LENGTHS:
        raise AssertionError("V31V_INVALID_WORKER")
    before = time.process_time_ns()
    source = train_source()["pretrained_shared"]
    trained = time.process_time_ns()
    signatures,stats = run(source,blocks,arm)
    replayed = time.process_time_ns()
    rss,method = actual_os_peak_resident_bytes()
    total = time.process_time_ns()
    if not (0 < before < trained < replayed <= total and rss > 0):
        raise AssertionError("V31V_GENUINE_PROCESS_CPU_RSS_UNAVAILABLE")
    print(json.dumps({
        "schema":SCHEMA,"role":"fresh_worker","host":sys.platform,
        "arm":arm,"blocks":blocks,"events":24*blocks,
        "source_original_pretraining_once":True,
        "source_training_updates":EXPECTED_SOURCE_UPDATES,
        "total_process_cpu_ns":total,
        "training_cpu_ns":trained-before,
        "replay_cpu_ns":replayed-trained,
        "os_peak_resident_bytes":rss,"os_peak_resident_method":method,
        "signatures":signatures,"public_diversity":verified_diversity(blocks),
        "owner_stats":stats if arm=="cooperative" else None,
        "native_source_modified":False,"scientific_first_use":False,
        "physical_transport_measured":False,
    },sort_keys=True,separators=(",",":"),allow_nan=False))


def launch(arm,blocks):
    env = dict(os.environ)
    env["PYTHONHASHSEED"]="0"
    env["PYTHONDONTWRITEBYTECODE"]="1"
    start = time.perf_counter_ns()
    result = subprocess.run(
        [sys.executable,"-B",str(Path(__file__).resolve()),
         "--worker",arm,str(blocks)],
        cwd=ROOT,env=env,capture_output=True,text=True,
        timeout=MAX_WORKER_SECONDS,check=False)
    wall = time.perf_counter_ns()-start
    if result.returncode or result.stderr.strip():
        raise AssertionError("V31V_FRESH_WORKER_FAIL_{}_{}_{}_{}".format(
            arm,blocks,result.returncode,result.stderr[-1700:]))
    try:
        d = json.loads(result.stdout)
    except (TypeError,ValueError) as exc:
        raise AssertionError("V31V_UNPARSABLE_FRESH_WORKER_REPORT") from exc
    if (type(d) is not dict or d.get("schema")!=SCHEMA or
            d.get("role")!="fresh_worker" or
            d.get("arm")!=arm or d.get("host")!=sys.platform or
            d.get("blocks")!=blocks or d.get("events")!=24*blocks or
            d.get("public_diversity")!=verified_diversity(blocks) or
            d.get("source_original_pretraining_once") is not True or
            d.get("source_training_updates")!=EXPECTED_SOURCE_UPDATES or
            d.get("native_source_modified") is not False or
            d.get("scientific_first_use") is not False or
            d.get("physical_transport_measured") is not False):
        raise AssertionError("V31V_FRESH_WORKER_SOURCE_IDENTITY_DRIFT")
    for k in ("total_process_cpu_ns","training_cpu_ns","replay_cpu_ns",
              "os_peak_resident_bytes"):
        if type(d.get(k)) is not int or d[k]<=0:
            raise AssertionError("V31V_MISSING_TRUE_RESOURCE_"+k)
    method=("LINUX_GETRUSAGE_SELF_RU_MAXRSS_KIB_X1024" if sys.platform=="linux"
            else "WINDOWS_GETPROCESSMEMORYINFO_PEAKWORKINGSETSIZE_BYTES"
            if sys.platform=="win32" else None)
    if not method or d.get("os_peak_resident_method")!=method:
        raise AssertionError("V31V_HOST_OS_RSS_METER_DRIFT")
    if (type(d.get("signatures")) is not list or
            len(d["signatures"])!=blocks or
            d["signatures"][0]["trace_sha256"]!=EXPECTED_TRACE_SHA or
            d["signatures"][0]["checkpoint_sha256"]!=EXPECTED_CHECKPOINT_SHA):
        raise AssertionError("V31V_ORIGINAL_CHECKPOINT_TRACE_NOT_PRESERVED")
    if arm=="cooperative":
        stats=d.get("owner_stats")
        if (type(stats) is not dict or
                stats.get("max_distinct_cell_owners_per_bank")!=8 or
                stats.get("original_feature_builds")!=2*24*blocks or
                stats.get("validated_bank_episode_resets")!=2*24*blocks or
                stats.get("directed_neighbor_messages")!=2*24*blocks*8*2*HOPS or
                stats.get("cell_local_feature_hits",0)<=0 or
                stats.get("independent_os_cell_threads_or_processes") is not False):
            raise AssertionError("V31V_OWNER_LOCAL_LOGICAL_EDGE_IDENTITY_DRIFT")
    elif d.get("owner_stats") is not None:
        raise AssertionError("V31V_CONTROL_POLLUTED_BY_OWNER_SCHEDULER")
    d["full_process_wall_ns"]=wall
    return d


def ratio(a,b):
    value=a/b
    if not math.isfinite(value) or value<=0:
        raise AssertionError("V31V_UNDEFINED_RESOURCE_RATIO")
    return value


def audit():
    reference=per_host_preflight()
    diagnostic=overhead_diagnostic()
    all_results=[]
    for blocks in LENGTHS:
        ref=reference[str(blocks)]
        for arm in ARMS:
            warm=launch(arm,blocks)
            if warm["signatures"]!=ref:
                raise AssertionError("V31V_WARMUP_EXACT_STATE_DRIFT")
        pairs=[]
        for i in range(PAIRS):
            order=("original","cooperative") if i%2==0 else (
                "cooperative","original")
            obs={arm:launch(arm,blocks) for arm in order}
            obs["v31r"]=launch("v31r",blocks)
            if any(x["signatures"]!=ref for x in obs.values()):
                raise AssertionError("V31V_ORIGINAL_BLOCK_TRACE_OR_CHECKPOINT_DRIFT")
            a,b,c=obs["original"],obs["cooperative"],obs["v31r"]
            pairs.append({
                "trial":i+1,"order":list(order),
                "original_cpu_ns":a["total_process_cpu_ns"],
                "cooperative_cpu_ns":b["total_process_cpu_ns"],
                "v31r_cpu_ns":c["total_process_cpu_ns"],
                "original_rss_bytes":a["os_peak_resident_bytes"],
                "cooperative_rss_bytes":b["os_peak_resident_bytes"],
                "v31r_rss_bytes":c["os_peak_resident_bytes"],
                "original_wall_ns":a["full_process_wall_ns"],
                "cooperative_wall_ns":b["full_process_wall_ns"],
                "v31r_wall_ns":c["full_process_wall_ns"],
                "cooperative_replay_cpu_ns":b["replay_cpu_ns"],
                "cooperative_feature_cpu_ns":b["owner_stats"]["total_feature_cpu_ns"],
                "cooperative_neighbor_hop_cpu_ns":b["owner_stats"]["hop_cpu_ns"],
                "cooperative_cache_hits":b["owner_stats"]["cell_local_feature_hits"],
                "logical_neighbor_messages":b["owner_stats"]["directed_neighbor_messages"],
                "cpu_ratio":ratio(b["total_process_cpu_ns"],a["total_process_cpu_ns"]),
                "rss_ratio":ratio(b["os_peak_resident_bytes"],a["os_peak_resident_bytes"]),
                "wall_ratio":ratio(b["full_process_wall_ns"],a["full_process_wall_ns"]),
                "vs_v31r_cpu_ratio":ratio(b["total_process_cpu_ns"],c["total_process_cpu_ns"]),
                "vs_v31r_rss_ratio":ratio(b["os_peak_resident_bytes"],c["os_peak_resident_bytes"]),
            })
        med=lambda key:statistics.median(x[key] for x in pairs)
        all_results.append({
            "blocks":blocks,"events":24*blocks,
            "public_diversity":verified_diversity(blocks),
            "cpu_ratio_median":round(med("cpu_ratio"),8),
            "rss_ratio_median":round(med("rss_ratio"),8),
            "wall_ratio_median":round(med("wall_ratio"),8),
            "vs_v31r_cpu_ratio_median":round(med("vs_v31r_cpu_ratio"),8),
            "vs_v31r_rss_ratio_median":round(med("vs_v31r_rss_ratio"),8),
            "original_cpu_median_ns":int(med("original_cpu_ns")),
            "cooperative_cpu_median_ns":int(med("cooperative_cpu_ns")),
            "v31r_cpu_median_ns":int(med("v31r_cpu_ns")),
            "cooperative_feature_cpu_median_ns":int(med("cooperative_feature_cpu_ns")),
            "cooperative_neighbor_hop_cpu_median_ns":int(med("cooperative_neighbor_hop_cpu_ns")),
            "logical_neighbor_messages":2*24*blocks*8*2*HOPS,
            "full_block_parity_and_cold_original_passed":True,
            "pairs":pairs,
        })
    short,long=all_results
    positive=(
        short["cpu_ratio_median"]<=.95 and short["rss_ratio_median"]<=1.10 and
        long["cpu_ratio_median"]<=.85 and long["rss_ratio_median"]<=1.10 and
        long["vs_v31r_cpu_ratio_median"]<=1.10 and
        long["vs_v31r_rss_ratio_median"]<=1.10)
    print(json.dumps({
        "schema":SCHEMA,"status":"COMPLETE","host":sys.platform,
        "classification":(
            "V31V_COOPERATIVE_HOST_RESOURCE_POSITIVE__NO_SCIENCE" if positive else
            "V31V_COOPERATIVE_NO_JOINT_RESOURCE_WIN__NO_SCIENCE"),
        "fresh_workers_launched":36,"fixed_ab_ba_pairs_per_length":PAIRS,
        "source_original_training_once_per_fresh_worker":True,
        "source_trace_checkpoint_and_cold_all_exact":True,
        "real_cell_processes_or_threads_claimed":False,
        "logical_neighbor_frames_not_physical_bytes":True,
        "original_native_source_modified":False,
        "scientific_first_use":False,
        "cpu96_gate_le":.95,"cpu384_gate_le":.85,
        "resident_gate_le":1.10,"cpu384_vs_v31r_gate_le":1.10,
        "resident384_vs_v31r_gate_le":1.10,
        "overhead_diagnostic":diagnostic,
        "results":all_results,
    },sort_keys=True,separators=(",",":"),allow_nan=False))


if __name__=="__main__":
    if len(sys.argv)==4 and sys.argv[1]=="--worker":
        worker(sys.argv[2],int(sys.argv[3]))
    elif len(sys.argv)==1:
        audit()
    else:
        raise SystemExit("V31V_INVALID_COMMAND")
