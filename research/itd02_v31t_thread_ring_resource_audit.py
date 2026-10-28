"""V31T: 8 real same-process Python threads, original ring-only bounded channels.

External engineering-only source experiment. No original native learner edits,
no scientific admission and no unsupported native parallel-speed claim.
"""
from __future__ import annotations

from contextlib import contextmanager
import hashlib
import json
import math
import os
from pathlib import Path
from queue import Queue, Empty
import statistics
import subprocess
import sys
import threading
import time
from weakref import WeakKeyDictionary

from research.itd02_v23_unfamiliar_mapping_audit import train_source
from research.itd02_v31i_cold_restart_audit import replay
from research.itd02_v31j_executed_edge_ledger_audit import (
    EXPECTED_CHECKPOINT_SHA, EXPECTED_TRACE_SHA,
)
from research.itd02_v31o_full_process_resource_audit import actual_os_peak_resident_bytes
from research.itd02_v31r_bank_cell_locality_audit import bank_cell_local_adapter
from research.itd02_v31s_eight_process_ring_audit import (
    wire, unwire, expected_local_pulse, verify_neighbor_packet,
    failclosed_negative_packet_tests,
)
from yggdrasil.itd02_v17_neighbor_carried_learner_dev import (
    ACTIONS, CELLS, CHANNELS, HOPS, PUBLIC_CUES, RING, canonical,
)
from yggdrasil.itd02_v18_intermediate_plasticity_dev import (
    INITIAL_GAIN, HEAD_FEATURES,
)
import yggdrasil.itd02_v22_shared_context_ring_dev as v22

ROOT = Path(__file__).resolve().parents[1]
SCHEMA = "yggdrasil.itd02.v31t.eight_thread_ring.v1"
ARMS = ("baseline", "eight_thread", "v31r_local")
PAIRS = 5
EXPECTED_BUILDS = 2 * 24
EXPECTED_MESSAGES = EXPECTED_BUILDS * CELLS * 2 * HOPS
EXPECTED_PEER_BYTES = 219136
MAX_WORKER_SECONDS = 180
MAX_CHANNEL_WAIT = 12


def cell_thread(cell, command, result, left_out, right_out, left_in, right_in):
    """Own exactly one cell's two bank rows, and only direct neighbor queues."""
    my_native_id = threading.get_native_id()
    slots = {}
    counts = {
        "peer_sent": 0, "peer_received": 0,
        "peer_bytes_sent": 0, "peer_bytes_received": 0,
        "builds": 0, "hits": 0, "clears": 0,
        "max_bank_slots": 0,
        "control_received": 0, "control_bytes_received": 0,
        "parent_sent": 0, "parent_bytes_sent": 0,
    }

    def reply(obj):
        data = wire(obj)
        result.put(data, timeout=MAX_CHANNEL_WAIT)
        counts["parent_sent"] += 1
        counts["parent_bytes_sent"] += len(data)

    try:
        while True:
            data = command.get(timeout=MAX_CHANNEL_WAIT)
            counts["control_received"] += 1
            counts["control_bytes_received"] += len(data)
            req = unwire(data)
            action = req.get("op")
            if action == "STOP":
                reply({
                    "op": "STATS", "cell": cell,
                    "native_thread_id": my_native_id,
                    "process_id": os.getpid(),
                    "thread_cpu_ns": time.thread_time_ns(),
                    "counts": counts,
                })
                break
            bank = req.get("bank")
            if type(bank) is not int or not 0 <= bank < 2:
                raise ValueError("V31T_UNAUTHORIZED_BANK")
            if action == "CLEAR":
                slots.pop(bank, None)
                counts["clears"] += 1
                reply({"op": "CLEARED", "bank": bank, "cell": cell})
                continue
            if action != "GET":
                raise ValueError("V31T_BAD_CELL_COMMAND")
            cue, first, pulse, epoch = (
                req.get("cue"), req.get("first"),
                req.get("pulse"), req.get("epoch"))
            if (type(epoch) is not int or not 0 < epoch <= 100000 or
                    type(pulse) is not list or
                    pulse != expected_local_pulse(cell, cue, first)):
                raise ValueError("V31T_ILLEGAL_OR_NONLOCAL_PUBLIC_PULSE")
            saved = slots.get(bank)
            if saved is not None and saved[:2] == (cue, first):
                counts["hits"] += 1
                reply({
                    "op": "ROW", "cell": cell, "bank": bank,
                    "epoch": epoch, "native_thread_id": my_native_id,
                    "hit": True, "row": list(saved[2]),
                })
                continue
            state = list(pulse)
            for hop in range(HOPS):
                frame = wire({
                    "episode": epoch, "hop": hop,
                    "source": cell, "row": state,
                })
                for outgoing in (left_out, right_out):
                    outgoing.put(frame, timeout=MAX_CHANNEL_WAIT)
                    counts["peer_sent"] += 1
                    counts["peer_bytes_sent"] += len(frame)
                try:
                    left_packet = left_in.get(timeout=MAX_CHANNEL_WAIT)
                    right_packet = right_in.get(timeout=MAX_CHANNEL_WAIT)
                except Empty as exc:
                    raise RuntimeError("V31T_REQUIRED_NEIGHBOR_NOT_RESPONDING") from exc
                left = verify_neighbor_packet(
                    left_packet, epoch, hop, RING[cell][0])
                right = verify_neighbor_packet(
                    right_packet, epoch, hop, RING[cell][1])
                counts["peer_received"] += 2
                counts["peer_bytes_received"] += len(left_packet) + len(right_packet)
                state = [
                    min(2.0, max(state[ch], INITIAL_GAIN *
                                 max(left[ch], right[ch])))
                    for ch in range(CHANNELS)
                ]
            row = [1.0] + list(state) + [
                state[c] * state[4 + a]
                for c in range(4) for a in range(3)
            ]
            if len(row) != HEAD_FEATURES:
                raise AssertionError("V31T_WRONG_ORIGINAL_FEATURE_DIMENSION")
            slots[bank] = (cue, first, tuple(row))
            counts["max_bank_slots"] = max(counts["max_bank_slots"], len(slots))
            counts["builds"] += 1
            reply({
                "op": "ROW", "cell": cell, "bank": bank,
                "epoch": epoch, "native_thread_id": my_native_id,
                "hit": False, "row": row,
            })
    except BaseException as exc:
        try:
            result.put(wire({
                "op": "ERROR", "cell": cell, "kind": type(exc).__name__,
                "error": str(exc)[:500],
            }), timeout=1)
        except BaseException:
            pass


class ThreadRing:
    def __init__(self):
        self.channels = {
            (cell, neighbor): Queue(maxsize=1)
            for cell in range(CELLS) for neighbor in RING[cell]
        }
        if (len(self.channels) != 16 or
                any(dst not in RING[src] for src, dst in self.channels)):
            raise AssertionError("V31T_NOT_ORIGINAL_DIRECT_NEIGHBOR_RING")
        self.commands = [Queue(maxsize=1) for _ in range(CELLS)]
        self.results = [Queue(maxsize=1) for _ in range(CELLS)]
        self.threads = []
        self.bank_ids = WeakKeyDictionary()
        self.next_bank = 0
        self.epoch = 0
        self.rows_requested = 0
        self.invalidations = 0
        self.parent_control_bytes_sent = 0
        self.parent_control_bytes_received = 0
        self.started = False

    def start(self):
        if self.started:
            raise AssertionError("V31T_ALREADY_STARTED")
        for cell in range(CELLS):
            left, right = RING[cell]
            thread = threading.Thread(
                target=cell_thread,
                name="v31t-original-cell-" + str(cell),
                args=(
                    cell, self.commands[cell], self.results[cell],
                    self.channels[(cell, left)], self.channels[(cell, right)],
                    self.channels[(left, cell)], self.channels[(right, cell)],
                ),
                daemon=True,
            )
            thread.start()
            self.threads.append(thread)
        self.started = True
        ids = [t.native_id for t in self.threads]
        if (len(ids) != 8 or len(set(ids)) != 8 or
                any(not t.is_alive() for t in self.threads) or
                threading.get_native_id() in ids):
            raise AssertionError("V31T_EIGHT_SEPARATE_NATIVE_THREAD_IDS_MISSING")

    def _bank(self, bank):
        if bank not in self.bank_ids:
            if self.next_bank >= 2:
                raise AssertionError("V31T_TOO_MANY_ORIGINAL_BANK_OBJECTS")
            self.bank_ids[bank] = self.next_bank
            self.next_bank += 1
        return self.bank_ids[bank]

    def request_all(self, requests, operation):
        if not self.started or len(requests) != CELLS:
            raise AssertionError("V31T_NOT_ACTIVE_EIGHT_CELL_QUEUE_RING")
        for queue, obj in zip(self.commands, requests):
            frame = wire(obj)
            queue.put(frame, timeout=MAX_CHANNEL_WAIT)
            self.parent_control_bytes_sent += len(frame)
        replies = []
        for cell, queue in enumerate(self.results):
            try:
                frame = queue.get(timeout=MAX_CHANNEL_WAIT)
            except Empty as exc:
                raise AssertionError("V31T_ORIGINAL_CELL_NONRESPONSE") from exc
            self.parent_control_bytes_received += len(frame)
            obj = unwire(frame)
            if obj.get("op") == "ERROR":
                raise AssertionError(
                    "V31T_CHILD_ERROR_CELL_{}_{}_{}".format(
                        cell, obj.get("kind"), obj.get("error")))
            if obj.get("op") != operation or obj.get("cell") != cell:
                raise AssertionError("V31T_CROSS_CELL_WRONG_RESPONSE")
            replies.append(obj)
        return replies

    def clear(self, bank):
        bankid = self._bank(bank)
        rows = self.request_all(
            [{"op": "CLEAR", "bank": bankid} for _ in range(CELLS)],
            "CLEARED",
        )
        if any(row.get("bank") != bankid for row in rows):
            raise AssertionError("V31T_INVALIDATION_NOT_BANK_LOCAL")
        self.invalidations += 1

    def get(self, bank):
        bankid = self._bank(bank)
        cue, first = bank.cue, bank.first
        if cue not in PUBLIC_CUES or first not in ACTIONS:
            raise ValueError("V31T_NO_ORIGINAL_ACCEPTED_FIRST")
        self.epoch += 1
        replies = self.request_all([
            {
                "op": "GET", "bank": bankid,
                "cue": cue, "first": first,
                "pulse": expected_local_pulse(cell, cue, first),
                "epoch": self.epoch,
            }
            for cell in range(CELLS)
        ], "ROW")
        ids = [x["native_thread_id"] for x in replies]
        if (len(set(ids)) != 8 or
                any(replies[cell].get("bank") != bankid or
                    replies[cell].get("epoch") != self.epoch or
                    ids[cell] != self.threads[cell].native_id or
                    type(replies[cell].get("row")) is not list or
                    len(replies[cell]["row"]) != HEAD_FEATURES
                    for cell in range(CELLS))):
            raise AssertionError("V31T_NONLOCAL_FEATURE_OR_WRONG_THREAD")
        self.rows_requested += 1
        return [x["row"] for x in replies]

    def finish(self, *, abort=False):
        if not self.started:
            return None
        stats = None
        if not abort:
            stats = self.request_all(
                [{"op": "STOP"} for _ in range(CELLS)], "STATS")
        for thread in self.threads:
            thread.join(timeout=MAX_CHANNEL_WAIT)
            if thread.is_alive():
                raise AssertionError("V31T_LEAKED_ACTIVE_CELL_THREAD")
        self.started = False
        if not abort:
            if (len(stats) != 8 or
                    len({x["native_thread_id"] for x in stats}) != 8 or
                    any(x["native_thread_id"] != self.threads[i].native_id or
                        x.get("process_id") != os.getpid() or
                        type(x.get("thread_cpu_ns")) is not int or
                        x["thread_cpu_ns"] <= 0
                        for i, x in enumerate(stats))):
                raise AssertionError("V31T_THREAD_CPU_OR_IDENTITY_MISSING")
        return stats


@contextmanager
def thread_adapter(pool):
    old_features = v22.SharedContextRingDev._features
    old_first = v22.SharedContextRingDev.accept_first
    original_site = v22._site_features
    original_mix = v22._mix_scalars

    def first(bank, *args, **kwargs):
        result = old_first(bank, *args, **kwargs)
        pool.clear(bank)
        return result

    def features(bank):
        bank._check_frozen()
        if bank.cue is None or bank.first is None:
            raise ValueError("V31T_ORIGINAL_PUBLIC_FIRST_NOT_ACCEPTED")
        return pool.get(bank)

    v22.SharedContextRingDev._features = features
    v22.SharedContextRingDev.accept_first = first
    try:
        yield
    finally:
        v22.SharedContextRingDev.accept_first = old_first
        v22.SharedContextRingDev._features = old_features
        if original_site is not v22._site_features:
            raise AssertionError("V31T_ORIGINAL_SITE_TRANSPORT_MUTATED")
        if original_mix is not v22._mix_scalars:
            raise AssertionError("V31T_ORIGINAL_SCALAR_MIX_MUTATED")


def verify_source(rows, checkpoint):
    if (type(rows) is not list or len(rows) != 24 or
            hashlib.sha256(canonical(rows)).hexdigest() != EXPECTED_TRACE_SHA or
            hashlib.sha256(checkpoint).hexdigest() != EXPECTED_CHECKPOINT_SHA):
        raise AssertionError("V31T_ORIGINAL_V31I_TRACE_OR_CHECKPOINT_DRIFT")


def thread_replay(source):
    ring = ThreadRing()
    ring.start()
    try:
        with thread_adapter(ring):
            rows, checkpoint = replay(source, False)
        stats = ring.finish()
        return rows, checkpoint, summarize_thread_stats(ring, stats)
    finally:
        if ring.started:
            ring.finish(abort=True)


def summarize_thread_stats(ring, stats):
    result = {
        "native_thread_ids": [x["native_thread_id"] for x in stats],
        "single_process_id": os.getpid(),
        "thread_count": len(stats),
        "directed_neighbor_queues": len(ring.channels),
        "peer_sent": sum(x["counts"]["peer_sent"] for x in stats),
        "peer_received": sum(x["counts"]["peer_received"] for x in stats),
        "peer_bytes_sent": sum(x["counts"]["peer_bytes_sent"] for x in stats),
        "peer_bytes_received": sum(x["counts"]["peer_bytes_received"] for x in stats),
        "builds": sum(x["counts"]["builds"] for x in stats),
        "hits": sum(x["counts"]["hits"] for x in stats),
        "clears": sum(x["counts"]["clears"] for x in stats),
        "max_slots_per_cell": max(x["counts"]["max_bank_slots"] for x in stats),
        "thread_cpu_sum_diagnostic_ns": sum(x["thread_cpu_ns"] for x in stats),
        "parent_control_bytes_sent": ring.parent_control_bytes_sent,
        "parent_control_bytes_received": ring.parent_control_bytes_received,
        "per_cell": stats,
    }
    if (result["thread_count"] != 8 or
            len(set(result["native_thread_ids"])) != 8 or
            result["directed_neighbor_queues"] != 16 or
            result["peer_sent"] != EXPECTED_MESSAGES or
            result["peer_received"] != EXPECTED_MESSAGES or
            result["peer_bytes_sent"] != EXPECTED_PEER_BYTES or
            result["peer_bytes_received"] != EXPECTED_PEER_BYTES or
            result["builds"] != EXPECTED_BUILDS * 8 or
            result["clears"] != EXPECTED_BUILDS * 8 or
            result["hits"] <= 0 or
            result["max_slots_per_cell"] > 2 or
            ring.invalidations != EXPECTED_BUILDS or
            ring.rows_requested <= EXPECTED_BUILDS or
            any(x["counts"]["builds"] != EXPECTED_BUILDS or
                x["counts"]["clears"] != EXPECTED_BUILDS or
                x["counts"]["hits"] <= 0 or
                x["counts"]["peer_bytes_sent"] != x["counts"]["peer_bytes_received"]
                for x in stats)):
        raise AssertionError("V31T_ORIGINAL_RING_THREAD_OR_IPC_CUSTODY_FAILED")
    return result


def source_preflight():
    failclosed_negative_packet_tests()
    ring = ThreadRing()
    ring.start()
    class Bank:
        pass
    bank = Bank()
    try:
        for cue in PUBLIC_CUES:
            for first in ACTIONS:
                bank.cue, bank.first = cue, first
                ring.clear(bank)
                expected = v22._site_features(cue, first)
                original = ring.get(bank)
                cached = ring.get(bank)
                if original != expected or cached != expected:
                    raise AssertionError("V31T_DIFFERENT_CELL_FEATURES_FROM_ORIGINAL")
        evidence = ring.finish()
        if (len(evidence) != 8 or
                sum(x["counts"]["builds"] for x in evidence) != 12*8 or
                sum(x["counts"]["hits"] for x in evidence) != 12*8):
            raise AssertionError("V31T_SOURCE_FEATURE_PREFLIGHT_INCOMPLETE")
    finally:
        if ring.started:
            ring.finish(abort=True)


def worker(arm):
    if arm not in ARMS:
        raise AssertionError("V31T_DISALLOWED_ARM")
    train_start = time.process_time_ns()
    source = train_source()["pretrained_shared"]
    train_end = time.process_time_ns()
    if arm == "eight_thread":
        rows, checkpoint, thread_stats = thread_replay(source)
    elif arm == "v31r_local":
        with bank_cell_local_adapter():
            rows, checkpoint = replay(source, False)
        thread_stats = None
    else:
        rows, checkpoint = replay(source, False)
        thread_stats = None
    replay_end = time.process_time_ns()
    verify_source(rows, checkpoint)
    resident, meter = actual_os_peak_resident_bytes()
    cpu = time.process_time_ns()
    if not (0 < train_end-train_start < cpu and
            0 < replay_end-train_end < cpu and resident > 0):
        raise AssertionError("V31T_PROCESS_OS_CPU_OR_RSS_UNAVAILABLE")
    print(json.dumps({
        "schema": SCHEMA, "role": "fresh_worker", "arm": arm,
        "host": sys.platform, "events": 24,
        "source_pretrained_this_process": True,
        "original_trace_sha256": EXPECTED_TRACE_SHA,
        "original_checkpoint_sha256": EXPECTED_CHECKPOINT_SHA,
        "total_process_cpu_ns": cpu,
        "training_cpu_ns": train_end - train_start,
        "replay_cpu_ns": replay_end - train_end,
        "true_os_peak_resident_bytes": resident,
        "os_resident_method": meter,
        "thread_neighbor_evidence": thread_stats,
        "cp_python_threads_not_independent_native_models": True,
        "all_thread_cpu_in_process_clock": True,
        "separate_child_processes_launched": False,
        "native_learner_modified": False,
        "scientific_first_use": False,
    }, separators=(",", ":"), sort_keys=True, allow_nan=False))


def launch(arm):
    if arm not in ARMS:
        raise AssertionError("V31T_INVALID_LAUNCH_ARM")
    env = dict(os.environ)
    env["PYTHONHASHSEED"] = "0"
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    start = time.perf_counter_ns()
    proc = subprocess.run(
        [sys.executable, "-B", str(Path(__file__).resolve()), "--worker", arm],
        cwd=ROOT, env=env, capture_output=True, text=True,
        timeout=MAX_WORKER_SECONDS, check=False)
    wall = time.perf_counter_ns() - start
    if proc.returncode or proc.stderr.strip():
        raise AssertionError("V31T_WORKER_FAILED_{}_{}_{}".format(
            arm, proc.returncode, proc.stderr[-1500:]))
    try:
        data = json.loads(proc.stdout)
    except (ValueError, TypeError) as exc:
        raise AssertionError("V31T_MALFORMED_WORKER_REPORT") from exc
    if (type(data) is not dict or data.get("schema") != SCHEMA or
            data.get("role") != "fresh_worker" or
            data.get("arm") != arm or
            data.get("host") != sys.platform or
            data.get("events") != 24 or
            data.get("source_pretrained_this_process") is not True or
            data.get("original_trace_sha256") != EXPECTED_TRACE_SHA or
            data.get("original_checkpoint_sha256") != EXPECTED_CHECKPOINT_SHA or
            data.get("scientific_first_use") is not False or
            data.get("native_learner_modified") is not False or
            data.get("all_thread_cpu_in_process_clock") is not True or
            data.get("separate_child_processes_launched") is not False):
        raise AssertionError("V31T_SOURCE_OR_WORKER_IDENTITY_DRIFT")
    method = ("LINUX_GETRUSAGE_SELF_RU_MAXRSS_KIB_X1024"
              if sys.platform == "linux" else
              "WINDOWS_GETPROCESSMEMORYINFO_PEAKWORKINGSETSIZE_BYTES"
              if sys.platform == "win32" else None)
    if not method or data.get("os_resident_method") != method:
        raise AssertionError("V31T_REAL_OS_RESIDENT_MISSING")
    for key in ("total_process_cpu_ns", "training_cpu_ns",
                "replay_cpu_ns", "true_os_peak_resident_bytes"):
        if type(data.get(key)) is not int or data[key] <= 0:
            raise AssertionError("V31T_UNMETERED_" + key)
    if (arm == "eight_thread") != (
            data.get("thread_neighbor_evidence") is not None):
        raise AssertionError("V31T_THREAD_METRICS_MISSING_OR_CONTROL_CONTAMINATED")
    if arm == "eight_thread":
        t = data["thread_neighbor_evidence"]
        if (t.get("thread_count") != 8 or
                t.get("directed_neighbor_queues") != 16 or
                t.get("peer_sent") != EXPECTED_MESSAGES or
                t.get("peer_received") != EXPECTED_MESSAGES or
                t.get("peer_bytes_sent") != EXPECTED_PEER_BYTES or
                t.get("peer_bytes_received") != EXPECTED_PEER_BYTES or
                len(set(t.get("native_thread_ids", []))) != 8 or
                t.get("builds") != 48*8 or t.get("clears") != 48*8 or
                t.get("max_slots_per_cell") > 2):
            raise AssertionError("V31T_WRONG_NEIGHBOR_CHANNEL_MESSAGE_OR_LOCAL_OWNER")
    if wall <= 0:
        raise AssertionError("V31T_INVALID_FULL_OS_WALL")
    data["parent_measured_full_worker_wall_ns"] = wall
    return data


def ratio(candidate, baseline):
    val = candidate / baseline
    if not math.isfinite(val) or val <= 0:
        raise AssertionError("V31T_UNAVAILABLE_RATIO")
    return val


def audit():
    source_preflight()
    for arm in ARMS:
        launch(arm)
    observations = []
    for n in range(PAIRS):
        order = ("baseline", "eight_thread") if n % 2 == 0 else (
            "eight_thread", "baseline")
        records = {arm: launch(arm) for arm in order}
        records["v31r_local"] = launch("v31r_local")
        a,b,c = (records["baseline"], records["eight_thread"],
                 records["v31r_local"])
        observations.append({
            "pair": n+1, "order": list(order),
            "original_cpu_ns": a["total_process_cpu_ns"],
            "threaded_cpu_ns": b["total_process_cpu_ns"],
            "local_emulation_cpu_ns": c["total_process_cpu_ns"],
            "original_rss_bytes": a["true_os_peak_resident_bytes"],
            "threaded_rss_bytes": b["true_os_peak_resident_bytes"],
            "local_emulation_rss_bytes": c["true_os_peak_resident_bytes"],
            "original_wall_ns": a["parent_measured_full_worker_wall_ns"],
            "threaded_wall_ns": b["parent_measured_full_worker_wall_ns"],
            "local_emulation_wall_ns": c["parent_measured_full_worker_wall_ns"],
            "threaded_vs_original_cpu_ratio": ratio(
                b["total_process_cpu_ns"], a["total_process_cpu_ns"]),
            "threaded_vs_original_rss_ratio": ratio(
                b["true_os_peak_resident_bytes"],
                a["true_os_peak_resident_bytes"]),
            "threaded_vs_original_wall_ratio": ratio(
                b["parent_measured_full_worker_wall_ns"],
                a["parent_measured_full_worker_wall_ns"]),
            "threaded_vs_local_cpu_ratio": ratio(
                b["total_process_cpu_ns"], c["total_process_cpu_ns"]),
            "threaded_vs_local_rss_ratio": ratio(
                b["true_os_peak_resident_bytes"],
                c["true_os_peak_resident_bytes"]),
            "direct_neighbor_messages": b["thread_neighbor_evidence"]["peer_sent"],
            "canonical_neighbor_payload_bytes": b["thread_neighbor_evidence"]["peer_bytes_sent"],
            "unique_native_threads": b["thread_neighbor_evidence"]["thread_count"],
        })
    med = lambda key: statistics.median(x[key] for x in observations)
    cpu, rss, wall, localcpu, localrss = (
        med("threaded_vs_original_cpu_ratio"),
        med("threaded_vs_original_rss_ratio"),
        med("threaded_vs_original_wall_ratio"),
        med("threaded_vs_local_cpu_ratio"),
        med("threaded_vs_local_rss_ratio"))
    qualified = (
        cpu <= 1.50 and rss <= 1.40 and wall <= 1.80 and
        localcpu <= 2.0 and localrss <= 1.30
    )
    report = {
        "schema": SCHEMA,
        "classification": (
            "V31T_THREAD_RING_HOST_RESOURCE_FEASIBLE__NO_SCIENCE"
            if qualified else
            "V31T_THREAD_RING_RESOURCE_NEGATIVE__NO_SCIENCE"),
        "host": sys.platform, "status": "COMPLETE",
        "fresh_workers_launched": 18,
        "fixed_pair_trials": PAIRS,
        "peer_only_queue_topology_verified": True,
        "bounded_directed_neighbor_queues": 16,
        "eight_distinct_original_cell_owner_threads": True,
        "original_trace_and_checkpoint_exact_every_arm": True,
        "parent_os_cpu_includes_all_eight_threads": True,
        "cpu_threads_not_double_added": True,
        "real_os_peak_resident_one_process": True,
        "main_and_science_original_untouched": True,
        "native_parallel_learning_cells_proven": False,
        "python_gil_concurrency_not_native_parallel_speed": True,
        "real_interthread_canonical_payload_bytes": EXPECTED_PEER_BYTES,
        "physical_hardware_wire_bytes_qualified": False,
        "scientific_first_use": False,
        "cpu_gate_le": 1.50, "rss_gate_le": 1.40, "wall_gate_le": 1.80,
        "cpu_to_local_gate_le": 2.0, "rss_to_local_gate_le": 1.30,
        "median_paired_cpu_ratio": round(cpu,8),
        "median_paired_rss_ratio": round(rss,8),
        "median_paired_wall_ratio": round(wall,8),
        "median_thread_to_local_cpu_ratio": round(localcpu,8),
        "median_thread_to_local_rss_ratio": round(localrss,8),
        "pairs": observations,
    }
    print(json.dumps(report,separators=(",",":"),sort_keys=True,allow_nan=False))


if __name__ == "__main__":
    if len(sys.argv) == 3 and sys.argv[1] == "--worker":
        worker(sys.argv[2])
    elif len(sys.argv) == 1:
        audit()
    else:
        raise SystemExit("V31T_UNAUTHORIZED_CLI")
