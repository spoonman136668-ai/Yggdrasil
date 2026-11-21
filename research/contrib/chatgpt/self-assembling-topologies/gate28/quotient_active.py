"""Frozen G28 quotient active/forced/cold development diagnostic only."""
from __future__ import annotations

import hashlib
import json
import os
import subprocess
import sys
import tempfile
import time
from pathlib import Path

import core
import dense_reference as dense
import quotient_reference as quotient
import world

SEEDS = {
    "diagnostic_shifted": (900311, 900312),
    "stationary": (900321, 900322),
    "independent_noise": (900331, 900332),
}
ARMS = core.ARMS + ("dense_causal_reward", "dense_causal_nullmix") + quotient.ARMS
MODES = ("active", "forced")
POLICY_SEEDS = {arm: 28100 + 17 * i for i, arm in enumerate(core.ARMS)}


def require(ok, reason):
    if not ok:
        raise ValueError("QAC_" + reason)


def guard(seed, cohort):
    require(type(seed) is int and cohort in SEEDS and
            seed in SEEDS[cohort], "UNFROZEN_SEED")


def module(arm):
    require(arm in ARMS, "ARM")
    if arm in core.ARMS:
        return core
    return quotient if arm in quotient.ARMS else dense


def new(arm):
    mod = module(arm)
    return mod.new(POLICY_SEEDS[arm], arm) if mod is core else mod.new(arm)


def observe(mod, state, row, meter):
    if mod is core:
        mod.observe(state, row.context, row.action, row.consequence, meter)
    else:
        mod.observe(state, row.context, row.intermediates,
                    row.action, row.consequence, meter)


def digest(value):
    return hashlib.sha256(core.canonical(value)).hexdigest()


def source_function(mod, state):
    values = []
    work = 0
    for mask in (3, 19, 37, 51, 88, 171, 238):
        for action in range(13):
            meter = core.Work()
            values.append(mod.source_predict(
                state, core.as_bits(mask), action, meter))
            work += meter.count
    return digest(values), work


def path(root, arm, mode):
    require(arm in ARMS and mode in MODES, "STATE_KEY")
    return root / (arm + "." + mode + ".json")


def run_arm(w, root, phase, arm, mode):
    mod = module(arm)
    cpu = 0
    total_work = 0
    peak = 0
    start = time.process_time_ns()
    if phase == "A":
        state = new(arm)
        old_sig = None
    else:
        raw = path(root, arm, mode).read_bytes()
        state = mod.unpack(raw)
        require(mod.pack(state) == raw and state["arm"] == arm,
                "COLD_STATE_IDENTITY")
        old_sig, cost = source_function(mod, state)
        total_work += cost
    cpu += time.process_time_ns() - start
    expected = {"A": 0, "B": 96, "R": 160}[phase]
    require(state["step"] == expected, "COLD_ORDER")
    start_edits, start_attempts = state["edits"], state["attempts"]
    exposure = []
    reward = regret = 0
    preq = 0.0
    for step in range(96 if phase == "A" else 64):
        meter = core.Work()
        if phase == "A":
            row = w.source(step)
        else:
            context = w.public_context(phase, step)
            start = time.process_time_ns()
            action = (mod.choose(state, context, meter) if mode == "active"
                      else w.forced_action(phase, step))
            forecast = mod.predict(state, context, action, meter)
            cpu += time.process_time_ns() - start
            row = w.feedback(phase, step, action)
            require(row.context == context, "CONTEXT_PARITY")
            oracle = max(w.feedback(phase, step, a).consequence
                         for a in world.ACTIONS)
            reward += row.consequence
            regret += oracle - row.consequence
            preq += (forecast - row.consequence) ** 2
        exposure.append([list(row.context), list(row.intermediates),
                         row.action, row.consequence])
        start = time.process_time_ns()
        observe(mod, state, row, meter)
        cpu += time.process_time_ns() - start
        total_work += meter.count
        peak = max(peak, meter.count)
    require(state["step"] == {"A": 96, "B": 160, "R": 224}[phase],
            "EXPOSURE_COUNT")
    start = time.process_time_ns()
    if phase == "A":
        mod.seal_source(state)
    sig, cost = source_function(mod, state)
    total_work += cost
    require(old_sig is None or old_sig == sig, "SOURCE_FUNCTION_CHANGED")
    before = mod.pack(state)
    cpu += time.process_time_ns() - start
    common_loss = selected_loss = 0.0
    held_reward = 0
    if phase != "A":
        for i in range(32):
            ctx = w.held_context(phase, i)
            common = w.forced_action(phase, i)
            meter = core.Work()
            start = time.process_time_ns()
            chosen = mod.choose(state, ctx, meter)
            forecast = mod.predict(state, ctx, chosen, meter)
            common_forecast = mod.predict(state, ctx, common, meter)
            cpu += time.process_time_ns() - start
            chosen_row = w.held_query(phase, i, chosen)
            forced_row = w.held_query(phase, i, common)
            require(chosen_row.context == ctx and forced_row.context == ctx,
                    "HELD_CONTEXT")
            held_reward += chosen_row.consequence
            selected_loss += (forecast - chosen_row.consequence) ** 2
            common_loss += (common_forecast - forced_row.consequence) ** 2
            total_work += meter.count
            peak = max(peak, meter.count)
    start = time.process_time_ns()
    after = mod.pack(state)
    require(before == after, "HELD_MUTATION")
    require(len(after) <= core.MAX_STATE_BYTES and peak <= core.MAX_RULE_EVALS,
            "BUDGET")
    cpu += time.process_time_ns() - start
    path(root, arm, mode).write_bytes(after)
    result = {"step": state["step"], "source_function": sig,
              "source_digest": state["source"]["digest"],
              "state_sha256": hashlib.sha256(after).hexdigest(),
              "exposure_sha256": digest(exposure), "peak_rule_work": peak,
              "total_rule_work": total_work, "checkpoint_bytes": len(after),
              "model_cpu_ns": cpu, "edits": state["edits"] - start_edits,
              "attempts": state["attempts"] - start_attempts}
    if phase != "A":
        result.update({"held_reward": held_reward, "observed_reward": reward,
                       "regret": regret, "prequential_brier": round(preq / 64, 9),
                       "common_held_brier": round(common_loss / 32, 9),
                       "selected_held_brier": round(selected_loss / 32, 9)})
    return result


def child(root, seed, cohort, phase):
    guard(seed, cohort)
    require(root.is_dir() and phase in ("A", "B", "R"), "CHILD_REQUEST")
    w = world.HiddenWorld(seed, diagnostic=True, diagnostic_cohort=cohort)
    rows = {}
    for arm in ARMS:
        for mode in ("active",) if phase == "A" else MODES:
            rows[arm + "." + mode] = run_arm(w, root, phase, arm, mode)
        if phase == "A":
            path(root, arm, "forced").write_bytes(
                path(root, arm, "active").read_bytes())
            rows[arm + ".forced"] = dict(rows[arm + ".active"])
    require(len({rows[a + ".forced"]["exposure_sha256"] for a in ARMS}) == 1,
            "FORCED_EXPOSURE_MISMATCH")
    return {"seed": seed, "cohort": cohort, "phase": phase,
            "pid": os.getpid(), "rows": rows, "primary_scored": False}


def evaluate(seed, cohort):
    guard(seed, cohort)
    stages = {}
    with tempfile.TemporaryDirectory(prefix="g28-quotient-active-") as temp:
        for phase in ("A", "B", "R"):
            args = [sys.executable, "-B", str(Path(__file__).resolve()),
                    temp, str(seed), cohort, phase]
            result = subprocess.run(args, capture_output=True, text=True)
            require(result.returncode == 0, "CHILD_FAILED:" + result.stderr[-2500:])
            data = json.loads(result.stdout)
            require(data["seed"] == seed and data["cohort"] == cohort and
                    data["phase"] == phase and not data["primary_scored"],
                    "CHILD_IDENTITY")
            stages[phase] = data
        require(len({x["pid"] for x in stages.values()}) == 3, "NOT_COLD")
        for arm in ARMS:
            for mode in MODES:
                key = arm + "." + mode
                a = stages["A"]["rows"][key]
                for phase in ("B", "R"):
                    p = stages[phase]["rows"][key]
                    require(p["source_function"] == a["source_function"] and
                            p["source_digest"] == a["source_digest"],
                            "COLD_SOURCE_PARITY")
                raw = path(Path(temp), arm, mode).read_bytes()
                model = module(arm).unpack(raw)
                require(model["step"] == 224 and
                        hashlib.sha256(raw).hexdigest() ==
                        stages["R"]["rows"][key]["state_sha256"],
                        "FINAL_CHECKPOINT_CUSTODY")
    return {"seed": seed, "cohort": cohort, "distinct_processes": 3,
            "primary_scored": False,
            "phases": {k: v["rows"] for k, v in stages.items()}}


def score(records):
    expected = {(cohort, seed) for cohort, seeds in SEEDS.items()
                for seed in seeds}
    require(len(records) == len(expected) and
            {(r["cohort"], r["seed"]) for r in records} == expected,
            "WORLD_COVERAGE")
    require(all(r["distinct_processes"] == 3 and not r["primary_scored"]
                for r in records), "CUSTODY")
    means = {}
    for cohort in SEEDS:
        group = [r for r in records if r["cohort"] == cohort]
        means[cohort] = {
            phase: {
                key: {m: sum(r["phases"][phase][key][m] for r in group) / len(group)
                      for m in ("held_reward", "regret", "common_held_brier",
                                "edits", "attempts")}
                for key in (a + "." + mode for a in ARMS for mode in MODES)}
            for phase in ("B", "R")}
    shift = means["diagnostic_shifted"]
    controls = [arm for arm in ARMS if arm != "adaptive"]
    reward_gains = {
        arm: (shift["R"]["adaptive.active"]["held_reward"] -
              shift["R"][arm + ".active"]["held_reward"]) / 32
        for arm in controls}
    regret_gains = {
        arm: sum(shift[p][arm + ".active"]["regret"] -
                 shift[p]["adaptive.active"]["regret"] for p in ("B", "R"))
        for arm in controls}
    forced_gains = {
        arm: shift["R"][arm + ".forced"]["common_held_brier"] -
        shift["R"]["adaptive.forced"]["common_held_brier"] for arm in controls}
    stationary = means["stationary"]
    edits = sum(stationary[p]["adaptive.active"]["edits"] for p in ("B", "R"))
    attempts = sum(stationary[p]["adaptive.active"]["attempts"] for p in ("B", "R"))
    fraction = edits / attempts if attempts else 0
    noise = means["independent_noise"]["R"]["adaptive.forced"]["common_held_brier"]
    checks = {"R_reward": min(reward_gains.values()) >= .05,
              "BR_regret": min(regret_gains.values()) > 0,
              "R_forced_Brier": min(forced_gains.values()) >= 0,
              "stationary_edits": fraction <= .1, "noise": noise <= .27}
    return {"status": ("QAC_DIAGNOSTIC_TARGETS_MET_NOT_SCIENCE"
                       if all(checks.values()) else "QAC_DIAGNOSTIC_NO_GO"),
            "checks": checks, "worlds": len(records),
            "shifted_reward_gains": reward_gains, "shifted_regret_gains": regret_gains,
            "shifted_forced_brier_gains": forced_gains,
            "stationary_edit_fraction": fraction, "noise_R_forced_brier": noise,
            "means": means, "records": records, "primary_scored": False,
            "strongest_matched_control_adequacy": "UNVERIFIED",
            "scientific_gain_verified": False,
            "transient_full_process_memory_matched": False}


if __name__ == "__main__":
    require(len(sys.argv) == 5, "CHILD_ONLY")
    print(json.dumps(child(Path(sys.argv[1]), int(sys.argv[2]), sys.argv[3],
                           sys.argv[4]), sort_keys=True))
