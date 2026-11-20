"""MH05 first fresh synthetic source-only bank storage DEV after invalid MH04.

Original V32E model remains unchanged; forced banks are EVALUATOR-ONLY.
No MH04/F/G, MH01 or MH02 old worlds or seeds are replayed.
"""
from __future__ import annotations

import json
import random
import time

from research import mh04_native_bank_retention as old
from research import mh03_checkpoint_bank_readback as bank

A = old.A
SEEDS = (503, 509, 521, 523, 541)
MAPS = {"H": (0, 2, 1, 0), "I": (2, 0, 0, 0)}
TRIAL = "MH05-SYNTH-HI-503-509-521-523-541-20261120"
# The third field decides ONLY whether the frozen negative arm learns;
# the actual V32E learner always receives genuine learning=True.
PHASES = (("a240", "A", True), ("x240", "X", False))
OFFSETS = {"A": 54000, "X": 64000}
PREREG = "47eda2556e72732c755988ef88c3d1adafe91e69"
PARENT = "3b6f11b4fb18ceb2616956a0bf80d3f15e583531"


def source_guard():
    old.source_guard()  # exactly the unchanged original V32E and MH03 source
    assert PHASES == (("a240", "A", True), ("x240", "X", False))
    assert SEEDS == (503, 509, 521, 523, 541)
    assert MAPS == {"H": (0, 2, 1, 0), "I": (2, 0, 0, 0)}
    forbidden = (set(old.SEEDS) | set(old.mh02.SEEDS) |
                 set(old.mh02.v32c.SEEDS) |
                 {181, 191, 193, 197, 211, 223, 227})
    if (set(SEEDS) & forbidden or len(set(MAPS.values())) != 2
            or any(m == A or m in old.MAPS.values() or
                   m in (old.mh02.v32c.B, old.mh02.v32c.C)
                   for m in MAPS.values())):
        raise AssertionError("MH05_CONSUMED_SOURCE_OR_WORLD")
    if (bank.SOURCE_BLOB != "85237dcc82905e05a273b11023b5be5db722726e"
            or bank.SIZE != 2264):
        raise AssertionError("MH05_ORIGINAL_NATIVE_CHECKPOINT_DRIFT")


def schedule(seed: int, phase: str):
    if type(seed) is not int or seed not in SEEDS or phase not in OFFSETS:
        raise ValueError("MH05_UNFROZEN_COHORT")
    rng = random.Random(seed + OFFSETS[phase])
    pairs = [(cue, action) for cue in range(4) for action in range(3)]
    rows = []
    for repeat in range(20):
        block = [(cue, action, repeat) for cue, action in pairs]
        rng.shuffle(block)
        rows += block
    if len(rows) != 240 or len(set(rows)) != 240:
        raise AssertionError("MH05_BAD_PUBLIC_SCHEDULE")
    return tuple(rows)


def reward(mapping, cue, action):
    return 1.0 if mapping[cue] == action else -1.0


def one_study(seed, name, world):
    api = old.mh02.v32e.API
    learner, frozen = api.new(), api.new()
    recency, history = old.mh02.Recency(), old.FullHistory()
    stages, raw, stream_shas = {}, {}, {}
    cpu_native = cpu_recency = cpu_full = 0
    try:
        api.layout(learner)
        api.layout(frozen)
        last_frozen_checkpoint = None
        cold = None
        for stage, phase, frozen_learning in PHASES:
            mapping = A if phase == "A" else world
            stream = schedule(seed, phase)
            rewards = []
            for cue, action, rep in stream:
                rw = reward(mapping, cue, action)
                rewards.append(rw)
                start = time.process_time_ns()
                api.observe_one(learner, cue)
                api.native_scores(learner)
                api.feedback_one(learner, action, rw, True)
                cpu_native += time.process_time_ns() - start
                start = time.process_time_ns()
                recency.learn(cue, action, rw)
                cpu_recency += time.process_time_ns() - start
                start = time.process_time_ns()
                history.learn(cue, action, rw)
                cpu_full += time.process_time_ns() - start
                api.observe_one(frozen, cue)
                api.native_scores(frozen)
                api.feedback_one(frozen, action, rw, frozen_learning)
            snap = api.checkpoint(learner)
            assert len(snap) == 2264
            raw[stage] = snap.hex()
            stream_shas[stage] = old.sha_json(rewards)
            native = old.rust_readout(api, learner, snap, world)
            stages[stage] = {"native": native,
                             "recency": old.arm_readout(recency, world),
                             "full_history": old.arm_readout(history, world)}
            frozen_snapshot = api.checkpoint(frozen)
            if stage == "a240":
                last_frozen_checkpoint = frozen_snapshot
            elif stage == "x240":
                if frozen_snapshot != last_frozen_checkpoint:
                    raise AssertionError("MH05_FROZEN_X_UPDATES_DETECTED")
                child = old.mh02.native_readout(api, learner, world)
                cold = old.mh02.verify_cold("v32e", child, world)
            else:
                raise AssertionError("MH05_UNDECLARED_PHASE")
        if set(stages) != {"a240", "x240"} or cold is None:
            raise AssertionError("MH05_STAGE_OR_COLD_NOT_EXECUTED")
        return {
            "seed": seed, "mapping": name, "world": list(world),
            "full_original_checkpoint_hex": raw,
            "reward_sign_sha256": stream_shas,
            "stages": stages, "cold_x240": cold,
            "frozen_x240_same_checkpoint": True,
            "resources": {"native_event_cpu_ns": cpu_native,
                          "recency_event_cpu_ns": cpu_recency,
                          "full_history_event_cpu_ns": cpu_full}
        }
    finally:
        api.free(frozen)
        api.free(learner)


def sham(seed):
    """Independent phase-blind +/- balanced false-world reward stream."""
    api = old.mh02.v32e.API
    h = api.new()
    try:
        api.layout(h)
        for cue, action, repeat in schedule(seed, "A"):
            api.observe_one(h, cue)
            api.native_scores(h)
            api.feedback_one(h, action, reward(A, cue, action), True)
        before = old.rust_readout(api, h, api.checkpoint(h), A)
        table = {}
        for cue in range(4):
            for action in range(3):
                signs = [1.0] * 10 + [-1.0] * 10
                random.Random(seed + 74000 + cue*101 + action*17).shuffle(signs)
                table[(cue, action)] = tuple(signs)
        assert all(v.count(-1.0) == v.count(1.0) == 10
                   for v in table.values())
        for cue, action, repeat in schedule(seed, "X"):
            api.observe_one(h, cue)
            api.native_scores(h)
            api.feedback_one(h, action, table[(cue, action)][repeat], True)
        after = old.rust_readout(api, h, api.checkpoint(h), A)
        switches = api.ledger(h)["switches"]
        return {"seed": seed, "a_before": before["active"]["a"],
                "a_after": after["active"]["a"],
                "switches": switches, "balanced": True,
                "checkpoint_sha": after["raw_sha256"]}
    finally:
        api.free(h)


def summarize(rows, shams):
    g = {}
    for key in MAPS:
        items = [r for r in rows if r["mapping"] == key]
        def avg(f):
            return sum(f(r) for r in items)/len(items)
        g[key] = {
            "pre_a_native_a": avg(lambda r: r["stages"]["a240"]["native"]["active"]["a"]),
            "post_x_native_x": avg(lambda r: r["stages"]["x240"]["native"]["active"]["x"]),
            "post_x_native_a": avg(lambda r: r["stages"]["x240"]["native"]["active"]["a"]),
            "post_x_stored_bank0_a": avg(lambda r: r["stages"]["x240"]["native"]["forced_bank0"]["a"]),
            "post_x_stored_bank1_a": avg(lambda r: r["stages"]["x240"]["native"]["forced_bank1"]["a"]),
            "post_x_recency_x": avg(lambda r: r["stages"]["x240"]["recency"]["x"]),
            "post_x_full_history_x": avg(lambda r: r["stages"]["x240"]["full_history"]["x"]),
        }
    null_pass = all(s["balanced"] and s["a_before"] >= .75
                    and s["a_after"] >= .75
                    and s["switches"] == [0]*8 for s in shams)
    storage = all(
        row["stages"]["a240"]["native"]["active"]["a"] >= .75
        and row["stages"]["x240"]["native"]["active"]["x"] >= .75
        and row["stages"]["x240"]["native"]["forced_bank0"]["a"] >= .75
        and (row["stages"]["a240"]["native"]["forced_bank0"]["a"] -
             row["stages"]["x240"]["native"]["forced_bank0"]["a"]) <= .25
        for row in rows) and null_pass
    total_nat = sum(r["resources"]["native_event_cpu_ns"] for r in rows)
    total_rec = sum(r["resources"]["recency_event_cpu_ns"] for r in rows)
    ratio = total_nat/max(total_rec, 1)
    return {
        "grouped": g, "storage_retained_all_ten": storage,
        "sham_all_pass": null_pass,
        "native_to_recency_event_cpu_ratio": ratio,
        "storage_class": ("MH05_DEV_STORAGE_RETAINED" if storage else
                          "MH05_DEV_STORAGE_NOT_RETAINED"),
        "cost_class": ("MH05_DEV_COST_NO_GO" if ratio > 2.0 else
                        "MH05_DEV_COST_WITHIN_CAP"),
        "scientific_gain_verified": False
    }


def main():
    source_guard()
    studies = [one_study(seed, name, world) for name, world in MAPS.items()
               for seed in SEEDS]
    shams = [sham(seed) for seed in SEEDS]
    summary = summarize(studies, shams)
    data = {"schema": "yggdrasil.mh05.fresh_bank_storage.dev.v1",
            "trial_id": TRIAL, "prior_mh04_cohort_invalid_consumed": True,
            "synthetic_only": True, "protected_original_source_first_use": False,
            "native_rust_changed": False, "scientific_gain_verified": False,
            "seed_set": list(SEEDS),
            "mappings": {k: list(v) for k,v in MAPS.items()},
            "original_rust_source_sha256": old.mh02.v32e.API.source_sha256,
            "binary_sha256": old.mh02.v32e.API.binary_sha256,
            "results": studies, "shams": shams, "summary": summary}
    print(json.dumps(data, sort_keys=True, separators=(",", ":"),
                     allow_nan=False))


if __name__ == "__main__":
    main()
