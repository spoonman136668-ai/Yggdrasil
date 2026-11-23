"""CCE04 synthetic development benchmark; fixed by its preregistration.

All models see identical public training histories. Evaluation uses previously
unseen five-action suffix 11111, with no access to the five future observations
until scoring. No native scientific first-use or accepted-model update.
"""
import argparse
import json
import math
import random
import time
from pathlib import Path

from cce04 import (CausalBeliefEcology, fit_grid, predict_future, templates,
                   TRAIN_EPISODES, TRAIN_ACTIONS)

SEEDS = (17, 37, 61, 109, 173)
EVAL_EPISODES = 96
PREFIX = 6
SUFFIX = (1, 1, 1, 1, 1)
MODELS = ("cce", "fine_hmm", "noaction_hmm", "suffix2", "iid", "oracle")


def action_prefix(rng: random.Random, horizon: int) -> tuple[int, ...]:
    actions = []
    for _ in range(horizon):
        action = rng.randrange(2)
        if len(actions) >= 2 and actions[-2:] == [1, 1]:
            action = 0
        actions.append(action)
    return tuple(actions)


def simulate(rng: random.Random, positive: bool,
             actions: tuple[int, ...]) -> tuple[int, ...]:
    if positive:
        hidden = rng.randrange(2)
        observations = [hidden ^ int(rng.random() < 0.18)]
        for action in actions:
            hidden ^= action
            hidden ^= int(rng.random() < 0.07)
            observations.append(hidden ^ int(rng.random() < 0.18))
    else:
        observations = [rng.randrange(2) for _ in range(len(actions) + 1)]
    return tuple(observations)


def training(seed: int, positive: bool) -> tuple:
    rng = random.Random(seed)
    return tuple((simulate(rng, positive,
                           (acts := action_prefix(rng, TRAIN_ACTIONS))), acts)
                 for _ in range(TRAIN_EPISODES))


def evaluation(seed: int, positive: bool) -> tuple:
    rng = random.Random(seed + 400000)
    episodes = []
    for _ in range(EVAL_EPISODES):
        prefix_actions = action_prefix(rng, PREFIX)
        obs = simulate(rng, positive, prefix_actions + SUFFIX)
        episodes.append((obs[:PREFIX + 1], prefix_actions, obs[PREFIX + 1:]))
    return tuple(episodes)


class SuffixCounts:
    def __init__(self):
        self.counts = {}

    def fit(self, episodes: tuple) -> None:
        for obs, acts in episodes:
            for i, action in enumerate(acts):
                prev = obs[i - 1] if i else obs[0]
                key = (prev, obs[i], action)
                pair = self.counts.setdefault(key, [0, 0])
                pair[obs[i + 1]] += 1

    def predict(self, obs: tuple, acts: tuple, future: tuple) -> tuple:
        prev, current = obs[-2], obs[-1]
        forecasts = []
        for action in future:
            pair = self.counts.get((prev, current, action), (0, 0))
            p = (pair[1] + 1) / (sum(pair) + 2)
            forecasts.append(p)
            prev, current = current, int(p > 0.5)
        return tuple(forecasts)


def one_world(seed: int, positive: bool) -> dict:
    train = training(seed, positive)
    start = time.perf_counter()
    cce = CausalBeliefEcology()
    cce.fit(train)
    cce_time = time.perf_counter() - start
    checkpoint = cce.snapshot()
    cold = CausalBeliefEcology.restore(checkpoint)
    start = time.perf_counter()
    fine_params, fine_score, _ = fit_grid(train, templates(coarse=False))
    fine_time = time.perf_counter() - start
    start = time.perf_counter()
    noaction_params, noaction_score, _ = fit_grid(
        train, templates(coarse=False, no_action=True))
    noaction_time = time.perf_counter() - start
    suffix = SuffixCounts()
    suffix.fit(train)
    evals = evaluation(seed, positive)
    cold_equal = checkpoint == cold.snapshot() and all(
        cce.predict(obs, acts, SUFFIX) == cold.predict(obs, acts, SUFFIX)
        for obs, acts, _ in evals)
    scores = {model: 0.0 for model in MODELS}
    for obs, acts, truths in evals:
        predictions = {
            "cce": cce.predict(obs, acts, SUFFIX),
            "fine_hmm": predict_future(obs, acts, SUFFIX, fine_params),
            "noaction_hmm": predict_future(obs, acts, SUFFIX, noaction_params),
            "suffix2": suffix.predict(obs, acts, SUFFIX),
            "iid": (0.5,) * len(SUFFIX),
            "oracle": predict_future(obs, acts, SUFFIX,
                                     ((0, 1), 0.18, 0.07) if positive else None),
        }
        for method, forecasts in predictions.items():
            scores[method] += sum((p - target) ** 2
                                  for p, target in zip(forecasts, truths))
    total = len(evals) * len(SUFFIX)
    return {
        "seed": seed, "world": "positive" if positive else "null",
        "brier": {model: scores[model] / total for model in MODELS},
        "selected_cce": cce.selected,
        "selected_fine_hmm": fine_params,
        "selected_noaction_hmm": noaction_params,
        "cce_null": cce.selected is None,
        "cold_equal": cold_equal, "checkpoint_bytes": len(checkpoint),
        "hypotheses_evaluated": {"cce": 36, "fine_hmm": 432,
                                 "noaction_hmm": 108},
        "training_seconds_diagnostic": {
            "cce": cce_time, "fine_hmm": fine_time,
            "noaction_hmm": noaction_time},
        "public_train_episodes": TRAIN_EPISODES,
        "public_train_transitions": TRAIN_EPISODES * TRAIN_ACTIONS,
        "eval_episodes": EVAL_EPISODES, "heldout_suffix": list(SUFFIX),
        "fine_log_likelihood": fine_score,
        "noaction_log_likelihood": noaction_score,
    }


def benchmark() -> dict:
    positive = [one_world(s, True) for s in SEEDS]
    null = [one_world(s, False) for s in SEEDS]
    averages = {mode: sum(row["brier"][mode] for row in positive) / len(SEEDS)
                for mode in MODELS}
    strongest = min(averages[m] for m in
                    ("fine_hmm", "noaction_hmm", "suffix2", "iid"))
    margin = strongest - averages["cce"]
    correct = sum(row["selected_cce"] is not None
                  and tuple(row["selected_cce"][0]) == (0, 1)
                  for row in positive)
    no_false = sum(row["cce_null"] for row in null)
    cold = sum(row["cold_equal"] for row in positive)
    supported = (margin >= 0.01 and correct >= 4 and no_false == 5 and cold == 5)
    partial = correct > 0 or any(averages["cce"] < averages[m]
                                for m in ("noaction_hmm", "suffix2", "iid"))
    return {
        "schema": "yggdrasil.y2.cce04.dev-result.v1",
        "classification": ("DEVELOPMENT_SIGNAL" if supported else
                           "MIXED" if partial else "NEGATIVE"),
        "scientific_gain_verified": False,
        "native_science_accepted": False,
        "seeds": list(SEEDS), "positive": positive, "null": null,
        "average_positive_brier": averages,
        "strongest_trained_control_brier": strongest,
        "margin_vs_strongest": margin,
        "correct_action_role_seeds": correct,
        "null_iid_selected_seeds": no_false, "cold_exact_seeds": cold,
        "limits": ["Hidden binary state with known 2-state hypothesis shape",
                   "Predefined action identities and candidate flip families",
                   "Novel action-string length, not genuinely new task class",
                   "Synthetic development screen, no native scientific first-use",
                   "Fine HMM grid searches more hypotheses than CCE",
                   "No dynamic population of developmental cells or AGI evidence"],
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    result = benchmark()
    payload = json.dumps(result, sort_keys=True, indent=2) + "\n"
    if args.output is not None:
        args.output.write_text(payload, encoding="utf-8")
    print(payload, end="")
