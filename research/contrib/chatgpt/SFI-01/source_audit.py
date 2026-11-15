"""SFI-01 public synthetic source identifiability and consequential goals audit.

Evaluator-only internal hypotheses are used here solely for public-source
feasibility, not as candidate training input or as a hidden held evaluator.
"""
from __future__ import annotations

from collections import namedtuple
from hashlib import sha256
import json
import random
import statistics
import time

ACTIONS = 8
REGISTERS = 8
EXPLORATION = 24
SCORING = 16
WORLD_SEEDS = tuple(range(32))
FAMILIES = ("additive", "xor_shifted", "reversed_inhibitory", "three_action")
PublicPrior = namedtuple("PublicPrior", "before action reward after done")
PublicStep = namedtuple("PublicStep", "before action after reward done history")
PUBLIC_FIELDS = ("before", "action", "after", "reward", "done", "history")


def _rng(seed: int, label: str) -> random.Random:
    raw = sha256(f"SFI01-PUBLIC-SRC-v1/{label}/{seed}".encode("ascii")).digest()
    return random.Random(int.from_bytes(raw[:16], "big"))


def _action(a: int) -> int:
    if type(a) is not int or not 0 <= a < ACTIONS:
        raise ValueError("SFI01_INVALID_ACTION")
    return a


def _seed(seed: int) -> int:
    if type(seed) is not int or seed not in WORLD_SEEDS:
        raise PermissionError("SFI01_PUBLIC_COHORT_ONLY")
    return seed


def exploration(seed: int) -> tuple[int, ...]:
    _seed(seed)
    rng = _rng(seed, "PUBLIC-EXPLORATION")
    return tuple(rng.randrange(ACTIONS) for _ in range(EXPLORATION))


def _target(family: int, shift: int, prev: int, prevprev: int, context: int) -> int:
    if family == 0:
        return (prev + shift + context) % ACTIONS
    if family == 1:
        return ((prev ^ shift) + 2 * context) % ACTIONS
    if family == 2:
        return (shift - prev + 4 * context) % ACTIONS
    if family == 3:
        return (prev + (prevprev ^ shift) + 3 * context) % ACTIONS
    raise ValueError("SFI01_LAW_FAMILY")


class _SourceWorld:
    """Private source-owner diagnostic. Never pass this object to a learner."""

    __slots__ = ("_seed", "_family", "_shift", "_contexts", "_noise", "_episode", "_streak", "_steps", "state")

    def __init__(self, seed: int, hypothesis: tuple[int, int] | None = None):
        self._seed = _seed(seed)
        if hypothesis is None:
            self._family, self._shift = seed // ACTIONS, seed % ACTIONS
        else:
            self._family, self._shift = hypothesis
            if (type(self._family) is not int or type(self._shift) is not int or
                    not 0 <= self._family < len(FAMILIES) or not 0 <= self._shift < ACTIONS):
                raise ValueError("SFI01_LAW_HYPOTHESIS")
        contexts = _rng(seed, "EXOGENOUS-PUBLIC-CONTEXT")
        noise = _rng(seed, "EXOGENOUS-PUBLIC-NOISE")
        self._contexts = tuple(contexts.randrange(2) for _ in range(EXPLORATION + SCORING + 1))
        self._noise = tuple(tuple(noise.randrange(16) for _ in range(4))
                            for _ in range(EXPLORATION + SCORING + 1))
        self._episode: list[PublicPrior] = []
        self._streak = 0
        self._steps = 0
        self.state = self._state(0)

    def _state(self, step: int) -> tuple[int, ...]:
        recent = self._episode[-1].action if self._episode else 15
        older = self._episode[-2].action if len(self._episode) >= 2 else 15
        return (self._contexts[step], self._streak, recent, older) + self._noise[step]

    def public_history(self) -> tuple[PublicPrior, ...]:
        return tuple(self._episode[-16:])

    def step(self, action: int) -> PublicStep:
        action = _action(action)
        if self._steps >= EXPLORATION + SCORING:
            raise ValueError("SFI01_PUBLIC_ACTION_BUDGET")
        before = self.state
        history = self.public_history()
        if len(self._episode) >= 3:
            eligible = self._episode[-2]
            prev = self._episode[-3].action
            prevprev = self._episode[-4].action if len(self._episode) >= 4 else 0
            context = eligible.before[0] & 1
            expected = _target(self._family, self._shift, prev, prevprev, context)
            if eligible.action == expected:
                self._streak += 1
                done = self._streak >= 3
                reward = 1.0 if done else 0.25
            else:
                self._streak = 0
                done = False
                reward = -0.25
        else:
            done, reward = False, 0.0
        self._steps += 1
        if done:
            self._episode.clear()
            self._streak = 0
        after = self._state(self._steps) if done else None
        if not done:
            self._episode.append(PublicPrior(before, action, reward, (), done))
            after = self._state(self._steps)
            self._episode[-1] = PublicPrior(before, action, reward, after, done)
        self.state = after
        return PublicStep(before, action, after, reward, done, history)


def collect_public(seed: int, tape: tuple[int, ...]) -> tuple[PublicStep, ...]:
    _seed(seed)
    if type(tape) is not tuple or len(tape) > EXPLORATION + SCORING:
        raise ValueError("SFI01_PUBLIC_TAPE")
    env = _SourceWorld(seed)
    return tuple(env.step(action) for action in tape)


def _signature(rows: tuple[PublicStep, ...], steps: int) -> tuple:
    return tuple((row.before, row.action, row.after, row.reward, row.done)
                 for row in rows[:steps])


def _audited_matches(seed: int, actions: tuple[int, ...], prefix: int) -> int:
    # Source-owner diagnostic ONLY: fixed public action tape and identical
    # exogenous observations across every possible hidden source hypothesis.
    prefix_actions = actions[:prefix]
    truth = _SourceWorld(seed)
    observed = tuple(truth.step(action) for action in prefix_actions)
    target = _signature(observed, prefix)
    return sum(1 for family in range(len(FAMILIES)) for shift in range(ACTIONS)
               if _signature(tuple(_SourceWorld_replay(seed, family, shift, prefix_actions)), prefix) == target)


def _SourceWorld_replay(seed: int, family: int, shift: int, actions: tuple[int, ...]):
    env = _SourceWorld(seed, (family, shift))
    for action in actions:
        yield env.step(action)


def _choose_oracle(env: _SourceWorld) -> int:
    hist = env.public_history()
    if not hist:
        return 0
    prev = hist[-1].action
    prevprev = hist[-2].action if len(hist) >= 2 else 0
    return _target(env._family, env._shift, prev, prevprev, env.state[0] & 1)


def _score(seed: int, oracle: bool) -> dict:
    env = _SourceWorld(seed)
    for action in exploration(seed):
        env.step(action)
    rng = _rng(seed, "SCORING-RANDOM")
    rewards = []
    goals = 0
    for _ in range(SCORING):
        action = _choose_oracle(env) if oracle else rng.randrange(ACTIONS)
        step = env.step(action)
        rewards.append(step.reward)
        goals += int(step.done)
    return {"reward": sum(rewards), "goal_events": goals,
            "positive": sum(x > 0 for x in rewards),
            "negative": sum(x < 0 for x in rewards)}


def source_study() -> dict:
    start = time.perf_counter()
    entries = []
    shared_positive, shared_negative = 0, 0
    for seed in WORLD_SEEDS:
        actions = exploration(seed)
        public = collect_public(seed, actions)
        shared_positive += sum(row.reward > 0 for row in public)
        shared_negative += sum(row.reward < 0 for row in public)
        count8 = _audited_matches(seed, actions, 8)
        count24 = _audited_matches(seed, actions, EXPLORATION)
        oracle = _score(seed, True)
        random_control = _score(seed, False)
        entries.append({"world": seed, "family": seed // ACTIONS, "shift": seed % ACTIONS,
                        "compatible_8": count8, "compatible_24": count24,
                        "oracle": oracle, "random": random_control})
    unique24 = sum(entry["compatible_24"] == 1 for entry in entries)
    ambiguous8 = sum(entry["compatible_8"] >= 2 for entry in entries)
    oracle_worlds = sum(entry["oracle"]["goal_events"] > 0 for entry in entries)
    random_worlds = sum(entry["random"]["goal_events"] > 0 for entry in entries)
    oracle_mean = statistics.mean(entry["oracle"]["reward"] for entry in entries)
    random_mean = statistics.mean(entry["random"]["reward"] for entry in entries)
    predicates = {
        "unique24_at_least_24": unique24 >= 24,
        "ambiguous8_at_least_16": ambiguous8 >= 16,
        "oracle_goal_worlds_at_least_24": oracle_worlds >= 24,
        "random_goal_worlds_at_most_4": random_worlds <= 4,
        "earned_headroom_at_least_2": oracle_mean - random_mean >= 2,
        "both_reward_signs_in_exploration": shared_positive > 0 and shared_negative > 0,
    }
    exact = json.dumps(entries, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode("ascii")
    return {"schema": "yggdrasil.sfi01.source-feasibility-result.v1",
            "experiment": "SFI-01-DELAYED-CONTEXT-SWITCHED-GOAL-SOURCE",
            "worlds": len(entries), "public_exploration_actions": len(entries) * EXPLORATION,
            "on_policy_actions": len(entries) * 2 * SCORING,
            "total_simulated_action_steps_including_source_identifiability": len(entries) * (EXPLORATION + (1 + len(FAMILIES) * ACTIONS) * (8 + EXPLORATION) + 2 * (EXPLORATION + SCORING)),
            "unique_hypotheses_after_24": unique24,
            "ambiguous_hypotheses_after_8": ambiguous8,
            "oracle_goal_worlds": oracle_worlds, "random_goal_worlds": random_worlds,
            "oracle_mean_16_step_reward": oracle_mean,
            "random_mean_16_step_reward": random_mean,
            "oracle_minus_random_mean": oracle_mean - random_mean,
            "shared_public_exploration_positive": shared_positive,
            "shared_public_exploration_negative": shared_negative,
            "predicates": predicates,
            "classification": "SOURCE_FEASIBLE" if all(predicates.values()) else "SOURCE_UNFIT",
            "original_fkp17_held_first_use": False,
            "science_pass": False,
            "public_per_world_sha256": sha256(exact).hexdigest(),
            "entries": entries,
            "elapsed_seconds": time.perf_counter() - start}


if __name__ == "__main__":
    print(json.dumps(source_study(), sort_keys=True, indent=2))
