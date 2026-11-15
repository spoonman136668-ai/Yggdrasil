"""FKP-18 PUBLIC diagnostic for two-step delayed causal credit.

Research only. Not an FKP-17 held evaluation, native Yggdrasil integration,
or scientific evidence of a superior learning substrate. Every agent receives
only public action-consequence records; the oracle is for source headroom.
"""
from __future__ import annotations

from collections import namedtuple
import hashlib
import json
import random
import statistics
import time

ACTIONS = 8
PUBLIC_WORLDS = tuple(range(880000, 880032))
SEED = 1818
EXPLORE = 24
SCORE = 16
STATE_WIDTH = 8
TRANSITION = namedtuple("PublicTransition", "before action reward after done")
STEP = namedtuple("PublicStep", "before action after reward done history")


def _state(state):
    if type(state) is not tuple or len(state) != STATE_WIDTH or any(
        type(x) is not int or not 0 <= x < 16 for x in state
    ):
        raise ValueError("FKP18_PUBLIC_STATE_ONLY")
    return state


def _action(action):
    if type(action) is not int or not 0 <= action < ACTIONS:
        raise ValueError("FKP18_PUBLIC_ACTION_ONLY")
    return action


def _history(history, before):
    if type(history) is not tuple or len(history) > 16:
        raise ValueError("FKP18_PUBLIC_HISTORY_ONLY")
    for event in history:
        if type(event) is not TRANSITION:
            raise ValueError("FKP18_PUBLIC_HISTORY_FIELDS")
        _state(event.before)
        _state(event.after)
        _action(event.action)
        if type(event.reward) not in (float, int) or event.reward not in (1.0, 0.0, -0.25):
            raise ValueError("FKP18_PUBLIC_HISTORY_REWARD")
        if type(event.done) is not bool:
            raise ValueError("FKP18_PUBLIC_HISTORY_TERMINAL")
    if history and history[-1].after != before:
        raise ValueError("FKP18_HISTORY_DISCONTINUITY")
    return history


def _earned(row):
    if type(row) is not STEP:
        raise ValueError("FKP18_PUBLIC_STEP_FIELDS")
    before = _state(row.before)
    _action(row.action)
    _state(row.after)
    _history(row.history, before)
    if type(row.done) is not bool or type(row.reward) not in (float, int):
        raise ValueError("FKP18_PUBLIC_STEP_REWARD")
    if row.reward not in (1.0, 0.0, -0.25):
        raise ValueError("FKP18_PUBLIC_STEP_REWARD_RANGE")
    if len(row.history) < 3:
        if row.reward != 0:
            raise ValueError("FKP18_WARMUP_NONZERO")
        return None
    if row.reward == 0:
        raise ValueError("FKP18_MISSING_CREDIT")
    prev = row.history[-3]
    eligible = row.history[-2]
    # At t, reward belongs to public action t-2, its context and predecessor.
    shift = (eligible.action - prev.action - (eligible.before[0] & 1)) % ACTIONS
    return shift, row.reward > 0, prev.action, eligible.before[0] & 1, eligible.action


class PublicWorld:
    """Toy public source; private rule never appears in returned records."""

    def __init__(self, seed):
        if type(seed) is not int or seed not in PUBLIC_WORLDS:
            raise PermissionError("FKP18_PUBLIC_DIAGNOSTIC_SEEDS_ONLY")
        rng = random.Random(int.from_bytes(hashlib.sha256(
            ("FKP18-PUBLIC-v1-%d" % seed).encode("ascii")
        ).digest()[:16], "big"))
        self._shift = rng.randrange(ACTIONS)
        self._contexts = tuple(rng.randrange(2) for _ in range(EXPLORE + SCORE + 1))
        self._events = []
        self.state = self._public_state(0)

    def _public_state(self, step):
        return (self._contexts[step],) + (8,) * (STATE_WIDTH - 1)

    def step(self, action):
        _action(action)
        t = len(self._events)
        if t >= EXPLORE + SCORE:
            raise ValueError("FKP18_PUBLIC_BUDGET")
        before = self.state
        if t < 3:
            reward = 0.0
        else:
            prev = self._events[-3]
            eligible = self._events[-2]
            goal = (prev.action + (eligible.before[0] & 1) + self._shift) % ACTIONS
            reward = 1.0 if eligible.action == goal else -0.25
        after = self._public_state(t + 1)
        row = STEP(before, action, after, reward, False, tuple(self._events[-16:]))
        self._events.append(TRANSITION(before, action, reward, after, False))
        self.state = after
        return row

    def public_history(self):
        return tuple(self._events[-16:])


def exploration(seed):
    r = random.Random(seed ^ 0xAC179)
    return tuple(r.randrange(ACTIONS) for _ in range(EXPLORE))


class NativeCompositionalTrace:
    """Eight bounded direct-written operator-hypothesis support bits."""

    parameter_bytes = 1

    def __init__(self):
        self.mask = 255
        self.observed = 0

    def observe_public(self, row):
        if self.observed >= EXPLORE + SCORE:
            raise ValueError("FKP18_TRACE_BUDGET")
        result = _earned(row)
        if result is not None:
            shift, positive, *_ = result
            target_bit = 1 << shift
            changed = self.mask & target_bit if positive else self.mask & ~target_bit
            if not changed:
                raise ValueError("FKP18_CONTRADICTORY_CAUSAL_EVIDENCE")
            self.mask = changed
        self.observed += 1

    def choose(self, before, history):
        _state(before)
        _history(history, before)
        if not history:
            return 0
        prev = history[-1].action
        context = before[0] & 1
        return max(range(ACTIONS), key=lambda a: (
            sum(1 for s in range(ACTIONS) if (self.mask >> s) & 1 and
                (prev + context + s) % ACTIONS == a), -a
        ))


class ConventionalSymbolic:
    """Independently implemented exact, equally informed Bayesian support."""

    parameter_bytes = 8

    def __init__(self):
        self.posterior = [1] * ACTIONS
        self.observed = 0

    def observe_public(self, row):
        if self.observed >= EXPLORE + SCORE:
            raise ValueError("FKP18_SYMBOLIC_BUDGET")
        result = _earned(row)
        if result is not None:
            shift, positive, *_ = result
            new = [old * int((index == shift) == positive)
                   for index, old in enumerate(self.posterior)]
            if not any(new):
                raise ValueError("FKP18_SYMBOLIC_CONTRADICTION")
            self.posterior = new
        self.observed += 1

    def choose(self, before, history):
        _state(before)
        _history(history, before)
        if not history:
            return 0
        prev = history[-1].action
        return max(range(ACTIONS), key=lambda action: (
            sum(prob for shift, prob in enumerate(self.posterior)
                if (prev + (before[0] & 1) + shift) % ACTIONS == action),
            -action))


class TabularHistory:
    """Conventional direct table of observed (preceding-action,context,action)."""

    parameter_bytes = ACTIONS * 2 * ACTIONS * 12

    def __init__(self):
        self.table = {}
        self.observed = 0

    def observe_public(self, row):
        if self.observed >= EXPLORE + SCORE:
            raise ValueError("FKP18_TABLE_BUDGET")
        result = _earned(row)
        if result is not None:
            _, _, p, ctx, action = result
            old_count, old_sum = self.table.get((p, ctx, action), (0, 0.0))
            self.table[(p, ctx, action)] = (old_count + 1, old_sum + row.reward)
        self.observed += 1

    def choose(self, before, history):
        _state(before)
        _history(history, before)
        if not history:
            return 0
        p, ctx = history[-1].action, before[0] & 1
        return max(range(ACTIONS), key=lambda a: (
            self.table[(p, ctx, a)][1] / self.table[(p, ctx, a)][0]
            if (p, ctx, a) in self.table else -0.25, -a
        ))


class WrongCredit:
    """Explicit negative: delayed consequence incorrectly attributed to now."""

    parameter_bytes = ACTIONS * 12

    def __init__(self):
        self.count = [0] * ACTIONS
        self.sums = [0.0] * ACTIONS
        self.observed = 0

    def observe_public(self, row):
        if self.observed >= EXPLORE + SCORE:
            raise ValueError("FKP18_WRONG_BUDGET")
        _earned(row)
        self.sums[row.action] += row.reward
        self.count[row.action] += 1
        self.observed += 1

    def choose(self, before, history):
        _state(before)
        _history(history, before)
        return max(range(ACTIONS), key=lambda a: (
            self.sums[a] / self.count[a] if self.count[a] else -0.25, -a
        ))


class Oracle:
    def __init__(self, private_shift):
        self.shift = private_shift

    def observe_public(self, row):
        _earned(row)

    def choose(self, before, history):
        return (history[-1].action + (before[0] & 1) + self.shift) % ACTIONS if history else 0


class RandomControl:
    def __init__(self, seed):
        self.rng = random.Random(seed ^ 0xA26F)

    def observe_public(self, row):
        _earned(row)

    def choose(self, before, history):
        return self.rng.randrange(ACTIONS)


ARMS = ("native", "symbolic", "tabular", "wrong", "oracle", "random")


def one_world(seed):
    result = {}
    tape = exploration(seed)
    # Every model replays IDENTICAL source-public actions and evidence; no
    # private shift is passed to a learner, only to the diagnostic oracle.
    for label in ARMS:
        world = PublicWorld(seed)
        model = {
            "native": lambda: NativeCompositionalTrace(),
            "symbolic": lambda: ConventionalSymbolic(),
            "tabular": lambda: TabularHistory(),
            "wrong": lambda: WrongCredit(),
            "oracle": lambda: Oracle(world._shift),
            "random": lambda: RandomControl(seed),
        }[label]()
        for action in tape:
            model.observe_public(world.step(action))
        total = 0.0
        for _ in range(SCORE):
            action = model.choose(world.state, world.public_history())
            row = world.step(action)
            model.observe_public(row)
            total += row.reward
        result[label] = total
    return result


def study():
    start = time.perf_counter()
    scores = [one_world(seed) for seed in PUBLIC_WORLDS]
    means = {k: statistics.mean(s[k] for s in scores) for k in ARMS}
    differences = [s["native"] - s["symbolic"] for s in scores]
    bootstrap = random.Random(SEED)
    paired = sorted(statistics.mean(bootstrap.choices(differences, k=len(differences)))
                    for _ in range(1000))
    ci = [paired[24], paired[975]]
    return {
        "classification": "PUBLIC_DIAGNOSTIC_ONLY",
        "preregistered": True,
        "source_public_worlds": len(PUBLIC_WORLDS),
        "source_simulated_actions": len(PUBLIC_WORLDS) * len(ARMS) * (EXPLORE + SCORE),
        "exploration_actions_per_world": EXPLORE,
        "scored_actions_per_world": SCORE,
        "means": means,
        "native_minus_equal_symbolic_mean": statistics.mean(differences),
        "native_minus_equal_symbolic_bootstrap_95": ci,
        "absolute_gain_gate": 0.10,
        "scientific_pass": False,
        "strong_control_advantage_gate": (
            statistics.mean(differences) >= 0.10 and ci[0] > 0.02),
        "wall_seconds": time.perf_counter() - start,
        "protected_fkp17_first_use": False,
    }


if __name__ == "__main__":
    print(json.dumps(study(), indent=2, sort_keys=True))
