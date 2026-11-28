"""Bounded persisted negative transition evidence for adaptive public probes.

Stores action-owned first-hop surprises as public transition exceptions.
Future probe scheduling avoids known unreliable first actions. This memory
does not fabricate a successor model, infer hidden states or claim that the
unexpected consequence is stable across environment changes. A subsequent
successful observation clears the corresponding exception explicitly.
"""
from adaptive_probe_scheduler import AdaptiveProbeScheduler

class PublicExceptionMemory:
    def __init__(self, capacity=16):
        if type(capacity) is not int or not 1 <= capacity <= 128:
            raise ValueError("EXCEPTION_MEMORY_CAP_INVALID")
        self.capacity = capacity
        self.exceptions = {}

    def unexpected(self, key, predicted, observed):
        if not isinstance(predicted, bytes) or not isinstance(observed, bytes):
            raise ValueError("PUBLIC_BYTES_REQUIRED")
        if key not in self.exceptions and len(self.exceptions) >= self.capacity:
            raise ValueError("EXCEPTION_MEMORY_FULL")
        self.exceptions[key] = (predicted, observed)

    def corroborated(self, key):
        self.exceptions.pop(key, None)

class RememberingProbeScheduler(AdaptiveProbeScheduler):
    def __init__(self, active_links, archived_links, starts, memory,
                 limit=6, candidate_cap=32):
        if not isinstance(memory, PublicExceptionMemory):
            raise ValueError("PUBLIC_MEMORY_REQUIRED")
        super().__init__(active_links, archived_links, starts,
                         limit=limit, candidate_cap=candidate_cap)
        self.memory = memory
        self.candidates = [candidate for candidate in self.candidates
                           if candidate[0] not in self.memory.exceptions]

    def first_outcome(self, public_successor):
        if self.pending is None:
            raise ValueError("NO_PENDING_PROBE")
        key, expected, _ = self.pending
        if public_successor != expected:
            self.memory.unexpected(key, expected, public_successor)
        else:
            self.memory.corroborated(key)
        return super().first_outcome(public_successor)
