"""AAI-06A frozen causal graph growth vs matched exhaustive MAP.
Contributor-only synthetic science; no Yggdrasil native integration.
"""
import hashlib
import itertools
import json
import math
import random
import time

PREREG = "71941d3d825050977ab5fb8a4d8dd6489d5bd546"
DEV = range(151000, 151032)
TRANSFER = range(152000, 152064)
NEGATIVE = range(153000, 153032)
INTERFERENCE = range(154000, 154032)
PAIR = tuple(itertools.combinations(range(5), 2))
PRIMITIVES = tuple((i, j, op) for i, j in PAIR for op in range(3))
MATCH = math.log(.92)
MISMATCH = math.log(.08)
CAP = 2
CANDIDATE_BEAM = 6
PROBES = 16
TASKS = 12
EPOCHS = 300
BOOTSTRAP = 1024


def h(seed, *parts):
    raw = ":".join(str(z) for z in (seed, *parts)).encode("utf-8")
    return int.from_bytes(hashlib.sha256(raw).digest()[:8], "big")


def bits(state, action):
    assert 0 <= state < 8 and 0 <= action < 4
    return tuple((state >> i) & 1 for i in range(3)) + tuple(
        (action >> i) & 1 for i in range(2))


def op(a, b, kind):
    if kind == 0:
        return a ^ b
    if kind == 1:
        return a & b
    return a | b


def primitive(index, input_bits):
    i, j, kind = PRIMITIVES[index]
    return op(input_bits[i], input_bits[j], kind)


def circuit(program, input_bits):
    first, second, root, bias = program
    return op(primitive(first, input_bits), primitive(second, input_bits), root) ^ bias


def world(seed, transfer=False):
    root = (1 + (h(seed, "root") % 2)) if transfer else 0
    circuits = tuple((
        h(seed, "a", bit) % 30,
        h(seed, "b", bit) % 30,
        root,
        h(seed, "bias", bit) % 2
    ) for bit in range(2))
    return {"seed": seed, "transfer": bool(transfer), "circuits": circuits}


def consequence(w, state, action):
    x = bits(state, action)
    return sum(circuit(w["circuits"][b], x) << b for b in range(2))


def observations(w):
    seed = w["seed"]
    ordered = sorted(range(8), key=lambda state: (h(seed, "state_order", state), state))
    train_states = ordered[:4]
    terminal_states = ordered[4:]
    pairs = sorted([(s, a) for s in train_states for a in range(4)],
                   key=lambda pair: (h(seed, "probe_order", pair[0], pair[1]), pair))
    observed = []
    for t, (state, action) in enumerate(pairs):
        result = consequence(w, state, action)
        for b in range(2):
            if h(seed, "noise", t, b) % 10000 < 800:
                result ^= (1 << b)
        observed.append((state, action, result))
    goals = [(terminal_states[t % 4], h(seed, "target", t) % 4)
             for t in range(TASKS)]
    assert len(observed) == PROBES
    assert len({(s, a) for s, a, _ in observed}) == PROBES
    assert not set(train_states).intersection(terminal_states)
    return observed, goals


def likelihood(yhat, y):
    return MATCH if yhat == y else MISMATCH


def score_program(program, dataset, bit):
    return sum(likelihood(circuit(program, x), y) for x, y in dataset[bit])


def prepared(observed):
    per_bit = [[], []]
    for state, action, outcome in observed:
        x = bits(state, action)
        for b in range(2):
            per_bit[b].append((x, (outcome >> b) & 1))
    return per_bit


def local_grow(data, bit):
    # First learn/select six useful primitive nodes, not a table of completed rules.
    first_stage = []
    for primitive_id in range(30):
        score0 = sum(likelihood(primitive(primitive_id, x), y)
                     for x, y in data[bit])
        score1 = sum(likelihood(1 ^ primitive(primitive_id, x), y)
                     for x, y in data[bit])
        first_stage.append((max(score0, score1), primitive_id))
    selected = sorted(first_stage, key=lambda s: (-s[0], s[1]))[:CANDIDATE_BEAM]
    best = None
    best_score = float("-inf")
    evaluated = 0
    for _, first in selected:
        for second in range(30):
            for root in range(3):
                for bias in (0, 1):
                    proposal = (first, second, root, bias)
                    score = score_program(proposal, data, bit)
                    evaluated += 1
                    if score > best_score + 1e-12 or (
                        abs(score - best_score) <= 1e-12 and (best is None or proposal < best)):
                        best_score, best = score, proposal
    assert evaluated == 1080
    return best, evaluated + 30


def exhaustive(data, bit):
    best = None
    best_score = float("-inf")
    evaluated = 0
    for first in range(30):
        for second in range(30):
            for root in range(3):
                for bias in (0, 1):
                    proposal = (first, second, root, bias)
                    score = score_program(proposal, data, bit)
                    evaluated += 1
                    if score > best_score + 1e-12 or (
                        abs(score - best_score) <= 1e-12 and (best is None or proposal < best)):
                        best_score, best = score, proposal
    assert evaluated == 5400
    return best, evaluated


def logit_features(x):
    return (1,) + x + tuple(x[i] * x[j] for i, j in PAIR)


def sigmoid(z):
    z = max(-30, min(30, z))
    return 1.0 / (1.0 + math.exp(-z))


def train_logistic(data):
    model = []
    for b in range(2):
        samples = [(logit_features(x), y) for x, y in data[b]]
        weight = [0.0] * 16
        for _ in range(EPOCHS):
            grad = [0.0] * 16
            for features, label in samples:
                error = sigmoid(sum(w * value for w, value in zip(weight, features))) - label
                for i, value in enumerate(features):
                    grad[i] += error * value
            for i in range(16):
                weight[i] -= .15 * grad[i] / len(samples)
        model.append(weight)
    return model


def fit(method, examples, seed=0):
    if method == "random":
        return {"circuits": [[h(seed, "random", b, k) % limit for k, limit in
                              enumerate((30, 30, 3, 2))] for b in range(2)],
                "evaluations": 0}
    if method == "shuffled":
        outcomes = [entry[2] for entry in examples]
        random.Random(16061 + seed).shuffle(outcomes)
        examples = [(s, a, shuffled) for (s, a, _), shuffled in zip(examples, outcomes)]
    data = prepared(examples)
    if method in ("grow", "exhaustive", "shuffled"):
        circuits, cost = [], 0
        for b in range(2):
            program, evals = (exhaustive(data, b) if method == "exhaustive"
                              else local_grow(data, b))
            circuits.append(list(program))
            cost += evals
        return {"circuits": circuits, "evaluations": cost}
    if method == "logistic":
        return {"weights": train_logistic(data), "evaluations": 0}
    raise ValueError(method)


def probability(method, model, state, action):
    x = bits(state, action)
    if method == "logistic":
        return [sigmoid(sum(w * value for w, value in zip(weights, logit_features(x))))
                for weights in model["weights"]]
    return [float(circuit(program, x)) for program in model["circuits"]]


def choice(method, model, state, target):
    scores = []
    for action in range(4):
        p = probability(method, model, state, action)
        score = sum((p[b] if target & (1 << b) else 1 - p[b])
                    for b in range(2)) / 2
        scores.append(score)
    return max(range(4), key=lambda action: scores[action])


def consequence_reward(w, method, model, goals):
    results = []
    for state, target in goals:
        selected = choice(method, model, state, target)
        actual = consequence(w, state, selected)
        results.append(1 - (actual ^ target).bit_count() / 2)
    return sum(results) / len(results), results


def json_snapshot(model):
    return json.dumps(model, sort_keys=True, separators=(",", ":"))


class SharedStore:
    """One mutable, capacity-constrained structure used across unrelated world updates."""
    def __init__(self, retention):
        self.retention = retention
        self.slots = {}
        self.clock = 0

    def put(self, key, model, public_priority):
        self.clock += 1
        self.slots[key] = {"model": model, "priority": public_priority, "last": self.clock}
        if len(self.slots) > CAP:
            if self.retention == "value":
                remove = min(self.slots, key=lambda name:
                             (self.slots[name]["priority"], self.slots[name]["last"]))
            else:
                assert self.retention == "lru"
                remove = min(self.slots, key=lambda name: self.slots[name]["last"])
            del self.slots[remove]
        assert len(self.slots) <= CAP

    def get(self, key):
        return self.slots[key]["model"] if key in self.slots else None

    def restore(self):
        return json.loads(json_snapshot(self.slots))


def one_world(seed, transfer, methods):
    w = world(seed, transfer)
    seen, goals = observations(w)
    results = {}
    for method in methods:
        start = time.perf_counter()
        model = fit(method, seen, seed)
        reward, predictions = consequence_reward(w, method, model, goals)
        elapsed = time.perf_counter() - start
        restored = json.loads(json_snapshot(model))
        reward2, predictions2 = consequence_reward(w, method, restored, goals)
        assert reward == reward2 and predictions == predictions2
        results[method] = {
            "reward": reward,
            "predictions": predictions,
            "seconds": elapsed,
            "bytes": len(json_snapshot(model).encode("utf-8")),
            "evaluations": model["evaluations"],
        }
    return results


def measure_cohort(seeds, transfer, methods):
    totals = {method: {"reward": 0.0, "seconds": 0.0, "bytes": 0,
                       "evaluations": 0} for method in methods}
    records = []
    for seed in seeds:
        outcomes = one_world(seed, transfer, methods)
        row = {}
        for method, result in outcomes.items():
            totals[method]["reward"] += result["reward"]
            for field in ("seconds", "bytes", "evaluations"):
                totals[method][field] += result[field]
            row[method] = round(result["reward"], 10)
        records.append((seed, row))
    n = len(seeds)
    means = {name: {
        "n": n,
        "reward": round(row["reward"] / n, 8),
        "mean_seconds": round(row["seconds"] / n, 6),
        "mean_model_bytes": round(row["bytes"] / n, 2),
        "mean_rule_evaluations": row["evaluations"] / n,
    } for name, row in totals.items()}
    return means, records


def paired_ci(records, x, y):
    diffs = [score[x] - score[y] for _, score in records]
    n = len(diffs)
    rng = random.Random(16060)
    results = sorted(sum(diffs[rng.randrange(n)] for _ in range(n)) / n
                     for _ in range(BOOTSTRAP))
    return [round(results[25], 8), round(results[998], 8)]


def interference_case(seed, method):
    worlds = [world(seed + 3 * i, transfer=True) for i in range(3)]
    originals = [observations(w) for w in worlds]
    store = SharedStore("value")
    lru = SharedStore("lru")
    before = None
    original_model = None
    for idx, (w, (seen, goals)) in enumerate(zip(worlds, originals)):
        model = fit(method, seen, w["seed"])
        if idx == 0:
            original_model = json_snapshot(model)
            before = consequence_reward(w, method, model, goals)[1]
        for s in (store, lru):
            s.put(str(idx), model, 2 if idx == 0 else 1)
    assert json_snapshot(store.get("0")) == original_model
    assert lru.get("0") is None
    final = consequence_reward(worlds[0], method, store.get("0"), originals[0][1])[1]
    restored = json.loads(json_snapshot(store.restore()))
    assert json_snapshot(restored["0"]["model"]) == original_model
    return {"retained_A": final == before,
            "lru_lost_A": lru.get("0") is None,
            "value_keys": sorted(store.slots.keys()),
            "peak_slots": max(len(store.slots), len(lru.slots))}


def audit():
    assert len(PRIMITIVES) == 30 and len(PAIR) == 10
    assert not (set(DEV) & set(TRANSFER) | set(TRANSFER) & set(NEGATIVE))
    assert len(set(DEV) | set(TRANSFER) | set(NEGATIVE)) == 128
    for seed in (990000, 990001, 990002, 990003):
        w = world(seed, transfer=seed % 2 == 1)
        seen, goals = observations(w)
        assert len(seen) == PROBES and len(goals) == TASKS
        assert not {s for s, _, _ in seen}.intersection({s for s, _ in goals})
        assert all((p[2] in ((1, 2) if w["transfer"] else (0,)))
                   for p in w["circuits"])
        for method in ("grow", "exhaustive", "logistic", "random", "shuffled"):
            model = fit(method, seen, seed)
            assert model == json.loads(json_snapshot(model))
            result = consequence_reward(w, method, model, goals)[0]
            assert 0 <= result <= 1
        grow = fit("grow", seen, seed)
        exact = fit("exhaustive", seen, seed)
        assert grow["evaluations"] == 2220
        assert exact["evaluations"] == 10800
    return True


def main():
    start = time.perf_counter()
    assert audit()
    methods = ("grow", "exhaustive", "logistic", "random")
    dev, dev_rows = measure_cohort(DEV, False, methods)
    transfer, transfer_rows = measure_cohort(TRANSFER, True, methods)
    neg, neg_rows = measure_cohort(NEGATIVE, True, ("grow", "shuffled"))
    retained = {name: [interference_case(seed, name) for seed in INTERFERENCE]
                for name in ("grow", "exhaustive")}
    direct = transfer["grow"]["reward"]
    exact = transfer["exhaustive"]["reward"]
    conventional = transfer["logistic"]["reward"]
    gap = {
        "transfer_grow_minus_map": round(direct - exact, 8),
        "transfer_grow_minus_logistic": round(direct - conventional, 8),
        "transfer_grow_seconds_ratio_to_map": round(transfer["grow"]["mean_seconds"] /
                                                    max(1e-9, transfer["exhaustive"]["mean_seconds"]), 6),
        "transfer_graph_evaluation_ratio_to_map": round(transfer["grow"]["mean_rule_evaluations"] /
                                                       transfer["exhaustive"]["mean_rule_evaluations"], 6),
        "negative_true_minus_shuffle": round(neg["grow"]["reward"] -
                                              neg["shuffled"]["reward"], 8),
    }
    ci = {
        "transfer_vs_map": paired_ci(transfer_rows, "grow", "exhaustive"),
        "transfer_vs_logistic": paired_ci(transfer_rows, "grow", "logistic"),
        "negative_vs_shuffled": paired_ci(neg_rows, "grow", "shuffled"),
    }
    checks = {
        "same_prior_approximation": gap["transfer_grow_minus_map"] >= -.035,
        "beats_logistic": gap["transfer_grow_minus_logistic"] >= .03,
        "lower_candidate_graph_search": gap["transfer_graph_evaluation_ratio_to_map"] <= .25,
        "wall_time_better": gap["transfer_grow_seconds_ratio_to_map"] <= .75,
        "shuffled_label_negative": gap["negative_true_minus_shuffle"] >= .08,
        "shared_memory_retained": all(z["retained_A"] for rows in retained.values() for z in rows),
        "lru_eviction_negative": all(z["lru_lost_A"] for rows in retained.values() for z in rows),
    }
    receipt = {"dev": dev_rows, "transfer": transfer_rows, "negative": neg_rows}
    return {
        "schema": "yggdrasil.contrib.aai06a.result.v1",
        "prereg_commit": PREREG,
        "classification": ("EXTERNAL_CANDIDATE_SUPPORTED_UNQUALIFIED" if all(checks.values())
                           else "VALID_NEGATIVE_OR_MIXED_NO_INTEGRATION"),
        "cohorts": {"dev": dev, "transfer": transfer, "negative": neg},
        "paired_bootstrap_ci": ci, "deltas": gap, "checks": checks,
        "interference": {name: {
            "n": len(rows),
            "A_retained": sum(x["retained_A"] for x in rows),
            "lru_A_lost": sum(x["lru_lost_A"] for x in rows),
            "all_two_slot": all(x["peak_slots"] == 2 for x in rows),
        } for name, rows in retained.items()},
        "receipt_sha256": hashlib.sha256(json_snapshot(receipt).encode()).hexdigest(),
        "limitations": "Boolean circuits assembled from provided primitive grammar; local beam growth is conventional heuristic program search, not proof of a new primitive, unknown dynamics or AGI. Shared memory uses provided hot key priority; retained state is key-isolated.",
        "integration": "NONE",
        "elapsed_seconds": round(time.perf_counter() - start, 6),
    }


if __name__ == "__main__":
    print(json.dumps(main(), sort_keys=True, indent=2))
