"""Source-frozen MD30 native tournament vs conventional controls.

All numerical results here are exploratory SYNTHETIC development diagnostics.
Neither DEV, cold, registered, nor MD29 reserve seed can be constructed.
Every policy receives exactly the same public observation interface and pays
for every physical action. Numeric thresholds were committed *before* code.
"""
import json
import math
import time
from pathlib import Path

from bayesian_control import (COUNT, TOY_TRANSFER, BayesianGraphControl,
                              paid_training_episodes)
from structural_catalog import TRANSFER_MOTIFS, synthetic_world
from structural_rewire import canonical, digest
from native_tournament import (LOCK, CausalTournament, PersistentCausalMemory,
                               trained_memory)

ARMS = ("native_persistent_causal_tournament", "native_stateless_ablation",
        "native_change_agnostic_ablation", "trained_bayesian", "blind_A")
FRESH = tuple(range(6301, 6361))
KNOWN = TOY_TRANSFER
assert LOCK["evaluation"]["already_used_toy_seeds"] == [KNOWN[0], KNOWN[-1]]
assert LOCK["evaluation"]["fresh_synthetic_diagnostic_seeds"] == [FRESH[0], FRESH[-1]]
assert LOCK["train"]["credit_rule"].startswith("For each public response bit")
MODE = {
    ARMS[0]: "persistent", ARMS[1]: "stateless",
    ARMS[2]: "change_agnostic",
}


def run_one(seed, arm, hypotheses, memory, bayes_prior):
    if (type(seed) is not int or seed >= 1000000 or
            seed not in KNOWN and seed not in FRESH):
        raise AssertionError("MD30_NATIVE_ONLY_FROZEN_SYNTHETIC_SEEDS")
    pool = KNOWN if seed in KNOWN else FRESH
    motif = TRANSFER_MOTIFS[(seed - pool[0]) % 3]
    world = synthetic_world(seed, motif, rewire=(seed % 2 == 0))
    if arm in MODE:
        controller = CausalTournament(hypotheses, memory, MODE[arm])
    elif arm == "trained_bayesian":
        controller = BayesianGraphControl(hypotheses, bayes_prior)
    elif arm == "blind_A":
        controller = None
    else:
        raise AssertionError("MD30_NATIVE_UNKNOWN_CONTROL")
    steps, diagnostics = 0, 0
    while True:
        before = world.observe()
        if before["phase"] == "done":
            break
        action = ({"kind": "actuator", "node": 0, "value": 1}
                  if controller is None else controller.choose(before))
        after, _, done = world.step(action)
        if after["charged_history"][-1]["action"] != action:
            raise AssertionError("MD30_NATIVE_UNPAID_ACTION")
        if controller is not None:
            if arm in MODE:
                controller.consume(before, action, after)
            else:
                controller.posterior_step(action, after["charged_history"][-1])
        diagnostics += int(action["kind"] == "diagnostic")
        steps += 1
        if steps > 8:
            raise AssertionError("MD30_NATIVE_PHYSICAL_ACTION_OVERFLOW")
        if done:
            break
    receipt = world.receipt()
    assert receipt["paid_steps"] == steps
    return {
        "seed": seed, "motif": motif, "rewire": seed % 2 == 0,
        "reward": receipt["net_utility"], "steps": steps,
        "probes": diagnostics, "trace_sha256": receipt["physical_sha256"],
    }


def group_stats(rows):
    assert rows
    return {
        "episodes": len(rows),
        "mean_net_utility": round(math.fsum(x["reward"] for x in rows) / len(rows), 6),
        "charged_physical_actions": sum(x["steps"] for x in rows),
        "charged_diagnostics": sum(x["probes"] for x in rows),
        "trace_collection_sha256": digest([x["trace_sha256"] for x in rows]),
        "per_motif": {
            motif: round(
                math.fsum(x["reward"] for x in rows if x["motif"] == motif)
                / sum(x["motif"] == motif for x in rows), 6)
            for motif in TRANSFER_MOTIFS
        },
        "stable_mean": round(
            math.fsum(x["reward"] for x in rows if not x["rewire"])
            / sum(not x["rewire"] for x in rows), 6),
        "rewire_mean": round(
            math.fsum(x["reward"] for x in rows if x["rewire"])
            / sum(x["rewire"] for x in rows), 6),
    }


def one_cohort(seeds, hypotheses, memory, prior):
    raw = {arm: [] for arm in ARMS}
    for seed in seeds:
        for arm in ARMS:
            raw[arm].append(run_one(seed, arm, hypotheses, memory, prior))
    result = {arm: group_stats(rows) for arm, rows in raw.items()}
    base = raw["trained_bayesian"]
    candidates = {}
    for arm in ARMS[:3]:
        rows = raw[arm]
        pairs = [row["reward"] - other["reward"]
                 for row, other in zip(rows, base)]
        motif_diff = {}
        for motif in TRANSFER_MOTIFS:
            selected = [r["reward"] - b["reward"] for r, b in zip(rows, base)
                        if r["motif"] == b["motif"] == motif]
            assert len(selected) == 20
            motif_diff[motif] = round(math.fsum(selected) / len(selected), 6)
        candidates[arm] = {
            "paired_mean_delta_vs_bayesian": round(math.fsum(pairs) / len(pairs), 6),
            "paired_motif_deltas": motif_diff,
        }
    threshold = LOCK["evaluation"]["novelty_threshold"]
    assert threshold.startswith("Development-only threshold candidate >= Bayesian by 0.05")
    delta = candidates[ARMS[0]]
    exploratory_threshold_met = (
        delta["paired_mean_delta_vs_bayesian"] >= 0.05
        and all(x >= -0.03 for x in delta["paired_motif_deltas"].values())
    )
    return {
        "episodes_per_arm": len(seeds),
        "results": result,
        "contrasts": candidates,
        "candidate_development_threshold_met": exploratory_threshold_met,
        "classification": "SYNTHETIC_ONLY_NO_SCIENTIFIC_PASS",
    }


def check_cold_replay(hypotheses, memory, prior):
    checkpoint = json.loads(canonical(memory.checkpoint()))
    restored = PersistentCausalMemory.from_checkpoint(hypotheses, checkpoint)
    first = [run_one(seed, ARMS[0], hypotheses, memory, prior)
             for seed in (6301, 6302, 6303)]
    second = [run_one(seed, ARMS[0], hypotheses, restored, prior)
              for seed in (6301, 6302, 6303)]
    if first != second or restored.checkpoint() != checkpoint:
        raise AssertionError("MD30_NATIVE_COLD_REPLAY_DRIFT")
    return {"checkpoint_sha256": digest(checkpoint),
            "cold_replay_sha256": digest(first),
            "cold_replay_episodes": 3,
            "identical": True}


def run_development():
    training_begin = time.process_time()
    sessions, custody = paid_training_episodes()
    hypotheses, memory = trained_memory(sessions, custody)
    native_cpu = time.process_time() - training_begin
    bayes_begin = time.process_time()
    bayes = BayesianGraphControl(hypotheses).fit(sessions)
    bayes_cpu = time.process_time() - bayes_begin
    if len(hypotheses) != COUNT:
        raise AssertionError("MD30_NATIVE_UNMATCHED_HYPOTHESIS_CAP")
    cold = check_cold_replay(hypotheses, memory, bayes.prior)
    eval_begin = time.process_time()
    known = one_cohort(KNOWN, hypotheses, memory, bayes.prior)
    fresh = one_cohort(FRESH, hypotheses, memory, bayes.prior)
    eval_cpu = time.process_time() - eval_begin
    # Hard provenance cross-check with previous already-seen synthetic result:
    if known["results"]["trained_bayesian"]["mean_net_utility"] != 0.7525:
        raise AssertionError("MD30_NATIVE_STRONG_BAYES_CONTROL_DRIFT")
    if known["results"]["blind_A"]["mean_net_utility"] != 0.51:
        raise AssertionError("MD30_NATIVE_FIXED_CONTROL_DRIFT")
    return {
        "schema": "yggdrasil.dg1-md30-native-tournament-development.v1",
        "status": "PRECOMMITTED_SYNTHETIC_DIAGNOSTIC_ONLY",
        "official_first_use": False,
        "experiment_lock_sha256": digest(LOCK),
        "source_hypothesis_count": COUNT,
        "train": {
            "charged_episodes": 240,
            "charged_physical_actions": custody["charged_steps"],
            "public_trace_sha256": custody["physical_sha256"],
            "native_memory_sha256": digest(memory.checkpoint()),
            "bayesian_checkpoint_sha256": digest(bayes.checkpoint()),
        },
        "cold": cold,
        "known_previous_toy": known,
        "fresh_synthetic_diagnostic": fresh,
        "cpu_seconds": {
            "training_and_memory": round(native_cpu, 4),
            "bayesian_fit": round(bayes_cpu, 4),
            "joint_synthetic_evaluation": round(eval_cpu, 4),
        },
        "limitations": (
            "Synthetic exploration only; previous known toy cohort is not independent; "
            "new frozen synthetic cohort is NOT official MD30 DEV or registered; "
            "novelty threshold is diagnostic only; no first-use, SCIENTIFIC_PASS or integration."
        ),
    }


def parity_receipt(result):
    """Only timings are removed from portability receipt, never model metrics."""
    return {k: v for k, v in result.items() if k != "cpu_seconds"}


if __name__ == "__main__":
    print(canonical(run_development()))
