"""AAI-03A frozen synthetic structural causal-law benchmark. No model integration."""
import hashlib
import json
import math
import random
import sys
import time

PREREG = "7f5b8b7150446a7b54a9fd9bc962cd584b2c92a6"
TRAIN = range(71000, 71512)
DEV = range(72000, 72128)
TRANSFER = range(73000, 73128)
NEGATIVE = range(74000, 74128)
MASKS = (1, 2, 3, 5)
CAPACITY = 8
PROBES = 4
DISTRACTORS = 32
NOISE = 0.20


def h(seed, *parts):
    raw = ":".join(str(x) for x in (seed, *parts))
    return int.from_bytes(hashlib.sha256(raw.encode("utf-8")).digest()[:8], "big")


def offset(context):
    return (5 * context + context // 4) % 4


def transform(state, kind):
    if kind == 0:
        return state
    if kind == 1:
        return ((state << 1) & 7) | (state >> 2)
    if kind == 2:
        return (state >> 1) | ((state & 1) << 2)
    return ((state & 1) << 2) | (state & 2) | ((state & 4) >> 2)


def transition(law, state, action, context):
    assert 0 <= law < 8 and 0 <= state < 8 and 0 <= action < 4
    s = transform(state, law % 4)
    mask = MASKS[(action + offset(context)) % 4]
    return (s ^ mask) if law < 4 else ((s + mask) & 7)


def world(seed, transfer=False):
    return {"seed": seed, "context": seed % 8 + (8 if transfer else 0),
            "law": h(seed, "law") % 8,
            "terminal_state": h(seed, "terminal_state") % 8,
            "target": h(seed, "target") % 8}


def likelihood(observed, expected):
    distance = (observed ^ expected).bit_count()
    return .8 if distance == 0 else (.2 / 3 if distance == 1 else 0.0)


def observe(w, state, action, step):
    actual = transition(w["law"], state, action, w["context"])
    corrupt = h(w["seed"], "corrupt", step) % 1000 < 200
    if corrupt:
        actual ^= (1 << (h(w["seed"], "flipbit", step) % 3))
    return {"kind": "do", "context": w["context"], "state": state,
            "action": action, "observed": actual, "t": step}


def normal_action(action, context):
    return (action + offset(context)) % 4


def train_table(worlds, scramble=False):
    labels = [w["law"] for w in worlds]
    if scramble:
        random.Random(3007).shuffle(labels)
    counts = [[[[1 for _ in range(8)] for _ in range(4)]
               for _ in range(8)] for _ in range(8)]
    for w, label in zip(worlds, labels):
        for step in range(PROBES):
            state = h(w["seed"], "random_state", step) % 8
            action = h(w["seed"], "random_action", step) % 4
            o = observe(w, state, action, step)
            counts[label][state][normal_action(action, w["context"])][o["observed"]] += 1
    return counts


def event_likelihood(model, law, event, table=None):
    if event["kind"] != "do":
        return 1.0
    if model == "exact":
        correct = transition(law, event["state"], event["action"], event["context"])
        return likelihood(event["observed"], correct)
    assert model == "tabular" and table is not None
    counts = table[law][event["state"]][normal_action(event["action"], event["context"])]
    return counts[event["observed"]] / sum(counts)


def posterior(memory, model="exact", table=None):
    weights = [1.0] * 8
    for event in memory:
        for law in range(8):
            weights[law] *= event_likelihood(model, law, event, table)
        norm = sum(weights)
        assert norm > 0, "True law must remain in exact Bayes support; tabular counts smoothed."
        weights = [value / norm for value in weights]
    norm = sum(weights)
    return [v / norm for v in weights]


def reward(law, state, target, action, context):
    return 1.0 - (transition(law, state, action, context) ^ target).bit_count() / 3.0


def terminal_action(belief, w):
    options = [sum(belief[law] * reward(law, w["terminal_state"], w["target"], action,
                                      w["context"]) for law in range(8))
               for action in range(4)]
    return max(range(4), key=lambda action: options[action]), max(options)


def posterior_if(belief, w, state, action, y):
    raw = [belief[law] * likelihood(y, transition(law, state, action, w["context"]))
           for law in range(8)]
    mass = sum(raw)
    return ([v / mass for v in raw] if mass > 0 else None), mass


def query_value(belief, w, state, action, mode):
    if mode == "utility":
        total = 0.0
        for observed in range(8):
            updated, probability = posterior_if(belief, w, state, action, observed)
            if probability:
                total += probability * terminal_action(updated, w)[1]
        return total
    assert mode == "eig"
    initial_entropy = -sum(p * math.log2(p) for p in belief if p)
    residual = 0.0
    for observed in range(8):
        updated, probability = posterior_if(belief, w, state, action, observed)
        if probability:
            entropy = -sum(p * math.log2(p) for p in updated if p)
            residual += probability * entropy
    return initial_entropy - residual


def choose_query(belief, w, mode, step):
    if mode not in ("utility", "eig"):
        return (h(w["seed"], "random_state", step) % 8,
                h(w["seed"], "random_action", step) % 4)
    options = [(query_value(belief, w, state, action, mode), state, action)
               for state in range(8) for action in range(4)]
    best = max(x[0] for x in options)
    # Deterministic lexicographic tie, no hidden label.
    return next((state, action) for value, state, action in options
                if value >= best - 1e-12)


def retain(memory, event, method):
    memory.append(event)
    if len(memory) > CAPACITY:
        if method == "recent":
            memory.pop(0)
        else:
            index = min(range(len(memory)),
                        key=lambda i: (memory[i]["kind"] == "do", memory[i]["t"]))
            memory.pop(index)
    assert len(memory) <= CAPACITY


def passive_event(w, index):
    return {"kind": "passive", "context": w["context"],
            "state": h(w["seed"], "passive", index, "state") % 8,
            "action": h(w["seed"], "passive", index, "action") % 4,
            "observed": h(w["seed"], "passive", index, "observed") % 8,
            "t": PROBES + index}


def run_arm(w, method, table=None):
    if method == "expert":
        action = max(range(4), key=lambda a: reward(w["law"], w["terminal_state"],
                                                     w["target"], a, w["context"]))
        return {"reward": reward(w["law"], w["terminal_state"], w["target"],
                                 action, w["context"]), "retained_do": 0,
                "probes": 0}
    memory = []
    no_probe = method == "no_probe"
    exact = method in ("utility", "eig", "random", "recent", "no_probe")
    for step in range(0 if no_probe else PROBES):
        model = "exact" if exact else "tabular"
        belief = posterior(memory, model, table)
        state, action = choose_query(belief, w, method, step)
        retain(memory, observe(w, state, action, step), method)
    for i in range(DISTRACTORS):
        retain(memory, passive_event(w, i), method)
    model = "exact" if exact else "tabular"
    belief = posterior(memory, model, table)
    action, _ = terminal_action(belief, w)
    return {"reward": reward(w["law"], w["terminal_state"], w["target"],
                             action, w["context"]),
            "retained_do": sum(e["kind"] == "do" for e in memory),
            "probes": 0 if no_probe else PROBES}


def audit():
    assert len(set(TRAIN) | set(DEV) | set(TRANSFER) | set(NEGATIVE)) == 896
    for c in range(16):
        for a in range(8):
            for b in range(a + 1, 8):
                assert any(transition(a, state, act, c) != transition(b, state, act, c)
                           for state in range(8) for act in range(4))
    for seed in (72000, 73000):
        x = world(seed, transfer=seed >= 73000)
        alt = dict(x, law=(x["law"] + 1) % 8)
        assert [passive_event(x, i) for i in range(DISTRACTORS)] == [
            passive_event(alt, i) for i in range(DISTRACTORS)]
        assert x["terminal_state"] == alt["terminal_state"]
        assert x["target"] == alt["target"]
    return True


def scores(seeds, transfer, methods, models):
    sums = {name: {"reward_sum": 0.0, "retained_do_sum": 0,
                   "probes_sum": 0} for name in methods}
    records = []
    for seed in seeds:
        w = world(seed, transfer)
        each = {}
        for name in methods:
            out = run_arm(w, name, models.get(name))
            for key, val in out.items():
                sums[name][key + "_sum"] += val
            each[name] = round(out["reward"], 10)
        records.append([seed, each])
    stats = {name: {"n": len(seeds), "mean_reward": round(v["reward_sum"] / len(seeds), 8),
                    "mean_retained_do": v["retained_do_sum"] / len(seeds),
                    "mean_probes": v["probes_sum"] / len(seeds)}
             for name, v in sums.items()}
    return stats, records


def evaluate():
    start = time.perf_counter()
    assert audit()
    train = [world(s) for s in TRAIN]
    table = train_table(train)
    shuffled = train_table(train, scramble=True)
    assert json.loads(json.dumps(table)) == table
    assert json.loads(json.dumps(shuffled)) == shuffled
    arms = ("utility", "eig", "random", "no_probe", "tabular", "expert", "recent")
    models = {"tabular": table, "shuffled": shuffled}
    dev, dev_records = scores(DEV, False, arms, models)
    transfer, transfer_records = scores(TRANSFER, True, arms, models)
    neg, neg_records = scores(NEGATIVE, True, ("no_probe", "shuffled"), models)
    u = dev["utility"]["mean_reward"]
    oracle = dev["expert"]["mean_reward"]
    random_reward = dev["random"]["mean_reward"]
    passive = dev["no_probe"]["mean_reward"]
    negative_gain = neg["shuffled"]["mean_reward"] - neg["no_probe"]["mean_reward"]
    gate = {
        "identifiability": True,
        "nonsaturated_lower": u >= .55,
        "nonsaturated_upper": u <= .92,
        "expert_headroom": oracle - u >= .04,
        "intervention_value": u - passive >= .05,
        "targeted_vs_random": u - random_reward >= .01,
        "shuffled_label_negative": negative_gain <= .03,
        "cold_restore": True,
        "memory_cap": True,
    }
    receipt = {"dev": dev_records, "transfer": transfer_records, "negative": neg_records}
    fingerprint = hashlib.sha256(json.dumps(receipt, sort_keys=True,
                                           separators=(",", ":")).encode()).hexdigest()
    return {"schema": "yggdrasil.contrib.aai03a.dev-admission.v1",
            "prereg_commit": PREREG,
            "classification": "BENCHMARK_ADMITTED_DEV" if all(gate.values())
             else "NEGATIVE_BENCHMARK_NO_PROMOTION",
            "train_worlds": len(train), "cohorts": {"dev": dev, "transfer": transfer,
                                                      "negative": neg},
            "gate": gate,
            "deltas": {"utility_minus_no_probe": round(u - passive, 8),
                       "utility_minus_random": round(u - random_reward, 8),
                       "oracle_minus_utility": round(oracle - u, 8),
                       "scrambled_minus_no_probe_neg": round(negative_gain, 8)},
            "predictions_sha256": fingerprint,
            "limitations": "Eight publicly specified synthetic law hypotheses and expert structural Bayes; not native learning, novel associations, model improvement, or AGI.",
            "integration": "NONE",
            "elapsed_seconds": round(time.perf_counter() - start, 6)}


def main():
    print(json.dumps(evaluate(), sort_keys=True, indent=2))


if __name__ == "__main__":
    main()
