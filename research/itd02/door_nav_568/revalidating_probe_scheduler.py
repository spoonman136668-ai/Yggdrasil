"""Bounded action-owned revalidation of quarantined public transitions.

The learner may explicitly spend one physical probe action to check a
previously surprising successor. A matching observed consequence clears the
quarantine; a conflicting result retains it. Rechecking does not count as
support for selecting active or archived memory. There is no expiry clock,
hidden regime identity, or inferred successor rewrite.
"""
from causal_probe_planner import CausalProbePlanner
from remembering_probe_scheduler import RememberingProbeScheduler

class RevalidatingProbeScheduler(RememberingProbeScheduler):
    def __init__(self, active_links, archived_links, starts, memory,
                 limit=6, candidate_cap=32):
        super().__init__(active_links, archived_links, starts, memory,
                         limit=limit, candidate_cap=candidate_cap)
        self.starts = {frame: frozenset(legal) for frame, legal in starts}
        self.candidate_cap = candidate_cap
        self.recheck_pending = None
        self.rechecks = 0

    def request_recheck(self, key):
        if (self.pending is not None or self.recheck_pending is not None or
                key not in self.memory.exceptions or
                key[1] not in self.starts.get(key[0], ()) or
                self.actions >= self.budget):
            return None
        self.recheck_pending = key
        self.actions += 1
        self.rechecks += 1
        return key

    def finish_recheck(self, observed):
        if self.recheck_pending is None or not isinstance(observed, bytes):
            raise ValueError("OWNED_PUBLIC_RECHECK_REQUIRED")
        key = self.recheck_pending
        expected = self.memory.exceptions[key][0]
        self.recheck_pending = None
        if observed != expected:
            self.memory.unexpected(key, expected, observed)
            return False
        self.memory.corroborated(key)
        ranked = CausalProbePlanner(self.candidate_cap).rank(
            self.active, self.archive, [(frame, tuple(sorted(legal)))
                                        for frame, legal in self.starts.items()])
        self.candidates = [c for c in ranked if c[0] not in self.memory.exceptions]
        return True

    def next_probe(self):
        if self.recheck_pending is not None:
            return None
        return super().next_probe()
