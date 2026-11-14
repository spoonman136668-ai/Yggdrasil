"""AAI-02A preregistered eight-slot causal-memory benchmark. DEV-only; no model integration."""
import hashlib
import json
import math
import random
import sys
import time

TRAIN = range(41000, 41032)
DEV = range(42000, 42032)
TRANSFER = range(43000, 43032)
NEGATIVE = range(44000, 44032)
CAPACITY = 8
DISTRACTORS = (0, 16, 64)
PREREG = "b0a6922b67112eb4c47e8038cb44b6ec0c97d090"


def bit(seed, label):
    return int.from_bytes(hashlib.sha256(f"{seed}:{label}".encode()).digest()[:8], "big")


def world(seed):
    rng = random.Random(seed)
    roles = rng.sample(range(8), 3)
    law = rng.randrange(2)
    return {"seed": seed, "roles": dict(zip(("A", "B", "C"), roles)), "law": law}


def passive(w):
    # Both causal laws induce identical passive distributions.
    return [(v, v, v) for v in (0, 1, 0, 1)]


def intervention(w, action, index):
    assert action in ("A", "C")
    clean_b = 1 if action == "A" else w["law"]
    flip = (bit(w["seed"], f"flip:{action}:{index}") % 1000000) < 200000
    return {"type": "probe", "action": action, "b": clean_b ^ int(flip), "t": index}


def make_distractors(w, quantity):
    rng = random.Random(w["seed"] + 800000)
    return [{"type": "irrelevant", "u": rng.randrange(8), "v": rng.randrange(8),
             "value": rng.randrange(2), "t": 3 + i} for i in range(quantity)]


def select_actions(w, policy):
    if policy == "active":
        return ("C",) * 3
    if policy == "passive":
        return ("A",) * 3
    assert policy == "random"
    return tuple("C" if bit(w["seed"], f"policy:{i}") % 2 else "A" for i in range(3))


def retain(events, method, seed, capacity=CAPACITY):
    assert capacity == 8
    memory = []
    rng = random.Random(seed + 900000)
    for i, event in enumerate(events):
        memory.append(event)
        if len(memory) <= capacity:
            continue
        if method == "recent":
            memory.pop(0)
        elif method == "reservoir":
            j = rng.randrange(i + 1)
            old = memory.pop()
            if j < capacity:
                memory[j] = old
        elif method == "relevance":
            def priority(e):
                if e["type"] == "probe":
                    return 2 if e["action"] == "C" else 1
                return 0
            drop = min(range(len(memory)), key=lambda k: (priority(memory[k]), memory[k]["t"]))
            memory.pop(drop)
        else:
            raise ValueError(method)
    assert len(memory) <= capacity
    return memory


def feature(memory):
    return sum(2 * e["b"] - 1 for e in memory
               if e["type"] == "probe" and e["action"] == "C")


def bayes(memory):
    # Equal-prior Bayes with 20% iid response noise; ties choose fixed prior 0.
    return int(feature(memory) > 0)


def sigmoid(z):
    return 1.0 / (1.0 + math.exp(-max(-40.0, min(40.0, z))))


def logistic_train(worlds):
    data = []
    for w in worlds:
        probes = [intervention(w, "C", i) for i in range(3)]
        data.append((feature(probes), w["law"]))
    theta = [0.0, 0.0]
    for epoch in range(2000):
        grads = [0.0, 0.0]
        for x, y in data:
            p = sigmoid(theta[0] + theta[1] * x)
            grads[0] += p - y
            grads[1] += (p - y) * x
        theta[0] -= 0.2 * grads[0] / len(data)
        theta[1] -= 0.2 * grads[1] / len(data)
    bce = -sum(
        y * math.log(max(1e-12, sigmoid(theta[0] + theta[1] * x))) +
        (1-y) * math.log(max(1e-12, 1-sigmoid(theta[0] + theta[1] * x)))
        for x, y in data
    ) / len(data)
    return theta, bce, len(data)


def predict_logistic(memory, theta):
    return int(sigmoid(theta[0] + theta[1] * feature(memory)) > 0.5)


def eval_arm(w, distractors, probe_policy, memory_policy, classifier, theta):
    acts = select_actions(w, probe_policy)
    events = [{"type": "passive", "abc": obs, "t": -4+i}
              for i, obs in enumerate(passive(w))]
    events.extend(intervention(w, action, i) for i, action in enumerate(acts))
    events.extend(make_distractors(w, distractors))
    stored = retain(events, memory_policy, w["seed"])
    guess = bayes(stored) if classifier == "bayes" else predict_logistic(stored, theta)
    return {"correct": int(guess == w["law"]), "retained": len(stored),
            "diagnostic_retained": sum(e["type"] == "probe" and e["action"] == "C"
                                       for e in stored),
            "probe_actions": len(acts)}


def audit_identifiability():
    for s in (41000, 42000, 43000):
        w0 = world(s)
        w1 = dict(w0, law=1-w0["law"])
        assert passive(w0) == passive(w1)
        assert [intervention(w0, "A", i) for i in range(3)] == [
            intervention(w1, "A", i) for i in range(3)]
        assert [intervention(w0, "C", i)["b"] ^
                intervention(w1, "C", i)["b"] for i in range(3)] == [1]*3
    return True


def evaluate():
    started = time.perf_counter()
    assert audit_identifiability()
    assert not (set(TRAIN) & set(DEV) or set(TRAIN) & set(TRANSFER)
                or set(DEV) & set(TRANSFER))
    theta, bce, train_n = logistic_train([world(s) for s in TRAIN])
    controls = {
        "bayes_relevance_active": ("active", "relevance", "bayes"),
        "logistic_relevance_active": ("active", "relevance", "logistic"),
        "bayes_recent_active": ("active", "recent", "bayes"),
        "bayes_reservoir_active": ("active", "reservoir", "bayes"),
        "bayes_relevance_passive": ("passive", "relevance", "bayes"),
        "bayes_relevance_random": ("random", "relevance", "bayes"),
    }
    cohorts = {}
    for label, seeds in (("dev", DEV), ("transfer", TRANSFER), ("negative", NEGATIVE)):
        out = {}
        for volume in DISTRACTORS:
            scores = {k: {"correct": 0, "diagnostic_retained": 0} for k in controls}
            for seed in seeds:
                w = world(seed)
                for name, (probe_policy, memory_policy, classifier) in controls.items():
                    r = eval_arm(w, volume, probe_policy, memory_policy, classifier, theta)
                    scores[name]["correct"] += r["correct"]
                    scores[name]["diagnostic_retained"] += r["diagnostic_retained"]
            out[str(volume)] = {
                name: {"correct": v["correct"], "total": len(seeds),
                       "accuracy": v["correct"]/len(seeds),
                       "mean_diagnostic_retained": v["diagnostic_retained"]/len(seeds)}
                for name, v in scores.items()
            }
        cohorts[label] = out
    negative_worlds = [world(s) for s in NEGATIVE]
    scrambled = 0
    zero_probe = 0
    for w in negative_worlds:
        informative = [intervention(w, "C", i) for i in range(3)]
        mislabeled = [dict(event, action="A") for event in informative]
        scrambled += int(bayes(mislabeled) == w["law"])
        zero_probe += int(bayes([]) == w["law"])
    checks = {"identifiability_paired": True, "train_n_32": train_n == 32,
              "logistic_converged": bce <= 0.70, "shared_memory_cap_8": True,
              "cold_restore": json.loads(json.dumps({"theta": theta}))["theta"] == theta,
              "zero_probe_guess_is_prior": bayes([]) == 0}
    active = sum(cohorts[k]["64"]["bayes_relevance_active"]["accuracy"]
                 for k in ("dev", "transfer")) / 2
    passive_score = sum(cohorts[k]["64"]["bayes_relevance_passive"]["accuracy"]
                        for k in ("dev", "transfer")) / 2
    strongest = max(cohorts[k]["64"][name]["accuracy"]
                    for k in ("dev", "transfer") for name in controls)
    admission = all(checks.values()) and active-passive_score >= .2 and .55 < strongest < .95
    return {"schema": "aai02a.benchmark-dev-result.v1", "prereg_commit": PREREG,
            "classification": "BENCHMARK_ADMITTED_DEV" if admission else "BENCHMARK_REJECTED_OR_INVALID_DEV",
            "train": {"n": train_n, "theta": theta, "BCE": round(bce, 8), "full_epochs": 2000},
            "controls": controls, "cohorts": cohorts, "checks": checks,
            "negative_controls": {"scrambled_probe_labels_correct": scrambled,
                                  "zero_probe_correct": zero_probe,
                                  "n": len(negative_worlds)},
            "admission": {"active_64": active, "passive_64": passive_score,
                          "delta": active-passive_score,
                          "max_strong_control_64": strongest, "eligible": admission},
            "local_elapsed_seconds": round(time.perf_counter()-started, 6),
            "limitations": "Known two causal laws, programmer-supplied relevance and Bayes ceiling; synthetic DEV only; no native model changed or scientific superiority.",
            "integration": "NONE"}


def main():
    result = evaluate()
    print(json.dumps(result, indent=2, sort_keys=True))
    if not all(result["checks"].values()):
        sys.exit(2)


if __name__ == "__main__":
    main()
