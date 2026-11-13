"""Frozen synthetic DEV diagnostic for DG1-MC01, never a protected science run.

Public learner gets only a continuous state/action/next-state trajectory.
Hidden gate identity is confined to this evaluator and is never passed to
LocalCausalMotifDev. No gradient or action on evaluator queries is permitted.
"""
from __future__ import annotations

import json
import random
import sys
import time
import tracemalloc
from pathlib import Path

# Execute from any cwd without requiring project installation.
sys.path.insert(0, str(Path(__file__).resolve().parents[4]))
from yggdrasil.local_causal_motif_dev import LocalCausalMotifDev


IN_FAMILY = (71101, 71102, 71103, 71104)
OUT_OF_FAMILY = (71105, 71106, 71107, 71108)


class EvaluatorOnlyRing:
    """The rule codes remain private to this evaluator, not the learner."""

    def __init__(self, seed):
        self.seed = seed
        self.gates = tuple(random.Random(seed + 17 * i).randrange(4)
                           for i in range(4))
        self.out_of_family = seed in OUT_OF_FAMILY

    def step(self, state, action):
        left = (state >> ((action - 1) % 4)) & 1
        right = (state >> ((action + 1) % 4)) & 1
        own = (state >> action) & 1
        if self.out_of_family:
            # Own-bit dependence is outside the candidate's representation.
            effect = (own == left) if self.gates[action] % 2 == 0 else (own != right)
        else:
            kind = self.gates[action]
            effect = (not left) if kind == 0 else (
                (not right) if kind == 1 else (
                    (left == right) if kind == 2 else (left or right)
                )
            )
        return state ^ (1 << action) if effect else state


def accuracy(predictions, targets):
    return sum(p == t for p, t in zip(predictions, targets)) / len(targets)


def balanced_accuracy(predictions, targets):
    tp = sum(p == t == 1 for p, t in zip(predictions, targets))
    tn = sum(p == t == 0 for p, t in zip(predictions, targets))
    positive = sum(t == 1 for t in targets)
    negative = sum(t == 0 for t in targets)
    if not positive or not negative:
        return None
    return (tp / positive + tn / negative) / 2


def one_world(seed):
    world = EvaluatorOnlyRing(seed)
    model = LocalCausalMotifDev()
    no_neighbors = LocalCausalMotifDev(neighbor_features=False)
    observed = {}
    state = 0
    start = time.perf_counter()
    for t in range(64):
        action = (t + seed) % 4
        successor = world.step(state, action)  # sole source transition
        model.observe(state, action, successor)
        no_neighbors.observe(state, action, successor)
        observed[(state, action)] = successor
        state = successor
    train_ms = round((time.perf_counter() - start) * 1000, 4)
    restored = LocalCausalMotifDev.restore(model.snapshot())
    assert restored.snapshot() == model.snapshot()
    assert model.updates == no_neighbors.updates == 64

    y_true = []
    pred = []
    control = []
    no_change = []
    ablated = []
    compositional = []
    cold_ok = True
    for before in range(16):
        for action in range(4):
            if (before, action) in observed:
                continue
            after = world.step(before, action)  # evaluator-only; no training
            toggle = int(after != before)
            y_true.append(toggle)
            pred.append(int(model.predict(before, action) != before))
            control.append(int(no_neighbors.predict(before, action) != before))
            no_change.append(0)
            ablated.append(int(model.predict(before, action, ablate_neighbors=True) != before))
            next_action = (action + 1) % 4
            expected = world.step(after, next_action)
            composed = model.rollout(before, (action, next_action))
            compositional.append(composed == expected)
            cold_ok = cold_ok and (
                model.predict(before, action) == restored.predict(before, action)
                and composed == restored.rollout(before, (action, next_action))
            )
    assert y_true  # otherwise cannot measure unfamiliar state/action contexts
    return {
        "seed": seed,
        "family": "out_of_family" if seed in OUT_OF_FAMILY else "in_family",
        "source_actions": 64,
        "unique_observed": len(observed),
        "unseen": len(y_true),
        "unseen_positive": sum(y_true),
        "unseen_negative": len(y_true) - sum(y_true),
        "candidate_balanced_accuracy": balanced_accuracy(pred, y_true),
        "candidate_unseen_accuracy": accuracy(pred, y_true),
        "no_neighbor_balanced_accuracy": balanced_accuracy(control, y_true),
        "always_no_change_balanced_accuracy": balanced_accuracy(no_change, y_true),
        "ablated_balanced_accuracy": balanced_accuracy(ablated, y_true),
        "exact_lookup_unseen_coverage": 0.0,
        "two_action_rollout_exact": sum(compositional) / len(compositional),
        "cold_restore_parity": cold_ok,
        "learned_float64_count": model.WEIGHTS,
        "logical_learned_bytes": model.LEARNED_BYTES,
        "checkpoint_bytes": len(model.snapshot()),
        "fit_wall_ms": train_ms
    }


def main():
    tracemalloc.start()
    worlds = [one_world(seed) for seed in IN_FAMILY + OUT_OF_FAMILY]
    _, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    inside = worlds[:4]
    valid = all(
        w["unseen"] >= 12 and
        w["candidate_balanced_accuracy"] is not None and
        w["no_neighbor_balanced_accuracy"] is not None
        for w in inside
    )
    mean = lambda key: sum(w[key] for w in inside) / 4
    best_control = max(mean("no_neighbor_balanced_accuracy"),
                       mean("always_no_change_balanced_accuracy"), 0.0)
    passed_signal = valid and all(
        w["candidate_balanced_accuracy"] >= 0.70 for w in inside
    ) and mean("candidate_balanced_accuracy") >= best_control + 0.10 and all(
        w["two_action_rollout_exact"] >= 0.60 and w["cold_restore_parity"]
        for w in inside
    )
    # This local development script cannot certify independent scientific
    # admission, authentic-world source, full regression or two-platform parity.
    if not valid:
        verdict = "INVALID_DEV"
    elif passed_signal:
        verdict = "DEV_SIGNAL_CANDIDATE_UNQUALIFIED"
    elif mean("candidate_balanced_accuracy") > best_control:
        verdict = "MIXED_DEV"
    else:
        verdict = "NEGATIVE_DEV"
    print(json.dumps({
        "schema": "yggdrasil.dg1-mc01.dev-report.v1",
        "classification": verdict,
        "scientific_acceptance": "UNVERIFIED",
        "test_only": True,
        "mean_in_family_balanced_accuracy": round(
            mean("candidate_balanced_accuracy"), 6) if valid else None,
        "mean_strongest_fair_control": round(best_control, 6) if valid else None,
        "peak_python_traced_bytes": peak,
        "worlds": worlds
    }, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
