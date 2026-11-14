"""AAI-02B. Frozen direct association vs conventional memory selection.
External synthetic contributor study. No model/owner-loop changes. Python standard library.
"""
import hashlib
import json
import math
import random
import sys
import time

PREREG = "32f4b7f3c05bf29533b1e571270c8df4f820de08"
TRAIN = range(62000, 62512)
DEV = range(63000, 63128)
TRANSFER = range(64000, 64128)
NEGATIVE = range(65000, 65128)
CAPACITY = 8
PASSIVE = 64
CHANNELS = 4
REPETITIONS = 8
EPOCHS = 400
LEARNING_RATE = 0.15


def h(seed, *parts):
    key = ":".join((str(seed), *(str(p) for p in parts)))
    return int.from_bytes(hashlib.sha256(key.encode("utf-8")).digest()[:8], "big")


def setting(seed, transfer=False):
    context = seed % 8 + (8 if transfer else 0)
    group = context % 4
    return {"seed": seed, "context": context, "group": group,
            "law": h(seed, "law") % 2, "diagnostic": (3 * group + 1) % 4}


def active_event(w, action, repetition, t, law=None, phase="base"):
    x = h(w["seed"], phase, "input", action, repetition) % 2
    if action == w["diagnostic"]:
        ylaw = w["law"] if law is None else law
        flip = h(w["seed"], phase, "noise", action, repetition) % 1000 < 200
        signal = ylaw ^ int(flip)
        y = x ^ signal
    else:
        y = h(w["seed"], phase, "decoy", action, repetition) % 2
    return {"kind": "do", "action": action, "input": x, "response": y,
            "context": w["context"], "t": t}


def events_for(w, reversal=False):
    events = []
    for repetition in range(REPETITIONS):
        for action in range(CHANNELS):
            events.append(active_event(w, action, repetition,
                                       repetition * CHANNELS + action))
    next_t = REPETITIONS * CHANNELS
    if reversal:
        # Additional observations are granted identically to every arm.
        for i in range(REPETITIONS):
            events.append(active_event(w, w["diagnostic"], i, next_t + i,
                                       law=1 - w["law"], phase="reversal"))
        next_t += REPETITIONS
    for i in range(PASSIVE):
        action = h(w["seed"], "passive", i, "action") % CHANNELS
        events.append({"kind": "passive", "action": action,
                       "input": h(w["seed"], "passive", i, "input") % 2,
                       "response": h(w["seed"], "passive", i, "response") % 2,
                       "context": w["context"], "t": next_t + i})
    assert len(events) == (104 if reversal else 96)
    return events


def signed_signal(e):
    return 2 * (e["input"] ^ e["response"]) - 1


def direct_fit(worlds, scramble=False):
    labels = [w["law"] for w in worlds]
    if scramble:
        random.Random(9007).shuffle(labels)
    sums = [0.0] * 16
    counts = [0] * 16
    for w, label in zip(worlds, labels):
        for e in events_for(w)[:32]:
            idx = w["group"] * CHANNELS + e["action"]
            sums[idx] += signed_signal(e) * (2 * label - 1)
            counts[idx] += 1
    assert all(counts)
    return [abs(s / n) for s, n in zip(sums, counts)]


def training_feature(w):
    features = [0.0] * 16
    for e in events_for(w)[:32]:
        idx = w["group"] * CHANNELS + e["action"]
        features[idx] += signed_signal(e)
    return features


def sigmoid(z):
    return 1.0 / (1.0 + math.exp(-max(-35.0, min(35.0, z))))


def logistic_fit(worlds):
    data = [(training_feature(w), w["law"]) for w in worlds]
    theta = [0.0] * 16
    for _ in range(EPOCHS):
        grad = [0.0] * 16
        for features, y in data:
            pred = sigmoid(sum(w * x for w, x in zip(theta, features)))
            err = pred - y
            for i, x in enumerate(features):
                grad[i] += err * x
        for i in range(16):
            theta[i] -= LEARNING_RATE * grad[i] / len(data)
    bce = sum(-y * math.log(max(1e-12, sigmoid(sum(t * x for t, x in zip(theta, f)))))
              -(1-y) * math.log(max(1e-12, 1-sigmoid(sum(t * x for t, x in zip(theta, f)))))
              for f, y in data) / len(data)
    return [abs(w) for w in theta], bce


def retain(events, method, context, seed, weights=None, oracle=None):
    memory = []
    rng = random.Random(seed + 90909)
    group = context % 4
    def priority(event):
        if method == "recent":
            return 0.0
        if event["kind"] != "do":
            return -1.0
        if method == "active_recent":
            return 0.0
        if method == "expert":
            return 2.0 if event["action"] == oracle else 0.0
        assert method in ("direct", "logistic", "scrambled")
        assert weights is not None and len(weights) == 16
        return weights[group * CHANNELS + event["action"]]
    for i, event in enumerate(events):
        memory.append(event)
        if len(memory) <= CAPACITY:
            continue
        if method == "reservoir":
            index = rng.randrange(i + 1)
            last = memory.pop()
            if index < CAPACITY:
                memory[index] = last
        else:
            victim = min(range(len(memory)),
                         key=lambda k: (priority(memory[k]), memory[k]["t"]))
            memory.pop(victim)
    assert len(memory) == CAPACITY
    return memory


def predict(memory):
    votes = sum(signed_signal(e) for e in memory if e["kind"] == "do")
    return int(votes > 0)


def one_world(w, method, weights, reversal=False):
    events = events_for(w, reversal=reversal)
    memory = retain(events, method, w["context"], w["seed"],
                    weights=weights, oracle=w["diagnostic"] if method == "expert" else None)
    guess = predict(memory)
    target = (1 - w["law"]) if reversal else w["law"]
    return {"correct": int(guess == target), "prediction": guess,
            "active_kept": sum(e["kind"] == "do" for e in memory),
            "diagnostic_kept": sum(e["kind"] == "do" and
                                   e["action"] == w["diagnostic"] for e in memory)}


def paired_p(b, c):
    n = b + c
    if n == 0:
        return 1.0
    return min(1.0, 2.0 * sum(math.comb(n, k) for k in range(min(b, c) + 1)) / (2 ** n))


def evaluate():
    started = time.perf_counter()
    assert len(set(TRAIN) | set(DEV) | set(TRANSFER) | set(NEGATIVE)) == 896
    train = [setting(seed) for seed in TRAIN]
    direct = direct_fit(train)
    conventional, train_bce = logistic_fit(train)
    scrambled = direct_fit(train, scramble=True)
    fitted = {"direct": direct, "logistic": conventional, "scrambled": scrambled}
    arms = ("direct", "logistic", "expert", "active_recent",
            "recent", "reservoir", "scrambled")
    cohorts = {}
    all_predictions = {}
    paired = [0, 0]
    reversal_scores = {"direct": 0, "logistic": 0}
    for name, seeds, transfer, reversal in (
        ("dev", DEV, False, False),
        ("transfer", TRANSFER, True, False),
        ("negative", NEGATIVE, True, False),
        ("dev_reversal", DEV, False, True),
        ("transfer_reversal", TRANSFER, True, True),
    ):
        scores = {arm: {"correct": 0, "active_kept": 0, "diagnostic_kept": 0}
                  for arm in arms}
        records = []
        for seed in seeds:
            w = setting(seed, transfer)
            answers = {}
            for arm in arms:
                ans = one_world(w, arm, fitted.get(arm), reversal)
                answers[arm] = ans["prediction"]
                for field in scores[arm]:
                    scores[arm][field] += ans[field]
            if name in ("dev", "transfer"):
                d = int(answers["direct"] == w["law"])
                l = int(answers["logistic"] == w["law"])
                paired[0] += int(d and not l)
                paired[1] += int(l and not d)
            records.append((seed, answers))
        cohorts[name] = {arm: {"correct": v["correct"], "n": len(seeds),
                               "accuracy": v["correct"] / len(seeds),
                               "mean_active_kept": v["active_kept"] / len(seeds),
                               "mean_diagnostic_kept": v["diagnostic_kept"] / len(seeds)}
                         for arm, v in scores.items()}
        all_predictions[name] = records
        if reversal:
            for arm in reversal_scores:
                reversal_scores[arm] += scores[arm]["correct"]
    restored = json.loads(json.dumps(fitted, sort_keys=True))
    assert restored == fitted
    for name in ("dev", "transfer"):
        seed = (DEV.start if name == "dev" else TRANSFER.start)
        w = setting(seed, name == "transfer")
        for arm in fitted:
            assert one_world(w, arm, restored[arm]) == one_world(w, arm, fitted[arm])
    dev_gap = cohorts["dev"]["direct"]["accuracy"] - cohorts["dev"]["logistic"]["accuracy"]
    transfer_gap = (cohorts["transfer"]["direct"]["accuracy"] -
                    cohorts["transfer"]["logistic"]["accuracy"])
    reversal_gap = (reversal_scores["direct"] - reversal_scores["logistic"]) / 256
    neg_accuracy = cohorts["negative"]["scrambled"]["accuracy"]
    exact_p = paired_p(*paired)
    sanity = {"valid_world_counts": True, "matched_16_scalars": all(len(x)==16 for x in fitted.values()),
              "fixed_eight_memory_slots": True, "trained_only_on_train": True,
              "cold_restore": True, "negative_leq_065": neg_accuracy <= .65}
    gain = dev_gap >= .05 and transfer_gap >= .05 and exact_p < .05 and reversal_gap >= -.03
    if not all(sanity.values()):
        classification = "INVALID_NEGATIVE_OR_CUSTODY"
    elif gain:
        classification = "SCIENTIFIC_PASS_CANDIDATE_REQUIRES_INDEPENDENT_QUALIFICATION"
    elif (dev_gap > 0 and transfer_gap > 0) or (dev_gap >= .05 or transfer_gap >= .05):
        classification = "MIXED_NO_PROMOTION"
    else:
        classification = "NEGATIVE_OR_NO_SUPERIORITY_NO_PROMOTION"
    digest = hashlib.sha256(json.dumps(all_predictions, sort_keys=True).encode()).hexdigest()
    return {"schema": "aai02b.result.v1", "experiment": "AAI-02B",
            "prereg_commit": PREREG, "classification": classification,
            "train": {"n": len(train), "logistic_epochs": EPOCHS,
                      "logistic_bce": round(train_bce, 8),
                      "direct_weights": direct, "logistic_abs_weights": conventional,
                      "scrambled_weights": scrambled},
            "cohorts": cohorts, "paired": {"direct_only": paired[0],
                                          "logistic_only": paired[1], "mcnemar_p": exact_p},
            "thresholds": {"dev_gap": dev_gap, "transfer_gap": transfer_gap,
                           "combined_reversal_gap": reversal_gap, "negative_accuracy": neg_accuracy},
            "sanity": sanity, "predictions_sha256": digest,
            "source_class": "synthetic-development-only", "integration": "NONE",
            "limitations": "Fixed four-channel synthetic causal family with shared group invariance; privileged expert is ceiling, not matched comparator; no native general-intelligence proof.",
            "elapsed_seconds": round(time.perf_counter() - started, 6)}


def main():
    result = evaluate()
    print(json.dumps(result, indent=2, sort_keys=True))
    if not all(result["sanity"].values()):
        sys.exit(2)


if __name__ == "__main__":
    main()
