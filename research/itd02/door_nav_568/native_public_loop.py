"""Bounded public action and consequence loop over learned memories."""
from two_hop_evidence_audit import build, SECOND
from remembering_probe_scheduler import PublicExceptionMemory
from revalidating_probe_scheduler import RevalidatingProbeScheduler

STARTS = [(b"xA-training", (0, 1)), (b"xB-training", (0, 1))]

class PublicWorld:
    def __init__(self, regime, surprise=False):
        self.regime = regime
        self.surprise = surprise
        self.actions = 0

    def step(self, frame, action):
        self.actions += 1
        if frame in (b"xA-training", b"xB-training"):
            if self.surprise:
                self.surprise = False
                return b"Z9-surprise"
            correct = 1 if frame[1:2] == b"A" else 0
            return b"M1-intermediate" if action == correct else b"D2-intermediate"
        for middle, second, old, new in SECOND:
            if (middle, second) == (frame, action):
                return old if self.regime == "A" else new
        raise ValueError("UNKNOWN_ACTION")

class NativePublicLoop:
    def __init__(self):
        self.model = build()
        self.memory = PublicExceptionMemory(capacity=4)

    def episode(self, world, budget=6, recheck=False):
        scheduler = RevalidatingProbeScheduler(
            self.model.active_links, self.model.archived_links, STARTS,
            self.memory, limit=budget)
        trace = []
        if recheck:
            for key in sorted(self.memory.exceptions):
                if scheduler.request_recheck(key) is not None:
                    outcome = world.step(*key)
                    trace.append(("recheck", key, outcome,
                                  scheduler.finish_recheck(outcome)))
                    break
        while scheduler.decision() is None:
            first = scheduler.next_probe()
            if first is None:
                break
            outcome = world.step(*first)
            second = scheduler.first_outcome(outcome)
            trace.append(("first", first, outcome))
            if second is not None:
                successor = world.step(*second)
                scheduler.second_outcome(successor)
                trace.append(("second", second, successor))
        assert scheduler.actions == world.actions
        return {
            "selected": scheduler.decision(),
            "actions": scheduler.actions,
            "confirmed": len(scheduler.confirmed),
            "rejected": len(scheduler.rejected),
            "rechecks": scheduler.rechecks,
            "exceptions": len(self.memory.exceptions),
            "trace": trace,
            "examples": self.model.stored_examples(),
        }
