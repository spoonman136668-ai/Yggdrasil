"""Public synthetic structure-free causal feedback source; evaluator-owned only.

No source-private table is supplied to learners. The query context is selected
by the common frozen tape, the action is actually attempted, and earned binary
feedback arrives two actions later. Public developmental source, not held science.
"""
from __future__ import annotations
from collections import namedtuple
from hashlib import sha256
import random

CONTEXTS = 128
ACTIONS = 8
SEEDS = tuple(range(880400, 880432))
Attempt = namedtuple('Attempt', 'context action')
PublicEvent = namedtuple('PublicEvent', 'context action reward history')


def _rng(seed, tag):
    if type(seed) is not int or seed not in SEEDS:
        raise PermissionError('SFI04_PUBLIC_SEED_ONLY')
    entropy = sha256(f'SFI04-RANDOM-LAW-v1/{seed}/{tag}'.encode('ascii')).digest()
    return random.Random(int.from_bytes(entropy[:16], 'big'))


def public_tape(seed):
    rng = _rng(seed, 'TAPE')
    contexts = list(range(CONTEXTS))
    rng.shuffle(contexts)
    return tuple(Attempt(ctx, ((ctx & 7) + cycle) & 7)
                 for cycle in range(16) for ctx in contexts)


class World:
    def __init__(self, seed):
        rng = _rng(seed, 'LAW')
        self._targets = tuple(rng.randrange(ACTIONS) for _ in range(CONTEXTS))
        self._queue = []
        self.steps = 0

    def step(self, context, action):
        if type(context) is not int or not 0 <= context < CONTEXTS:
            raise ValueError('SFI04_PUBLIC_CONTEXT')
        if type(action) is not int or not 0 <= action < ACTIONS:
            raise ValueError('SFI04_PUBLIC_ACTION')
        if self.steps >= 2048:
            raise ValueError('SFI04_PUBLIC_BUDGET')
        history = tuple(self._queue)
        earned = (1 if history[0].action == self._targets[history[0].context]
                  else -1) if len(history) == 2 else 0
        if len(self._queue) == 2:
            self._queue.pop(0)
        self._queue.append(Attempt(context, action))
        self.steps += 1
        return PublicEvent(context, action, earned, history)

    def probe(self, context, action):
        """Read-only actual action consequence, returned to evaluator only."""
        if type(context) is not int or not 0 <= context < CONTEXTS:
            raise ValueError('SFI04_PROBE_CONTEXT')
        if type(action) is not int or not 0 <= action < ACTIONS:
            raise ValueError('SFI04_PROBE_ACTION')
        return 1 if action == self._targets[context] else -1
