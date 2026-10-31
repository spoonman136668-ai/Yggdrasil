"""MR32-O multi-step task utility with terminal episodic credit.

Source-only deterministic fixture. The policy sees public query IDs only.
A single paired terminal task-return delta arrives after all 12 events.
"""
from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
import os
import random
import time
import tracemalloc
from typing import Iterable

Q = 65_536
ALPHA_Q16 = 5_243
LAMBDA_Q16 = 52_429
TOTAL = 16
ACTIVE = 7
RETAINED = 9
EVENTS = 12
GOALS = 3
FIT_SEEDS = (
    101, 103, 107, 109, 113, 127, 131, 137,
    139, 149, 151, 157, 163, 167, 173, 179,
)
TRANSFER_SEEDS = (
    1009, 1013, 1019, 1021, 1031, 1033, 1039, 1049,
    1051, 1061, 1063, 1069, 1087, 1091, 1093, 1097,
    1103, 1109, 1117, 1123, 1129, 1151, 1153, 1163,
    1171, 1181, 1187, 1193, 1201, 1213, 1217, 1223,
)
METHODS = (
    "random", "fixed_recency", "evidence_only",
    "uniform_mc", "interaction", "deca_q16",
)
LEARNED = {"uniform_mc", "interaction", "deca_q16"}
SCHEMA = "yggdrasil.mr32o.episodic-delayed-credit.v1"
STATE_SCHEMA = "yggdrasil.mr32o.policy-state.v1"
BOOTSTRAP_DRAWS = 10_000
BOOTSTRAP_SEED = 320_014


@dataclass(frozen=True)
class EpisodeSpec:
    seed: int
    regime: int
    episode: int
    public_items: tuple[int, ...]
    goal_positions: tuple[int, ...]
    required_actions: tuple[int, ...]
    hidden_sha256: str


@dataclass(frozen=True)
class UseReceipt:
    step: int
    item: int
    action: int
    features: tuple[int, ...]


def memory_metadata(item: int) -> tuple[int, int, int]:
    if isinstance(item, bool) or not isinstance(item, int) or not 0 <= item < TOTAL:
        raise ValueError("ITEM_RANGE")
    evidence_level = item % 8
    error_level = (item // 2 + item // 8) % 4
    contradiction_level = (3 * item + item // 4) % 4
    return evidence_level, error_level, contradiction_level


def proposal_action(item: int) -> int:
    return (item * 7 + 3) & 1


def correct_probability_bp(item: int, regime: int) -> int:
    evidence, error, contradiction = memory_metadata(item)
    if regime == 0:
        value = 5600 + 400 * evidence - 450 * error - 300 * contradiction
    elif regime == 1:
        value = (5200 + 160 * evidence - 250 * error - 150 * contradiction
                 + 200 * evidence * (3 - contradiction))
    else:
        raise ValueError("REGIME_RANGE")
    return max(2000, min(9500, value))


def _canonical_sha(value: object) -> str:
    raw = json.dumps(value, sort_keys=True, separators=(",", ":"),
                     ensure_ascii=True, allow_nan=False).encode("utf-8")
    return hashlib.sha256(raw).hexdigest()


def make_episode_spec(seed: int, regime: int, episode: int) -> EpisodeSpec:
    if regime not in (0, 1):
        raise ValueError("REGIME_RANGE")
    if seed <= 0 or episode < 0:
        raise ValueError("EPISODE_ID_RANGE")
    episode_seed = ((seed * 1_000_003) ^ (regime * 97_409)
                    ^ (episode * 65_537) ^ 0x4D52324F)
    rng = random.Random(episode_seed)
    public_items = tuple(rng.sample(range(TOTAL), EVENTS))
    goal_positions = tuple(sorted(rng.sample(range(EVENTS), GOALS)))
    required = [-1] * EVENTS
    for goal_index, position in enumerate(goal_positions):
        item = public_items[position]
        answer_rng = random.Random(
            episode_seed ^ (item * 257) ^ (goal_index * 65_537) ^ 0x4F445543
        )
        p_bp = correct_probability_bp(item, regime)
        guess = proposal_action(item)
        required[position] = (
            guess if answer_rng.randrange(10_000) < p_bp else 1 - guess
        )
    hidden_payload = {
        "seed": seed,
        "regime": regime,
        "episode": episode,
        "goal_positions": list(goal_positions),
        "required_actions": required,
    }
    return EpisodeSpec(seed, regime, episode, public_items, goal_positions,
                       tuple(required), _canonical_sha(hidden_payload))


def terminal_return(actions: Iterable[int], spec: EpisodeSpec) -> int:
    observed = tuple(actions)
    if len(observed) != EVENTS or any(x not in (0, 1) for x in observed):
        raise ValueError("ACTION_STREAM_INVALID")
    return int(all(observed[position] == spec.required_actions[position]
                   for position in spec.goal_positions))


def no_memory_return(spec: EpisodeSpec) -> int:
    return terminal_return([0] * EVENTS, spec)


def base_features(item: int, uses: int, last_used: int, clock: int) -> tuple[int, ...]:
    evidence, error, contradiction = memory_metadata(item)
    age = max(0, clock - last_used)
    return (
        Q,
        evidence * Q // 7,
        error * Q // 3,
        contradiction * Q // 3,
        Q // (1 + age),
        min(uses, 16) * Q // 16,
    )


def interaction_features(base: tuple[int, ...]) -> tuple[int, ...]:
    features = list(base)
    for left in range(1, 6):
        for right in range(left + 1, 6):
            features.append((base[left] * base[right]) // Q)
    return tuple(features)


def predict_q16(weights: list[int], features: tuple[int, ...]) -> int:
    if len(weights) != len(features):
        raise ValueError("FEATURE_WEIGHT_DIMENSION")
    return max(-Q, min(Q, sum(w * x for w, x in zip(weights, features)) // Q))


@dataclass
class PolicyState:
    method: str
    weights: list[int]
    uses: list[int]
    last_used: list[int]
    clock: int = 0
    feedback_events: int = 0
    episodes_seen: int = 0

    @classmethod
    def create(cls, method: str) -> "PolicyState":
        if method not in METHODS:
            raise ValueError("UNKNOWN_POLICY")
        count = 16 if method == "interaction" else (6 if method in LEARNED else 0)
        return cls(method, [0] * count, [0] * TOTAL, [-1] * TOTAL)

    def features(self, item: int) -> tuple[int, ...]:
        return base_features(item, self.uses[item], self.last_used[item], self.clock)

    def active_items(self, seed: int, regime: int, episode: int) -> set[int]:
        if self.method == "random":
            random_seed = ((seed * 65_521) ^ (regime * 104_729)
                           ^ (episode * 257) ^ 0x52414E44)
            order = random.Random(random_seed).sample(range(TOTAL), TOTAL)
            return set(order[:ACTIVE])
        if self.method == "fixed_recency":
            return set(sorted(range(TOTAL),
                              key=lambda item: (-self.last_used[item], item))[:ACTIVE])
        if self.method == "evidence_only":
            return set(sorted(range(TOTAL),
                              key=lambda item: (-2 ** memory_metadata(item)[0], item))[:ACTIVE])
        ranked = []
        for item in range(TOTAL):
            base = self.features(item)
            x = interaction_features(base) if self.method == "interaction" else base
            ranked.append((predict_q16(self.weights, x), item))
        ranked.sort(key=lambda pair: (-pair[0], pair[1]))
        return {item for _, item in ranked[:ACTIVE]}

    def act_episode(self, public_items: tuple[int, ...], seed: int,
                    regime: int, episode: int) -> tuple[list[int], list[UseReceipt], list[dict]]:
        if len(public_items) != EVENTS or len(set(public_items)) != EVENTS:
            raise ValueError("PUBLIC_QUERY_STREAM_INVALID")
        active = self.active_items(seed, regime, episode)
        actions: list[int] = []
        uses: list[UseReceipt] = []
        public_events: list[dict] = []
        for step, item in enumerate(public_items):
            selected = item in active
            if selected:
                features = self.features(item)
                action = proposal_action(item)
                uses.append(UseReceipt(step, item, action, features))
                self.uses[item] += 1
                self.last_used[item] = self.clock
            else:
                action = 0
            actions.append(action)
            public_events.append({
                "step": step, "item": item,
                "selected_memory": selected, "action": action,
            })
            self.clock += 1
        self.episodes_seen += 1
        if len(active) != ACTIVE or self.clock < EVENTS:
            raise RuntimeError("MEMORY_BUDGET_OR_CLOCK_INVARIANT")
        return actions, uses, public_events

    def allocate_terminal_credit(self, uses: list[UseReceipt],
                                 delta_q16: int) -> list[int]:
        if not uses:
            return []
        ordered = sorted(uses, key=lambda receipt: receipt.step)
        if self.method == "deca_q16":
            eligibilities = []
            for receipt in ordered:
                eligibility = Q
                for _ in range(EVENTS - 1 - receipt.step):
                    eligibility = (eligibility * LAMBDA_Q16) // Q
                eligibilities.append(eligibility)
        else:
            eligibilities = [Q] * len(ordered)
        total = sum(eligibilities)
        credits = [(delta_q16 * value) // total for value in eligibilities]
        remainder = delta_q16 - sum(credits)
        credits[-1] += remainder
        if sum(credits) != delta_q16:
            raise RuntimeError("TERMINAL_CREDIT_NOT_CONSERVED")
        return credits

    def apply_terminal_feedback(self, uses: list[UseReceipt],
                                delta_return: int) -> list[dict]:
        if self.method not in LEARNED:
            return []
        if delta_return not in (-1, 0, 1):
            raise ValueError("TERMINAL_DELTA_RANGE")
        credits = self.allocate_terminal_credit(uses, delta_return * Q)
        receipts = []
        for use, credit in zip(sorted(uses, key=lambda r: r.step), credits):
            base = use.features
            features = interaction_features(base) if self.method == "interaction" else base
            prediction = predict_q16(self.weights, features)
            error = credit - prediction
            for index, feature in enumerate(features):
                change = (ALPHA_Q16 * error * feature) // (Q * Q)
                self.weights[index] = max(-4 * Q, min(4 * Q,
                                                       self.weights[index] + change))
            receipts.append({
                "method": self.method, "step": use.step, "item": use.item,
                "features_q16": list(base), "eligibility_credit_q16": credit,
                "terminal_delta_q16": delta_return * Q,
            })
        self.feedback_events += len(uses)
        return receipts

    def payload(self) -> dict:
        return {
            "schema": STATE_SCHEMA,
            "method": self.method,
            "weights": self.weights,
            "uses": self.uses,
            "last_used": self.last_used,
            "clock": self.clock,
            "feedback_events": self.feedback_events,
            "episodes_seen": self.episodes_seen,
        }

    def snapshot(self) -> bytes:
        payload = self.payload()
        return json.dumps({
            "payload": payload, "sha256": _canonical_sha(payload)
        }, sort_keys=True, separators=(",", ":"), allow_nan=False).encode("utf-8")

    @classmethod
    def restore(cls, raw: bytes) -> "PolicyState":
        try:
            envelope = json.loads(raw.decode("utf-8"))
            payload = envelope["payload"]
            digest = _canonical_sha(payload)
        except Exception as exc:
            raise ValueError("POLICY_CHECKPOINT_FORMAT") from exc
        if digest != envelope.get("sha256"):
            raise ValueError("POLICY_CHECKPOINT_HASH_MISMATCH")
        if payload.get("schema") != STATE_SCHEMA:
            raise ValueError("POLICY_CHECKPOINT_SCHEMA")
        method = payload.get("method")
        state = cls.create(method)
        weights = payload.get("weights")
        uses = payload.get("uses")
        last_used = payload.get("last_used")
        clock = payload.get("clock")
        feedback = payload.get("feedback_events")
        episodes = payload.get("episodes_seen")
        if not isinstance(weights, list) or len(weights) != len(state.weights):
            raise ValueError("POLICY_CHECKPOINT_WEIGHTS")
        if not isinstance(uses, list) or len(uses) != TOTAL:
            raise ValueError("POLICY_CHECKPOINT_USES")
        if not isinstance(last_used, list) or len(last_used) != TOTAL:
            raise ValueError("POLICY_CHECKPOINT_RECENCY")
        for value in weights:
            if isinstance(value, bool) or not isinstance(value, int) or not -4 * Q <= value <= 4 * Q:
                raise ValueError("POLICY_CHECKPOINT_WEIGHT_RANGE")
        for value in uses:
            if isinstance(value, bool) or not isinstance(value, int) or value < 0:
                raise ValueError("POLICY_CHECKPOINT_USE_RANGE")
        for value in (clock, feedback, episodes):
            if isinstance(value, bool) or not isinstance(value, int) or value < 0:
                raise ValueError("POLICY_CHECKPOINT_COUNTER_RANGE")
        if clock != episodes * EVENTS:
            raise ValueError("POLICY_CHECKPOINT_CLOCK_EPISODE_MISMATCH")
        for value in last_used:
            if (isinstance(value, bool) or not isinstance(value, int)
                    or value < -1 or (value != -1 and value >= clock)):
                raise ValueError("POLICY_CHECKPOINT_RECENCY_RANGE")
        if method in LEARNED:
            if sum(uses) != feedback or feedback > episodes * EVENTS:
                raise ValueError("POLICY_CHECKPOINT_FEEDBACK_USE_MISMATCH")
        state.weights = list(weights)
        state.uses = list(uses)
        state.last_used = list(last_used)
        state.clock = clock
        state.feedback_events = feedback
        state.episodes_seen = episodes
        return state


def _seed_regime(index: int, per_regime: int) -> int:
    return 0 if index < per_regime else 1


def _cluster_summary(seed: int, regime: int, rows: list[dict]) -> dict:
    successes = {method: sum(row["terminal_return"][method] for row in rows)
                 for method in METHODS}
    return {
        "seed": seed, "regime": regime, "episode_count": len(rows),
        "successes": successes,
        "mean_return_q16": {
            method: (successes[method] * Q) // len(rows) for method in METHODS
        },
    }


def _paired_bootstrap_lower(differences_q16: list[int]) -> int:
    rng = random.Random(BOOTSTRAP_SEED)
    n = len(differences_q16)
    samples = []
    for _ in range(BOOTSTRAP_DRAWS):
        samples.append(sum(differences_q16[rng.randrange(n)] for _ in range(n)) // n)
    samples.sort()
    return samples[249]


def _peak_rss() -> tuple[int | None, str]:
    try:
        if os.name == "nt":
            import psutil  # type: ignore
            return int(psutil.Process().memory_info().peak_wset), "windows_peak_working_set"
        import resource
        return int(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss * 1024), "linux_ru_maxrss"
    except Exception:
        return None, "unavailable"


def run() -> dict:
    start_wall = time.perf_counter_ns()
    start_cpu = time.process_time_ns()
    tracemalloc.start()

    states = {method: PolicyState.create(method) for method in METHODS}
    method_cpu = {method: 0 for method in METHODS}
    fit_episode_receipts = []
    fit_feedback_receipts = []
    fit_event_rows = []
    fit_clusters = []

    for cluster_index, seed in enumerate(FIT_SEEDS):
        regime = _seed_regime(cluster_index, 8)
        cluster_rows = []
        for episode in range(8):
            spec = make_episode_spec(seed, regime, episode)
            baseline_return = no_memory_return(spec)
            method_returns = {}
            method_uses = {}
            method_actions = {}
            for method in METHODS:
                tick = time.process_time_ns()
                actions, uses, public_events = states[method].act_episode(
                    spec.public_items, seed, regime, episode
                )
                result = terminal_return(actions, spec)
                delta = result - baseline_return
                feedback = states[method].apply_terminal_feedback(uses, delta)
                method_cpu[method] += time.process_time_ns() - tick
                method_returns[method] = result
                method_uses[method] = [receipt.item for receipt in uses]
                method_actions[method] = actions
                fit_feedback_receipts.extend(feedback)
                fit_event_rows.append({
                    "seed": seed, "regime": regime, "episode": episode,
                    "method": method, "public_items": list(spec.public_items),
                    "public_actions": public_events, "hidden_spec_sha256": spec.hidden_sha256,
                    "terminal_return": result, "no_memory_return": baseline_return,
                    "delta_return": delta, "used_items": method_uses[method],
                    "feedback_count": len(feedback),
                })
            row = {
                "episode": episode, "no_memory_return": baseline_return,
                "terminal_return": method_returns, "used_items": method_uses,
            }
            cluster_rows.append(row)
            fit_episode_receipts.append({
                "seed": seed, "regime": regime, **row,
            })
        fit_clusters.append({
            "seed": seed, "regime": regime, "episode_count": len(cluster_rows),
            "successes": {
                method: sum(r["terminal_return"][method] for r in cluster_rows)
                for method in METHODS
            },
        })

    fit_feedback_counts = {
        method: sum(row["method"] == method for row in fit_feedback_receipts)
        for method in METHODS
    }
    fitted_checkpoints = {method: states[method].snapshot() for method in METHODS}
    fitted_checkpoint_sha = {
        method: hashlib.sha256(fitted_checkpoints[method]).hexdigest()
        for method in METHODS
    }
    checkpoint_bytes = {
        method: len(fitted_checkpoints[method]) for method in METHODS
    }
    fit_weights_sha256 = {
        method: _canonical_sha(states[method].weights) for method in METHODS
    }

    transfer_episode_receipts = []
    transfer_event_rows = []
    transfer_cluster_rows = []
    transfer_feedback_counts = {method: 0 for method in METHODS}
    transfer_cold_restore_counts = {method: 0 for method in METHODS}

    for cluster_index, seed in enumerate(TRANSFER_SEEDS):
        regime = _seed_regime(cluster_index, 16)
        cluster_rows = []

        # Each transfer cluster starts from the identical FIT terminal
        # checkpoint. No query/use/recency state carries across seed clusters.
        cluster_states = {}
        cluster_start_checkpoint_sha256 = {}
        cluster_start_weights_sha256 = {}
        cluster_start_feedback = {}
        cluster_start_episodes = {}
        for method in METHODS:
            restored = PolicyState.restore(fitted_checkpoints[method])
            if restored.snapshot() != fitted_checkpoints[method]:
                raise RuntimeError("TRANSFER_CLUSTER_COLD_RESTORE_BYTE_MISMATCH")
            cluster_states[method] = restored
            cluster_start_checkpoint_sha256[method] = hashlib.sha256(
                restored.snapshot()).hexdigest()
            cluster_start_weights_sha256[method] = _canonical_sha(restored.weights)
            cluster_start_feedback[method] = restored.feedback_events
            cluster_start_episodes[method] = restored.episodes_seen
            transfer_cold_restore_counts[method] += 1

        for episode in range(8):
            spec = make_episode_spec(seed, regime, episode)
            baseline_return = no_memory_return(spec)
            method_returns = {}
            method_uses = {}
            method_loo = {}
            for method in METHODS:
                tick = time.process_time_ns()
                actions, uses, public_events = cluster_states[method].act_episode(
                    spec.public_items, seed, regime, episode
                )
                result = terminal_return(actions, spec)
                method_cpu[method] += time.process_time_ns() - tick
                method_returns[method] = result
                method_uses[method] = [receipt.item for receipt in uses]
                loo = []
                for use in uses:
                    ablated = list(actions)
                    ablated[use.step] = 0
                    ablated_return = terminal_return(ablated, spec)
                    loo.append({
                        "item": use.item, "step": use.step,
                        "terminal_return_without_memory": ablated_return,
                        "marginal_terminal_return": result - ablated_return,
                    })
                method_loo[method] = loo
                transfer_event_rows.append({
                    "seed": seed, "regime": regime, "episode": episode,
                    "method": method, "public_items": list(spec.public_items),
                    "public_actions": public_events, "hidden_spec_sha256": spec.hidden_sha256,
                    "terminal_return": result, "no_memory_return": baseline_return,
                    "delta_return": result - baseline_return,
                    "used_items": method_uses[method],
                    "transfer_feedback_applied": False,
                    "loo_diagnostic": loo,
                })
            cluster_rows.append({
                "terminal_return": method_returns,
                "used_items": method_uses,
            })
            transfer_episode_receipts.append({
                "seed": seed, "regime": regime, "episode": episode,
                "no_memory_return": baseline_return,
                "terminal_return": method_returns,
                "delta_return": {
                    method: method_returns[method] - baseline_return for method in METHODS
                },
                "used_items": method_uses,
                "loo_diagnostic": method_loo,
                "transfer_feedback_applied": False,
            })

        cluster_feedback_delta = {}
        cluster_terminal_weights_sha256 = {}
        cluster_end_checkpoint_sha256 = {}
        cluster_episode_delta = {}
        for method in METHODS:
            state = cluster_states[method]
            feedback_delta = state.feedback_events - cluster_start_feedback[method]
            episode_delta = state.episodes_seen - cluster_start_episodes[method]
            weights_sha = _canonical_sha(state.weights)
            if feedback_delta != 0:
                raise RuntimeError("TRANSFER_FEEDBACK_WAS_APPLIED")
            if weights_sha != fit_weights_sha256[method]:
                raise RuntimeError("TRANSFER_LEARNED_WEIGHTS_CHANGED")
            if episode_delta != 8:
                raise RuntimeError("TRANSFER_CLUSTER_EPISODE_COUNT_MISMATCH")
            cluster_feedback_delta[method] = feedback_delta
            cluster_episode_delta[method] = episode_delta
            cluster_terminal_weights_sha256[method] = weights_sha
            cluster_end_checkpoint_sha256[method] = hashlib.sha256(
                state.snapshot()).hexdigest()
            transfer_feedback_counts[method] += feedback_delta

        transfer_cluster_rows.append({
            "seed": seed,
            "regime": regime,
            "episode_count": len(cluster_rows),
            "cold_restore_checkpoint_sha256": cluster_start_checkpoint_sha256,
            "fit_weights_sha256": cluster_start_weights_sha256,
            "terminal_weights_sha256": cluster_terminal_weights_sha256,
            "terminal_checkpoint_sha256": cluster_end_checkpoint_sha256,
            "episodes_executed_after_restore": cluster_episode_delta,
            "feedback_events_applied": cluster_feedback_delta,
            "successes": {
                method: sum(row["terminal_return"][method] for row in cluster_rows)
                for method in METHODS
            },
            "mean_return_q16": {
                method: (sum(row["terminal_return"][method] for row in cluster_rows) * Q)
                         // len(cluster_rows)
                for method in METHODS
            },
        })

    total_successes = {
        method: sum(row["successes"][method] for row in transfer_cluster_rows)
        for method in METHODS
    }
    mean_success = {
        method: total_successes[method] / (len(TRANSFER_SEEDS) * 8)
        for method in METHODS
    }
    comparator_order = METHODS[:-1]
    strongest = max(comparator_order,
                    key=lambda method: (total_successes[method],
                                        -comparator_order.index(method)))
    paired_differences = {
        method: [
            row["mean_return_q16"]["deca_q16"]
            - row["mean_return_q16"][method]
            for row in transfer_cluster_rows
        ]
        for method in METHODS if method != "deca_q16"
    }
    wins = {
        method: sum(value > 0 for value in differences)
        for method, differences in paired_differences.items()
    }
    bootstrap = {
        method: _paired_bootstrap_lower(differences)
        for method, differences in paired_differences.items()
    }
    regime_wins = {}
    regime_means = {}
    for regime in (0, 1):
        rows = [row for row in transfer_cluster_rows if row["regime"] == regime]
        regime_wins[str(regime)] = sum(
            row["mean_return_q16"]["deca_q16"]
            > row["mean_return_q16"][strongest] for row in rows
        )
        regime_means[str(regime)] = {
            method: sum(row["successes"][method] for row in rows)
                     / (len(rows) * 8)
            for method in METHODS
        }

    current_mem, peak_mem = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    rss_bytes, rss_method = _peak_rss()
    total_cpu = time.process_time_ns() - start_cpu
    total_wall = time.perf_counter_ns() - start_wall

    deca_cpu = method_cpu["deca_q16"]
    mc_cpu = method_cpu["uniform_mc"]
    deca_state = checkpoint_bytes["deca_q16"]
    mc_state = checkpoint_bytes["uniform_mc"]
    mean_delta_q16_sum = sum(paired_differences[strongest])
    mean_delta_q16 = mean_delta_q16_sum // len(TRANSFER_SEEDS)
    minimum_delta_q16 = (2 * Q + 99) // 100
    falsifiers = {
        "delta_at_least_0_02": (
            mean_delta_q16_sum >= minimum_delta_q16 * len(TRANSFER_SEEDS)
        ),
        "wins_at_least_24_of_32": wins[strongest] >= 24,
        "wins_at_least_12_of_16_each_regime": all(
            value >= 12 for value in regime_wins.values()
        ),
        "bootstrap_lower_above_zero": bootstrap[strongest] > 0,
        "transfer_feedback_zero": all(value == 0 for value in transfer_feedback_counts.values()),
        "fit_transfer_seed_disjoint": not set(FIT_SEEDS).intersection(TRANSFER_SEEDS),
        "deca_checkpoint_bytes_within_1_25x_uniform_mc": deca_state * 4 <= mc_state * 5,
        "deca_cpu_within_1_25x_uniform_mc": deca_cpu * 4 <= mc_cpu * 5,
    }

    result = {
        "schema": SCHEMA,
        "classification": "CONTROLLED_MULTI_STEP_TASK_FIXTURE_DEVELOPMENT_ONLY",
        "protocol": {
            "protocol_parent_sha": "8220c8dccbd389a7ea348d88d8ceb92835dd3453",
            "protocol_current_sha": "7cb8acbbc945d32abb669bd85d1ffeebc803b08b",
            "fit_seeds": list(FIT_SEEDS),
            "transfer_seeds": list(TRANSFER_SEEDS),
            "fit_episode_count": len(FIT_SEEDS) * 8,
            "transfer_episode_count": len(TRANSFER_SEEDS) * 8,
            "events_per_episode": EVENTS,
            "hidden_goal_events": GOALS,
            "total_memory_budget": TOTAL,
            "active_budget": ACTIVE,
            "retained_budget": RETAINED,
            "q16_scale": Q,
            "eligibility_lambda_q16": LAMBDA_Q16,
            "learning_rate_q16": ALPHA_Q16,
        },
        "fit": {
            "event_sha256": _canonical_sha(fit_event_rows),
            "event_receipt_count": len(fit_event_rows),
            "episode_receipts": fit_episode_receipts,
            "feedback_receipts": fit_feedback_receipts,
            "feedback_counts": fit_feedback_counts,
            "cluster_receipts": fit_clusters,
            "checkpoint_sha256": fitted_checkpoint_sha,
        },
        "transfer": {
            "event_sha256": _canonical_sha(transfer_event_rows),
            "event_receipt_count": len(transfer_event_rows),
            "episode_receipts": transfer_episode_receipts,
            "cluster_receipts": transfer_cluster_rows,
            "method_mean_terminal_success": mean_success,
            "strongest_comparator": strongest,
            "deca_mean_delta_vs_strongest": (
                mean_delta_q16_sum / (len(TRANSFER_SEEDS) * Q)
            ),
            "deca_mean_delta_q16_floor": mean_delta_q16,
            "deca_delta_q16_sum": mean_delta_q16_sum,
            "minimum_delta_q16": minimum_delta_q16,
            "deca_wins_by_comparator": wins,
            "bootstrap_2p5_q16_by_comparator": bootstrap,
            "regime_mean_terminal_success": regime_means,
            "deca_wins_by_regime_vs_strongest": regime_wins,
            "feedback_events_applied": transfer_feedback_counts,
            "cold_restore_cluster_count_by_method": transfer_cold_restore_counts,
        },
        "resource_diagnostics": {
            "process_cpu_ns": total_cpu,
            "process_wall_ns": total_wall,
            "process_peak_rss_bytes": rss_bytes,
            "process_peak_rss_method": rss_method,
            "tracemalloc_current_bytes": current_mem,
            "tracemalloc_peak_bytes": peak_mem,
            "per_method_cpu_ns_fit_plus_transfer": method_cpu,
            "checkpoint_bytes": checkpoint_bytes,
            "process_scope": "one process executes all methods sequentially; peak RSS is whole-process not isolated per-method",
        },
        "falsifiers": falsifiers,
    }
    result["development_signal"] = all(falsifiers.values())
    return result


if __name__ == "__main__":
    print(json.dumps(run(), sort_keys=True, indent=2, allow_nan=False))
