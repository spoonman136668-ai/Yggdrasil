"""AAI-05 frozen causal motif learner vs strong trained controls.
Independent contributor-only synthetic experiment; no native Yggdrasil changes.
"""
import hashlib
import itertools
import json
import math
import random
import time

PREREG = "d417e2aff50db08d2b12af7d02ced094d17983cc"
DEV = range(110000, 110064)
TRANSFER = range(120000, 120128)
NEGATIVE = range(130000, 130064)
OPS = ("xor", "and", "or", "xnor")
PAIRS = tuple(itertools.combinations(range(6), 2))
RULES = tuple((i, j, op) for i, j in PAIRS for op in range(4))
LOG_MATCH = math.log(0.92)
LOG_MISMATCH = math.log(0.08)
PROBES = 16
TASKS = 12
LOGISTIC_EPOCHS = 300
BOOTSTRAP = 1024


def h(seed, *parts):
    key = ":".join(str(x) for x in (seed, *parts)).encode("utf-8")
    return int.from_bytes(hashlib.sha256(key).digest()[:8], "big")


def input_bits(state, action):
    assert 0 <= state < 16 and 0 <= action < 4
    return tuple((state >> bit) & 1 for bit in range(4)) + tuple(
        (action >> bit) & 1 for bit in range(2))


def apply_rule(rule_id, bits):
    i, j, op = RULES[rule_id]
    a, b = bits[i], bits[j]
    return ((a ^ b), (a & b), (a | b), 1 ^ (a ^ b))[op]


def rule_ids(world):
    allowed_ops = (2, 3) if world["transfer"] else (0, 1)
    return tuple(4 * (h(world["seed"], "pair", bit) % 15)
                 + allowed_ops[h(world["seed"], "operator", bit) % 2]
                 for bit in range(2))


def world(seed, transfer=False):
    return {"seed": seed, "transfer": bool(transfer)}


def underlying(world_, state, action):
    bits = input_bits(state, action)
    r0, r1 = rule_ids(world_)
    return apply_rule(r0, bits) | (apply_rule(r1, bits) << 1)


def data_for(world_):
    seed = world_["seed"]
    states = sorted(range(16), key=lambda state: (h(seed, "state_split", state), state))
    train_states, terminal_states = states[:12], states[12:]
    choices = [(state, action) for state in train_states for action in range(4)]
    probe_pairs = sorted(choices, key=lambda pair: (
        h(seed, "probe_pair", pair[0], pair[1]), pair))[:PROBES]
    observations = []
    for index, (state, action) in enumerate(probe_pairs):
        true_result = underlying(world_, state, action)
        y = true_result
        for bit in range(2):
            if h(seed, "flip", index, bit) % 10000 < 800:
                y ^= 1 << bit
        observations.append({"state": state, "action": action, "observed": y,
                             "kind": "do", "time": index})
    tasks = [(terminal_states[index % 4], h(seed, "target", index) % 4)
             for index in range(TASKS)]
    assert len(observations) == PROBES and len(set(probe_pairs)) == PROBES
    assert not set(train_states).intersection(terminal_states)
    return observations, tasks


def score_rules(observations, scramble=False, seed=0):
    records = observations
    if scramble:
        ys = [e["observed"] for e in observations]
        random.Random(15051 + seed).shuffle(ys)
        records = [dict(e, observed=y) for e, y in zip(observations, ys)]
    scores = [[0.0] * 60 for _ in range(2)]
    for event in records:
        assert event["kind"] == "do"
        bits = input_bits(event["state"], event["action"])
        for j in range(60):
            prediction = apply_rule(j, bits)
            for bit in range(2):
                observed = (event["observed"] >> bit) & 1
                scores[bit][j] += LOG_MATCH if prediction == observed else LOG_MISMATCH
    return scores


def direct_fit(observations, scramble=False, seed=0):
    scores = score_rules(observations, scramble, seed)
    return [max(range(60), key=lambda j: scores[b][j]) for b in range(2)]


def bayes_fit(observations):
    raw = score_rules(observations)
    distributions = []
    for scores in raw:
        peak = max(scores)
        weights = [math.exp(v - peak) for v in scores]
        mass = sum(weights)
        distributions.append([w / mass for w in weights])
    return distributions


def feature_vector(state, action):
    bits = input_bits(state, action)
    return (1,) + bits + tuple(bits[i] * bits[j] for i, j in PAIRS)


def sigmoid(z):
    if z > 32:
        return 1.0
    if z < -32:
        return 0.0
    return 1.0 / (1.0 + math.exp(-z))


def logistic_fit(observations):
    xs = [feature_vector(e["state"], e["action"]) for e in observations]
    matrix = [[0.0] * 22 for _ in range(2)]
    for bit in range(2):
        weights = matrix[bit]
        ys = [(e["observed"] >> bit) & 1 for e in observations]
        for epoch in range(LOGISTIC_EPOCHS):
            grad = [0.0] * 22
            for x, y in zip(xs, ys):
                z = sum(value * coefficient for value, coefficient in zip(x, weights))
                residual = sigmoid(z) - y
                for j, value in enumerate(x):
                    grad[j] += residual * value
            for j in range(22):
                weights[j] -= 0.15 * grad[j] / len(xs)
    return matrix


def cart_fit(observations):
    inputs = [input_bits(e["state"], e["action"]) for e in observations]
    def train_bit(bit):
        labels = [(e["observed"] >> bit) & 1 for e in observations]
        def build(indices, depth, available):
            ones = sum(labels[k] for k in indices)
            p = (ones + 1) / (len(indices) + 2)
            if depth == 3 or not available or ones in (0, len(indices)):
                return {"p": p}
            parent_gini = 2 * (ones / len(indices)) * (1 - ones / len(indices))
            candidates = []
            for feat in available:
                left = [k for k in indices if inputs[k][feat] == 0]
                right = [k for k in indices if inputs[k][feat] == 1]
                if not left or not right:
                    continue
                def imp(ids):
                    q = sum(labels[k] for k in ids) / len(ids)
                    return 2 * q * (1 - q)
                weighted = (len(left) * imp(left) + len(right) * imp(right)) / len(indices)
                candidates.append((parent_gini - weighted, feat, left, right))
            if not candidates:
                return {"p": p}
            gain, feat, left, right = max(candidates, key=lambda x:(x[0], -x[1]))
            if gain <= 1e-12:
                return {"p": p}
            rest = tuple(j for j in available if j != feat)
            return {"split": feat, "left": build(left, depth + 1, rest),
                    "right": build(right, depth + 1, rest)}
        return build(list(range(len(labels))), 0, tuple(range(6)))
    return [train_bit(0), train_bit(1)]


def lookup_fit(observations):
    table = {str(e["state"]) + ":" + str(e["action"]):e["observed"] for e in observations}
    means = [sum((e["observed"] >> bit) & 1 for e in observations) / len(observations)
             for bit in range(2)]
    return {"table": table, "means": means}


def predict_probability(method, trained, state, action):
    bits = input_bits(state, action)
    if method in ("direct", "shuffled"):
        return [float(apply_rule(program, bits)) for program in trained]
    if method == "bayes":
        return [sum(weight * apply_rule(i, bits) for i, weight in enumerate(row))
                for row in trained]
    if method == "logistic":
        features = feature_vector(state, action)
        return [sigmoid(sum(w * x for w, x in zip(row, features)))
                for row in trained]
    if method == "cart":
        probabilities = []
        for tree in trained:
            node = tree
            while "split" in node:
                node = node["right" if bits[node["split"]] else "left"]
            probabilities.append(node["p"])
        return probabilities
    assert method == "lookup"
    key = str(state) + ":" + str(action)
    if key in trained["table"]:
        y = trained["table"][key]
        return [float(y & 1), float((y >> 1) & 1)]
    return trained["means"]


def choose_action(method, trained, state, target):
    options = []
    for action in range(4):
        p0,p1 = predict_probability(method, trained, state, action)
        score = ((p0 if target & 1 else 1 - p0)
                 + (p1 if target & 2 else 1 - p1)) / 2
        options.append(score)
    return max(range(4), key=lambda i: options[i])


def terminal_reward(world_, method, trained, tasks):
    outcomes = []
    for state, target in tasks:
        action = choose_action(method, trained, state, target)
        actual = underlying(world_, state, action)
        outcomes.append(1 - (actual ^ target).bit_count() / 2)
    return sum(outcomes) / len(outcomes), outcomes


def serialize(obj):
    return json.dumps(obj, sort_keys=True, separators=(",", ":"))


def train(method, observations, seed=0):
    if method == "direct":
        return direct_fit(observations)
    if method == "shuffled":
        return direct_fit(observations, scramble=True, seed=seed)
    if method == "bayes":
        return bayes_fit(observations)
    if method == "logistic":
        return logistic_fit(observations)
    if method == "cart":
        return cart_fit(observations)
    assert method == "lookup"
    return lookup_fit(observations)


def one_world(seed, transfer, methods):
    w = world(seed, transfer)
    observations, tasks = data_for(w)
    results = {}
    for method in methods:
        tick = time.perf_counter()
        trained = train(method, observations, seed)
        score, predictions = terminal_reward(w, method, trained, tasks)
        fit_and_score = time.perf_counter() - tick
        packed = serialize(trained)
        restored = json.loads(packed)
        score2, preds2 = terminal_reward(w, method, restored, tasks)
        # Learning on unrelated worlds occurs between snapshot and cold restoration.
        # Stateless methods must not touch the original serialization.
        for new_seed in (seed + 200000, seed + 300000):
            distractor = world(new_seed, not transfer)
            other_obs,_ = data_for(distractor)
            train(method, other_obs, new_seed)
        score3, preds3 = terminal_reward(w, method, json.loads(packed), tasks)
        assert score == score2 == score3 and predictions == preds2 == preds3
        results[method] = {
            "reward": score,
            "predictions": predictions,
            "cold_restored": True,
            "interference_restored": True,
            "serialized_bytes": len(packed.encode("utf-8")),
            "fit_eval_seconds": fit_and_score,
        }
    return results


def evaluate_cohort(seeds, transfer, methods):
    totals = {m: {"reward":0.0,"bytes":0,"seconds":0.0} for m in methods}
    rows = []
    for seed in seeds:
        scores = one_world(seed, transfer, methods)
        rec = {}
        for name in methods:
            result = scores[name]
            totals[name]["reward"] += result["reward"]
            totals[name]["bytes"] += result["serialized_bytes"]
            totals[name]["seconds"] += result["fit_eval_seconds"]
            rec[name] = round(result["reward"], 10)
        rows.append((seed, rec))
    n=len(seeds)
    means={name:{"n":n,"mean_reward":round(row["reward"]/n,8),
                 "mean_serialized_bytes":round(row["bytes"]/n,2),
                 "mean_fit_eval_seconds":round(row["seconds"]/n,6)}
           for name,row in totals.items()}
    return means,rows


def paired_ci(rows, first, second):
    differences=[values[first]-values[second] for _,values in rows]
    n=len(differences)
    rng=random.Random(15050)
    sampled=sorted(sum(differences[rng.randrange(n)] for _ in range(n)) / n
                   for _ in range(BOOTSTRAP))
    return [round(sampled[25],8),round(sampled[998],8)]


def audit():
    assert len(RULES)==60 and len(PAIRS)==15
    all_seeds=set(DEV)|set(TRANSFER)|set(NEGATIVE)
    assert len(all_seeds)==256
    for seed, transfer in ((900000,False),(900001,True),(900002,False)):
        w=world(seed,transfer)
        obs,tasks=data_for(w)
        assert len(obs)==PROBES and len(tasks)==TASKS
        assert not {e["state"] for e in obs}.intersection({s for s,_ in tasks})
        assert all(e["kind"]=="do" and "law" not in e for e in obs)
        assert len(set((e["state"],e["action"]) for e in obs))==PROBES
        assert all((rid%4 in ((2,3) if transfer else (0,1)))
                   for rid in rule_ids(w))
        for m in ("direct","bayes","logistic","cart","lookup","shuffled"):
            model=train(m,obs,seed)
            encoded=serialize(model)
            assert json.loads(encoded)==model
            p=predict_probability(m,model,tasks[0][0],0)
            assert len(p)==2 and all(0<=x<=1 for x in p)
    return True


def main():
    start=time.perf_counter()
    assert audit()
    major=("direct","bayes","logistic","cart","lookup")
    dev,dev_rows=evaluate_cohort(DEV,False,major)
    transfer,transfer_rows=evaluate_cohort(TRANSFER,True,major)
    negative,negative_rows=evaluate_cohort(NEGATIVE,True,("direct","shuffled"))
    strongest_dev=max(("logistic","cart"),key=lambda a:dev[a]["mean_reward"])
    strongest_transfer=max(("logistic","cart"),key=lambda a:transfer[a]["mean_reward"])
    differences={
        "dev_vs_strongest_conventional":round(dev["direct"]["mean_reward"]-dev[strongest_dev]["mean_reward"],8),
        "transfer_vs_strongest_conventional":round(transfer["direct"]["mean_reward"]-transfer[strongest_transfer]["mean_reward"],8),
        "transfer_vs_bayes":round(transfer["direct"]["mean_reward"]-transfer["bayes"]["mean_reward"],8),
        "negative_proper_minus_shuffled":round(negative["direct"]["mean_reward"]-negative["shuffled"]["mean_reward"],8),
    }
    ci={
        "dev_vs_strongest_conventional":paired_ci(dev_rows,"direct",strongest_dev),
        "transfer_vs_strongest_conventional":paired_ci(transfer_rows,"direct",strongest_transfer),
        "transfer_vs_bayes":paired_ci(transfer_rows,"direct","bayes"),
        "negative_proper_minus_shuffled":paired_ci(negative_rows,"direct","shuffled"),
    }
    checks={
        "no_leakage_and_disjointness":True,
        "cold_and_interference_restoration":True,
        "transfer_gain":differences["transfer_vs_strongest_conventional"]>=.03,
        "transfer_positive_ci":ci["transfer_vs_strongest_conventional"][0]>0,
        "bayes_near_parity":differences["transfer_vs_bayes"]>=-.025,
        "dev_nonregression":differences["dev_vs_strongest_conventional"]>=-.02,
        "shuffled_negative":differences["negative_proper_minus_shuffled"]>=.10,
    }
    rows={"dev":dev_rows,"transfer":transfer_rows,"negative":negative_rows}
    fingerprint=hashlib.sha256(serialize(rows).encode("utf-8")).hexdigest()
    result={
        "schema":"yggdrasil.contrib.aai05.result.v1",
        "prereg_commit":PREREG,
        "classification":"SCIENTIFIC_PASS_CANDIDATE_UNQUALIFIED" if all(checks.values())
                         else "SCIENTIFIC_NEGATIVE_NO_INTEGRATION",
        "cohorts":{"development":dev,"transfer":transfer,"negative":negative},
        "strongest_conventional":{"development":strongest_dev,"transfer":strongest_transfer},
        "differences":differences,"paired_bootstrap_95pct":ci,"checks":checks,
        "prediction_receipt_sha256":fingerprint,
        "cost_basis":"wall-clock fit plus terminal scoring; cold/interference extra work excluded from per-method fit time; memory report is serialized inference state only",
        "limitations":"World generator and hypothesis catalog are known to the associator and exact Bayes; transfer involves operator combinations unseen in the development cohort, NOT arbitrary unknown causal physics. Test is synthetic and does not prove general intelligence or native Yggdrasil learning.",
        "integration":"NONE","duration_seconds":round(time.perf_counter()-start,6),
    }
    print(json.dumps(result,indent=2,sort_keys=True))


if __name__ == "__main__":
    main()
