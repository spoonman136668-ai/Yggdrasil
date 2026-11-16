"""Public synthetic paid-probe decision source; hides source-private causal channel."""
from __future__ import annotations
from collections import namedtuple
import random

SEEDS = tuple(range(82600, 82632))
CHANNELS = 6
Event = namedtuple('Event', 'channel positive cost')


def public_config(seed):
    if type(seed) is not int or seed not in SEEDS:
        raise PermissionError('CB7_PUBLIC_SEEDS_ONLY')
    rng = random.Random(seed)
    regime = (seed - SEEDS[0]) % 4
    if regime == 0:
        masses = [17., 2., 2., 2., 2., 2.]
        rng.shuffle(masses)
        costs = [0.1] * CHANNELS
    elif regime == 1:
        masses = [1.] * CHANNELS
        costs = [round(rng.uniform(.02, .38), 3) for _ in range(CHANNELS)]
    elif regime == 2:
        masses = [rng.random()**3 + .05 for _ in range(CHANNELS)]
        costs = [round(rng.uniform(.02, .45), 3) for _ in range(CHANNELS)]
    else:
        masses = [1.+rng.random()*.3 for _ in range(CHANNELS)]
        costs = [round(rng.uniform(.02, .45), 3) for _ in range(CHANNELS)]
    total = sum(masses)
    prior = tuple(x/total for x in masses)
    return prior, tuple(costs)


class World:
    """One hidden causal identity. Each do(channel) costs its public rate."""
    def __init__(self, seed, hidden):
        self.prior, self.costs = public_config(seed)
        if type(hidden) is not int or not 0 <= hidden < CHANNELS:
            raise ValueError('CB7_SOURCE_OWNER_HIDDEN_ID_ONLY')
        self._hidden = hidden
        self._tested = set()
        self.cost = 0.
        self._ended = False
        self.events = []

    def probe(self, channel):
        if self._ended or type(channel) is not int or not 0 <= channel < CHANNELS or channel in self._tested:
            raise ValueError('CB7_INVALID_ACTUAL_INTERVENTION')
        self._tested.add(channel)
        self.cost += self.costs[channel]
        event = Event(channel, channel == self._hidden, self.costs[channel])
        self.events.append(event)
        return event

    def terminal(self, answer):
        if self._ended or type(answer) is not int or not 0 <= answer < CHANNELS:
            raise ValueError('CB7_TERMINAL_ACTION')
        self._ended = True
        correct = answer == self._hidden
        return (1. if correct else 0.) - self.cost, correct
