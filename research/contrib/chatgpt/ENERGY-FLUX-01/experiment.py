#!/usr/bin/env python3
"""ENERGY-FLUX-01 source-free finite-state causal flux study, stdlib only.
Source protocol: PREREG.md, committed before this file. No native checkpoint.
"""
import argparse
import hashlib
import json
import math
import random
import time

PRIMARY = [721101, 721127, 721147, 721169, 721181, 721199]
SCENARIOS = {"DRIFT": (0.8, 0.2), "REVERSIBLE": (0.5, 0.5),
             "ACTION_NULL": (0.8, 0.8)}
ARMS = ("conservative", "flux", "row_markov", "exact_flux_bayes",
        "action_blind", "no_learning")
N_TRAIN = 8
N_HELD_PER_STATE_ACTION = 256
STATE_COUNT = 4

def stream(seed, scenario, action, phase, state=-1):
    # Keep hidden outcome draws separate by action, state, phase, and family.
    key = f"energy-flux01|{seed}|{scenario}|{action}|{phase}|{state}"
    digest = hashlib.sha256(key.encode("ascii")).digest()
    return random.Random(int.from_bytes(digest[:16], "big"))

def outcome(state, q, rng):
    is_cw = int(rng.random() < q)
    target = (state + (1 if is_cw else -1)) % STATE_COUNT
    return target, is_cw

def beta_mean(successes, total):
    return (1.0 + successes) / (2.0 + total)

def build_predictors(tape):
    totals = [0, 0]
    clockwise = [0, 0]
    by_state_n = [[0] * STATE_COUNT for _ in range(2)]
    by_state_cw = [[0] * STATE_COUNT for _ in range(2)]
    for state, action, nxt in tape:
        assert nxt in ((state + 1) % STATE_COUNT, (state - 1) % STATE_COUNT)
        cw = int(nxt == ((state + 1) % STATE_COUNT))
        totals[action] += 1
        clockwise[action] += cw
        by_state_n[action][state] += 1
        by_state_cw[action][state] += cw
    flux = [beta_mean(clockwise[a], totals[a]) for a in range(2)]
    global_p = beta_mean(sum(clockwise), sum(totals))
    row = [[beta_mean(by_state_cw[a][s], by_state_n[a][s])
            for s in range(STATE_COUNT)] for a in range(2)]
    return {
        "conservative": lambda a, s: 0.5,
        "flux": lambda a, s: flux[a],
        "row_markov": lambda a, s: row[a][s],
        "exact_flux_bayes": lambda a, s: flux[a],
        "action_blind": lambda a, s: global_p,
        "no_learning": lambda a, s: 0.5,
    }, {"flux": flux, "row": row, "action_blind": global_p,
        "clockwise": clockwise, "totals": totals}

def world(seed, scenario):
    probs = SCENARIOS[scenario]     # Hidden source-only causal law
    tape = []
    for action in range(2):
        rng = stream(seed, scenario, action, "train")
        for _ in range(N_TRAIN):
            state = rng.randrange(STATE_COUNT)
            nxt, _ = outcome(state, probs[action], rng)
            tape.append((state, action, nxt))
    # Action-0 cold retention must survive action-1 fitting and JSON restore.
    stage0, meta0 = build_predictors([r for r in tape if r[1] == 0])
    p0 = stage0["flux"](0, 0)
    predictors, meta = build_predictors(tape)
    cold = json.loads(json.dumps(meta, sort_keys=True))
    retention = (p0 == predictors["flux"](0, 0) == cold["flux"][0])
    accum = {arm: {"brier_sum": 0.0, "correct": 0, "n": 0}
             for arm in ARMS}
    held_hash = hashlib.sha256()
    for action in range(2):
        for state in range(STATE_COUNT):
            rng = stream(seed, scenario, action, "held", state)
            for _ in range(N_HELD_PER_STATE_ACTION):
                nxt, label = outcome(state, probs[action], rng)
                held_hash.update(bytes((state, action, nxt)))
                for arm in ARMS:
                    p = predictors[arm](action, state)
                    scores = accum[arm]
                    scores["brier_sum"] += (p - label) ** 2
                    scores["correct"] += int((p > 0.5) == bool(label))
                    scores["n"] += 1
    for arm in ARMS:
        record = accum[arm]
        record["brier"] = record["brier_sum"] / record["n"]
        record["accuracy"] = record["correct"] / record["n"]
    action_gap = meta["flux"][0] - meta["flux"][1]
    return {
        "seed": seed, "scenario": scenario,
        "training_witnesses": tape,
        "held_sha256": held_hash.hexdigest(),
        "fit": meta,
        "cold_retention": retention,
        "chosen_clockwise_action": 0 if action_gap >= 0 else 1,
        "declares_action_effect": abs(action_gap) >= 0.30,
        "action_gap": action_gap,
        "scores": accum,
    }

def summarize(worlds):
    summary = {}
    for scenario in SCENARIOS:
        subset = [w for w in worlds if w["scenario"] == scenario]
        arms = {}
        for arm in ARMS:
            count = sum(w["scores"][arm]["n"] for w in subset)
            arms[arm] = {
                "brier": sum(w["scores"][arm]["brier_sum"]
                             for w in subset) / count,
                "accuracy": sum(w["scores"][arm]["correct"]
                                for w in subset) / count,
                "held_predictions": count,
            }
        summary[scenario] = {
            "arms": arms,
            "action_gap_declarations": sum(w["declares_action_effect"]
                                            for w in subset),
            "correct_clockwise_action": sum(
                w["chosen_clockwise_action"] == 0 for w in subset),
            "cold_retention_passes": sum(w["cold_retention"] for w in subset),
        }
    drift = summary["DRIFT"]
    other = [summary[s] for s in ("REVERSIBLE", "ACTION_NULL")]
    conservative_gain = drift["arms"]["conservative"]["brier"] - \
                        drift["arms"]["flux"]["brier"]
    exact_gain = drift["arms"]["exact_flux_bayes"]["brier"] - \
                 drift["arms"]["flux"]["brier"]
    row_gain = drift["arms"]["row_markov"]["brier"] - \
               drift["arms"]["flux"]["brier"]
    gates = {
        "cycle_affinity_counterexample": abs(4 * math.log(4)) > 5,
        "feasibility_brier_gain_ge_0_02": conservative_gain >= 0.02,
        "feasibility_policy_5_of_6": drift["correct_clockwise_action"] >= 5,
        "no_false_action_effect_declarations": all(
            s["action_gap_declarations"] == 0 for s in other),
        "cold_retention_18_of_18": sum(
            s["cold_retention_passes"] for s in summary.values()) == 18,
        "scientific_accuracy_gain_ge_0_01_vs_strongest": min(exact_gain, row_gain) >= 0.01,
    }
    return {"by_scenario": summary, "gates": gates,
            "drift_gain_vs_conservative_brier": conservative_gain,
            "drift_gain_vs_exact_bayes_brier": exact_gain,
            "drift_gain_vs_row_markov_brier": row_gain,
            "science_verdict": "DEVELOPMENT_NO_GO" if not gates[
                "scientific_accuracy_gain_ge_0_01_vs_strongest"] else "UNQUALIFIED",
            "note": "Full-process speedup alternative requires independent qualification; exact Bayesian control is algorithmically identical to pooled flux."}

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--smoke", action="store_true")
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    seeds = [721001] if a.smoke else PRIMARY
    start_wall = time.perf_counter()
    start_cpu = time.process_time()
    worlds = [world(seed, scenario) for seed in seeds for scenario in SCENARIOS]
    result = {
        "protocol": "ENERGY-FLUX-01",
        "phase": "SMOKE" if a.smoke else "PRIMARY",
        "seeds": seeds,
        "sources": "synthetic_source_free",
        "model_integration": "NONE",
        "witnesses_total": len(worlds) * 2 * N_TRAIN,
        "held_events_total": len(worlds) * 2 * STATE_COUNT * N_HELD_PER_STATE_ACTION,
        "worlds": worlds,
        "summary": summarize(worlds),
        "timing": {"wall_seconds": time.perf_counter() - start_wall,
                   "cpu_seconds": time.process_time() - start_cpu},
    }
    with open(a.out, "w", encoding="utf-8") as f:
        json.dump(result, f, sort_keys=True, indent=2)
        f.write("\n")
    print(json.dumps({k: result[k] for k in ("phase", "witnesses_total",
                                             "held_events_total", "summary", "timing")},
                     sort_keys=True, indent=2))

if __name__ == "__main__":
    main()
