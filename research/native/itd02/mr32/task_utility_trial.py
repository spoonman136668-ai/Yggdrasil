"""MR32-M task-derived memory-utility development trial.

Task outcomes come from a deterministic action-selection environment. The
utility learner receives only post-use task return relative to a paired
no-memory replay, and only for memories actually selected by the policy.
This is a controlled development fixture, not an original-source experiment.
"""
from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
import math
import random
import time
import tracemalloc
from typing import Iterable

from learned_memory_allocator import LearnedMemoryAllocator, ACTIVE, TOTAL

FIT_SEEDS = (101, 103, 107, 109, 113, 127, 131, 137)
TRANSFER_SEEDS = (1009, 1013, 1019, 1021, 1031, 1033, 1039, 1049,
                  1051, 1061, 1063, 1069, 1087, 1091, 1093, 1097)
EPISODES_PER_FIT_CLUSTER = 6
EPISODES_PER_TRANSFER_CLUSTER = 4
TASKS_PER_EPISODE = 16
BOOTSTRAP_DRAWS = 10_000
BOOTSTRAP_SEED = 320_031

# Every item has public metadata, a proposed action stored in its representation,
# and a hidden task-world probability that the proposal is correct.
_EVIDENCE = (1, 2, 4, 8, 16, 32, 64, 128)
_LEVELS = (0.05, 0.25, 0.55, 0.85)


def _metadata(item: int) -> tuple[int, float, float]:
    evidence = _EVIDENCE[item % len(_EVIDENCE)]
    error = _LEVELS[(item // 2 + item // 8) % len(_LEVELS)]
    contradiction = _LEVELS[(item * 3 + item // 4) % len(_LEVELS)]
    return evidence, error, contradiction


def _norm_evidence(evidence: int) -> float:
    return min(1.0, math.log1p(evidence) / math.log(257.0))


def _correct_probability(regime: int, evidence: int,
                          error: float, contradiction: float) -> float:
    ev = _norm_evidence(evidence) - 0.5
    er = error - 0.5
    co = contradiction - 0.5
    if regime == 0:
        p = 0.5 + 0.22 * ev - 0.22 * er - 0.18 * co
    elif regime == 1:
        p = 0.5 + 0.15 * ev - 0.15 * er - 0.30 * co + 0.10 * ev * (-co)
    else:
        raise ValueError("UNKNOWN_TASK_REGIME")
    return min(0.90, max(0.10, p))


@dataclass(frozen=True)
class TaskEvent:
    item: int
    guessed_action: int
    correct_action: int

    @property
    def task_return(self) -> float:
        return 1.0 if self.guessed_action == self.correct_action else -1.0


def _score_task_action(event: TaskEvent, guessed_action: int | None) -> float:
    # Abstaining without a retrieved memory has a declared zero-return baseline.
    if guessed_action is None:
        return 0.0
    return 1.0 if guessed_action == event.correct_action else -1.0


def _paired_memory_utility(event: TaskEvent, guessed_action: int) -> float:
    # Same deterministic task state: action with memory minus abstain/no-memory.
    return (_score_task_action(event, guessed_action)
            - _score_task_action(event, None))


def _stored_guess(seed: int, regime: int, item: int) -> int:
    # This is the action proposed by the stored public memory representation.
    rng = random.Random((seed * 131_071) ^ (regime * 524_287) ^ item)
    return rng.randrange(2)


def _event(seed: int, regime: int, episode: int, step: int,
           item: int) -> TaskEvent:
    evidence, error, contradiction = _metadata(item)
    p = _correct_probability(regime, evidence, error, contradiction)
    # Correctness is conditional on the exact action encoded in the memory.
    guess = _stored_guess(seed, regime, item)
    rng = random.Random((seed * 1_000_003) ^ (regime * 97_409)
                        ^ (episode * 65_537) ^ (step * 257) ^ item
                        ^ 0x4D523332)
    correct = guess if rng.random() < p else 1 - guess
    return TaskEvent(item, guess, correct)


def _query_order(seed: int, regime: int, episode: int) -> list[int]:
    # A task-world demand distribution; it is not exposed as a utility label.
    rng = random.Random((seed * 65_537) ^ (regime * 8191) ^ (episode * 131))
    weights = [rng.expovariate(1.0) for _ in range(TOTAL)]
    total = sum(weights)
    weights = [w / total for w in weights]
    return rng.choices(range(TOTAL), weights=weights, k=TASKS_PER_EPISODE)


def _representation(item: int, seed: int, regime: int) -> tuple[float, ...]:
    # First coordinate is the stored proposed action (-1 or +1); remaining
    # coordinates are a deterministic public item code, not the hidden answer.
    guess = _stored_guess(seed, regime, item)
    values = [0.0] * 16
    values[0] = 1.0 if guess else -1.0
    values[item % 15 + 1] = 1.0
    return tuple(values)


def _key(seed: int, regime: int, item: int, permutation: list[int]) -> str:
    return f"{permutation[item]:02d}-r{regime}-s{seed}-m{item:02d}"


@dataclass
class BayesianRecord:
    key: str
    item: int
    evidence_count: int
    prediction_error: float
    contradiction_rate: float
    uses: int = 0
    last_used: int = 0
    active: bool = False
    guess: int = 0


class InteractionBayesianUtility:
    """Competent interaction-capable diagonal Bayesian utility control."""
    def __init__(self) -> None:
        self.mean = [0.0] * 16
        self.variance = [1.0] * 16
        self.noise = 0.25
        self.step = 0
        self.feedback_count = 0
        self.records: list[BayesianRecord] = []

    @staticmethod
    def _features(r: BayesianRecord, step: int) -> tuple[float, ...]:
        base = (
            _norm_evidence(r.evidence_count),
            min(1.0, math.log1p(r.uses) / math.log(257.0)),
            1.0 / (1.0 + max(0, step-r.last_used) / 32.0),
            r.prediction_error,
            r.contradiction_rate,
        )
        out = [1.0, *base]
        out.extend(base[i] * base[j]
                   for i in range(5) for j in range(i + 1, 5))
        return tuple(out)

    def predict(self, r: BayesianRecord) -> float:
        raw = sum(w*x for w, x in zip(self.mean, self._features(r, self.step)))
        return min(1.0, max(0.0, 0.5 + raw))

    def _rank(self) -> None:
        ranked = sorted(self.records,
                        key=lambda r: (-self.predict(r), r.key))
        active = {r.key for r in ranked[:ACTIVE]}
        for r in self.records:
            r.active = r.key in active

    def insert_records(self, seed: int, regime: int,
                       permutation: list[int]) -> None:
        self.records = []
        self.step = 0
        for item in range(TOTAL):
            evidence, error, contradiction = _metadata(item)
            key = _key(seed, regime, item, permutation)
            guess = 1 if _representation(item, seed, regime)[0] > 0 else 0
            self.records.append(BayesianRecord(
                key, item, evidence, error, contradiction, 0, 0, False, guess))
        self._rank()

    def observe_use(self, record: BayesianRecord, task_return: float) -> None:
        if not record.active:
            raise RuntimeError("BAYESIAN_FEEDBACK_FOR_UNSELECTED_RECORD")
        self.step += 1
        record.uses += 1
        record.last_used = self.step
        x = self._features(record, self.step)
        target = 0.5 + 0.5 * task_return  # paired no-memory return is zero
        prediction = self.predict(record)
        innovation_variance = self.noise + sum(
            self.variance[i] * value * value for i, value in enumerate(x))
        for i, value in enumerate(x):
            prior = self.variance[i]
            gain = prior * value / innovation_variance
            self.mean[i] += gain * (target - prediction)
            self.variance[i] = max(1e-9, prior - gain * prior * value)
        self.feedback_count += 1
        self._rank()

    def active_items(self) -> set[int]:
        return {r.item for r in self.records if r.active}


def _permute(seed: int, regime: int) -> list[int]:
    values = list(range(TOTAL))
    random.Random((seed * 17_171) ^ (regime * 97_409)).shuffle(values)
    return values


def _new_h_allocator(seed: int, regime: int, permutation: list[int],
                     weights: list[float]) -> tuple[LearnedMemoryAllocator, dict[int, str]]:
    model = LearnedMemoryAllocator()
    model.weights = list(weights)
    keys: dict[int, str] = {}
    for item in range(TOTAL):
        evidence, error, contradiction = _metadata(item)
        key = _key(seed, regime, item, permutation)
        keys[item] = key
        model.insert(key, _representation(item, seed, regime),
                     evidence_count=evidence, prediction_error=error,
                     contradiction_rate=contradiction)
    return model, keys


def _h_active_items(model: LearnedMemoryAllocator,
                    keys: dict[int, str]) -> set[int]:
    active_keys = {m.key for m in model.memories if m.occupied and m.active}
    return {item for item, key in keys.items() if key in active_keys}


def _fixed_sets(seed: int, regime: int, permutation: list[int]) -> dict[str, set[int]]:
    keys = {i: _key(seed, regime, i, permutation) for i in range(TOTAL)}
    random_order = list(range(TOTAL))
    random.Random((seed * 65_521) ^ (regime * 104_729)).shuffle(random_order)
    random_set = set(random_order[:ACTIVE])
    # Item insertion order is the common immutable recency order.
    recency = set(range(TOTAL - ACTIVE, TOTAL))
    evidence = set(sorted(range(TOTAL),
                           key=lambda i: (-_metadata(i)[0], keys[i]))[:ACTIVE])
    return {"random": random_set, "fixed_recency": recency,
            "evidence_only": evidence}


def _record_hash(events: list[dict]) -> str:
    raw = json.dumps(events, sort_keys=True, separators=(",", ":")).encode()
    return hashlib.sha256(raw).hexdigest()


def _fit() -> tuple[list[float], InteractionBayesianUtility, dict]:
    h_weights = [0.0] * 6
    bayes = InteractionBayesianUtility()
    event_receipts = []
    # Eight FIT clusters: four frozen clusters per independently parameterized regime.
    for cluster, seed in enumerate(FIT_SEEDS):
        regime = 0 if cluster < len(FIT_SEEDS) // 2 else 1
        permutation = _permute(seed, regime)
        h, h_keys = _new_h_allocator(seed, regime, permutation, h_weights)
        bayes.insert_records(seed, regime, permutation)
        for episode in range(EPISODES_PER_FIT_CLUSTER):
            actual_episode = cluster * 10 + episode
            for step, item in enumerate(_query_order(seed, regime, actual_episode)):
                event = _event(seed, regime, actual_episode, step, item)
                if item in _h_active_items(h, h_keys):
                    key = h_keys[item]
                    mem = h._get(key)
                    guess = 1 if mem.representation[0] > 0 else 0
                    paired_delta = _paired_memory_utility(event, guess)
                    h.mark_use(key)
                    h.observe_task_outcome(key, 0.5 + 0.5 * paired_delta)
                b_record = next(r for r in bayes.records if r.item == item)
                if b_record.active:
                    task_return = _paired_memory_utility(event, b_record.guess)
                    bayes.observe_use(b_record, task_return)
                event_receipts.append({
                    "phase": "fit", "seed": seed, "regime": regime,
                    "episode": actual_episode, "step": step, "item": item,
                    "correct_action_sha": hashlib.sha256(
                        str(event.correct_action).encode()).hexdigest(),
                })
        h_weights = list(h.weights)
    receipt = {
        "fit_seeds": list(FIT_SEEDS),
        "fit_regimes": {"0": list(FIT_SEEDS[:len(FIT_SEEDS)//2]),
                        "1": list(FIT_SEEDS[len(FIT_SEEDS)//2:])},
        "fit_episodes": len(FIT_SEEDS) * EPISODES_PER_FIT_CLUSTER,
        "fit_event_count": len(event_receipts),
        "fit_event_sha256": _record_hash(event_receipts),
        "learned_weights": h_weights,
        "bayes_feedback_count": bayes.feedback_count,
        "bayes_mean": bayes.mean,
        "bayes_variance": bayes.variance,
    }
    return h_weights, bayes, receipt


def _bayes_from_fit(mean: list[float], variance: list[float]) -> InteractionBayesianUtility:
    model = InteractionBayesianUtility()
    model.mean = list(mean)
    model.variance = list(variance)
    return model


def _bootstrap_lower(values: list[float]) -> float:
    rng = random.Random(BOOTSTRAP_SEED)
    means = []
    n = len(values)
    for _ in range(BOOTSTRAP_DRAWS):
        means.append(sum(values[rng.randrange(n)] for _ in range(n)) / n)
    means.sort()
    return means[int(0.025 * BOOTSTRAP_DRAWS)]


def run() -> dict:
    started = time.perf_counter_ns()
    cpu_started = time.process_time_ns()
    tracemalloc.start()
    h_weights, bayes_fit, fit_receipt = _fit()
    bayes_mean = list(bayes_fit.mean)
    bayes_variance = list(bayes_fit.variance)

    cluster_rows = []
    held_event_receipts = []
    h_transfer_feedback = 0
    bayes_transfer_feedback = 0
    h_state_bytes = []
    bayes_state_bytes = []

    for cluster, seed in enumerate(TRANSFER_SEEDS):
        regime = 0 if cluster < len(TRANSFER_SEEDS) // 2 else 1
        regime_returns = {name: [] for name in
                          ("random", "fixed_recency", "evidence_only",
                           "mr32_h_learned", "interaction_bayesian")}
        permutation = _permute(seed, regime)
        fixed = _fixed_sets(seed, regime, permutation)
        h, h_keys = _new_h_allocator(seed, regime, permutation, h_weights)
        bayes = _bayes_from_fit(bayes_mean, bayes_variance)
        bayes.insert_records(seed, regime, permutation)
        h_state_bytes.append(len(h.snapshot()))
        bayes_state_bytes.append(len(json.dumps({
            "mean": bayes.mean, "variance": bayes.variance,
            "records": [r.__dict__ for r in bayes.records]
        }, sort_keys=True, separators=(",", ":")).encode()))

        for episode in range(EPISODES_PER_TRANSFER_CLUSTER):
            actual_episode = cluster * 10 + episode
            for step, item in enumerate(_query_order(seed, regime, actual_episode)):
                event = _event(seed, regime, actual_episode, step, item)
                for name, active in fixed.items():
                    if item in active:
                        guess = 1 if _representation(item, seed, regime)[0] > 0 else 0
                        score = _score_task_action(event, guess)
                    else:
                        score = _score_task_action(event, None)
                    regime_returns[name].append(score)

                if item in _h_active_items(h, h_keys):
                    mem = h._get(h_keys[item])
                    guess = 1 if mem.representation[0] > 0 else 0
                    score = _score_task_action(event, guess)
                else:
                    score = _score_task_action(event, None)
                regime_returns["mr32_h_learned"].append(score)

                b_record = next(r for r in bayes.records if r.item == item)
                if b_record.active:
                    score = _score_task_action(event, b_record.guess)
                else:
                    score = _score_task_action(event, None)
                regime_returns["interaction_bayesian"].append(score)

                held_event_receipts.append({
                    "phase": "transfer", "seed": seed, "regime": regime,
                    "episode": actual_episode, "step": step, "item": item,
                    "correct_action_sha": hashlib.sha256(
                        str(event.correct_action).encode()).hexdigest(),
                })

        h_transfer_feedback += h.feedback_count
        bayes_transfer_feedback += bayes.feedback_count
        cluster_rows.append({
            "seed": seed, "regime": regime,
            "method_mean_task_return": {
                name: sum(values) / len(values)
                for name, values in regime_returns.items()
            },
            "task_count": len(next(iter(regime_returns.values()))),
        })

    methods = ("random", "fixed_recency", "evidence_only",
               "mr32_h_learned", "interaction_bayesian")
    means = {method: sum(row["method_mean_task_return"][method]
                         for row in cluster_rows) / len(cluster_rows)
             for method in methods}
    strongest = max((m for m in methods if m != "mr32_h_learned"),
                    key=lambda m: means[m])
    paired_diffs = {
        comparator: [
            row["method_mean_task_return"]["mr32_h_learned"]
            - row["method_mean_task_return"][comparator]
            for row in cluster_rows
        ]
        for comparator in methods if comparator != "mr32_h_learned"
    }
    h_wins = {name: sum(diff > 0 for diff in diffs)
              for name, diffs in paired_diffs.items()}
    lower_bounds = {name: _bootstrap_lower(diffs)
                    for name, diffs in paired_diffs.items()}

    regime_detail = {}
    regime_wins = {}
    for regime in (0, 1):
        rows = [row for row in cluster_rows if row["regime"] == regime]
        regime_means = {
            method: sum(row["method_mean_task_return"][method] for row in rows)
            / len(rows) for method in methods
        }
        comparator_wins = sum(
            row["method_mean_task_return"]["mr32_h_learned"]
            > row["method_mean_task_return"][strongest] for row in rows)
        regime_wins[str(regime)] = comparator_wins
        regime_detail[str(regime)] = {
            "seed_clusters": len(rows),
            "method_mean_task_return": regime_means,
            "mr32_h_wins_vs_overall_strongest": comparator_wins,
        }

    current, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    cpu_ns = time.process_time_ns() - cpu_started
    wall_ns = time.perf_counter_ns() - started
    rss_bytes = None
    rss_method = "unavailable"
    try:
        import os
        if os.name == "nt":
            import psutil  # type: ignore
            rss_bytes = int(psutil.Process().memory_info().peak_wset)
            rss_method = "windows_peak_working_set"
        else:
            import resource
            # Linux ru_maxrss is reported in KiB.
            rss_bytes = int(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss * 1024)
            rss_method = "linux_ru_maxrss"
    except Exception:
        try:
            import psutil  # type: ignore
            rss_bytes = int(psutil.Process().memory_info().rss)
            rss_method = "current_rss_fallback_not_peak"
        except Exception:
            pass

    strongest_delta = means["mr32_h_learned"] - means[strongest]
    result = {
        "schema": "yggdrasil.mr32m.task-derived-utility.v1",
        "classification": "CONTROLLED_TASK_FIXTURE_DEVELOPMENT_NOT_SCIENTIFIC_ADMISSION",
        "protocol": {
            "fit_seeds": list(FIT_SEEDS),
            "transfer_seeds": list(TRANSFER_SEEDS),
            "fit_episodes_per_cluster": EPISODES_PER_FIT_CLUSTER,
            "transfer_episodes_per_cluster": EPISODES_PER_TRANSFER_CLUSTER,
            "tasks_per_episode": TASKS_PER_EPISODE,
            "active_budget": ACTIVE, "total_memory_budget": TOTAL,
            "fit_regime_split": 4, "transfer_regime_split": 8,
        },
        "fit": fit_receipt,
        "transfer": {
            "event_count": len(held_event_receipts),
            "event_sha256": _record_hash(held_event_receipts),
            "feedback_events_h": h_transfer_feedback,
            "feedback_events_bayesian": bayes_transfer_feedback,
            "seed_cluster_count": len(TRANSFER_SEEDS),
            "method_mean_task_return": means,
            "mr32_h_wins_by_comparator": h_wins,
            "bootstrap_2p5_by_comparator": lower_bounds,
            "strongest_comparator": strongest,
            "delta_vs_strongest": strongest_delta,
            "per_seed": cluster_rows,
            "regime_detail": regime_detail,
            "regime_wins_vs_overall_strongest": regime_wins,
        },
        "resource_diagnostics": {
            "process_cpu_ns": cpu_ns,
            "wall_ns": wall_ns,
            "process_peak_rss_bytes": rss_bytes,
            "process_peak_rss_method": rss_method,
            "tracemalloc_current_bytes": current,
            "tracemalloc_peak_bytes": peak,
            "h_checkpoint_bytes_mean": sum(h_state_bytes) / len(h_state_bytes),
            "bayes_state_json_bytes_mean": sum(bayes_state_bytes) / len(bayes_state_bytes),
        },
        "falsifiers": {
            "delta_at_least_0_02": strongest_delta >= 0.02,
            "wins_at_least_12_of_16": h_wins.get(strongest, 0) >= 12,
            "wins_at_least_6_of_8_each_regime": all(v >= 6 for v in regime_wins.values()),
            "bootstrap_lower_above_zero": lower_bounds.get(strongest, -1.0) > 0,
            "transfer_feedback_zero": h_transfer_feedback == 0 and bayes_transfer_feedback == 0,
            "fit_transfer_seeds_disjoint": not set(FIT_SEEDS).intersection(TRANSFER_SEEDS),
        },
    }
    result["development_signal"] = all(result["falsifiers"].values())
    return result

if __name__ == "__main__":
    print(json.dumps(run(), sort_keys=True, indent=2, allow_nan=False))
