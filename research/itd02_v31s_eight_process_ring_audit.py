"""V31S: source-only eight genuine OS-process *feature transport* cells.

Development experiment, not native learner implementation or proof of native
distributed learning; each worker has only its own row + direct ring IPC.
"""
from __future__ import annotations

from contextlib import contextmanager
import hashlib
import json
import math
import multiprocessing as mp
import os
from pathlib import Path
import statistics
import subprocess
import sys
import time
from weakref import WeakKeyDictionary

from research.itd02_v23_unfamiliar_mapping_audit import train_source
from research.itd02_v31i_cold_restart_audit import replay
from research.itd02_v31j_executed_edge_ledger_audit import (
    EXPECTED_CHECKPOINT_SHA, EXPECTED_TRACE_SHA,
)
from research.itd02_v31o_full_process_resource_audit import actual_os_peak_resident_bytes
from yggdrasil.itd02_v17_neighbor_carried_learner_dev import (
    ACTIONS, ACTION_SITES, CELLS, CHANNELS, HOPS, PUBLIC_CUES, canonical,
)
from yggdrasil.itd02_local_ring_memory_dev import OBS_SITES, OBSERVATIONS
from yggdrasil.itd02_v18_intermediate_plasticity_dev import INITIAL_GAIN, HEAD_FEATURES
import yggdrasil.itd02_v22_shared_context_ring_dev as v22

ROOT = Path(__file__).resolve().parents[1]
SCHEMA = "yggdrasil.itd02.v31s.eight_os_process_ring.v1"
ARMS = ("baseline", "eight_process")
PAIR_TRIALS = 3
MAX_WORKER_SECONDS = 240
MAX_NEIGHBOR_WAIT_S = 20
CELLS_EXPECTED = 8
EXPECTED_BUILDS = 2 * 24
PEER_MSG_PER_BUILD = CELLS * 2 * HOPS


def wire(obj):
    return canonical(obj)


def unwire(raw):
    if type(raw) is not bytes or not 0 < len(raw) <= 4096:
        raise ValueError("V31S_BAD_WIRE_FRAME")
    try:
        o = json.loads(raw)
    except (TypeError, ValueError) as exc:
        raise ValueError("V31S_BAD_JSON") from exc
    if type(o) is not dict:
        raise ValueError("V31S_BAD_PACKET")
    return o


def expected_local_pulse(cell, cue, first):
    if (type(cell) is not int or not 0 <= cell < 8 or
            type(cue) is not str or cue not in PUBLIC_CUES or
            type(first) is not str or first not in ACTIONS):
        raise ValueError("V31S_BAD_PUBLIC_LOCAL_INPUT")
    row = [0.0] * CHANNELS
    if cell == OBS_SITES[OBSERVATIONS.index(cue)]:
        row[PUBLIC_CUES.index(cue)] = 1.0
    if cell == ACTION_SITES[ACTIONS.index(first)]:
        row[4 + ACTIONS.index(first)] = 1.0
    return row


def verify_neighbor_packet(raw, episode, hop, source):
    obj = unwire(raw)
    if set(obj) != {"episode", "hop", "source", "row"} or (
            type(obj["episode"]) is not int or obj["episode"] != episode or
            type(obj["hop"]) is not int or obj["hop"] != hop or
            type(obj["source"]) is not int or obj["source"] != source or
            type(obj["row"]) is not list or len(obj["row"]) != CHANNELS or
            any(type(v) not in (int, float) or not math.isfinite(v) or
                not 0.0 <= v <= 2.0 for v in obj["row"])):
        raise ValueError("V31S_WRONG_HOP_SOURCE_OR_PAYLOAD")
    return obj["row"]


def failclosed_negative_packet_tests():
    good = wire({"episode": 11, "hop": 2, "source": 7,
                 "row": [0.0] * CHANNELS})
    assert verify_neighbor_packet(good, 11, 2, 7) == [0.0] * CHANNELS
    negatives = [
        (good, 11, 2, 6),
        (good, 11, 3, 7),
        (good, 12, 2, 7),
        (b'{"hop":2}', 11, 2, 7),
    ]
    for packet, ep, hop, peer in negatives:
        try:
            verify_neighbor_packet(packet, ep, hop, peer)
        except ValueError:
            continue
        raise AssertionError("V31S_NEGATIVE_PACKET_WAS_ACCEPTED")


def cell_process(cell, controller, left_pipe, right_pipe):
    """Executed in its own spawned process; no cross-cell access/memory."""
    my_pid = os.getpid()
    bank_slots = {}
    counts = {"peer_sent": 0, "peer_received": 0,
              "peer_bytes_sent": 0, "peer_bytes_received": 0,
              "parent_received": 0, "parent_bytes_received": 0,
              "parent_sent": 0, "parent_bytes_sent": 0,
              "builds": 0, "hits": 0, "clears": 0,
              "max_bank_slots": 0}
    def answer(payload):
        raw = wire(payload)
        controller.send_bytes(raw)
        counts["parent_sent"] += 1
        counts["parent_bytes_sent"] += len(raw)
    try:
        while True:
            if not controller.poll(MAX_NEIGHBOR_WAIT_S):
                raise RuntimeError("V31S_PARENT_CONTROL_TIMEOUT")
            raw = controller.recv_bytes()
            counts["parent_received"] += 1
            counts["parent_bytes_received"] += len(raw)
            cmd = unwire(raw)
            operation = cmd.get("op")
            if operation == "STOP":
                resident, source = actual_os_peak_resident_bytes()
                answer({"op": "STATS", "cell": cell, "pid": my_pid,
                        "cpu_ns": time.process_time_ns(),
                        "peak_rss_bytes": resident, "peak_rss_method": source,
                        "counts": counts})
                break
            bank = cmd.get("bank")
            if type(bank) is not int or not 0 <= bank < 8:
                raise ValueError("V31S_UNTRUSTED_BANK_ID")
            if operation == "CLEAR":
                bank_slots.pop(bank, None)
                counts["clears"] += 1
                answer({"op": "CLEARED", "cell": cell, "bank": bank})
                continue
            if operation != "GET":
                raise ValueError("V31S_DISALLOWED_COMMAND")
            cue, first, pulse, episode = (
                cmd.get("cue"), cmd.get("first"),
                cmd.get("pulse"), cmd.get("episode"))
            if (type(episode) is not int or not 0 < episode <= 100000 or
                    type(pulse) is not list or
                    pulse != expected_local_pulse(cell, cue, first)):
                raise ValueError("V31S_NONLOCAL_OR_INVALID_PUBLIC_PULSE")
            old = bank_slots.get(bank)
            if old is not None and old[:2] == (cue, first):
                counts["hits"] += 1
                answer({"op": "ROW", "cell": cell, "pid": my_pid,
                        "bank": bank, "episode": episode, "hit": True,
                        "row": list(old[2])})
                continue
            state = list(pulse)
            for hop in range(HOPS):
                frame = wire({"episode": episode, "hop": hop,
                              "source": cell, "row": state})
                for endpoint in (left_pipe, right_pipe):
                    endpoint.send_bytes(frame)
                    counts["peer_sent"] += 1
                    counts["peer_bytes_sent"] += len(frame)
                if not left_pipe.poll(MAX_NEIGHBOR_WAIT_S) or (
                        not right_pipe.poll(MAX_NEIGHBOR_WAIT_S)):
                    raise RuntimeError("V31S_MISSING_REQUIRED_NEIGHBOR")
                left_raw, right_raw = left_pipe.recv_bytes(), right_pipe.recv_bytes()
                left = verify_neighbor_packet(
                    left_raw, episode, hop, (cell - 1) % CELLS)
                right = verify_neighbor_packet(
                    right_raw, episode, hop, (cell + 1) % CELLS)
                counts["peer_received"] += 2
                counts["peer_bytes_received"] += len(left_raw) + len(right_raw)
                state = [
                    min(2.0, max(state[ch], INITIAL_GAIN *
                                 max(left[ch], right[ch])))
                    for ch in range(CHANNELS)
                ]
            representation = [1.0] + list(state) + [
                state[c] * state[4+a] for c in range(4) for a in range(3)
            ]
            if len(representation) != HEAD_FEATURES:
                raise AssertionError("V31S_ORIGINAL_SITE_REPRESENTATION_CHANGED")
            bank_slots[bank] = (cue, first, tuple(representation))
            counts["max_bank_slots"] = max(counts["max_bank_slots"],
                                           len(bank_slots))
            counts["builds"] += 1
            answer({"op": "ROW", "cell": cell, "pid": my_pid,
                    "bank": bank, "episode": episode, "hit": False,
                    "row": representation})
    finally:
        controller.close()
        left_pipe.close()
        right_pipe.close()


class EightCellRing:
    def __init__(self):
        self.context = mp.get_context("spawn")
        self.children = []
        self.controllers = []
        self.bank_ids = WeakKeyDictionary()
        self.next_bank = 0
        self.episode = 0
        self.rows_requests = 0
        self.invalidations = 0
        self.started = False

    def start(self):
        if self.started:
            raise AssertionError("V31S_RING_ALREADY_STARTED")
        # edge[i][0] belongs to cell i (right), edge[i][1] to cell i+1 (left).
        edges = [self.context.Pipe(duplex=True) for _ in range(CELLS)]
        ctrls = [self.context.Pipe(duplex=True) for _ in range(CELLS)]
        try:
            for cell in range(CELLS):
                p = self.context.Process(
                    target=cell_process,
                    args=(cell, ctrls[cell][1], edges[(cell-1)%CELLS][1],
                          edges[cell][0]), daemon=False)
                p.start()
                self.children.append(p)
                self.controllers.append(ctrls[cell][0])
                ctrls[cell][1].close()
            for a,b in edges:
                a.close()
                b.close()
            self.started = True
            pids = [p.pid for p in self.children]
            if (len(set(pids)) != 8 or None in pids or
                    os.getpid() in pids):
                raise AssertionError("V31S_EIGHT_SEPARATE_PROCESS_IDENTITIES_MISSING")
        except Exception:
            self.finish(abort=True)
            raise

    def _bank(self, bank):
        if bank not in self.bank_ids:
            if self.next_bank >= 8:
                raise AssertionError("V31S_TOO_MANY_BANK_INSTANCES")
            self.bank_ids[bank] = self.next_bank
            self.next_bank += 1
        return self.bank_ids[bank]

    def _request_all(self, commands, response_type):
        if not self.started or len(commands) != CELLS:
            raise AssertionError("V31S_NOT_EIGHT_CELL_ORCHESTRATION")
        for conn, cmd in zip(self.controllers, commands):
            conn.send_bytes(wire(cmd))
        out = []
        for cell, conn in enumerate(self.controllers):
            if not conn.poll(MAX_NEIGHBOR_WAIT_S):
                raise AssertionError("V31S_CELL_ORIGINAL_NEIGHBOR_TIMEOUT")
            answer = unwire(conn.recv_bytes())
            if answer.get("op") != response_type or answer.get("cell") != cell:
                raise AssertionError("V31S_WRONG_CELL_OR_COMMAND_RESULT")
            out.append(answer)
        return out

    def clear(self, bank):
        bankid = self._bank(bank)
        reports = self._request_all([{"op": "CLEAR", "bank": bankid}]
                                    * CELLS, "CLEARED")
        if any(x.get("bank") != bankid for x in reports):
            raise AssertionError("V31S_INVALIDATED_WRONG_ORIGINAL_BANK")
        self.invalidations += 1

    def get(self, bank):
        bankid = self._bank(bank)
        cue, first = bank.cue, bank.first
        if cue not in PUBLIC_CUES or first not in ACTIONS:
            raise ValueError("V31S_ORIGINAL_FIRST_PUBLIC_EVENT_REQUIRED")
        self.episode += 1
        plans = [
            {"op": "GET", "bank": bankid, "cue": cue, "first": first,
             "pulse": expected_local_pulse(cell, cue, first),
             "episode": self.episode}
            for cell in range(CELLS)
        ]
        rows = self._request_all(plans, "ROW")
        if (any(x.get("bank") != bankid or
                x.get("episode") != self.episode or
                x.get("pid") != self.children[cell].pid or
                type(x.get("row")) is not list or
                len(x["row"]) != HEAD_FEATURES
                for cell,x in enumerate(rows))):
            raise AssertionError("V31S_NONLOCAL_ROW_OR_PROCESS")
        self.rows_requests += 1
        return [x["row"] for x in rows]

    def finish(self, *, abort=False):
        if not self.children:
            return None
        stats = []
        if self.started and not abort:
            stats = self._request_all([{"op": "STOP"}] * CELLS, "STATS")
            if (len(stats) != 8 or
                    any(x.get("pid") != self.children[i].pid or
                        type(x.get("cpu_ns")) is not int or x["cpu_ns"] <= 0 or
                        type(x.get("peak_rss_bytes")) is not int or
                        x["peak_rss_bytes"] <= 0
                        for i,x in enumerate(stats))):
                raise AssertionError("V31S_CHILD_CPU_RSS_PROCESS_ID_PROVENANCE_DRIFT")
        for c in self.controllers:
            c.close()
        for p in self.children:
            p.join(timeout=MAX_NEIGHBOR_WAIT_S)
            if p.is_alive():
                p.terminate()
                p.join(timeout=MAX_NEIGHBOR_WAIT_S)
                raise AssertionError("V31S_ORPHANED_CHILD_PROCESS")
            if not abort and p.exitcode != 0:
                raise AssertionError("V31S_CHILD_PROCESS_NONZERO_EXIT")
        self.started = False
        return stats


@contextmanager
def eight_process_adapter(pool):
    old_feat = v22.SharedContextRingDev._features
    old_first = v22.SharedContextRingDev.accept_first
    old_site = v22._site_features
    old_mix = v22._mix_scalars

    def first(bank, *args, **kwargs):
        value = old_first(bank, *args, **kwargs)
        pool.clear(bank)
        return value

    def features(bank):
        bank._check_frozen()
        if bank.cue is None or bank.first is None:
            raise ValueError("V31S_NO_ORIGINAL_FIRST_PUBLIC_EVENT")
        return pool.get(bank)

    v22.SharedContextRingDev._features = features
    v22.SharedContextRingDev.accept_first = first
    try:
        yield
    finally:
        v22.SharedContextRingDev._features = old_feat
        v22.SharedContextRingDev.accept_first = old_first
        if v22._site_features is not old_site or v22._mix_scalars is not old_mix:
            raise AssertionError("V31S_ORIGINAL_NATIVE_SCALAR_OR_INPUT_MUTATED")


def replay_candidate(source):
    pool = EightCellRing()
    pool.start()
    try:
        with eight_process_adapter(pool):
            rows, checkpoint = replay(source, False)
        evidence = pool.finish()
        return rows, checkpoint, pool, evidence
    finally:
        if pool.started:
            pool.finish(abort=True)


def verify_source_result(rows, checkpoint):
    if (type(rows) is not list or len(rows) != 24 or
            hashlib.sha256(canonical(rows)).hexdigest() != EXPECTED_TRACE_SHA or
            hashlib.sha256(checkpoint).hexdigest() != EXPECTED_CHECKPOINT_SHA):
        raise AssertionError("V31S_ORIGINAL_V31I_LEARNING_OR_CHECKPOINT_DRIFT")


def source_preflight():
    failclosed_negative_packet_tests()
    # Distinct public cue+first contexts computed in independent OS cells,
    # against the unmodified original transport function.
    ring = EightCellRing()
    ring.start()
    class TestBank:
        pass
    bank = TestBank()
    try:
        for cue in PUBLIC_CUES:
            for first in ACTIONS:
                bank.cue, bank.first = cue, first
                ring.clear(bank)
                original = v22._site_features(cue, first)
                observed = ring.get(bank)
                if observed != original or ring.get(bank) != original:
                    raise AssertionError("V31S_NATIVE_SITE_FEATURE_ROW_MISMATCH")
        ring.finish()
    finally:
        if ring.started:
            ring.finish(abort=True)


def worker(arm):
    if arm not in ARMS:
        raise AssertionError("V31S_UNKNOWN_ARM")
    source = train_source()["pretrained_shared"]
    if arm == "eight_process":
        rows, checkpoint, pool, cell_stats = replay_candidate(source)
    else:
        rows, checkpoint = replay(source, False)
        pool, cell_stats = None, None
    verify_source_result(rows, checkpoint)
    parent_peak, parent_method = actual_os_peak_resident_bytes()
    parent_cpu = time.process_time_ns()
    total_cpu = parent_cpu
    rss_sum = parent_peak
    summary = None
    if cell_stats is not None:
        child_cpu = sum(x["cpu_ns"] for x in cell_stats)
        child_rss = sum(x["peak_rss_bytes"] for x in cell_stats)
        total_cpu += child_cpu
        rss_sum += child_rss
        summary = {
            "child_count": len(cell_stats),
            "child_distinct_pids": len(set(x["pid"] for x in cell_stats)),
            "peer_sent": sum(x["counts"]["peer_sent"] for x in cell_stats),
            "peer_received": sum(x["counts"]["peer_received"] for x in cell_stats),
            "peer_bytes_sent": sum(x["counts"]["peer_bytes_sent"] for x in cell_stats),
            "peer_bytes_received": sum(x["counts"]["peer_bytes_received"] for x in cell_stats),
            "cell_feature_builds": sum(x["counts"]["builds"] for x in cell_stats),
            "cell_feature_hits": sum(x["counts"]["hits"] for x in cell_stats),
            "bank_invalidations": pool.invalidations,
            "child_cpu_ns": child_cpu,
            "child_peak_rss_sum_bytes": child_rss,
            "parent_get_requests": pool.rows_requests,
            "child_max_bank_slots": max(x["counts"]["max_bank_slots"] for x in cell_stats),
            "per_cell": cell_stats,
        }
        if (summary["child_count"] != 8 or
                summary["child_distinct_pids"] != 8 or
                summary["peer_sent"] != EXPECTED_BUILDS * PEER_MSG_PER_BUILD or
                summary["peer_received"] != summary["peer_sent"] or
                summary["peer_bytes_sent"] != summary["peer_bytes_received"] or
                summary["cell_feature_builds"] != EXPECTED_BUILDS * CELLS or
                summary["bank_invalidations"] != EXPECTED_BUILDS or
                summary["child_max_bank_slots"] > 2 or
                summary["cell_feature_hits"] <= 0 or
                child_cpu <= 0 or child_rss <= 0):
            raise AssertionError("V31S_PROCESS_CELL_NEIGHBOR_MESSAGE_OR_LOCAL_SLOT_CUSTODY_DRIFT")
    print(json.dumps({
        "schema": SCHEMA, "role": "worker", "arm": arm,
        "host": sys.platform, "events": 24,
        "source_pretrained": True, "original_trace_sha256": EXPECTED_TRACE_SHA,
        "original_checkpoint_sha256": EXPECTED_CHECKPOINT_SHA,
        "parent_cpu_ns": parent_cpu, "total_cpu_including_child_ns": total_cpu,
        "parent_os_peak_rss_bytes": parent_peak,
        "conservative_sum_individual_peak_rss_bytes": rss_sum,
        "peak_rss_method": parent_method,
        "real_child_ipc_stats": summary,
        "scientific_first_use": False, "native_learner_modified": False,
        "truly_native_cell_runtime_qualified": False,
    }, sort_keys=True, separators=(",", ":"), allow_nan=False))


def launch(arm):
    env = dict(os.environ)
    env["PYTHONHASHSEED"] = "0"
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    start = time.perf_counter_ns()
    p = subprocess.run(
        [sys.executable, "-B", str(Path(__file__).resolve()), "--worker", arm],
        cwd=ROOT, env=env, text=True, capture_output=True,
        timeout=MAX_WORKER_SECONDS, check=False)
    elapsed = time.perf_counter_ns() - start
    if p.returncode or p.stderr.strip():
        raise AssertionError("V31S_WORKER_PROCESS_ERROR_{}_{}_{}".format(
            arm, p.returncode, p.stderr[-1600:]))
    try:
        result = json.loads(p.stdout)
    except (TypeError, ValueError) as exc:
        raise AssertionError("V31S_NONJSON_MEASUREMENT") from exc
    if (result.get("schema") != SCHEMA or result.get("arm") != arm or
            result.get("role") != "worker" or
            result.get("host") != sys.platform or result.get("events") != 24 or
            result.get("source_pretrained") is not True or
            result.get("original_trace_sha256") != EXPECTED_TRACE_SHA or
            result.get("original_checkpoint_sha256") != EXPECTED_CHECKPOINT_SHA or
            result.get("scientific_first_use") is not False or
            result.get("native_learner_modified") is not False):
        raise AssertionError("V31S_PARITY_AND_SOURCE_IDENTITY_DRIFT")
    for key in ("parent_cpu_ns", "total_cpu_including_child_ns",
                "parent_os_peak_rss_bytes",
                "conservative_sum_individual_peak_rss_bytes"):
        if type(result.get(key)) is not int or result[key] <= 0:
            raise AssertionError("V31S_NO_TRUE_RESOURCE_" + key)
    method = ("LINUX_GETRUSAGE_SELF_RU_MAXRSS_KIB_X1024"
              if sys.platform == "linux" else
              "WINDOWS_GETPROCESSMEMORYINFO_PEAKWORKINGSETSIZE_BYTES"
              if sys.platform == "win32" else None)
    if not method or result.get("peak_rss_method") != method:
        raise AssertionError("V31S_OS_PEAK_RSS_METHOD_UNAVAILABLE")
    if (arm == "eight_process") != (result.get("real_child_ipc_stats") is not None):
        raise AssertionError("V31S_CHILD_IPC_EVIDENCE_MISSING_OR_UNEXPECTED")
    result["spawn_to_exit_wall_ns"] = elapsed
    return result


def ratio(a, b):
    value = a/b
    if not math.isfinite(value) or value <= 0:
        raise AssertionError("V31S_MISSING_RESOURCE_RATIO")
    return value


def audit():
    source_preflight()
    for arm in ARMS:
        launch(arm)  # exactly one independent warmup per arm
    trials = []
    for i in range(PAIR_TRIALS):
        order = ARMS if i % 2 == 0 else tuple(reversed(ARMS))
        points = {arm: launch(arm) for arm in order}
        a, b = points["baseline"], points["eight_process"]
        trials.append({
            "trial": i+1, "order": list(order),
            "baseline_cpu_ns": a["total_cpu_including_child_ns"],
            "candidate_parent_cpu_ns": b["parent_cpu_ns"],
            "candidate_child_cpu_ns": b["real_child_ipc_stats"]["child_cpu_ns"],
            "candidate_total_cpu_ns": b["total_cpu_including_child_ns"],
            "baseline_peak_rss_bytes": a["conservative_sum_individual_peak_rss_bytes"],
            "candidate_parent_peak_rss_bytes": b["parent_os_peak_rss_bytes"],
            "candidate_child_peak_sum_bytes": b["real_child_ipc_stats"]["child_peak_rss_sum_bytes"],
            "candidate_peak_sum_bytes": b["conservative_sum_individual_peak_rss_bytes"],
            "baseline_wall_ns": a["spawn_to_exit_wall_ns"],
            "candidate_wall_ns": b["spawn_to_exit_wall_ns"],
            "cpu_ratio": ratio(b["total_cpu_including_child_ns"],
                               a["total_cpu_including_child_ns"]),
            "conservative_peak_sum_ratio": ratio(
                b["conservative_sum_individual_peak_rss_bytes"],
                a["conservative_sum_individual_peak_rss_bytes"]),
            "wall_ratio": ratio(b["spawn_to_exit_wall_ns"],
                                a["spawn_to_exit_wall_ns"]),
            "peer_sent": b["real_child_ipc_stats"]["peer_sent"],
            "peer_bytes_sent": b["real_child_ipc_stats"]["peer_bytes_sent"],
            "peer_bytes_received": b["real_child_ipc_stats"]["peer_bytes_received"],
            "child_unique_pids": b["real_child_ipc_stats"]["child_distinct_pids"],
        })
    med = lambda name: statistics.median(x[name] for x in trials)
    cpu, rss, wall = med("cpu_ratio"), med("conservative_peak_sum_ratio"), med("wall_ratio")
    report = {
        "schema": SCHEMA,
        "classification": (
            "V31S_EIGHT_OS_PROCESS_RING_RESOURCE_FEASIBLE__NO_SCIENCE"
            if cpu <= 3.0 and rss <= 6.0 and wall <= 5.0 else
            "V31S_EIGHT_OS_PROCESS_RING_RESOURCE_NEGATIVE__NO_SCIENCE"),
        "host": sys.platform,
        "topology": "EIGHT_INDEPENDENT_OS_PROCESSES_DIRECT_NEIGHBOR_RING",
        "topology_evidence_passed": True,
        "original_first_block_exact_trace_checkpoint": True,
        "original_native_source_or_weights_modified": False,
        "three_paired_trials": PAIR_TRIALS,
        "external_source_training_one_per_worker": True,
        "child_cpu_included": True,
        "child_peak_memory_conservative_sum_not_simultaneous_peak": True,
        "independent_native_yggdrasil_cells_proven": False,
        "actual_os_pipe_serialized_bytes_measured": True,
        "original_model_wire_bytes_reduced": False,
        "scientific_first_use": False,
        "q_holdouts_evaluated": False,
        "expected_peer_messages_per_candidate_replay": EXPECTED_BUILDS * PEER_MSG_PER_BUILD,
        "median_paired_cpu_ratio": round(cpu, 8),
        "median_paired_resident_sum_ratio": round(rss, 8),
        "median_paired_wall_ratio": round(wall, 8),
        "frozen_cpu_ratio_le": 3.0,
        "frozen_resident_ratio_le": 6.0,
        "frozen_wall_ratio_le": 5.0,
        "paired_trials": trials,
    }
    print(json.dumps(report, sort_keys=True, separators=(",", ":"), allow_nan=False))


if __name__ == "__main__":
    if len(sys.argv) == 3 and sys.argv[1] == "--worker":
        worker(sys.argv[2])
    elif len(sys.argv) == 1:
        audit()
    else:
        raise SystemExit("V31S_INVALID_CLI")
