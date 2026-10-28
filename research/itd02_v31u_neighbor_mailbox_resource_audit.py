"""V31U: original eight cell-owner threads, strictly neighbor-only barrier mailboxes.

External research/audit harness only; no native source, learner, checkpoint
or accepted artifact mutation. Object mailbox deliveries are NOT wire bytes.
"""
from __future__ import annotations
from dataclasses import dataclass
import hashlib
import json
import math
import os
from pathlib import Path
from queue import Empty
import statistics
import subprocess
import sys
import threading
import time

from research.itd02_v23_unfamiliar_mapping_audit import train_source
from research.itd02_v31i_cold_restart_audit import replay
from research.itd02_v31j_executed_edge_ledger_audit import (
    EXPECTED_CHECKPOINT_SHA, EXPECTED_TRACE_SHA,
)
from research.itd02_v31o_full_process_resource_audit import actual_os_peak_resident_bytes
from research.itd02_v31s_eight_process_ring_audit import (
    expected_local_pulse, failclosed_negative_packet_tests, wire, unwire,
)
from research import itd02_v31t_thread_ring_resource_audit as v31t
from yggdrasil.itd02_v17_neighbor_carried_learner_dev import (
    ACTIONS, CELLS, CHANNELS, HOPS, PUBLIC_CUES, RING, canonical,
)
from yggdrasil.itd02_v18_intermediate_plasticity_dev import (
    INITIAL_GAIN, HEAD_FEATURES,
)
import yggdrasil.itd02_v22_shared_context_ring_dev as v22

ROOT = Path(__file__).resolve().parents[1]
SCHEMA = "yggdrasil.itd02.v31u.neighbor_mailbox.v1"
ARMS = ("original", "mailbox")
PAIRS = 5
MAX_TIMEOUT = 150
WAIT = 12
EXPECTED_BUILDS = 48
EXPECTED_MESSAGES = EXPECTED_BUILDS * CELLS * 2 * HOPS
EXPECTED_SHADOW_JSON_BYTES = 219136


@dataclass
class Mailbox:
    """Exactly one immutable producer-owned frame, read by one original neighbor."""
    payload: tuple | None = None


def check_frame(frame, epoch, hop, source):
    if not isinstance(frame, tuple) or len(frame) != 5:
        raise ValueError("V31U_MALFORMED_MAILBOX_FRAME")
    e,h,s,row,n = frame
    if (type(e) is not int or e != epoch or
            type(h) is not int or h != hop or
            type(s) is not int or s != source or
            type(row) is not tuple or len(row) != CHANNELS or
            any(type(x) not in (int,float) or not math.isfinite(x) or
                not 0 <= x <= 2 for x in row) or
            type(n) is not int or n <= 0 or n > 4096):
        raise ValueError("V31U_STALE_NONNEIGHBOR_OR_NONFINITE_FRAME")
    # n is the *counterfactual* canonical JSON packet length (not IPC bytes).
    # Frame never contains a mutable row list or another owner's state pointer.
    actual_shadow = len(wire({
        "episode":e, "hop":h, "source":s, "row":list(row)}))
    if n != actual_shadow:
        raise ValueError("V31U_SHADOW_FRAME_LENGTH_DRIFT")
    return row,n


def reject_wrong_mailbox_packets():
    good = (9,1,2,tuple([0.] * CHANNELS),len(wire({
        "episode":9,"hop":1,"source":2,"row":[0.]*CHANNELS})))
    assert check_frame(good,9,1,2)[0] == tuple([0.]*CHANNELS)
    for case in (
        (good,9,1,3), (good,9,2,2), (good,10,1,2),
        (list(good),9,1,2),
        ((9,1,2,tuple([float("nan")]*7),good[4]),9,1,2),
        ((9,1,2,tuple([0.]*7),good[4]+1),9,1,2),
    ):
        try:
            check_frame(*case)
        except ValueError:
            continue
        raise AssertionError("V31U_WRONG_OWNER_EPOCH_HOP_OR_FLOAT_ACCEPTED")


def owner_cell(cell, command, result, outbound_left, outbound_right,
               inbound_left, inbound_right, hop_barrier):
    """One native OS thread owns its own cell row and two directed output slots."""
    my_id = threading.get_native_id()
    banks = {}
    counts = {
        "peer_sent":0, "peer_received":0,
        "peer_bytes_sent":0, "peer_bytes_received":0,
        "builds":0, "hits":0, "clears":0, "max_bank_slots":0,
        "control_received":0, "control_bytes_received":0,
        "parent_sent":0, "parent_bytes_sent":0,
    }

    def respond(obj):
        raw = wire(obj)
        result.put(raw, timeout=WAIT)
        counts["parent_sent"] += 1
        counts["parent_bytes_sent"] += len(raw)

    try:
        while True:
            command_raw = command.get(timeout=WAIT)
            counts["control_received"] += 1
            counts["control_bytes_received"] += len(command_raw)
            req = unwire(command_raw)
            operation = req.get("op")
            if operation == "STOP":
                respond({
                    "op":"STATS", "cell":cell,
                    "process_id":os.getpid(),
                    "native_thread_id":my_id,
                    "thread_cpu_ns":time.thread_time_ns(),
                    "counts":counts,
                })
                return
            bank = req.get("bank")
            if type(bank) is not int or bank not in (0,1):
                raise ValueError("V31U_WRONG_BANK_OWNER")
            if operation == "CLEAR":
                banks.pop(bank,None)
                counts["clears"] += 1
                respond({"op":"CLEARED","cell":cell,"bank":bank})
                continue
            if operation != "GET":
                raise ValueError("V31U_ILLEGAL_CELL_COMMAND")
            cue, first, pulse, epoch = (
                req.get("cue"),req.get("first"),
                req.get("pulse"),req.get("epoch"))
            if (type(epoch) is not int or not 0 < epoch <= 100000 or
                    type(pulse) is not list or
                    pulse != expected_local_pulse(cell,cue,first)):
                raise ValueError("V31U_ORIGINAL_CELL_LOCAL_INPUT_REQUIRED")
            prior=banks.get(bank)
            if prior is not None and prior[:2] == (cue,first):
                counts["hits"] += 1
                respond({
                    "op":"ROW","cell":cell,"bank":bank,
                    "epoch":epoch,"native_thread_id":my_id,
                    "hit":True,"row":list(prior[2]),
                })
                continue
            state=list(pulse)
            for hop in range(HOPS):
                row=tuple(state)
                shadow=len(wire({
                    "episode":epoch,"hop":hop,"source":cell,"row":state}))
                frame=(epoch,hop,cell,row,shadow)
                outbound_left.payload=frame
                outbound_right.payload=frame
                counts["peer_sent"] += 2
                counts["peer_bytes_sent"] += 2*shadow
                hop_barrier.wait(timeout=WAIT)  # ALL original adjacent owners published
                left,lb=check_frame(
                    inbound_left.payload,epoch,hop,RING[cell][0])
                right,rb=check_frame(
                    inbound_right.payload,epoch,hop,RING[cell][1])
                counts["peer_received"] += 2
                counts["peer_bytes_received"] += lb+rb
                next_state=[
                    min(2.0,max(state[ch],INITIAL_GAIN*
                                max(left[ch],right[ch])))
                    for ch in range(CHANNELS)
                ]
                hop_barrier.wait(timeout=WAIT)  # ALL readers done, safe overwrite
                state=next_state
            features=[1.0]+state+[
                state[c]*state[4+a] for c in range(4) for a in range(3)
            ]
            if len(features) != HEAD_FEATURES:
                raise AssertionError("V31U_ORIGINAL_SITE_FEATURE_DIMENSION_CHANGED")
            banks[bank]=(cue,first,tuple(features))
            counts["max_bank_slots"]=max(counts["max_bank_slots"],len(banks))
            counts["builds"]+=1
            respond({
                "op":"ROW","cell":cell,"bank":bank,
                "epoch":epoch,"native_thread_id":my_id,
                "hit":False,"row":features,
            })
    except BaseException as exc:
        hop_barrier.abort()
        try:
            result.put(wire({
                "op":"ERROR","cell":cell,"kind":type(exc).__name__,
                "error":str(exc)[:400],
            }),timeout=1)
        except BaseException:
            pass


class MailboxRing(v31t.ThreadRing):
    """Inherit original accepted-first orchestration, replace queue edge transport."""
    def __init__(self):
        super().__init__()
        self.channels={
            (i,j):Mailbox()
            for i in range(CELLS) for j in RING[i]
        }
        if len(self.channels)!=16 or any(
                j not in RING[i] for i,j in self.channels):
            raise AssertionError("V31U_NOT_ORIGINAL_SIXTEEN_DIRECTED_EDGES")
        self.hop_barrier=threading.Barrier(CELLS,timeout=WAIT)

    def start(self):
        if self.started:
            raise AssertionError("V31U_ALREADY_STARTED")
        for i in range(CELLS):
            left,right=RING[i]
            thread=threading.Thread(
                target=owner_cell,name="v31u-original-owner-cell-"+str(i),
                args=(
                    i,self.commands[i],self.results[i],
                    self.channels[(i,left)],self.channels[(i,right)],
                    self.channels[(left,i)],self.channels[(right,i)],
                    self.hop_barrier,
                ),daemon=True)
            thread.start()
            self.threads.append(thread)
        self.started=True
        pids=[th.native_id for th in self.threads]
        if (len(pids)!=8 or len(set(pids))!=8 or
                any(not th.is_alive() for th in self.threads) or
                threading.get_native_id() in pids):
            raise AssertionError("V31U_EIGHT_REAL_CELL_OWNER_THREADS_MISSING")

    def finish(self,*,abort=False):
        if abort:
            self.hop_barrier.abort()
        return super().finish(abort=abort)


def mailbox_replay(source):
    ring=MailboxRing()
    ring.start()
    try:
        with v31t.thread_adapter(ring):
            rows,checkpoint=replay(source,False)
        stats=ring.finish()
        result=v31t.summarize_thread_stats(ring,stats)
        if (result["peer_sent"]!=EXPECTED_MESSAGES or
                result["peer_received"]!=EXPECTED_MESSAGES or
                result["peer_bytes_sent"]!=EXPECTED_SHADOW_JSON_BYTES or
                result["peer_bytes_received"]!=EXPECTED_SHADOW_JSON_BYTES or
                result["directed_neighbor_queues"]!=16):
            raise AssertionError("V31U_ORIGINAL_NEIGHBOR_SHADOW_CUSTODY_CHANGED")
        result["neighbor_transport_kind"]="BOUND_SINGLE_WRITER_SINGLE_READER_MAILBOX_IMMUTABLE_PYTHON_REFERENCES"
        result["actual_copied_wire_bytes_measured"]=False
        result["canonical_json_bytes_are_counterfactual_shadow"]=True
        result["logical_deliveries"]=result["peer_sent"]
        result["seven_float64_conceptual_payload_bytes_per_message"]=56
        result["real_bounded_mailboxes"]=len(ring.channels)
        result["two_barriers_each_original_hop"]=True
        return rows,checkpoint,result
    finally:
        if ring.started:
            ring.finish(abort=True)


def preflight():
    failclosed_negative_packet_tests()
    reject_wrong_mailbox_packets()
    ring=MailboxRing()
    ring.start()
    class Bank:pass
    bank=Bank()
    try:
        for cue in PUBLIC_CUES:
            for first in ACTIONS:
                bank.cue,bank.first=cue,first
                ring.clear(bank)
                expected=v22._site_features(cue,first)
                if ring.get(bank)!=expected or ring.get(bank)!=expected:
                    raise AssertionError("V31U_ORIGINAL_PUBLIC_FEATURE_PARITY_FAILED")
        evidence=ring.finish()
        if (len(evidence)!=8 or
                sum(x["counts"]["builds"] for x in evidence)!=12*8 or
                sum(x["counts"]["hits"] for x in evidence)!=12*8):
            raise AssertionError("V31U_TWELVE_PUBLIC_FEATURE_PROVENANCE_MISSING")
    finally:
        if ring.started:
            ring.finish(abort=True)


def worker(arm):
    if arm not in ARMS:
        raise ValueError("V31U_UNKNOWN_WORKER_ARM")
    before_train=time.process_time_ns()
    source=train_source()["pretrained_shared"]
    after_train=time.process_time_ns()
    if arm=="mailbox":
        rows,checkpoint,transport=mailbox_replay(source)
    else:
        rows,checkpoint=replay(source,False)
        transport=None
    after_replay=time.process_time_ns()
    v31t.verify_source(rows,checkpoint)
    peak,method=actual_os_peak_resident_bytes()
    cpu=time.process_time_ns()
    if not (0 < before_train < after_train < after_replay <= cpu and peak>0):
        raise AssertionError("V31U_PROCESS_CLOCK_OR_TRUE_OS_RSS_MISSING")
    print(json.dumps({
        "schema":SCHEMA,"role":"worker","host":sys.platform,
        "arm":arm,"events":24,
        "source_pretraining_once_in_worker":True,
        "total_process_cpu_ns":cpu,
        "source_training_cpu_ns":after_train-before_train,
        "replay_cpu_ns":after_replay-after_train,
        "peak_os_resident_bytes":peak,"os_peak_method":method,
        "original_trace_sha256":EXPECTED_TRACE_SHA,
        "original_checkpoint_sha256":EXPECTED_CHECKPOINT_SHA,
        "mailbox_transport":transport,
        "same_os_process_all_threads_cpu_included":True,
        "original_native_learner_changed":False,
        "scientific_first_use":False,
        "actual_physical_wire_bytes_measured":False,
    },separators=(",",":"),sort_keys=True,allow_nan=False))


def run_fresh(arm):
    if arm not in ARMS:
        raise ValueError("V31U_LAUNCH_ARM")
    env=dict(os.environ)
    env["PYTHONHASHSEED"]="0"
    env["PYTHONDONTWRITEBYTECODE"]="1"
    start=time.perf_counter_ns()
    proc=subprocess.run(
        [sys.executable,"-B",str(Path(__file__).resolve()),"--worker",arm],
        cwd=ROOT,env=env,capture_output=True,text=True,
        timeout=MAX_TIMEOUT,check=False)
    elapsed=time.perf_counter_ns()-start
    if proc.returncode or proc.stderr.strip():
        raise AssertionError("V31U_WORKER_FAILED_{}_{}_{}".format(
            arm,proc.returncode,proc.stderr[-1600:]))
    try:
        data=json.loads(proc.stdout)
    except (TypeError,ValueError) as exc:
        raise AssertionError("V31U_INVALID_FRESH_WORKER_JSON") from exc
    if (type(data) is not dict or data.get("schema")!=SCHEMA or
            data.get("role")!="worker" or
            data.get("arm")!=arm or data.get("host")!=sys.platform or
            data.get("events")!=24 or
            data.get("source_pretraining_once_in_worker") is not True or
            data.get("original_trace_sha256")!=EXPECTED_TRACE_SHA or
            data.get("original_checkpoint_sha256")!=EXPECTED_CHECKPOINT_SHA or
            data.get("scientific_first_use") is not False or
            data.get("original_native_learner_changed") is not False or
            data.get("same_os_process_all_threads_cpu_included") is not True or
            data.get("actual_physical_wire_bytes_measured") is not False):
        raise AssertionError("V31U_SOURCE_OR_MODEL_OR_WORKER_PROVENANCE_MISMATCH")
    method=("LINUX_GETRUSAGE_SELF_RU_MAXRSS_KIB_X1024" if sys.platform=="linux"
            else "WINDOWS_GETPROCESSMEMORYINFO_PEAKWORKINGSETSIZE_BYTES"
            if sys.platform=="win32" else None)
    if not method or data.get("os_peak_method")!=method:
        raise AssertionError("V31U_MISSING_GENUINE_OS_RESIDENT_METER")
    for field in ("total_process_cpu_ns","source_training_cpu_ns",
                  "replay_cpu_ns","peak_os_resident_bytes"):
        if type(data.get(field)) is not int or data[field]<=0:
            raise AssertionError("V31U_RESOURCE_MISSING_"+field)
    if (arm=="mailbox") != (data.get("mailbox_transport") is not None):
        raise AssertionError("V31U_MAILBOX_CUSTODY_MISSING_OR_CONTROL_CONTAMINATION")
    if arm=="mailbox":
        ev=data["mailbox_transport"]
        if (ev.get("logical_deliveries")!=EXPECTED_MESSAGES or
                ev.get("real_bounded_mailboxes")!=16 or
                ev.get("peer_bytes_sent")!=EXPECTED_SHADOW_JSON_BYTES or
                ev.get("peer_bytes_received")!=EXPECTED_SHADOW_JSON_BYTES or
                ev.get("actual_copied_wire_bytes_measured") is not False or
                ev.get("canonical_json_bytes_are_counterfactual_shadow") is not True or
                len(set(ev.get("native_thread_ids",[])))!=8):
            raise AssertionError("V31U_NEIGHBOR_DELIVERIES_OR_SHADOW_METRIC_MISSING")
    data["parent_full_worker_wall_ns"]=elapsed
    return data


def ratio(a,b):
    val=a/b
    if not math.isfinite(val) or val<=0:
        raise AssertionError("V31U_UNMETERED_RESOURCE_RATIO")
    return val


def audit():
    preflight()
    for arm in ARMS:
        run_fresh(arm)
    v31t.launch("eight_thread")  # fixed contemporary comparator warmup
    pairs=[]
    for i in range(PAIRS):
        order=ARMS if i%2==0 else tuple(reversed(ARMS))
        readings={arm:run_fresh(arm) for arm in order}
        original,mailbox=readings["original"],readings["mailbox"]
        queued=v31t.launch("eight_thread")  # independently re-trains same source
        if (queued["original_trace_sha256"]!=EXPECTED_TRACE_SHA or
                queued["original_checkpoint_sha256"]!=EXPECTED_CHECKPOINT_SHA):
            raise AssertionError("V31U_V31T_COMPARATOR_NOT_ORIGINAL")
        pair={
            "trial":i+1,"order":list(order),
            "original_cpu_ns":original["total_process_cpu_ns"],
            "mailbox_cpu_ns":mailbox["total_process_cpu_ns"],
            "v31t_queue_cpu_ns":queued["total_process_cpu_ns"],
            "original_rss_bytes":original["peak_os_resident_bytes"],
            "mailbox_rss_bytes":mailbox["peak_os_resident_bytes"],
            "v31t_queue_rss_bytes":queued["true_os_peak_resident_bytes"],
            "original_wall_ns":original["parent_full_worker_wall_ns"],
            "mailbox_wall_ns":mailbox["parent_full_worker_wall_ns"],
            "v31t_queue_wall_ns":queued["parent_measured_full_worker_wall_ns"],
            "cpu_vs_original":ratio(mailbox["total_process_cpu_ns"],
                                    original["total_process_cpu_ns"]),
            "rss_vs_original":ratio(mailbox["peak_os_resident_bytes"],
                                    original["peak_os_resident_bytes"]),
            "wall_vs_original":ratio(mailbox["parent_full_worker_wall_ns"],
                                     original["parent_full_worker_wall_ns"]),
            "cpu_vs_v31t_queue":ratio(mailbox["total_process_cpu_ns"],
                                      queued["total_process_cpu_ns"]),
            "wall_vs_v31t_queue":ratio(mailbox["parent_full_worker_wall_ns"],
                                       queued["parent_measured_full_worker_wall_ns"]),
            "rss_vs_v31t_queue":ratio(mailbox["peak_os_resident_bytes"],
                                      queued["true_os_peak_resident_bytes"]),
            "logical_directed_neighbor_messages":mailbox["mailbox_transport"]["logical_deliveries"],
            "counterfactual_original_json_bytes":mailbox["mailbox_transport"]["peer_bytes_sent"],
            "eight_distinct_cell_owner_threads":len(set(
                mailbox["mailbox_transport"]["native_thread_ids"])),
        }
        pairs.append(pair)
    med=lambda key:statistics.median(x[key] for x in pairs)
    cpu,rss,wall,qcpu,qwall,qrss=(
        med("cpu_vs_original"),med("rss_vs_original"),
        med("wall_vs_original"),med("cpu_vs_v31t_queue"),
        med("wall_vs_v31t_queue"),med("rss_vs_v31t_queue"))
    positive=(cpu<=1.10 and rss<=1.25 and wall<=1.20 and
              qcpu<=0.92 and qwall<=0.90 and qrss<=1.10)
    print(json.dumps({
        "schema":SCHEMA,
        "classification":(
            "V31U_MAILBOX_HOST_RESOURCE_POSITIVE__NO_SCIENCE" if positive else
            "V31U_MAILBOX_RESOURCE_NEGATIVE__NO_SCIENCE"),
        "host":sys.platform,"status":"COMPLETE",
        "fresh_os_workers_launched":18,
        "paired_trial_count":PAIRS,
        "original_trace_checkpoint_exact_all_workers":True,
        "eight_distinct_live_cell_owner_threads":True,
        "directed_original_neighbor_mailboxes":16,
        "logical_neighbor_reference_deliveries":EXPECTED_MESSAGES,
        "counterfactual_canonical_json_bytes":EXPECTED_SHADOW_JSON_BYTES,
        "real_peer_bytes_copied_or_physical_wire_measured":False,
        "python_barrier_scheduling_not_native_learning_speed":True,
        "whole_process_cpu_includes_all_thread_cost":True,
        "original_native_model_changed":False,
        "scientific_first_use":False,
        "frozen_original_cpu_le":1.10,"frozen_original_rss_le":1.25,
        "frozen_original_wall_le":1.20,
        "frozen_v31t_queue_cpu_le":0.92,
        "frozen_v31t_queue_wall_le":0.90,
        "frozen_v31t_queue_rss_le":1.10,
        "median_cpu_vs_original":round(cpu,8),
        "median_rss_vs_original":round(rss,8),
        "median_wall_vs_original":round(wall,8),
        "median_cpu_vs_v31t_queue":round(qcpu,8),
        "median_wall_vs_v31t_queue":round(qwall,8),
        "median_rss_vs_v31t_queue":round(qrss,8),
        "pairs":pairs,
    },separators=(",",":"),sort_keys=True,allow_nan=False))


if __name__=="__main__":
    if len(sys.argv)==3 and sys.argv[1]=="--worker":
        worker(sys.argv[2])
    elif len(sys.argv)==1:
        audit()
    else:
        raise SystemExit("V31U_DISALLOWED_COMMAND")
