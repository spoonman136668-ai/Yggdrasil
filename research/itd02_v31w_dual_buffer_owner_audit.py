"""V31W: original eight ring-cell owners and per-owner dual scalar buffers.

External Python engineering only. Never modifies original shipped cell models,
training rules, checkpoint, accepted refs, or scientific holdouts.
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

from research.itd02_v23_unfamiliar_mapping_audit import train_source
from research.itd02_v31q_varied_public_resource_audit import (
    extended_replay, verified_diversity, EVENTS_PER_BLOCK,
)
from research.itd02_v31r_bank_cell_locality_audit import bank_cell_local_adapter
from research.itd02_v31o_full_process_resource_audit import actual_os_peak_resident_bytes
from research.itd02_v31j_executed_edge_ledger_audit import (
    EXPECTED_TRACE_SHA, EXPECTED_CHECKPOINT_SHA,
)
from yggdrasil.itd02_v17_neighbor_carried_learner_dev import (
    ACTIONS, ACTION_SITES, CELLS, CHANNELS, HOPS, PUBLIC_CUES, RING,
)
from yggdrasil.itd02_local_ring_memory_dev import (
    OBSERVATIONS, OBS_SITES,
)
from yggdrasil.itd02_v18_intermediate_plasticity_dev import (
    INITIAL_GAIN, HEAD_FEATURES,
)
import yggdrasil.itd02_v22_shared_context_ring_dev as v22

ROOT = Path(__file__).resolve().parents[1]
SCHEMA = "yggdrasil.itd02.v31w.dual_buffer_original_neighbor.v1"
ARMS = ("original", "dual_buffer", "v31r")
LENGTHS = (4,16)
TRIALS = 5
MAX_WORKER_SECONDS = 180
TRAINING_UPDATES = 16*36


class Cell:
    __slots__=("identity","state","scratch","row","cue","first")

    def __init__(self, identity):
        self.identity=identity
        self.state=[0.0]*CHANNELS
        self.scratch=[0.0]*CHANNELS
        self.row=None
        self.cue=None
        self.first=None

    def clear(self):
        self.row=None
        self.cue=None
        self.first=None

    def site_pulse(self, cue_site, cue_idx, first_site, action_idx):
        state=self.state
        for i in range(CHANNELS):
            state[i]=0.0
        if self.identity==cue_site:
            state[cue_idx]=1.0
        if self.identity==first_site:
            state[4+action_idx]=1.0

    def build_row(self, cue, first):
        v=self.state
        row=[1.0]+list(v)+[
            v[c]*v[4+a] for c in range(4) for a in range(3)
        ]
        if len(row)!=HEAD_FEATURES:
            raise AssertionError("V31W_ORIGINAL_LOCAL_FEATURE_WIDTH_CHANGED")
        self.row=tuple(row)
        self.cue=cue
        self.first=first


def original_ring_contract():
    if (CELLS!=8 or CHANNELS!=7 or HOPS!=4 or
        len(RING)!=8 or
        len(PUBLIC_CUES)!=4 or len(ACTIONS)!=3 or
        len(OBS_SITES)!=len(OBSERVATIONS) or
        len(ACTION_SITES)!=len(ACTIONS) or
        HEAD_FEATURES!=20 or INITIAL_GAIN!=0.92):
        raise AssertionError("V31W_ORIGINAL_NATIVE_SOURCE_CONSTANTS_CHANGED")
    for i,neighbors in enumerate(RING):
        if (type(neighbors) is not tuple or
            neighbors!=((i-1)%CELLS,(i+1)%CELLS) or
            neighbors[0]==neighbors[1] or i in neighbors):
            raise AssertionError("V31W_NOT_ORIGINAL_DIRECT_NEIGHBOR_RING")
    for cue in PUBLIC_CUES:
        if cue not in OBSERVATIONS:
            raise AssertionError("V31W_ORIGINAL_OBSERVATION_SITE_UNKNOWN")
    if ACTION_SITES != (0,2,5):
        raise AssertionError("V31W_ORIGINAL_ACTION_SITE_DRIFT")


def negative_source_controls():
    original_ring_contract()
    for cue in PUBLIC_CUES:
        for first in ACTIONS:
            rows, msgs, _ = original_build_rows(
                [Cell(i) for i in range(CELLS)],cue,first)
            if rows!=v22._site_features(cue,first) or msgs!=CELLS*2*HOPS:
                raise AssertionError("V31W_TWELVE_PUBLIC_CUE_FIRST_ORIGINAL_OUTPUT_DRIFT")
    # Explicit invalid original input, immutable topology and nonfinite
    # controls. Cells never accept neighbor IDs supplied by user messages.
    for cue,first in (
        ("INVENTED",ACTIONS[0]), (PUBLIC_CUES[0],"INVENTED"),
    ):
        try:
            original_build_rows([Cell(i) for i in range(CELLS)],cue,first)
        except ValueError:
            continue
        raise AssertionError("V31W_INVALID_PUBLIC_INPUT_ACCEPTED")
    cell=Cell(1)
    cell.state[0]=float("nan")
    if not any(not math.isfinite(x) for x in cell.state):
        raise AssertionError("V31W_NEGATIVE_NONFINITE_PROBE_BROKEN")
    # Freeze adjacency validation blocks malicious monkeypatched topology.
    original_ring_contract()


def original_build_rows(cells,cue,first):
    if (type(cells) is not list or len(cells)!=CELLS or
        len({id(x) for x in cells})!=CELLS or
        any(type(x) is not Cell or x.identity!=i
            for i,x in enumerate(cells))):
        raise AssertionError("V31W_EIGHT_DISTINCT_PER_BANK_CELL_OWNERS_REQUIRED")
    if type(cue) is not str or cue not in PUBLIC_CUES:
        raise ValueError("V31W_INVALID_CUE")
    if type(first) is not str or first not in ACTIONS:
        raise ValueError("V31W_INVALID_FIRST_ACTION")
    cue_idx=PUBLIC_CUES.index(cue)
    first_idx=ACTIONS.index(first)
    cue_site=OBS_SITES[OBSERVATIONS.index(cue)]
    first_site=ACTION_SITES[first_idx]
    for cell in cells:
        cell.site_pulse(cue_site,cue_idx,first_site,first_idx)
    directed=0
    t=time.process_time_ns()
    for _hop in range(HOPS):
        # All reads below use the PREVIOUS hop's private owner.state buffers.
        # Every cell only accesses its two original ring neighbor owners.
        for i,owner in enumerate(cells):
            prior=owner.state
            left,right=RING[i]
            l=cells[left].state
            r=cells[right].state
            dest=owner.scratch
            for ch in range(CHANNELS):
                incoming=l[ch] if l[ch]>=r[ch] else r[ch]
                val=INITIAL_GAIN*incoming
                dest[ch]=min(2.0,max(prior[ch],val))
            directed+=2
        # Fixed synchronous hop boundary, no OS threads, locks or global cache.
        for owner in cells:
            owner.state,owner.scratch=owner.scratch,owner.state
    hop_ns=time.process_time_ns()-t
    for cell in cells:
        if any(not math.isfinite(x) or x<0.0 or x>2.0
               for x in cell.state):
            raise AssertionError("V31W_NONFINITE_OR_OUT_OF_BOUNDS_NEIGHBOR_STATE")
        cell.build_row(cue,first)
    return [list(cell.row) for cell in cells],directed,hop_ns


@contextmanager
def dual_buffer_adapter():
    original_features=v22.SharedContextRingDev._features
    original_first=v22.SharedContextRingDev.accept_first
    original_site=v22._site_features
    original_mix=v22._mix_scalars
    original_ring_contract()
    banks=WeakKeyDictionary()
    stats={
        "eight_distinct_owners_per_bank":0,
        "validated_first_action_resets":0,
        "real_source_feature_builds":0,
        "cell_local_row_hits":0,
        "logical_neighbor_deliveries":0,
        "four_hop_owner_cpu_ns":0,
        "native_source_or_scalar_route_modified":False,
        "all_feature_rows_owned_individually":True,
        "threads_or_processes_spawned":False,
        "physical_bytes_or_wire_measured":False,
    }

    def owners(bank):
        if bank not in banks:
            banks[bank]=[Cell(i) for i in range(CELLS)]
        cells=banks[bank]
        if len(cells)!=8 or len({id(c) for c in cells})!=8:
            raise AssertionError("V31W_CELL_OWNERSHIP_LOST")
        stats["eight_distinct_owners_per_bank"]=max(
            stats["eight_distinct_owners_per_bank"],len(cells))
        return cells

    def first(bank,*args,**kwargs):
        result=original_first(bank,*args,**kwargs)
        for cell in owners(bank):
            cell.clear()
        stats["validated_first_action_resets"]+=1
        return result

    def features(bank):
        bank._check_frozen()
        if bank.cue is None or bank.first is None:
            raise ValueError("V31W_ORIGINAL_PUBLIC_FIRST_ACTION_MISSING")
        cells=owners(bank)
        if all(c.row is not None and c.cue==bank.cue and
               c.first==bank.first for c in cells):
            stats["cell_local_row_hits"]+=1
            return [list(c.row) for c in cells]
        rows,directed,ns=original_build_rows(cells,bank.cue,bank.first)
        stats["real_source_feature_builds"]+=1
        stats["logical_neighbor_deliveries"]+=directed
        stats["four_hop_owner_cpu_ns"]+=ns
        return rows

    v22.SharedContextRingDev._features=features
    v22.SharedContextRingDev.accept_first=first
    try:
        yield stats
    finally:
        v22.SharedContextRingDev._features=original_features
        v22.SharedContextRingDev.accept_first=original_first
        if (v22._site_features is not original_site or
            v22._mix_scalars is not original_mix):
            raise AssertionError("V31W_ORIGINAL_FEATURE_OR_SCALAR_NATIVE_WAS_PATCHED")


def run(source,blocks,arm,*,cold=False):
    if arm not in ARMS or blocks not in LENGTHS:
        raise ValueError("V31W_INVALID_ARM_OR_LENGTH")
    if arm=="dual_buffer":
        with dual_buffer_adapter() as stats:
            signatures=extended_replay(source,blocks,False,cold=cold)
        expected=2*EVENTS_PER_BLOCK*blocks
        if (stats["eight_distinct_owners_per_bank"]!=8 or
            stats["validated_first_action_resets"]!=expected or
            stats["real_source_feature_builds"]!=expected or
            stats["cell_local_row_hits"]<=0 or
            stats["logical_neighbor_deliveries"]!=expected*8*2*HOPS or
            stats["native_source_or_scalar_route_modified"] is not False or
            stats["threads_or_processes_spawned"] is not False):
            raise AssertionError("V31W_OWNER_RING_OR_EPISODE_SCOPE_DRIFT")
    elif arm=="v31r":
        with bank_cell_local_adapter() as stats:
            signatures=extended_replay(source,blocks,False,cold=cold)
        expected=2*EVENTS_PER_BLOCK*blocks
        if (stats["max_slots_per_bank"]!=8 or
            stats["original_feature_builds"]!=expected or
            stats["validated_bank_episode_resets"]!=expected or
            stats["bank_local_feature_hits"]<=0):
            raise AssertionError("V31W_V31R_COMPARATOR_UNCHANGED_OR_SCOPE_DRIFT")
    else:
        signatures=extended_replay(source,blocks,False,cold=cold)
        stats=None
    return signatures,stats


def parity_preflight():
    negative_source_controls()
    source=train_source()["pretrained_shared"]
    expected={}
    for blocks in LENGTHS:
        original,_=run(source,blocks,"original")
        for arm in ARMS:
            continuous,_=run(source,blocks,arm)
            cold,_=run(source,blocks,arm,cold=True)
            if original!=continuous or cold!=original:
                raise AssertionError("V31W_ORIGINAL_AND_COLD_CHECKPOINT_OR_TRACE_DIFFERENCE")
        expected[str(blocks)]=original
    return expected


def worker(arm,blocks):
    if arm not in ARMS or blocks not in LENGTHS:
        raise ValueError("V31W_UNAUTHORIZED_WORKER")
    start=time.process_time_ns()
    source=train_source()["pretrained_shared"]
    trained=time.process_time_ns()
    signatures,stats=run(source,blocks,arm)
    replayed=time.process_time_ns()
    resident,meter=actual_os_peak_resident_bytes()
    total=time.process_time_ns()
    if not (0<start<trained<replayed<=total and resident>0):
        raise AssertionError("V31W_REAL_OS_RESIDENT_OR_PROCESS_CPU_UNAVAILABLE")
    print(json.dumps({
        "schema":SCHEMA,"role":"fresh_worker","host":sys.platform,
        "arm":arm,"blocks":blocks,"events":24*blocks,
        "source_trained_original_once":True,
        "source_training_updates":TRAINING_UPDATES,
        "total_process_cpu_ns":total,"source_training_cpu_ns":trained-start,
        "replay_cpu_ns":replayed-trained,
        "os_peak_resident_bytes":resident,
        "os_peak_resident_meter":meter,
        "signatures":signatures,"public_diversity":verified_diversity(blocks),
        "cell_owner_stats":stats if arm=="dual_buffer" else None,
        "scientific_first_use":False,"original_learner_modified":False,
        "physical_wire_or_energy_measured":False,
    },sort_keys=True,separators=(",",":"),allow_nan=False))


def launch(arm,blocks):
    if arm not in ARMS or blocks not in LENGTHS:
        raise ValueError("V31W_INVALID_WORKER_REQUEST")
    env=dict(os.environ)
    env["PYTHONHASHSEED"]="0"
    env["PYTHONDONTWRITEBYTECODE"]="1"
    t=time.perf_counter_ns()
    p=subprocess.run(
        [sys.executable,"-B",str(Path(__file__).resolve()),
         "--worker",arm,str(blocks)],
        cwd=ROOT,env=env,text=True,capture_output=True,
        check=False,timeout=MAX_WORKER_SECONDS)
    wall=time.perf_counter_ns()-t
    if p.returncode or p.stderr.strip():
        raise AssertionError("V31W_WORKER_PROCESS_FAILURE_{}_{}_{}_{}".format(
            arm,blocks,p.returncode,p.stderr[-1200:]))
    try:
        d=json.loads(p.stdout)
    except (TypeError,ValueError) as e:
        raise AssertionError("V31W_MISSING_WORKER_JSON") from e
    if (type(d) is not dict or d.get("schema")!=SCHEMA or
        d.get("role")!="fresh_worker" or d.get("host")!=sys.platform or
        d.get("arm")!=arm or d.get("blocks")!=blocks or
        d.get("events")!=24*blocks or
        d.get("source_trained_original_once") is not True or
        d.get("source_training_updates")!=TRAINING_UPDATES or
        d.get("public_diversity")!=verified_diversity(blocks) or
        d.get("scientific_first_use") is not False or
        d.get("original_learner_modified") is not False or
        d.get("physical_wire_or_energy_measured") is not False):
        raise AssertionError("V31W_WORKER_IDENTITY_OR_SOURCE_CHANGED")
    for f in ("total_process_cpu_ns","source_training_cpu_ns",
              "replay_cpu_ns","os_peak_resident_bytes"):
        if type(d.get(f)) is not int or d[f]<=0:
            raise AssertionError("V31W_WORKER_RESOURCE_MISSING_"+f)
    method=("LINUX_GETRUSAGE_SELF_RU_MAXRSS_KIB_X1024" if sys.platform=="linux"
            else "WINDOWS_GETPROCESSMEMORYINFO_PEAKWORKINGSETSIZE_BYTES"
            if sys.platform=="win32" else None)
    if not method or d.get("os_peak_resident_meter")!=method:
        raise AssertionError("V31W_TRUE_HOST_PEAK_RSS_MISSING")
    sig=d.get("signatures")
    if (type(sig) is not list or len(sig)!=blocks or
        sig[0]["trace_sha256"]!=EXPECTED_TRACE_SHA or
        sig[0]["checkpoint_sha256"]!=EXPECTED_CHECKPOINT_SHA):
        raise AssertionError("V31W_FIRST_ORIGINAL_STATE_NOT_PRESERVED")
    if arm=="dual_buffer":
        stats=d.get("cell_owner_stats")
        expected=2*24*blocks
        if (type(stats) is not dict or
            stats.get("eight_distinct_owners_per_bank")!=8 or
            stats.get("validated_first_action_resets")!=expected or
            stats.get("real_source_feature_builds")!=expected or
            stats.get("cell_local_row_hits",0)<=0 or
            stats.get("logical_neighbor_deliveries")!=expected*8*2*HOPS or
            stats.get("threads_or_processes_spawned") is not False):
            raise AssertionError("V31W_SOURCE_LOCAL_CELL_OWNER_AUDIT_DRIFT")
    elif d.get("cell_owner_stats") is not None:
        raise AssertionError("V31W_CONTROL_HAS_CANDIDATE_CELL_STATE")
    d["parent_full_worker_wall_ns"]=wall
    return d


def ratio(a,b):
    v=a/b
    if not math.isfinite(v) or v<=0:
        raise AssertionError("V31W_INVALID_OS_RESOURCE_RATIO")
    return v


def audit():
    reference=parity_preflight()
    out=[]
    for blocks in LENGTHS:
        orig_sig=reference[str(blocks)]
        for arm in ARMS:
            if launch(arm,blocks)["signatures"]!=orig_sig:
                raise AssertionError("V31W_WARMUP_STATE_OR_FIRST_BLOCK_DRIFT")
        pairs=[]
        for i in range(TRIALS):
            order=("original","dual_buffer") if i%2==0 else (
                "dual_buffer","original")
            sample={arm:launch(arm,blocks) for arm in order}
            sample["v31r"]=launch("v31r",blocks)
            if any(s["signatures"]!=orig_sig for s in sample.values()):
                raise AssertionError("V31W_MODEL_REWARD_SCHEDULE_OR_CHECKPOINT_NOT_EXACT")
            a,b,c=sample["original"],sample["dual_buffer"],sample["v31r"]
            pairs.append({
                "trial":i+1,"order":list(order),
                "original_cpu_ns":a["total_process_cpu_ns"],
                "dual_cpu_ns":b["total_process_cpu_ns"],
                "v31r_cpu_ns":c["total_process_cpu_ns"],
                "original_rss_bytes":a["os_peak_resident_bytes"],
                "dual_rss_bytes":b["os_peak_resident_bytes"],
                "v31r_rss_bytes":c["os_peak_resident_bytes"],
                "original_wall_ns":a["parent_full_worker_wall_ns"],
                "dual_wall_ns":b["parent_full_worker_wall_ns"],
                "v31r_wall_ns":c["parent_full_worker_wall_ns"],
                "dual_hop_cpu_diagnostic_ns":b["cell_owner_stats"]["four_hop_owner_cpu_ns"],
                "dual_row_cache_hits":b["cell_owner_stats"]["cell_local_row_hits"],
                "dual_logical_neighbor_messages":b["cell_owner_stats"]["logical_neighbor_deliveries"],
                "cpu_ratio":ratio(b["total_process_cpu_ns"],a["total_process_cpu_ns"]),
                "rss_ratio":ratio(b["os_peak_resident_bytes"],a["os_peak_resident_bytes"]),
                "wall_ratio":ratio(b["parent_full_worker_wall_ns"],a["parent_full_worker_wall_ns"]),
                "vs_v31r_cpu_ratio":ratio(b["total_process_cpu_ns"],c["total_process_cpu_ns"]),
                "vs_v31r_rss_ratio":ratio(b["os_peak_resident_bytes"],c["os_peak_resident_bytes"]),
            })
        median=lambda field:statistics.median(z[field] for z in pairs)
        out.append({
            "blocks":blocks,"events":24*blocks,
            "public_diversity":verified_diversity(blocks),
            "cpu_ratio_median":round(median("cpu_ratio"),8),
            "rss_ratio_median":round(median("rss_ratio"),8),
            "wall_ratio_median":round(median("wall_ratio"),8),
            "vs_v31r_cpu_ratio_median":round(median("vs_v31r_cpu_ratio"),8),
            "vs_v31r_rss_ratio_median":round(median("vs_v31r_rss_ratio"),8),
            "original_cpu_median_ns":int(median("original_cpu_ns")),
            "dual_cpu_median_ns":int(median("dual_cpu_ns")),
            "v31r_cpu_median_ns":int(median("v31r_cpu_ns")),
            "hop_cpu_median_ns":int(median("dual_hop_cpu_diagnostic_ns")),
            "logical_neighbor_deliveries":2*24*blocks*8*2*HOPS,
            "original_checkpoint_and_cold_restore_parity":True,
            "pairs":pairs,
        })
    short,long=out
    positive=(short["cpu_ratio_median"]<=.95 and
              short["rss_ratio_median"]<=1.10 and
              long["cpu_ratio_median"]<=.85 and
              long["rss_ratio_median"]<=1.10 and
              long["vs_v31r_cpu_ratio_median"]<=1.05 and
              long["vs_v31r_rss_ratio_median"]<=1.10)
    print(json.dumps({
        "schema":SCHEMA,"host":sys.platform,"status":"COMPLETE",
        "classification":(
            "V31W_DUAL_BUFFER_HOST_RESOURCE_POSITIVE__NO_SCIENCE"
            if positive else
            "V31W_DUAL_BUFFER_NO_JOINT_RESOURCE_WIN__NO_SCIENCE"),
        "fresh_source_trained_os_workers":36,
        "fixed_five_pairs_per_length":TRIALS,
        "original_learner_and_checkpoint_all_exact":True,
        "original_eight_cell_neighbors_only":True,
        "real_os_threads_or_processes_as_cells_claimed":False,
        "original_native_source_unchanged":True,
        "physical_message_traffic_or_wire_bytes_claimed":False,
        "scientific_first_use":False,
        "cpu96_le":.95,"cpu384_le":.85,"rss_limit":1.10,
        "vs_v31r_cpu384_le":1.05,"vs_v31r_rss384_le":1.10,
        "results":out,
    },sort_keys=True,separators=(",",":"),allow_nan=False))


if __name__=="__main__":
    if len(sys.argv)==4 and sys.argv[1]=="--worker":
        worker(sys.argv[2],int(sys.argv[3]))
    elif len(sys.argv)==1:
        audit()
    else:
        raise SystemExit("V31W_DISALLOWED_CLI")
