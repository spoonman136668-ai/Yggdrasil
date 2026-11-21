"""NC2: fixed-share confidence recovery; isolated contributor diagnostics only."""
from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path

import core
import dense_reference as dense
import world

SCHEMA = "yggdrasil.gate28.NC2-checkpoint.v1"
HAZARD = 1 / 64
SEEDS = {
    "diagnostic_shifted": (900211, 900212, 900213, 900214),
    "stationary": (900221, 900222, 900223, 900224),
    "independent_noise": (900231, 900232, 900233, 900234),
}


def require(condition, reason):
    if not condition:
        raise ValueError("NC2_" + reason)


def mix(q, weight):
    require(0 <= q <= 1 and 0 <= weight <= 1, "PROBABILITY")
    return 0.5 + weight * (q - 0.5)


def advance(weight, q, y):
    require(type(y) is int and y in (0, 1), "PUBLIC_LABEL")
    require(HAZARD <= weight <= 1 - HAZARD and 0 <= q <= 1,
            "WEIGHT_OR_FORECAST")
    likelihood = q if y else 1 - q
    posterior = weight * likelihood / (weight * likelihood + (1 - weight) * 0.5)
    return HAZARD + (1 - 2 * HAZARD) * posterior


def pack(state, weight, source_weight):
    require(HAZARD <= weight <= 1 - HAZARD, "WEIGHT")
    require((state["source"] is None and source_weight is None) or
            (state["source"] is not None and source_weight is not None and
             HAZARD <= source_weight <= 1 - HAZARD), "SOURCE_WEIGHT")
    payload = {"schema": SCHEMA, "dense": json.loads(dense.pack(state)),
               "weight": weight, "source_weight": source_weight}
    raw = core.canonical(payload)
    wire = core.canonical({"payload": payload,
                           "sha256": hashlib.sha256(raw).hexdigest()})
    require(len(wire) <= core.MAX_STATE_BYTES, "CHECKPOINT_CAP")
    return wire


def unpack(wire):
    require(len(wire) <= core.MAX_STATE_BYTES, "CHECKPOINT_CAP")
    item = json.loads(wire)
    require(type(item) is dict and set(item) == {"payload", "sha256"},
            "CHECKPOINT_KEYS")
    payload = item["payload"]
    require(payload["schema"] == SCHEMA and hashlib.sha256(
        core.canonical(payload)).hexdigest() == item["sha256"], "DIGEST")
    state = dense.unpack(core.canonical(payload["dense"]))
    require(state["arm"] == "dense_causal_reward", "ARM")
    weight = payload["weight"]
    source_weight = payload["source_weight"]
    require(pack(state, weight, source_weight) == wire, "NONCANONICAL")
    return state, weight, source_weight


def source_signature(state, source_weight):
    values = []
    for mask in (3, 19, 88):
        for action in range(13):
            q = dense.source_predict(
                state, core.as_bits(mask), action, core.Work())
            values.append(round(mix(q, source_weight), 12))
    return hashlib.sha256(core.canonical(values)).hexdigest()


def evaluate(seed, cohort):
    """One forced-exposure world, shared raw fit, three calibration arms.

    Sharing is valid here only because the arms cannot change the raw fit or
    selected action. No active-learning or independent process-exit claim.
    """
    require(cohort in SEEDS and seed in SEEDS[cohort], "FROZEN_SEED")
    w = world.HiddenWorld(seed, diagnostic=True, diagnostic_cohort=cohort)
    state = dense.new("dense_causal_reward")
    weight = 0.5
    recent = []
    source_weight, source_digest = None, None
    peak, max_bytes = 0, 0
    phases = {}
    for phase in ("A", "B", "R"):
        rows = []
        for step in range(96 if phase == "A" else 64):
            row = (w.source(step) if phase == "A" else
                   w.feedback(phase, step, w.forced_action(phase, step)))
            meter = core.Work()
            q = dense.predict(state, row.context, row.action, meter)
            weight = advance(weight, q, row.consequence)
            likelihood = q if row.consequence else 1 - q
            recent.append(round(math.log(2 * likelihood), 9))
            recent = recent[-32:]
            dense.observe(state, row.context, row.intermediates,
                          row.action, row.consequence, meter)
            peak = max(peak, meter.count)
            rows.append([list(row.context), list(row.intermediates),
                         row.action, row.consequence])
        expected = {"A": 96, "B": 160, "R": 224}[phase]
        require(state["step"] == expected, "EXPOSURE_COUNT")
        if phase == "A":
            dense.seal_source(state)
            source_weight = weight
            source_digest = source_signature(state, source_weight)
        wire = pack(state, weight, source_weight)
        max_bytes = max(max_bytes, len(wire))
        state, weight, source_weight = unpack(wire)
        require(source_signature(state, source_weight) == source_digest,
                "SOURCE_FUNCTION")
        if phase != "A":
            sums = [0.0, 0.0, 0.0]
            reward = 0
            actions = []
            before = pack(state, weight, source_weight)
            rolling_weight = dense._null_weight(recent)
            for i in range(32):
                ctx = w.held_context(phase, i)
                action = w.forced_action(phase, i)
                meter = core.Work()
                q = dense.predict(state, ctx, action, meter)
                chosen = dense.choose(state, ctx, meter)
                predictions = (q, mix(q, rolling_weight), mix(q, weight))
                outcome = w.held_query(phase, i, action)
                selected = w.held_query(phase, i, chosen)
                require(outcome.context == ctx and selected.context == ctx,
                        "HELD_CONTEXT")
                for j, pred in enumerate(predictions):
                    sums[j] += (pred - outcome.consequence) ** 2
                reward += selected.consequence
                actions.append(chosen)
                peak = max(peak, meter.count)
            require(pack(state, weight, source_weight) == before,
                    "HELD_MUTATION")
            phases[phase] = {
                "brier": dict(zip(("dense", "NC1", "NC2"),
                                  [round(x / 32, 9) for x in sums])),
                "shared_selected_reward": reward,
                "shared_selected_action_sha256": hashlib.sha256(
                    core.canonical(actions)).hexdigest(),
                "public_rows_sha256": hashlib.sha256(
                    core.canonical(rows)).hexdigest(),
                "NC2_weight": round(weight, 9),
            }
    return {"cohort": cohort, "seed": seed, "phases": phases,
            "peak_rule_work": peak, "max_candidate_checkpoint_bytes": max_bytes,
            "source_function_parity": True, "primary_scored": False}


def score(records):
    expected = {(cohort, seed) for cohort, seeds in SEEDS.items()
                for seed in seeds}
    require(len(records) == len(expected) and
            {(r["cohort"], r["seed"]) for r in records} == expected,
            "TRIAL_COVERAGE")
    require(all(r["primary_scored"] is False and
                r["source_function_parity"] is True and
                r["peak_rule_work"] <= 8192 and
                r["max_candidate_checkpoint_bytes"] <= 16384
                for r in records), "RESOURCE_OR_PRIMARY_FENCE")
    means = {}
    for cohort in SEEDS:
        group = [r for r in records if r["cohort"] == cohort]
        means[cohort] = {
            phase: {arm: sum(r["phases"][phase]["brier"][arm]
                             for r in group) / len(group)
                    for arm in ("dense", "NC1", "NC2")}
            for phase in ("B", "R")
        }
    noise = means["independent_noise"]["R"]
    checks = {"noise_R": noise["NC2"] <= 0.270 and noise["NC2"] < noise["dense"]}
    for cohort in ("diagnostic_shifted", "stationary"):
        for phase in ("R", "BR"):
            ps = ("B", "R") if phase == "BR" else ("R",)
            delta = sum(means[cohort][p]["NC2"] - means[cohort][p]["dense"]
                        for p in ps) / len(ps)
            checks[cohort + "_" + phase] = delta <= 0.015
    checks["overall_NC1_improvement"] = sum(
        means[c][p]["NC2"] - means[c][p]["NC1"]
        for c in SEEDS for p in ("B", "R")) < 0
    checks["shared_action_policy"] = True
    checks["resource_and_snapshot"] = True
    return {"status": ("NC2_DIAGNOSTIC_TARGETS_MET_NOT_SCIENCE"
                       if all(checks.values()) else "NC2_DIAGNOSTIC_NO_GO"),
            "checks": checks, "cohort_means": means, "records": records,
            "worlds": len(records), "primary_scored": False,
            "scientific_gain_verified": False,
            "action_gain": "NOT_TESTED_SHARED_POLICY",
            "cold_process": "NOT_TESTED_SAME_PROCESS_SNAPSHOT",
            "next": "NO_PARAMETER_SWEEP_PENDING_INDEPENDENT_REVIEW"}
