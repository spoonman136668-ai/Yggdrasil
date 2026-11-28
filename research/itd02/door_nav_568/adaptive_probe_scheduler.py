"""Bounded adaptive public probe scheduler.

Only learned two-hop disagreement ranks probes. First-hop observations are
checked against both memories before a second action is requested. A failed
first hop is discarded and an alternative is selected, with no model selection
from that failed chain. This is an experimental scheduler, not an agent acting
without an environment adapter.
"""
from causal_probe_planner import CausalProbePlanner

class AdaptiveProbeScheduler:
    def __init__(self, active_links, archived_links, starts, limit=6, candidate_cap=32):
        if type(limit) is not int or not 2 <= limit <= 16:
            raise ValueError("ACTION_BUDGET_INVALID")
        self.active = active_links
        self.archive = archived_links
        self.candidates = CausalProbePlanner(candidate_cap).rank(
            active_links, archived_links, starts)
        self.budget = limit
        self.actions = 0
        self.attempted = set()
        self.confirmed = []
        self.rejected = []
        self.pending = None

    def next_probe(self):
        if self.pending is not None or self.actions >= self.budget:
            return None
        for chain in self.candidates:
            first, middle, second = chain
            if first in self.attempted:
                continue
            if self.confirmed and (first[0] == self.confirmed[0][0][0] or
                                   second == self.confirmed[0][2]):
                continue
            self.attempted.add(first)
            self.pending = chain
            self.actions += 1
            return first
        return None

    def first_outcome(self, public_successor):
        if self.pending is None:
            raise ValueError("NO_PENDING_PROBE")
        _, expected, second = self.pending
        if public_successor != expected:
            self.rejected.append(self.pending[0])
            self.pending = None
            return None
        if self.actions >= self.budget:
            self.pending = None
            return None
        self.actions += 1
        return second

    def second_outcome(self, public_successor):
        if self.pending is None:
            raise ValueError("NO_PENDING_CHAIN")
        first, middle, second = self.pending
        self.confirmed.append((first, middle, second, public_successor))
        self.pending = None

    def decision(self):
        if len(self.confirmed) != 2:
            return None
        scores = [
            sum(links.get(first) == middle and links.get(second) == final
                for first, middle, second, final in self.confirmed)
            for links in (self.active, self.archive)
        ]
        if scores[0] == scores[1] or max(scores) != 2:
            return None
        return "active" if scores[0] > scores[1] else "snapshot"
