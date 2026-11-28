"""Bounded recency candidate with retained, non-authoritative historical archive.

A fresh prediction requires two matching latest observations. Historical
transitions are retained separately and never converted into unobserved
current facts. The recency buffer is capped at two per public-action key.
"""
from collections import deque

class RecencyTransitionCandidate:
    def __init__(self, archive, capacity=128):
        if type(capacity) is not int or not 1 <= capacity <= 512:
            raise ValueError("CAPACITY_INVALID")
        self.archive = dict(archive)
        self.capacity = capacity
        self.recent = {}
        self.examples = 0
        self.revisions = 0
        self._previous = {}

    def observe(self, key, successor):
        if (not isinstance(key, tuple) or len(key) != 2 or
                not isinstance(key[0], bytes) or
                not isinstance(key[1], int) or
                not isinstance(successor, bytes) or not successor):
            raise ValueError("ACTION_OWNED_PUBLIC_OBSERVATION_REQUIRED")
        if key not in self.recent and len(self.recent) >= self.capacity:
            raise ValueError("RECENCY_CAP_REACHED")
        sample = self.recent.setdefault(key, deque(maxlen=2))
        sample.append(successor)
        self.examples += 1
        newest = self.predict(key)
        if newest is not None and newest != self._previous.get(key):
            self.revisions += 1
            self._previous[key] = newest

    def predict(self, key):
        recent = self.recent.get(key)
        return recent[-1] if recent is not None and len(recent) == 2 and recent[0] == recent[1] else None

    def records(self):
        return sum(len(v) for v in self.recent.values())
