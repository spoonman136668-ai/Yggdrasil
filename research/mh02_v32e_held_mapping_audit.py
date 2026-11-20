"""MH02: untouched V32E vs unchanged V32D and a source-public recency control.

Synthetic DEV only. Not original-world science, reward-free meta-learning,
new Yggdrasil accepted learning, first-use authority, or a new controller.
"""
from __future__ import annotations

from collections import deque
import hashlib
import json
import os
from pathlib import Path
import random
import subprocess
import sys
import tempfile
import time

import research.itd02_v32e_pair_consensus_audit as v32e
import research.itd02_v32d_context_memory_audit as v32d
import research.itd02_v32b_null_margin_audit as v32b
import research.itd02_v32c_world_reversal_audit as v32c
import research.itd02_v32a_native_microcells_audit as v32a
from research.itd02_v31o_full_process_resource_audit import actual_os_peak_resident_bytes

ROOT = Path(__file__).resolve().parents[1]
A = (0, 1, 2, 1)
MAPS = {"D": (1, 2, 2, 0), "E": (2, 2, 1, 0)}
SEEDS = (101, 103, 107, 109, 113)
PHASES = ("a", "b", "return_a")
STAGES = ("a240", "x0", "x60", "x240", "return_a240")
PARENT_SHA = "1b615944bab5bc6e60db63a6f78bd7d601905aa4"
PREREG_SHA = "5f543f7825dfdb46f952ca048656d97db8590b15"


def digest(data):
    if isinstance(data, bytes):
        raw = data
    else:
        raw = json.dumps(data, sort_keys=True, separators=(",", ":"),
                         allow_nan=False).encode()
    return hashlib.sha256(raw).hexdigest()


def source_guard():
    v32e.original_source_guard()
    if v32e.API.source_sha256 != hashlib.sha256(
            (ROOT / "research/itd02_v32e_pair_consensus.rs").read_bytes()).hexdigest():
        raise AssertionError("MH02_FROZEN_V32E_RUST_DRIFT")
    if (A != v32c.A or MAPS["D"] in (v32c.A, v32c.B, v32c.C)
            or MAPS["E"] in (v32c.A, v32c.B, v32c.C)
            or MAPS["D"] == MAPS["E"] or v32b.EPS != 1e-10):
        raise AssertionError("MH02_FROZEN_PUBLIC_MAPPING_DRIFT")
    assert tuple(sum(aa != bb for aa, bb in zip(A, m))
                 for m in MAPS.values()) == (3, 4)
    if set(SEEDS) & set(v32c.SEEDS) or set(SEEDS) & {181,191,193,197,211,223,227}:
        raise AssertionError("MH02_CONSUMED_SEED_OVERLAP")


def schedule(seed, phase):
    """Exactly the public v32c source algorithm on newly frozen seeds.

    v32c.schedule rejects new seeds by design: do not modify its allowlist.
    """
    if seed not in SEEDS or phase not in PHASES:
        raise ValueError("MH02_UNFROZEN_SEED_OR_PHASE")
    rng = random.Random(seed + {"a": 1000, "b": 2000, "return_a": 3000}[phase])
    result = []
    pairs = {(cue, action) for cue in range(4) for action in range(3)}
    for repeat in range(20):
        items = [(cue, action, repeat) for cue, action in sorted(pairs)]
        rng.shuffle(items)
        assert {(c, a) for c, a, _ in items} == pairs
        result.extend(items)
    assert len(result) == 240 and len(set(result)) == 240
    return result


def shuffled_null(seed):
    out = {}
    for cue in range(4):
        for action in range(3):
            sample = [1.0] * 10 + [-1.0] * 10
            random.Random(seed + 47000 + cue * 101 + action * 17).shuffle(sample)
            out[(cue, action)] = tuple(sample)
    return out


def outcome(mapping, cue, action, repeat, null=None, null_rows=None):
    if null == "alternating":
        return 1.0 if repeat % 2 == 0 else -1.0
    if null == "shuffled":
        assert null_rows is not None
        return null_rows[(cue, action)][repeat]
    return 1.0 if mapping[cue] == action else -1.0


class Recency:
    """Source-blind fully trained last-36 public outcome control, 12 cue-action bins."""
    def __init__(self):
        self.events = deque(maxlen=36)
        self.updates = 0

    def learn(self, cue, action, reward):
        if type(cue) is not int or cue not in range(4) or type(action) is not int or action not in range(3) or reward not in (-1.0, 1.0):
            raise ValueError("MH02_BAD_PUBLIC_FEEDBACK")
        self.events.append((cue, action, reward))
        self.updates += 1

    def scores(self, cue):
        if type(cue) is not int or cue not in range(4):
            raise ValueError("MH02_BAD_PUBLIC_CUE")
        values = []
        for action in range(3):
            seen = [reward for c, a, reward in self.events if c == cue and a == action]
            values.append(sum(seen) / len(seen) if seen else 0.0)
        return values

    def checkpoint(self):
        raw = {"schema": "ygg.mh02.recency.v1", "events": list(self.events),
               "updates": self.updates}
        return json.dumps(raw, sort_keys=True, separators=(",", ":")).encode()


def native_readout(api, h, target):
    before = api.checkpoint(h)
    ledger = api.ledger(h)
    rows = []
    for rep in range(24):
        for cue in range(4):
            api.observe_one(h, cue)
            rows.append(api.native_scores(h))
    if before != api.checkpoint(h) or ledger != api.ledger(h):
        raise AssertionError("MH02_READ_ONLY_EVAL_MUTATED_NATIVE_STATE")
    diag_a = v32b.diagnostics(rows, A)
    diag_x = v32b.diagnostics(rows, target)
    return {"a": diag_a["epsilon_stabilized_accuracy"],
            "x": diag_x["epsilon_stabilized_accuracy"],
            "score_sha": v32a.scores_hash(rows),
            "first_four_hex": diag_x["first_four_score_hex"],
            "checkpoint_sha": digest(before),
            "checkpoint_bytes": len(before),
            "ledger": ledger, "checkpoint": before}


def recency_readout(model, target):
    before = model.checkpoint()
    rows = [model.scores(cue) for _ in range(24) for cue in range(4)]
    if model.checkpoint() != before:
        raise AssertionError("MH02_RECENCY_READOUT_MUTATED_STATE")
    return {"a": v32b.diagnostics(rows, A)["epsilon_stabilized_accuracy"],
            "x": v32b.diagnostics(rows, target)["epsilon_stabilized_accuracy"],
            "score_sha": v32a.scores_hash(rows),
            "checkpoint_sha": digest(before),
            "checkpoint_bytes": len(before),
            "updates": model.updates}


def cold_probe(api_name, path, target):
    api = {"v32e": v32e.API, "v32d": v32d.API}[api_name]
    h = api.new()
    try:
        api.layout(h)
        raw = Path(path).read_bytes()
        if api.restore(h, raw):
            raise AssertionError("MH02_COLD_RESTORE_REJECTED")
        stage = native_readout(api, h, target)
        if stage["checkpoint"] != raw:
            raise AssertionError("MH02_COLD_FULL_BYTES_CHANGED")
        rss, meter = actual_os_peak_resident_bytes()
        print(json.dumps({
            "checkpoint_sha": stage["checkpoint_sha"],
            "score_sha": stage["score_sha"],
            "first_four_hex": stage["first_four_hex"],
            "ledger": stage["ledger"], "a": stage["a"], "x": stage["x"],
            "cpu_ns": time.process_time_ns(),
            "whole_process_peak_rss": rss, "rss_meter": meter,
            "native_source_sha": api.source_sha256,
            "native_binary_sha": api.binary_sha256,
        }, sort_keys=True, separators=(",", ":")))
    finally:
        api.free(h)


def verify_cold(api_name, stage, target):
    with tempfile.TemporaryDirectory(prefix="mh02-cold-") as temp:
        path = Path(temp) / "checkpoint.bin"
        path.write_bytes(stage["checkpoint"])
        before = time.perf_counter_ns()
        p = subprocess.run(
            [sys.executable, "-B", str(Path(__file__).resolve()),
             "--cold", api_name, str(path), ",".join(map(str, target))],
            cwd=ROOT, env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1"},
            text=True, capture_output=True, timeout=60, check=False)
        wall = time.perf_counter_ns() - before
    if p.returncode or p.stderr.strip():
        raise AssertionError("MH02_FRESH_OS_COLD_FAILURE " + p.stderr[-1000:])
    data = json.loads(p.stdout)
    for key in ("checkpoint_sha", "score_sha", "first_four_hex", "ledger", "a", "x"):
        if data[key] != stage[key]:
            raise AssertionError("MH02_COLD_SCORE_OR_MEMORY_MISMATCH_" + key)
    if not data["cpu_ns"] or not data["whole_process_peak_rss"]:
        raise AssertionError("MH02_COLD_OS_RESOURCES_MISSING")
    return {"cpu_ns": data["cpu_ns"], "wall_ns": wall,
            "rss_bytes": data["whole_process_peak_rss"]}


def frozen_native_arm(api_name, seed, target, null=None):
    api = {"v32e": v32e.API, "v32d": v32d.API}[api_name]
    h = api.new()
    initial = schedule(seed, "a")
    changed = schedule(seed, "b")
    returning = schedule(seed, "return_a")
    rows_for_null = shuffled_null(seed) if null == "shuffled" else None
    early = changed[:60]
    later = changed[60:]
    start_cpu = time.process_time_ns()
    stages, cold, streams = {}, {}, {}
    try:
        api.layout(h)
        for label, events, mapping, learn in (
            ("a240", initial, A, True),
            ("x0", (), target, True),
            ("x60", early, target, null != "frozen"),
            ("x240", later, target, null != "frozen"),
            ("return_a240", returning if null is None else (), A, null is None),
        ):
            signs = []
            for cue, action, repeat in events:
                reward = outcome(mapping, cue, action, repeat,
                                 null=null if label in ("x60", "x240") else None,
                                 null_rows=rows_for_null)
                api.observe_one(h, cue)
                api.native_scores(h)
                api.feedback_one(h, action, reward, learn)
                signs.append(reward)
            streams[label] = {"events": len(events), "reward_sha": digest(signs)}
            state = native_readout(api, h, target)
            if api_name == "v32e" and null is None and label != "x0":
                cold[label] = verify_cold(api_name, state, target)
            stages[label] = {k: v for k, v in state.items() if k != "checkpoint"}
        cpu_ns = time.process_time_ns() - start_cpu
        rss, meter = actual_os_peak_resident_bytes()
        return {"stages": stages, "streams": streams, "cold": cold,
                "cpu_ns_including_native": cpu_ns, "rss": rss,
                "rss_meter": meter, "binary_sha": api.binary_sha256}
    finally:
        api.free(h)


def recency_arm(seed, target):
    model = Recency()
    initial, changed, returning = (schedule(seed, x) for x in PHASES)
    start = time.process_time_ns()
    stages = {}
    for label, events, mapping in (
        ("a240", initial, A), ("x0", (), target),
        ("x60", changed[:60], target), ("x240", changed[60:], target),
        ("return_a240", returning, A),
    ):
        for cue, action, repeat in events:
            model.learn(cue, action, outcome(mapping, cue, action, repeat))
        stages[label] = recency_readout(model, target)
    return {"stages": stages, "cpu_ns": time.process_time_ns() - start,
            "checkpoint_bytes": len(model.checkpoint())}


def score(r, stage, policy):
    return r["stages"][stage][policy]


def seed_study(seed, label, target):
    fresh = frozen_native_arm("v32e", seed, target)
    old = frozen_native_arm("v32d", seed, target)
    control = recency_arm(seed, target)
    frozen = frozen_native_arm("v32e", seed, target, null="frozen")
    alt = frozen_native_arm("v32e", seed, target, null="alternating")
    sham = frozen_native_arm("v32e", seed, target, null="shuffled")
    result = {"seed": seed, "mapping": label,
              "adapt": fresh, "old_v32d": old,
              "recency": control, "frozen": frozen,
              "null_alternating": alt, "null_shuffled": sham}
    native_valid = (
        score(fresh, "a240", "a") >= .75
        and score(fresh, "x60", "x") >= .75
        and score(fresh, "x240", "x") >= .75
        and score(fresh, "return_a240", "a") >= .75
        and all(x["checkpoint_bytes"] == 2264 for x in fresh["stages"].values())
        and all(k in fresh["cold"] for k in
                ("a240", "x60", "x240", "return_a240"))
        and score(frozen, "x240", "a") >= .75
        and all(score(result[key], "x240", "a") >= .75 and
                all(x == 0 for x in result[key]["stages"]["x240"]["ledger"]["switches"])
                for key in ("null_alternating", "null_shuffled"))
    )
    strongest_early = max(score(old, "x60", "x"), score(control, "x60", "x"))
    result["native_gate_pass"] = native_valid
    result["best_control_early"] = strongest_early
    result["native_advantage_early"] = score(fresh, "x60", "x") - strongest_early
    return result


def run():
    source_guard()
    started = time.process_time_ns()
    pre = v32e.API.source_sha256
    results = []
    for label, target in MAPS.items():
        for seed in SEEDS:
            results.append(seed_study(seed, label, target))
    grouped = {}
    for label in MAPS:
        xs = [r for r in results if r["mapping"] == label]
        grouped[label] = {
            "native_mean_x60": sum(score(r["adapt"], "x60", "x") for r in xs) / len(xs),
            "old_mean_x60": sum(score(r["old_v32d"], "x60", "x") for r in xs) / len(xs),
            "recency_mean_x60": sum(score(r["recency"], "x60", "x") for r in xs) / len(xs),
            "native_mean_advantage": sum(r["native_advantage_early"] for r in xs) / len(xs),
            "all_native_gates": all(r["native_gate_pass"] for r in xs)}
    compile_wall = os.environ.get("MH02_COMPILE_WALL_NS")
    if compile_wall is None or not compile_wall.isdecimal():
        raise AssertionError("MH02_NATIVE_BUILD_COST_MISSING")
    native_ns = int(compile_wall) + sum(
        r["adapt"]["cpu_ns_including_native"] + sum(x["cpu_ns"] for x in r["adapt"]["cold"].values())
        for r in results)
    conventional_ns = sum(r["recency"]["cpu_ns"] for r in results)
    cost_ratio = native_ns / max(1, conventional_ns)
    accuracy_gain = all(d["all_native_gates"] and d["native_mean_advantage"] >= .05
                        for d in grouped.values())
    positive = accuracy_gain and cost_ratio <= 2.
    result_class = ("MH02_SOURCE_FREE_DEV_MECHANISM_GO" if positive else
                    "MH02_DEV_NO_GO_COST" if cost_ratio > 2 else "MH02_DEV_NO_GO")
    rss, meter = actual_os_peak_resident_bytes()
    return {"schema": "ygg.mh02.heldmapping.dev.v1",
            "parent_sha": PARENT_SHA, "prereg_amendment_sha": PREREG_SHA,
            "native_source_sha": pre,
            "native_binary_sha": v32e.API.binary_sha256,
            "original_source_first_use": False,
            "original_native_model_modified": False,
            "unseen_mapping_not_new_causal_family": True,
            "seeds": SEEDS, "targets": MAPS,
            "grouped": grouped, "results": results,
            "native_allin_cpu_or_compile_wall_ns": native_ns,
            "conventional_cpu_ns": conventional_ns,
            "native_to_recency_cost_ratio": cost_ratio,
            "whole_process_peak_rss_bytes": rss, "rss_meter": meter,
            "total_process_cpu_ns": time.process_time_ns() - started,
            "classification": result_class}


if __name__ == "__main__":
    if len(sys.argv) == 5 and sys.argv[1] == "--cold":
        api, path, mapping = sys.argv[2], sys.argv[3], tuple(map(int, sys.argv[4].split(",")))
        if api not in ("v32e", "v32d") or len(mapping) != 4:
            raise SystemExit("MH02_UNSUPPORTED_COLD_ARGS")
        cold_probe(api, path, mapping)
    elif len(sys.argv) == 1:
        print(json.dumps(run(), indent=2, sort_keys=True, allow_nan=False))
    else:
        raise SystemExit("MH02_UNKNOWN_ENTRYPOINT")
