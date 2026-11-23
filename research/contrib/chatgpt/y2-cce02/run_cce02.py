"""CCE02 frozen synthetic development evaluator; never native scientific first-use."""

import argparse
import json
import random
from pathlib import Path

from cce02 import IdentityEcology

SEEDS = (11, 23, 47, 89, 167)
TRAIN = 512
EVAL = 256


def training(seed: int, positive: bool):
    rng = random.Random(seed)
    for _ in range(TRAIN):
        hidden = rng.randrange(2)
        probe = rng.randrange(2)
        noise = rng.random() < 0.1 if positive and probe == 0 else None
        observation = hidden ^ int(noise) if noise is not None else rng.randrange(2)
        terminal = rng.randrange(2)
        reward = int(terminal == hidden)
        yield probe, observation, terminal, reward


def evaluation(seed: int, positive: bool):
    rng = random.Random(seed + 200000)
    for _ in range(EVAL):
        hidden = rng.randrange(2)
        noisy = hidden ^ int(rng.random() < 0.1)
        random_sensor = rng.randrange(2)
        # Generate both potential observations without leaking alternatives
        # to any model; only the selected observation is shown.
        observations = (noisy if positive else random_sensor, random_sensor)
        yield observations, hidden


def world(seed: int, positive: bool) -> dict:
    learner = IdentityEcology()
    for record in training(seed, positive):
        learner.observe(*record)
    admitted = learner.freeze()
    snapshot = learner.snapshot()
    cold = IdentityEcology.restore(snapshot)
    cold_equal = snapshot == cold.snapshot() and all(
        learner.p_reward(t, probe=p, observation=z)
        == cold.p_reward(t, probe=p, observation=z)
        for p in (0, 1) for z in (0, 1) for t in (0, 1)
    ) and learner.choose_probe() == cold.choose_probe()
    trained_best = max((0, 1), key=lambda p: (learner.value(p), -p))
    rng_uniform = random.Random(seed + 900000)
    totals = dict(cce=0, uniform=0, full_best=0, pooled=0, oracle=0)
    for observations, hidden in evaluation(seed, positive):
        cce_probe = learner.choose_probe()
        cce_terminal = learner.choose(observations[cce_probe])
        uniform_probe = rng_uniform.randrange(2)
        uniform_terminal = learner.choose_terminal(
            uniform_probe, observations[uniform_probe], conditional=True)
        fixed_terminal = learner.choose_terminal(
            trained_best, observations[trained_best], conditional=True)
        pooled_terminal = learner.choose_terminal(
            1, observations[1], conditional=False)
        for method, terminal in (("cce", cce_terminal),
                                 ("uniform", uniform_terminal),
                                 ("full_best", fixed_terminal),
                                 ("pooled", pooled_terminal)):
            totals[method] += int(terminal == hidden)
        totals["oracle"] += 1
    return {
        "seed": seed, "world": "positive" if positive else "null",
        "selected_probe": admitted, "trained_best_probe": trained_best,
        "probe_values": [learner.value(p) for p in (0, 1)],
        "prequential_gain": learner.gains,
        "success": {method: count / EVAL for method, count in totals.items()},
        "cold_equal": cold_equal, "checkpoint_bytes": len(snapshot),
        "training_episodes": TRAIN, "evaluation_episodes": EVAL,
    }


def benchmark() -> dict:
    positive = [world(seed, True) for seed in SEEDS]
    negative = [world(seed, False) for seed in SEEDS]
    averages = {
        key: sum(record["success"][key] for record in positive) / len(SEEDS)
        for key in ("cce", "uniform", "full_best", "pooled", "oracle")
    }
    correct = sum(v["selected_probe"] == 0 for v in positive)
    false = sum(v["selected_probe"] is not None for v in negative)
    cold = sum(v["cold_equal"] for v in positive)
    supported = (correct >= 4 and false == 0 and cold == 5
                 and averages["cce"] >= averages["uniform"] + 0.08
                 and averages["cce"] >= averages["full_best"] - 0.025)
    partial = correct > 0 or averages["cce"] > averages["uniform"]
    return {
        "schema": "yggdrasil.y2.cce02.dev-result.v1",
        "classification": ("DEVELOPMENT_SIGNAL" if supported
                           else "MIXED" if partial else "NEGATIVE"),
        "scientific_gain_verified": False,
        "native_acceptance": False,
        "notes": "Synthetic hidden regime only; finite fixed cells, centralized arbiter, no demonstrated autonomous world identity or unfamiliar transfer.",
        "seeds": list(SEEDS), "training_episodes": TRAIN,
        "evaluation_episodes": EVAL,
        "positive": positive, "null": negative, "averages": averages,
        "positive_correct_probe_seeds": correct,
        "null_false_admission_seeds": false,
        "cold_equal_seeds": cold,
        "advantage_over_uniform": averages["cce"] - averages["uniform"],
        "margin_to_trained_best": averages["cce"] - averages["full_best"],
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    result = benchmark()
    output = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if args.output:
        args.output.write_text(output, encoding="utf-8")
    print(output, end="")
