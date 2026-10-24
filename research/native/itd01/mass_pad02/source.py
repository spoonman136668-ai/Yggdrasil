"""PAD-02 internally authored DEVELOPMENT source only.

Never import candidate/control modules. Hidden rules stay inside the evaluator.
This is NOT an independent authored source or sealed scientific first use.
"""
import hashlib
import json
import random

BASE = 202610250000
FAMILIES = ("T", "L")
REPLICAS = (0, 1, 2)
FIT = 192
DEV = 128
ARMS = ("pad01_frozen_pair", "trained_pair_table",
        "trained_structural_search", "trained_episodic",
        "trained_action_prior", "credit_destroyed")
ZERO = (0, 0, 0, 0, 0, 0)


def digest(value):
    raw = json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    return hashlib.sha256(raw).hexdigest()


def seed_for(family, replica):
    if family not in FAMILIES or replica not in REPLICAS:
        raise ValueError("UNFROZEN_SOURCE_ROLE")
    return BASE + FAMILIES.index(family) * 100000 + replica * 1000


class HiddenSource:
    """Real action-indexed source with a public-history-dependent L rule."""

    def __init__(self, family, seed):
        if family not in FAMILIES:
            raise ValueError("UNKNOWN_SOURCE_FAMILY")
        self.family = family
        rng = random.Random(seed + 101)
        self.rules = [
            (tuple(rng.sample(range(6), 3 if family == "T" else 2)), rng.randrange(2))
            for _ in range(3)
        ]
        self.previous = ZERO
        self.steps = 0

    def step(self, observation, chosen_action):
        if len(observation) != 6 or any(x not in (0, 1) for x in observation):
            raise ValueError("SOURCE_BAD_PUBLIC_OBSERVATION")
        if chosen_action not in (0, 1, 2):
            raise ValueError("SOURCE_BAD_ACTION")
        indexes, flip = self.rules[chosen_action]
        if self.family == "T":
            i, j, k = indexes
            reward = observation[i] ^ observation[j] ^ observation[k] ^ flip
        else:
            i, j = indexes
            reward = self.previous[i] ^ observation[j] ^ flip
        self.previous = tuple(observation)
        self.steps += 1
        return int(reward)

    def identity(self):
        # Audit only: never serialize rules in learner-visible input.
        return digest(self.rules)


def fit_source(family, task_seed):
    source = HiddenSource(family, task_seed)
    rng_obs = random.Random(task_seed + 11)
    rng_action = random.Random(task_seed + 17)
    rows = []
    previous = ZERO
    for _ in range(FIT):
        x = tuple(rng_obs.randrange(2) for _ in range(6))
        action = rng_action.randrange(3)
        reward = source.step(x, action)
        rows.append((x, previous, action, reward))
        previous = x
    if source.steps != FIT:
        raise AssertionError("SOURCE_FIT_ACTION_COUNT")
    return rows, source.identity()


def dev_public_inputs(task_seed):
    rng = random.Random(task_seed + 29)
    return [tuple(rng.randrange(2) for _ in range(6)) for _ in range(DEV)]
