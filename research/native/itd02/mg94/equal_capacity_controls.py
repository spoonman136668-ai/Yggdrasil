"""MG94-O: equal-capacity synthetic interference controls. Development only.

Predeclared budget: four binary observations for all methods. No privilege,
reward labels, oracle priority, learned native mechanism or original world.
"""
from collections import deque
import json
import random

BUDGET = 4
SEED = 1904
STREAMS = {
    "stable": [0] * 24,
    "reversal": [0] * 8 + [1] * 16,
    "recurrence": [0] * 8 + [1] * 8 + [0] * 8,
}
def vote(bits):
    if not bits or 2 * sum(bits) == len(bits):
        return None
    return int(2 * sum(bits) > len(bits))

def evaluate(events, policy):
    rng = random.Random(SEED)
    sample = []
    history = deque(maxlen=BUDGET)
    correct = 0
    abstained = 0
    for index, value in enumerate(events):
        bits = list(history) if policy == "recent" else sample
        prediction = vote(bits)
        correct += prediction == value
        abstained += prediction is None
        history.append(value)
        if len(sample) < BUDGET:
            sample.append(value)
        elif policy == "reservoir":
            slot = rng.randrange(index + 1)
            if slot < BUDGET:
                sample[slot] = value
        elif policy == "recent":
            sample = list(history)
        elif policy == "first":
            pass
        else:
            raise ValueError(policy)
    return {"correct": int(correct), "total": len(events), "abstained": abstained}

def run():
    results = {name: {policy: evaluate(events, policy)
                      for policy in ("first", "recent", "reservoir")}
               for name, events in STREAMS.items()}
    assert all(v["total"] == 24 for row in results.values() for v in row.values())
    print(json.dumps({"schema": "mg94.equal_capacity_controls.v1",
                      "classification": "SYNTHETIC_DEVELOPMENT_ONLY",
                      "capacity_bits": BUDGET,
                      "seed": SEED,
                      "results": results,
                      "limits": "No learned task relevance, recurrent model, or scientific qualification"}, sort_keys=True))
if __name__ == "__main__":
    run()
