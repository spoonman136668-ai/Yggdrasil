"""Source-free two-session exception retention and probe-efficiency audit."""
import json
from remembering_probe_scheduler import PublicExceptionMemory, RememberingProbeScheduler
from adaptive_probe_audit import trial
from two_hop_evidence_audit import build, SECOND

def session(memory, first_failure):
    native = build()
    starts = [(b"xA-training", (0, 1)), (b"xB-training", (0, 1))]
    scheduler = RememberingProbeScheduler(native.active_links, native.archived_links,
                                         starts, memory, limit=6)
    public_second = {(middle, act): old for middle, act, old, _ in SECOND}
    failed = False
    while scheduler.decision() is None:
        first = scheduler.next_probe()
        if first is None:
            break
        expected = native.active_links[first]
        observed = b"Z9-unexpected" if first_failure and not failed else expected
        if observed != expected:
            failed = True
        second = scheduler.first_outcome(observed)
        if second is not None:
            scheduler.second_outcome(public_second[second])
    return {"selected": scheduler.decision(),
            "actions": scheduler.actions,
            "rejections": len(scheduler.rejected),
            "known_exceptions": len(memory.exceptions),
            "confirmed": len(scheduler.confirmed)}

def run():
    memory = PublicExceptionMemory(capacity=4)
    first = session(memory, True)
    second = session(memory, False)
    baseline = trial("A", first_failure=True)
    return {
        "first_session": first,
        "second_session_with_memory": second,
        "unremembered_failure_baseline": baseline,
        "memory_capacity": memory.capacity,
        "scope": "Source-free synthetic public first-hop surprises; persistent negative evidence only",
        "limitation": "A stale exception can suppress useful future probes; no autonomous environment-change inference",
    }

if __name__ == "__main__":
    print(json.dumps(run(), sort_keys=True))
