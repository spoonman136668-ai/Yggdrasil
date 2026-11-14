"""AAI-04R1 preregistered four-family, two-step causal benchmark. Synthetic research only."""
import hashlib
import json
import math
import random
import sys
import time

PREREG = "d9b8d86593a23b32dcf87e74490fb65f5dae8e6c"
TRAIN = range(91000, 91512)
DEV = range(92000, 92256)
TRANSFER = range(93000, 93256)
NEGATIVE = range(94000, 94256)
MASKS = (1, 2, 4, 7)
PROBE_STATES = (0, 2, 5, 7)
ACTIONS = range(4)
PROBES = 2
CAPACITY = 4
DISTRACTORS = 32
FLIP_PROB = 0.35
BOOTSTRAP_SAMPLES = 1024
BOOTSTRAP_SEED = 10404


def h(seed, *parts):
    raw = ":".join(str(value) for value in (seed, *parts))
    return int.from_bytes(hashlib.sha256(raw.encode("utf-8")).digest()[:8], "big")


def rol3(state, shift):
    shift %= 3
    return ((state << shift) | (state >> (3 - shift))) & 7 if shift else state


def reverse3(state):
    return ((state & 1) << 2) | (state & 2) | ((state & 4) >> 2)


def transition(law, state, action):
    assert 0 <= law < 12 and 0 <= state < 8 and 0 <= action < 4
    family, variant = divmod(law, 3)
    if family == 0:
        return rol3(state, variant + 1) ^ MASKS[action]
    if family == 1:
        return (state + (variant + 1) * (action + 1)) & 7
    if family == 2:
        return (reverse3(state ^ MASKS[action]) + variant + action + 1) & 7
    return ((state * (2 * variant + 1)) & 7) ^ ((action + 2 * variant + 1) & 7)


def world(seed, transfer=False):
    family = (2 if transfer else 0) + h(seed, "family") % 2
    variant = h(seed, "variant") % 3
    return {"seed": seed, "context": seed % 16, "law": 3 * family + variant,
            "terminal_start": h(seed, "terminal_start") % 8,
            "terminal_target": h(seed, "terminal_target") % 8}


def observation_likelihood(observed, expected):
    bits = (observed ^ expected).bit_count()
    if bits == 0:
        return 1.0 - FLIP_PROB
    if bits == 1:
        return FLIP_PROB / 3.0
    return 0.0


def observe(w, state, action, index, sham=False):
    expected = transition(w["law"], state, action)
    if sham:
        # Independent fixed pseudo-law over both probes: misleading causal data
        # with nonzero support under the preregistered exact likelihood.
        pseudolaw = h(w["seed"], "sham_law") % 12
        pseudo_successor = transition(pseudolaw, state, action)
        if h(w["seed"], "sham_corrupt", index) % 10000 < 3500:
            observed = pseudo_successor ^ (1 << (h(w["seed"], "sham_flipbit", index) % 3))
        else:
            observed = pseudo_successor
    elif h(w["seed"], "corrupt", index) % 10000 < 3500:
        observed = expected ^ (1 << (h(w["seed"], "flipbit", index) % 3))
    else:
        observed = expected
    return {"kind": "do", "context": w["context"], "state": state,
            "action": action, "observed": observed, "t": index}


def passive_event(w, index):
    return {"kind": "passive", "context": w["context"],
            "state": h(w["seed"], "passive", index, "state") % 8,
            "action": h(w["seed"], "passive", index, "action") % 4,
            "observed": h(w["seed"], "passive", index, "observed") % 8,
            "t": PROBES + index}


def retain(memory, event, mode):
    memory.append(event)
    if len(memory) <= CAPACITY:
        return
    if mode == "recent":
        memory.pop(0)
    else:
        victim = min(range(len(memory)),
                     key=lambda i: (memory[i]["kind"] == "do", memory[i]["t"]))
        memory.pop(victim)
    assert len(memory) <= CAPACITY


def fit_tabular(worlds, scrambled=False):
    labels = [w["law"] for w in worlds]
    if scrambled:
        random.Random(10337).shuffle(labels)
    counts = [[[[1 for y in range(8)] for action in ACTIONS]
               for state in range(8)] for law in range(12)]
    for w, label in zip(worlds, labels):
        for step in range(PROBES):
            state, action = random_probe(w, step)
            e = observe(w, state, action, step)
            counts[label][state][action][e["observed"]] += 1
    return counts


def random_probe(w, step):
    return (PROBE_STATES[h(w["seed"], "random_state", step) % 4],
            h(w["seed"], "random_action", step) % 4)


def posterior(memory, mode="exact", table=None):
    weights = [1.0 / 12] * 12
    for e in memory:
        if e["kind"] != "do":
            continue
        for law in range(12):
            if mode == "exact":
                pred = transition(law, e["state"], e["action"])
                prob = observation_likelihood(e["observed"], pred)
            else:
                assert table is not None and mode == "tabular"
                row = table[law][e["state"]][e["action"]]
                prob = row[e["observed"]] / sum(row)
            weights[law] *= prob
        norm = sum(weights)
        assert norm > 0.0
        weights = [x / norm for x in weights]
    return weights


def two_step_reward(law, s0, target, plan):
    a1, a2 = plan
    mid = transition(law, s0, a1)
    final = transition(law, mid, a2)
    return 1.0 - (final ^ target).bit_count() / 3.0


def all_plan_rewards(w):
    return [[two_step_reward(law, w["terminal_start"], w["terminal_target"], (a1, a2))
             for law in range(12)] for a1 in ACTIONS for a2 in ACTIONS]


def best_plan(belief, plan_rewards):
    expected = [sum(p * r for p, r in zip(belief, row)) for row in plan_rewards]
    k = max(range(len(expected)), key=lambda i: expected[i])
    return (k // 4, k % 4), expected[k]


def query_score(belief, w, state, action, plan_rewards, mode):
    predictions = [transition(law, state, action) for law in range(12)]
    if mode == "utility":
        # Expected value of the optimal terminal plan after each possible observation.
        # Joint probability weights avoid unnecessary posterior normalization.
        total = 0.0
        for observed in range(8):
            joint = [belief[law] * observation_likelihood(observed, predictions[law])
                     for law in range(12)]
            total += max(sum(p * r for p, r in zip(joint, row))
                         for row in plan_rewards)
        return total
    assert mode == "eig"
    entropy = -sum(p * math.log2(p) for p in belief if p > 0.0)
    residual = 0.0
    for observed in range(8):
        joint = [belief[law] * observation_likelihood(observed, predictions[law])
                 for law in range(12)]
        mass = sum(joint)
        if mass <= 0:
            continue
        updated = [v / mass for v in joint]
        remaining = -sum(p * math.log2(p) for p in updated if p > 0)
        residual += mass * remaining
    return entropy - residual


def choose_probe(belief, w, mode, step, plan_rewards):
    if mode not in ("utility", "eig"):
        return random_probe(w, step)
    choices = [(query_score(belief, w, state, action, plan_rewards, mode),
                state, action)
               for state in PROBE_STATES for action in ACTIONS]
    maximum = max(v for v, state, action in choices)
    # Stable tie-breaking never consults the world law or future probe outcome.
    return next((state, action) for v, state, action in choices
                if v >= maximum - 1e-12)


def run_arm(w, mode, table=None):
    plan_rewards = all_plan_rewards(w)
    if mode == "expert":
        plan, _ = best_plan([int(law == w["law"]) for law in range(12)],
                            plan_rewards)
        return {"reward": two_step_reward(w["law"], w["terminal_start"],
                                          w["terminal_target"], plan),
                "retained_do": 0, "probe_count": 0}
    memory = []
    for step in range(0 if mode == "no_probe" else PROBES):
        inference = "tabular" if mode in ("tabular", "shuffled") else "exact"
        belief = posterior(memory, inference, table)
        state, action = choose_probe(belief, w, mode, step, plan_rewards)
        retain(memory, observe(w, state, action, step, sham=mode == "sham"), mode)
    for i in range(DISTRACTORS):
        retain(memory, passive_event(w, i), mode)
    inference = "tabular" if mode in ("tabular", "shuffled") else "exact"
    belief = posterior(memory, inference, table)
    plan, _ = best_plan(belief, plan_rewards)
    return {"reward": two_step_reward(w["law"], w["terminal_start"],
                                     w["terminal_target"], plan),
            "retained_do": sum(e["kind"] == "do" for e in memory),
            "probe_count": 0 if mode == "no_probe" else PROBES}


def audit():
    assert len(set(TRAIN) | set(DEV) | set(TRANSFER) | set(NEGATIVE)) == 1280
    for first in range(12):
        for second in range(first + 1, 12):
            assert any(transition(first, state, act) != transition(second, state, act)
                       for state in range(8) for act in ACTIONS), (first, second)
    for seed, transfer in ((82000, False), (83000, True), (84000, True)):
        w = world(seed, transfer)
        other = dict(w, law=(w["law"] + 1) % 12)
        assert [passive_event(w, i) for i in range(DISTRACTORS)] == [
            passive_event(other, i) for i in range(DISTRACTORS)]
        assert (w["terminal_start"], w["terminal_target"]) == (
            other["terminal_start"], other["terminal_target"])
    assert all(w["law"] < 6 for w in map(world, TRAIN))
    assert all(world(s, True)["law"] >= 6 for s in TRANSFER)
    assert all(world(s, True)["law"] >= 6 for s in NEGATIVE)
    for outcome in range(8):
        assert abs(sum(observation_likelihood(v, outcome) for v in range(8)) - 1) < 1e-12
    # Use only reserved non-evaluation diagnostic worlds before first use.
    for seed in range(99000, 99032):
        w = world(seed, transfer=True)
        sham = []
        for step in range(PROBES):
            state, action = random_probe(w, step)
            sham.append(observe(w, state, action, step, sham=True))
        assert abs(sum(posterior(sham)) - 1.0) < 1e-12
    return True


def cohort(seeds, transfer, methods, models):
    by_method = {m: {"total_reward": 0.0, "retained_do": 0, "probes": 0}
                 for m in methods}
    records = []
    for seed in seeds:
        w = world(seed, transfer)
        scores = {}
        for method in methods:
            result = run_arm(w, method, models.get(method))
            by_method[method]["total_reward"] += result["reward"]
            by_method[method]["retained_do"] += result["retained_do"]
            by_method[method]["probes"] += result["probe_count"]
            scores[method] = round(result["reward"], 10)
        records.append((seed, scores))
    count = len(seeds)
    stats = {
        name: {"n": count, "mean_reward": round(row["total_reward"] / count, 8),
               "mean_retained_do": row["retained_do"] / count,
               "mean_probes": row["probes"] / count}
        for name, row in by_method.items()
    }
    return stats, records


def bootstrap_paired(records, first, second):
    differences = [scores[first] - scores[second] for seed, scores in records]
    n = len(differences)
    rng = random.Random(BOOTSTRAP_SEED)
    means = sorted(sum(differences[rng.randrange(n)] for _ in range(n)) / n
                   for _ in range(BOOTSTRAP_SAMPLES))
    return [round(means[25], 8), round(means[998], 8)]


def evaluate():
    started = time.perf_counter()
    assert audit()
    training = [world(s) for s in TRAIN]
    table = fit_tabular(training)
    shuffled = fit_tabular(training, scrambled=True)
    restored = json.loads(json.dumps({"tabular": table, "shuffled": shuffled}))
    assert restored == {"tabular": table, "shuffled": shuffled}
    methods = ("utility", "eig", "random", "no_probe", "tabular", "recent", "expert")
    models = {"tabular": table, "shuffled": shuffled}
    dev, dev_rows = cohort(DEV, False, methods, models)
    transfer, transfer_rows = cohort(TRANSFER, True, methods, models)
    negative, negative_rows = cohort(NEGATIVE, True,
                                     ("no_probe", "shuffled", "sham"), models)
    d = lambda field: dev[field]["mean_reward"]
    t = lambda field: transfer[field]["mean_reward"]
    n = lambda field: negative[field]["mean_reward"]
    delta = {
        "dev_utility_minus_no_probe": round(d("utility") - d("no_probe"), 8),
        "dev_utility_minus_random": round(d("utility") - d("random"), 8),
        "dev_expert_minus_utility": round(d("expert") - d("utility"), 8),
        "transfer_expert_minus_utility": round(t("expert") - t("utility"), 8),
        "transfer_utility_minus_no_probe": round(t("utility") - t("no_probe"), 8),
        "negative_shuffled_minus_no_probe": round(n("shuffled") - n("no_probe"), 8),
        "negative_sham_minus_no_probe": round(n("sham") - n("no_probe"), 8),
    }
    checks = {
        "audit": True, "cold_restore": True, "memory_cap": True,
        "utility_dev_min": d("utility") >= .53,
        "utility_dev_max": d("utility") <= .91,
        "dev_expert_headroom": delta["dev_expert_minus_utility"] >= .05,
        "transfer_expert_headroom": delta["transfer_expert_minus_utility"] >= .05,
        "dev_intervention_value": delta["dev_utility_minus_no_probe"] >= .035,
        "transfer_intervention_value": delta["transfer_utility_minus_no_probe"] >= .02,
        "dev_informative_vs_random": delta["dev_utility_minus_random"] >= .005,
        "negative_shuffled": delta["negative_shuffled_minus_no_probe"] <= .06,
        "negative_sham": delta["negative_sham_minus_no_probe"] <= .06,
    }
    receipt = {"dev": dev_rows, "transfer": transfer_rows,
               "negative": negative_rows}
    fingerprint = hashlib.sha256(json.dumps(receipt, sort_keys=True,
                                             separators=(",", ":")).encode()).hexdigest()
    return {
        "schema": "yggdrasil.aai04r1.benchmark-admission-result.v1",
        "prereg_commit": PREREG,
        "classification": "BENCHMARK_ADMITTED_DEV_CANDIDATE" if all(checks.values())
                          else "BENCHMARK_REJECTED_VALID_NEGATIVE",
        "train": {"n": len(training), "two_probe_training_events": 2 * len(training),
                  "families": [0, 1]},
        "cohorts": {"dev": dev, "transfer": transfer, "negative": negative},
        "checks": checks, "deltas": delta,
        "paired_bootstrap_95pct": {
            "dev_utility_vs_random": bootstrap_paired(dev_rows, "utility", "random"),
            "dev_utility_vs_no_probe": bootstrap_paired(dev_rows, "utility", "no_probe"),
            "transfer_utility_vs_random": bootstrap_paired(transfer_rows, "utility", "random"),
            "transfer_utility_vs_no_probe": bootstrap_paired(transfer_rows, "utility", "no_probe"),
        },
        "predictions_sha256": fingerprint,
        "cost": {"probe_budget": PROBES, "passive_events": DISTRACTORS,
                 "memory_slots": CAPACITY, "two_step_plans": 16, "paid_api_calls": 0},
        "limitations": "Synthetic known twelve-law catalog gives exact Bayes structural prior, including unseen fitting families. Benchmark-only; does not demonstrate a novel model, autonomous association, AGI, or generalization to arbitrary new causal structures.",
        "integration": "NONE", "elapsed_seconds": round(time.perf_counter() - started, 6),
    }


if __name__ == "__main__":
    result = evaluate()
    print(json.dumps(result, indent=2, sort_keys=True))
