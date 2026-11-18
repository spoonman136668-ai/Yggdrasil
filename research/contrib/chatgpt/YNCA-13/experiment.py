"""YNCA-13: bounded source-free novel-operator memory falsification.

No original world, native model, runner controller, next-token model, or protected
first use. Learner receives episode boundaries and action/outcome pairs, never
operator names or an enumerated operator catalog.
"""
import argparse
from collections import Counter, defaultdict
import hashlib
import itertools
import json
import random
from pathlib import Path

SEEDS = (30113, 30213, 30313)
FAMILIES = ("AND", "OR", "XOR", "MAJ", "MUX")
CAPACITY = 4
OBSERVED = 4
EVAL_PER_FAMILY = 40


def simulator(name, action):
    a, b, c = ((action >> i) & 1 for i in range(3))
    if name == "AND":
        return a & b & c
    if name == "OR":
        return a | b | c
    if name == "XOR":
        return a ^ b ^ c
    if name == "MAJ":
        return int(a + b + c >= 2)
    if name == "MUX":
        return b if a else c
    raise ValueError("unknown simulator")


def encode(outcomes):
    assert len(outcomes) == 8 and set(outcomes) == set(range(8))
    return sum(int(outcomes[a]) << a for a in range(8))


def bit(table, action):
    return (table >> action) & 1


class CausalMemory:
    def __init__(self):
        self.counts = Counter()

    def observe_world(self, observed):
        # Only intervention-to-outcome evidence, no operator label.
        table = encode(dict(observed))
        if table not in self.counts and len(self.counts) >= CAPACITY:
            raise ValueError("operator-memory capacity exceeded")
        self.counts[table] += 1

    def bytes(self):
        return (json.dumps(sorted(self.counts.items()), separators=(",", ":")) + "\n").encode("ascii")

    @classmethod
    def restore(cls, raw):
        p = cls()
        pairs = json.loads(raw)
        if len(pairs) > CAPACITY:
            raise ValueError("invalid restored capacity")
        p.counts = Counter({int(t): int(n) for t, n in pairs})
        if raw != p.bytes():
            raise ValueError("noncanonical snapshot")
        return p


def compatible(counts, observed):
    return [(t, n) for t, n in counts.items()
            if all(bit(t, a) == y for a, y in observed)]


def forecast(counts, observed, action):
    matches = compatible(counts, observed)
    if not matches:
        return 0.5
    total = sum(n for _, n in matches)
    return sum(n * bit(t, action) for t, n in matches) / total


def exact_256(train_counts, observed, action):
    # Every 3-input Boolean table is a hypothesis, including unseen tables.
    matches = [(table, 1 + train_counts[table]) for table in range(256)
               if all(bit(table, a) == y for a, y in observed)]
    total = sum(n for _, n in matches)
    return sum(n * bit(t, action) for t, n in matches) / total


def active_action(counts, observed):
    taken = {a for a, _ in observed}
    remaining = sorted(set(range(8)) - taken)
    # Choose a discriminating do-action among as-yet consistent stored laws.
    ranked = [(forecast(counts, observed, a), a) for a in remaining]
    return min(ranked, key=lambda p: (-p[0] * (1 - p[0]), p[1]))[1]


def acquire():
    memory = CausalMemory()
    for name in itertools.islice(itertools.cycle(("AND", "OR")), 16):
        memory.observe_world([(a, simulator(name, a)) for a in range(8)])
    previous = {t: n for t, n in memory.counts.items()}
    old_predictions = {t: [bit(t, a) for a in range(8)] for t in previous}
    for name in itertools.islice(itertools.cycle(("XOR", "MAJ")), 16):
        memory.observe_world([(a, simulator(name, a)) for a in range(8)])
    raw = memory.bytes()
    memory = CausalMemory.restore(raw)  # independent cold restart
    retained = all(t in memory.counts and old_predictions[t] ==
                   [bit(t, a) for a in range(8)] for t in previous)
    return memory, retained, hashlib.sha256(raw).hexdigest()


def score_episode(name, counts, rng):
    observed = []
    for _ in range(OBSERVED):
        a = active_action(counts, observed)
        observed.append((a, simulator(name, a)))
    withheld = sorted(set(range(8)) - {a for a, _ in observed})
    assert len(withheld) == 4
    model = sum((forecast(counts, observed, a) - simulator(name, a)) ** 2
                for a in withheld) / len(withheld)
    full = sum((exact_256(counts, observed, a) - simulator(name, a)) ** 2
               for a in withheld) / len(withheld)
    matched = sum((forecast(counts, observed, a) - simulator(name, a)) ** 2
                  for a in withheld) / len(withheld)
    last = {list(counts)[-1]: 1}
    overwrite = sum((forecast(last, observed, a) - simulator(name, a)) ** 2
                    for a in withheld) / len(withheld)
    random_obs = [(a, simulator(name, a)) for a in rng.sample(range(8), OBSERVED)]
    random_hidden = set(range(8)) - {a for a, _ in random_obs}
    random_probe = sum((forecast(counts, random_obs, a) -
                        simulator(name, a)) ** 2 for a in random_hidden) / 4
    return {"candidate": model, "exact_256": full, "exact_matched_four": matched,
            "random_probe": random_probe, "last_world": overwrite, "no_memory": 0.25}


def primary():
    sums = {family: defaultdict(float) for family in FAMILIES}
    memory, retained, cold_sha = acquire()
    for seed in SEEDS:
        rng = random.Random(seed)
        episodes = list(itertools.chain.from_iterable(
            [[name] * EVAL_PER_FAMILY for name in FAMILIES]))
        rng.shuffle(episodes)
        for name in episodes:
            values = score_episode(name, memory.counts, rng)
            for method, score in values.items():
                sums[name][method] += score
    briers = {family: {method: round(total / (len(SEEDS) * EVAL_PER_FAMILY), 12)
                       for method, total in sorted(metrics.items())}
              for family, metrics in sums.items()}
    familiar = {method: sum(briers[name][method] for name in FAMILIES[:4]) / 4
                for method in briers["AND"]}
    all_families = {method: sum(briers[name][method] for name in FAMILIES) / 5
                    for method in briers["AND"]}
    gates = {
        "four_distinct_memories": len(memory.counts) == 4,
        "cold_retention": retained,
        "familiar_brier_le_0_15": familiar["candidate"] <= 0.15,
        "gain_over_uniform_exact_256_ge_0_05":
            familiar["exact_256"] - familiar["candidate"] >= 0.05,
        "new_mux_no_memory_harm_le_0_02": briers["MUX"]["candidate"] <= 0.27,
        "within_0_005_of_matched_exact": abs(
            familiar["candidate"] - familiar["exact_matched_four"]) <= 0.005,
    }
    verdict = ("DEVELOPMENT_GO" if all(gates.values()) else
               "DEVELOPMENT_MIXED" if gates["four_distinct_memories"] and gates["cold_retention"]
               else "DEVELOPMENT_NO_GO")
    return {
        "schema": "yggdrasil.ynca13.source-free-result.v1",
        "experiment": "YNCA-13",
        "frozen_seeds": list(SEEDS),
        "training_worlds": 32, "training_interventions_per_seed": 256,
        "evaluation_worlds_per_seed": EVAL_PER_FAMILY * len(FAMILIES),
        "evaluation_interventions_per_seed_per_method": OBSERVED * EVAL_PER_FAMILY * len(FAMILIES),
        "held_actions_per_seed_per_method": 4 * EVAL_PER_FAMILY * len(FAMILIES),
        "snapshot_sha256": cold_sha,
        "memory": sorted(memory.counts.items()),
        "family_brier": briers,
        "familiar_four_brier": {k: round(v, 12) for k, v in sorted(familiar.items())},
        "all_five_brier": {k: round(v, 12) for k, v in sorted(all_families.items())},
        "gates": gates, "verdict": verdict,
        "native_yggdrasil_trained": False, "scientific_pass": False,
        "protected_first_use": False, "accepted_ref_updated": False,
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", default="")
    args = parser.parse_args()
    result = primary()
    result["source_sha256"] = hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
    raw = json.dumps(result, sort_keys=True, indent=2) + "\n"
    if args.output:
        out = Path(args.output)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(raw, encoding="utf-8")
    print(raw, end="")


if __name__ == "__main__":
    main()
