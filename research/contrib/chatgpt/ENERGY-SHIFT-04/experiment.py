#!/usr/bin/env python3
"""ENERGY-SHIFT-04: frozen source-free action-conditioned causal-shift experiment.

This tests local contradiction-gated repair against fully fitted adaptive
controls and a correctly specified oracle. NOT native Yggdrasil qualification.
"""
import argparse
import hashlib
import itertools
import json
import math
import platform
import random
import time

N, Q, ALPHA = 5, 0.85, 0.5
SEEDS = (92501, 92517, 92519, 92533, 92549, 92557,
         92569, 92581, 92593, 92603, 92611, 92627)
MODES = ("LOCAL_SWAP", "GLOBAL_REVERSE", "NULL")
ARMS = ("local_repair", "static_dirichlet", "decay_dirichlet",
        "reset_dirichlet", "change_point_bayes", "global_change_bayes",
        "oracle_structured_bayes")
SPEC = ("ENERGY-SHIFT-04-v1|states=5|actions=2|q=0.85|"
        "pre=4/state/action|adapt=3/state/action|held=128/state/action|"
        "modes=LOCAL_SWAP,GLOBAL_REVERSE,NULL|"
        "seeds=92501,92517,92519,92533,92549,92557,92569,"
        "92581,92593,92603,92611,92627|noise=uniform-other")


def stream(seed, mode, phase, action=-1, state=-1):
    key = f"ENERGY-SHIFT-04|{seed}|{mode}|{phase}|{action}|{state}"
    digest = hashlib.sha256(key.encode("ascii")).digest()
    return random.Random(int.from_bytes(digest[:16], "big"))


def successor(cycle):
    return tuple(cycle[(cycle.index(s) + 1) % N] for s in range(N))


def inverse(targets):
    return tuple(targets.index(s) for s in range(N))


def outcome(target, rng):
    if rng.random() < Q:
        return target
    return rng.choice([i for i in range(N) if i != target])


def generate(seed, mode):
    hidden = stream(seed, mode, "hidden")
    order = list(range(N))
    hidden.shuffle(order)
    base = successor(tuple(order))
    old = inverse(base)
    pair = tuple(sorted(hidden.sample(range(N), 2)))
    if mode == "NULL":
        new = old
    elif mode == "GLOBAL_REVERSE":
        new = base
    else:
        new = list(old)
        new[pair[0]], new[pair[1]] = new[pair[1]], new[pair[0]]
        new = tuple(new)
    pre, adapt, held = [], [], []
    for phase, count, target_set, dest in (
        ("pre", 4, (base, old), pre),
        ("adapt", 3, (base, new), adapt),
        ("held", 128, (base, new), held),
    ):
        for action in range(2):
            for state in range(N):
                r = stream(seed, mode, phase, action, state)
                dest.extend((state, action, outcome(target_set[action][state], r))
                            for _ in range(count))
    return pre, adapt, held, pair


def zeros():
    return [[[0] * N for _ in range(N)] for _ in range(2)]


def counts(tape):
    c = zeros()
    for s, a, target in tape:
        c[a][s][target] += 1
    return c


def add(x, y, wx=1.0, wy=1.0):
    return [[[wx * x[a][s][t] + wy * y[a][s][t]
              for t in range(N)] for s in range(N)] for a in range(2)]


def predict(row):
    values = [v + ALPHA for v in row]
    total = sum(values)
    return [v / total for v in values]


def predict_all(rows):
    return [[predict(rows[a][s]) for s in range(N)] for a in range(2)]


def log_dm(observed, prior):
    n = sum(observed)
    total = sum(prior)
    return (math.lgamma(total) - math.lgamma(total + n) +
            sum(math.lgamma(prior[i] + observed[i]) -
                math.lgamma(prior[i]) for i in range(N)))


def change_bf(before, after):
    prior = [ALPHA] * N
    post_prior = [ALPHA + x for x in before]
    return log_dm(after, prior) - log_dm(after, post_prior)


def posterior_change(bf, prior=0.25):
    odds_log = math.log(prior / (1 - prior)) + bf
    if odds_log > 40:
        return 1.0
    if odds_log < -40:
        return 0.0
    return 1.0 / (1.0 + math.exp(-odds_log))


def interpolate(a, b, w):
    return [(1 - w) * x + w * y for x, y in zip(a, b)]


def model(pre, adapt, arm):
    before, after = counts(pre), counts(adapt)
    pooled = add(before, after)
    historical = predict_all(before)
    changed_rows = [False] * N
    if arm == "oracle_structured_bayes":
        return oracle(pre, adapt), historical, changed_rows
    if arm == "static_dirichlet":
        return predict_all(pooled), historical, changed_rows
    if arm == "decay_dirichlet":
        return predict_all(add(before, after, .25, 1)), historical, changed_rows
    if arm == "reset_dirichlet":
        return [[predict(pooled[0][s]) for s in range(N)],
                [predict(after[1][s]) for s in range(N)]], historical, changed_rows
    bf = [change_bf(before[1][s], after[1][s]) for s in range(N)]
    global_weight = posterior_change(sum(bf), .5)
    result = [[], []]
    for a in range(2):
        for s in range(N):
            pooled_p = predict(pooled[a][s])
            if a == 0:
                result[a].append(pooled_p)
                continue
            reset_p = predict(after[a][s])
            if arm == "local_repair":
                w = posterior_change(bf[s], .25)
                changed_rows[s] = w >= .75
                result[a].append(reset_p if changed_rows[s] else pooled_p)
            elif arm == "change_point_bayes":
                result[a].append(interpolate(pooled_p, reset_p, posterior_change(bf[s], .25)))
            elif arm == "global_change_bayes":
                result[a].append(interpolate(pooled_p, reset_p, global_weight))
            else:
                raise ValueError(arm)
    return result, historical, changed_rows


def oracle(pre, adapt):
    # Correct synthetic-generator prior: each of 24 hidden directed cycles
    # has equal probability; modes have equal prior; swaps uniform given mode.
    hypotheses = []
    possible_cycles = [(0,) + p for p in itertools.permutations(range(1, N))]
    possible_pairs = list(itertools.combinations(range(N), 2))
    for cycle in possible_cycles:
        base = successor(cycle)
        old = inverse(base)
        for mode in MODES:
            pairs = possible_pairs if mode == "LOCAL_SWAP" else [None]
            for pair in pairs:
                new = list(old)
                if mode == "LOCAL_SWAP":
                    i, j = pair
                    new[i], new[j] = new[j], new[i]
                elif mode == "GLOBAL_REVERSE":
                    new = list(base)
                new = tuple(new)
                lp = -math.log(len(possible_cycles) * len(MODES) * len(pairs))
                for tape, action_targets in ((pre, (base, old)), (adapt, (base, new))):
                    for state, action, target in tape:
                        truth = action_targets[action][state]
                        lp += math.log(Q if target == truth else (1-Q)/(N-1))
                hypotheses.append((lp, (base, new)))
    maxlog = max(w for w, _ in hypotheses)
    weights = [math.exp(v-maxlog) for v, _ in hypotheses]
    denom = sum(weights)
    output = [[[0.0] * N for _ in range(N)] for _ in range(2)]
    for w, (_, targets) in zip(weights, hypotheses):
        for a in range(2):
            for s in range(N):
                target = targets[a][s]
                for t in range(N):
                    output[a][s][t] += w * (Q if t == target else (1-Q)/(N-1))
    return [[[v/denom for v in row] for row in arm] for arm in output]


def loss(p, target):
    return sum((v - (1 if i == target else 0))**2 for i, v in enumerate(p))


def sha_rows(rows):
    return hashlib.sha256(json.dumps(rows, separators=(",", ":")).encode()).hexdigest()


def trial(seed, mode):
    gen_cpu_start, gen_wall_start = time.process_time(), time.perf_counter()
    pre, adapt, held, swapped = generate(seed, mode)
    gen_cpu = time.process_time()-gen_cpu_start
    gen_wall = time.perf_counter()-gen_wall_start
    records = {}
    for arm in ARMS:
        begin_cpu, begin_wall = time.process_time(), time.perf_counter()
        predictions, historical, flags = model(pre, adapt, arm)
        snapshot = {"predictions": predictions, "historical": historical, "changed": flags}
        serialized = json.dumps(snapshot, sort_keys=True, separators=(",", ":"))
        restored = json.loads(serialized)
        stable = (restored == snapshot and restored["historical"] == historical)
        a0 = [loss(restored["predictions"][a][s], t)
              for s, a, t in held if a == 0]
        a1 = [loss(restored["predictions"][a][s], t)
              for s, a, t in held if a == 1]
        old_a0 = [loss(restored["historical"][a][s], t)
                  for s, a, t in held if a == 0]
        old_a1 = [loss(restored["historical"][a][s], t)
                  for s, a, t in held if a == 1]
        cpu = time.process_time() - begin_cpu
        wall = time.perf_counter() - begin_wall
        records[arm] = {"brier":(sum(a0)+sum(a1))/(len(a0)+len(a1)),
                        "action0_brier":sum(a0)/len(a0),
                        "action1_brier":sum(a1)/len(a1),
                        "historical_action0_brier":sum(old_a0)/len(old_a0),
                        "historical_action1_brier":sum(old_a1)/len(old_a1),
                        "cold_exact":stable, "snapshot_bytes":len(serialized.encode()),
                        "cpu_seconds_all_in":cpu+gen_cpu,
                        "wall_seconds_all_in":wall+gen_wall,
                        "changed_rows":flags}
    return {"seed":seed,"scenario":mode,"swapped_rows_test_only":swapped,
            "pre_sha256":sha_rows(pre),"adapt_sha256":sha_rows(adapt),
            "held_sha256":sha_rows(held),"train_count":len(pre)+len(adapt),
            "held_count":len(held),"records":records}


def summarize(worlds):
    averages = {}
    for arm in ARMS:
        averages[arm] = {}
        for field in ("brier","action0_brier","action1_brier",
                      "historical_action0_brier","historical_action1_brier",
                      "cpu_seconds_all_in","wall_seconds_all_in","snapshot_bytes"):
            v = [w["records"][arm][field] for w in worlds]
            averages[arm][field] = sum(v)/(len(v) if "seconds" not in field else 1)
    scenario = {}
    for mode in MODES:
        xs = [w for w in worlds if w["scenario"] == mode]
        scenario[mode] = {
            "brier_action1": {a:sum(w["records"][a]["action1_brier"] for w in xs)/len(xs)
                              for a in ARMS},
            "candidate_change_worlds":sum(any(w["records"]["local_repair"]["changed_rows"])
                                           for w in xs)}
    conventional = [x for x in ARMS if x not in ("local_repair","oracle_structured_bayes")]
    strongest = min(conventional, key=lambda a: averages[a]["action1_brier"])
    cand, ctrl = averages["local_repair"], averages[strongest]
    false_null = scenario["NULL"]["candidate_change_worlds"]
    old_cold = all(w["records"]["local_repair"]["cold_exact"] for w in worlds)
    protected_a0 = cand["action0_brier"] <= min(averages[a]["action0_brier"]
                                               for a in conventional) + .01
    baseline_gain = ctrl["action1_brier"] - cand["action1_brier"]
    cost = cand["cpu_seconds_all_in"]/max(ctrl["cpu_seconds_all_in"],1e-12)
    allowed = false_null == 0 and old_cold and protected_a0
    supported = allowed and (baseline_gain >= .01 or
                             (cost <= .5 and cand["action1_brier"] <= ctrl["action1_brier"]+.005))
    local_gain = scenario["LOCAL_SWAP"]["brier_action1"]["static_dirichlet"] - \
                 scenario["LOCAL_SWAP"]["brier_action1"]["local_repair"]
    mixed = local_gain >= .01
    return {"overall":averages,"by_scenario":scenario,"strongest_adaptive_control":strongest,
            "candidate_brier_gain_vs_control":baseline_gain,
            "candidate_cost_ratio_vs_control":cost,
            "null_false_change_worlds":false_null,
            "candidate_cold_retention_worlds":sum(w["records"]["local_repair"]["cold_exact"]
                                                   for w in worlds),
            "protected_action0_guard":protected_a0,
            "local_swap_gain_vs_static":local_gain,
            "classification":"SOURCE_FREE_SUPPORTED" if supported else
                             ("MIXED_NO_GO" if mixed else "NEGATIVE_NO_GO"),
            "native_scientific_qualified":False,"integration":"NONE"}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--smoke", action="store_true")
    ap.add_argument("--out", required=True)
    args = ap.parse_args()
    seeds = (92489,) if args.smoke else SEEDS
    start = time.process_time()
    worlds = [trial(seed, mode) for seed in seeds for mode in MODES]
    summary = summarize(worlds)
    report = {"schema":"yggdrasil.energy-shift04-result.v1",
              "phase":"SMOKE" if args.smoke else "PRIMARY",
              "data_spec_sha256":hashlib.sha256(SPEC.encode()).hexdigest(),
              "seeds":seeds,"worlds":worlds,"summary":summary,
              "source_free":True,"primary_worlds_consumed":not args.smoke,
              "python":platform.python_version(),"platform":platform.platform(),
              "process_cpu_seconds":time.process_time()-start}
    with open(args.out,"w",encoding="utf-8") as f:
        json.dump(report, f, sort_keys=True, indent=2)
        f.write("\n")
    print(json.dumps({"phase":report["phase"],"worlds":len(worlds),
                      "summary":summary,"cpu_total":report["process_cpu_seconds"]},
                     sort_keys=True))


if __name__ == "__main__":
    main()
