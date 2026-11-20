"""MH04 preregistered *public synthetic DEV*, source-equivalent bank storage/return audit.

No new native learner, external source, historic seed replay, or promotion.
The evaluator may force offline bank readouts; the Rust learner NEVER can.
"""
from __future__ import annotations

from collections import defaultdict
import hashlib
import json
import os
from pathlib import Path
import random
import sys
import time

from research import mh03_checkpoint_bank_readback as bank
from research import mh02_v32e_held_mapping_audit as mh02
from research import itd02_v32b_null_margin_audit as v32b

ROOT = Path(__file__).resolve().parents[1]
PARENT_SHA = "907ad8d90b8a4bb6aa0b0473fd31890a4f88b909"
PREREG_SHA = "baf32dd04e12d10036049216c45afac8d38b909b"
TRIAL = "MH04-SYNTH-FG-401-409-419-421-431-20261120"
A = (0, 1, 2, 1)
MAPS = {"F": (2, 1, 0, 2), "G": (1, 0, 1, 2)}
SEEDS = (401, 409, 419, 421, 431)
STOPS = (1, 2, 4, 8, 24, 48)
OFFSETS = {"A": 14000, "X": 24000, "return": 34000}


def sha(x: bytes) -> str:
    return hashlib.sha256(x).hexdigest()


def sha_json(x) -> str:
    return sha(json.dumps(x, sort_keys=True, separators=(",", ":"),
                          allow_nan=False).encode())


def source_guard():
    mh02.source_guard()
    if (bank.SOURCE.read_bytes() != mh02.v32e.SOURCE.read_bytes()
            or bank.SIZE != mh02.v32e.API.size()
            or bank.SOURCE_BLOB !=
                "85237dcc82905e05a273b11023b5be5db722726e"
            or A != mh02.A or any(m == A or m in mh02.MAPS.values()
                                   for m in MAPS.values())
            or MAPS["F"] != (2, 1, 0, 2)
            or MAPS["G"] != (1, 0, 1, 2)
            or set(SEEDS) & (set(mh02.SEEDS) | set(mh02.v32c.SEEDS)
                             | {181, 191, 193, 197, 211, 223, 227})):
        raise AssertionError("MH04_FROZEN_SOURCE_OR_COHORT_DRIFT")


def events(seed: int, phase: str):
    if type(seed) is not int or seed not in SEEDS or phase not in OFFSETS:
        raise ValueError("MH04_UNFROZEN_SEED_PHASE")
    rng = random.Random(seed + OFFSETS[phase])
    pairs = [(cue, action) for cue in range(4) for action in range(3)]
    schedule = []
    for repeat in range(20):
        block = [(cue, action, repeat) for cue, action in pairs]
        rng.shuffle(block)
        schedule.extend(block)
    if len(schedule) != 240 or len(set(schedule)) != 240:
        raise AssertionError("MH04_SOURCE_SCHEDULE_BAD")
    return tuple(schedule)


def reward(mapping, cue, action):
    if cue not in range(4) or action not in range(3):
        raise ValueError("MH04_OUTCOME_INPUT_INVALID")
    return 1.0 if mapping[cue] == action else -1.0


def score4(rows4, mapping):
    if len(rows4) != 4 or len(mapping) != 4:
        raise ValueError("MH04_BAD_FOUR_CUE_READOUT")
    return sum(v32b.tolerant_action(tuple(float(x) for x in row)) ==
               mapping[cue] for cue, row in enumerate(rows4)) / 4.0


def stored_view(raw: bytes, target):
    before = raw
    report = bank.inspect_snapshot(raw)
    if raw != before or report["checkpoint_sha256"] != sha(raw):
        raise AssertionError("MH04_STORAGE_PROBE_MUTATED_CHECKPOINT")
    out = {
        "raw_sha256": sha(raw),
        "checkpoint_bytes": len(raw),
        "active_banks": list(report["active_bank_vector"]),
        "bank_ages": [list(x) for x in report["bank_ages"]],
        "update_calls": report["update_calls"],
    }
    for field, rows in report["readouts"].items():
        out[field] = {"a": score4(rows, A), "x": score4(rows, target),
                      "scores_sha256": sha_json(rows)}
    return out


def rust_readout(api, h, raw, target):
    """Check the MH03 full numeric offline active-readout against real Rust."""
    state = bank.inspect_snapshot(raw)
    fixed = state["readouts"]["active"]
    original = api.checkpoint(h)
    if original != raw:
        raise AssertionError("MH04_RUST_SNAPSHOT_CHANGED_BEFORE_READ")
    for cue in range(4):
        api.observe_one(h, cue)
        actual = api.native_scores(h)
        for action in range(3):
            if abs(actual[action] - fixed[cue][action]) > 1e-12:
                raise AssertionError("MH04_ACTUAL_RUST_AND_OFFLINE_ACTIVE_DRIFT")
    if api.checkpoint(h) != original:
        raise AssertionError("MH04_NUMERIC_READOUT_MUTATED_NATIVE")
    return stored_view(raw, target)


class FullHistory:
    """Phase-blind all-available-outcome mean control; capacity NOT matched."""
    def __init__(self):
        self.count = [[0] * 3 for _ in range(4)]
        self.total = [[0.0] * 3 for _ in range(4)]
        self.updates = 0

    def learn(self, cue, action, outcome):
        if (type(cue) is not int or cue not in range(4)
                or type(action) is not int or action not in range(3)
                or outcome not in (-1.0, 1.0)):
            raise ValueError("MH04_INVALID_FULL_HISTORY_OUTCOME")
        self.count[cue][action] += 1
        self.total[cue][action] += outcome
        self.updates += 1

    def scores(self, cue):
        return [self.total[cue][a] / self.count[cue][a]
                if self.count[cue][a] else 0.0 for a in range(3)]

    def checkpoint(self):
        return json.dumps({"count": self.count, "total": self.total,
                           "updates": self.updates}, sort_keys=True,
                          separators=(",", ":")).encode()


def arm_readout(arm, target):
    if isinstance(arm, mh02.Recency):
        prior = arm.checkpoint()
        rows = [arm.scores(cue) for cue in range(4)]
        if arm.checkpoint() != prior:
            raise AssertionError("MH04_RECENCY_READ_CHANGED")
    else:
        prior = arm.checkpoint()
        rows = [arm.scores(cue) for cue in range(4)]
        if arm.checkpoint() != prior:
            raise AssertionError("MH04_CONVENTIONAL_READ_CHANGED")
    return {"a": score4(rows, A), "x": score4(rows, target),
            "bytes": len(prior), "sha": sha(prior)}


def one_study(seed, label, target):
    api = mh02.v32e.API
    h = api.new()
    frozen = api.new()
    recency = mh02.Recency()
    history = FullHistory()
    sched_a, sched_x, sched_r = (events(seed, name)
                                 for name in ("A", "X", "return"))
    phases = ((sched_a, A, True), (sched_x, target, True))
    stages, raw_hex, reward_digest = {}, {}, {}
    cpu_native, cpu_recency, cpu_history = 0, 0, 0
    t_begin = time.process_time_ns()
    try:
        api.layout(h)
        api.layout(frozen)
        for p, (stream, mapping, is_initial) in enumerate(phases):
            rewards = []
            for cue, action, repeat in stream:
                rw = reward(mapping, cue, action)
                rewards.append(rw)
                t = time.process_time_ns()
                api.observe_one(h, cue)
                api.native_scores(h)
                api.feedback_one(h, action, rw, True)
                cpu_native += time.process_time_ns() - t
                t = time.process_time_ns()
                recency.learn(cue, action, rw)
                cpu_recency += time.process_time_ns() - t
                t = time.process_time_ns()
                history.learn(cue, action, rw)
                cpu_history += time.process_time_ns() - t
                api.observe_one(frozen, cue)
                api.native_scores(frozen)
                api.feedback_one(frozen, action, rw, is_initial)
            key = "a240" if is_initial else "x240"
            snap = api.checkpoint(h)
            raw_hex[key] = snap.hex()
            state = rust_readout(api, h, snap, target)
            stages[key] = {"native": state, "recency": arm_readout(recency, target),
                           "full_history": arm_readout(history, target)}
            reward_digest[key] = sha_json(rewards)
            if key == "x240":
                frozen_now = api.checkpoint(frozen)
                if frozen_now != frozen_before_x:
                    raise AssertionError("MH04_NEGATIVE_FROZEN_STATE_DRIFT")
                cold_stage = mh02.native_readout(api, h, target)
                cold = mh02.verify_cold("v32e", cold_stage, target)
            else:
                frozen_before_x = api.checkpoint(frozen)
        for index, (cue, action, repeat) in enumerate(sched_r[:48], 1):
            rw = reward(A, cue, action)
            t = time.process_time_ns()
            api.observe_one(h, cue)
            api.native_scores(h)
            api.feedback_one(h, action, rw, True)
            cpu_native += time.process_time_ns() - t
            t = time.process_time_ns()
            recency.learn(cue, action, rw)
            cpu_recency += time.process_time_ns() - t
            t = time.process_time_ns()
            history.learn(cue, action, rw)
            cpu_history += time.process_time_ns() - t
            if index in STOPS:
                snap = api.checkpoint(h)
                stages[f"return_a{index}"] = {
                    "native": rust_readout(api, h, snap, target),
                    "recency": arm_readout(recency, target),
                    "full_history": arm_readout(history, target)
                }
        frozen_x = mh02.native_readout(api, frozen, target)
        return {
            "seed": seed, "mapping": label, "world": list(target),
            "reward_sha256": reward_digest, "stages": stages,
            "original_stage_checkpoint_hex": raw_hex,
            "frozen_x240_a": frozen_x["a"], "frozen_x240_x": frozen_x["x"],
            "frozen_x240_unchanged": True,
            "cold_x240": cold,
            "resources": {"native_event_cpu_ns": cpu_native,
                          "recency_event_cpu_ns": cpu_recency,
                          "full_history_event_cpu_ns": cpu_history,
                          "parent_all_in_cpu_ns": time.process_time_ns() - t_begin}
        }
    finally:
        api.free(frozen)
        api.free(h)


def sham_for_seed(seed):
    api = mh02.v32e.API
    h = api.new()
    try:
        api.layout(h)
        for cue, action, repeat in events(seed, "A"):
            api.observe_one(h, cue)
            api.native_scores(h)
            api.feedback_one(h, action, reward(A, cue, action), True)
        baseline = rust_readout(api, h, api.checkpoint(h), A)
        table = {}
        for cue in range(4):
            for action in range(3):
                signs = [1.0] * 10 + [-1.0] * 10
                random.Random(seed + 44000 + cue * 101 + action * 17).shuffle(signs)
                table[(cue, action)] = tuple(signs)
        for cue, action, rep in events(seed, "X"):
            api.observe_one(h, cue)
            api.native_scores(h)
            api.feedback_one(h, action, table[(cue, action)][rep], True)
        after = rust_readout(api, h, api.checkpoint(h), A)
        return {"seed": seed,
                "a_before": baseline["active"]["a"],
                "a_after": after["active"]["a"],
                "switches": mh02.v32e.API.ledger(h)["switches"],
                "balanced": all(v.count(1.0) == v.count(-1.0) == 10
                                for v in table.values())}
    finally:
        api.free(h)


def grouped_result(rows, shams):
    grouped = {}
    for label in MAPS:
        selected = [x for x in rows if x["mapping"] == label]
        def ave(fn):
            return sum(fn(r) for r in selected) / len(selected)
        grouped[label] = {
            "native_x240_x": ave(lambda r: r["stages"]["x240"]["native"]["active"]["x"]),
            "bank0_x240_a": ave(lambda r: r["stages"]["x240"]["native"]["forced_bank0"]["a"]),
            "native_return_a8": ave(lambda r: r["stages"]["return_a8"]["native"]["active"]["a"]),
            "recency_return_a8": ave(lambda r: r["stages"]["return_a8"]["recency"]["a"]),
            "full_history_return_a8": ave(lambda r: r["stages"]["return_a8"]["full_history"]["a"]),
            "native_advantage_at8": ave(
                lambda r: r["stages"]["return_a8"]["native"]["active"]["a"] -
                max(r["stages"]["return_a8"]["recency"]["a"],
                    r["stages"]["return_a8"]["full_history"]["a"]))
        }
    storage = all(
        r["stages"]["a240"]["native"]["active"]["a"] >= .75 and
        r["stages"]["x240"]["native"]["active"]["x"] >= .75 and
        r["stages"]["x240"]["native"]["forced_bank0"]["a"] >= .75 and
        r["stages"]["a240"]["native"]["forced_bank0"]["a"] -
        r["stages"]["x240"]["native"]["forced_bank0"]["a"] <= .25
        for r in rows)
    shams_pass = all(s["a_before"] >= .75 and s["a_after"] >= .75
                     and s["balanced"] and s["switches"] == [0] * 8 for s in shams)
    return48 = all(r["stages"]["return_a48"]["native"]["active"]["a"] >= .75
                   for r in rows)
    cpu_nat = sum(r["resources"]["native_event_cpu_ns"] for r in rows)
    cpu_rec = sum(r["resources"]["recency_event_cpu_ns"] for r in rows)
    cpu_ratio = cpu_nat / max(1, cpu_rec)
    advantage = all(g["native_advantage_at8"] >= .05 for g in grouped.values())
    retrieval = bool(advantage and return48 and shams_pass and cpu_ratio <= 2.0)
    classification = ("MH04_PUBLIC_SYNTHETIC_DEV_SIGNAL" if retrieval and storage
        else "MH04_DEV_NO_GO_COST" if cpu_ratio > 2.0 else "MH04_DEV_NO_GO")
    return {"grouped": grouped, "storage_retained_all_cohorts": storage,
            "sham_all_pass": shams_pass, "return_a48_all_pass": return48,
            "native_advantage_both_maps": advantage,
            "native_cpu_over_recency_event_cpu": cpu_ratio,
            "retrieval_dev_gate": retrieval,
            "classification": classification,
            "storage_classification": ("MH04_DEV_STORAGE_RETAINED" if storage
                                       else "MH04_DEV_STORAGE_NOT_RETAINED")}


def main():
    source_guard()
    rows = [one_study(seed, label, target) for label, target in MAPS.items()
            for seed in SEEDS]
    shams = [sham_for_seed(seed) for seed in SEEDS]
    result = grouped_result(rows, shams)
    report = {"schema": "yggdrasil.mh04.synthetic_bank_retention.v1",
              "trial_identity": TRIAL, "original_source_first_use": False,
              "public_synthetic_dev_only": True, "native_rust_modified": False,
              "scientific_gain_verified": False,
              "cohort_count": len(rows), "seed_set": list(SEEDS),
              "mappings": {k: list(v) for k, v in MAPS.items()},
              "original_native_rust_sha256": mh02.v32e.API.source_sha256,
              "native_binary_sha256": mh02.v32e.API.binary_sha256,
              "checkpoints_full_hex_preserved": True,
              "results": rows, "shams": shams, "assessment": result}
    print(json.dumps(report, sort_keys=True, separators=(",", ":"), allow_nan=False))


if __name__ == "__main__":
    main()
