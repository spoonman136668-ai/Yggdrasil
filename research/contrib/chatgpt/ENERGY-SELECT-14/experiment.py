#!/usr/bin/env python3
"""ENERGY-SELECT-14: frozen source-free public-action tournament vs matched selectors.

Only synthetic categorical consequences. No Yggdrasil-native model, runner or protected source.
"""
import argparse
import hashlib
import json
import math
import os
import subprocess
import sys
import tempfile
import time
from pathlib import Path

SEEDS = [97711, 97717, 97729, 97731, 97747, 97753, 97767, 97773, 97783, 97789, 97807, 97813]
SCENARIOS = ("NULL", "SINGLE_REWIRE", "OUT_FAMILY_DOUBLE")
POLICIES = ("tournament", "bayesian_information_gain", "round_robin", "random")
ROWS, K, OLD_N, BUDGET, HELD_N = 12, 6, 6, 24, 96


def bits(*parts):
    msg = ":".join(map(str, parts)).encode("ascii")
    return int.from_bytes(hashlib.sha256(msg).digest()[:8], "big")


def preferred_old(seed, scenario, row):
    return bits(seed, scenario, "prefer", row) % K


def draw(seed, scenario, phase, row, ordinal, preferred):
    key = bits(seed, scenario, phase, row, ordinal)
    if key < ((1 << 64) * 110 // 125):
        return preferred
    return [v for v in range(K) if v != preferred][bits(seed, scenario, phase, row, ordinal, "tail") % (K - 1)]


def make_world(seed, scenario):
    old_target = [preferred_old(seed, scenario, row) for row in range(ROWS)]
    new_target = old_target.copy()
    if scenario != "NULL":
        first = bits(seed, scenario, "changed1") % ROWS
        changed = [first]
        if scenario == "OUT_FAMILY_DOUBLE":
            second = (first + 1 + bits(seed, scenario, "changed2") % (ROWS - 1)) % ROWS
            changed.append(second)
        for row in changed:
            options = [i for i in range(K) if i != old_target[row]]
            new_target[row] = options[bits(seed, scenario, "newtarget", row) % len(options)]
    old = [[0] * K for _ in range(ROWS)]
    held = []
    for row in range(ROWS):
        for i in range(OLD_N):
            old[row][draw(seed, scenario, "old", row, i, old_target[row])] += 1
        held.append([draw(seed, scenario, "held", row, i, new_target[row]) for i in range(HELD_N)])
    return old, old_target, new_target, held


def row_stats(old, new):
    n = sum(new)
    stay_a = [old[i] + 0.5 for i in range(K)]
    lb = math.lgamma(3.0) - math.lgamma(3.0 + n) - math.lgamma(9.0) + math.lgamma(9.0 + n)
    for i in range(K):
        lb += math.lgamma(0.5 + new[i]) - math.lgamma(0.5)
        lb -= math.lgamma(stay_a[i] + new[i]) - math.lgamma(stay_a[i])
    odds_log = lb - math.log(3.0)
    reset = 1 / (1 + math.exp(-odds_log))
    stay_p = [(stay_a[i] + new[i]) / (9.0 + n) for i in range(K)]
    reset_p = [(0.5 + new[i]) / (3.0 + n) for i in range(K)]
    mix = [(1 - reset) * stay_p[i] + reset * reset_p[i] for i in range(K)]
    def ent(p):
        return -sum(x * math.log(x) for x in p if x > 0)
    ig = ent(mix) - (1 - reset) * ent(stay_p) - reset * ent(reset_p)
    return {"reset": reset, "log_bf": lb, "mi": ig, "predict": mix}


def selector(policy, step, old, new, seed, scenario):
    if policy == "round_robin":
        return step % ROWS
    if policy == "random":
        return bits(seed, scenario, "randompolicy", step) % ROWS
    if policy == "tournament":
        unseen = [i for i in range(ROWS) if sum(new[i]) == 0]
        if unseen:
            return unseen[0]
        return max(range(ROWS), key=lambda i: (max(0.0, row_stats(old[i], new[i])["log_bf"]) + 0.001 / (1 + sum(new[i])), -i))
    if policy == "bayesian_information_gain":
        return max(range(ROWS), key=lambda i: (row_stats(old[i], new[i])["mi"], -i))
    raise ValueError(policy)


def score(p, outcomes):
    ss = sum(x * x for x in p)
    return sum(1.0 + ss - 2.0 * p[y] for y in outcomes)


def run_policy(seed, scenario, policy, old, old_target, new_target, held):
    start = time.process_time()
    wall_start = time.perf_counter()
    new = [[0] * K for _ in range(ROWS)]
    actions = []
    for step in range(BUDGET):
        row = selector(policy, step, old, new, seed, scenario)
        ordinal = sum(new[row])
        observation = draw(seed, scenario, "new", row, ordinal, new_target[row])
        new[row][observation] += 1
        actions.append([row, observation])
    stats = [row_stats(old[i], new[i]) for i in range(ROWS)]
    total = sum(score(stats[row]["predict"], held[row]) for row in range(ROWS))
    cpu_s = time.process_time() - start
    wall_s = time.perf_counter() - wall_start
    changed = [i for i in range(ROWS) if new_target[i] != old_target[i]]
    detected = [i for i in range(ROWS) if stats[i]["reset"] >= 0.8]
    return {"brier": total / (ROWS * HELD_N), "changed": changed, "detected": detected,
            "true_positive": sum(i in detected for i in changed),
            "false_positive": sum(i not in changed for i in detected),
            "intervention_count": sum(sum(r) for r in new),
            "new_row_counts": [sum(r) for r in new], "trace": actions,
            "cpu_s": cpu_s, "wall_s": wall_s}


def old_snapshot(old):
    return [[(c + 0.5) / 9.0 for c in row] for row in old]


def cold_check(path):
    data = json.loads(Path(path).read_text())
    for obj in data:
        if old_snapshot(obj["old"]) != obj["readout"]:
            print(json.dumps({"pass": False, "reason": "old readout mismatch"}))
            return 2
    print(json.dumps({"pass": True, "snapshots": len(data)}))
    return 0


def study(seeds):
    samples = []
    cold = []
    prior = {p: 0.0 for p in POLICIES}
    t0 = time.process_time()
    wall0 = time.perf_counter()
    for seed in seeds:
        for scenario in SCENARIOS:
            old, old_target, new_target, held = make_world(seed, scenario)
            readout = old_snapshot(old)
            cold.append({"old": old, "readout": readout})
            world = {"seed": seed, "scenario": scenario, "changed_rows": [i for i in range(ROWS) if old_target[i] != new_target[i]], "policies": {}}
            for policy in POLICIES:
                result = run_policy(seed, scenario, policy, old, old_target, new_target, held)
                world["policies"][policy] = result
                prior[policy] += result["cpu_s"]
            world["oracle_brier"] = sum(score([0.88 if i == new_target[row] else 0.024 for i in range(K)], held[row]) for row in range(ROWS)) / (ROWS * HELD_N)
            assert readout == old_snapshot(old)
            samples.append(world)
    with tempfile.TemporaryDirectory(prefix="energy14-cold-") as temp:
        path = Path(temp) / "old.json"
        path.write_text(json.dumps(cold))
        proc = subprocess.run([sys.executable, str(Path(__file__).resolve()), "--cold-check", str(path)], capture_output=True, text=True, check=True)
        cold_status = json.loads(proc.stdout)
    summary = {}
    for p in POLICIES:
        arms = [w["policies"][p] for w in samples]
        summary[p] = {"brier": sum(x["brier"] for x in arms) / len(arms),
                      "family_brier": {s: sum(w["policies"][p]["brier"] for w in samples if w["scenario"] == s) / len(seeds) for s in SCENARIOS},
                      "changed_row_detection": sum(x["true_positive"] for x in arms) / sum(len(x["changed"]) for x in arms),
                      "null_world_false_alert_rate": sum(w["policies"][p]["false_positive"] > 0 for w in samples if w["scenario"] == "NULL") / len(seeds),
                      "cpu_s": prior[p]}
    best = min((summary[x]["brier"], x) for x in POLICIES if x != "tournament")
    cand = summary["tournament"]
    scenario_wins = all(cand["family_brier"][s] <= min(summary[p]["family_brier"][s] for p in POLICIES if p != "tournament") for s in SCENARIOS)
    good = ((best[0] - cand["brier"]) >= 0.010 and scenario_wins and cand["changed_row_detection"] >= 0.80 and cand["null_world_false_alert_rate"] <= 0.05 and cold_status["pass"])
    return {"schema": "yggdrasil.energy-select14-result.v1", "experiment_id": "ENERGY-SELECT-14", "seeds": seeds, "families": list(SCENARIOS),
            "source_free": True, "n_worlds": len(samples), "old_observations": len(samples)*ROWS*OLD_N,
            "new_observations_per_policy": len(samples)*BUDGET, "held_events": len(samples)*ROWS*HELD_N,
            "summary": summary, "oracle_brier": sum(w["oracle_brier"] for w in samples)/len(samples),
            "best_control": {"policy": best[1], "brier": best[0]}, "candidate_gain": best[0] - cand["brier"],
            "scenario_wins": scenario_wins, "cold_restore": cold_status, "cpu_whole_study_s": time.process_time()-t0, "wall_whole_study_s": time.perf_counter()-wall0,
            "decision": "DEV_SIGNAL_UNQUALIFIED" if good else "NEGATIVE_NO_GO", "per_world": samples,
            "science_gain_verified": False, "native_model_changed": False}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--cold-check", default=None)
    parser.add_argument("--smoke", action="store_true")
    parser.add_argument("--output", default=None)
    args = parser.parse_args()
    if args.cold_check:
        return cold_check(args.cold_check)
    result = study([97801] if args.smoke else SEEDS)
    payload = json.dumps(result, sort_keys=True, indent=2) + "\n"
    if args.output:
        Path(args.output).write_text(payload)
    else:
        print(json.dumps({"decision": result["decision"], "summary": result["summary"], "cold_restore": result["cold_restore"]}, sort_keys=True))
    return 0

if __name__ == "__main__":
    sys.exit(main())
