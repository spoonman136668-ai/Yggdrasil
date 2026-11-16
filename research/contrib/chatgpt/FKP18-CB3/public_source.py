"""CB3 public synthetic source-owner diagnostic, never imported by a learner.

Private causal feature locations/formula are stored ONLY in this source module.
A public step gives action-conditioned delayed earned reward, not future oracle.
"""
from __future__ import annotations
from collections import namedtuple
import random

import binding

START = 82300
WORLD_COUNT = 16
WORLDS = tuple(range(START, START + WORLD_COUNT))
ACTIONS = (0, 1)
TRAIN_ROWS = 515
TEST_ROWS = 128
PRIVATE_CONFIGS = (
    ((1, 32), (17, 22)),
    ((10, 35), (12, 27)),
    ((24, 14), (4, 9)),
    ((5, 31), (3, 21)),
)
Step = namedtuple("Step", binding.FIELDS)
Past = namedtuple("Past", binding.PAST_FIELDS)

def _seed(seed):
    if type(seed) is not int or seed not in WORLDS:
        raise PermissionError("CB3_PUBLIC_WORLD_COHORT_ONLY")
    return seed

def _law(seed, features):
    contents, gates = PRIVATE_CONFIGS[(_seed(seed) - START) % len(PRIVATE_CONFIGS)]
    x, y = ((features >> bit) & 1 for bit in contents)
    g0, g1 = ((features >> bit) & 1 for bit in gates)
    return x ^ y ^ int((2*x+y) == (2*g0+g1))

def public_training(seed):
    rng = random.Random(_seed(seed))
    state = [tuple(rng.randrange(16) for _ in range(8)) for _ in range(TRAIN_ROWS + 1)]
    actions = [rng.randrange(2) for _ in range(TRAIN_ROWS)]
    reward = [0] * TRAIN_ROWS
    for t in range(3, TRAIN_ROWS):
        j = t - 2
        bitset = binding._feature_bits(state[j], actions[j-1],
                                       actions[j-2] if j >= 2 else 0)
        reward[t] = 1 if actions[j] == _law(seed, bitset) else -1
    return tuple(Step(state[t], actions[t], state[t+1], reward[t], False,
                      tuple(Past(state[j], actions[j], reward[j], state[j+1], False)
                            for j in range(max(0, t-16), t)))
                 for t in range(TRAIN_ROWS))

def unseen_queries(seed):
    rng = random.Random(_seed(seed) + 1000)
    rows = []
    for _ in range(TEST_ROWS):
        earlier = tuple(rng.randrange(16) for _ in range(8))
        previous = tuple(rng.randrange(16) for _ in range(8))
        state = tuple(rng.randrange(16) for _ in range(8))
        p0, p1 = rng.randrange(2), rng.randrange(2)
        history = (Past(earlier, p0, 0, previous, False),
                   Past(previous, p1, 0, state, False))
        bitset = binding._feature_bits(state, p1, p0)
        actual = _law(seed, bitset)
        rows.append((state, history, actual))
    return tuple(rows)

def source_private_feature_pairs(seed):
    """Source-owner audit only; never called by candidate/control methods."""
    content, gate = PRIVATE_CONFIGS[(_seed(seed) - START) % len(PRIVATE_CONFIGS)]
    return tuple(sorted(content)), tuple(sorted(gate))
