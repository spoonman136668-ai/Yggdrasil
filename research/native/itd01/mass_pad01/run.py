"""PAD-01: bounded internally-authored public-development action-credit screen.

The original source simulator is internal (NOT externally first-use or a native learner).
Only public (six-bit observation, chosen action, completed source reward) is trained on.
"""
from __future__ import annotations

import argparse
import hashlib
import itertools
import json
import random
import resource
import statistics
import time
from pathlib import Path

SEED_BASE = 202610230000
ARMS = ("sparse_pair_credit", "pairwise_ridge", "episodic_hamming",
        "action_prior", "random_policy", "pair_credit_ablated")
FAMILIES = ("P", "N")
REPLICAS = (0, 1, 2)
FIT = 96
DEV = 128
PAIRS = tuple(itertools.combinations(range(6), 2))


def sha(obj):
    return hashlib.sha256(json.dumps(obj, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


class HiddenSource:
    """Development-only authored causal source. Never pass this to a policy."""

    def __init__(self, family, task_seed):
        assert family in FAMILIES
        self.family = family
        rng = random.Random(task_seed + 101)
        self.rules = []
        for _ in range(3):
            indexes = rng.sample(range(6), 3)
            self.rules.append((indexes, rng.randrange(2)))

    def step(self, observation, chosen_action):
        assert len(observation) == 6 and set(observation) <= {0, 1}
        assert chosen_action in (0, 1, 2)
        (i, j, k), flip = self.rules[chosen_action]
        if self.family == "P":
            value = observation[i] ^ observation[j] ^ flip
        else:
            value = (observation[i] & observation[j]) ^ observation[k] ^ flip
        return int(value)


def family_seed(family, replica):
    return SEED_BASE + 10000 * FAMILIES.index(family) + 1000 * replica


def fit_history(source, seed):
    obs_rng = random.Random(seed + 11)
    act_rng = random.Random(seed + 17)
    public = []
    for _ in range(FIT):
        obs = tuple(obs_rng.randrange(2) for _ in range(6))
        chosen = act_rng.randrange(3)
        reward = source.step(obs, chosen)
        public.append((obs, chosen, reward))
    return public


def dev_inputs(seed):
    rng = random.Random(seed + 29)
    return [tuple(rng.randrange(2) for _ in range(6)) for _ in range(DEV)]


def fit_sparse_pair(rows):
    """Original chosen-action credit; selects a per-action 2-bit table by FIT loss."""
    out = []
    for action in range(3):
        data = [(x, y) for x, a, y in rows if a == action]
        candidates = []
        for i, j in PAIRS:
            cells = [[0, 0] for _ in range(4)]
            for x, y in data:
                index = 2 * x[i] + x[j]
                cells[index][0] += y
                cells[index][1] += 1
            # Smoothed estimates and penalized FIT squared error, no DEV selection.
            probabilities = [(ones + 1) / (n + 2) for ones, n in cells]
            loss = sum((y - probabilities[2*x[i] + x[j]]) ** 2 for x, y in data)
            loss += 0.025 * sum(n == 0 for _, n in cells)
            candidates.append((loss, i, j, tuple(probabilities)))
        _, i, j, probabilities = min(candidates)
        out.append((i, j, probabilities))
    return out


def predict_sparse(model, x, action):
    i, j, probabilities = model[action]
    return probabilities[2*x[i] + x[j]]


def feature(x):
    return (1.0,) + tuple(float(b) for b in x) + tuple(float(x[i] * x[j]) for i, j in PAIRS)


def fit_ridge(rows):
    """Conventional regularized trained main/pair logistic-like square-loss readout."""
    weights = []
    for action in range(3):
        data = [(feature(x), float(y)) for x, a, y in rows if a == action]
        w = [0.0] * 22
        for _ in range(125):
            grad = [0.0] * 22
            for vector, y in data:
                estimate = sum(a*b for a, b in zip(w, vector))
                for i, v in enumerate(vector):
                    grad[i] += (estimate-y) * v
            scale = 0.12 / max(1, len(data))
            w = [v - scale * (grad[i] + (0 if i == 0 else 0.8 * v))
                 for i, v in enumerate(w)]
        weights.append(tuple(w))
    return weights


def predict_ridge(model, x, action):
    result = sum(a*b for a, b in zip(model[action], feature(x)))
    return min(1.0, max(0.0, result))


def predict_episodic(rows, x, action):
    candidates = [(sum(b1 != b2 for b1, b2 in zip(x, prior)), index, y)
                  for index, (prior, a, y) in enumerate(rows) if a == action]
    top = sorted(candidates)[:5]
    return (1 + sum(y / (d + 1) for d, _, y in top)) / (
        2 + sum(1 / (d + 1) for d, _, _ in top))


def fit_prior(rows):
    return tuple((1 + sum(y for _, a, y in rows if a == action)) /
                 (2 + sum(a == action for _, a, _ in rows))
                 for action in range(3))


def train(arm, original_rows):
    # Action-label ablation shifts only training credit; original source DEV unchanged.
    rows = [(x, (a+1)%3, y) for x, a, y in original_rows] if arm == "pair_credit_ablated" else original_rows
    if arm in ("sparse_pair_credit", "pair_credit_ablated"):
        return fit_sparse_pair(rows)
    if arm == "pairwise_ridge":
        return fit_ridge(rows)
    if arm == "episodic_hamming":
        return tuple(rows)
    if arm == "action_prior":
        return fit_prior(rows)
    return None


def choose(arm, model, observation, dev_index):
    if arm == "random_policy":
        # Deliberately source-blind and chosen without source reward, family or seed.
        return (sum(observation) + dev_index) % 3
    if arm in ("sparse_pair_credit", "pair_credit_ablated"):
        scores = [predict_sparse(model, observation, a) for a in range(3)]
    elif arm == "pairwise_ridge":
        scores = [predict_ridge(model, observation, a) for a in range(3)]
    elif arm == "episodic_hamming":
        scores = [predict_episodic(model, observation, a) for a in range(3)]
    else:
        scores = model
    return max(range(3), key=lambda a: (scores[a], -a))


def run_task(family, replica):
    seed = family_seed(family, replica)
    source = HiddenSource(family, seed)
    rows = fit_history(source, seed)
    dev = dev_inputs(seed)
    outputs = {}
    for arm in ARMS:
        start_cpu = time.process_time()
        start_wall = time.perf_counter()
        model = train(arm, rows)
        fit_cpu = time.process_time() - start_cpu
        actions = [choose(arm, model, obs, idx) for idx, obs in enumerate(dev)]
        # Reward is an ORIGINAL hidden-source output AFTER decision, no model update.
        rewards = [source.step(obs, action) for obs, action in zip(dev, actions)]
        cpu = time.process_time() - start_cpu
        wall = time.perf_counter() - start_wall
        assert len(rewards) == DEV and all(r in (0, 1) for r in rewards)
        outputs[arm] = {
            "score": sum(rewards)/DEV,
            "fit_cpu_s": round(fit_cpu, 6),
            "fit_plus_dev_cpu_s": round(cpu, 6),
            "fit_plus_dev_wall_s": round(wall, 6),
            "model_bytes_json": len(json.dumps(model, separators=(",", ":")).encode()),
            "real_chosen_actions": actions, "real_source_rewards": rewards,
            "fit_updates": len(rows) if arm != "random_policy" else 0
        }
    # Hidden source identity is recorded ONLY in the evaluator's after-scoring receipt.
    return {
        "family": family, "replica": replica, "public_role_seed": seed,
        "source_rule_sha256_auditor_only": sha(source.rules),
        "fit_public_trace_sha256": sha(rows),
        "dev_public_observations_sha256": sha(dev),
        "source_real_fit_steps": len(rows),
        "source_real_dev_steps": DEV*len(ARMS),
        "arms": outputs,
        "candidate_vs_ablated_action_disagreements": sum(
            a != b for a, b in zip(outputs["sparse_pair_credit"]["real_chosen_actions"],
                                  outputs["pair_credit_ablated"]["real_chosen_actions"]))
    }


def finish(all_tasks):
    per_family = {}
    valid = True
    for family in FAMILIES:
        tasks = [x for x in all_tasks if x["family"] == family]
        means = {arm: round(statistics.mean(t["arms"][arm]["score"] for t in tasks), 6) for arm in ARMS}
        candidate = means["sparse_pair_credit"]
        best = max(means[x] for x in ("pairwise_ridge","episodic_hamming","action_prior"))
        delta = round(candidate-best, 6)
        ablation = round(candidate-means["pair_credit_ablated"], 6)
        losses = [t["arms"]["sparse_pair_credit"]["score"] -
                  max(t["arms"][a]["score"] for a in ("pairwise_ridge","episodic_hamming","action_prior"))
                  for t in tasks]
        family_ok = delta >= 0.03 and ablation >= 0.05 and min(losses) >= -0.05
        valid &= family_ok
        per_family[family] = {"mean_original_source_reward": means,
                              "candidate_minus_best_fitted_conventional": delta,
                              "candidate_minus_action_credit_ablation": ablation,
                              "worst_replica_candidate_minus_best_fitted": round(min(losses),6),
                              "frozen_accuracy_conditions_met": family_ok}
    # Deliberately fail closed: model-isolated process/energy and independent rerun absent.
    return {"family_results": per_family,
            "model_isolated_process_resource_parity": "NOT_MEASURED",
            "independent_replication": "NOT_PERFORMED",
            "scientific_classification": "PAD01_PUBLIC_DEVELOPMENT_NO_GO",
            "development_accuracy_screen_condition": bool(valid),
            "reason": "Resource parity and independent replication unqualified; no native integration or external first-use"}


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--out", type=Path, required=True)
    args = p.parse_args()
    start_cpu, start_wall = time.process_time(), time.perf_counter()
    tasks = [run_task(family, replica) for family in FAMILIES for replica in REPLICAS]
    result = finish(tasks)
    audit = {
        "schema": "mass.pad01.internal-public-dev.v1",
        "first_protocol_commit": "4f100e9e4fc1ff439482668b73d221c76e3b0ebf",
        "source_type": "internally_authored_public_development_NOT_independent_original_first_use",
        "source_public_fit_actions": FIT*len(tasks),
        "source_public_dev_actions": DEV*len(ARMS)*len(tasks),
        "source_task_count": len(tasks), "no_protected_holdout_consumed": True,
        "all_in_process_cpu_s": round(time.process_time()-start_cpu,6),
        "all_in_process_wall_s": round(time.perf_counter()-start_wall,6),
        "peak_process_rss_kib_linux": resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
        "tasks": tasks, "disposition": result
    }
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(audit, indent=2, sort_keys=True)+"\n", encoding="utf-8")
    print("PAD01_RESULT="+result["scientific_classification"])
    print("PAD01_FAMILY_SUMMARY="+json.dumps(result["family_results"],sort_keys=True))
    print("PAD01_PUBLIC_FIT_STEPS="+str(audit["source_public_fit_actions"]))
    print("PAD01_PUBLIC_DEV_STEPS="+str(audit["source_public_dev_actions"]))
    print("PAD01_RESOURCE_PARITY=NOT_QUALIFIED")
    return 0


if __name__=="__main__":
    raise SystemExit(main())
