"""Controlled online-model influence on the following public action session.

Unlike the shadow-learning baseline, the experimental arm uses its learned
public transitions to rank the next session's probes. The archival model is
kept immutable. Data from the current session is applied only after its
decision, without reading future observations. Conflicting predictions can
cause abstention; no correctness guarantee or promotion is assumed.
"""
from time import perf_counter_ns
from online_public_learning import LearningPublicLoop
from native_public_loop import STARTS
from revalidating_probe_scheduler import RevalidatingProbeScheduler

class FeedbackPublicLoop(LearningPublicLoop):
    def __init__(self, enabled=True, capacity=128, recovery=False):
        super().__init__(capacity=capacity)
        self.enabled = enabled
        self.recovery = recovery

    def episode(self, world, budget=6, recheck=False):
        if not self.enabled:
            return super().episode(world, budget=budget, recheck=recheck)
        # All learned changes were committed after PREVIOUS sessions only.
        current = dict(self.learned.links)
        archive = dict(self.model.archived_links)
        start_ns = perf_counter_ns()
        scheduler = RevalidatingProbeScheduler(current, archive, STARTS,
                                               self.memory, limit=budget)
        # A complete loss of disagreement is NOT evidence that either model
        # is correct. Recover only the independent pre-update hypothesis pool;
        # every recovered hypothesis must still pass physical corroboration.
        fallback_used = False
        if self.recovery and not scheduler.candidates:
            scheduler = RevalidatingProbeScheduler(
                dict(self.model.active_links), archive, STARTS,
                self.memory, limit=budget)
            fallback_used = True
        candidate_count = len(scheduler.candidates)
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
            observed = world.step(*first)
            second = scheduler.first_outcome(observed)
            trace.append(("first", first, observed))
            if second is not None:
                successor = world.step(*second)
                scheduler.second_outcome(successor)
                trace.append(("second", second, successor))
        elapsed_ns = perf_counter_ns() - start_ns
        if scheduler.actions != world.actions:
            raise AssertionError("INTERVENTION_COUNT_MISMATCH")
        for event in trace:
            self.learned.observe(event[1], event[2])
            self.interactions += 1
        return {
            "selected": scheduler.decision(),
            "actions": scheduler.actions,
            "confirmed": len(scheduler.confirmed),
            "rejected": len(scheduler.rejected),
            "rechecks": scheduler.rechecks,
            "exceptions": len(self.memory.exceptions),
            "trace": trace,
            "examples": self.model.stored_examples(),
            "online_changes": self.learned.changes,
            "online_examples": self.learned.examples(),
            "online_records": len(self.learned.links),
            "decision_ns": elapsed_ns,
            "feedback_enabled": True,
            "recovery_enabled": self.recovery,
            "fallback_used": fallback_used,
            "candidate_count": candidate_count,
        }
